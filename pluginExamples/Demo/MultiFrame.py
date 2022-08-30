import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginResponse, \
                            EnlightenPluginField,     \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

class MultiFrame(EnlightenPluginBase):

    def __init__(self):
        super().__init__()

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(name="Greeting", direction="output", datatype=str, 
            initial="None", 
            tooltip="What the plugin outputs"))

        return EnlightenPluginConfiguration(name            = "Hello Plugin", 
                                            streaming       = False,
        # Field Names must be unique
        # They are returned as a flat list, not by page
                                            fields          = {"test":fields, "test2":[]})
    def connect(self, enlighten_info):
        return super().connect(enlighten_info)

    def process_request(self, request):
        log.debug(f"for multi page fields are {request.fields}")
        outputs = {
            "Greeting" : "Hello World"
            }
        return EnlightenPluginResponse(request, outputs=outputs)

    def disconnect(self):
        super().disconnect()
