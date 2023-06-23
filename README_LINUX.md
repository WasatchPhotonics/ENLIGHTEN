# Linux Development Environment

The following process was tested from a fresh Ubuntu 16.04 LTS VM running under
Parallels 13.3.2 on MacOS 10.14.2.

## Start from a fresh Ubuntu 22.04 VM

- enable Canonical Partners repo
- update all

## Install dependencies

These are the only dependencies we install via apt-get:

    $ sudo apt-get install cmake 

On Ubuntu, I found this was required to get Qt5 working
(see [qt.io](https://forum.qt.io/topic/93247/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it-was-found)):

    $ sudo apt-get install libxcb-xinerama0

The pyinstaller build will reflect the systems global installations, therefore when building Enlighten on Linux be sure to only have LibUSB0 installed. We reference our desired backend of libusb0 directly in pyusb, but for some reason libusb1 still intereferes. Maybe it's a bug in pyusb.

    $ sudo apt remove libusb-1.0
    $ sudo apt remove libusb-1.0-dev
    $ sudo apt install libusb-0.1.14

Optional but recommended:

    $ sudo apt-get install git vim doxygen graphviz cloc

## Install Miniconda3

Download and run the latest 64-bit installer from:

- https://conda.io/en/latest/miniconda.html

E.g.:

    $ bash Miniconda3-latest-Linux-x86_64.sh
    $ conda update conda

## Clone repositories

    $ git clone git@github.com:wasatchphotonics/Enlighten.git
    $ git clone git@github.com:wasatchphotonics/Wasatch.PY.git

## update USB permissions

By default only root can access USB devices; this allows standard users to access
our VID/PID.

    $ cd Wasatch.PY
    $ sudo cp udev/10-wasatch.rules /etc/udev/rules.d

## Verify that Wasatch.PY driver works

Create conda env:

    $ cd Wasatch.PY
    $ rm environment.yml
    $ cp environments/conda-linux.yml environment.yml
    $ conda update -n base -c defaults conda
    $ conda env create -n wasatch3

Run demo:

    $ conda activate wasatch3
    $ pip install crcmod bleak
    $ python -u demo.py
    $ conda deactivate

## Create ENLIGHTEN conda environment

    $ cd enlighten
    $ cp environments/conda-linux.yml environment.yml
    $ conda env create -n conda_enlighten3  

## Activate ENLIGHTEN conda environment

    $ cd enlighten
    $ conda activate conda_enlighten3
    $ export PYTHONPATH="../spyc_writer/src:../Wasatch.PY:pluginExamples:.:enlighten/assets/uic_qrc"

## Install pip dependencies (inside activated environment)

    $ python -m pip install -r requirements.txt

## Install Linux specific depenedencies

    $ python -m pip install pyudev

## Rebuild Qt artifacts

    (Workaround to PySide2 dependency problem: rebuild_resources from Windows)

    $ scripts/rebuild_resources.sh

## Run ENLIGHTEN

    $ python scripts/Enlighten.py

## Build a Linux installer

    $ make linux-installer
