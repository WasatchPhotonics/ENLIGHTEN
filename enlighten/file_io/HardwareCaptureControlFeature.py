
class HardwareCaptureControlFeature:

    def __init__(self,
                 cfu,
                 graph,
                 laser_feature,
                 detector_feature):
        self.cfu = cfu
        self.graph = graph
        self.laser_feature = laser_feature
        self.detector_feature = detector_feature

        self.cb_laser = self.cfu.checkBox_laser_tec_temp
        self.cb_detector = self.cfu.checkBox_detector_tec_temp
        self.cb_live     = self.cfu.checkBox_hardware_live

        self.cb_chart_map = {
            self.cb_laser: self.cfu.frame_hardware_capture_temperatures_laser,
            self.cb_detector: self.cfu.frame_hardware_capture_temperatures_detector,
            self.cb_live: self.cfu.frame_area_scan_live,
            }

        self.cb_laser.setChecked(False)
        self.cb_detector.setChecked(True)
        self.cb_live.setChecked(True)

        self.hide_charts()

        self.cb_laser       .stateChanged   .connect(self.hide_charts)
        self.cb_detector    .stateChanged   .connect(self.hide_charts)
        self.cb_live        .stateChanged   .connect(self.hide_charts)

    def hide_charts(self):
        for key, feature in self.cb_chart_map.items():
            if key.isChecked():
                feature.show()
            else:
                feature.hide()
