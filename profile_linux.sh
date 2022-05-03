# this file should be "source'd", not executed

if [ -d ../Wasatch.PY ]
then
    echo "Updating PYTHONPATH"
    export PYTHONPATH="../Wasatch.PY:$PWD:$PWD/enlighten:$PYTHONPATH"

    echo "Activating environment"
    conda activate conda_enlighten3
else
    echo "ERROR: expecting Wasatch.PY as sibling of this directory"
fi
