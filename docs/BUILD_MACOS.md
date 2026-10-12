# MacOS Development Environment

In general, MacOS platforms should follow BUILD_PYPI.md.

The following additional steps may be required to properly configure the "system Python", in ways which cannot be done within a `venv`.

For legacy versions of this document, see ENLIGHTEN sources <4.2.14.

## How to Install Python

On MacOS, Python should be installed like this, to provide the compiled-in Tcl/Tk
support required by some GUI dependencies.

    $ brew install python-tk@3.14

(MZ: I tried 3.15 12-Ocxt-2026 on Golden Gate 27.0.1 and there was no matching 
ai-edge-litert wheel)

## missing backend

    $ brew install libusb
