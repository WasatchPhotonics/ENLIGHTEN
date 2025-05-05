import subprocess
import sys
import platform
from pathlib import Path

def embed_stylesheet():
    print("Embedding stylesheet...")
    subprocess.run([sys.executable, 'scripts/embed_stylesheet.py'], check=True)

    if platform.system() == 'Linux':
        ui_file = Path('enlighten/assets/uic_qrc/enlighten_layout.ui')
        subprocess.run(['unix2dos', str(ui_file)], check=True)
        print(f"Converted line endings in {ui_file}")

def convert_qt_files():
    uic = "pyside6-uic"
    rcc = "pyside6-rcc"

    for qrc_file in Path('.').glob('**/assets/uic_qrc/*.qrc'):
        dest_py = qrc_file.with_name(qrc_file.stem + "_rc.py")
        print(f"Converting resource file {qrc_file} -> {dest_py}")
        subprocess.run([rcc, str(qrc_file), '-o', str(dest_py)], check=True)

    for ui_file in Path('.').glob('**/assets/uic_qrc/*.ui'):
        dest_py = ui_file.with_suffix('.py')
        print(f"Converting UI file {ui_file} -> {dest_py}")
        subprocess.run([uic, '--from-imports', str(ui_file), '-o', str(dest_py)], check=True)

    uic_qrc_dirs = set(f.parent for f in Path('.').glob('**/assets/uic_qrc/*.ui'))
    for d in uic_qrc_dirs:
        init_py = d / "__init__.py"
        init_py.touch()
        print(f"Ensured Python module by touching {init_py}")

if __name__ == "__main__":
    embed_stylesheet()
    convert_qt_files()