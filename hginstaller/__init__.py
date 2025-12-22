"""
HGInstaller - Python 빌드 자동화 도구

PyInstaller, Inno Setup, UI 변환, PYD 변환 등을 자동화하는 라이브러리.

가장 자주 쓰는 것은 `HgInstaller` 클래스이며, 필요 시 개별 유틸리티도 직접 import 해서 사용할 수 있습니다.
"""

__version__ = "0.1.1"

# 메인 클래스
from .hg_installer import HgInstaller

# 설정 관리
from .hg_settings import LocalSettings, GlobalSettings

# PyInstaller 빌드 유틸리티
from .pyi_builder import pyi_maker

# PYD 변환
from .py2pyd import py2pyd

# Inno Setup 빌드 유틸리티
from .inno_builder import init_iss, run_inno

# UI 변환
from .ui2py import convert_ui_to_py, convert_all_ui_files_in_directory

# pyproject.toml 유틸리티
from .pyproject_utils import (
    get_dependencies_from_pyproject,
    get_optional_dependencies_from_pyproject,
)

__all__ = [
    # 버전
    "__version__",
    # 메인 클래스
    "HgInstaller",
    # 설정 관리
    "LocalSettings",
    "GlobalSettings",
    # PyInstaller
    "pyi_maker",
    # PYD 변환
    "py2pyd",
    # Inno Setup
    "init_iss",
    "run_inno",
    # UI 변환
    "convert_ui_to_py",
    "convert_all_ui_files_in_directory",
    # pyproject.toml 유틸리티
    "get_dependencies_from_pyproject",
    "get_optional_dependencies_from_pyproject",
]
