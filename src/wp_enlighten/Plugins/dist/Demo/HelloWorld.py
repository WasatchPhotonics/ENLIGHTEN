from EnlightenPlugin import EnlightenPluginBase

class HelloWorld(EnlightenPluginBase):
    """ Simplest-possible demonstration plugin. """

    def get_configuration(self):
        self.field(name="Message", direction="output", datatype=str, tooltip="What the plugin outputs")

    def process_request(self, request):
        self.outputs["Message"] = "Hello, World!"
