import subprocess
import sys
import os
from pathlib import Path

def pyi_maker(build_config: dict ,  pyi_config:dict):
    program_name = build_config["program_name"]
    project_path = Path(build_config["project_path"])

    output_type = pyi_config["output_type"]
    console_mode = pyi_config["console_mode"]
    spec_path = Path(build_config["build_src_path"])

    main_py = pyi_config["main_py"]

    cmd = ["pyi-makespec"]
    # - main.py 

    # # - spec path
    cmd += ["--specpath", str(spec_path)]

    # - output type
    if output_type in ["onefile","onedir"]:
        cmd.append(f"--{output_type}")
    else:
        raise ValueError(f"Invalid output type : {output_type} / Allowed : onefile, onedir")

    if console_mode == True:
        cmd.append("--console")
    elif console_mode == False:
        cmd.append("--noconsole")
    else:
        raise ValueError(f"Invalid console mode : {console_mode} / Allowed : True, False")

    # # - name 프로그램 이름
    cmd += ["--name", program_name]

    # # - icon 아이콘 경로
    icon_path = pyi_config.get("icon_path")
    if icon_path:
        # icon_path도 절대 경로로 변환
        icon_path_obj = Path(icon_path)
        if not icon_path_obj.is_absolute():
            icon_path_obj = project_path / icon_path_obj
        cmd += ["--icon", str(icon_path_obj)]

    # # - hidden imports: pyproject.toml의 dependencies 자동 추가
    hidden_imports = pyi_config.get("hidden_imports", [])
    for mod in hidden_imports:
        cmd += ["--hidden-import", mod]

    # # - add_data, collect_data 등 다른 옵션들도 추가
    add_data = pyi_config.get("add_data", [])
    for data in add_data:
        # add_data 경로를 프로젝트 루트 기준 절대 경로로 변환
        # 형식: "src/ui/*;src/ui/" 또는 "src/ui/*;."
        if ":" in data:
            src_path, dest_path = data.split(":", 1)
        else:
            src_path, dest_path = data, "."
        
        # src_path가 절대 경로가 아니면 프로젝트 루트 기준으로 변환
        # 와일드카드(*)가 포함될 수 있으므로 문자열로 처리
        if not Path(src_path).is_absolute():
            # 프로젝트 루트와 결합 (와일드카드 유지)
            src_path_abs = str(project_path / src_path)
        else:
            src_path_abs = src_path
        
        # 절대 경로를 문자열로 변환 (Windows 경로 처리)
        normalized_data = f"{src_path_abs};{dest_path}"
        cmd += ["--add-data", normalized_data]
    
    collect_data = pyi_config.get("collect_data", [])
    for data in collect_data:
        cmd += ["--collect-data", data]

    collect_binary = pyi_config.get("collect_binary", [])
    for data in collect_binary:
        cmd += ["--collect-binaries", data]

    collect_submodules = pyi_config.get("collect_submodules", [])
    for data in collect_submodules:
        cmd += ["--collect-submodules", data]

    collect_all = pyi_config.get("collect_all", [])
    for data in collect_all:
        cmd += ["--collect-all", data]

    exclude_module = pyi_config.get("exclude_module", [])
    for data in exclude_module:
        cmd += ["--exclude-module", data]   


    # pyi-makespec 실행
    cmd += [main_py]
    print('='*30)
    print("실행할 명령어:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, cwd=str(project_path))
        print('='*30)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

    


    # # - console mode


    # # - name

    # # - icon

    # # - hidden imports: pyproject.toml의 dependencies 자동 추가
    
    # # pyproject.toml에서 dependencies 읽어오기
    

    # # hidden imports 추가
    # for mod in hidden_imports:
    #     cmd += ["--hidden-import", mod]

    # # add_data, collect_data 등 다른 옵션들도 추가
    # add_data = pyi_config.get("add_data", [])
    # for data in add_data:
    #     cmd += ["--add-data", data]
    
    # collect_data = pyi_config.get("collect_data", [])
    # for pkg in collect_data:
    #     cmd += ["--collect-data", pkg]
    
    # collect_binary = pyi_config.get("collect_binary", [])
    # for pkg in collect_binary:
    #     cmd += ["--collect-binaries", pkg]
    
    # collect_submodules = pyi_config.get("collect_submodules", [])
    # for pkg in collect_submodules:
    #     cmd += ["--collect-submodules", pkg]
    
    # collect_all = pyi_config.get("collect_all", [])
    # for pkg in collect_all:
    #     cmd += ["--collect-all", pkg]
    
    # exclude_module = pyi_config.get("exclude_module", [])
    # for mod in exclude_module:
    #     cmd += ["--exclude-module", mod]

    # cmd.append(pyi_config["main_py"])

    # # pyi-makespec 실행
    # print("실행할 명령어:", " ".join(cmd))
    # subprocess.run(cmd, check=True)

    # # --- spec 파일 수정 ---
    # spec_file = os.path.join(spec_path, f"{program_name}.spec")
    # print(f"생성된 spec 파일 수정 중: {spec_file}")

    # if not os.path.exists(spec_file):
    #     print("spec 파일이 생성되지 않았습니다!", file=sys.stderr)
    #     sys.exit(1)

    # with open(spec_file, "r", encoding="utf-8") as f:
    #     spec_content = f.read()

    # # datas 수정
    # datas_block = []
    # for d in add_data:
    #     if ";" in d:
    #         src, dest = d.split(";", 1)
    #         datas_block.append(f"('{src}', '{dest}')")
    #     else:
    #         datas_block.append(f"('{d}', '.')")
    # datas_str = f"[{', '.join(datas_block)}]" if datas_block else "[]"

    # # hiddenimports 수정
    # hidden_str = f"{hidden_imports}" if hidden_imports else "[]"

    # # binaries 수정
    # binaries_block = []
    # for b in collect_binary:
    #     binaries_block.append(f"('{b}', '.')")
    # binaries_str = f"[{', '.join(binaries_block)}]" if binaries_block else "[]"

    # # excludes 수정
    # exclude_str = f"{exclude_module}" if exclude_module else "[]"

    # # replace (기본 패턴 기준)
    # spec_content = spec_content.replace("datas=[]", f"datas={datas_str}")
    # spec_content = spec_content.replace("hiddenimports=[]", f"hiddenimports={hidden_str}")
    # spec_content = spec_content.replace("binaries=[]", f"binaries={binaries_str}")
    # spec_content = spec_content.replace("excludes=[]", f"excludes={exclude_str}")

    # with open(spec_file, "w", encoding="utf-8") as f:
    #     f.write(spec_content)

    # print("✅ spec 파일 자동 수정 완료 (빌드는 하지 않음)")
    # print(f"👉 {spec_file} 파일을 확인한 후, 필요 시 아래 명령어로 빌드하세요:")
    # print(f"   pyinstaller {spec_file}")

    

if __name__ == "__main__":
    build_config = {
        "program_name": "NX_Logging",
        "project_path": "C:\\prog\\HG_Installer\\TEST",
        "src_path": "C:\\prog\\HG_Installer\\TEST\\src",
        "pyd_path": "C:\\prog\\HG_Installer\\TEST\\src_pyd",
        "output_path": "C:\\prog\\HG_Installer\\TEST\\output",
        "iss_exsist": True
        }  
    pyi_config =  {
        "output_type": "onedir",
        "console_mode": True,
        "spec_path": "C:\\prog\\HG_Installer\\TEST\\build_src",
        "icon_path": None,
        "add_data": [
        "build_src/src_pyd/*;."
        ],
        "hidden_imports": [
        "tqdm",
        "Cython",
        "setuptools",
        "platformdirs"
        ],
        "collect_data": [],
        "collect_binary": [],
        "collect_submodules": [],
        "collect_all": [],
        "exclude_module": [],
        "main_py": "main.py"
    }
    pyi_maker(build_config,pyi_config)