from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginResponse, \
                            EnlightenPluginField,     \
                            EnlightenPluginConfiguration

class HelloWorldPlugin(EnlightenPluginBase):

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(name="Greeting", direction="output", datatype=str, 
            initial="None", 
            tooltip="What the plugin outputs"))

        return EnlightenPluginConfiguration(name            = "Hello Plugin", 
                                            streaming       = False,
                                            fields          = fields)
    def connect(self):
        return super().connect()

    def process_request(self, request):
        outputs = {
            "Greeting" : "Hello World"
            }
        return EnlightenPluginResponse(request, outputs=outputs)

    def disconnect(self):
        super().disconnect()
