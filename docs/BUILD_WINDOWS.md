# Windows 10/11 Development Environment

This document attempts to maintain a common build process for both
Windows 10 and Windows 11.  Note that released installers are currently
always built from Windows 11 (but are believed to work on Windows 10).

## Dependencies

The default supported Python version is 3.11. The latest Python 3.11 binary 
installer for Windows can be found here:

- https://www.python.org/downloads/windows/
    - e.g. https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

By default, this will put Python 3.11 someplace like:

    /c/Users/mzieg/AppData/Local/Programs/Python/Python311/python
    /c/Users/mzieg/AppData/Local/Programs/Python/Python311/python/Scripts

You will need to update your Windows %PATH% to make sure those directories
are high in your search order.

Other than Python, the following installation sequence is recommended:

- [Git for Windows](https://git-scm.com/download/win)
    - select "Use Git and optional Unix tools from the Command Prompt"
- [InnoSetup](http://www.jrsoftware.org/isinfo.php) (last tested 6.3.3)
- [Wasatch.PY](https://github.com/WasatchPhotonics/Wasatch.PY) (clone parallel to Enlighten)

Windows environments have additional dependencies if you need KnowItAll support:

- [KnowItAllWrapper](https://github.com/WasatchPhotonics/KnowItAllWrapper)
    - a compiled copy of KIAConsole is in dist/

See [MAINTENANCE](MAINTENANCE.md) for temporary changes or workarounds to
the build process.

# Windows 11 Standard Development Process (New Bootstrap Scripts)

For Windows 11, you should then be able to install all Python dependencies, and 
run the program from source like this (assuming you've cloned ENLIGHTEN to 
%HOME%\work\code\enlighten):

    C> cd %HOME%\work\code\enlighten
    C> python scripts\bootstrap\win11\bootstrap.py

# Release Installer

After successfully running ENLIGHTEN from source using the above procedure, you 
can then build a release installer using Pyinstaller and Inno Setup:

    C> cd %HOME%\work\code\enlighten
    C> scripts\make_windows_installer.bat
