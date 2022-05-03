# Raspberry Pi

This addendum to our [Linux Docs](README_LINUX.md) applies to Raspberry Pi, 
Odroid and other ARM-based Linux variants following the Debian model.

# Packaged dependencies

Conda doesn't seem to have PySide2 packages for ARM, so follow this:

- https://www.raspberrypi.org/forums/viewtopic.php?p=1485265&sid=eb447c56004ea941be4aaefa2f837108#p1485265

At writing that is:  

    $ sudo apt-get install                  \
        python3-pyside2.qt3dcore            \
        python3-pyside2.qt3dinput           \
        python3-pyside2.qt3dlogic           \
        python3-pyside2.qt3drender          \
        python3-pyside2.qtcharts            \
        python3-pyside2.qtconcurrent        \
        python3-pyside2.qtcore              \
        python3-pyside2.qtgui               \
        python3-pyside2.qthelp              \
        python3-pyside2.qtlocation          \
        python3-pyside2.qtmultimedia        \
        python3-pyside2.qtmultimediawidgets \
        python3-pyside2.qtnetwork           \
        python3-pyside2.qtopengl            \
        python3-pyside2.qtpositioning       \
        python3-pyside2.qtprintsupport      \
        python3-pyside2.qtqml               \
        python3-pyside2.qtquick             \
        python3-pyside2.qtquickwidgets      \
        python3-pyside2.qtscript            \
        python3-pyside2.qtscripttools       \
        python3-pyside2.qtsensors           \
        python3-pyside2.qtsql               \
        python3-pyside2.qtsvg               \
        python3-pyside2.qttest              \
        python3-pyside2.qttexttospeech      \
        python3-pyside2.qtuitools           \
        python3-pyside2.qtwebchannel        \
        python3-pyside2.qtwebsockets        \
        python3-pyside2.qtwidgets           \
        python3-pyside2.qtx11extras         \
        python3-pyside2.qtxml               \
        python3-pyside2.qtxmlpatterns       \
        python3-pyside2uic

Then remaining packages:

    $ sudo apt-get install pyside2-tools python3-xlwt libatlas-base-dev python3-pywt 2to3

And finally:

    $ pip3 install superman pygtail pyusb pexpect

# Source dependencies

    // can probably now be done with "pip3 install pyqtgraph"
    $ git clone https://github.com/pyqtgraph/pyqtgraph.git
    $ cd pyqtgraph
    $ git checkout develop
    $ sudo python3 setup.py install

# Test

    $ cd work/code/enlighten
    $ export PYTHONPATH=".:../Wasatch.PY"
    $ python3 scripts/Enlighten.py

# Resetting USB Ports

Raspberry Pi have a unique ability to power-cycle the entire internal USB hub, 
forcing re-enumeration on all devices, and power-cycling those which are powered
via USB.  This is the command to do so:

    $ sudo ( uhubctl -l 2 -a 0 ; sleep 2 ; uhubctl -l 2 -a 1 )

# Deprecated

Since PySide2 currently needs to be installed via apt-get on RPi, and will therefore be
installed in the "system Python" package tree, there doesn't seem much point in using
Miniconda at this time.  That said, instructions are retained here:

- https://github.com/WasatchPhotonics/Wasatch.PY/blob/master/README_RPI.md#install-miniconda3
