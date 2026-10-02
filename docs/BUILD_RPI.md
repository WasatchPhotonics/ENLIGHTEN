# Raspberry Pi

This addendum to our [Linux Docs](BUILD_LINUX.md) applies to Raspberry Pi, 
Odroid and other ARM-based Linux variants following the Debian model.

See [MAINTENANCE](MAINTENANCE.md) for temporary changes or workarounds to
the build process.

# Raspberry Pi Zero 

To be completely upfront: the Raspberry Pi Zero 2 W is NOT a suitable runtime 
platform for ENLIGHTEN, due to its limitation to no more than 512MB (0.5GB) RAM.
ENLIGHTEN will only run "well" on Raspberry Pi models with 4-8GB RAM. That said,
I was able to launch and run ENLIGHTEN on a Pi Zero and take some spectra before
the kernel's Out-of-Memory (OOM) killer shut it down.

These setup notes were taken on an RPi Zero 2 W in Oct 2026 with the following
configuration:

    PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
    NAME="Debian GNU/Linux"
    VERSION_ID="13"
    VERSION="13 (trixie)"
    VERSION_CODENAME=trixie
    DEBIAN_VERSION_FULL=13.2
    ID=debian

## System Preparation

I had a lot of overheating? swap? disk space? issues on my RPi Zero 2 W, which 
caused the unit to repeatedly freeze during package download / installation. To 
address those, I attempted all of the following in various combinations. I'm not
sure which were the most critical, but I'm pretty sure the $TMPDIR fix was part
of it.

- add heat sink to RPi
- add fan pointing to heat sink
- install rpi-swap
- configure rpi-swap to 4GB (up from default 2GB)
    - sudo apt install rpi-swap
    - sudo vi /etc/rpi/swap.conf
- kill GUI (sudo systemctl stop lightdm)
- monitor temperature (vcgencmd measure_temp)
- throttle bandwidth 
    - tc qdisc show dev wlan0
    - (qdisc fq_codel 0: root refcnt 2 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb ecn drop_batch 64)
    - sudo tc qdisc add dev wlan0 root tbf rate 1mbit burst 10kb latency 70ms
- change pip's temp dir (this was critical)
    - mkdir ~/tmp
    - export TMPDIR=$HOME/tmp

## Installation Process

    $ mkdir ~/tmp
    $ export TMPDIR=$HOME/tmp       # or someplace with 1GB+ free
    $ mkdir ~/work/code
    $ cd ~/work/code
    $ git clone https://github.com/WasatchPhotonics/ENLIGHTEN.git
    $ git clone https://github.com/WasatchPhotonics/Wasatch.PY.git
    $ cd ENLIGHTEN

    $ python -m venv venv --system-site-packages
    $ . venv/bin/activate
    $ sudo apt update
    $ sudo apt install -y pkg-config libusb-1.0-0-dev   # for seabreeze?
    $ pip download tensorflow --timeout 60              # can possibly skip
    $ pip install -r requirements.txt

    $ scripts/rebuild_resources.sh

Add the following to your path:

    $ export PYTHONPATH=".:plugins:../Wasatch.PY:enlighten/assets/uic_qrc"

Copy the `10-wasatch.rules` rules file to set appropriate permissions for usb access 
(you will need to restart or reload after this):

    $ sudo cp -vf ../Wasatch.PY/udev/10-wasatch.rules /etc/udev/rules.d

Launch ENLIGHTEN:

    $ python -u scripts/Enlighten.py

## OOM-Killer

The Linux kernel has a feature called the OOM-Killer designed to automatically 
shutdown programs consuming dangerous levels of memory. If ENLIGHTEN abruptly 
terminates on your Raspberry Pi, run the following command to confirm it was the 
OMM-Killer responsible, and not a software bug:

    $ sudo dmesg -T | egrep -i 'killed process|out of memory'

# Appendix: PySide2 Instructions

At one time, PySide6 wasn't available on all RPi distros, so users had to use PySide2 
[instructions](https://www.raspberrypi.org/forums/viewtopic.php?p=1485265&sid=eb447c56004ea941be4aaefa2f837108#p1485265).

At writing (Sep 2026), PySide6 seems available on a Pi Zero 2 W (pretty much the
baby of the platform), so presumably this is no longer needed?

These are all the packages I installed via apt:

    $ apt install \
        2to3 \
        doxygen \
        graphviz \
        libatlas-base-dev \
        libopenblas-base \
        libopenblas-dev \
        libusb-0.1-4 \
        libusb-dev \
        pandoc
        pyqt5-dev-tools \
        pyside2-tools \
        python3-pil.imagetk \
        python3-pyside2.qt3dcore \
        python3-pyside2.qt3dinput \
        python3-pyside2.qt3dlogic \
        python3-pyside2.qt3drender \
        python3-pyside2.qtcharts \
        python3-pyside2.qtconcurrent \
        python3-pyside2.qtcore \
        python3-pyside2.qtgui \
        python3-pyside2.qthelp \
        python3-pyside2.qtlocation \
        python3-pyside2.qtmultimedia \
        python3-pyside2.qtmultimediawidgets \
        python3-pyside2.qtnetwork \
        python3-pyside2.qtopengl \
        python3-pyside2.qtpositioning \
        python3-pyside2.qtprintsupport \
        python3-pyside2.qtqml \
        python3-pyside2.qtquick \
        python3-pyside2.qtquickwidgets \
        python3-pyside2.qtscript \
        python3-pyside2.qtscripttools \
        python3-pyside2.qtsensors \
        python3-pyside2.qtsql \
        python3-pyside2.qtsvg \
        python3-pyside2.qttest \
        python3-pyside2.qttexttospeech \
        python3-pyside2.qtuitools \
        python3-pyside2.qtwebchannel \
        python3-pyside2.qtwebsockets \
        python3-pyside2.qtwidgets \
        python3-pyside2.qtx11extras \
        python3-pyside2.qtxml \
        python3-pyside2.qtxmlpatterns \
        python3-pywt \
        python3-xlwt 

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

    See the Appendix below for a full list of installed pip packages.

## Issue: missing python3-pyside2uic

Ideally, we would want to also `pip3 install python3-pyside2uic` (and historically, 
that was indeed part of the process).

Unfortunately, there is no current pre-built binary "wheel" for pyside2uic for 
the Raspberry Pi.  This is well-documented on the internet, and currently there
is no good way to install or build one.  

However, for now, we can get around this by not using pyside2uic on the RPi at
all, but instead using it on a different computer / OS and copying the result
over to the RPi.

There are two main utilities ENLIGHTEN uses from pyside2uic: UIC and RCC.  They
are used to convert ENLIGHTEN's .ui files and .rcc files (under enlighten/assets)
into .py files.  Those conversions can be performed under MacOS or Windows, and
the result copied to RPi.

The additional "gotcha" here is that our Mac and Windows builds now default to
PySide6, so you'll need to use the `USE_PYSIDE_2` environment variable to tell
rebuild_resources.sh to use the older rcc/uic scripts.

Example (both starting from ~/work/code/ENLIGHTEN):

    // on Mac
    $ export USE_PYSIDE_2=1
    $ scripts/rebuild_resources.sh

    // on Raspberry Pi
    $ rsync --progress --archive USER@MAC_IP:work/code/ENLIGHTEN/enlighten/assets/uic_qrc/ enlighten/assets/uic_qrc/

# Test

    $ cd work/code/ENLIGHTEN
    $ export PYTHONPATH=".:plugins:../Wasatch.PY:enlighten/assets/uic_qrc"
    $ python scripts/Enlighten.py

# Building an Installer

I had to do this to add pyinstaller to my PATH:

    $ export PATH=$HOME/.local/bin:$PATH

(as above)

    $ cd work/code/ENLIGHTEN
    $ export PYTHONPATH=".:plugins:../Wasatch.PY:enlighten/assets/uic_qrc"
    $ python scripts/Enlighten.py

(then)

    $ make rpi-installer

# Appendix: Resetting USB Ports

Raspberry Pi have a unique ability to power-cycle the entire internal USB hub, 
forcing re-enumeration on all devices, and power-cycling those which are powered
via USB.  This can be done with commands like:

    $ sudo uhubctl -l 2 -a 0 && sleep 2 && uhubctl -l 2 -a 1 

or

    $ sudo uhubctl --action 2 --location 2 --repeat 2 --delay 5 --wait 1000
