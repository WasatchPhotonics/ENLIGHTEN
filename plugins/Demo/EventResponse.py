import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginResponse, \
                            EnlightenPluginField,     \
                            EnlightenPluginRequest,    \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

class EventResponse(EnlightenPluginBase):

    def __init__(self, ctl):
        super().__init__(ctl)
        self.event_count = 0
        self.events = []

    def get_event_responses(self):
        return self.events

    def clear_event_responses(self):
        self.events.clear()

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(
            name = "test callback",
            datatype="button",
            callback = self.callback
            ))
        fields.append(EnlightenPluginField(name="callback verify", direction="output", datatype=int, 
            initial=0, 
            tooltip="What the plugin outputs"))

        return EnlightenPluginConfiguration(name            = "Event Response", 
                                            streaming       = True,
                                            fields          = fields)
    def connect(self, enlighten_info):
        self.app_info = enlighten_info
        return super().connect(enlighten_info)

    def process_request(self, request):
        return EnlightenPluginResponse(request)

    def callback(self):
        self.event_count += 1
        log.debug(f"clipboard measure is {self.app_info.read_measurements()}")
        response = EnlightenPluginResponse(EnlightenPluginRequest(),
                                           outputs={"callback verify": self.event_count})
        self.events.append(response)

    def disconnect(self):
        super().disconnect()
