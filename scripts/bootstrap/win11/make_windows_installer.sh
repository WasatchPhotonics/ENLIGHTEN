#!/bin/bash

function log()
{
    local MSG
    MSG="$@"
    echo "$(date) ${MSG}"
}

function header()
{
    local MSG
    MSG="$@"
    log " "
    log "=================================================="
    log "$MSG"
    log "=================================================="
    log " "
}

################################################################################
header "checking pre-requisites"
################################################################################

log "checking Inno Setup"
if which iscc > /dev/null
then
    log "iscc found"
else
    log "iscc not found -- install Inno Setup and add to PATH"
    exit 1
fi

log "checking for keys.py"
if [ -f src/wp_enlighten/network/keys.py ]
then
    log "keys.py found"
else
    log "WARNING: keys.py not found -- so AWS cloud access will not be available"
    read -p "Press return to continue..."
fi

log "checking for XD models"
if ls src/wp_enlighten/assets/example_data/XD_models | grep -qi tflite
then
    log "one or more XD models found"
else
    log "WARNING: no XD models found, so XD processing will not be available"
    read -p "Press return to continue..."
fi

VERSION=`grep '^VERSION' src/wp_enlighten/common.py | grep -E -o '([0-9]\.?)+'`
log "version $VERSION"

################################################################################
header "checking environment"
################################################################################

if ! [ -d venv ]
then
    log "creating venv"
    python -m venv venv
fi

if [ "$VIRTUAL_ENV" ]
then
    log "already running in venv: $VIRTUAL_ENV"
else
    log "activating venv"
    . venv/Scripts/activate
fi

log "installing wheel locally"
pip install .

################################################################################
header "building resources"
################################################################################

scripts/rebuild_resources.sh

################################################################################
header "running pyinstaller"
################################################################################

# @see https://stackoverflow.com/a/69521558 re: _bootlocale
if false
then
    pyinstaller \
        --onefile \
        --windowed \
        --name enlighten \
        --clean \
        --path src/wp_enlighten/Plugins/dist \
        --path src/wp_enlighten/assets/uic_qrc \
        --icon src/wp_enlighten/assets/uic_qrc/images/EnlightenIcon.ico \
        --add-data="src/wp_enlighten/assets:src/wp_enlighten/assets" \
        src/wp_enlighten/app.py
else
    rm -rf pyinstaller-build
    mkdir -p pyinstaller-build/dist
    mkdir -p pyinstaller-build/work

    pyinstaller \
        --clean \
        --name enlighten \
        --path src/wp_enlighten/Plugins/dist \
        --path src/wp_enlighten/assets/uic_qrc \
        --icon "src/wp_enlighten/assets/uic_qrc/images/EnlightenIcon.ico" \
        --distpath="pyinstaller-build/dist" \
        --workpath="pyinstaller-build/work" \
        --specpath="pyinstaller-build" \
        --noconfirm \
        --noconsole \
        --python-option "X utf8" \
        --hidden-import="numpy.core._multiarray_umath" \
        --hidden-import="numpy._core._exceptions" \
        --hidden-import="scipy._lib.messagestream" \
        --hidden-import="scipy._lib.array_api_compat.numpy.fft" \
        --hidden-import="scipy.special._special_ufuncs" \
        --hidden-import="scipy.special.cython_special" \
        --hidden-import="scipy._cyutility" \
        --hidden-import="colour" \
        src/wp_enlighten/app.py 2>&1 | tee pyinstaller.out

    # --add-data="support_files/libusb_drivers/amd64/libusb0.dll:." \
    # --exclude-module _bootlocale \
fi

if (( $? != 0 ))
then
    log "pyinstaller failed (see pyinstaller.out)"
    exit 1
fi

log "result in pyinstaller-build/dist"

################################################################################
header "running Inno Setup"
################################################################################

rm -rf innosetup-build
mkdir -p innosetup-build

# see https://jrsoftware.org/ishelp/index.php?topic=compilercmdline
# see https://jrsoftware.org/ishelp/index.php?topic=setup_compression

cmd //c "iscc /DENLIGHTEN_VERSION=4.3.0 /DCOMPRESSION=lzma/max scripts/Application_InnoSetup.iss"
if (( $? != 0 ))
then
    log "innosetup failure"
    exit 1
fi

header "done"
ls -la windows_installer
