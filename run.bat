@echo off

where /q python3.11
if ERRORLEVEL 1 (
    python     -u scripts\bootstrap\win11\bootstrap.py --arg log-level=debug 2>enlighten.err 1>enlighten.out
) else (
    python3.11 -u scripts\bootstrap\win11\bootstrap.py --arg log-level=debug 2>enlighten.err 1>enlighten.out
)
