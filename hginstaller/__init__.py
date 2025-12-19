"""
HGInstaller - Python 빌드 자동화 도구

PyInstaller, Inno Setup, UI 변환, PYD 변환 등을 자동화하는 라이브러리
"""

__version__ = "0.1.0"

# 메인 클래스
from .hg_installer import HgInstaller

# 설정 관리
from .hg_settings import LocalSettings, GlobalSettings

# PyInstaller 빌드
from .pyi_builder import pyi_maker

# PYD 변환
from .py2pyd import py2pyd

# Inno Setup 빌드
from .inno_builder import build_inno, update_inno_version

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
    "build_inno",
    "update_inno_version",
    # UI 변환
    "convert_ui_to_py",
    "convert_all_ui_files_in_directory",
    # pyproject.toml 유틸리티
    "get_dependencies_from_pyproject",
    "get_optional_dependencies_from_pyproject",
]
