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
        self.field(name="Vertical Binning", direction="input", datatype="combobox", choices=choices, callback=self.format_callback, tooltip="Image format used for vertical binning")
        self.field(name="Area Scan", direction="input", datatype="combobox", choices=choices, callback=self.format_callback, tooltip="Image format used for area scan")

        device_id = DeviceID(label="IDSPeak")
        log.debug(f"adding to other_device_ids: {device_id}")
        self.ctl.other_device_ids.add(device_id)

    def format_callback(self):
        spec = self.ctl.current_spectrometer()
        if spec is None:
            return

        if "IDSPeak" not in str(spec.device_id):
            self.ctl.marquee.error("IDSPeak plugin can only be used with IDSPeak spectrometers")
            return

        vert_name = self.get_widget_from_name("Vertical Binning").currentText()
        area_name = self.get_widget_from_name("Area Scan").currentText()

        spec.change_device_setting("vertical_binning_format_name", vert_name)
        spec.change_device_setting("area_scan_format_name", area_name)
