@echo off

:START

"C:\Program Files\Wasatch Photonics\ENLIGHTEN\Enlighten\enlighten.exe" --plugin Prod.BurnIn --log-append

echo Sleeping 10sec...
timeout /t 10

goto START
