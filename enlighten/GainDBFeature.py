from . import util
import logging

log = logging.getLogger(__name__)

from .ScrollStealFilter import ScrollStealFilter
from .MouseWheelFilter import MouseWheelFilter
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
class GainDBFeature(object):

    # per https://www.misptc.com/wp-content/uploads/2018/04/2018041306101956.pdf
    MIN_GAIN_DB = 0
    MAX_GAIN_DB = 72

    def __init__(self,
            bt_dn,
            bt_up,
            label,
            multispec,
            slider,
            spinbox     # actually doubleSpinBox
        ):

        self.bt_dn      = bt_dn
        self.bt_up      = bt_up
        self.label      = label
        self.multispec  = multispec
        self.slider     = slider
        self.spinbox    = spinbox

        self.widgets    = [ bt_dn, bt_up, label, slider, spinbox ]
        self.visible    = False

        # bindings
        self.slider     .valueChanged       .connect(self.sync_slider_to_spinbox_callback)
        self.slider                         .installEventFilter(MouseWheelFilter(self.slider))
        self.spinbox    .valueChanged       .connect(self.sync_spinbox_to_slider_callback)
        self.spinbox                        .installEventFilter(ScrollStealFilter(self.spinbox))
        self.bt_up      .clicked            .connect(self.up_callback)
        self.bt_dn      .clicked            .connect(self.dn_callback)

        self.update_visibility()

    ##
    # Only show these controls when an IMX-based spectrometer is selected
    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
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
        spec = self.multispec.current_spectrometer()
        spec.settings.state.gain_db = spec.settings.eeprom.detector_gain

        self.spinbox.setValue(spec.settings.state.gain_db)
        log.debug("GainDBFeature.init_hotplug: initialized to %.2f", spec.settings.state.gain_db)

    # called by initialize_new_device a little after the other function
    def reset(self, hotplug=False):
        if not self.update_visibility():
            return

        # TEMPORARILY set a value within limits (this is the SLIDER)
        self.slider.blockSignals(True)
        self.slider.setMinimum(self.MIN_GAIN_DB)
        self.slider.setMaximum(self.MAX_GAIN_DB)
        self.slider.setValue  (self.MIN_GAIN_DB) 
        self.slider.blockSignals(False)

        log.debug("slider limits (%d, %d) (temporary value %d)",
            self.slider.minimum(), self.slider.maximum(), self.slider.value())

        spec = self.multispec.current_spectrometer()
        now_db = spec.settings.state.gain_db

        # apply limits to SPINBOX
        self.spinbox.blockSignals(True)
        self.spinbox.setMinimum(self.MIN_GAIN_DB)
        self.spinbox.setMaximum(self.MAX_GAIN_DB)
        self.spinbox.blockSignals(False)

        # apply the "real" value to spinbox.  This will clamp to supported limits, 
        # update slider to clamped and send clamped downstream
        self.spinbox.setValue(now_db)

        log.info("spinbox limits (%d, %d) (current %d)",
            self.spinbox.minimum(), self.spinbox.maximum(), self.spinbox.value())

    def set_db(self, db):
        self.spinbox.setValue(db)

    def up_callback(self):
        util.incr_spinbox(self.spinbox)

    def dn_callback(self):
        util.decr_spinbox(self.spinbox)

    def sync_slider_to_spinbox_callback(self):
        self.spinbox.setValue(self.slider.value()) 

    def sync_spinbox_to_slider_callback(self):
        db = self.spinbox.value()

        self.slider.blockSignals(True)
        self.slider.setValue(db)
        self.slider.blockSignals(False)

        self.multispec.set_state("gain_db", db)
        self.multispec.change_device_setting("detector_gain", db)
