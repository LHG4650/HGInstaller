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
        pass

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
        subprocess.run(["pyinstaller", spec_path], check=True,cwd=build_config["project_path"])
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
        pyi_config["add_data"] = ["src_pyd/*;."]
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



if __name__ == "__main__":
    program_name = "NX_Logging"
    project_path = r"C:\prog\NX Logging"
    hg_installer = HgInstaller(program_name, project_path)
    
    hg_installer.run()
    