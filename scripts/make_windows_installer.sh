#!/bin/bash
################################################################################
#                            make_windows_installer.sh                         #
################################################################################
#                                                                              #
#  DESCRIPTION: Build an ENLIGHTEN installer using PyInstaller and Inno Setup. #
#               Generates a venv if not found, and populates all pip           #
#               dependencies.                                                  #
#                                                                              #
#  INVOCATION:  $ time scripts/make_windows_installer.sh 2>&1 | tee build.out  #
#                                                                              #
#               This script is expected to be run from the root directory of   #
#               an ENLIGHTEN GitHub clone (parent of ./src, ./scripts, root    #
#               of README.md etc). It should be run from a "Git for Windows"   #
#               Bash shell.                                                    #
#                                                                              #
################################################################################

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
header "processing cmd-line args"
################################################################################

INNO_ONLY=false
for arg in "$@"
do
    if [ "$arg" == "--inno-only" ]
    then
        INNO_ONLY=true
    fi
done

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
log "version ${VERSION}"

EXE_NAME="ENLIGHTEN-Setup64-${VERSION}.exe"
if [ -f ${EXE_NAME} ]
then
    log "removing old ${EXE_NAME}"
fi

if $INNO_ONLY
then
    log "..."
    log "skipping everything up to Inno Setup"
    log "..."
else

    ################################################################################
    header "checking environment"
    ################################################################################

    if ! [ -d venv ]
    then
        log "creating venv"
        python -m venv venv
    fi

    if [ "${VIRTUAL_ENV}" ]
    then
        log "already running in venv: ${VIRTUAL_ENV}"
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

    # NB: --onefile doesn't seem to work well because it was hard to tell where
    #     --add-data was placing assets (needed for stylesheets etc). The fact that
    #     os.walk() would not work in ~/AppData/Local/Temp was frankly terrifying.
    #
    # --icon paths etc start with ../ because pyinstaller will run within specpath,
    #     in this case pyinstaller-build. I don't know if --path calls are doing 
    #     anything at this point.

    rm -rf pyinstaller-build
    mkdir -pv pyinstaller-build/dist
    mkdir -pv pyinstaller-build/work

    time pyinstaller --clean \
                     --name=enlighten \
                     --path=src/wp_enlighten/Plugins/dist \
                     --path=src/wp_enlighten/assets/uic_qrc \
                     --icon=../src/wp_enlighten/assets/uic_qrc/images/EnlightenIcon.ico \
                     --add-data=../src/wp_enlighten/assets:assets \
                     --distpath=pyinstaller-build/dist \
                     --workpath=pyinstaller-build/work \
                     --specpath=pyinstaller-build \
                     --noconfirm \
                     --noconsole \
                     --hidden-import=numpy.core._multiarray_umath \
                     --hidden-import=numpy._core._exceptions \
                     --hidden-import=scipy._lib.messagestream \
                     --hidden-import=scipy._lib.array_api_compat.numpy.fft \
                     --hidden-import=scipy.special._special_ufuncs \
                     --hidden-import=scipy.special.cython_special \
                     --hidden-import=scipy._cyutility \
                     --hidden-import=colour \
                     src/wp_enlighten/app.py

    # MZ: I removed these basically to see if anything would break. I have no
    #     idea if they are still needed.
    #
    # --python-option "X utf8" \
    # --add-data="support_files/libusb_drivers/amd64/libusb0.dll:." \
    # --exclude-module _bootlocale \

    if (( $? != 0 ))
    then
        log "pyinstaller failed (see pyinstaller.out)"
        exit 1
    fi

    log "pyinstaller result in pyinstaller-build/dist/enlighten"
fi

################################################################################
header "running Inno Setup"
################################################################################

rm -rf innosetup-build
mkdir -p innosetup-build

# see https://jrsoftware.org/ishelp/index.php?topic=compilercmdline
# see https://jrsoftware.org/ishelp/index.php?topic=setup_compression

time cmd //c "iscc /DENLIGHTEN_VERSION=${VERSION} /DCOMPRESSION=lzma/max InnoSetup.iss"

# NB: the generated ENLIGHTEN-x.y.z-Setup64.exe can be run with "/?" for command-
#     line options, including /LOG=installer.log

if (( $? != 0 ))
then
    log "Inno Setup failure"
    exit 1
fi

header "done"

echo
ls -la *.exe
