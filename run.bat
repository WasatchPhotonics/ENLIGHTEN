@echo off

REM This is for DOS Command Prompt development environments

REM Note be sure to do this, or run with -X utf8 
set PYTHONUTF8=1
set QT_AUTO_SCREEN_SCALE_FACTOR=1

python scripts\Enlighten.py --log-append False --log-level debug 1>enlighten.out 2>enlighten.err
