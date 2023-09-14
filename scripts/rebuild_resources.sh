#!/bin/bash
#
# Run supporting pyrcc files to generate resource files and future
# designer conversions into python code. Run this from the home project
# directory like:
# <project root> $ ./scripts/rebuild_resources.sh

QUICK=false
PAUSE=false
echo "args: $*"
echo "first arg: $1"
while [ "$1" != "" ]
do
    echo "evaluating arg '$1'"
    case $1 in
         --quick) QUICK=true; ;;
         --pause) PAUSE=true; ;;
    esac
    shift
done

function convertToPy3()
{
    local DEST="$1"

    echo -n "...to Python3"
    $TWO_TO_THREE -w $DEST > /dev/null 2>&1
}

################################################################################
# Tailor to the operating system
################################################################################

UIC_PRE=""
UIC_OPTS=""
RCC_OPTS=""
PYTHON="python"

# Change to Windows tool filenames if not on Linux
if (uname -s | grep -q '^MINGW') || (uname -s | grep -q '^MSYS_NT')
then
    # this line was needed when we moved to Qt5, because uic is now a python script 
    # rather than executable, and it therefore needs to be running in the appropriate
    # Conda environment to find PySide2
    source activate conda_enlighten3

    OS="Windows"

    TWO_TO_THREE="$CONDA_PREFIX/Scripts/2to3.exe"

    RCC="$CONDA_PREFIX/Scripts/pyside2-rcc.exe"
    UIC="$CONDA_PREFIX/Scripts/pyside2-uic.exe"

    # added because recent(?) versions of Git Cmd / Git Bash seem to 
    # automatically launch new shells (run .sh scripts like this one)
    # in $HOME rather than the "current working directory" (and this
    # truthfully shouldn't hurt anything)
    SCRIPT_DIR=`dirname $0` 
    cd $SCRIPT_DIR/.. 
else
    if uname -a | grep -qi armv7
    then
        OS="RPi"

        # probably in /usr/bin per apt-get install pyside2-tools
        RCC=`which pyside2-rcc`
        UIC=`which pyside2-uic`
        TWO_TO_THREE=`which 2to3`  # probably in ${CONDA_ENV_PATH}/bin/2to3
        PYTHON="python3"

        UIC_PRE=$PYTHON
    else
        if uname -a | grep -qi darwin
        then
            OS="MacOS"
            # PATH should include /usr/local/lib/python3.10/site-packages/PySide2 or equivalent
            RCC=`which rcc`
            UIC=`which uic`
            TWO_TO_THREE=`which 2to3-3.10`

            PYTHON="python3.10"
            UIC_OPTS="--generator python"
            RCC_OPTS="--generator python"
        else
            OS="Linux"
            RCC="$CONDA_PREFIX/bin/pyside2-rcc"
            UIC="$CONDA_PREFIX/bin/pyside2-uic"
            TWO_TO_THREE="$CONDA_PREFIX/bin/2to3"
        fi
    fi
fi

echo "QUICK = $QUICK"
echo "PAUSE = $PAUSE"
echo "PYTHON= $PYTHON"
echo "OS    = $OS"
echo "RCC   = $RCC (opts $RCC_OPTS)"
echo "UIC   = $UIC (pre $UIC_PRE opts $UIC_OPTS)"
echo "2to3  = $TWO_TO_THREE"
echo

FAILED=false
if ! [ -f $RCC ]
then
    echo "Error: can't locate RCC: $RCC"
    FAILED=true
fi
if ! [ -f $UIC ]
then
    echo "Error: can't locate UIC: $UIC"
    FAILED=true
fi
if ! [ -f $TWO_TO_THREE ]
then
    echo "Error: can't locate 2to3: $TWO_TO_THREE"
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
        unix2dos enlighten/assets/uic_qrc/enlighten_layout.ui
    fi
fi

################################################################################
# Convert Qt files to Python
################################################################################

if ! $QUICK
then
    # Process all of the QT Resource Files
    for FILE in */assets/uic_qrc/*.qrc
    do 
        ROOT=$(echo $FILE | cut -d '.' -f 1)
        DEST=${ROOT}_rc.py

        echo -n "converting $FILE"
        $RCC $FILE -o $DEST $RCC_OPTS
        echo "...done"
    done
    echo
fi

for FILE in */assets/uic_qrc/*.ui
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
$UIC_PRE $UIC $FILE -o $DEST $UIC_OPTS && convertToPy3 $DEST
echo "...done"
done

# make uic_qrc a valid Python module
touch enlighten/assets/uic_qrc/__init__.py

if $PAUSE
then
    echo "Press return to continue..."
    read foo
fi
