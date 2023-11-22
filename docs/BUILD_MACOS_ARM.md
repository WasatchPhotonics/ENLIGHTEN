# MacOS Development Environment

These are instructions to set up an Enlighten build and development environment on an ARM based Mac.
These instructions were developed against a 2022 Apple M2 Macbook Air running macOS Monterey 12.7.1.

1) Install homebrew using the instructions from http://brew.sh

Be sure to include the following line in your `~/.zshrc` file. This enables the `brew` command in
subsequent terminals.

    eval "$(/opt/homebrew/bin/brew shellenv)"

2) From a terminal pointing to your Enlighten directory setup the correct python path.

    export PYTHONPATH=.:pluginExamples:enlighten/assets/uic_qrc:../Wasatch.PY:../spyc_writer/src:../jcamp

You may choose to include something similar to this in your `~/.zshrc` as well. If you do, make sure to use 
absolute paths.

3) Clone all depending repositories.

    cd .. # cd to directory containing Enlighten
    git clone git@github.com:WasatchPhotonics/Wasatch.PY
    git clone git@github.com:WasatchPhotonics/spyc_writer
    git clone git@github.com:WasatchPhotonics/jcamp

Note these commands may require you to have your ssh keys setup to read and write our repositories. If you
do not wish to modify these repositories you may use these alternative commands instead.

    cd .. # cd to directory containing Enlighten
    git clone https://github.com/WasatchPhotonics/Wasatch.PY
    git clone https://github.com/WasatchPhotonics/spyc_writer
    git clone https://github.com/WasatchPhotonics/jcamp

4) Install pip requirements

    python4 -m pip install -r requirements.txt


5) Rebuild resources

I had trouble running our rebuild_resources.sh script on the ARM mac. I'm not sure if it works on Intel macs
either. I decided to remove the generated files from our .gitignore so it can be generated on a different
OS and pulled into the build platform.

6) Install additional dependencies

Some of these are left out of requirements.txt because they are installed via miniconda on other platforms.

    python3 -m pip install psutil
    brew install libusb # get a backend for pyusb
    ln -s /opt/homebrew/lib ~/lib # make it available to python
    python3 -m pip install xlwt
    python3 -m pip install qimage2ndarray
    python3 -m pip install pexpect
    python3 -m pip install pandas

    # enlighten will start without these, but they are still useful or needed for some features
    python3 -m pip install scipy
    python3 -m pip install pytest

7) Start Enlighten

    python scripts/Enlighten.py --log-level debug 1>enlighten.out 2>enlighten.err

You can also use the shorter to type command, for a quick test:

    python scripts/Enlighten.py

See [MAINTENANCE](MAINTENANCE.md) for temporary changes or workarounds to
the build process.

# Installer Build Process

## Install dependencies, if not already done:

    pip install pyinstaller

## Run pyinstaller

    make mac-installer

We used platypus to convert the program into a MacOS .app, but platypus is no longer supported.
It is also no longer available on brew.

## Test the program.

    cd build-mac/EnlightenGUI
    ./EnlightenGUI

I had an error where jcamp was not found. I resolved it by copying the repository into the _internal folder.

    cp -rf ../../../jcamp _internal

Clicking the [x] to close the program causes it to segfault without the normal prompt.
Then the program halts without returning to a new prompt line. Press Ctrl-C to fully close it.

This is something we should fix, but I will continue now to see if I can get it to the .dmg stage.
I checked that the program is able to display spectra from an XS unit.

## Package into a .app

The steps for creating a .app package may change over time. I recommended checking online for the latest technique, and applying that to the output binary and resource files generated in the last step (The contents of build-mac/EnlightenGUI).

I am following these steps: https://apple.stackexchange.com/a/269045

It's simply to make a folder with the .app extension and place the executable script (binary) of the same name in it.

This method does not provide the app icon. That can be added by dragging it into the Get Info window in
macOS.

## Create a .dmg

This part is not currently scripted, and is being tested manually.  Basically:

- use Disk Utility to create a blank read-write .dmg (not from Folder) of the needed size (.app filesize + 20%)
    - name the new .dmg file ENLIGHTEN-x.y.z-rw.dmg
    - mount the dmg (double-click .dmg)
    - label the volume "ENLIGHTEN™ x.y.z"
- populate and decorate read-write image
    - open the dmg (dbl-click Finder icon)
    - drag the .app into the window
    - opt-cmd-drag an alias of your Applications folder into the window
    - set view to icon
    - create a new folder inside the window called 'background'
    - in Terminal
        - cd /Volumes/ENLIGHTEN*
        - mv background .background
        - open .background
        - copy scripts/mac_installer/folder_background.png to .background
    - right-click on folder and choose "View Options"
    - set background to Picture
    - drag folder_background.png from (currently open) .background folder into View Options
    - arrange icons sensibly
    - close window
    - unmount .dmg (drag to Trash)
- make read-only with checksum:
    - `hdiutil convert ENLIGHTEN-x.y.z-rw.dmg -format UFBI -o ENLIGHTEN-x.y.z.dmg`
    - rm ENLIGHTEN-x.y.z-rw.dmg
    
## Post to website

Old method: (needs updated for .dmg)

    $ scripts/deploy --mac

# FAQ

## Installer capitalization

Note PyInstaller capitalization in Makefile target mac-installer.

## Known differences from Windows/Linux versions

Keyboard shortcuts use command key (⌘) rather than ctrl, e.g. cmd-D toggles the 
dark spectrum. Cmd-H seems pre-allocated to "minimize window" unfortunately.

## Expanded .zip may not run from Downloads directory

I have no theory or link to explain this, but I was able to reproduce it on my 
Macbook. I downloaded the ENLIGHTEN-MacOS-x.y.z.zip to ~/Downloads, then expanded
the zipfile to create ENLIGHTEN-x.y.z.app.

I right-clicked on the .app to open it (since it was from the internet), and gave
approval.

The ENLIGHTEN icon briefly appeared in my Dock (showing it was launching), then
it immediately closed.  Huh.

I then MOVED the ENLIGHTEN-x.y.z.app to a different directory (~/work/tmp),
double-clicked on it...and now it would open and run.  I have no idea why.

## Why is Platypus required?

- Currently there is some issue and it is unclear the root cause, but the 
  issue means the app will run from the command line but the .app will not
- An example if you navigate to the app and do Enlighten.app/Content/MacOS/Enlighten, 
  it will run normally, but a double click on the app icon will just cause the 
  normal animation but Enlighten never opens
- This has been common across Mac for some time and seems to come up in various 
  forms and is just hard to track down because there is no feedback or logging, 
  so this is the work around for the time being

Below are some example threads:

- https://github.com/pyinstaller/pyinstaller/issues/3753
- https://stackoverflow.com/questions/63611190/python-macos-builds-run-from-terminal-but-crash-on-finder-launch
- https://github.com/pyinstaller/pyinstaller/issues/5109

# Appendix: Homebrew

I don't remember everything I installed, when or why, but this is what I had 
installed when it worked...

    mzieg-macbook.local [~/work/code/enlighten] mzieg  8:16PM $ brew ls
    ==> Formulae
    aom             glm              libraw        markdown       python-tk@3.11
    apr             gmp              librsvg       md5sha1sum     python@3.10
    apr-util        gnu-getopt       libsamplerate mpdecimal      python@3.11
    astyle          graphite2        libsm         mpg123         qt@5
    awscli          graphviz         libsndfile    mysql@5.6      rapidjson
    bdw-gc          gts              libsodium     ncurses        rclone
    berkeley-db     harfbuzz         libtiff       netpbm         readline
    brotli          hidapi           libtool       node           ruby
    c-ares          highway          libunistring  oniguruma      sdl2
    ca-certificates icu4c            libusb        openexr        sdl2_mixer
    cairo           ilmbase          libusb-compat openjdk        shared-mime-info
    cffi            imagemagick      libuv         openjpeg       six
    cloc            imath            libvmaf       openmotif      sloccount
    cmake           jasper           libvorbis     openssl@1.1    sphinx-doc
    cocoapods       jbig2dec         libx11        openssl@3      sqlite
    coreutils       jpeg             libxau        opus           stlink
    docbook         jpeg-turbo       libxcb        opusfile       subversion
    docbook-xsl     jpeg-xl          libxdmcp      p7zip          swig
    docutils        jq               libxext       pandoc         tcl-tk
    dos2unix        jsonlint         libxft        pango          telnet
    doxygen         lame             libxmp        pcre           tree
    flac            libao            libxmu        pcre2          udunits
    fluid-synth     libavif          libxp         pdfcrack       unrar
    fontconfig      libde265         libxrender    perl           utf8proc
    freetype        libffi           libxt         pixman         vim
    fribidi         libheif          libyaml       pkg-config     w3m
    frotz           libice           little-cms2   platypus       webp
    gd              libidn           llvm          pngcrush       wget
    gdb             libidn2          llvm@15       portaudio      x265
    gdbm            liblqr           lsusb         portmidi       xbitmaps
    gdk-pixbuf      libmodplug       lua           pugixml        xmlto
    gdrive          libnghttp2       lynx          pycparser      xorgproto
    gettext         libogg           lz4           pygments       xpdf
    ghostscript     libomp           lzo           pyside@2       xz
    giflib          libpng           m4            python-certifi z3
    glib            libpthread-stubs mame          python-tk@3.10 zstd

    ==> Casks
    xquartz

    mzieg-macbook.local [~/work/code/enlighten] mzieg $ echo $PATH
    /Users/mzieg/bin:/Users/mzieg/work/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt/mysql@5.6/bin:/usr/local/share/dotnet

    mzieg-macbook.local [~/work/code/enlighten] mzieg $ echo $PYTHONPATH
    .:pluginExamples:enlighten/assets/uic_qrc:../Wasatch.PY:../spyc_writer/src:../jcamp

    mzieg-macbook.local [~/work/code/enlighten] mzieg $ which python
    python: aliased to python3.10

    mzieg-macbook.local [~/work/code/enlighten] mzieg $ which python3.10 
    /usr/local/bin/python3.10

    macbook.local [~/work/code/enlighten] mzieg $ pip list
    Package                          Version
    -------------------------------- ---------
    absl-py                          1.4.0
    Adafruit-Blinka                  8.20.1
    adafruit-circuitpython-busdevice 5.2.6
    adafruit-circuitpython-requests  2.0.1
    adafruit-circuitpython-typing    1.9.4
    Adafruit-PlatformDetect          3.49.0
    Adafruit-PureIO                  1.1.11
    altgraph                         0.17.3
    astunparse                       1.6.3
    async-timeout                    4.0.3
    bleak                            0.20.2
    boto3                            1.28.38
    botocore                         1.31.38
    cachetools                       5.3.1
    certifi                          2023.7.22
    charset-normalizer               3.2.0
    construct                        2.8.22
    contourpy                        1.1.0
    crcmod                           1.7
    cycler                           0.11.0
    Cython                           3.0.2
    exceptiongroup                   1.1.3
    flatbuffers                      23.5.26
    fonttools                        4.42.1
    gast                             0.4.0
    google-auth                      2.22.0
    google-auth-oauthlib             1.0.0
    google-pasta                     0.2.0
    grpcio                           1.57.0
    h5py                             3.9.0
    idna                             3.4
    importlib-metadata               6.8.0
    importlib-resources              6.0.1
    iniconfig                        2.0.0
    jmespath                         1.0.1
    joblib                           1.3.2
    keras                            2.13.1
    kiwisolver                       1.4.5
    libclang                         16.0.6
    libusb                           1.0.26b5
    macholib                         1.16.2
    Markdown                         3.4.4
    MarkupSafe                       2.1.3
    matplotlib                       3.7.2
    numpy                            1.24.3
    oauthlib                         3.2.2
    opt-einsum                       3.3.0
    packaging                        23.1
    pandas                           2.1.0
    pefile                           2023.2.7
    pexpect                          4.8.0
    Pillow                           10.0.0
    pip                              23.3.1
    pkg-about                        1.0.8
    pluggy                           1.3.0
    protobuf                         4.24.2
    psutil                           5.9.5
    ptyprocess                       0.7.0
    pyasn1                           0.5.0
    pyasn1-modules                   0.3.0
    pyftdi                           0.55.0
    Pygments                         2.16.1
    pygtail                          0.14.0
    pyinstaller                      5.13.2
    pyinstaller-hooks-contrib        2023.8
    pyobjc-core                      9.2
    pyobjc-framework-Cocoa           9.2
    pyobjc-framework-CoreBluetooth   9.2
    pyobjc-framework-libdispatch     9.2
    pyparsing                        3.0.9
    pyqtgraph                        0.13.3
    pyserial                         3.5
    PySide2                          5.15.2.1
    PySide6                          6.6.0
    PySide6-Addons                   6.6.0
    PySide6-Essentials               6.6.0
    pytest                           7.4.0
    python-dateutil                  2.8.2
    pytz                             2023.3
    pyudev                           0.24.1
    pyusb                            1.2.1
    PyWavelets                       1.4.1
    qimage2ndarray                   1.10.0
    requests                         2.31.0
    requests-oauthlib                1.3.1
    rsa                              4.9
    s3transfer                       0.6.2
    scikit-learn                     1.3.0
    scipy                            1.11.2
    seabreeze                        2.4.0
    setuptools                       68.1.2
    shiboken2                        5.15.2.1
    shiboken6                        6.6.0
    six                              1.16.0
    spc-spectra                      0.4.0
    SPyC_Writer                      0.2.0
    superman                         0.1.2
    tensorboard                      2.13.0
    tensorboard-data-server          0.7.1
    tensorflow                       2.13.0
    tensorflow-estimator             2.13.0
    tensorflow-io-gcs-filesystem     0.33.0
    termcolor                        2.3.0
    threadpoolctl                    3.2.0
    tk                               0.1.0
    tomli                            2.0.1
    typing_extensions                4.5.0
    tzdata                           2023.3
    urllib3                          1.26.16
    Werkzeug                         2.3.7
    wheel                            0.41.2
    wrapt                            1.15.0
    xlwt                             1.3.0
    zipp                             3.16.2

# Appendix: MacOS and PySide2

If you need to get PySide2 running on MacOS, note the following worked:

    $ brew install pyside2
    $ brew install python-tk@3.10
    $ export PATH=/usr/local/Cellar/python@3.10/3.10.13/bin:$PATH
