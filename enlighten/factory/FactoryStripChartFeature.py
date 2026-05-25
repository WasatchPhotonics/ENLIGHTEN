import logging

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class FactoryStripChartFeature(EnlightenFeature):
    """
    This class manages the set of strip-charts on the Factory View which graph 
    device characteristics against a time axis.
    """

    def __init__(self, ctl):
        super().__init__(ctl)

        cfu = ctl.form.ui

        # MZ: why is hardware_live here? 
        self.charts = { cfu.checkBox_hardware_live     : cfu.frame_area_scan_live,
                        cfu.checkBox_laser_tec_temp    : cfu.frame_factory_laser_temperature,
                        cfu.checkBox_detector_tec_temp : cfu.frame_factory_detector_temperature }

        for cb, frame in self.charts.items():
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_visibility)

        self.update_visibility()

    def update_visibility(self):
        for cb, frame in self.charts.items():
            frame.setVisible(cb.isChecked())
