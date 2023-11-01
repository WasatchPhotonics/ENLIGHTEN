from .. import util
import logging
import enlighten

log = logging.getLogger(__name__)

from enlighten.ScrollStealFilter import ScrollStealFilter
from enlighten.MouseWheelFilter import MouseWheelFilter
##
# This class encapsulates control of detector gain (decibels), currently used 
# only for Sony IMX detectors (SiG).  
#
# This is different from the gain and offset used for Hamamatsu detectors, 
# although the same EEPROM field (detector_gain) is used to persist both (note 
# that Hamamatsu gain is a float32, while decibels are currently integral, 
# although firmware and IMX sensors support 0.1dB precision).
#
# This is even *more* different from the "High-Gain Mode" feature found on InGaAs 
# detectors.
#
# Note that changing the detector gain through the Scope widget DOES NOT 
# affect the "Detector Gain" value shown in the Hardware Setup EEPROMEditor, 
# although they DO represent the same value.  The EEPROM value represents the
# setting that will be sent to the spectrometer/FPGA at initial connection;
# the Scope widget represents the current "session" value, but this is not 
# persisted through EEPROM anymore than is, say, momentary integration time
# used to update startupIntegrationTimeMS.
#
# Note that although the SiG can actually handle gain in increments of 0.1dB,
# and our FunkyFloat type can support increments of 1/256 dB, the widget is
# currently implemented as an integral QSpinBox (not QDoubleSpinBox), so
# UI precision is currently 1dB.
#
# @todo support gain resolution of 0.1 dB
# @see additional notes in wasatch.SpectrometerState
class GainDBFeature:

    # per https://www.misptc.com/wp-content/uploads/2018/04/2018041306101956.pdf
    MIN_GAIN_DB = 0
    MAX_GAIN_DB = 72

    def __init__(self, ctl):
        self.ctl = ctl  # type: enlighten.Controller.Controller

        self.widgets = [
            self.ctl.form.ui.pushButton_gain_dn,
            self.ctl.form.ui.pushButton_gain_up,
            self.ctl.form.ui.label_gainWidget_title,
            self.ctl.form.ui.slider_gain,
            self.ctl.form.ui.doubleSpinBox_gain
        ]
        self.visible = False
        self.locked = False

        # bindings
        self.ctl.form.ui.slider_gain.valueChanged.connect(self.sync_slider_to_spinbox_callback)
        self.ctl.form.ui.slider_gain.installEventFilter(MouseWheelFilter(self.ctl.form.ui.slider_gain))
        self.ctl.form.ui.doubleSpinBox_gain.valueChanged.connect(self.sync_spinbox_to_slider_callback)
        self.ctl.form.ui.doubleSpinBox_gain.installEventFilter(ScrollStealFilter(self.ctl.form.ui.doubleSpinBox_gain))
        self.ctl.form.ui.pushButton_gain_up.clicked.connect(self.up_callback)
        self.ctl.form.ui.pushButton_gain_dn.clicked.connect(self.dn_callback)

        self.ctl.presets.register(self, "gain_db", getter=self.get_db, setter=self.set_db_callback)

        self.update_visibility()

    def set_locked(self, flag):
        self.locked = flag
        self.update_visibility()

    ##
    # Only show these controls when an IMX-based spectrometer is selected
    def update_visibility(self):

        if self.locked:
            self.visible = False
        else:
            spec = self.ctl.multispec.current_spectrometer()
            if spec is None:
                self.visible = False
            else:
                self.visible = spec.settings.is_micro()

        # normally we'd do this at the enclosing frame, but gain is currently 
        # nested within the detectorControlWidget, and a sub-frame breaks the
        # CSS, so...just disappear the widgets for now
        for w in self.widgets:
            w.setVisible(self.visible)

        return self.visible

    # called by initialize_new_device on hotplug, BEFORE reading / applying .ini
    def init_hotplug(self):
        if not self.update_visibility():
            log.debug("GainDBFeature.init_hotplug: no visibility")
            return

        # on hotplug, initialize GainDB widget from EEPROM value
        spec = self.ctl.multispec.current_spectrometer()
        spec.settings.state.gain_db = spec.settings.eeprom.detector_gain

    # called by initialize_new_device a little after the other function
    def reset(self, hotplug=False):
        if not self.update_visibility():
            return

        spec = self.ctl.multispec.current_spectrometer()

        # load gain_db from .ini, falling back to spec.settings.state (copied from EEPROM)
        if spec:
            serial_number = spec.settings.eeprom.serial_number

            if self.ctl.config.has_option(serial_number, "gain_db"):
                ini_gain_db = self.ctl.config.get_float(serial_number, "gain_db")
                log.debug("Get gain from INI: %s", ini_gain_db)
                self.set_db(ini_gain_db)
            elif spec.settings.state.gain_db != None:
                log.debug("Get gain from SpectrometerSettings: %s", spec.settings.state.gain_db)
                self.set_db(spec.settings.state.gain_db)
            elif spec.settings.eeprom.detector_gain != None:
                gain_eeprom = spec.settings.eeprom.detector_gain
                log.debug("Get gain from EEPROM: %s", gain_eeprom)
                self.set_db(gain_eeprom)
            else:
                gain_default = 8
                log.debug("Get gain from hardcoded default: %s", gain_default)
                self.set_db(gain_default)

            # apply limits to SPINBOX
            self.ctl.form.ui.doubleSpinBox_gain.blockSignals(True)
            self.ctl.form.ui.doubleSpinBox_gain.setMinimum(self.MIN_GAIN_DB)
            self.ctl.form.ui.doubleSpinBox_gain.setMaximum(self.MAX_GAIN_DB)
            self.ctl.form.ui.doubleSpinBox_gain.blockSignals(False)

            log.info("spinbox limits (%d, %d) (current %d)",
                self.ctl.form.ui.doubleSpinBox_gain.minimum(), self.ctl.form.ui.doubleSpinBox_gain.maximum(), self.ctl.form.ui.doubleSpinBox_gain.value())

    def _quiet_set(self, widget, value):
        """
        Set the value of a widget without invoking the ValueChanged event
        """
        widget.blockSignals(True)
        widget.setValue(value)
        widget.blockSignals(False)

    def set_focus(self):
        self.spinbox.setFocus()
        self.spinbox.selectAll()

    def set_db(self, db):
        db = float(db)
        
        # save gain_db to application state
        self.ctl.multispec.set_state("gain_db", db)

        # persist gain_db in .ini
        self.ctl.config.set(self.ctl.multispec.current_spectrometer().settings.eeprom.serial_number, "gain_db", db)

        # send gain update message to device
        self.ctl.multispec.change_device_setting("detector_gain", db)

        # ensure both gain widgets are correct, without generating additional events
        self._quiet_set(self.ctl.form.ui.doubleSpinBox_gain, db)
        self._quiet_set(self.ctl.form.ui.slider_gain, db)

    def up_callback(self):
        util.incr_spinbox(self.ctl.form.ui.doubleSpinBox_gain)
        self.set_db(self.ctl.form.ui.doubleSpinBox_gain.value())

    def dn_callback(self):
        util.decr_spinbox(self.ctl.form.ui.doubleSpinBox_gain)
        self.set_db(self.ctl.form.ui.doubleSpinBox_gain.value())

    def sync_slider_to_spinbox_callback(self):
        self.set_db(self.ctl.form.ui.slider_gain.value()) 

    def sync_spinbox_to_slider_callback(self):
        self.set_db(self.ctl.form.ui.doubleSpinBox_gain.value())

    def get_db(self):
        return self.ctl.form.ui.doubleSpinBox_gain.value()

    def set_db_callback(self, value):
        if self.visible:
            self.set_db(value)
