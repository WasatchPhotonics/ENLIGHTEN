# Installing and running ENLIGHTEN on MacOS

In general, MacOS platforms should follow BUILD_PYPI.md:

    $ mkdir ~/enlighten
    $ cd ~/enlighten
    $ python3 -m venv venv
    $ . venv/bin/activate
    (venv) $ pip install wp-enlighten
    (venv) $ enlighten

That's it. On successive executions, it's even shorter:

    $ cd ~/enlighten
    $ . venv/bin/activate
    (venv) $ enlighten

Instructions assume [Homebrew](https://brew.sh) is installed (essentially the
MacOS equivalent to Linux's RPM / apt-get, or FreeBSD's "ports").

# How to Install Python

On MacOS, Python should be installed like this, to provide the compiled-in Tcl/Tk
support required by some GUI dependencies.

    $ brew install python-tk@3.14

MZ: I tried python-tk@3.15 on 12-Oct-2026 from Golden Gate 27.0.1 and there was
    no matching wheel for ai-edge-litert.

# Common Problems

## Tooltips

ENLIGHTEN makes heavy use of mouse-over tooltips to provide status or help about
on-screen features, and unfortunately not all tooltips are working on MacOS at
the moment. This seems to be due to issues between Apple's "Liquid Glass" motif
and Qt, and is widely documented online. It's weird because many tooltips work,
but not all of them (like the middle cluster above the scope graph, and the mini-
laser convenience button).

## missing backend

Install the libusb backend with:

    $ brew install libusb

If that doesn't do it, make sure libusb-1.0.dylib is in your $DYLD_LIBRARY_PATH:

    $ export DYLD_LIBRARY_PATH=/opt/homebrew/lib:/usr/local/lib
