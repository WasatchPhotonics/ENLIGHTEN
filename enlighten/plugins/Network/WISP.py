import logging

from EnlightenPlugin import EnlightenPluginBase
from wasatch.DeviceID import DeviceID

log = logging.getLogger(__name__)

class WISP(EnlightenPluginBase):
    """
    All this does is take the provided IP address and add it to the Controller's
    existing WasatchBus object responsible for periodically polling for new 
    spectrometers.

    @todo persist previous addresses in Configuration and auto-add them to TCPBus
          for polling.
    """

    def get_configuration(self):
        self.name = "WISP"
        self.streaming = False
        self.process_requests = False

        self.field(name="Address", direction="input", datatype=str, initial="192.168.1.248", tooltip="IPv4 address of network spectrometer, e.g. 192.168.1.100")
        self.field(name="Port",    direction="input", datatype=int, minimum=1025, initial=9999, maximum=65535, tooltip="IPv4 port")
        self.field(name="Connect", direction="input", datatype="button", callback=self.connect_callback, tooltip="Connect to specified spectrometer")

    def connect_callback(self):
        addr = self.get_plugin_field("Address").field_value
        port = self.get_plugin_field("Port").field_value

        # self.ctl.bus.tcp_bus.add_addr(addr)

        device_id = DeviceID(label=f"TCP:{addr}:{port}")
        log.debug(f"adding to other_device_ids: {device_id}")
        self.ctl.other_device_ids.add(device_id)
