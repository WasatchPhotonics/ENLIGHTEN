#!/bin/bash
#
# Run supporting pyrcc files to generate resource files and future
# designer conversions into python code. Invoked from the repo root:
# 
# $ ./scripts/rebuild_resources.sh
#   or 
# $ sh scripts/rebuild_resources.sh

QUICK=false
PAUSE=false
BOOTSTRAP=false
while [ "$1" != "" ]
do
    case $1 in
	    --quick) QUICK=true; ;;
	    --pause) PAUSE=true; ;;
	    --bootstrap) BOOTSTRAP=true; ;;
    esac
    shift
done

################################################################################
# Check invocation
################################################################################

if ! $BOOTSTRAP
then
    echo "Warning: this script should normally be run automatically by one of the scripts"
    echo "under scripts/bootstrap, e.g. scripts/bootstrap/win11/bootstrap.py"
    echo
fi

################################################################################
# Tailor to the operating system
################################################################################

UIC_PRE=""
UIC_OPTS=""
RCC_OPTS=""
PYTHON="python"

if (uname -s | grep -q '^MINGW') || (uname -s | grep -q '^MSYS_NT')
then
    # this line was needed when we moved to Qt5, because uic is now a python script 
    # rather than executable, and it therefore needs to be running in the appropriate
    # Conda environment to find PySide2
    # 
    # source activate conda_enlighten3

    OS="Windows"

    RCC="${VIRTUAL_ENV}/Scripts/pyside6-rcc.exe"
    UIC="${VIRTUAL_ENV}/Scripts/pyside6-uic.exe"

    # added because recent(?) versions of Git Cmd / Git Bash seem to 
    # automatically launch new shells (run .sh scripts like this one)
    # in $HOME rather than the "current working directory" (and this
    # truthfully shouldn't hurt anything)
    SCRIPT_DIR=`dirname $0` 
    cd $SCRIPT_DIR/.. 
else
    if uname -a | grep -qi raspberrypi
    then
        OS="RPi"

        # probably in /usr/bin per apt-get install pyside2-tools
        RCC=`which pyside6-rcc`
        UIC=`which pyside6-uic`
        PYTHON="python3"

        UIC_PRE=$PYTHON
    else
        if uname -a | grep -qi darwin
        then
            OS="MacOS"
            RCC="${VIRTUAL_ENV}/bin/pyside6-rcc"
            UIC="${VIRTUAL_ENV}/bin/pyside6-uic"

            UIC_OPTS="--generator python"
            RCC_OPTS="--generator python"
        else
            OS="Linux"
            RCC="${VIRTUAL_ENV}/bin/pyside6-rcc"
            UIC="${VIRTUAL_ENV}/bin/pyside6-uic"
        fi
    fi
fi

# are we running against source (against src/wp_enlighten/assets/uic_qrc) or against 
# an installed wheel (venv/lib/python3.14/site-packages/wp_enlighten/assets/uic_qrc)?
if [ -d src/wp_enlighten/assets ]
then
    ASSET_DIR=src/wp_enlighten/assets
else
    if [ -d venv/lib/python*/site-packages/wp_enlighten/assets ]
    then
        ASSET_DIR=venv/lib/python*/site-packages/wp_enlighten/assets
    else
        echo "ERROR: can't find assets/uic_qrc"
        exit 1
    fi
fi

echo "ASSET_DIR   = $ASSET_DIR"
echo "VIRTUAL_ENV = $VIRTUAL_ENV"
echo "QUICK       = $QUICK"
echo "PAUSE       = $PAUSE"
echo "PYTHON      = $PYTHON"
echo "OS          = $OS"
echo "RCC         = $RCC (opts '$RCC_OPTS')"
echo "UIC         = $UIC (pre '$UIC_PRE', opts '$UIC_OPTS')"
echo

FAILED=false
if ! [ -f "$RCC" ]
then
    echo "Error: can't locate RCC: $RCC"
    FAILED=true
fi
if ! [ -f "$UIC" ]
then
    echo "Error: can't locate UIC: $UIC"
    FAILED=true
fi

if $FAILED
then
    echo "Press return to exit..."
    read foo
    exit 1
fi

################################################################################
# Embed latest CSS into Qt Designer layout
################################################################################

if ! $QUICK
then
    $PYTHON scripts/embed_stylesheet.py
    echo

    if [ $OS = "Linux" ]
    then
        unix2dos $ASSET_DIR/uic_qrc/enlighten_layout.ui
    fi
fi

################################################################################
# Convert Qt files to Python
################################################################################

# Process all of the QT Resource Files
if ! $QUICK
then
    for FILE in $ASSET_DIR/uic_qrc/*.qrc
    do 
        ROOT=$(echo $FILE | cut -d '.' -f 1)
        DEST=${ROOT}_rc.py

        echo -n "converting $FILE"
        "$RCC" $FILE -o $DEST $RCC_OPTS
        echo "...done"
    done
    echo
fi

# Process all of the QT .ui (User Interface) forms
for FILE in $ASSET_DIR/uic_qrc/*.ui
do 
    BASENAME=$(echo $FILE | awk -F/ '{print $NF}')
    ROOT=$(echo $FILE | cut -d '.' -f 1)
    DEST=${ROOT}.py

    if $QUICK && [ $BASENAME != "enlighten_layout.ui" ]
    then
        echo "skipping $FILE"
        continue
    fi

    echo -n "converting $FILE"
    $UIC_PRE "$UIC" $FILE -o $DEST $UIC_OPTS 
    echo "...done"
done

# make uic_qrc a valid Python module
touch $ASSET_DIR/uic_qrc/__init__.py

if $PAUSE
then
    echo "Press return to continue..."
    read foo
fi
