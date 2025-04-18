import logging

from enlighten import util
from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten.ui.MouseWheelFilter import MouseWheelFilter

from enlighten.common import msgbox

log = logging.getLogger(__name__)

class IntegrationTimeFeature:

    # integration time slider steps in 100ms increments, and only goes up to 5sec
    MILLISEC_TO_TENTHS = 0.01
    TENTHS_TO_SEC = 0.1
    MAX_SLIDER_SEC = 5

    def __init__(self, ctl):
        self.ctl = ctl

        cfu = ctl.form.ui
        self.bt_dn = cfu.pushButton_integration_time_ms_dn
        self.bt_up = cfu.pushButton_integration_time_ms_up
        self.slider = cfu.slider_integration_time_ms
        self.spinbox = cfu.spinBox_integration_time_ms

        # bindings
        self.slider.valueChanged.connect(self.slider_callback)
        self.spinbox.valueChanged.connect(self.spinbox_callback)
        self.bt_up.clicked.connect(self.up_callback)
        self.bt_dn.clicked.connect(self.dn_callback)

        self.slider.installEventFilter(MouseWheelFilter(self.slider))
        self.spinbox.installEventFilter(ScrollStealFilter(self.spinbox))

        self.ctl.presets.register(self, "integration_time_ms", getter=self.get_ms, setter=self.set_ms)

        for widget in [ self.slider, self.spinbox, self.bt_up, self.bt_dn ]:
            widget.setWhatsThis("Control the detector integration time, or sensor exposure time, in milliseconds.")

    # called by initialize_new_device on hotplug, BEFORE reading / applying .ini
    def init_hotplug(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

    # called by initialize_new_device a little after the other function
    def reset(self, hotplug=False):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        min_ms = spec.settings.eeprom.min_integration_time_ms
        max_ms = spec.settings.eeprom.max_integration_time_ms if spec.settings.is_xs() else 2**24

        if max_ms == 0:
            # do not silently replace a zero value, let the user know
            msgbox("Warning: Max integration time is set to zero. Using 1000ms instead.")
            max_ms = 1000

        # set slider limits FIRST, with signals disabled, because when we later
        # set the spinner, it will correctly set the final value within the limits.
        min_tenths = self.MILLISEC_TO_TENTHS * min_ms
        max_tenths = self.MILLISEC_TO_TENTHS * max_ms
        if (max_tenths * self.TENTHS_TO_SEC > self.MAX_SLIDER_SEC):
            max_tenths = self.MAX_SLIDER_SEC / self.TENTHS_TO_SEC

        now_ms = self.ctl.config.get_float(spec.settings.eeprom.serial_number, "integration_time_ms")
        log.info("integration time from config: %d" % now_ms)
        
        self.slider.blockSignals(True)
        self.slider.setMinimum(min_tenths)
        self.slider.setMaximum(max_tenths)
        self.slider.setValue  (min_tenths) # this will shortly be overwritten, which is fine
        self.slider.blockSignals(False)

        log.debug("slider limits (%.2f, %.2f tenths) (temporary value %.2f tenths)",
            self.slider.minimum(), self.slider.maximum(), self.slider.value())

        # now set the spinbox (with signals enabled), which will ensure both that
        # the slider gets the final value, and MAY send the integration times 
        # downstream and to state...IF THEY REPRESENT A CHANGE (may not be the 
        # case for some hotplug events).
        if hotplug:
            # cap at 5sec, else application seems dead
            now_ms = min(max_ms, max(min_ms, min(5000, now_ms)))
            
        self.spinbox.blockSignals(True)
        self.spinbox.setMinimum(min_ms)
        self.spinbox.setMaximum(max_ms)
        self.spinbox.blockSignals(False)

        self.set_ms(now_ms)

        log.info("spinbox integration limits updated to (%.2f, %.2fms) (current %.2fms)",
            self.spinbox.minimum(), self.spinbox.maximum(), self.spinbox.value())

        if hotplug:
            # save integration time to application state
            self.ctl.multispec.set_state("integration_time_ms", now_ms)

            # send integration time change to hardware
            spec.change_device_setting("integration_time_ms", now_ms)

            spec.app_state.received_reading_at_current_integration_time = False

            spec.reset_acquisition_timeout()

    ## If you're not sure which function to call, call this one.
    #
    # This sets the spinbox, which should (passively) auto-sync the slider, and then sends
    # the new value downstream (to one if unlocked, all if locked), plus updates states
    # appropriately.
    def set_ms(self, ms, quiet=False):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        ms = int(ms)

        self.slider.blockSignals(True)
        tenths = int(round(ms * self.MILLISEC_TO_TENTHS, 0))
        self.slider.setValue(tenths)
        self.slider.blockSignals(False)

        self.spinbox.blockSignals(True)
        self.spinbox.setValue(ms) 
        self.spinbox.blockSignals(False)

        # save integration time to application state
        self.ctl.multispec.set_state("integration_time_ms", ms)

        # persist integration time in .ini
        log.debug("integration time to config: %d", ms)
        if self.ctl.multispec.locked:
            for foo in self.ctl.multispec.get_spectrometers():
                self.ctl.config.set(foo.settings.eeprom.serial_number, "integration_time_ms", ms)
        else:
            self.ctl.config.set(spec.settings.eeprom.serial_number, "integration_time_ms", ms)

        # send changed integration time to hardware
        self.ctl.multispec.change_device_setting("integration_time_ms", ms)
        self.ctl.multispec.set_app_state("received_reading_at_current_integration_time", False)

        # reset timeouts
        if self.ctl.multispec.locked:
            for spec in self.ctl.multispec.get_spectrometers():
                spec.reset_acquisition_timeout()
        else:
            spec.reset_acquisition_timeout()
            if not quiet:
                spec.app_state.check_refs()

    def up_callback(self):
        util.incr_spinbox(self.spinbox)

    def dn_callback(self):
        util.decr_spinbox(self.spinbox)

    def slider_callback(self):
        tenths = self.slider.value()
        ms = tenths / self.MILLISEC_TO_TENTHS

        if ms < self.spinbox.minimum():
            ms = self.spinbox.minimum()
        elif ms > self.spinbox.maximum():
            ms = self.spinbox.maximum()
        self.set_ms(ms) 

    def spinbox_callback(self):
        ms = self.spinbox.value()
        self.set_ms(ms)

    def set_focus(self):
        self.spinbox.setFocus()
        self.spinbox.selectAll()

    def get_ms(self):
        return self.spinbox.value()
