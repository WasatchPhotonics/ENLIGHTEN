@echo off

REM Zieg has this script in his C:\Users\mzieg Windows directory, so when he 
REM opens a new Git Command Window, he can just type "go" to prepare everything
REM for ENLIGHTEN development and testing.
REM
REM This assumes your repo is cloned at Z:\work\code\enlighten

z:
cd work\code\enlighten

set PATH=%HOME%\miniconda3;%HOME%\miniconda3\scripts;%HOME%\miniconda3\library\bin;%PATH%

REM I don't think these are used by standard ENLIGHTEN development.
set PATH=C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools;%PATH%
set PATH=C:\Windows\Microsoft.NET\Framework64\v4.0.30319;%PATH%
set PATH=C:\Program Files\Microsoft\R Client\R_SERVER\bin\x64;%PATH%
set PATH=C:\Program Files (x86)\SEGGER\JLink;%PATH%

set PYTHONPATH=.;z:\work\code\Wasatch.PY;.\pluginExamples
set QT_PLUGIN_PATH=%HOME%\Miniconda3\envs\conda_enlighten3\Lib\site-packages\PyQt5\Qt\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=%HOME%\Miniconda3\envs\conda_enlighten3\Lib\site-packages\PyQt5\Qt\plugins
set R_LIBS_USER=Z:\Documents\R\win-library\3.3

echo PYTHONPATH = %PYTHONPATH%
echo QT_PLUGIN_PATH = %QT_PLUGIN_PATH%
echo R_LIBS_USER = %R_LIBS_USER%

echo Use run.bat for: python -u scripts\Enlighten.py --log-level debug 1^>enlighten.out 2^>enlighten.err
echo activating Conda environment conda_enlighten3
activate conda_enlighten3
rem setx prompt $T$H$H$H$S$P$G
