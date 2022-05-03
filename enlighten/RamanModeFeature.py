import logging

log = logging.getLogger(__name__)

##
# This class encapsulates the "Raman Mode" features intended for the new 
# ramanMicro (SiG) spectrometers.  Note that HW features are developmental, so
# some are currently implemented in software; this may change as FW develops.
#
# If and when other spectrometers receive a Laser Watchdog feature, we may break
# that and other portions out into other classes.
#
# This feature cannot be enabled at startup for safety reasons.
#
# @todo consider if and where we should disable the laser if battery too low
class RamanModeFeature(object):

    def __init__(self,
            bt_laser,
            cb_enable,
            multispec,
            page_nav,
            vcr_controls):

        self.bt_laser           = bt_laser
        self.cb_enable          = cb_enable
        self.page_nav           = page_nav
        self.multispec          = multispec
        self.vcr_controls       = vcr_controls

        self.enabled = False
        self.visible = False

        self.vcr_controls.register_observer("pause", self.update_visibility)
        self.vcr_controls.register_observer("play",  self.update_visibility)

        self.cb_enable          .stateChanged       .connect(self.enable_callback)

        self.update_visibility()

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            self.visible = False
            is_micro = False
        else:
            is_micro = spec.settings.is_micro()
            self.visible = is_micro and \
                           self.page_nav.doing_raman() and \
                           self.vcr_controls.is_paused() and \
                           spec.settings.eeprom.has_laser

        log.debug("visible = %s", self.visible)
        self.cb_enable      .setVisible(self.visible)

        if not self.visible:
            self.cb_enable.setChecked(False)
        else:
            self.enable_callback()

    ##
    # called by Controller.disconnect_device to ensure we turn this off between
    # connections
    def disconnect(self):
        self.cb_enable.setChecked(False)
        self.update_visibility()

    ############################################################################
    # Callbacks
    ############################################################################

    def enable_callback(self):
        self.enabled = self.visible and self.cb_enable.isChecked()

        log.debug("enable = %s", self.enabled)

        self.multispec.set_state("acquisition_laser_trigger_enable", self.enabled)
        self.multispec.change_device_setting("acquisition_laser_trigger_enable", self.enabled)

        # is there anything else in ENLIGHTEN which might dis/enable the laser button?
        self.bt_laser.setEnabled(not self.enabled)
        self.bt_laser.setToolTip("disabled in Raman Mode" if self.enabled else "fire laser (ctrl-L)")
