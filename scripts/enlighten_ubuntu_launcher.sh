#!/usr/bin/env bash

################################################################################
#                           Enlighten Ubuntu Launcher
################################################################################
#
# Author: Samie Bee 2023
# 
# Invocation: 
# 
# $ wget https://wasatchphotonics.com/binaries/apps/enlighten/enlighten_ubuntu_launcher.sh
# $ chmod +x enlighten_ubuntu_launcher.sh
# $ sudo ./enlighten_ubuntu_launcher.sh
#
# Description: 
#
# This script has no dependencies. It will install and run Enlighten on Ubuntu 
# from source.
#
# The installation process installs a number of dependencies, including Python 
# 3.7. The majority of pip (PyPi) dependencies are placed in a "venv" virtual
# environment named "enlighten_venv".
#
# This installer was written for Enlighten 4.0.12 (via the branch ubu-py37).
# It has been tested to various degrees on Ubuntu 18, Ubuntu 20 and Ubuntu 22.
#
# The ubu-py37 is to be considered a downstream distribution branch
# containing a tag + patches required to run on Ubuntu.
#
################################################################################

# fail on error
set -e

LAUNCHER_VERSION="1.0.1"
INSTALL_PATH="$HOME/ENLIGHTEN"
INSTALL_LOG="$INSTALL_PATH/install.log"

if [ -e "$INSTALL_PATH/completed.txt" ]
then
    # activate
    source $INSTALL_PATH/enlighten_venv/bin/activate

    cd $INSTALL_PATH/ENLIGHTEN
    export PYTHONUTF8=1
    export QT_AUTO_SCREEN_SCALE_FACTOR=1
    export PYTHONPATH="../SPyC_Writer/src:../Wasatch.PY:pluginExamples:.:enlighten/assets/uic_qrc"
    python3.7 scripts/Enlighten.py --log-level debug 1>enlighten.out 2>enlighten.err
else
    echo "-------------------------------------------------------"
    echo "ENLIGHTEN Ubuntu Launcher ${LAUNCHER_VERSION}"
    echo
    echo "ENLIGHTEN is not yet installed. This script can automatically"
    echo "download and install ENLIGHTEN to the following directory:"
    echo
    echo "  $INSTALL_PATH"
    echo
    echo -n "Press enter to continue, or ctrl-C to cancel: "
    read null

    echo "-------------------------------------------------------"
    echo "Beginning installation at $(date)"
    echo
    mkdir -p "$INSTALL_PATH"
    cd "$INSTALL_PATH"
    echo "You may be prompted for a 'sudo' password during the following dependency installations."
    echo
    (

        sudo apt update 
        sudo apt install git 

        sudo apt install software-properties-common
        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt install python3.7
        sudo apt install python3.7-venv
        sudo apt install python3.7-distutils

        sudo apt install libxcb-xinerama0
        sudo apt install libusb-0.1-4
        sudo apt install curl

        # clone Enlighten and internal dependencies
        test -e ENLIGHTEN   || git clone https://github.com/WasatchPhotonics/ENLIGHTEN
        test -e SPyC_Writer || git clone https://github.com/WasatchPhotonics/SPyC_Writer
        test -e Wasatch.PY  || git clone https://github.com/WasatchPhotonics/Wasatch.PY

        # checkout Ubuntu distribution branch on each
        ( cd ENLIGHTEN   && git checkout ubu-py37 )
        ( cd SPyC_Writer && git checkout ubu-py37 )
        ( cd Wasatch.PY  && git checkout ubu-py37 )

        # keep subsequent pip install scripts from failing 
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3.7 get-pip.py

        # create venv for python dependencies
        python3.7 -m venv enlighten_venv

        # activate
        source $INSTALL_PATH/enlighten_venv/bin/activate

        python3.7 -m pip install --upgrade pip
        python3.7 get-pip.py
        python3.7 -m pip install numpy

        # install pip requirements
        python3.7 -m pip install -r ENLIGHTEN/requirements.txt
        python3.7 -m pip install -r SPyC_Writer/requirements.txt
        python3.7 -m pip install -r Wasatch.PY/requirements.txt

        # install requirements which had been maintained via conda 
        # in Python 3.7-era ENLIGHTEN
        python3.7 -m pip install PySide2
        python3.7 -m pip install xlwt
        python3.7 -m pip install superman
        python3.7 -m pip install pyqtgraph
        python3.7 -m pip install seabreeze
        python3.7 -m pip install crcmod
        python3.7 -m pip install bleak
        python3.7 -m pip install pandas
        python3.7 -m pip install pexpect
        python3.7 -m pip install psutil
        python3.7 -m pip install pytest
        python3.7 -m pip install scipy
        python3.7 -m pip install qimage2ndarray
        python3.7 -m pip install pyudev
        python3.7 -m pip install spc_spectra

        # copy udev
        sudo cp -vf $INSTALL_PATH/Wasatch.PY/udev/10-wasatch.rules /etc/udev/rules.d

        echo "-------------------------------------------------------"
        echo "Installation completed $(date)" >> $INSTALL_PATH/completed.txt
        echo "The installation is complete. Re-run $0 to launch ENLIGHTEN."
    ) | tee -a $INSTALL_LOG
fi
