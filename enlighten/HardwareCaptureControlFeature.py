
class HardwareCaptureControlFeature:

    def __init__(self,
                 sfu,
                 graph,
                 laser_feature,
                 detector_feature):
        self.sfu = sfu
        self.graph = graph
        self.laser_feature = laser_feature
        self.detector_feature = detector_feature

        self.cb_laser = self.sfu.checkBox_laser_tec_temp
        self.cb_detector = self.sfu.checkBox_detector_tec_temp
        self.cb_live     = self.sfu.checkBox_hardware_live

        self.cb_chart_map = {
            self.cb_laser: self.sfu.frame_hardware_capture_temperatures_laser,
            self.cb_detector: self.sfu.frame_hardware_capture_temperatures_detector,
            self.cb_live: self.sfu.frame_area_scan_live,
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
