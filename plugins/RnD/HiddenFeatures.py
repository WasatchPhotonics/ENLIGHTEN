import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class HiddenFeatures(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "Hidden Features"
        self.streaming = False
        self.process_requests = False

        self.field(name="Averaging",  direction="input", datatype=int, initial=   1, minimum=1, maximum= 255, callback=self.averaging_callback, tooltip="Onboard scans to average")
        self.field(name="Start Line", direction="input", datatype=int, initial=   0, minimum=0, maximum=1079, callback=self.vertical_roi_callback, tooltip="Vertical ROI")
        self.field(name="Stop Line",  direction="input", datatype=int, initial=1079, minimum=0, maximum=1079, callback=self.vertical_roi_callback, tooltip="Vertical ROI")

    def averaging_callback(self):
        spec = self.ctl.current_spectrometer()
        if spec is None:
            return

        n = int(self.get_widget_from_name("Averaging").value())
        spec.settings.state.scans_to_average = n
        spec.change_device_setting("scans_to_average", n)

    def vertical_roi_callback(self):
        spec = self.ctl.current_spectrometer()
        if spec is None:
            return

        start = int(self.get_widget_from_name("Start Line").value())
        stop  = int(self.get_widget_from_name("Stop Line" ).value())
        roi = (start, stop)

        spec.settings.eeprom.roi_vertical_region_1_start = start
        spec.settings.eeprom.roi_vertical_region_1_end   = stop
        spec.change_device_setting("vertical_roi", roi)
