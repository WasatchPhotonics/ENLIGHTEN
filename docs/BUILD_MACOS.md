# MacOS Development Environment

In general, MacOS platforms should follow BUILD_PYPI.md.

The following additional steps may be required to properly configure the "system 
Python" in ways which cannot be done within a `venv`.

Instructions assume [Homebrew](https://brew.sh) is installed (essentially the
MacOS equivalent to Linux's RPM / apt-get, or FreeBSD's "ports").

Testing is henceforth exclusive to Apple Silicon (M-series ARM SoC), as 
regrettably I've destroyed my third and likely final 2019 Intel PowerBook :-(

For legacy versions of this document, see ENLIGHTEN sources <4.2.14.

## How to Install Python

On MacOS, Python should be installed like this, to provide the compiled-in Tcl/Tk
support required by some GUI dependencies.

    $ brew install python-tk@3.14

MZ: I tried python-tk@3.15 on 12-Oct-2026 from Golden Gate 27.0.1 and there was
    no matching wheel for ai-edge-litert.

## missing backend

Install the libusb backend with:

    $ brew install libusb

If that doesn't do it, make sure libusb-1.0.dylib is in your $DYLD_LIBRARY_PATH:

    $ export DYLD_LIBRARY_PATH=/opt/homebrew/lib:/usr/local/lib
