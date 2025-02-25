import os
import re
import logging
import textwrap
import configparser

# I think we're importing these modules so we can access their static class 
# functions before Controller's constructor is yet complete.
from enlighten.data.ColorNames import ColorNames
from enlighten.measurement.SaveOptions import SaveOptions

from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

class Configuration:
    """
    This is a wrapper over ConfigParser.  It adds the following features:
    
    - generates a stub template if none found
    - preserves comments when saving .ini
    - auto-expands named Colors 
    - auto-converts Qt line styles to enum
    
    This class manages enlighten.ini, which should be found under
    EnlightenSpectra.
    
    A default template file will be created if none exists.
    
    Like most .ini files, sections are delineated in [brackets], 
    followed by lines of "name = value" pairs.  Blank lines and those
    starting with pound (#) are ignored.
    
    Most sections are global and affect all spectrometers.
    Individual spectrometer settings can be controlled by sections
    named with the given device's serialNumber ([WP-00001], etc).
    
    Note that in the name of user-friendliness and automation, some 
    English-language values are dynamically translated from strings
    to corresponding Qt objects (colors, pen styles etc) in get().
    
    @todo allow Business Objects to define their own ConfigurationDefaults.
    
    @todo support registration, similar to EEPROMEditor, of tuples like the following:
    
    (widget, type, ini_label)
    e.g., config.register(checkbox_batch_enabled, bool, "batch.enabled")
    
    Such that:
    
    - register() will apply NON-DEFAULT config values to the widget
    - set() will update both the widget and config section
    - get() will return the current widget value

    @par Design Considerations
    
    "enlighten.ini" pre-dated me, and needed to be supported.  Doing this
    from scratch, I'd go with JSON, which supports much more complex 
    structured data.  For now, the compromise will be that "complex" objects
    requiring JSON configuration can use their own configuration files,
    pointed to by this one.

    @par Stale code notice

    We are using what current configparser docs call the "legacy API" -- my
    recollection is that it was the only API when this class was written 
    under Python 2.7. At some point we may want to update to the newer dict-
    style interface.
    """

    def clear(self):
        self.lines = []
        self.config = None
        self.defaults = None
        self.multispec = None
        self.linenum = 0

    def __init__(self, ctl):
        self.clear()

        self.ctl = ctl

        cfu = ctl.form.ui
        self.lb_save_result = cfu.label_save_ini_result

        # not using Colors.color_names because not yet constructed
        self.color_names = ColorNames()

        self.directory = common.get_default_data_dir()
        self.pathname  = os.path.join(self.directory, "enlighten.ini")
        self.test_dir = os.path.join(self.directory, 'testSpectrometers') # MZ: this doesn't belong in Configuration

        self.load_defaults()
        self.stub_missing()
        self.stub_test() # MZ: I don't think this belongs in Configuration

        self.lb_save_result.setText("calibration will be saved to %s" % self.pathname)

        try:
            self.reload()
        except:
            log.error("encountered exception during Configuration.reload", exc_info=1)

        cfu.pushButton_save_ini.clicked.connect(self.save_callback)

    def reload(self):
        """
        We read the .ini twice:
        - once as an array of lines (we use this when re-saving the file later)
        - again as a parsed configuration tree
        """
        self.load_text()
        self.parse()
        self.dump()

    # ##########################################################################
    # Initialization
    # ##########################################################################

    def stub_dir(self):
        """ create EnlightenSpectra directory if not found. """
        if os.path.exists(self.directory):
            return

        try:
            log.info("creating configuration directory: %s", self.directory)
            os.makedirs(self.directory)
        except Exception:
            log.critical("failed to create config directory", exc_info=1)

    def stub_test(self):
        """ Create test spectra dir if not found. """
        if os.path.exists(self.test_dir):
            return

        try:
            log.info(f"creating test directory: {self.test_dir}")
            os.makedirs(self.test_dir)
        except Exception:
            log.critical("failed to create test directory", exc_info=1)

    def stub_missing(self):
        """ If no enlighten.ini file exists, make one. """
        if os.path.exists(self.pathname):
            return

        self.stub_dir()
        try:
            with open(self.pathname, "w", newline="", encoding="utf-8") as outfile:
                header = """
                    # ENLIGHTEN configuration file
                    # 
                    # This file is created automatically if not found when ENLIGHTEN is run. You
                    # can edit it to change ENLIGHTEN run-time options.  It is automatically saved
                    # when ENLIGHTEN shuts down.
                    #
                    # Valid pen colors include names from http://htmlcolorcodes.com/color-names/, or
                    # match the regex '^#[0-9a-f]{6}$'. Valid pen styles include solid, dash, dot,
                    # dashdot and dashdotdot.
                """
                outfile.write(textwrap.dedent(header))

                # defaults
                for section in sorted(self.defaults):
                    outfile.write("\n[%s]\n" % section)
                    for key in sorted(self.defaults[section]):
                        outfile.write("# %s = %s\n" % (key, self.get(section, key, raw=True)))

                log.info("created stub %s", self.pathname)
        except:
            log.critical(f"failed to stub {self.pathname}")

    def load_text(self):
        """ Slurp file as array of lines. """
        if not os.path.exists(self.pathname):
            log.debug("not found: %s", self.pathname)
            return

        with open(self.pathname, encoding="utf-8") as infile:
            self.lines = infile.readlines()
        self.lines = [x.strip() for x in self.lines] 

    def parse(self):
        """ Load as ConfigParser object. """

        # strict=False allows allows duplicate keys to be loaded
        self.config = configparser.ConfigParser(interpolation=None, strict=False)
        self.config.optionxform = str
        try:
            self.config.read(self.pathname)
            log.info("loaded %s", self.pathname)
            return
        except:
            log.error(f"Failed to parse {self.pathname}", exc_info=1)

        # re-generate blank ConfigParser object, which we can use when saving
        self.config = configparser.ConfigParser()
        self.config.optionxform = str

    def dump(self):
        log.debug("Configuration:")
        for section in self.config.sections():
            log.debug("  [%s]", section)
            for key in self.config.options(section):
                log.debug("  %s = %s", key, self.config.get(section, key, raw=True))
            log.debug("")

    # ##########################################################################
    # Saving options
    # ##########################################################################

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        # log.debug("Configuration.set: (%s, %s, %s)", section, key, value)

    def save(self):
        try:
            with open(self.pathname, "w", encoding="utf-8") as outfile:
                for section in sorted(self.config.sections()):
                    if len(section) > 0 and ']' not in section:
                        outfile.write(f"[{section}]\n")
                        for key in sorted(self.config.options(section)):
                            value = self.config.get(section, key, raw=True)
                            outfile.write(f"{key} = {value}\n")
                        outfile.write("\n")
            log.info("saved %s", self.pathname)
        except:
            log.critical(f"failed to save {self.pathname}")

    # ##########################################################################
    # Reading options
    # ##########################################################################
    
    def get(self, section, key, raw=False, default="0"):
        """
        @param raw    return the literal value exactly as found in the file
                      (otherwise, perform interpretive post-processing of color
                       names and pen styles)
        @param section which INI section the key should be found in
        @param key     which setting we're looking for
        @param default value to return if not found
        @returns something, always (defaults to string "0")
        """
        if self.config and self.config.has_section(section) and self.config.has_option(section, key):
            value = self.config.get(section, key, raw=True)   # self.config != self :-)
        elif section in self.defaults and key in self.defaults[section]:
            value = str(self.defaults[section][key])
        else:
            log.error("Configuration.get: unknown option (%s, %s)", section, key)
            value = default # safer than None

        if not raw and value is not None:
            if key.endswith("_pen_color"):
                value = self.process_color(value)
            elif key.endswith("_pen_style"):
                value = self.process_pen_style(value)

        return value

    def get_sections(self):
        keys = []
        for k, _ in self.config.items():
            keys.append(k)
        return keys

    def get_options(self, section):
        if not (self.config and self.config.has_section(section)):
            return

        keys = []
        for k, _ in self.config[section].items():
            keys.append(k)
        return keys

    def get_bool(self, section, key, default=False):
        """ Not using ConfigParser.getboolean() because we want to support defaults. """
        if self.has_option(section, key):
            s = self.get(section, key)
            return s.lower() in ["true", "yes", "on", "1"]
        else:
            return default

    def get_int(self, section, key, default=0):
        value = default
        if self.has_option(section, key):
            s = self.get(section, key)
            try:
                value = int(round(float(s)))
            except ValueError:
                log.error(f"invalid int for {section}.{key} ({s})")
        return value

    def get_float(self, section, key, default=0.0):
        value = default
        if self.has_option(section, key):
            try:
                s = self.get(section, key)
                value = float(s)
            except ValueError:
                log.error(f"invalid float for {section}.{key} ({s})")
        return value

    def has_section(self, section):
        if self.config and self.config.has_section(section):
            return True
        else:
            return section in self.defaults

    def remove_section(self, section):
        if not self.config:
            return
        log.debug(f"removing Configuration section {section}")
        self.config.remove_section(section)

    def has_option(self, section, option):
        # any option which is defaulted will always indicate "has_option -> true";
        # .ini file may override value, but can't change that there IS a value
        if section in self.defaults and option in self.defaults[section]:
            return True

        # non-default options may or may not be defined
        if self.config and self.config.has_section(section):
            return self.config.has_option(section, option)

        return False            

    def process_color(self, value):
        if re.match(r'^#[0-9A-F]{6}', value.upper()):
            return value
        elif self.color_names.has(value):
            return self.color_names.get(value)
        else:
            return self.color_names.get("white")
        
    def process_pen_style(self, value):
        value = value.lower()
        if "dashdotdot" in value:
            return QtCore.Qt.DashDotDotLine
        elif "dashdot" in value:
            return QtCore.Qt.DashDotLine     
        elif "dash" in value:
            return QtCore.Qt.DashLine
        elif "dot" in value:
            return QtCore.Qt.DotLine
        return QtCore.Qt.SolidLine

    def load_defaults(self):
        self.defaults = {}

        self.defaults["save"] = SaveOptions.get_default_configuration()

        self.defaults["batch"] = {
            "enabled": False,
            "laser_mode": "manual",
            "count": 0,
            "batch_period_sec": 0,
            "spectrum_period_ms": 0,
            "laser_warmup_ms": 0,
            "start_on_connect": False,
            "wipe_thumbnails": False,
        }

        self.defaults["sound"] = {
            "enabled" : False,
        }

        self.defaults["advanced_options"] = {
            "never_show": False
        }

        self.defaults["interpolation"] = {}

        # Note that all of these affect the GLOBAL graph settings, not individual
        # spectrometers.  Also, all of these strictly relate to cosmetic 
        # appearance; no functionality is impacted here.
        self.defaults["graphs"] = {
                # area scan
                "area_scan_live_pen_color": "enlighten_default",
                "area_scan_live_pen_width": 1,
                "area_scan_live_pen_style": "solid",

                # scope views
                "scope_pen_color": "enlighten_default",
                "scope_pen_width": 1,
                "scope_pen_style": "solid",

                "raman_pen_color": "enlighten_default",
                "raman_pen_width": 1,
                "raman_pen_style": "solid",

                "transmission_pen_color": "enlighten_default",
                "transmission_pen_width": 1,
                "transmission_pen_style": "solid",

                "absorbance_pen_color": "enlighten_default",
                "absorbance_pen_width": 1,
                "absorbance_pen_style": "solid",

                "relative_irradiance_pen_color": "enlighten_default",
                "relative_irradiance_pen_width": 1,
                "relative_irradiance_pen_style": "solid",

                # scope setup
                "live_pen_color": "blue",
                "live_pen_width": 1,
                "live_pen_style": "solid",

                "dark_pen_color": "gray",
                "dark_pen_width": 1,
                "dark_pen_style": "solid",

                "reference_pen_color": "gray",
                "reference_pen_width": 1,
                "reference_pen_style": "solid",

                # saved spectra
                "thumbnail_pen_color": "enlighten_default",
                "thumbnail_pen_width": 1,
                "thumbnail_pen_style": "solid",

                # temperatures
                "detector_temperature_pen_color": "enlighten_blue",
                "detector_temperature_pen_width": 1,
                "detector_temperature_pen_style": "solid",

                "laser_temperature_pen_color": "enlighten_red",
                "laser_temperature_pen_width": 1,
                "laser_temperature_pen_style": "solid",
                
                # peakfinding
                "peaks_pen_color": "yellow",
                "peaks_pen_width": 1,
                "peaks_pen_style": "solid",

                "emission_pen_color": "darkblue",
                "emission_pen_width": 5,
                "emission_pen_style": "solid",

                # irradiance
                "blackbody_pen_color": "dimgray",
                "blackbody_pen_width": 2,
                "blackbody_pen_style": "solid",

                # field wavecal
                "raman_shift_correction_pen_color": "yellow",
                "raman_shift_correction_pen_width": 1,
                "raman_shift_correction_pen_style": "solid",

                # cursors
                "scope_cursor_pen_color": "red",
                "scope_cursor_pen_width": 1,
                "scope_cursor_pen_style": "solid",

                "emission_cursor_pen_color": "aqua",
                "emission_cursor_pen_width": 1,
                "emission_cursor_pen_style": "dash",

                "baseline_cursor_pen_color": "blue",
                "baseline_cursor_pen_width": 1,
                "baseline_cursor_pen_style": "solid",
            }

    def save_file(self, full=False):
        # grab key attributes from all connected spectrometers
        if self.multispec is not None:
            for spec in self.multispec.get_spectrometers():
                if spec.device:
                    eeprom = spec.settings.eeprom
                    state = spec.settings.state
                    sn = spec.settings.eeprom.serial_number
                    if sn is None or len(sn) == 0:
                        log.error("declining to save settings for unit without serial number")
                        continue

                    log.info("saving config for %s", sn)

                    # only save EEPROM overrides if explicitly instructed
                    if full:
                        if spec.settings.eeprom.degC_to_dac_coeffs:
                            self.set(sn, "degC_to_dac_coeff_0",        eeprom.degC_to_dac_coeffs[0])
                            self.set(sn, "degC_to_dac_coeff_1",        eeprom.degC_to_dac_coeffs[1])
                            self.set(sn, "degC_to_dac_coeff_2",        eeprom.degC_to_dac_coeffs[2])
                        self.set(sn, "detector_tec_setpoint_degC",     state.tec_setpoint_degC)
                        self.set(sn, "detector_tec_max_degC",          eeprom.max_temp_degC)
                        self.set(sn, "detector_tec_min_degC",          eeprom.min_temp_degC)
                        self.set(sn, "excitation_nm",                  eeprom.excitation_nm_float)
                        self.set(sn, "slit_size_um",                   eeprom.slit_size_um)
                        if spec.settings.eeprom.wavelength_coeffs:
                            self.set(sn, "wavelength_coeff_0",         eeprom.wavelength_coeffs[0])
                            self.set(sn, "wavelength_coeff_1",         eeprom.wavelength_coeffs[1])
                            self.set(sn, "wavelength_coeff_2",         eeprom.wavelength_coeffs[2])
                            self.set(sn, "wavelength_coeff_3",         eeprom.wavelength_coeffs[3])
                            if len(spec.settings.eeprom.wavelength_coeffs) > 4:
                                self.set(sn, "wavelength_coeff_4",     eeprom.wavelength_coeffs[4])
                        if spec.settings.eeprom.adc_to_degC_coeffs:
                            self.set(sn, "adc_to_degC_coeff_0",        eeprom.adc_to_degC_coeffs[0])
                            self.set(sn, "adc_to_degC_coeff_1",        eeprom.adc_to_degC_coeffs[1])
                            self.set(sn, "adc_to_degC_coeff_2",        eeprom.adc_to_degC_coeffs[2])
                        self.set(sn, "ccd_gain",                       eeprom.detector_gain)
                        self.set(sn, "ccd_offset",                     eeprom.detector_offset)
                        self.set(sn, "ccd_gain_odd",                   eeprom.detector_gain_odd)
                        self.set(sn, "ccd_offset_odd",                 eeprom.detector_offset_odd)

        self.save()

    def save_callback(self):
        self.save_file(full=True)
        self.reload()
        self.lb_save_result.setText("calibration saved to %s" % self.pathname)
