import logging
import os

from enum import IntEnum

log = logging.getLogger(__name__)

# needed to allow plugins to access tensorflow
try:
    import tensorflow
except:
    log.warning(f"tensorflow not found. skipping. some plugins may not work")

"""
Namespace containing various enums and constants used elsewhere within the 
application.

@todo consider making "common" a package (directory), and each of these classes
      can be modules (files) within it
"""
VERSION = "3.2.32"

""" ENLIGHTEN's application version number (checked by scripts/deploy and bootstrap.bat) """

class Techniques(IntEnum):
    HARDWARE            = 0
    SCOPE               = 1
    RAMAN               = 2 
    TRANSMISSION        = 3
    ABSORBANCE          = 4
"""
It's important to keep this list in sync with the comboBoxTechnique items.
@todo consider auto-populating inside code
"""

class TechniquesHelper:
    pretty_names = {
        Techniques.HARDWARE:     "Hardware",
        Techniques.SCOPE:        "Scope",
        Techniques.RAMAN:        "Raman",
        Techniques.TRANSMISSION: "Transmission",
        Techniques.ABSORBANCE:   "Absorbance"
    }

    def get_pretty_name(n):
        return TechniquesHelper.pretty_names.get(n, "UNKNOWN")

    def parse(s):
        s = s.upper()
        if "HARDWARE"             in s: return Techniques.HARDWARE
        if "SCOPE"                in s: return Techniques.SCOPE
        if "RAMAN"                in s: return Techniques.RAMAN
        if "ABS"                  in s: return Techniques.ABSORBANCE
        if "TRANS" in s or "REFL" in s: return Techniques.TRANSMISSION
        log.error("Invalid technique: %s", s)
        return Techniques.SCOPE

class OperationModes(IntEnum):
    SETUP   = 0
    CAPTURE = 1

class OperationModesHelper:
    def parse(s):
        s = s.upper()
        if "SETUP"   in s: return OperationModes.SETUP
        if "CAPTURE" in s: return OperationModes.CAPTURE
        log.error("Invalid operation mode: %s", s)
        return OperationModes.SETUP

class Pages(IntEnum):
    HARDWARE_SETUP   = 0
    HARDWARE_CAPTURE = 1
    SCOPE_SETUP      = 2
    SCOPE_CAPTURE    = 3

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

def get_default_data_dir():
    if os.name == "nt":
        return os.path.join(os.path.expanduser("~"), "Documents", "EnlightenSpectra")
    return os.path.join(os.environ["HOME"], "EnlightenSpectra")
