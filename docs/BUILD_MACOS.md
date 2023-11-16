# MacOS Development Environment

We used to be able to get MacOS running with Miniconda, but I think that no 
longer works with PySide2; it may with PySide6, but we haven't attempted that 
conversion yet.

I was able to get it running from source on an Intel Mac (Ventura 13.4.1(c))
using Homebrew.  Basically (I'm not sure everything I typed) this:

    $ brew install pyside2
    $ brew install python-tk@3.10
    $ export PATH=/usr/local/Cellar/python@3.10/3.10.13/bin
    $ export PYTHONPATH=.:pluginExamples:enlighten/assets/uic_qrc:../Wasatch.PY:../spyc_writer/src
    $ python3.10 scripts/Enlighten.py --log-level debug 1>enlighten.out 2>enlighten.err

See appendices below for notes.

See [MAINTENANCE](README_MAINTENANCE.md) for temporary changes or workarounds to
the build process.

# Installer Build Process

## Install dependencies, if not already done:

    $ pip install pyinstaller
    $ brew install platypus

## Run pyinstaller

    $ make mac-installer

(Note this will automatically run Platypus to convert the Mac Python .dylibs to 
a MacOS .app "application".)

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

    $ brew ls
    ==> Formulae
    aom             gdk-pixbuf  libffi           libxft      openssl@1.1    sdl2
    apr             gdrive      libheif          libxmp      openssl@3      sdl2_mixer
    apr-util        gettext     libice           libxmu      opus           shared-mime-info
    astyle          ghostscript libidn           libxp       opusfile       six
    awscli          giflib      libidn2          libxrender  p7zip          sloccount
    bdw-gc          glib        liblqr           libxt       pandoc         sphinx-doc
    berkeley-db     glm         libmodplug       libyaml     pango          sqlite
    brotli          gmp         libnghttp2       little-cms2 pcre           stlink
    c-ares          gnu-getopt  libogg           llvm        pcre2          subversion
    ca-certificates graphite2   libomp           llvm@15     pdfcrack       swig
    cairo           graphviz    libpng           lsusb       perl           tcl-tk
    cffi            gts         libpthread-stubs lua         pixman         telnet
    cloc            harfbuzz    libraw           lynx        pkg-config     tree
    cmake           hidapi      librsvg          lz4         platypus       udunits
    cocoapods       highway     libsamplerate    lzo         portaudio      unrar
    coreutils       icu4c       libsm            m4          portmidi       utf8proc
    docbook         ilmbase     libsndfile       mame        pugixml        vim
    docbook-xsl     imagemagick libsodium        markdown    pycparser      w3m
    docutils        imath       libtiff          md5sha1sum  pygments       webp
    dos2unix        jasper      libtool          mpdecimal   pyside@2       wget
    doxygen         jbig2dec    libunistring     mpg123      python-certifi x265
    flac            jpeg        libusb           mysql@5.6   python-tk@3.10 xbitmaps
    fluid-synth     jpeg-turbo  libuv            ncurses     python-tk@3.11 xmlto
    fontconfig      jpeg-xl     libvmaf          netpbm      python@3.10    xorgproto
    freetype        jq          libvorbis        node        python@3.11    xpdf
    fribidi         jsonlint    libx11           oniguruma   qt@5           xz
    frotz           lame        libxau           openexr     rapidjson      z3
    gd              libao       libxcb           openjdk     rclone         zstd
    gdb             libavif     libxdmcp         openjpeg    readline
    gdbm            libde265    libxext          openmotif   ruby

    ==> Casks
    xquartz

    mzieg-macbook.local [~/work/code/enlighten] mzieg  8:16PM $ echo $PATH
    /usr/local/Cellar/python@3.10/3.10.13/bin:/Users/mzieg/bin:/Users/mzieg/work/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt/mysql@5.6/bin:/usr/local/share/dotnet

    mzieg-macbook.local [~/work/code/enlighten] mzieg  8:16PM $ echo $PYTHONPATH
    ../spyc_writer/src:../Wasatch.PY:pluginExamples:.:enlighten/assets/uic_qrc

    mzieg-macbook.local [~/work/code/enlighten] mzieg  8:16PM $ which python3.10
    /usr/local/Cellar/python@3.10/3.10.13/bin/python3.10

    macbook.local [~/work/code/enlighten] mzieg  8:15PM $ python3.10 -m pip list
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
    pip                              23.2.1
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
