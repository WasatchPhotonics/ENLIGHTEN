import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# This writes received spectra into a custom folder with a different
# file format than ENLIGHTEN.
class LoadHook(EnlightenPluginBase):

    def __init__(self, ctl):
        super().__init__(ctl)

        self.notice_status = 0
        self.basename = "load_hook"

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(
            name        = "Load Notice", 
            datatype    = "int", 
            direction   = "output"))

        return EnlightenPluginConfiguration(
            name        = "Load Hook", 
            fields      = fields,
            events      = { "load": self.load_notice }, 
            streaming   = True,               
            is_blocking = False)

    def connect(self, enlighten_info):
        super().connect(enlighten_info)
        self.notice_status = 0
        return True

    # This is the default process_request method that all ENLIGHTEN plug-ins have.
    # It receives EnlightenPluginRequests, as normal.
    def process_request(self, request):

        return EnlightenPluginResponse(request,
                                       outputs = {"Load Notice": self.notice_status})

    def disconnect(self):
        super().disconnect()

    def load_notice(self, measurement):
        self.notice_status += 1
