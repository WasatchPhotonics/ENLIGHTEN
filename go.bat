@echo off

z:
cd \work\code\enlighten

set PATH=C:\Program Files\Git\usr\bin;%PATH%
set PYTHONPATH=.;..\Wasatch.PY;.\plugins;enlighten\assets\uic_qrc;..\jcamp

echo PYTHONPATH = %PYTHONPATH%
echo Use run.bat for: python3.11 -u scripts\bootstrap\win11\bootstrap.py --arg log-level=debug 2^>enlighten.err 1^>enlighten.out
