"""
HGInstaller - Python 빌드 자동화 도구

PyInstaller, Inno Setup, UI 변환, PYD 변환 등을 자동화하는 라이브러리
"""

__version__ = "0.1.0"

from .build_config import *
from .build_util import (
    get_latest_modified_time,
    get_file_modified_time,
    modified_time_read,
    modified_time_save,
)
from .del_temp import delete_all_in_dir, delete_files_by_extension
from .inno_builder import build_inno, update_inno_version
from .py2pyd import build_pyd_in_dir
from .pyi_builder import *
from .ui2py import convert_ui_to_py, convert_all_ui_files_in_directory

__all__ = [
    # build_config
    "PROGRAM_NAME",
    "SRC_PATH",
    "PYD_PATH",
    "UI_PATH",
    "BUILD_SRC_PATH",
    "SPEC_PATH",
    "build_path",
    "MAIN_PY",
    "BUILD_MODE_ONEFILE",
    "CONSOLE_MODE",
    "ICON_ICO",
    "ADD_DATA",
    "HIDDEN_IMPORT",
    "COLLECT_DATA",
    "COLLECT_BINARY",
    "COLLECT_SUBMODULES",
    "COLLECT_ALL",
    "EXCLUDE_MODULE",
    "ISS_PATH",
    "OUTPUT_PATH",
    # build_util
    "get_latest_modified_time",
    "get_file_modified_time",
    "modified_time_read",
    "modified_time_save",
    # del_temp
    "delete_all_in_dir",
    "delete_files_by_extension",
    # inno_builder
    "build_inno",
    "update_inno_version",
    # py2pyd
    "build_pyd_in_dir",
    # ui2py
    "convert_ui_to_py",
    "convert_all_ui_files_in_directory",
]

