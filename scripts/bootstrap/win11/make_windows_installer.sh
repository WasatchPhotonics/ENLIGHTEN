#!/bin/bash

function log()
{
    MSG="$@"
    echo "$(date) ${MSG}"
}

log "checking pyinstaller"
if which pyinstaller > /dev/null
then
    log "pyinstaller found"
else
    echo "pyinstaller not installed -- please run:"
    echo "  $ python -m venv venv"
    echo "  $ . venv/Scripts/activate"
    echo "  $ pip install ."
    exit 1
fi

log "checking Inno Setup"
if which iscc > /dev/null
then
    log "iscc found"
else
    echo "iscc not found -- install Inno Setup and add to PATH"
    exit 1
fi

log "checking for keys.py"
if [ -f src/wp_enlighten/network/keys.py ]
then
    log "keys.py found"
else
    echo "WARNING: keys.py not found -- so AWS cloud access will not be available"
    read -p "Press return to continue..."
fi

log "checking for XD models"
if ls src/wp_enlighten/assets/example_data/XD_models | grep -qi tflite
then
    log "one or more XD models found"
else
    echo "WARNING: no XD models found, so XD processing will not be available"
    read -p "Press return to continue..."
fi

VERSION=`grep '^VERSION' src/wp_enlighten/common.py | grep -E -o '([0-9]\.?)+'`
log "version $VERSION"

rm -rf pyinstaller-build
mkdir -p pyinstaller-build/dist
mkdir -p pyinstaller-build/work

# @see https://stackoverflow.com/a/69521558 re: _bootlocale
log "running pyinstaller"
pyinstaller \
    --distpath="pyinstaller-build/dist" \
    --workpath="pyinstaller-build/work" \
    --noconfirm \
    --python-option "X utf8" \
    --noconsole \
    --clean \
    --hidden-import="numpy.core._multiarray_umath" \
    --hidden-import="numpy._core._exceptions" \
    --hidden-import="scipy._lib.messagestream" \
    --hidden-import="scipy._lib.array_api_compat.numpy.fft" \
    --hidden-import="scipy.special._special_ufuncs" \
    --hidden-import="scipy.special.cython_special" \
    --hidden-import="scipy._cyutility" \
    --hidden-import="colour" \
    --add-data="support_files/libusb_drivers/amd64/libusb0.dll:." \
    --icon "../src/wp_enlighten/assets/uic_qrc/images/EnlightenIcon.ico" \
    --specpath="$PWD/scripts" \
    --exclude-module _bootlocale \
    src/wp_enlighten/app.py 2>&1 | tee pyinstaller.out

if $? != 0
then
    echo "pyinstaller failed (see pyinstaller.out)"
    exit 1
fi

log "running Inno Setup"
rm -rf windows_installer
mkdir windows_installer
# see https://jrsoftware.org/ishelp/index.php?topic=setup_compression
iscc /DENLIGHTEN_VERSION=$VERSION /DCOMPRESSION=lzma/max scripts/Application_InnoSetup.iss
if $? != 0
then
    echo "innosetup failure"
    exit 1
fi

log "done"
ls -la windows_installer
