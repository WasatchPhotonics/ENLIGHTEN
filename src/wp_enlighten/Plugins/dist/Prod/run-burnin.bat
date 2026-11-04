@echo off

REM see https://github.com/WasatchPhotonics/ENLIGHTEN/issues/294 
cd "C:\Program Files\Wasatch Photonics\ENLIGHTEN\Enlighten"

:START

enlighten.exe --plugin Prod.BurnIn --log-append

echo Sleeping 10sec...
timeout /t 10

goto START
