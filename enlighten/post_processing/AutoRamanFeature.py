import logging
from datetime import datetime, timedelta

from wasatch.TakeOneRequest   import TakeOneRequest
from wasatch.AutoRamanRequest import AutoRamanRequest 

from enlighten.util import unwrap

log = logging.getLogger(__name__)

class AutoRamanFeature:
    """
    This feature controls the (normally-hidden) "Auto-Raman Measurement" button 
    on the Laser Control Widget.

    @todo consider registering to LaserControlFeature events so if the user tries
          turning off the laser, we can force-stop the Auto-Raman measurement.
    """

    LASER_WARMUP_MS = 5000
    SECTION = "Auto-Raman"
    LASER_CONTROL_DISABLE_REASON = "Auto-Raman enabled"

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = self.ctl.form.ui

        self.bt_laser   = cfu.pushButton_laser_toggle
        self.bt_measure = cfu.pushButton_auto_raman_measurement
        self.cb_config  = cfu.checkBox_auto_raman_config
        self.fr_config  = cfu.frame_auto_raman_config

        self.visible = False
        self.running = False

        self.bt_measure.clicked.connect(self.measure_callback)
        self.cb_config.stateChanged.connect(self.update_visibility)

        self.bt_measure.setWhatsThis(unwrap("""
            Auto-Raman provides one-click collection of an averaged, 
            dark-corrected Raman measurement with automatically optimized 
            integration time (and gain, on XS series).

            This feature is potentially hazardous as it involves automonously 
            enabling the laser, so please read the ENLIGHTEN documentation 
            carefully before enabling it.

            Clicking the button will clear the current dark, then enable the 
            laser, wait a configured "warmup" time for the laser to stabilize, 
            then attempt to optimize acquisition parameters by first tuning 
            integration time, then when necessary gain. 

            After acquisition parameters have been optimized, ENLIGHTEN will 
            determine how many averaged measurements can be acquired within the 
            configured "measurement" period. It will then complete the computed
            number of Raman sample spectra, disable the laser, take the same 
            number of averaged dark spectra (storing the averaged dark), and 
            perform dark correction.

            The final processed measurement will then be graphed and sent to any 
            connected plug-ins for additional processing. The optimized 
            integration time and gain will be updated to the ENLIGHTEN GUI."""))

        self.update_visibility()

        self.ctl.vcr_controls.register_observer("pause", self.update_visibility)
        self.ctl.vcr_controls.register_observer("play",  self.update_visibility)

    ##
    # called by Controller.disconnect_device to ensure we turn this off between
    # connections
    def disconnect(self):
        self.update_visibility()

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.visible = True # False (do not commit)
        else:
            self.visible = self.ctl.page_nav.doing_raman() and \
                           self.ctl.vcr_controls.is_paused() and \
                           spec.settings.eeprom.has_laser

        log.debug(f"update_visibility: visible {self.visible}")
        self.bt_measure.setVisible(self.visible)

        if self.visible and self.ctl.page_nav.doing_expert():
            self.cb_config.setVisible(True)
            self.fr_config.setVisible(self.cb_config.isChecked())
        else:
            self.cb_config.setVisible(False)
            self.fr_config.setVisible(False)

    def measure_callback(self):
        log.debug(f"measure_callback: starting")
        self.running = True

        self.ctl.gui.colorize_button(self.bt_measure, True)

        # clear existing dark
        self.ctl.dark_feature.clear(quiet=True)
        self.ctl.marquee.info("Collecting Auto-Raman measurement...")

        # define a TakeOneRequest with AutoRaman enabled
        # - consider start_integ_ms = self.ctl.integration_time_feature.get_ms()
        # - consider start_gain_db  = self.ctl.gain_db_feature.get_db()
        auto_raman_request = AutoRamanRequest()
        take_one_request = TakeOneRequest(auto_raman_request=auto_raman_request)

        log.debug(f"measure_callback: starting TakeOne")
        self.ctl.take_one.start(completion_callback=self.completion_callback, stop_callback=self.stop_callback, template=take_one_request)

        log.debug(f"measure_callback: done")

    def stop_callback(self):
        log.debug(f"stop_callback: here")
        self.running = False
        self.ctl.gui.colorize_button(self.bt_measure, False)
        self.ctl.marquee.error("Auto-Raman measurement cancelled")

    def completion_callback(self):
        log.debug(f"completion_callback: here")
        # self.ctl.laser_control.refresh_laser_buttons()
        self.running = False
        self.ctl.gui.colorize_button(self.bt_measure, False)
        self.ctl.marquee.info("Auto-Raman measurement complete")
