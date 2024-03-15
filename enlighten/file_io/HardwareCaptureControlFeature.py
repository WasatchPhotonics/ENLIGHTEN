import logging

log = logging.getLogger(__name__)

class FactoryStripCharts:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.charts = { cfu.checkBox_hardware_live     : cfu.frame_area_scan_live,
                        cfu.checkBox_laser_tec_temp    : cfu.frame_factory_laser_temperature,
                        cfu.checkBox_detector_tec_temp : cfu.frame_factory_detector_temperature }

        for cb, frame in self.charts:
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_visibility)

        self.update_visibility()

    def update_visibility(self):
        for cb, frame in self.charts.items():
            frame.setVisible(cb.isChecked())
