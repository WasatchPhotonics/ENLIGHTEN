@echo off
rem python -X utf8 scripts\Enlighten.py --log-append False --log-level debug 1>enlighten.out 2>enlighten.err
python scripts\bootstrap\win11\bootstrap.py 2>enlighten.err 1>enlighten.out
