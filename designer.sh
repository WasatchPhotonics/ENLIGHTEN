#!/bin/sh

# A quick script to quickly bring up the Qt Designer

FILE="enlighten/assets/uic_qrc/enlighten_layout.ui"

if uname -s | grep -q '^Darwin'
then
    # On MacOS, you can install the Designer with "conda install pyqt"
    # $CONDA_PREFIX/bin/Designer.app/Contents/MacOS/Designer $FILE

    # or you can get it from "pip install PySide6"
    /usr/local/bin/pyside6-designer $FILE
else
    # This comes up right away on Win10, but takes ~20sec on 
    # Ubuntu...?
    designer $FILE
fi
