@echo off

REM Zieg has this script in his C:\Users\mzieg Windows directory, so when he 
REM opens a new Git Command Window, he can just type "go-installer" to build
REM a new installer.
REM
REM This assumes your repo is cloned at Z:\work\code\enlighten

Z:
cd \work\code\enlighten
set PYTHONUTF8=1
scripts\bootstrap.bat installer 2>build.err | tee build.out
