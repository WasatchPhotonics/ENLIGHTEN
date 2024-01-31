from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginResponse, \
                            EnlightenPluginConfiguration
import logging
import time

log = logging.getLogger(__name__)

##
# This is a simple plugin that zeros every other pixel in the spectrum, taking 
# 3sec to do so.  The purpose is simply to show that the ENLIGHTEN GUI does not
# freeze (remains responsive) while the plugin works.
#
class BlockNullOdd(EnlightenPluginBase):

    def get_configuration(self):
        return EnlightenPluginConfiguration(name            = "Null Odd Px (3 sec)", 
                                            has_other_graph = True, 
                                            is_blocking     = True,
                                            series_names    = ["Long Process Data"])
    def connect(self, enlighten_info):
        return super().connect(enlighten_info)

    def process_request(self, request):
        log.debug(f"received request {request.request_id}")
        spectrum = request.processed_reading.processed
        series = {
            "Long Process Data": [ i if i % 2 == 0 else 0 for i in spectrum ]
        }

        log.debug("waiting 3sec")
        time.sleep(3)

        log.debug("finished processing, sending response")
        return EnlightenPluginResponse(request, series=series)

    def disconnect(self):
        super().disconnect()
