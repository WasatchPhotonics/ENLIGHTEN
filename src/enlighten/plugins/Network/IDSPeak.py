import logging

from EnlightenPlugin import EnlightenPluginBase
from wasatch.DeviceID import DeviceID
from wasatch.IDSCamera import IDSCamera

log = logging.getLogger(__name__)

class IDSPeak(EnlightenPluginBase):
    """
    Tell the Controller to attempt to connect to an IDS camera via the IDSPeak SDK.
    """

    def get_configuration(self):
        self.name = "IDS Peak"
        self.streaming = False
        self.process_requests = False

        choices = IDSCamera.SUPPORTED_CONVERSIONS

        # self.field(name="Connect", direction="input", datatype="button", callback=self.connect_callback, tooltip="Attempt to connect to an IDS camera via the IDSPeak SDK")
        self.field(name="Format Name",direction="input", datatype="combobox", choices=choices, callback=self.format_callback, tooltip="Image format used for vertical binning")
        self.field(name="Start Line", direction="input", datatype=int, initial=0, minimum=0, maximum=1079, callback=self.roi_callback, tooltip="Vertical ROI start line")
        self.field(name="Stop Line",  direction="input", datatype=int, initial=0, minimum=0, maximum=1079, callback=self.roi_callback, tooltip="Vertical ROI stop line")

        device_id = DeviceID(label="IDSPeak")
        log.debug(f"adding to other_device_ids: {device_id}")
        self.ctl.other_device_ids.add(device_id)

    def update_visibility(self):
        """
        Something has happened -- a new spectrometer may have connected -- so update field state.
        """
        log.debug("update_visibility: called")
        spec = self.ctl.current_spectrometer()
        if spec is None:
            log.debug("update_visibility: no spec")
            return

        if "IDSPeak" not in str(spec.device_id):
            self.ctl.marquee.error("IDSPeak plugin can only be used with IDSPeak spectrometers")
            return

        start_line = spec.settings.eeprom.roi_vertical_region_1_start
        stop_line  = spec.settings.eeprom.roi_vertical_region_1_end
        log.debug(f"update_visibility: updating widgets to ({start_line}, {stop_line})")

        self.get_widget_from_name("Start Line").setValue(start_line)
        self.get_widget_from_name("Stop Line") .setValue(stop_line)

    def roi_callback(self):
        spec = self.ctl.current_spectrometer()
        if spec is None:
            return

        start_line = int(self.get_widget_from_name("Start Line").value())
        stop_line  = int(self.get_widget_from_name("Stop Line") .value())

        if start_line >= stop_line or start_line < 0 or stop_line > 1079:
            log.debug(f"invalid range: ({start_line}, {stop_line})")
            return

        spec.settings.eeprom.roi_vertical_region_1_start = start_line
        spec.settings.eeprom.roi_vertical_region_1_end   = stop_line
        spec.change_device_setting("vertical_binning", (start_line, stop_line))
        
    def format_callback(self):
        spec = self.ctl.current_spectrometer()
        if spec is None:
            return

        if "IDSPeak" not in str(spec.device_id):
            self.ctl.marquee.error("IDSPeak plugin can only be used with IDSPeak spectrometers")
            return

        format_name = self.get_widget_from_name("Format Name").currentText()
        spec.change_device_setting("output_format_name", format_name)
