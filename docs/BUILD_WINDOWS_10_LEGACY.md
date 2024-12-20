# Windows 10 Legacy Development Process (no longer tested/supported)

The current ENLIGHTEN development process is based in Windows 11 and described in
[BUILD_WINDOWS](docs/BUILD_WINDOWS.md).

These are older setup instructions from before the new win11\bootstrap.py script
was available. They may still work for you, they may not.

## Create Virtual Environment

    $ cd %HOME%
    $ python3.11 -m venv enlighten_py311
    $ enlighten_py311\Scripts\activate

## Getting Enlighten Source

You must have a copy of Wasatch.PY in a parallel directory.

    $ git clone git@github.com:WasatchPhotonics/ENLIGHTEN.git
    $ git clone git@github.com:WasatchPhotonics/Wasatch.PY.git
    $ cd ENLIGHTEN

## Install Package Dependencies

    $ pip install requirements.txt
    $ pip install pywin32 spc_spectra

## Configuration

    $ set PYTHONPATH=..\Wasatch.PY;..\jcamp;plugins;.;enlighten\assets\uic_qrc
    $ sh scripts\rebuild_resources.sh

## Install libusb-win32 drivers

To test ENLIGHTEN with a spectrometer, you'll need to install the libusb drivers.
Normally this is done for customers when they run the ENLIGHTEN binary installer.
If you're running from a source distribution, you'll need to install those 
drivers manually so Windows knows how to enumerate the spectrometer.

Basically, follow this...

- https://github.com/WasatchPhotonics/Wasatch.NET#post-install-step-1-libusb-drivers

...except when it tells you to navigate here...

    C:\Program Files\Wasatch Photonics\Wasatch.NET\libusb\drivers

...instead navigate here:

    enlighten\scripts\support\files\libusb\drivers

## Run ENLIGHTEN

    $ python scripts\Enlighten.py --help
    $ python scripts\Enlighten.py 

## Build a Release Installer

The latest recommended process is to build installers on Win11-64.

To build an installer, you need to first install all dependencies for your
platform, then run this from a Git Cmd shell (will destroy and re-create venv)

    $ scripts\bootstrap\win10\bootstrap.bat oneshot 

## Convenience Scripts

See scripts/dos for some convenience scripts for quickly running ENLIGHTEN from 
source and building installers.

## Debugging Inno Setup installers

Note that you can run the generated ENLIGHTEN-Setup64-x.y.z.exe installer with a /log
argument, which will write a file like "Setup Log YYYY-MM-DD #001.txt" in your %TEMP%
directory.  This can be helpful in determining which files were installed where during
the installation process.

## pyusb "backend not found"

This typically means you need to install libusb's Windows DLL in the appropriate
System32 folder.  Ironically, one of the easiest ways to do this is to install a
previous version of ENLIGHTEN (the installer does this automatically).

## libusb-win32 issues

Try setting this environment variable before launching ENLIGHTEN, then checking STDERR:

    > set LIBUSB_DEBUG=4

### libusb1 "Entity not found"

If you get something like this on Windows using ENLIGHTEN 64-bit:

  File "C:\Users\mzieg\miniconda3\envs\conda\_enlighten3\lib\site-packages\usb\backend\libusb1.py", line 893, in ctrl\_transfer
    ret = _check(self.lib.libusb_control_transfer(
  File "C:\Users\mzieg\miniconda3\envs\conda\_enlighten3\lib\site-packages\usb\backend\libusb1.py", line 604, in \_check
    raise USBError(_strerror(ret), ret, _libusb_errno[ret])
        usb.core.USBError: [Errno 2] Entity not found

One option is to rename C:/Windows/System32/libusb-1.0.dll to Libusb-1.0-save.dll.

This issue should be solved by Wasatch.PY 2.0.2, which explicitly specified the
libusb0 backend in calls to usb.core.find().
