#!/bin/sh

# A quick script to bring up the Qt Designer

FILE="enlighten/assets/uic_qrc/enlighten_layout.ui"

# on MacOS, found in /usr/local/bin/pyside6-designer (not using venv)
# on Windows, found in /c/Users/mzieg/enlighten_py311/Scripts/pyside6-designer
# (%VIRTUAL_ENV%\Scripts)
pyside6-designer $FILE
