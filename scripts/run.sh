#!/bin/sh

export PYTHONPATH=.:plugins:enlighten/assets/uic_qrc:../Wasatch.PY:../spyc_writer/src:../jcamp

python -u scripts/bootstrap/win11/bootstrap.py --force --arg log-level=debug 2>enlighten.err 1>enlighten.out

cat enlighten.err

# https://askubuntu.com/a/849016
cat enlighten.out | sed -n '/^Traceback/,/^[^ ]/p'
