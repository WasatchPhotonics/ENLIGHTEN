from .. import util
import logging

log = logging.getLogger(__name__)

from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.ui.MouseWheelFilter import MouseWheelFilter

class GainDBFeature:
    """
    This class encapsulates control of detector gain (decibels), currently used 
    only for Sony IMX detectors (SiG).  
    
    This is different from the gain and offset used for Hamamatsu detectors, 
    although the same EEPROM field (detector_gain) is used to persist both.
    
    This is even *more* different from the "High-Gain Mode" feature found on 
    InGaAs detectors.
    
    Note that changing the detector gain through the Scope widget DOES NOT 
    affect the "Detector Gain" value shown in the Hardware Setup EEPROMEditor, 
    although they DO represent the same value.  The EEPROM value represents the
    setting that will be sent to the spectrometer/FPGA at initial connection;
    the Scope widget represents the current "session" value, but this is not 
    persisted through EEPROM anymore than is, say, momentary integration time
    used to update startupIntegrationTimeMS.
    
    @see additional notes in wasatch.SpectrometerState

    @todo currently re-using this class for IDSPeak cameras, even though they
          seem to treat gain as a scalar rather than dB. Possibly we should
          continue to pass gain as dB all the way through the pipeline and
          only linearize it in IDSDevice?
    """

    # for IMX385
    MIN_GAIN_DB = 0
    MAX_GAIN_DB = 72

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.spinbox = cfu.doubleSpinBox_gain 

        self.widgets = [
            cfu.pushButton_gain_dn,
            cfu.pushButton_gain_up,
            cfu.label_gainWidget_title,
            cfu.slider_gain,
            self.spinbox ]

        self.locked = False # when Locked, don't show on-screen even in Expert mode
        self.visible = False

        # bindings
        self.spinbox.valueChanged.connect(self._sync_spinbox_to_slider_callback)
        self.spinbox.installEventFilter(ScrollStealFilter(self.spinbox))
        cfu.slider_gain.valueChanged.connect(self._sync_slider_to_spinbox_callback)
        cfu.slider_gain.installEventFilter(MouseWheelFilter(cfu.slider_gain))
        cfu.pushButton_gain_up.clicked.connect(self._up_callback)
        cfu.pushButton_gain_dn.clicked.connect(self._dn_callback)

        self.ctl.presets.register(self, "gain_db", getter=self.get_db, setter=self.set_db_callback)
        self.ctl.page_nav.register_observer("mode", self.update_visibility)
        self.update_visibility()

        for widget in self.widgets:
            widget.setWhatsThis("Configure gain in decibels (dB) on Sony IMX sensors.")

    def set_locked(self, flag):
        self.locked = flag
        self.update_visibility()

    def update_visibility(self):
        """ 
        Only show these controls when an IMX-based spectrometer is selected,
        and in Expert mode.
        """

        if self.locked:
            self.visible = False
        else:
            spec = self.ctl.multispec.current_spectrometer()
            if spec is None:
                self.visible = False
            else:
                self.visible = (spec.settings.is_micro() or spec.settings.is_ids()) and self.ctl.page_nav.doing_expert()

        # normally we'd do this at the enclosing frame, but gain is currently 
        # nested within the detectorControlWidget, and a sub-frame breaks the
        # CSS, so...just disappear the widgets for now
        for w in self.widgets:
            w.setVisible(self.visible)

        return self.visible

    def init_hotplug(self):
        """ called by initialize_new_device on hotplug, BEFORE reading / applying .ini """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        # on hotplug, initialize GainDB widget from EEPROM value
        spec.settings.state.gain_db = spec.settings.eeprom.detector_gain

    def reset(self):
        """ called by initialize_new_device a little after the other function """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        if not spec.settings.is_xs():
            return

        # load gain_db from .ini, falling back to spec.settings.state (copied from EEPROM)
        sn = spec.settings.eeprom.serial_number

        if spec.settings.is_xs():
            db = 8.0
        elif spec.settings.is_ids():
            db = 0.0

        if self.ctl.config.has_option(sn, "gain_db"):
            db = self.ctl.config.get_float(sn, "gain_db")
        elif spec.settings.state.gain_db is not None:
            db = spec.settings.state.gain_db
        elif spec.settings.eeprom.detector_gain is not None:
            db = spec.settings.eeprom.detector_gain

        self.set_db(db)

        # apply limits to SPINBOX
        self.spinbox.blockSignals(True)
        self.spinbox.setMinimum(self.MIN_GAIN_DB)
        self.spinbox.setMaximum(self.MAX_GAIN_DB)
        self.spinbox.blockSignals(False)

    def _quiet_set(self, widget, value):
        """ Set the value of a widget without invoking the ValueChanged event """
        widget.blockSignals(True)
        widget.setValue(value)
        widget.blockSignals(False)

    def set_focus(self):
        if self.visible:
            self.spinbox.setFocus()
            self.spinbox.selectAll()

    def set_db(self, db, quiet=False):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if not (spec.settings.is_xs() or spec.settings.is_ids()):
            return

        db = float(db)
        
        # save gain_db to application state
        self.ctl.multispec.set_state("gain_db", db)

        # persist gain_db in .ini
        self.ctl.config.set(spec.settings.eeprom.serial_number, "gain_db", db)

        # send gain update message to device 

        # TODO: support "gain_db" in FeatureIdentificationDevice for XS
        if spec.settings.is_xs():
            self.ctl.multispec.change_device_setting("detector_gain", db)
        elif spec.settings.is_ids():
            self.ctl.multispec.change_device_setting("gain_db", db)

        # ensure both gain widgets are correct, without generating additional events
        self._quiet_set(self.spinbox, db)
        self._quiet_set(self.ctl.form.ui.slider_gain, db)

        if not quiet:
            spec.app_state.check_refs()

    def _up_callback(self):
        util.incr_spinbox(self.spinbox)
        self.set_db(self.spinbox.value())

    def _dn_callback(self):
        util.decr_spinbox(self.spinbox)
        self.set_db(self.spinbox.value())

    def _sync_slider_to_spinbox_callback(self):
        self.set_db(self.ctl.form.ui.slider_gain.value()) 

    def _sync_spinbox_to_slider_callback(self):
        self.set_db(self.spinbox.value())

    def get_db(self):
        return self.spinbox.value()

    def set_db_callback(self, value):
        """ used by Presets """
        self.set_db(value)
