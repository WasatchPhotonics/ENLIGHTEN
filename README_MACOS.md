# MacOS Development Environment

The normal setup process seems to work, with just a few tweaks:

- Use miniconda3 and the conda_win10.yml environment file to create a conda_enlighten3 environment.
- Use pip to install the packages listed at the end of conda_win10.yml (including pyqtgraph).
- scripts/rebuild_resources.sh seems to work as-is (follows the Linux conditionals).
- designer.sh has a tweak to support MacOS.
- wasatch.applog has a tweak to support both old "Darwin" and new "macOS" Python platforms.
- scripts/enlighten.py has a tweak for Big Sur from here:
    - https://forum.qt.io/topic/120846/big-sur-pyside2-not-showing-a-widgets

# Running from Source (example)

    $ cd ~/work/code/enlighten
    $ conda activate conda_enlighten3
    $ export PYTHONPATH="../Wasatch.PY:pluginExamples:."
    $ python scripts/Enlighten.py
    
# Installer Build Process

Install dependencies, if not already done:

    $ pip install pyinstaller
    $ brew install platypus

Run pyinstaller:

    $ make mac-installer

(Note this will automatically run Platypus to convert the Mac Python .dylibs to 
a MacOS .app "application".)

Post to website:

    $ scripts/deploy --mac

# FAQ

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
