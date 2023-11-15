# Maintenance

Miscellaneous notes, advice and history on how to maintain and extend ENLIGHTEN.

If you haven't already, see [Architecture](ARCHITECTURE.md) for an 
introduction to key classes.

## jcamp_writefile

ENLIGHTEN currently depends on an in-progress pull request on a fork of the main
jcamp repository:

- https://github.com/nzhagen/jcamp/pull/35

For now, developers are recommended to clone Wasatch's fork of frenchytheasian/jcamp
(e.g. in in a sibling directory to ENLIGHTEN) and add to your PYTHONPATH:

    $ cd ..   
    $ git clone git@github.com:WasatchPhotonics/jcamp.git
    $ export PYTHONPATH=$PYTHONPATH:$PWD/jcamp

This note will be removed when frenchytheasian's pull request is merged into the
main (nzhagen) jcamp distribution and released over PyPi.

## Nomenclature

### Why "enlighten.Authentication.Authentication" vs just "enlighten.Authentication"?

In Python, a directory is a _package_ and a .py/c file is a _module_.  If you 
want to seperate each class in its own file (which is my preference), then by
definition each class will exist within its own module.

According to [PEP8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names),
module names should be lowercase, so technically the Authentication class should
be defined in authentication.py.  But I came from C++ and Java, where we like to
name the file after the class for consistency.

## Release Process

- update version number in enlighten/common.py
    - re-run Enlighten.py (forces common.pyc recompile)
- update CHANGELOG.md 
- build a Windows installer (see [Windows](BUILD_WIN11.md))
- git tag x.y.z
- git push --tag
- optionally build [Linux](BUILD_LINUX.md) and [Mac](BUILD_MACOS.md) installers
- run scripts/deploy --win [--linux] [--mac]

## Graphics

(see [Qt](QT.md) and [CSS](CSS.md) notes)

When adding images to uic\_qrc/images/devices or ./grey\_images, remember 
to update uic\_qrc/devices.qrc or ./grey\_icons.qrc, then do "scripts\rebuild_resources.sh".

Note there's a Qt-CSS bug where you can't have whitespace in "qlineargradient(spread:pad":

- https://www.qtcentre.org/threads/46371-QSS-qlineargradient-not-working-when-inserting-whitespaces

## "Script will not execute"

Sometimes you'll build a Windows installer, and the installed Enlighten.exe executable
won't launch at all with a "Script will not execute" message.  No logfile is available,
typically because Python failed to even load and start Enlighten.py.

You can debug these by removing the "--windowed" line in scripts/bootstrap.bat's call
to pyinstaller.  That will let the generated Enlighten.exe run within a "DOS Window"
which will allow error messages to appear at stdout/stderr.

It is also helpful to simply run the installed enlighten.exe from a Cmd shell, i.e.:

    C:\Program Files (x86)\Wasatch Photonics\ENLIGHTEN\Enlighten> enlighten.exe

    Traceback (most recent call last):
      File "scripts\Enlighten.py", line 15, in <module>
      File "c:\users\mzieg\miniconda2\envs\conda_enlighten\lib\site-packages\PyInstaller-3.4.dev0_ga2c73bce.mod-py2.7.egg\PyInstaller\loader\pyimod03_importers.py", line 396, in load_module
            exec(bytecode, module.__dict__)
      File "enlighten\Controller.py", line 11, in <module>
    ImportError: No module named psutil
    [6572] Failed to execute script Enlighten
