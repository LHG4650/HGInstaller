import os
from pathlib import Path
import subprocess

from .hg_settings import GlobalSettings, LocalSettings


class HgInstaller:
    def __init__(self, program_name: str, project_path: str, option:str=None):
        self.program_name = program_name
        self.project_path = Path(project_path)
        self.option = option

        # 로컬 설정에 프로젝트 경로 설정
        LocalSettings.set_project_path(self.project_path)
        if not LocalSettings.is_local_config_exists():
            self._init_config()
        elif option == "init":
            self._init_config()



    def help(self):
        """HGInstaller 사용법을 간단히 출력한다."""
        print("=" * 50)
        print(f"HGInstaller - {self.program_name}")
        print(f"프로젝트 경로 : {self.project_path}")
        print("-" * 50)
        print("1) 기본 설정 파일 생성")
        print("   - 처음 한 번만 필요")
        print("   - 예시:")
        print("       from hginstaller import HgInstaller")
        print("       HgInstaller('프로그램이름', r'프로젝트_루트_경로', option='init')")
        print()
        print("2) 추가 PyInstaller 설정(add_config)")
        print("   - 필요할 때마다 일부만 넣어서 호출 가능")
        print("   - 이미 저장된 값은 유지되고, 새 값만 추가/갱신됨")
        print("   - 예시:")
        print("       hg = HgInstaller('프로그램이름', r'프로젝트_루트_경로')")
        print("       hg.add_config(")
        print("           icon='app.ico',                   # 아이콘 (옵션)")
        print("           add_files=['src/ui/*;src/ui/'],   # datas (옵션)")
        print("           collect_binaries=['pkg'],        # collect_binaries (옵션)")
        print("       )")
        print()
        print("3) 빌드 실행")
        print("   - Py2Pyd → spec 생성 → PyInstaller 순서로 실행")
        print("   - 예시:")
        print("       hg = HgInstaller('프로그램이름', r'프로젝트_루트_경로')")
        print("       hg.run()")
        print("=" * 50)

    def run(self):
        build_config = LocalSettings.load("build_config")
        pyi_config = LocalSettings.load("pyi_config")

        print(f"### Run HG Installer for {self.program_name}")

        # choeck config
        src_path = build_config["src_path"]
        pyd_path = build_config["pyd_path"]

        print(f"### PY2PYD Start ###")
        from .py2pyd import py2pyd
        py2pyd(src_path, pyd_path)
        print(f"~~~ PY2PYD completed ~~~")

        print(f"### Pyinstaller Spec writer Start ###")
        from .pyi_builder import pyi_maker
        pyi_maker(build_config, pyi_config)
        print(f"~~~ Pyinstaller Spec writer completed ~~~")

        print(f"### Pyinstaller Run Start ###")
        spec_path = os.path.join(pyi_config["spec_path"],build_config["program_name"]+".spec")
        subprocess.run(["pyinstaller", "--noconfirm",spec_path], check=True,cwd=build_config["project_path"])
        print(f"~~~ Pyinstaller Run completed ~~~")

    def _init_config(self):
        build_config = {}

        dependencies = self._read_toml()
        iss_exsist = self.check_iss_path()

        build_config["program_name"] = self.program_name
        build_config["project_path"] = self.project_path
        build_config["src_path"] = self.project_path /"src"
        build_config["pyd_path"] = self.project_path /"build_src"/"src_pyd"
        build_config["output_path"] = self.project_path /"output"
        build_config["iss_exsist"] = iss_exsist

        pyi_config = {}
        pyi_config["output_type"] = "onedir"
        pyi_config["console_mode"] = True
        pyi_config["spec_path"] = self.project_path / "build_src"
        pyi_config["icon_path"] = None
        pyi_config["add_data"] = ["build_src/src_pyd/*;."]
        pyi_config["hidden_imports"] = dependencies
        pyi_config["collect_data"] = []
        pyi_config["collect_binary"] = []
        pyi_config["collect_submodules"] = []
        pyi_config["collect_all"] = []
        pyi_config["exclude_module"] = []
        pyi_config["main_py"] = "main.py"   

        LocalSettings.save("build_config", build_config)
        LocalSettings.save("pyi_config", pyi_config)

    def _read_toml(self):
        if not os.path.exists(self.project_path / "pyproject.toml"):
            return []

        from .pyproject_utils import get_dependencies_from_pyproject

        dependencies = get_dependencies_from_pyproject(
            self.project_path / "pyproject.toml"
        )
        return dependencies

    @classmethod
    def set_iss_path(cls,iss_path:str):
        GlobalSettings.save("iss", {"iss_path": iss_path})

    @classmethod
    def check_iss_path(cls):
        iss_config = GlobalSettings.load("iss")
        default_iss_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
        if iss_config == {}:
            print('set iss path 가 필요합니다.')
            if os.path.exists(default_iss_path):
                cls.set_iss_path(default_iss_path)
                print('iss 가 설치되어 있습니다.')
                print(f'set iss path to {default_iss_path}')
                return True
        else:
            if os.path.exists(iss_config["iss_path"]):
                return True
            else:
                print('inno setup 경로를 찾지 못했습니다.')
                print('inno setupt 을 설치하거나 ISCC.exe 의 경로를 설정해주세요.')
                print("ex) HGInstaller.set_iss_path(iss_path)")
        
        return False

    def add_config(
        self,
        icon=None,
        add_files=None,
        collect_files=None,
        collect_binaries=None,
        collect_submodules=None,
        collect_all=None,
        exclude_modules=None,
    ):
        """PyInstaller 관련 설정을 부분적으로/누적해서 갱신한다.

        - 어떤 인자든 None 이면 건너뛰고, 기존 설정 값은 유지된다.
        - 리스트 계열 인자는 기존 리스트에 '중복 없이' 새 값만 추가된다.
        - 여러 번 나누어서 호출해도 누적되면서 동작한다.
        """
        build_config = LocalSettings.load("build_config")
        pyi_config = LocalSettings.load("pyi_config")

        # 아이콘: 값이 넘어오면 교체, 아니면 기존 유지
        if icon:
            pyi_config["icon_path"] = icon

        def _merge_list(key: str, new_values):
            """기존 리스트에 새 값만 append (중복은 무시)."""
            if new_values is None:
                return
            if not isinstance(new_values, (list, tuple)):
                new_values = [new_values]

            exist = pyi_config.get(key) or []
            # 문자열 리스트 기준 중복 제거
            exist_set = set(exist)
            for v in new_values:
                if v not in exist_set:
                    exist.append(v)
                    exist_set.add(v)
            pyi_config[key] = exist

        _merge_list("add_data", add_files)
        _merge_list("collect_data", collect_files)
        _merge_list("collect_binary", collect_binaries)
        _merge_list("collect_submodules", collect_submodules)
        _merge_list("collect_all", collect_all)
        _merge_list("exclude_module", exclude_modules)

        LocalSettings.save("pyi_config", pyi_config)

if __name__ == "__main__":
    program_name = "NX_Logging"
    project_path = r"C:\prog\NX Logging"
    hg_installer = HgInstaller(program_name, project_path)
    
    hg_installer.run()
    