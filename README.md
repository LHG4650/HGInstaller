## HGInstaller

Python 프로젝트의 배포 과정을 자동화해 주는 **빌드 유틸리티 라이브러리**입니다.

- **PyInstaller** 스펙 생성 및 빌드 지원
- **Inno Setup** 설치 파일 빌드 헬퍼
- `.py` → `.pyd` 변환(Python 확장 모듈 빌드)
- Qt Designer `.ui` → `.py` 변환 등

`HGInstaller`를 사용하면 기존 프로젝트 폴더에 약간의 설정만 추가해서, 빌드 파이프라인을 스크립트 하나로 묶어 관리할 수 있습니다.

---

### 설치

아직 PyPI에는 올리지 않았으므로, GitHub 주소로 직접 설치합니다.

```bash
pip install git+https://github.com/LHG4650/HGInstaller.git
```

또는 개발 중에는 로컬에서 editable 모드로 설치할 수 있습니다.

```bash
# 프로젝트 루트에서
pip install -e .
```

---

### 기본 사용법

`hginstaller.HgInstaller` 클래스를 사용해, 특정 프로그램에 대한 빌드 설정을 만들고 실행합니다.

```python
from hginstaller.hg_installer import HgInstaller

# 예시: "NX_Logging" 이라는 프로그램을 빌드한다고 가정
program_name = "NX_Logging"
project_path = r"C:\prog\NX Logging"  # 실제 프로젝트 루트 경로

# 처음 한 번은 option="init" 으로 기본 설정 파일 생성
installer = HgInstaller(program_name, project_path, "init")

# 이후에는 그냥 run() 만 호출하면
# 1) .py → .pyd 빌드
# 2) PyInstaller spec 생성/수정
# 3) PyInstaller 실행까지 한 번에 수행
installer.run()
```

프로젝트 루트에는 일반적으로 다음과 같은 구조를 가정합니다.

```text
project_root/
  src/              # 소스 코드
  build_src/        # HGInstaller 가 사용하는 중간 빌드 디렉토리
  output/           # 최종 결과물(실행 파일 등)
  pyproject.toml    # 의존성 정의 파일
```

`pyproject.toml` 의 `[project.dependencies]` 에 적힌 패키지들은 자동으로 PyInstaller의 `hidden_imports` 에 반영되어, 의존성 누락으로 인한 빌드 실패를 줄여 줍니다.

---

### 설정 파일(HGSettings.json)

HGInstaller는 **글로벌/로컬 설정 파일**을 사용해 빌드 구성을 저장합니다.

- 로컬 설정: 각 프로젝트 폴더 안의 `HGSettings.json`
- 글로벌 설정: 사용자 설정 디렉토리(`platformdirs.user_config_dir`) 아래 저장

`hg_settings.LocalSettings` / `hg_settings.GlobalSettings` 클래스를 통해 직접 읽고 쓸 수도 있습니다.

---

### 라이선스

이 프로젝트는 **MIT License**를 따릅니다.
