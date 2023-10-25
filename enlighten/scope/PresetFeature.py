import logging

from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox

from enlighten.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class PresetFeature:
    """
    This feature allows the user to save named presets (referring to a snapshot 
    of key acquisition parameters), irrespective of spectrometer serial number.

    The proposed design is to let any Feature (or Plugin) register itself to 
    PresetFeature and add one or more attributes.

    Calling API would be something like:

        class IntegrationTimeFeature:
            def __init__:
                ctl.presets.register(self, ["integration_time_ms"])

            def get_preset_value(self, attr):
                if attr == "integration_time_ms":
                    return self.current_ms

            def set_preset_value(self, attr, value):
                if attr == "integration_time_ms":
                    self.set_ms(int(value))

    Note that all values will be written and read as strings; it will be 
    on the receiving set_preset_value to cast any persisted values back to the
    expected type.
    """

    SECTION = "Presets"
    
    def __init__(self, ctl):
        self.ctl = ctl

        self.combo = ctl.form.ui.comboBox_presets
        self.selected_preset = None

        self.presets = {} # { "Winchester bottles": { "IntegrationTimeFeature": { "integration_time_ms": "2000" } } }
        self.observers = {} # { <IntegrationTimeFeature>: [ "integration_time_ms"' ] }


        self.load_from_ini():

        self.combo.currentIndexChanged.connect(self.combo_callback)
        self.combo.installEventFilter(ScrollStealFilter(self.combo))

    def load_from_ini(self):
        config = self.ctl.config
        if not config.has_option(self.SECTION, "presets"):
            return

        # parse Winchester.IntegrationTimeFeature.integration_time_ms keys into dict tree
        keys = config.get_keys(self.SECTION)
        for k in keys:
            tok = k.split(".")
            if len(tok) != 3:
                log.error(f"unable to parse preset: {k}")
                continue
            preset, feature, attr = tok
            self.store(preset, feature, attr, config.get(self.SECTION, k))

    def store(self, preset, feature, attr, value):
        if preset not in self.presets:
            self.presets[preset] = {}
        if feature not in self.presets[preset]:
            self.presets[preset][feature] = {}
        self.presets[preset][feature][attr] = value
        log.debug(f"stored {preset}.{feature}.{attr} = {value}")

    def register(self, feature, attrs):
        feature_name = feature.__class__.__name__
        log.debug(f"registered {feature_name}: {attrs}")
        self.observers[feature] = attrs

    def unregister(self, feature):
        feature_name = feature.__class__.__name__
        if feature in self.observers:
            del self.observers[feature]
        log.debug(f"unregistered {feature_name}")

    def combo_callback(self):
        preset = str(self.combo.currentText())

        if preset.lower() == "create new...":
            self.create_new()
        elif preset.lower() == "remove":
            self.remove(self.selected_preset)
        else:
            self.apply(preset)
    
    def create_new(self):
        # prompt the user for a name
        (preset, ok) = QtWidgets.QInputDialog().getText(
            self.ctl.form,          # parent
            "Create New Preset",    # title
            "New Preset Name:",     # label
            QtWidgets.QLineEdit.Normal, 
            "")
        if not (ok and preset):
            log.info("cancelling preset creation")
            return 

        # only allow certain characters (no period)
        preset = re.sub(r'[^a-z0-9()\[\]\' _-]', '_', preset, re.IGNORECASE)

        log.debug("creating preset {preset}")
        config = self.ctl.config
        for obs in self.observers:
            feature = obs.__class__.__name__
            for attr in self.observers[obs]:
                try:
                    value = obs.get_preset_value(attr)
                except:
                    log.error("unable to read {attr} from {feature}", exc_info=1)
                    continue

                # persist to Configuration
                key = f"{preset}.{feature}.{attr}"
                config.set(self.SECTION, key, value)

                # store locally
                self.store(preset, feature, attr, value)

        self.reset(preset)

    def reset(self, selected=None):
        # clear previous Configuration
        self.config.remove_section(self.SECTION)

        # re-populate comboBox
        self.combo.clear()
        self.combo.addItem("Create new...")
        selectedIndex = 0
        for preset in sorted(self.presets):
            self.combo.addItem(preset)
            if preset == selected:
                selectedIndex = idx + 1
        self.combo.addItem("(Remove)")

        if selectedIndex > 0:
            self.combo.setCurrentIndex(selectedIndex)
            self.selected_preset = selected

    def apply(self):
        preset = str(self.combo.currentText())
        if preset not in self.presets:
            return

        # send any stored attribute values to registered observers
        for obs in self.observers:
            feature = obs.__class__.__name__
            if feature in self.presets[preset]:
                for attr in self.observers[obs]:
                    if attr in self.presets[preset][feature]:
                        value = self.presets[preset][feature][attr]
                        try:
                            obs.set_preset_value(attr, value)
                        except:
                            log.error("failed to apply preset {preset} to feature {feature} with {attr} = {value}", exc_info=1)
        self.reset(preset)

    def remove(self, preset):
        if preset not in self.presets:
            log.error(f"remove: {preset} not in presets")
            return

        dlg = QMessageBox(self.ctl.form)
        dlg.setWindowTitle("Remove Preset")
        dlg.setText(f"Permanently delete preset {preset}?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        result = dlg.exec_()
        if result == QMessageBox.No:
            return
        
        del self.presets[preset]
        self.selected_preset = None
        self.reset()
