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
import sys
import os

from datetime import datetime

print(f"{datetime.now()} Bootstrap.py starting")

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--rebuild", action="store_true", help="rebuild environment even if previous run detected")
parser.add_argument("--virtspec", action="store_true", help="support virtual spectrometers")
parser.add_argument("--arg", action="append", help="take multiple name=value args to pass-on to ENLIGHTEN")
parser.epilog = "Example: $ python scripts/bootstrap/win11/bootstrap.py --rebuild --arg log-level=debug"
args = parser.parse_args()

if platform.system() != 'Windows':
    print("This program is intended for the Windows operating system.")
    exit(1)

if sys.getwindowsversion().build < 22000:
    print("This program is intended for Windows 11 or later versions.")
    exit(1)

if not (sys.version_info.major==3 and sys.version_info.minor==11):
    print("This program is intended for Python 3.11.")
    exit(1)

rebuild = args.rebuild or not (os.path.exists('.env') and
                               os.path.exists("enlighten/assets/uic_qrc/enlighten_layout.py"))

if rebuild:
    if not os.path.exists('.env'):
        os.mkdir('.env')

    print(f"{datetime.now()} Creating environment...")
    os.system(sys.executable + " -m venv .env/enlighten")

env_python = ".env/enlighten/Scripts/python"

if rebuild:
    print(f"{datetime.now()} Installing dependencies")
    installer = subprocess.Popen([env_python, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    installer.wait()

    print(f"{datetime.now()} Installing special dependencies")
    installer_special = subprocess.Popen([env_python, '-m', 'pip', 'install', 'pywin32', 'spc_spectra', 'jcamp'])
    installer_special.wait()

os.environ["PYTHONPATH"] = "..\\Wasatch.PY;..\\jcamp;plugins;.;enlighten\\assets\\uic_qrc"
print(f"{datetime.now()} PYTHONPATH = {os.environ['PYTHONPATH']}")

if rebuild:
    print(f"{datetime.now()} (Re)building UI")
    os.environ["VIRTUAL_ENV"] = ".env\\enlighten"
    ui_script = subprocess.Popen(["sh", "scripts/rebuild_resources.sh"])
    ui_script.wait()

    if args.virtspec:
        print("*** Use virtual spectrometer ***")
        uninstall_pyusb = subprocess.Popen([env_python, '-m', 'pip', 'uninstall', 'pyusb'])
        uninstall_pyusb.wait()
        os.environ["PYTHONPATH"] = "..\\pyusb-virtSpec;..\\Wasatch.PY;..\\jcamp;plugins;.;enlighten\\assets\\uic_qrc"

cmd = [env_python, "scripts\\Enlighten.py"]
for arg in args.arg:
    cmd.append(f"--{arg}")
print(f"{datetime.now()} Running: {cmd}")
enlighten = subprocess.Popen(cmd)
enlighten.wait()

print(f"{datetime.now()} Enlighten done")
