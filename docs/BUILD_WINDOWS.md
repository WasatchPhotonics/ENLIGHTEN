# Windows 11 Development Environment

The Windows development process closely mimics the MacOS, Linux and Raspberry Pi
process, in that it too now heavily uses BUILD_PYPI. 

However, it does have a few unique notes, especially given that we still plan to
release pre-compiled binary installers for Windows (which are not planned for 
other platforms.

All Windows development steps currently assume using Git for Windows Bash shell:

- https://git-scm.com/install/windows

There is probably no reason this could not be made to work using PowerShell or 
[Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl),
I just haven't taken time to learn and verify those environments. If someone
wants to do so, and update the docs accordingly, that would be sweet.

## Dependencies

### Python 3.14

The default supported Python version is 3.14. At writing, the latest Python 3.14
binary installer for Windows can be found here:

- https://www.python.org/downloads/release/python-3148/

By default, this will put Python 3.14 someplace like:

    /c/Users/mzieg/AppData/Local/Programs/Python/Python314/python

You will need to update your Windows %PATH% to make sure those directories
are high in your search order.

Other than Python, the following installation sequence is recommended:

- [Git for Windows](https://git-scm.com/install/windows)
    - select "Use Git and optional Unix tools from the Command Prompt"

### Inno Setup (building installers)

If you want to build binary installers, you will need the following additional 
tools:

- [InnoSetup](http://www.jrsoftware.org/isinfo.php) (last tested 6.3.3)

# Windows 11 Standard Development Process 

For Windows 11, you should then be able to install all Python dependencies, and 
run the program from source like this (assuming you've cloned ENLIGHTEN to 
$HOME/work/code/enlighten):

    $ cd ~/work/code/enlighten
    $ python -m venv venv
    $ . venv/Scripts/activate
    (venv) $ pip install -e .
    (venv) $ enlighten --log-level debug 2>enlighten.err 1>enlighten.out

    (edit files under src/wp_enlighten as you will)

# Build Installer

    $ scripts/make_windows_installer.sh

# Release Installer

    $ scripts/deploy

# Release PyPi Package

Personally I do this from MacOS, but:

    $ make publish-test
    $ make publish
