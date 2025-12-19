"""pyproject.toml 파일에서 dependencies를 읽어오는 유틸리티 함수들"""
import re
from pathlib import Path
from typing import List, Optional

try:
    # Python 3.11+에서는 tomllib이 표준 라이브러리
    import tomllib
except ImportError:
    # Python 3.10 이하는 tomli 사용
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def parse_package_name(dep_string: str) -> str:
    """의존성 문자열에서 패키지 이름만 추출합니다.
    
    예:
        "tqdm>=4.65.0" -> "tqdm"
        "Cython>=3.0.0" -> "Cython"
        "package[extra]" -> "package"
    """
    # 버전 제약 조건 제거 (>=, ==, <=, <, >, ~=, !=)
    # extras 제거 ([extra])
    # 주석 제거 (# comment)
    dep_string = dep_string.split("#")[0].strip()
    
    # extras 제거
    if "[" in dep_string:
        dep_string = dep_string.split("[")[0]
    
    # 버전 제약 조건 제거
    # 패턴: 패키지명 뒤에 오는 비교 연산자와 버전 정보 제거
    match = re.match(r"^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)", dep_string)
    if match:
        return match.group(1)
    
    return dep_string.strip()


def get_dependencies_from_pyproject(
    pyproject_path: Optional[str | Path] = None
) -> List[str]:
    """pyproject.toml 파일에서 dependencies 목록을 읽어옵니다.
    
    Args:
        pyproject_path: pyproject.toml 파일 경로. None이면 현재 디렉토리에서 찾습니다.
    
    Returns:
        패키지 이름 리스트 (버전 정보 제거됨)
    
    Raises:
        FileNotFoundError: pyproject.toml 파일을 찾을 수 없을 때
        ValueError: tomllib/tomli를 사용할 수 없을 때
    """
    if pyproject_path is None:
        pyproject_path = Path.cwd() / "pyproject.toml"
    else:
        pyproject_path = Path(pyproject_path)
    
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml 파일을 찾을 수 없습니다: {pyproject_path}")
    
    if tomllib is None:
        raise ValueError(
            "tomllib 또는 tomli가 필요합니다. "
            "Python 3.11 이상을 사용하거나, 'uv add tomli'로 설치하세요."
        )
    
    # TOML 파일 읽기
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    
    # dependencies 추출
    dependencies = []
    
    # [project] 섹션의 dependencies
    if "project" in data and "dependencies" in data["project"]:
        deps = data["project"]["dependencies"]
        if isinstance(deps, list):
            dependencies.extend(deps)
    
    # [project.optional-dependencies] 섹션의 dependencies도 포함할지 선택 가능
    # 기본적으로는 포함하지 않지만, 필요시 옵션으로 추가 가능
    
    # 패키지 이름만 추출 (버전 정보 제거)
    package_names = [parse_package_name(dep) for dep in dependencies]
    
    return package_names


def get_optional_dependencies_from_pyproject(
    pyproject_path: Optional[str | Path] = None,
    groups: Optional[List[str]] = None
) -> List[str]:
    """pyproject.toml 파일에서 optional-dependencies 목록을 읽어옵니다.
    
    Args:
        pyproject_path: pyproject.toml 파일 경로. None이면 현재 디렉토리에서 찾습니다.
        groups: 포함할 optional dependency 그룹 목록. None이면 모든 그룹을 포함합니다.
    
    Returns:
        패키지 이름 리스트 (버전 정보 제거됨)
    """
    if pyproject_path is None:
        pyproject_path = Path.cwd() / "pyproject.toml"
    else:
        pyproject_path = Path(pyproject_path)
    
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml 파일을 찾을 수 없습니다: {pyproject_path}")
    
    if tomllib is None:
        raise ValueError(
            "tomllib 또는 tomli가 필요합니다. "
            "Python 3.11 이상을 사용하거나, 'uv add tomli'로 설치하세요."
        )
    
    # TOML 파일 읽기
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    
    dependencies = []
    
    # [project.optional-dependencies] 섹션
    if "project" in data and "optional-dependencies" in data["project"]:
        optional_deps = data["project"]["optional-dependencies"]
        if isinstance(optional_deps, dict):
            if groups is None:
                # 모든 그룹 포함
                for group_deps in optional_deps.values():
                    if isinstance(group_deps, list):
                        dependencies.extend(group_deps)
            else:
                # 지정된 그룹만 포함
                for group in groups:
                    if group in optional_deps:
                        deps = optional_deps[group]
                        if isinstance(deps, list):
                            dependencies.extend(deps)
    
    # 패키지 이름만 추출
    package_names = [parse_package_name(dep) for dep in dependencies]
    
    return package_names

if __name__ == "__main__":
    print('a')
    print(get_dependencies_from_pyproject())
    print('a')
    print(get_optional_dependencies_from_pyproject())