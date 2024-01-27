import logging

from enlighten.ui.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class RegionControlFeature:

    def __init__(self,
            cb_enabled,
            multispec,
            spinbox):
        
        self.cb_enabled = cb_enabled
        self.multispec  = multispec
        self.spinbox    = spinbox

        self.enabled = False
        self.spinbox.setEnabled(False)

        self.cb_enabled .stateChanged   .connect(self.enabled_callback)
        self.spinbox    .valueChanged   .connect(self.region_callback)
        self.spinbox                    .installEventFilter(ScrollStealFilter(self.spinbox))

    def enabled_callback(self):
        was_enabled = self.enabled
        self.enabled = self.cb_enabled.isChecked()

        self.spinbox.setEnabled(self.enabled)

        if not self.enabled and was_enabled:
            log.debug("disabling (clearing regions)")
            spec = self.multispec.current_spectrometer()
            if spec is not None:
                spec.change_device_setting("clear_regions")

        if self.enabled and not was_enabled:
            log.debug("enabling (sending downstream)")
            self.region_callback()

    def region_callback(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or not self.enabled:
            return

        # GUI is 1-4, internal is 0-3
        n = self.spinbox.value() - 1

        log.debug(f"setting region to {n}")

        # update locally, to cause wavelengths / wavenumbers to be updated
        # SB: needed? isn't this call generated using process_f in the next line ?
        spec.settings.set_single_region(n)

        # send downstream
        spec.change_device_setting("single_region", n)

        spec.settings.state.ignore_timeouts_for(sec=2)
