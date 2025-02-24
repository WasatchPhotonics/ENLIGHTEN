import logging
import os

from enum import IntEnum

log = logging.getLogger(__name__)

"""
Namespace containing various enums and constants used elsewhere within the 
application.

@todo consider making "common" a package (directory), and each of these classes
      can be modules (files) within it
"""

VERSION = "4.1.24"

ctl = None

class Techniques(IntEnum):
    """ ENLIGHTEN's application version number (checked by scripts/deploy and bootstrap.bat) """
    NONE                     = 0
    EMISSION                 = 1
    RAMAN                    = 2
    REFLECTANCE_TRANSMISSION = 3
    ABSORBANCE               = 4
    COLOR                    = 5
    FLUORESCENCE             = 6
    RELATIVE_IRRADIANCE      = 7

class TechniquesHelper:
    pretty_names = {
        Techniques.NONE: "None",
        Techniques.EMISSION: "Emission",
        Techniques.RAMAN: "Raman",
        Techniques.REFLECTANCE_TRANSMISSION: "Reflectance/Transmission",
        Techniques.ABSORBANCE: "Absorbance",
        Techniques.COLOR: "Color",
        Techniques.FLUORESCENCE: "Fluorescence",
        Techniques.RELATIVE_IRRADIANCE: "Relative Irradiance",
    }

    def get_pretty_name(n):
        return TechniquesHelper.pretty_names.get(n, "UNKNOWN")

class Views(IntEnum):
    """
    It's important to keep this list in sync with the comboBox_view items.
    @todo consider auto-populating inside code
    """
    SCOPE               = 0
    SETTINGS            = 1
    HARDWARE            = 2
    LOG                 = 3
    FACTORY             = 4

class ViewsHelper:
    pretty_names = {
        Views.SCOPE:    "Scope",
        Views.SETTINGS: "Settings",
        Views.HARDWARE: "Hardware",
        Views.LOG:      "Log",
        Views.FACTORY:  "Factory",
    }

    def get_pretty_name(n):
        return ViewsHelper.pretty_names.get(n, "UNKNOWN")

    def parse(s):
        s = s.upper()
        if "HARDWARE"             in s: return Views.HARDWARE
        if "SCOPE"                in s: return Views.SCOPE
        if "RAMAN"                in s: return Views.RAMAN
        if "ABS"                  in s: return Views.ABSORBANCE
        if "TRANS" in s or "REFL" in s: return Views.TRANSMISSION
        log.error("Invalid view: %s", s)
        return Views.SCOPE

class OperationModes(IntEnum):
    RAMAN     = 0
    NON_RAMAN = 1
    EXPERT    = 2

class Pages(IntEnum):
    HARDWARE              = 0 # EEPROM etc
    FACTORY               = 1 # AreaScan etc
    SETTINGS              = 2 # SaveOptions etc
    SCOPE                 = 3 # Graph etc
    LOG                   = 4 # Log view

class Axes(IntEnum):
    PIXELS      = 0
    WAVELENGTHS = 1
    WAVENUMBERS = 2
    COUNTS      = 3
    PERCENT     = 4
    AU          = 5

class AxesHelper:
    ## HTML for Qt
    pretty_names = {
        Axes.PIXELS      : "pixel",
        Axes.WAVELENGTHS : "wavelength (nm)",
        Axes.WAVENUMBERS : "wavenumber (cm&#8315;&#185;)", # cm⁻¹
        Axes.COUNTS      : "intensity (counts)",
        Axes.PERCENT     : "percent (%)",
        Axes.AU          : "absorbance (AU)",
    }

    ## Unicode (not sure these are used)
    suffixes = {
        Axes.PIXELS      : "px",
        Axes.WAVELENGTHS : "nm",
        Axes.WAVENUMBERS : "cm⁻¹",
        Axes.COUNTS      : "",
        Axes.PERCENT     : "%",
        Axes.AU          : "AU",
    }

    def get_pretty_name(n): return AxesHelper.pretty_names.get(n, "Unknown")
    def get_suffix     (n): return AxesHelper.suffixes    .get(n, "??")

class LaserPowerUnits(IntEnum):
    PERCENT     = 0
    MILLIWATT   = 1

##
# We don't actually have FW API to read all of these; final implementation should treat
# enable, delayState, watchdogLockdown, interlockState, and isFiring as separate bits.
class LaserStates(IntEnum):
    DISABLED    = 0
    REQUESTED   = 1
    FIRING      = 2

class FakeOutputHandle:
    """
    We [think we] need to build Windows installers with PyInstaller. However, 
    since Win11 came out, PyInstaller's compiled executables tend to display a 
    black "console window" on either Win10 or Win11, depending on which 
    PyInstaller options you use. The only way we've found to completely hide
    the console window is with --noconsole.

    However, some Python packages (like Tensorflow) really, really want to write
    directly to stdout, and raise exceptions if they can't. So this class is
    provided to represent a fake output filehandle which we can assign to 
    sys.stdout or sys.stderr, even when our executing environment doesn't provide
    those things.
    """
    def __init__(self, name):
        self.name = name

    def write(self, msg):
        if msg is None:
            return
        msg = msg.strip()
        if msg:
            log.debug(f"{self.name}: {msg}")

    def flush(self):
        pass

    def reconfigure(self, *args, **kwargs):
        pass

def get_default_data_dir():
    """
    Return the path used for all Enlighten data except for spectra. This will be something like "~/Documents/EnlightenSpectra"
    The path appropriate for the given platform is returned.

    This location is used for logs and configuration files. Not that this path is NOT configurable, since it is used to load the 
    config (.ini) file.

    The default save location for spectra is also ~/Documents/EnlightenSpectra, but that is driven by SaveOptions, and it IS
    configurable.
    """

    if os.name == "nt":
        return os.path.join(os.path.expanduser("~"), "Documents", "EnlightenSpectra")
    return os.path.join(os.environ["HOME"], "EnlightenSpectra")

def set_controller_instance(inst):
    global ctl
    ctl = inst

def msgbox(prompt, title="Alert", buttons="", detail=None, informative_text=None):
    """
    Display an interupting message to the user.  In common rather than GUI so it can
    be used before Controller / Business Objects fully instantiated.

    Inspired by VB msgbox: 
    https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/msgbox-function
    """

    # doing this import within this method to avoid breaking all dependents of common.py
    # not sure that this would break anything, just to be safe -- move up when confident
    if use_pyside2():
        from PySide2.QtWidgets import QMessageBox
    else:
        from PySide6.QtWidgets import QMessageBox

    # TODO: see enlighten/ui/BasicWindow.py for an example how to implement this using
    # Enlighten's style. This should always be callable as a single function call without
    # the caller needing to create her own class instance

    # let's persist these in the logfile too
    log.debug(f"msgbox: {title}: {prompt}")

    mb = QMessageBox(parent=ctl.form) if ctl else QMessageBox()
    mb.setWindowTitle(title)
    mb.setText(prompt)

    mask = 0
    buttons = buttons.lower()
    if "ok"     in buttons: mask |= QMessageBox.Ok
    if "no"     in buttons: mask |= QMessageBox.No
    if "yes"    in buttons: mask |= QMessageBox.Yes
    if "cancel" in buttons: mask |= QMessageBox.Cancel
    if mask == 0:
        mask = QMessageBox.Ok

    mb.setStandardButtons(mask)
    mb.setIcon(QMessageBox.Warning)

    if detail:
        mb.setDetailedText(detail)
    if informative_text:
        mb.setInformativeText(informative_text)

    retval = None
    result = mb.exec_()
    if result == QMessageBox.Ok:     retval = "Ok"
    if result == QMessageBox.No:     retval = "No"
    if result == QMessageBox.Yes:    retval = "Yes"
    if result == QMessageBox.Cancel: retval = "Cancel"

    log.debug(f"msgbox: retval {retval}, result {result}")
    return retval 

def is_rpi():
    result = False
    try:
        # Win32 doesn't have os.uname :-(
        (sysname, nodename, release, version, machine) = os.uname() # pylint: disable=unused-variable
        result = nodename == "raspberrypi"
    except:
        pass
    return result

def use_pyside2():
    result = is_rpi() or "USE_PYSIDE_2" in os.environ
    return result
