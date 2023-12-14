import os
import logging
import datetime

from enlighten import common

log = logging.getLogger(__name__)

class HardwareFileOutputManager:

    def __init__(self, ctl):
        self.ctl = ctl
        sfu = ctl.form.ui

        self.features = []
        self.file_map = {}

        self.cb_output = sfu.checkBox_feature_file_capture
        self.spin_timeout = sfu.spinBox_hardware_capture_timeout

        self.output_timeout = None
        
        self.cb_output.toggled.connect(self.cb_callback)

    def cb_callback(self):
        if self.cb_output.isChecked():
            self.enable_output()
        else:
            self.disable_output()

    def register_feature(self, feature_obj):
        self.features.append(feature_obj)

    def enable_output(self):
        current_time = datetime.datetime.now()
        time_info = f"{current_time.isoformat(sep='-',timespec='hours')}-{current_time.minute}-{current_time.second}-"
        self.hardware_dir = os.path.join(common.get_default_data_dir(), "hardware_captures", f"{time_info}hardware_capture")
        timeout = self.spin_timeout.value()
        if timeout != 0:
            delta = datetime.timedelta(minutes=timeout)
            self.output_timeout = datetime.datetime.now() + delta
        os.makedirs(self.hardware_dir)
        for feature in self.features:
            file_name = f"{time_info}" + feature.name + ".csv"
            feature_file = os.path.join(self.hardware_dir, file_name)
            feature_file_obj = open(feature_file, 'w')
            self.file_map[feature.name] = feature_file_obj
            feature.output_to_file = True

    def write_line(self, feature_name, value):
        file_obj = self.file_map.get(feature_name, None)
        if file_obj == None:
            log.error("Passed feature to write to file that does not exist")
            return
        file_obj.write(value)
        file_obj.write('\n')
        if self.output_timeout != None and self.output_timeout < datetime.datetime.now():
            self.disable_output()
            self.cb_output.setChecked(False)

    def disable_output(self):
        self.output_timeout = None
        for file_obj in self.file_map.values():
            file_obj.close()
        self.file_map.clear()

        for feature in self.features:
            feature.output_to_file = False
