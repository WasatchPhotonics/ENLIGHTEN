@echo off

python3.11 -u scripts\bootstrap\win11\bootstrap.py --arg log-level=debug 2>enlighten.err 1>enlighten.out
