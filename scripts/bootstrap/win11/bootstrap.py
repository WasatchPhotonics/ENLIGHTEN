################################################################################
#                         Enlighten Windows 11 Bootstrap
################################################################################
#
# Author: Samie Bee 2024
# 
# Invocation: 
# 
# $ python scripts\boostrap\win11\bootstrap.py
#
# Description: 
#
# This script will initialize a development environment of Enlighten on Windows
# 11. If an environment already exists it will launch Enlighten from source.
#
# A number of dependencies will be installed into a python virtual environment
# (venv). 
#
# This installer was written for Enlighten 4.1.6.
# It has been tested on Windows 11 version 10.0.22631
################################################################################

import subprocess
import platform
import argparse
import shutil
import sys
import os

from datetime import datetime

is_win = platform.system() == 'Windows'
is_mac = platform.system() == 'Darwin'

def fix_path(path):
    return path if is_win else path.replace("\\", "/").replace(";", ":")

def check_if_ui_rebuild_needed():
    checkfile = "enlighten/assets/uic_qrc/__init__.py"
    if not os.path.exists(checkfile):
        return True

    last_rebuild_time = os.path.getmtime(checkfile)
    path = "enlighten/assets/uic_qrc"
    for filename in os.listdir(path):
        if filename.endswith(".ui") or filename.endswith(".qrc"):
            pathname = os.path.join(path, filename)
            mtime = os.path.getmtime(pathname)
            if mtime > last_rebuild_time:
                print(f"rebuild required ({pathname} newer than {checkfile}")
                return True

    pathname = "enlighten/assets/stylesheets/dark/enlighten.css"
    if os.path.getmtime(pathname) > last_rebuild_time:
        print(f"rebuild required ({pathname} newer than {checkfile}")
        return True

print(f"{datetime.now()} Bootstrap.py starting")

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--rebuild-env", action="store_true", help="rebuild environment even if previous run detected")
parser.add_argument("--rebuild-ui", action="store_true", help="rebuild Qt files even if source files unchanged")
parser.add_argument("--force", action="store_true", help="ignore script warnings")
parser.add_argument("--virtspec", action="store_true", help="support virtual spectrometers")
parser.add_argument("--arg", action="append", help="take multiple name=value args to pass-on to ENLIGHTEN")
parser.epilog = "Example: $ python scripts/bootstrap/win11/bootstrap.py --rebuild --arg log-level=debug"
args = parser.parse_args()

if not (is_win or is_mac or args.force):
    print("This program has only been tested on Win11 and MacOS (Intel/ARM)...add --force to use on other environments.")
    exit(1)

if (is_win and sys.getwindowsversion().build < 22000) and not args.force:
    print("On Windows, this program is intended for Windows 11 or later versions.")
    exit(1)

if not (sys.version_info.major==3 and sys.version_info.minor==11) and not args.force:
    print("This program is intended for Python 3.11.")
    exit(1)

env_dir = '.env'
rebuild_ui = args.rebuild_ui
rebuild_env = args.rebuild_env or not (os.path.exists(env_dir) and
                                       os.path.exists("enlighten/assets/uic_qrc/enlighten_layout.py"))

if rebuild_env:
    rebuild_ui = True
if not rebuild_ui:
    rebuild_ui = check_if_ui_rebuild_needed()

if rebuild_env:
    if args.force:
        shutil.rmtree(env_dir)
    if not os.path.exists(env_dir):
        os.makedirs(env_dir)

    print(f"{datetime.now()} Creating environment...")
    os.system(sys.executable + f" -m venv {env_dir}/enlighten")

if is_win:
    env_python = f"{env_dir}/enlighten/Scripts/python"
else:
    env_python = f"{env_dir}/enlighten/bin/python"

if rebuild_env:
    print(f"{datetime.now()} Installing dependencies")
    installer = subprocess.Popen([env_python, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    installer.wait()

    print(f"{datetime.now()} Installing special dependencies")
    tok = [env_python, '-m', 'pip', 'install', 'spc_spectra', 'jcamp']
    if is_win:
        tok.append('pywin32')
    installer_special = subprocess.Popen(tok)
    installer_special.wait()

os.environ["PYTHONPATH"] = fix_path("..\\Wasatch.PY;..\\jcamp;plugins;.;enlighten\\assets\\uic_qrc")
print(f"{datetime.now()} PYTHONPATH = {os.environ['PYTHONPATH']}")

if rebuild_ui:
    print(f"{datetime.now()} (Re)building UI")
    os.environ["VIRTUAL_ENV"] = fix_path(f"{env_dir}\\enlighten")
    ui_script = subprocess.Popen(["sh", "scripts/rebuild_resources.sh", "--bootstrap"])
    ui_script.wait()

if args.virtspec:
    print("*** Use virtual spectrometer ***")
    uninstall_pyusb = subprocess.Popen([env_python, '-m', 'pip', 'uninstall', 'pyusb'])
    uninstall_pyusb.wait()
    os.environ["PYTHONPATH"] = fix_path("..\\pyusb-virtSpec;..\\Wasatch.PY;..\\jcamp;plugins;.;enlighten\\assets\\uic_qrc")

cmd = [env_python, fix_path("scripts\\Enlighten.py")]
if args.arg:
    for arg in args.arg:
        cmd.append(f"--{arg}")

print(f"{datetime.now()} Running: {cmd}")
enlighten = subprocess.Popen(cmd)
enlighten.wait()

print(f"{datetime.now()} Enlighten done")
