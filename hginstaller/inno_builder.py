import re
import subprocess
import os
import shutil
from pathlib import Path
from .hg_settings import LocalSettings

# 패키지 내부의 template.iss 파일 경로 가져오기
try:
    # Python 3.9+
    from importlib.resources import files
    _TEMPLATE_ISS_PATH = files('hginstaller').joinpath('template.iss')
except ImportError:
    # Python 3.8
    import importlib.resources as pkg_resources
    _TEMPLATE_ISS_PATH = None  # 동적으로 처리

def check_inno_setup(iss_config:dict):
    print("check_inno_setup")
    iss_path = iss_config["iss_path"]
    if os.path.exists(iss_path):
        return True
    else:
        return False

def _get_template_iss_content() -> str:
    """패키지 내부의 template.iss 파일 내용을 읽어온다."""
    try:
        # Python 3.9+
        if _TEMPLATE_ISS_PATH is not None:
            return _TEMPLATE_ISS_PATH.read_text(encoding='utf-8')
    except (AttributeError, TypeError):
        pass
    
    # Python 3.8 또는 fallback: __file__ 기준으로 찾기
    try:
        import importlib.resources as pkg_resources
        with pkg_resources.path('hginstaller', 'template.iss') as template_path:
            return Path(template_path).read_text(encoding='utf-8')
    except (ImportError, FileNotFoundError):
        # 최후의 수단: 현재 파일 기준 상대 경로
        current_dir = Path(__file__).parent
        template_path = current_dir / 'template.iss'
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        else:
            raise FileNotFoundError(f"template.iss 파일을 찾을 수 없습니다: {template_path}")


def init_iss(iss_config: dict = None):
    """패키지 내부의 template.iss를 프로젝트로 복사하고 #define 값을 치환한다.
    
    - 패키지 내부의 template.iss 파일을 프로젝트의 build_src_path로 복사
    - 상단의 TEMP_* 플레이스홀더를 실제 값으로 치환
    """
    build_config = LocalSettings.load("build_config")
    iss_config = LocalSettings.load("iss_config")
    
    # 설정 값 추출
    app_name = build_config["program_name"]
    app_version = build_config["program_version"]
    app_publisher = iss_config["app_publisher"]
    app_url = iss_config["app_url"]
    app_exe_name = app_name + ".exe"
    project_folder = str(build_config["project_path"])
    app_id = gen_appid()
    
    # 패키지 내부의 template.iss 내용 읽기
    template_content = _get_template_iss_content()
    
    # #define 값 치환
    content = template_content.replace("TEMP_APP_NAME", app_name)
    content = content.replace("TEMP_APP_VERSION", app_version)
    content = content.replace("TEMP_PUBLISHER", app_publisher)
    content = content.replace("TEMP_URL", app_url)
    content = content.replace("TEMP_APPEXE_NAME", app_exe_name)
    content = content.replace("TEMP_PROJECT_PATH", project_folder)
    content = content.replace("TEMP_APP_ID", app_id)
    
    # 프로젝트의 build_src_path에 .iss 파일 생성
    build_src_path = Path(build_config["build_src_path"])
    build_src_path.mkdir(parents=True, exist_ok=True)
    iss_path = build_src_path / f"{app_name}.iss"
    
    iss_path.write_text(content, encoding='utf-8')
    print(f"✅ Inno Setup 스크립트 생성 완료: {iss_path}")
    
    return str(iss_path)
    


def run_inno():
    """Inno Setup 스크립트를 생성하고 컴파일한다.
    
    - init_iss()로 .iss 파일이 없으면 생성
    - Inno Setup 컴파일러로 .iss 파일을 컴파일하여 설치 파일 생성
    """
    build_config = LocalSettings.load("build_config")
    
    app_name = build_config["program_name"]
    build_src_path = Path(build_config["build_src_path"])
    iss_file_path = build_src_path / f"{app_name}.iss"
    
    # .iss 파일이 없으면 생성
    if not iss_file_path.exists():
        print(f"### Inno Setup 스크립트 생성 ###")
        init_iss()
    
    # Inno Setup 컴파일러 경로 확인 (GlobalSettings에서 가져오기)
    from .hg_settings import GlobalSettings
    global_iss_config = GlobalSettings.load("iss")
    if not global_iss_config or "iss_path" not in global_iss_config:
        raise FileNotFoundError("Inno Setup 컴파일러 경로가 설정되지 않았습니다. HgInstaller.set_iss_path()를 먼저 호출하세요.")
    
    iscc_path = global_iss_config["iss_path"]
    if not os.path.exists(iscc_path):
        raise FileNotFoundError(f"Inno Setup 컴파일러를 찾을 수 없습니다: {iscc_path}")
    
    # Inno Setup 컴파일 실행
    print(f"### Inno Setup 컴파일 시작 ###")
    print(f"스크립트: {iss_file_path}")
    subprocess.run([iscc_path, str(iss_file_path)], check=True)
    print(f"~~~ Inno Setup 컴파일 완료 ~~~")
        

def gen_appid():
    import uuid
    new_guid = str(uuid.uuid4()).upper()
    return new_guid



# 사용 예시
if __name__ == "__main__":
    run_inno(iss_config)
