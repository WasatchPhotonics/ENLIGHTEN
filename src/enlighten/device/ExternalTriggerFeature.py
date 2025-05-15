import logging

from wasatch.SpectrometerState        import SpectrometerState

log = logging.getLogger(__name__)

class ExternalTriggerFeature:
    """
    Encapsulate external hardware triggering.
    """
    
    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_enabled = cfu.checkBox_external_trigger_enabled

        self.enabled = False

        self.cb_enabled.stateChanged.connect(self.enable_callback)
        
    def update_visibility(self):
        """ Called by init_new_spectrometer on connection or selection. """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.cb_enabled.setVisible(False)
            return

        try:
            # is checkbox visible?
            supports_triggering = spec.settings.hardware_info.supports_triggering()
            visible = supports_triggering and self.ctl.page_nav.doing_expert()
            self.cb_enabled.setVisible(visible)

            # is checkbox checked?
            self.enabled = visible and (spec.settings.state.trigger_source == SpectrometerState.TRIGGER_SOURCE_EXTERNAL)
            self.cb_enabled.setChecked(self.enabled)
        except:
            self.cb_enabled.setVisible(False)
            self.enabled = False
            self.cb_enabled.setChecked(self.enabled)

    def is_enabled(self): 
        return self.enabled

    def enable_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        self.enabled = self.cb_enabled.isChecked()

        if self.enabled:
            value = SpectrometerState.TRIGGER_SOURCE_EXTERNAL
        else:
            value = SpectrometerState.TRIGGER_SOURCE_INTERNAL

        # Track trigger status to ensure that it only gets sent once
        if value == spec.settings.state.trigger_source:
            return

        # Don't actually set the SpectrometerState here; let wasatch.FID do that.
        # Note that now that we're multithreaded, ENLIGHTEN's copy of SpectrometerState
        # is the same as WasatchDevice's.  That means that if we transition from
        # external to internal here, it happens IMMEDIATELY in wasatch.FID, meaning
        # as soon as the current acquisition times-out, it immediately says "I timed-
        # out but wasn't externally triggered, so let's flow a poison pill upstream!"
        #
        # self.ctl.multispec.set_state("trigger_source", value)

        log.warn("Setting trigger source to %d", value)
        self.ctl.multispec.change_device_setting("trigger_source", value)

        if self.enabled:
            self.ctl.marquee.info("waiting for trigger")

        spec.reset_acquisition_timeout()
