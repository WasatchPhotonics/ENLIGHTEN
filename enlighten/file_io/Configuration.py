from PySide2 import QtCore

import os
import re
import shutil
import logging
import textwrap
import threading
import configparser

from enlighten.data.ColorNames import ColorNames
from enlighten.measurement.SaveOptions import SaveOptions

from enlighten import common

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
    """

    def clear(self):
        self.lines = []
        self.config = None
        self.defaults = None
        self.multispec = None
        self.linenum = 0

    def __init__(self,
            button_save,
            lb_save_result):
        self.clear()

        self.button_save    = button_save
        self.lb_save_result = lb_save_result

        self.lock = threading.Lock()
        self.color_names = ColorNames()

        self.directory = common.get_default_data_dir()
        self.pathname  = os.path.join(self.directory, "enlighten.ini")
        self.test_dir = os.path.join(self.directory,'testSpectrometers')

        self.load_defaults()
        self.stub_missing()
        self.stub_test() # MZ: I don't think this belongs in Configuration

        self.lb_save_result.setText("calibration will be saved to %s" % self.pathname)

        try:
            self.reload()
        except:
            log.error("encountered exception during Configuration.reload", exc_info=1)

        self.button_save.clicked.connect(self.save_callback)

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
        except Exception as exc:
            log.critical("failed to create config directory", exc_info=1)

    def stub_test(self):
        """ Create test spectra dir if not found. """
        if os.path.exists(self.test_dir):
            return

        try:
            log.info(f"creating test directory: {self.test_dir}")
            os.makedirs(self.test_dir)
        except Exception as exc:
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
                log.debug("  %s = %s", key, self.config.get(section, key))
            log.debug("")

    # ##########################################################################
    # Saving options
    # ##########################################################################

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        log.debug("Configuration.set: (%s, %s, %s)", section, key, value)

    def write(self, f, s):
        log.debug(s)
        f.write(s + "\n")
            
    def save(self):
        try:
            with self.lock:
                section = None
                seen = {}

                with open(self.pathname, "w", newline="", encoding="utf-8") as outfile:

                    def dump_keys():
                        if section is not None and section in seen and self.config.has_section(section):
                            for key in sorted(self.config.options(section)):
                                if key not in seen[section]:
                                    value = self.get(section, key, raw=True)
                                    self.write(outfile, "%s = %s" % (key, value))
                                    seen[section].add(key)
                
                    # first re-create the originally loaded file, updating any non-
                    # commented options and filling-out old sections
                    log.debug("saving old lines")
                    for line in self.lines:

                        # ignore blanks
                        if len(line.strip()) == 0:
                            continue

                        # retain comments
                        if line.startswith("#"):
                            self.write(outfile, line)
                            continue

                        # was this a section header?
                        m = re.match(r'^\[(.+)\]$', line)
                        if m:
                            # dump any new keys from the PREVIOUS section
                            dump_keys()

                            # start next section
                            section = m.group(1)
                            seen[section] = set()
                            self.write(outfile, "")
                            self.write(outfile, "[%s]" % section)
                            continue

                        # was it a key-value line?
                        m = re.match(r"^([A-Za-z0-9_ ]+) *=", line)
                        if m and section is not None:
                            # it was a key-value line, so update the line with the current value
                            key = m.group(1).strip()

                            # ensure we don't output duplicate keys
                            if key not in seen[section]:
                                self.write(outfile, "%s = %s" % (key, self.get(section, key, raw=True)))
                                seen[section].add(key)
                            continue

                        log.error("unexpected line in source .ini file: %s", line)

                    # dump any new keys from the FINAL section
                    log.debug("dumping new keys from final section")
                    dump_keys()

                    # add any NEW sections
                    log.debug("adding new sections")
                    for section in sorted(self.config.sections()):
                        if section not in seen:
                            self.write(outfile, "\n[%s]" % section)
                            for key in sorted(self.config.options(section)):
                                self.write(outfile, "%s = %s" % (key, self.config.get(section, key, raw=True)))

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
            value = self.config.get(section, key)   # self.config != self :-)
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

    def get_bool(self, section, key, default=False):
        """ Not using ConfigParser.getboolean() because we want to support defaults. """
        if self.has_option(section, key):
            return self.get(section, key).lower() == "true"
        else:
            return default

    def get_int(self, section, key, default=0):
        value = default
        if self.has_option(section, key):
            try:
                value = int(self.get(section, key))
            except ValueError:
                log.error("invalid int for %s.%s got value of %s", section, key, self.get(section, key))
        return value

    def get_float(self, section, key, default=0.0):
        value = default
        if self.has_option(section, key):
            try:
                value = float(self.get(section, key))
            except ValueError:
                log.error("invalid float for %s.%s got value of %s", section, key, self.get(section, key))
        return value

    def has_section(self, section):
        if self.config and self.config.has_section(section):
            return True
        else:
            return section in self.defaults

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
                    settings = spec.settings
                    eeprom = settings.eeprom
                    state = settings.state
                    sn = eeprom.serial_number
                    if sn is None or len(sn) == 0:
                        log.error("declining to save settings for unit without serial number")
                        continue

                    log.info("saving config for %s", sn)

                    # these application-session settings can always be saved
                    self.set(sn, "integration_time_ms", state.integration_time_ms)
                    self.set(sn, "boxcar_half_width", state.boxcar_half_width)
                    self.set(sn, "gain_db", state.gain_db)

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
