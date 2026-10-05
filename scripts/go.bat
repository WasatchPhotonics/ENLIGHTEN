@echo off

rem note Windows Python may be in %HOME%\AppData\Local\Programs\Python\Python311

set VENV=.env\enlighten
set FW_UTIL=%HOME%\AppData\Local\Programs\Wasatch Photonics\Firmware Update Utility

set PATH=C:\Program Files\Git\usr\bin;%PATH%
set PATH=%FW_UTIL%;%PATH%
set PATH=%VENV%\Scripts;%PATH%

cd work\code\enlighten
set PYTHONPATH=..\Wasatch.PY;.;plugins;enlighten\assets\uic_qrc;..\jcamp
echo PYTHONPATH = %PYTHONPATH%
echo Use scripts\bootstrap\win11\make_windows_installer.bat
echo Use run.bat for: python -u scripts\Enlighten.py --log-level debug 1^>enlighten.out 2^>enlighten.err
%VENV%\Scripts\activate
