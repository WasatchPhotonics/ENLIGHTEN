@echo off

:START

"C:\Program Files\Wasatch Photonics\ENLIGHTEN\Enlighten\enlighten.exe" --plugin Prod.BurnIn

echo Sleeping 10sec...
sleep 10

goto START
