import logging

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

        self.sb_max_ms         = cfu.spinBox_auto_raman_max_ms           
        self.sb_start_integ_ms = cfu.spinBox_auto_raman_start_integ_ms   
        self.sb_start_gain_db  = cfu.spinBox_auto_raman_start_gain_db    
        self.sb_max_integ_ms   = cfu.spinBox_auto_raman_max_integ_ms     
        self.sb_min_integ_ms   = cfu.spinBox_auto_raman_min_integ_ms     
        self.sb_max_gain_db    = cfu.spinBox_auto_raman_max_gain_db      
        self.sb_min_gain_db    = cfu.spinBox_auto_raman_min_gain_db      
        self.sb_target_counts  = cfu.spinBox_auto_raman_target_counts    
        self.sb_max_counts     = cfu.spinBox_auto_raman_max_counts       
        self.sb_min_counts     = cfu.spinBox_auto_raman_min_counts       
        self.sb_max_factor     = cfu.spinBox_auto_raman_max_factor       
        self.sb_saturation     = cfu.spinBox_auto_raman_saturation       
        self.ds_drop_factor    = cfu.doubleSpinBox_auto_raman_drop_factor

        self.sb_max_ms         .valueChanged.connect(self.update_from_gui)
        self.sb_start_integ_ms .valueChanged.connect(self.update_from_gui)
        self.sb_start_gain_db  .valueChanged.connect(self.update_from_gui)
        self.sb_max_integ_ms   .valueChanged.connect(self.update_from_gui)
        self.sb_min_integ_ms   .valueChanged.connect(self.update_from_gui)
        self.sb_max_gain_db    .valueChanged.connect(self.update_from_gui)
        self.sb_min_gain_db    .valueChanged.connect(self.update_from_gui)
        self.sb_target_counts  .valueChanged.connect(self.update_from_gui)
        self.sb_max_counts     .valueChanged.connect(self.update_from_gui)
        self.sb_min_counts     .valueChanged.connect(self.update_from_gui)
        self.sb_max_factor     .valueChanged.connect(self.update_from_gui)
        self.sb_saturation     .valueChanged.connect(self.update_from_gui)
        self.ds_drop_factor    .valueChanged.connect(self.update_from_gui)

        ctl.presets.register(self, "auto_raman_max_ms"        , setter=self.set_max_ms        , getter=self.get_max_ms        )
        ctl.presets.register(self, "auto_raman_start_integ_ms", setter=self.set_start_integ_ms, getter=self.get_start_integ_ms)
        ctl.presets.register(self, "auto_raman_start_gain_db" , setter=self.set_start_gain_db , getter=self.get_start_gain_db )
        ctl.presets.register(self, "auto_raman_max_integ_ms"  , setter=self.set_max_integ_ms  , getter=self.get_max_integ_ms  )
        ctl.presets.register(self, "auto_raman_min_integ_ms"  , setter=self.set_min_integ_ms  , getter=self.get_min_integ_ms  )
        ctl.presets.register(self, "auto_raman_max_gain_db"   , setter=self.set_max_gain_db   , getter=self.get_max_gain_db   )
        ctl.presets.register(self, "auto_raman_min_gain_db"   , setter=self.set_min_gain_db   , getter=self.get_min_gain_db   )
        ctl.presets.register(self, "auto_raman_target_counts" , setter=self.set_target_counts , getter=self.get_target_counts )
        ctl.presets.register(self, "auto_raman_max_counts"    , setter=self.set_max_counts    , getter=self.get_max_counts    )
        ctl.presets.register(self, "auto_raman_min_counts"    , setter=self.set_min_counts    , getter=self.get_min_counts    )
        ctl.presets.register(self, "auto_raman_max_factor"    , setter=self.set_max_factor    , getter=self.get_max_factor    )
        ctl.presets.register(self, "auto_raman_saturation"    , setter=self.set_saturation    , getter=self.get_saturation    )
        ctl.presets.register(self, "auto_raman_drop_factor"   , setter=self.set_drop_factor   , getter=self.get_drop_factor   )

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
        auto_raman_request = AutoRamanRequest(
            max_ms         = self.get_max_ms        (),
            start_integ_ms = self.get_start_integ_ms(), # consider self.ctl.integration_time_feature.get_ms()
            start_gain_db  = self.get_start_gain_db (), # consider self.ctl.gain_db_feature.get_db()
            max_integ_ms   = self.get_max_integ_ms  (),
            min_integ_ms   = self.get_min_integ_ms  (),
            max_gain_db    = self.get_max_gain_db   (),
            min_gain_db    = self.get_min_gain_db   (),
            target_counts  = self.get_target_counts (),
            max_counts     = self.get_max_counts    (),
            min_counts     = self.get_min_counts    (),
            max_factor     = self.get_max_factor    (),
            saturation     = self.get_saturation    (),
            drop_factor    = self.get_drop_factor   ())
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

    def update_from_gui(self):
        pass

    def set_max_ms        (self, value): self.sb_max_ms        .setValue(value)
    def set_start_integ_ms(self, value): self.sb_start_integ_ms.setValue(value)
    def set_start_gain_db (self, value): self.sb_start_gain_db .setValue(value)
    def set_max_integ_ms  (self, value): self.sb_max_integ_ms  .setValue(value)
    def set_min_integ_ms  (self, value): self.sb_min_integ_ms  .setValue(value)
    def set_max_gain_db   (self, value): self.sb_max_gain_db   .setValue(value)
    def set_min_gain_db   (self, value): self.sb_min_gain_db   .setValue(value)
    def set_target_counts (self, value): self.sb_target_counts .setValue(value)
    def set_max_counts    (self, value): self.sb_max_counts    .setValue(value)
    def set_min_counts    (self, value): self.sb_min_counts    .setValue(value)
    def set_max_factor    (self, value): self.sb_max_factor    .setValue(value)
    def set_saturation    (self, value): self.sb_saturation    .setValue(value)
    def set_drop_factor   (self, value): self.ds_drop_factor   .setValue(value)

    def get_max_ms        (self): return self.sb_max_ms        .value()
    def get_start_integ_ms(self): return self.sb_start_integ_ms.value()
    def get_start_gain_db (self): return self.sb_start_gain_db .value()
    def get_max_integ_ms  (self): return self.sb_max_integ_ms  .value()
    def get_min_integ_ms  (self): return self.sb_min_integ_ms  .value()
    def get_max_gain_db   (self): return self.sb_max_gain_db   .value()
    def get_min_gain_db   (self): return self.sb_min_gain_db   .value()
    def get_target_counts (self): return self.sb_target_counts .value()
    def get_max_counts    (self): return self.sb_max_counts    .value()
    def get_min_counts    (self): return self.sb_min_counts    .value()
    def get_max_factor    (self): return self.sb_max_factor    .value()
    def get_saturation    (self): return self.sb_saturation    .value()
    def get_drop_factor   (self): return self.ds_drop_factor   .value()
