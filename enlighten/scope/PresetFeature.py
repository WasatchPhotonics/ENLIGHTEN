import logging

from PySide6 import QtWidgets

from enlighten.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class PresetFeature:
    """
    This feature allows the user to save named presets (referring to a snapshot 
    of key acquisition parameters), irrespective of spectrometer serial number.

    @par Plugins

    At this time, I have not considered how / whether plugins might tie into this
    service (such that if a given plugin is connected, and that plugin contains 
    internal state which it wishes to be included in presets, then 
    PluginController and PresetFeature will communicate to make that silently 
    transpire), but I am confident this will prove no great hurdle if requested.

    @par Alternate Design

    I am considering an alternate design where any Feature can register itself to
    PresetFeature and add one or more attributes to an ever-growing list. 
    Something like:

        IntegrationTimeFeature
            def __init__:
                ctl.presets.register(self, ["integration_time_ms"])
            def preset_get(self):
                return { "integration_time_ms": self.ms }
            def preset_set(self, values):
                self.apply(values["integration_time_ms"])

    This would make it trivial to support plugins, so long as the get/set 
    methods were called within try/except blocks in the event that a plugin
    had disconnected / unloaded without unregistering itself.

    Saving current state in a snapshot commit if I regret this :-)
    """

    SECTION = "Presets"
    
    def __init__(self, ctl):
        self.ctl = ctl

        self.combo = ctl.form.ui.comboBox_presets

        self.presets = {}

        self.load_from_ini():

        self.combo.currentIndexChanged.connect(self.combo_callback)
        self.combo.installEventFilter(ScrollStealFilter(self.combo))

    def load_from_ini(self):
        config = self.ctl.config
        if not config.has_option(self.SECTION, "presets"):
            return
            
        names = [s.strip() in config.get_string(self.SECTION, "presets").split("|")]
        for s in names:
            self.presets[s] = Preset(self.ctl, f"Preset.{s}")
            log.debug("loaded {s} -> {self.presets[s]}")

    def combo_callback(self):
        name = str(self.combo.currentText())

        if value.lower() == "create new...":
            self.create_new()
        elif value.lower() == "remove":
            self.remove()
        else:
            self.apply(value)
    
    def create_new(self):
        # prompt the user for a name
        (name, ok) = QtWidgets.QInputDialog().getText(
            self.ctl.form,          # parent
            "Create New Preset",    # title
            "New Preset Name:",     # label
            QtWidgets.QLineEdit.Normal, 
            "")
        if not (ok and name):
            log.info("cancelling preset creation")
            return 
        
        log.debug("creating preset {name}")

        preset = Preset(self.ctl)
        preset.save(f"Preset.{name}")

        self.presets[name] = preset

        self.reset()

    def reset(self):
        names = sorted(self.presets.keys())
        self.ctl.config.set(self.SECTION, "presets", "|".join(names))

        self.combo.clear()
        self.combo.addItem("Create new...")
        selectedIndex = 0
        for idx, s in enumerate(names):
            self.combo.addItem(s)
            if s == name:
                selectedIndex = idx + 1
        self.combo.addItem("(Remove)")

        if selectedIndex > 0:
            self.combo.setCurrentIndex(selectedIndex)

    def apply(self):
        name = str(self.combo.currentText())
        if name not in self.presets:
            log.error(f"apply: impossible? {name} not in presets")
            return
        self.presets[name].apply()

        self.reset()

    def remove(self):
        name = str(self.combo.currentText())
        if name not in self.presets:
            log.error(f"remove: impossible? {name} not in presets")
            return
        
        del self.presets[name]
        self.reset()

class Preset:
    def __init__(self, ctl, section=None):
        self.ctl = ctl
        self.section = section

        self.integration_time_ms = None
        self.gain_db = None
        self.scans_to_average = None
        self.boxcar_half_width = None
        self.baseline_correction_algo = None
        self.raman_intensity_correction = None

        if section:
            self.init_from_config()
        else:
            self.init_from_live()

    def __repr__(self):
        return f"Preset<section {self.section}, " +
               f"integ {self.integration_time_ms}, " +
               f"gain {self.gain_db}, " +
               f"scans {self.scans_to_average}, " +
               f"boxcar {self.boxcar_half_width}, " +
               f"algo {self.baseline_correction_algo}, " +
               f"SRM {self.raman_intensity_correction}>"

    def init_from_config(self):
        config = self.ctl.config
        if config.has_option(self.section, "integration_time_ms"):
            self.integration_time_ms = config.get_int(section, "integration_time_ms")
        if config.has_option(self.section, "gain_db"):
            self.gain_db = config.get_float(section, "gain_db")
        if config.has_option(self.section, "scans_to_average"):
            self.scans_to_average = config.get_int(section, "scans_to_average")
        if config.has_option(self.section, "boxcar_half_width"):
            self.boxcar_half_width = config.get_int(section, "boxcar_half_width")
        if config.has_option(self.section, "raman_intensity_correction"):
            self.raman_intensity_correction = config.get_bool(section, "raman_intensity_correction")

    def init_from_live(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        self.integration_time_ms = spec.settings.state.integration_time_ms
        self.gain_db = spec.settings.state.gain_db
        self.scans_to_average = spec.settings.state.scans_to_average
        self.boxcar_half_width = spec.settings.state.boxcar_half_width
        self.raman_intensity_correction = self.ctl.raman_intensity_correction.enable_when_allowed
        if ctl.baseline_correction.enabled:
            self.baseline_correction_algo = self.ctl.baseline_correction.current_algo_name

    def save(self, section=None):
        if section is None:
            section = self.section
        if section is None:
            log.error("unable to save preset w/o name")
            return

        config = self.ctl.config
        config.set(section, "integration_time_ms", self.integration_time_ms)
        config.set(section, "gain_db", self.gain_db)
        config.set(section, "scans_to_average", self.scans_to_average)
        config.set(section, "boxcar_half_width", self.boxcar_half_width)
        config.set(section, "baseline_correction_algo", self.baseline_correction_algo)
        config.set(section, "raman_intensity_correction", self.raman_intensity_correction)

    def apply(self):
        pass

        # YOU ARE HERE

