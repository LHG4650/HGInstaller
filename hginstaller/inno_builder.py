import re
import subprocess
import os
def update_inno_version(file_path: str, new_version: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 정규식: #define MyAppVersion "2.2.2"
    pattern = r'(#define\s+MyAppVersion\s+")([\d\.]+)(")'

    # 올바른 치환: re.sub에서 람다 사용 → 그룹과 새 버전을 안전하게 결합
    updated_content = re.sub(
        pattern,
        lambda m: f'{m.group(1)}{new_version}{m.group(3)}',
        content
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"MyAppVersion updated to {new_version} in {file_path}")


def build_inno(installer_script: str, iscc_path: str = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"):
    """
    Inno Setup 스크립트(.iss)를 컴파일해서 설치파일(.exe)을 생성한다.
    
    :param installer_script: .iss 파일 경로
    :param iscc_path: Inno Setup Compiler(ISCC.exe) 경로
    """
    if not os.path.isfile(iscc_path):
        raise FileNotFoundError(f"ISCC.exe not found at {iscc_path}")

    if not os.path.isfile(installer_script):
        raise FileNotFoundError(f"Inno script not found at {installer_script}")

    try:
        subprocess.run([iscc_path, installer_script], check=True)
        print("✅ Inno Setup build completed successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Build failed:", e)


# 사용 예시
if __name__ == "__main__":
    iss_file = r"C:\prog\SFDC_WRITER_2\installer_script.iss"
    update_inno_version(iss_file, "2.3.0")
