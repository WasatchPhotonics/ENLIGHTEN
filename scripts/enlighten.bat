@echo off

rem resolves Python logging errors when messages contain Unicode characters
set PYTHONUTF8=1

rem helps with high-DPI widget sizing
set QT_AUTO_SCREEN_SCALE_FACTOR=1

@taskkill /f /im Enlighten.exe  /t 2> NUL
@taskkill /f /im KIAConsole.exe /t 2> NUL

enlighten.exe %1 %2 %3 %4 %5 %6 %7 %8 %9

@taskkill /f /im Enlighten.exe  /t 2> NUL
@taskkill /f /im KIAConsole.exe /t 2> NUL

REM pause
