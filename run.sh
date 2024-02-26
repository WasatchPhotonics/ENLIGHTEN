#!/bin/sh

# for POSIX development environments
#export PYTHONUTF8=1
#export QT_AUTO_SCREEN_SCALE_FACTOR=1

python scripts/Enlighten.py --log-level debug 1>enlighten.out 2>enlighten.err
cat enlighten.err
egrep -i traceback enlighten.out
