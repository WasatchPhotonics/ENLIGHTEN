@echo off

:START

python scripts\Enlighten.py --log-level debug --plugin Prod.BurnIn 1>>enlighten.out 2>>enlighten.err

echo Sleeping 10 sec...ctrl-C to cancel
sleep 10

goto START
