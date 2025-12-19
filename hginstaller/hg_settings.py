import json
from abc import ABC, abstractmethod
from pathlib import Path

from platformdirs import user_config_dir


class BaseSettings(ABC):
    """설정 파일을 저장/로드하는 베이스 클래스.
    
    파일 구조 예시:
    {
        "global": {...},
        "program_name_1": {...},
        "program_name_2": {...}
    }
    """
    
    FILENAME = "HGSettings.json"
    
    @classmethod
    @abstractmethod
    def get_path(cls) -> Path:
        """설정 파일의 경로를 반환합니다. 하위 클래스에서 구현해야 합니다."""
        pass
    
    @classmethod
    def _load_all(cls) -> dict:
        """전체 설정 파일(JSON)을 통째로 읽어서 dict 로 반환."""
        p = cls.get_path()
        if not p.is_file():
            return {}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # 파일이 깨져 있으면 안전하게 초기화
            return {}
    
    @classmethod
    def _convert_paths_to_str(cls, obj):
        """Path 객체를 문자열로 변환하는 재귀 함수."""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {key: cls._convert_paths_to_str(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [cls._convert_paths_to_str(item) for item in obj]
        else:
            return obj
    
    @classmethod
    def _save_all(cls, data: dict) -> None:
        """전체 설정 dict 를 파일에 통째로 저장."""
        p = cls.get_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        # Path 객체를 문자열로 변환
        serializable_data = cls._convert_paths_to_str(data)
        p.write_text(json.dumps(serializable_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    @classmethod
    def load(cls, section: str) -> dict:
        """지정한 섹션(global, program_name 등) 하나만 로드.
        
        예)
            Settings.load("global")
            Settings.load("NX_Logging")
        """
        all_data = cls._load_all()
        value = all_data.get(section, {})
        # dict 가 아닐 경우 방어적으로 빈 dict 반환
        return value if isinstance(value, dict) else {}
    
    @classmethod
    def save(cls, section: str, data: dict) -> None:
        """지정한 섹션 하나만 저장 (나머지 섹션은 유지).
        
        예)
            Settings.save("global", {...})
            Settings.save("NX_Logging", {...})
        """
        all_data = cls._load_all()
        all_data[section] = data
        cls._save_all(all_data)


class LocalSettings(BaseSettings):
    """프로젝트 폴더에 로컬 설정 파일을 저장/로드하는 헬퍼.
    
    프로젝트 폴더 내에 Settings.json 파일을 생성하여 프로젝트별 설정을 관리합니다.
    """
    
    _project_path = None
    
    @classmethod
    def set_project_path(cls, project_path: str | Path) -> None:
        """프로젝트 경로를 설정합니다."""
        cls._project_path = Path(project_path)
    
    @classmethod
    def get_path(cls) -> Path:
        """로컬 설정 파일의 경로를 반환합니다."""
        if cls._project_path is None:
            raise ValueError("프로젝트 경로가 설정되지 않았습니다. set_project_path()를 먼저 호출하세요.")
        return cls._project_path / cls.FILENAME

    @classmethod
    def is_local_config_exists(cls) -> bool:
        return cls.get_path().is_file()


class GlobalSettings(BaseSettings):
    """PC의 사용자 설정 디렉토리에 글로벌 설정 파일을 저장/로드하는 헬퍼.
    
    여러 프로젝트에서 공유하는 전역 설정을 관리합니다.
    """
    
    APP_NAME = f"HGSettings"
    APP_AUTHOR = "LHG"
    
    @classmethod
    def get_path(cls) -> Path:
        """글로벌 설정 파일의 경로를 반환합니다."""
        cfg_dir = Path(user_config_dir(cls.APP_NAME, cls.APP_AUTHOR))
        cfg_dir.mkdir(parents=True, exist_ok=True)
        return cfg_dir / cls.FILENAME


if __name__ == "__main__":
    print("=" * 60)
    print("HG Settings 사용법 예시")
    print("\n[1] 로컬 설정 (LocalSettings) - 프로젝트 폴더에 저장")
    project_path = Path(r"C:\prog\HG_Installer\TEST")
    LocalSettings.set_project_path(project_path)
    
    print(f"프로젝트 경로: {project_path}")
    print(f"설정 파일 경로: {LocalSettings.get_path()}")
    
    # 설정 저장
    program_name = "NX_Logging"
    local_config = {
        "program_name": program_name,
        "src_path": str(project_path / "src"),
        "pyd_path": str(project_path / "src_pyd"),
        "output_path": str(project_path / "output"),
        "pyi_output_type": "onedir",
        "pyi_console_mode": True,
    }
    LocalSettings.save(program_name, local_config)
    print(f"✅ 로컬 설정 저장 완료: {program_name}")
    
    # 설정 로드
    loaded_config = LocalSettings.load(program_name)
    print(f"✅ 로컬 설정 로드 완료:")
    for key, value in loaded_config.items():
        print(f"   {key}: {value}")
    
    # ===== 2. 글로벌 설정 (PC 사용자 설정 디렉토리에 저장) =====
    print("-" * 60)
    print("\n[2] 글로벌 설정 (GlobalSettings) - PC에 저장")
    print(f"설정 파일 경로: {GlobalSettings.get_path()}")
    
    # 글로벌 설정 저장
    global_config = {
        "default_output_type": "onedir",
        "default_console_mode": True,
        "last_used_program": program_name,
    }
    GlobalSettings.save("dev", global_config)
    print("✅ 글로벌 설정 저장 완료: global")
    
    # 프로그램별 글로벌 설정 저장
    program_global_config = {
        "version": "1.0.0",
        "author": "LHG",
    }
    GlobalSettings.save(program_name, program_global_config)
    print(f"✅ 글로벌 설정 저장 완료: {program_name}")
    
    # 글로벌 설정 로드
    loaded_global = GlobalSettings.load("global")
    print(f"✅ 글로벌 설정 로드 완료:")
    for key, value in loaded_global.items():
        print(f"   {key}: {value}")
    
    loaded_program = GlobalSettings.load(program_name)
    print(f"✅ 프로그램별 글로벌 설정 로드 완료:")
    for key, value in loaded_program.items():
        print(f"   {key}: {value}")
