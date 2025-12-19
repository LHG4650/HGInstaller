from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, Tuple
import os
import shutil
from setuptools import Extension, setup


Status = Literal[
    "py_missing",     # input .py 가 없음
    "pyd_missing",    # output 에 대응되는 .pyd 가 전혀 없음
    "py_newer",       # .py 가 가장 최신 .pyd 보다 더 최신
    "pyd_newer",      # 가장 최신 .pyd 가 .py 보다 더 최신
    "same_mtime",     # 둘의 수정 시간이 동일 (초 단위)
]


def find_pyd_target(
    input_root: str | Path,
    output_root: str | Path,
) -> list[Tuple[Path, Optional[Path], Status]]:
    """
    ### CLEAR ###
    input_root 아래 모든 .py 와 output_root 아래 대응 .pyd 의 관계를 조사한다.

    - __init__.py 는 pyd 대상으로 만들지 않으므로 스킵한다.
    - 결과에는 실제로 빌드 대상이 되는 것들만 포함한다.
      (pyd 가 없거나(pyd_missing) py 가 더 최신(py_newer) 인 경우)
    """

    input_root = Path(input_root)
    output_root = Path(output_root)

    results: list[Tuple[Path, Optional[Path], Status]] = []

    for py_path in input_root.rglob("*.py"):
        if not py_path.is_file():
            continue

        # init 은 pyd 안 만들기로 함
        if py_path.name == "__init__.py":
            continue

        relative_py = py_path.relative_to(input_root)

        pyd_dir = output_root / relative_py.parent
        file_stem = py_path.stem

        candidates = list(pyd_dir.glob(f"{file_stem}.*.pyd"))
        latest_pyd: Optional[Path]
        if not candidates:
            # pyd 가 아예 없으면 빌드 대상
            results.append((py_path, None, "pyd_missing"))
            continue

        latest_pyd = max(candidates, key=lambda p: p.stat().st_mtime)

        py_mtime = py_path.stat().st_mtime
        pyd_mtime = latest_pyd.stat().st_mtime

        if py_mtime > pyd_mtime:
            status: Status = "py_newer"
        elif py_mtime < pyd_mtime:
            status = "pyd_newer"
        else:
            status = "same_mtime"

        # 실제 빌드 대상만 리스트에 추가
        if status in ("py_newer", "pyd_missing"):
            results.append((py_path, latest_pyd, status))
            
    return results

def set_extentions(
    targets: list[Tuple[Path, Optional[Path], Status]],
    input_root: str | Path,
) -> list[Extension]:
    """Extension name 을 패키지 경로 기준으로 a.b 형식으로 만든다."""

    input_root = Path(input_root)
    extensions: list[Extension] = []

    for py_path, pyd_path, status in targets:
        # input_root 기준 상대 경로를 구해서 a/b.py -> a.b 로 변환
        relative = py_path.relative_to(input_root).with_suffix("")
        module_name = ".".join(relative.parts)

        extensions.append(Extension(module_name, [str(py_path)]))

    return extensions


def run_setup(
    extensions: list[Extension],
    output_root: str | Path,
    workers: int | None = None,
) -> None:
    """setuptools.setup 을 호출해서 .pyd 를 빌드한다.

    - output_root: 빌드된 .pyd 가 떨어질 폴더
    - workers: build_ext --parallel 에 넘길 worker 개수 (None 이면 옵션 생략)
    """

    output_root = Path(output_root)

    # workers 가 지정되지 않은 경우, 가능한 큰 값으로 자동 설정
    if workers is None:
        # os.cpu_count() 는 논리적 CPU 코어 수(하이퍼스레딩 포함)를 반환
        cpu_count = os.cpu_count() or 1
        # 너무 과한 값은 피하고, 최소 1개는 보장
        workers = max(1, cpu_count - 1)

    script_args: list[str] = [
        "build_ext",
        f"--build-lib={output_root}",
    ]
    script_args.append(f"--build-temp={output_root}")
    
    if workers is not None and workers > 0:
        script_args.append(f"--parallel={workers}")

    setup(
        script_args=script_args,
        ext_modules=extensions,
    )

def remove_temp_files(input_root: str | Path, output_root: str | Path,):
    output_root = Path(output_root)
    # remove dir 
    temp_dir = output_root / "Release"
    if temp_dir.exists():
        shutil.rmtree(temp_dir) # 디렉토리 삭제

    input_root = Path(input_root)
    # remove .c files
    for c_path in input_root.rglob("*.c"):
        if c_path.is_file():
            c_path.unlink()  # .c 파일 삭제



def py2pyd(input_root: str | Path, output_root: str | Path, workers: int | None = None):
    targets = find_pyd_target(input_root, output_root)
    extensions = set_extentions(targets, input_root)
    run_setup(extensions, output_root, workers)
    remove_temp_files(input_root, output_root)


if __name__ == "__main__":
    # 간단 수동 테스트용 (필요 시 수정해서 사용)
    input_root = r"C:\prog\HG_Installer\test_py"
    output_root = r"C:\prog\HG_Installer\test_pyd"
    py2pyd(input_root, output_root, workers=4)