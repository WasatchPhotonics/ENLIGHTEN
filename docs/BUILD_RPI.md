# Raspberry Pi

This addendum to our [Linux Docs](BUILD_LINUX.md) applies to Raspberry Pi, 
Odroid and other ARM-based Linux variants following the Debian model.

See [MAINTENANCE](README_MAINTENANCE.md) for temporary changes or workarounds to
the build process.

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
        python3-pyside2.qtxmlpatterns       

Then remaining packages:

    $ sudo apt-get install pyside2-tools python3-xlwt libatlas-base-dev \
                           python3-pywt 2to3 python3-pil.imagetk libusb-0.1-4 \
			   libusb-dev

And finally, install everything in requirements.txt OTHER THAN PySide2 :-)

    $ pip3 install \
	adafruit-blinka \
	bleak \
	boto3 \
	crcmod \
	libusb \
	pandas \
	pefile \
	pexpect \
	pyftdi \
	pygtail \
	pyinstaller \
	pyqtgraph \
	pyudev \
	pyusb \
	pywavelets \
	qimage2ndarray \
	seabreeze \
	spc_spectra \
	SPyC_Writer \
	superman \
	tensorflow

If you also want to build and deploy installers, the following additional utilities are required:

    $ sudo apt-get install doxygen graphviz pandoc

## Issue: missing python3-pyside2uic

Ideally, we would want to also `pip3 install python3-pyside2uic` (and historically, 
that was indeed part of the process).

Unfortunately, there is no current pre-built binary "wheel" for pyside2uic for 
the Raspberry Pi.  This is well-documented on the internet, and currently there
is no good way to install or build one.  Going forward, the world seems to be
moving from PySide2 to PyQt, and ENLIGHTEN will probably need to follow along.

However, for now, we can get around this by not using pyside2uic on the RPi at
all, but instead using it on a different computer / OS and copying the result
over to the RPi.

There are two main utilities ENLIGHTEN uses from pyside2uic: UIC and RCC.  They
are used to convert ENLIGHTEN's .ui files and .rcc files (under enlighten/assets)
into .py files.  Those conversions can be performed under MacOS or Windows, and
the result copied to RPi.

Example (both starting from ~/work/code/ENLIGHTEN):

    // on Mac
    $ scripts/rebuilt_resources.sh

    // on Raspberry Pi
    $ rsync --progress --archive USER@MAC_IP:work/code/ENLIGHTEN/enlighten/assets/uic_qrc/ enlighten/assets/uic_qrc/

# Test

    $ cd work/code/enlighten

    $ export PYTHONPATH=".:pluginExamples:../Wasatch.PY:enlighten/assets/uic_qrc"
    $ python scripts/Enlighten.py

# Building an Installer

(as above)

    $ cd work/code/enlighten
    $ export PYTHONPATH=".:pluginExamples:../Wasatch.PY:enlighten/assets/uic_qrc"
    $ python scripts/Enlighten.py

(then)

    $ make rpi-installer

# Resetting USB Ports

Raspberry Pi have a unique ability to power-cycle the entire internal USB hub, 
forcing re-enumeration on all devices, and power-cycling those which are powered
via USB.  This can be done with commands like:

    $ sudo uhubctl -l 2 -a 0 && sleep 2 && uhubctl -l 2 -a 1 

or

    $ sudo uhubctl --action 2 --location 2 --repeat 2 --delay 5 --wait 1000

# Deprecated

Since PySide2 currently needs to be installed via apt-get on RPi, and will therefore be
installed in the "system Python" package tree, there doesn't seem much point in using
Miniconda at this time.  That said, instructions are retained here:

- https://github.com/WasatchPhotonics/Wasatch.PY/blob/master/README_RPI.md#install-miniconda3
