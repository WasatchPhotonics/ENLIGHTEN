import logging
import datetime
import pyqtgraph

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class LaserTemperatureFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        self.lb_widget      = cfu.label_laser_tec_mode
        self.combo_mode     = cfu.comboBox_laser_tec_mode

        self.ctl.page_nav.register_observer(self.update_visibility, "mode")

        self.combo_mode  .currentIndexChanged .connect(self.combo_callback)

        self.strip_chart = self.ctl.strip_charts.create_chart(name="Laser Temperature", y_unit="Celsius (°C)", fmt="%.2f%%", warn_hi=36)

        self.update_visibility()

    def init_hotplug(self):
        log.debug("init_hotplug: start")
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        if spec.settings.is_xs() and spec.settings.eeprom.sig_laser_tec:
            self.combo_mode.blockSignals(True)
            log.debug(f"init_hotplug: setting index to {spec.settings.state.laser_tec_mode}")
            self.combo_mode.setCurrentIndex(spec.settings.state.laser_tec_mode)
            self.combo_mode.blockSignals(False)

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        visible = spec is not None and spec.settings.eeprom.sig_laser_tec and self.ctl.page_nav.doing_expert()

        for widget in [ self.combo_mode, self.lb_widget ]:
            widget.setVisible(visible)

        self.strip_chart.set_visible(visible)

    def combo_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec and spec.settings.is_xs() and spec.settings.eeprom.sig_laser_tec:
            self.ctl.multispec.change_device_setting("set_laser_tec_mode", self.combo_mode.currentIndex())

    def notify(self, spec, s):
        """ if selected spectrometer, displays on Factory and sends to observers """
        if spec != self.ctl.multispec.current_spectrometer():
            return

        self.notify_observers_with_value(s)

    def process_reading(self, spec, reading):
        if spec is None:
            return self.notify(spec, "disconnected")

        if spec.settings.eeprom.format <= 12:
            return self.notify(spec, "ambient")

        if not spec.settings.eeprom.sig_laser_tec:
            return self.notify(spec, "ambient")

        if not reading.laser_tec_enabled:
            return self.notify(spec, "disabled")
            
        app_state = spec.app_state
        degC = reading.laser_temperature_degC
        if degC is None:
            return

        self.strip_chart.add_value(degC)

        self.notify(spec, f"{degC:-.2f} °C")
