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

VERSION = "4.0.12"

""" ENLIGHTEN's application version number (checked by scripts/deploy and bootstrap.bat) """
class Techniques(IntEnum):
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
    SCOPE               = 0
    SETTINGS            = 1
    HARDWARE            = 2
    LOG                 = 3
    FACTORY             = 4
"""
It's important to keep this list in sync with the comboBox_view items.
@todo consider auto-populating inside code
"""

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

def get_default_data_dir():
    if os.name == "nt":
        return os.path.join(os.path.expanduser("~"), "Documents", "EnlightenSpectra")
    return os.path.join(os.environ["HOME"], "EnlightenSpectra")
