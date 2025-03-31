import logging

from EnlightenPlugin import EnlightenPluginBase
from wasatch.DeviceID import DeviceID

log = logging.getLogger(__name__)

class IDSPeak(EnlightenPluginBase):
    """
    Tell the Controller to attempt to connect to an IDS camera via the IDSPeak SDK.
    """

    def get_configuration(self):
        self.name = "IDS Peak"
        self.streaming = False
        self.process_requests = False

        self.field(name="Connect", direction="input", datatype="button", callback=self.connect_callback, tooltip="Attempt to connect to an IDS camera via the IDSPeak SDK")

    def connect_callback(self):
        device_id = DeviceID(label="IDSPeak")
        log.debug(f"adding to other_device_ids: {device_id}")
        self.ctl.other_device_ids.add(device_id)
