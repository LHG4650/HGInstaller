import subprocess
import os

def convert_ui_to_py(ui_file, output_file):
    """pyside6-uic 으로 .ui → .py 변환"""
    command = ['pyside6-uic', ui_file, '-o', output_file]
    try:
        subprocess.run(command, check=True)
        print(f"✅ {ui_file} → {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 변환 실패: {ui_file}, 오류: {e}")

def convert_all_ui_files_in_directory(directory_path):
    """폴더 내부의 모든 .ui 파일을 _ui.py 로 변환"""
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.ui'):
                ui_file = os.path.join(root, file)
                output_file = os.path.splitext(ui_file)[0] + '_ui.py'
                convert_ui_to_py(ui_file, output_file)

if __name__ == "__main__":
    # 변환할 디렉토리 경로 지정
    directory_path = 'src/ui'   # 필요에 맞게 경로 변경
    convert_all_ui_files_in_directory(directory_path)
    print("__Convert UI Complete__")
