import logging

from . import util
from .ScrollStealFilter import ScrollStealFilter
from .MouseWheelFilter import MouseWheelFilter

log = logging.getLogger(__name__)

class IntegrationTimeFeature(object):

    # integration time slider steps in 100ms increments, and only goes up to 5sec
    MILLISEC_TO_TENTHS = 0.01
    TENTHS_TO_SEC = 0.1
    MAX_SLIDER_SEC = 5

    def __init__(self,
            bt_dn,
            bt_up,
            multispec,
            slider,
            spinbox
        ):

        self.bt_dn      = bt_dn
        self.bt_up      = bt_up
        self.multispec  = multispec
        self.slider     = slider
        self.spinbox    = spinbox

        # bindings
        self.slider     .valueChanged       .connect(self.sync_slider_to_spinbox_callback)
        self.spinbox    .valueChanged       .connect(self.sync_spinbox_to_slider_callback)
        self.slider                         .installEventFilter(MouseWheelFilter(self.slider))
        self.spinbox                        .installEventFilter(ScrollStealFilter(self.spinbox))
        self.bt_up      .clicked            .connect(self.up_callback)
        self.bt_dn      .clicked            .connect(self.dn_callback)

    # called by initialize_new_device on hotplug, BEFORE reading / applying .ini
    def init_hotplug(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        self.spinbox.setValue(spec.settings.eeprom.startup_integration_time_ms)

    # called by initialize_new_device a little after the other function
    def reset(self, hotplug=False):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        min_ms = spec.settings.eeprom.min_integration_time_ms
        max_ms = 2**24

        # set slider limits FIRST, with signals disabled, because when we later
        # set the spinner, it will correctly set the final value within the limits.
        min_tenths = self.MILLISEC_TO_TENTHS * min_ms
        max_tenths = self.MILLISEC_TO_TENTHS * max_ms
        if (max_tenths * self.TENTHS_TO_SEC > self.MAX_SLIDER_SEC):
            max_tenths = self.MAX_SLIDER_SEC / self.TENTHS_TO_SEC

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
            # cap at 1sec, else application seems dead
            now_ms = min(max_ms, max(min_ms, min(1000, self.spinbox.value())))
        else:
            now_ms = spec.settings.state.integration_time_ms
        self.spinbox.blockSignals(True)
        self.spinbox.setMinimum(min_ms)
        self.spinbox.setMaximum(max_ms)
        self.spinbox.blockSignals(False)

        # signals enabled, so will propogate everywhere
        self.spinbox.setValue  (now_ms)

        log.info("spinbox integration limits updated to (%.2f, %.2fms) (current %.2fms)",
            self.spinbox.minimum(), self.spinbox.maximum(), self.spinbox.value())

        if hotplug:
            log.debug("forcing integration time downstream on hotplug")
            self.multispec.set_state("integration_time_ms", now_ms)
            spec.change_device_setting("integration_time_ms", now_ms)
            spec.reset_acquisition_timeout()

    ## If you're not sure which function to call, call this one.
    #
    # This sets the spinbox, which should (passively) auto-sync the slider, and then sends
    # the new value downstream (to one if unlocked, all if locked), plus updates states
    # appropriately.
    def set_ms(self, ms):
        self.spinbox.setValue(ms)

    def up_callback(self):
        util.incr_spinbox(self.spinbox)

    def dn_callback(self):
        util.decr_spinbox(self.spinbox)

    def sync_slider_to_spinbox_callback(self):
        tenths = self.slider.value()
        ms = tenths / self.MILLISEC_TO_TENTHS

        if ms < self.spinbox.minimum():
            ms = self.spinbox.minimum()
        elif ms > self.spinbox.maximum():
            ms = self.spinbox.maximum()

        log.debug("sync_to_spinbox_callback: slider %.2f tenths to %.2f ms", tenths, ms)
        self.spinbox.setValue(ms) 

    def sync_spinbox_to_slider_callback(self):
        ms = self.spinbox.value()

        # update other GUI widget WITHOUT triggering its callback (but apparently abiding its limits)
        tenths = int(round(ms * self.MILLISEC_TO_TENTHS, 0))
        log.debug("sync_spinbox_to_slider: spinbox %.2f ms to %d tenths", ms, tenths)
        self.slider.blockSignals(True)
        self.slider.setValue(tenths)
        self.slider.blockSignals(False)

        # actually send the change downstream
        self.multispec.set_state("integration_time_ms", ms)
        self.multispec.change_device_setting("integration_time_ms", ms)

        # reset timeouts
        if self.multispec.locked:
            for spec in self.multispec.get_spectrometers():
                spec.reset_acquisition_timeout()
        else:
            spec = self.multispec.current_spectrometer()
            if spec is not None:
                spec.reset_acquisition_timeout()

            ####################################################################
            # remind users to keep dark/reference in sync
            ####################################################################
            
            app_state = spec.app_state
            refresh_dark      = app_state.has_dark()      and ms != app_state.dark_integration_time_ms 
            refresh_reference = app_state.has_reference() and ms != app_state.reference_integration_time_ms 
            if refresh_dark and refresh_reference:
                self.marquee.info("Recommend re-taking dark and reference with new integration time")
            elif refresh_reference:
                self.marquee.info("Recommend re-taking reference with new integration time")
            elif refresh_dark:
                self.marquee.info("Recommend re-taking dark with new integration time")

