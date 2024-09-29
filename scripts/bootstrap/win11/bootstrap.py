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

import platform, sys, os, subprocess

if platform.system() != 'Windows':
    print("This program is intended for the Windows operating system.")
    exit(1)

if sys.getwindowsversion().build < 22000:
    print("This program is intended for Windows 11 or later versions.")
    exit(1)

if not (sys.version_info.major==3 and sys.version_info.minor==11):
    print("This program is intended for Python 3.11.")
    exit(1)

if not os.path.exists('.env'):
    os.mkdir('.env')

print("Creating environment...")

os.system(sys.executable + " -m venv .env/enlighten")

print("Activating environment...")

env_python = ".env/enlighten/Scripts/python"

print("Installing dependencies")

installer = subprocess.Popen([env_python, '-m', 'pip', 'install', '-r', 'requirements.txt'])
installer.wait()

print("Installing special dependencies")

installer_special = subprocess.Popen([env_python, '-m', 'pip', 'install', 'pywin32', 'spc_spectra', 'jcamp'])
installer_special.wait()

print("Setting PYTHONPATH")

os.environ["PYTHONPATH"] = "..\\Wasatch.PY;..\\jcamp;plugins;.;enlighten\\assets\\uic_qrc"

print("(Re)building UI")

os.environ["VIRTUAL_ENV"] = ".env\\enlighten"
ui_script = subprocess.Popen(["sh", "scripts/rebuild_resources.sh"])
ui_script.wait()

print("Run Enlighten")

enlighten = subprocess.Popen([env_python, "scripts\\Enlighten.py"])
enlighten.wait()
