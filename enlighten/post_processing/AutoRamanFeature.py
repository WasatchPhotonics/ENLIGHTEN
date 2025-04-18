import logging
from datetime import datetime

from wasatch.TakeOneRequest   import TakeOneRequest
from wasatch.AutoRamanRequest import AutoRamanRequest 

from enlighten.util import unwrap
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

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

        self.bt_laser           = cfu.pushButton_laser_toggle
        self.bt_measure         = cfu.pushButton_auto_raman_measurement
        self.bt_convenience     = cfu.pushButton_auto_raman_convenience
        self.cb_config          = cfu.checkBox_auto_raman_config
        self.cb_retain_settings = cfu.checkBox_auto_raman_retain_settings
        self.cb_auto_save       = cfu.checkBox_auto_raman_auto_save
        self.lb_elapsed         = cfu.label_auto_raman_elapsed
        self.fr_config          = cfu.frame_auto_raman_config
        self.buttons            = [ self.bt_measure, self.bt_convenience ]

        self.visible = False
        self.running = False
        self.auto_save = False
        self.retain_settings = False
        self.prev_integration_time_ms = None
        self.prev_gain_db = None
        self.request_time = None

        self.sb_max_ms                  = cfu.spinBox_auto_raman_max_ms           
        self.sb_start_integ_ms          = cfu.spinBox_auto_raman_start_integ_ms   
        self.sb_start_gain_db           = cfu.spinBox_auto_raman_start_gain_db    
        self.sb_max_integ_ms            = cfu.spinBox_auto_raman_max_integ_ms     
        self.sb_min_integ_ms            = cfu.spinBox_auto_raman_min_integ_ms     
        self.sb_max_gain_db             = cfu.spinBox_auto_raman_max_gain_db      
        self.sb_min_gain_db             = cfu.spinBox_auto_raman_min_gain_db      
        self.sb_target_counts           = cfu.spinBox_auto_raman_target_counts    
        self.sb_max_counts              = cfu.spinBox_auto_raman_max_counts       
        self.sb_min_counts              = cfu.spinBox_auto_raman_min_counts       
        self.sb_max_factor              = cfu.spinBox_auto_raman_max_factor       
        self.sb_max_avg                 = cfu.spinBox_auto_raman_max_avg
        self.sb_saturation              = cfu.spinBox_auto_raman_saturation       
        self.ds_drop_factor             = cfu.doubleSpinBox_auto_raman_drop_factor
        self.sb_laser_warning_delay_sec = cfu.spinBox_auto_raman_laser_warning_delay_sec
        self.cb_onboard                 = cfu.checkBox_auto_raman_onboard

        self.cb_config          .clicked    .connect(self.update_config)
        self.cb_retain_settings .clicked    .connect(self.update_config)
        self.cb_auto_save       .clicked    .connect(self.update_config)
        self.cb_onboard         .clicked    .connect(self.update_config)

        for b in self.buttons:
            b.clicked.connect(self.measure_callback)

        for widget in [ self.sb_max_ms,
                        self.sb_start_integ_ms,
                        self.sb_start_gain_db,
                        self.sb_max_integ_ms,
                        self.sb_min_integ_ms,
                        self.sb_max_gain_db,
                        self.sb_min_gain_db,
                        self.sb_target_counts,
                        self.sb_max_counts,
                        self.sb_min_counts,
                        self.sb_max_factor,
                        self.sb_max_avg,
                        self.sb_saturation,
                        self.ds_drop_factor,
                        self.sb_laser_warning_delay_sec ]:
            widget.installEventFilter(ScrollStealFilter(widget))

        ctl.presets.register(self, "auto_raman_max_ms"                 , setter=self.set_max_ms                 , getter=self.get_max_ms                 )
        ctl.presets.register(self, "auto_raman_start_integ_ms"         , setter=self.set_start_integ_ms         , getter=self.get_start_integ_ms         )
        ctl.presets.register(self, "auto_raman_start_gain_db"          , setter=self.set_start_gain_db          , getter=self.get_start_gain_db          )
        ctl.presets.register(self, "auto_raman_max_integ_ms"           , setter=self.set_max_integ_ms           , getter=self.get_max_integ_ms           )
        ctl.presets.register(self, "auto_raman_min_integ_ms"           , setter=self.set_min_integ_ms           , getter=self.get_min_integ_ms           )
        ctl.presets.register(self, "auto_raman_max_gain_db"            , setter=self.set_max_gain_db            , getter=self.get_max_gain_db            )
        ctl.presets.register(self, "auto_raman_min_gain_db"            , setter=self.set_min_gain_db            , getter=self.get_min_gain_db            )
        ctl.presets.register(self, "auto_raman_target_counts"          , setter=self.set_target_counts          , getter=self.get_target_counts          )
        ctl.presets.register(self, "auto_raman_max_counts"             , setter=self.set_max_counts             , getter=self.get_max_counts             )
        ctl.presets.register(self, "auto_raman_min_counts"             , setter=self.set_min_counts             , getter=self.get_min_counts             )
        ctl.presets.register(self, "auto_raman_max_factor"             , setter=self.set_max_factor             , getter=self.get_max_factor             )
        ctl.presets.register(self, "auto_raman_max_avg"                , setter=self.set_max_avg                , getter=self.get_max_avg                )
        ctl.presets.register(self, "auto_raman_saturation"             , setter=self.set_saturation             , getter=self.get_saturation             )
        ctl.presets.register(self, "auto_raman_drop_factor"            , setter=self.set_drop_factor            , getter=self.get_drop_factor            )
        ctl.presets.register(self, "auto_raman_laser_warning_delay_sec", setter=self.set_laser_warning_delay_sec, getter=self.get_laser_warning_delay_sec)
        ctl.presets.register(self, "auto_raman_onboard"                , setter=self.set_onboard                , getter=self.get_onboard                )

        self.init_from_config()

        for b in self.buttons:
            b.setToolTip("Collect one dark-corrected, averaged Raman measurement (ctrl-*)")
            b.setWhatsThis(unwrap("""
                Auto-Raman provides one-click collection of an averaged, 
                dark-corrected Raman measurement with automatically optimized 
                integration time (and gain, on XS series).

                This feature is potentially hazardous as it involves automonously 
                enabling the laser, so please read the ENLIGHTEN documentation 
                carefully before enabling it.

                Clicking the button will clear the current dark, enable the 
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
                connected plug-ins for additional processing. If requested, ENLIGHTEN 
                will then apply the optimized to the ENLIGHTEN GUI."""))

    def init_from_config(self):
        s = "Auto-Raman"
        self.cb_config         .setChecked(self.ctl.config.get_bool(s, "config"))
        self.cb_auto_save      .setChecked(self.ctl.config.get_bool(s, "auto_save"))
        self.cb_retain_settings.setChecked(self.ctl.config.get_bool(s, "retain_settings"))
        self.cb_onboard        .setChecked(self.ctl.config.get_bool(s, "onboard"))

        self.update_visibility()

    def update_config(self):
        self.update_visibility() # sets .auto_save, .retain_settings etc

        self.ctl.config.set(self.SECTION, "config",          self.cb_config.isChecked())
        self.ctl.config.set(self.SECTION, "auto_save",       self.auto_save)
        self.ctl.config.set(self.SECTION, "retain_settings", self.retain_settings)
        self.ctl.config.set(self.SECTION, "onboard",         self.get_onboard())

    ##
    # called by Controller.disconnect_device to ensure we turn this off between
    # connections
    def disconnect(self):
        self.update_visibility()

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.visible = False 
        else:
            self.visible = self.ctl.page_nav.doing_raman() and \
                           spec.settings.eeprom.has_laser

        self.auto_save = self.cb_auto_save.isChecked()
        self.retain_settings = self.cb_retain_settings.isChecked()

        for b in self.buttons:
            b.setVisible(self.visible)

        if self.visible and self.ctl.page_nav.doing_expert():
            self.cb_config.setVisible(True)
            self.fr_config.setVisible(self.cb_config.isChecked())
        else:
            self.cb_config.setVisible(False)
            self.fr_config.setVisible(False)

    def force_on(self, flag):
        for b in self.buttons:
            self.ctl.gui.colorize_button(b, flag)
            b.setEnabled(not flag)

    def measure_callback(self):

        # warn user of laser-safety precautions
        warn_suppress = self.ctl.config.get(self.SECTION, "suppress_warning", default=False)
        if not warn_suppress:
            result = self.ctl.gui.msgbox_with_checkbox(
                title="Auto-Raman Laser Warning", 
                text=unwrap("""Auto-Raman measurements will automatically fire the laser
                               while optimizing and collecting the dark-corrected Raman
                               measurement. While the measurement is in progress, the
                               standard laser control buttons will be disabled, but you
                               can halt the Auto-Raman measurement at any time by pressing
                               the 'Stop' button (⏹️) on the VCR controls."""),
                checkbox_text="Don't show again")

            if not result["ok"]:
                return

            if result["checked"]:
                self.ctl.config.set(self.SECTION, "suppress_warning", True)

        # ensure we're paused
        self.ctl.vcr_controls.pause()

        # clear graph trace
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        spec.clear_graph()

        # disable Laser Control
        self.ctl.laser_control.set_restriction(self.LASER_CONTROL_DISABLE_REASON)

        self.running = True
        for b in self.buttons:
            self.ctl.gui.colorize_button(b, True)

        # clear existing dark
        self.ctl.dark_feature.clear(quiet=True)
        self.ctl.marquee.info("Collecting Auto-Raman measurement...")

        self.prev_integration_time_ms = self.ctl.integration_time_feature.get_ms()
        self.prev_gain_db = self.ctl.gain_db_feature.get_db()

        # define a TakeOneRequest with AutoRaman enabled
        log.debug("generating AutoRamanRequest")
        auto_raman_request = self.generate_auto_raman_request()
        log.debug(f"AutoRamanRequest {auto_raman_request}")
        take_one_request = TakeOneRequest(auto_raman_request=auto_raman_request)

        self.request_time = datetime.now()
        log.debug("measure_callback: calling take_one.start with AutoRamanRequest {auto_raman_request}")
        self.ctl.take_one.start(completion_callback=self.completion_callback, stop_callback=self.stop_callback, template=take_one_request, save=self.auto_save)

    def generate_auto_raman_request(self):
        return AutoRamanRequest(
            max_ms                  = self.get_max_ms        (),
            start_integ_ms          = self.get_start_integ_ms(), # consider self.ctl.integration_time_feature.get_ms()
            start_gain_db           = self.get_start_gain_db (), # consider self.ctl.gain_db_feature.get_db()
            max_integ_ms            = self.get_max_integ_ms  (),
            min_integ_ms            = self.get_min_integ_ms  (),
            max_gain_db             = self.get_max_gain_db   (),
            min_gain_db             = self.get_min_gain_db   (),
            target_counts           = self.get_target_counts (),
            max_counts              = self.get_max_counts    (),
            min_counts              = self.get_min_counts    (),
            max_factor              = self.get_max_factor    (),
            max_avg                 = self.get_max_avg       (),
            saturation              = self.get_saturation    (),
            drop_factor             = self.get_drop_factor   (),
            laser_warning_delay_sec = self.get_laser_warning_delay_sec(),
            onboard                 = self.get_onboard       ())

    def stop_callback(self):
        self.running = False

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        # this will tell the thread to stop collections and turn off the laser at
        # the end of the current integration
        spec.send_alert("auto_raman_cancel")

        # hide the progress bar
        self.ctl.reading_progress_bar.hide()

        # forcibly disable the laser, regardless of inferred state
        self.ctl.laser_control.set_laser_enable(False)

        # permit manual control of laser 
        self.ctl.laser_control.clear_restriction(self.LASER_CONTROL_DISABLE_REASON)

        # we already cleared the old graph, and leaving it paused with no spectrum
        # would be disquieting, so even though we just hit "Stop", go ahead and
        # resume "Play"
        self.ctl.vcr_controls.play()

        for b in self.buttons:
            self.ctl.gui.colorize_button(b, False)
        self.ctl.marquee.error("Auto-Raman measurement cancelled")

        self.restore_acquisition_parameters()

    def completion_callback(self):
        self.running = False

        if self.request_time:
            elapsed_sec = (datetime.now() - self.request_time).total_seconds()
            self.lb_elapsed.setText(f"{elapsed_sec:.2f}sec")

        self.ctl.laser_control.clear_restriction(self.LASER_CONTROL_DISABLE_REASON)
        for b in self.buttons:
            self.ctl.gui.colorize_button(b, False)

        self.ctl.marquee.info("Auto-Raman measurement complete")

    def process_reading(self, reading):
        spec = self.ctl.multispec.current_spectrometer()
        if spec.device_id != reading.device_id:
            return

        log.debug("processing reading")

        if self.retain_settings:
            log.debug("retaining settings")
            if reading.dark is not None:
                self.ctl.dark_feature.store(reading.dark)
            if reading.new_integration_time_ms is not None:
                self.ctl.integration_time_feature.set_ms(reading.new_integration_time_ms, quiet=True)
            if reading.new_gain_db is not None:
                self.ctl.gain_db_feature.set_db(reading.new_gain_db, quiet=True)
            if reading.sum_count is not None:
                self.ctl.scan_averaging.set_scans_to_average(max(1, reading.sum_count))
        else:
            self.restore_acquisition_parameters()

    def restore_acquisition_parameters(self):
        if self.prev_integration_time_ms is not None:
            self.ctl.integration_time_feature.set_ms(self.prev_integration_time_ms, quiet=True)
        if self.prev_gain_db is not None:
            self.ctl.gain_db_feature.set_db(self.prev_gain_db, quiet=True)
            
    def set_max_ms                 (self, value): self.sb_max_ms                 .setValue(int(value))
    def set_start_integ_ms         (self, value): self.sb_start_integ_ms         .setValue(int(value))
    def set_start_gain_db          (self, value): self.sb_start_gain_db          .setValue(int(value))
    def set_max_integ_ms           (self, value): self.sb_max_integ_ms           .setValue(int(value))
    def set_min_integ_ms           (self, value): self.sb_min_integ_ms           .setValue(int(value))
    def set_max_gain_db            (self, value): self.sb_max_gain_db            .setValue(int(value))
    def set_min_gain_db            (self, value): self.sb_min_gain_db            .setValue(int(value))
    def set_target_counts          (self, value): self.sb_target_counts          .setValue(int(value))
    def set_max_counts             (self, value): self.sb_max_counts             .setValue(int(value))
    def set_min_counts             (self, value): self.sb_min_counts             .setValue(int(value))
    def set_max_factor             (self, value): self.sb_max_factor             .setValue(int(value))
    def set_max_avg                (self, value): self.sb_max_avg                .setValue(int(value))
    def set_saturation             (self, value): self.sb_saturation             .setValue(int(value))
    def set_drop_factor            (self, value): self.ds_drop_factor            .setValue(float(value))
    def set_laser_warning_delay_sec(self, value): self.sb_laser_warning_delay_sec.setValue(int(value))
    def set_onboard                (self, value): self.cb_onboard                .setChecked("true" == value.lower())

    def get_max_ms                 (self): return self.sb_max_ms                 .value()
    def get_start_integ_ms         (self): return self.sb_start_integ_ms         .value()
    def get_start_gain_db          (self): return self.sb_start_gain_db          .value()
    def get_max_integ_ms           (self): return self.sb_max_integ_ms           .value()
    def get_min_integ_ms           (self): return self.sb_min_integ_ms           .value()
    def get_max_gain_db            (self): return self.sb_max_gain_db            .value()
    def get_min_gain_db            (self): return self.sb_min_gain_db            .value()
    def get_target_counts          (self): return self.sb_target_counts          .value()
    def get_max_counts             (self): return self.sb_max_counts             .value()
    def get_min_counts             (self): return self.sb_min_counts             .value()
    def get_max_factor             (self): return self.sb_max_factor             .value()
    def get_max_avg                (self): return self.sb_max_avg                .value()
    def get_saturation             (self): return self.sb_saturation             .value()
    def get_drop_factor            (self): return self.ds_drop_factor            .value()
    def get_laser_warning_delay_sec(self): return self.sb_laser_warning_delay_sec.value()
    def get_onboard                (self): return self.cb_onboard                .isChecked()
