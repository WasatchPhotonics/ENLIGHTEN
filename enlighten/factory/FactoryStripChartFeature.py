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

        # MZ: why is hardware_live here? should be:
        #
        # - detector temperature
        # - laser temperature
        # - µC temperature
        # - battery charge level
        # - battery temperature
        # - battery IC temperature

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

class StripChart:
    """
    Each of these should instantiate and own:

    - a name
    - a checkbox to log data to a file
    - a checkbox to display the chart
    - a plot to graph the value over time
    - a clipboard icon to copy data to the system clipboard
    - potentially, warn_hi and warn_lo thresholds to colorize
    """
    
    def __init__(self, name):

        self.name = name
        self.plot = None
        self.bt_clipboard = None
        self.cb_append_to_file = None
        self.warn_lo = None
        self.warn_hi = None
        self.window_sec = 180

