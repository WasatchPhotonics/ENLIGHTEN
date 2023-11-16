# Windows 10 Development Environment

Consider using the wiki page instead: https://github.com/WasatchPhotonics/ENLIGHTEN/wiki/Build-Win10

## Dependencies

The following installation sequence is recommended:

- [Miniconda](https://conda.io/miniconda.html) (latest for Python 3.x on Win64)
- [Git for Windows](https://git-scm.com/download/win)
    - select "Use Git and optional Unix tools from the Command Prompt"
- [InnoSetup](http://www.jrsoftware.org/isinfo.php) (tested 6.0.4)
- [Wasatch.PY](https://github.com/WasatchPhotonics/Wasatch.PY) (clone parallel to Enlighten)
- [Enlighten](https://github.com/WasatchPhotonics/ENLIGHTEN) (clone parallel to Wasatch.PY)

Windows environments have additional dependencies if you need KnowItAll support:

- [KnowItAllWrapper](https://github.com/WasatchPhotonics/KnowItAllWrapper)
    - a compiled copy of KIAConsole is in dist/

Binary snapshots of key installers are retained for posterity in [Enlighten-dependencies](https://github.com/WasatchPhotonics/Enlighten-dependencies).

See [MAINTENANCE](MAINTENANCE.md) for temporary changes or workarounds to
the build process.

## Getting Enlighten Source

You must have a copy of Wasatch.PY in a parallel directory.

    $ git clone git@github.com:WasatchPhotonics/ENLIGHTEN.git
    $ git clone git@github.com:WasatchPhotonics/Wasatch.PY.git
    $ cd ENLIGHTEN

## Configuration

Enlighten is written in Python, so there is no "build" per se -- you don't have
to explicitly compile classes the way you do in C++ or Java.

However, you do need to properly configure your environment with all our library 
dependencies and package requirements.

This includes adding to your PYTHONPATH:

    $ set PYTHONPATH=..\Wasatch.PY;pluginExamples;.;enlighten\assets\uic_qrc

*Note:* when setting environment variables like PYTHONPATH under Windows, 
_do not_ quote them (e.g., do *not* type: set PYTHONPATH="..\Wasatch.PY")

## Activating the environment

When interacting with Enlighten, be sure to activate your shell. This provides 
access to the dependencies, such as numpy and matplotlib, and it is required for
running Enlighten or creating installers.

    $ scripts\bootstrap.bat activate

Note that conda will "solve" (create) environments much more quickly if you
use the new libmamba solver described here:

- https://www.anaconda.com/blog/a-faster-conda-for-a-growing-community

## Running Enlighten

From an activated shell, use the run script

    $ run.bat

Note that to test ENLIGHTEN with a spectrometer, you'll need to install the
libusb drivers.  Normally this is done for customers when they run the 
ENLIGHTEN binary installer.  If you're running from a source distribution,
you'll need to install those drivers manually so Windows knows how to enumerate
the spectrometer.

Basically, follow this procedure:

- https://github.com/WasatchPhotonics/Wasatch.NET#post-install-step-1-libusb-drivers

Except when it tells you to navigate here:

    C:\Program Files\Wasatch Photonics\Wasatch.NET\libusb\drivers

instead navigate here:

    enlighten\scripts\support\files\libusb\drivers.

## Build a Release Installer

The current recommended process is to build installers on Win10-64.

To build an installer, you need to first install all dependencies for your
platform, then run this from a Git Cmd shell:

    scripts\bootstrap.bat installer

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

If you get this on Windows using ENLIGHTEN 64-bit:

  File "C:\Users\mzieg\miniconda3\envs\conda\_enlighten3\lib\site-packages\usb\backend\libusb1.py", line 893, in ctrl\_transfer
    ret = _check(self.lib.libusb_control_transfer(
  File "C:\Users\mzieg\miniconda3\envs\conda\_enlighten3\lib\site-packages\usb\backend\libusb1.py", line 604, in \_check
    raise USBError(_strerror(ret), ret, _libusb_errno[ret])
        usb.core.USBError: [Errno 2] Entity not found

One option is to rename C:/Windows/System32/libusb-1.0.dll to Libusb-1.0-save.dll.

This issue should be solved by Wasatch.PY 2.0.2, which explicitly specified the
libusb0 backend in calls to usb.core.find().
