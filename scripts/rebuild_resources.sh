#!/bin/bash
#
# Run supporting pyrcc files to generate resource files and future
# designer conversions into python code. Run this from the home project
# directory like:
# <project root> $ ./scripts/rebuild_resources.sh

LAYOUT_ONLY=false
ICONS_ONLY=false
while [ "$1" != "" ]; do
    case $1 in
        --layout) LAYOUT_ONLY=true; shift ;;
         --icons)  ICONS_ONLY=true; shift ;;
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

# Change to Windows tool filenames if not on Linux
if uname -s | grep -q '^MINGW'
then
    # this line was needed when we moved to Qt5, because uic is now a python script 
    # rather than executable, and it therefore needs to be running in the appropriate
    # Conda environment to find PySide2
    source activate conda_enlighten3

    OS="Windows"

    TWO_TO_THREE="$CONDA_PREFIX/Scripts/2to3.exe"

    RCC="$CONDA_PREFIX/Scripts/pyside2-rcc.exe"
    UIC="$CONDA_PREFIX/Scripts/pyside2-uic.exe"
else
    if uname -a | grep -qi armv7
    then
        OS="RPi"

        # probably in /usr/bin per apt-get install pyside2-tools
        RCC=`which pyside2-rcc`
        UIC=`which pyside2-uic`
        TWO_TO_THREE=`which 2to3`  # probably in ${CONDA_ENV_PATH}/bin/2to3

        UIC_PRE="/usr/bin/python3"
    else
        OS="Linux"
        RCC="$CONDA_PREFIX/bin/pyside2-rcc"
        UIC="$CONDA_PREFIX/bin/pyside2-uic"
        TWO_TO_THREE="$CONDA_PREFIX/bin/2to3"
    fi
fi

echo "OS   = $OS"
echo "RCC  = $RCC"
echo "UIC  = $UIC"
echo "2to3 = $TWO_TO_THREE"
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

if ! $ICONS_ONLY
then
	python scripts/embed_stylesheet.py
	echo

    if [ $OS = "Linux" ]
    then
        unix2dos enlighten/assets/uic_qrc/enlighten_layout.ui
    fi
fi

################################################################################
# Convert Qt files to Python
################################################################################

if ! $LAYOUT_ONLY
then
	# Process all of the QT Resource Files
	for FILE in */assets/uic_qrc/*.qrc
	do 
		ROOT=$(echo $FILE | cut -d '.' -f 1)
		DEST=${ROOT}_rc.py

		echo -n "converting $FILE"
		$RCC $FILE -o $DEST
		echo "...done"
	done
	echo
fi

if ! $ICONS_ONLY
then
    for FILE in */assets/uic_qrc/*.ui
    do 
        BASENAME=$(echo $FILE | awk -F/ '{print $NF}')
        ROOT=$(echo $FILE | cut -d '.' -f 1)
        DEST=${ROOT}.py

		if $LAYOUT_ONLY && [ $BASENAME != "enlighten_layout.ui" ]
		then
            echo "skipping $FILE"
            continue
		fi

        echo -n "converting $FILE"
        $UIC_PRE $UIC $FILE -o $DEST && convertToPy3 $DEST
        echo "...done"
    done
fi

# make uic_qrc a valid Python module
touch enlighten/assets/uic_qrc/__init__.py

#echo "Press return to continue..."
#read foo
