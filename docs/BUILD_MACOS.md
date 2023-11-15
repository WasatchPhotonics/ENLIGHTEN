# MacOS Development Environment

We used to be able to get MacOS running with Miniconda, but we moved to Homebrew
after problems with PySide2. Even though we've now moved to PySide6, we're
currently sticking with Homebrew until a reason presents itself to move back.

Testing was conducted from an Intel Mac (Ventura 13.4.1(c)) using MacOS 14 Sonoma
and Homebrew.  See the "Appendix: Homebrew" at the bottom of this file for 
a list of the homebrew and pip packages I had installed.  I'm afraid I have not
yet generated a "minimal" set of what is required to run ENLIGHTEN, but this set
seems to work.

    $ export PYTHONPATH=.:pluginExamples:enlighten/assets/uic_qrc:../Wasatch.PY:../spyc_writer/src:../jcamp
    $ python scripts/Enlighten.py --log-level debug 1>enlighten.out 2>enlighten.err

See [MAINTENANCE](MAINTENANCE.md) for temporary changes or workarounds to
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

    (base) mzieg-macbook.local [~/work/code/enlighten] mzieg 10:22AM $ echo $PATH
    /Users/mzieg/miniconda3/bin:/Users/mzieg/miniconda3/condabin:/Users/mzieg/bin:/Users/mzieg/work/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/opt/mysql@5.6/bin:/usr/local/share/dotnet

    (base) mzieg-macbook.local [~/work/code/enlighten] mzieg 10:22AM $ echo $PYTHONPATH
    .:pluginExamples:enlighten/assets/uic_qrc:../Wasatch.PY:../spyc_writer/src:../jcamp

    (base) mzieg-macbook.local [~/work/code/enlighten] mzieg 10:23AM $ which python
    python: aliased to python3.10

    (base) mzieg-macbook.local [~/work/code/enlighten] mzieg 10:23AM $ which python3.10 
    /usr/local/bin/python3.10

    macbook.local [~/work/code/enlighten] mzieg  8:15PM $ python3.10 -m pip list
    Package                 Version
    ----------------------- ---------
    boltons                 23.0.0
    Brotli                  1.0.9
    certifi                 2023.7.22
    cffi                    1.15.1
    charset-normalizer      3.2.0
    colorama                0.4.6
    conda                   23.7.3
    conda-content-trust     0.1.3
    conda-libmamba-solver   23.7.0
    conda-package-handling  2.2.0
    conda_package_streaming 0.9.0
    contourpy               1.2.0
    cryptography            38.0.4
    cycler                  0.12.1
    fonttools               4.44.0
    idna                    3.4
    jsonpatch               1.32
    jsonpointer             2.0
    kiwisolver              1.4.5
    libmambapy              1.5.0
    matplotlib              3.8.1
    numpy                   1.26.2
    packaging               23.1
    Pillow                  10.1.0
    pip                     23.2.1
    pluggy                  1.3.0
    pycosat                 0.6.4
    pycparser               2.21
    pyOpenSSL               23.2.0
    pyparsing               3.1.1
    PySide6                 6.6.0
    PySide6-Addons          6.6.0
    PySide6-Essentials      6.6.0
    PySocks                 1.7.1
    python-dateutil         2.8.2
    requests                2.31.0
    ruamel.yaml             0.17.32
    ruamel.yaml.clib        0.2.7
    setuptools              68.1.2
    shiboken6               6.6.0
    six                     1.16.0
    toolz                   0.12.0
    tqdm                    4.66.1
    urllib3                 2.0.4
    wheel                   0.41.2
    zstandard               0.19.0

# Appendix: MacOS and PySide2

If you need to get PySide2 running on MacOS, note the following worked:

    $ brew install pyside2
    $ brew install python-tk@3.10
    $ export PATH=/usr/local/Cellar/python@3.10/3.10.13/bin:$PATH
