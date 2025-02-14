# Raspberry Pi

This addendum to our [Linux Docs](BUILD_LINUX.md) applies to Raspberry Pi, 
Odroid and other ARM-based Linux variants following the Debian model.

See [MAINTENANCE](MAINTENANCE.md) for temporary changes or workarounds to
the build process.

# Packaged dependencies

## Raspberry Pi 4 / Debian Bookworm 64 bit

PySide6 is available as a wheel on 64 bit Bookworm, simplifying installation instructions.

Clone ENLIGHTEN and Wasatch.PY into parallel directories.

    git clone https://github.com/WasatchPhotonics/ENLIGHTEN.git
    git clone https://github.com/WasatchPhotonics/Wasatch.PY.git

Create a virtual environment including system packages

    python -m venv venv --system-site-packages

Activate the virtual environment

    . venv/bin/activate

Install the following dependencies listed in the requirements.txt (note: PyQt5 is included in system packages
so isn't included):

    numpy
    tensorflow==2.13.1
    PySide6
    pygtail 
    pyusb 
    pefile 
    pyinstaller==6.10.0
    pywavelets 
    superman 
    pyqtgraph 
    libusb 
    seabreeze==2.7.0
    boto3 
    bleak 
    pyftdi 
    adafruit-blinka
    SPyC_Writer
    crcmod
    pandas
    pexpect
    pip
    psutil
    scipy
    xlwt
    qimage2ndarray
    2to3
    matplotlib
    pyserial
    colour-science

If you run into any issues while installing a dependency, use specify the version referenced in 
in the `Installed PIP packages` appendix below.

Build the GUI by calling: 
    
    . scripts/rebuild_resources.sh

Add the following to your path:

    export PYTHONPATH=".:plugins:../Wasatch.PY:enlighten/assets/uic_qrc"

Copy the `10-wasatch.rules` rules file to set appropriate permissions for usb access 
(you will need to restart or reload after this):

    sudo cp -vf Wasatch.PY/udev/10-wasatch.rules /etc/udev/rules.d

Launch ENLIGHTEN:

    python -u scripts/Enlighten.py


## PySide2 Instructions

PySide6 isn't available on all RPi distros, so you may need to use PySide2 
[instructions](https://www.raspberrypi.org/forums/viewtopic.php?p=1485265&sid=eb447c56004ea941be4aaefa2f837108#p1485265).

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

# Appendix: Installed PIP packages

These are the PIP packages I had installed when testing 4.0.62:

    Package                                  Version
    ---------------------------------------- -----------
    2to3                                     1.0
    Adafruit-Blinka                          8.39.2
    adafruit-circuitpython-busdevice         5.2.9
    adafruit-circuitpython-connectionmanager 3.1.0
    adafruit-circuitpython-requests          4.0.0
    adafruit-circuitpython-typing            1.10.3
    Adafruit-PlatformDetect                  3.63.0
    Adafruit-PureIO                          1.1.11
    altgraph                                 0.17.4
    arandr                                   0.1.10
    astroid                                  2.5.1
    asttokens                                2.0.4
    async-timeout                            4.0.3
    automationhat                            0.2.0
    beautifulsoup4                           4.9.3
    bleak                                    0.22.1
    blinker                                  1.4
    blinkt                                   0.1.2
    boto3                                    1.34.114
    botocore                                 1.34.114
    buttonshim                               0.0.2
    Cap1xxx                                  0.1.3
    certifi                                  2020.6.20
    chardet                                  4.0.0
    click                                    7.1.2
    colorama                                 0.4.4
    colorzero                                1.1
    construct                                2.8.22
    contourpy                                1.2.1
    crcmod                                   1.7
    cryptography                             3.3.2
    cupshelpers                              1.0
    cycler                                   0.12.1
    Cython                                   3.0.10
    DateTime                                 5.5
    dbus-fast                                2.21.3
    dbus-python                              1.2.16
    distro                                   1.5.0
    docutils                                 0.16
    drumhat                                  0.1.0
    envirophat                               1.0.0
    exceptiongroup                           1.2.1
    ExplorerHAT                              0.4.2
    Flask                                    1.1.2
    fonttools                                4.52.4
    fourletterphat                           0.1.0
    gpiozero                                 1.6.2
    html5lib                                 1.1
    idna                                     2.10
    importlib_metadata                       7.1.0
    importlib_resources                      6.4.0
    iniconfig                                2.0.0
    isort                                    5.6.4
    itsdangerous                             1.1.0
    jcamp                                    1.2.2
    jedi                                     0.18.0
    Jinja2                                   2.11.3
    jmespath                                 1.0.1
    joblib                                   1.4.2
    kiwisolver                               1.4.5
    lazy-object-proxy                        0.0.0
    libusb                                   1.0.27
    logilab-common                           1.8.1
    lxml                                     4.6.3
    MarkupSafe                               1.1.1
    matplotlib                               3.7.0
    mccabe                                   0.6.1
    microdotphat                             0.2.1
    mote                                     0.0.4
    motephat                                 0.0.3
    mypy                                     0.812
    mypy-extensions                          0.4.3
    numpy                                    1.26.4
    oauthlib                                 3.1.0
    packaging                                24.0
    pandas                                   2.2.2
    pantilthat                               0.0.7
    parso                                    0.8.1
    pefile                                   2023.2.7
    pexpect                                  4.8.0
    pgzero                                   1.2
    phatbeat                                 0.1.1
    pianohat                                 0.1.0
    picamera                                 1.13
    picamera2                                0.3.12
    pidng                                    4.0.9
    piexif                                   1.1.3
    piglow                                   1.2.5
    pigpio                                   1.78
    Pillow                                   8.1.2
    pip                                      24.0
    pkg-about                                1.1.5
    pluggy                                   1.5.0
    psutil                                   5.8.0
    pycairo                                  1.16.2
    pycups                                   2.0.1
    pyftdi                                   0.55.4
    pygame                                   1.9.6
    Pygments                                 2.7.1
    PyGObject                                3.38.0
    pygtail                                  0.14.0
    pyinotify                                0.9.6
    pyinstaller                              6.7.0
    pyinstaller-hooks-contrib                2024.6
    PyJWT                                    1.7.1
    pylint                                   2.7.2
    PyOpenGL                                 3.1.5
    pyOpenSSL                                20.0.1
    pyparsing                                3.1.2
    PyQt5                                    5.15.2
    PyQt5-sip                                12.8.1
    pyqtgraph                                0.13.7
    pyserial                                 3.5b0
    pysmbc                                   1.0.23
    pytest                                   8.2.1
    python-apt                               2.2.1
    python-dateutil                          2.9.0.post0
    python-prctl                             1.7
    pytz                                     2024.1
    pyudev                                   0.24.3
    pyusb                                    1.2.1
    PyWavelets                               1.1.1
    qimage2ndarray                           1.10.0
    rainbowhat                               0.1.0
    reportlab                                3.5.59
    requests                                 2.25.1
    requests-oauthlib                        1.0.0
    responses                                0.12.1
    roman                                    2.0.0
    RPi.GPIO                                 0.7.0
    rpi-ws281x                               5.0.0
    RTIMULib                                 7.2.1
    s3transfer                               0.10.1
    scikit-learn                             1.4.2
    scipy                                    1.13.1
    scrollphat                               0.0.7
    scrollphathd                             1.2.1
    seabreeze                                2.7.0
    Send2Trash                               1.6.0b1
    sense-hat                                2.6.0
    setuptools                               70.0.0
    simplejpeg                               1.6.4
    simplejson                               3.17.2
    six                                      1.16.0
    skywriter                                0.0.7
    sn3218                                   1.2.7
    soupsieve                                2.2.1
    spc-spectra                              0.4.0
    spidev                                   3.5
    SPyC_Writer                              1.0.0
    ssh-import-id                            5.10
    superman                                 0.1.2
    sysv-ipc                                 1.1.0
    thonny                                   4.0.1
    threadpoolctl                            3.5.0
    toml                                     0.10.1
    tomli                                    2.0.1
    touchphat                                0.0.1
    twython                                  3.8.2
    typed-ast                                1.4.2
    typing_extensions                        4.12.0
    tzdata                                   2024.1
    unicornhathd                             0.0.4
    urllib3                                  1.26.5
    usb                                      0.0.83.dev0
    v4l2-python3                             0.3.2
    webencodings                             0.5.1
    Werkzeug                                 1.0.1
    wheel                                    0.43.0
    wrapt                                    1.12.1
    xlwt                                     1.3.0
    zipp                                     3.19.0
    zope.interface                           6.4.post2
