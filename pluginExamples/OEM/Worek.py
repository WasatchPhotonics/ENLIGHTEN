import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import EnlightenPluginBase, EnlightenPluginField, EnlightenPluginResponse, EnlightenPluginConfiguration

log = logging.getLogger(__name__)

"""
HEMO-PLUGIN by s.bee

Currently outputs three labeled scalars using dataframe

TODO: enable-able only in non-Raman mode
    [x] requires PluginWorker connect on main thread
    [x] fixes workaround sleep for error, error msg

TODO: fix graphing bugs
    [ ] graph only shows up sometimes?
    [ ] series_names duplicates
    -- remove need to "declare" series_names

TODO: actually compute the scalars
TODO: actually compute AU/min
    * maintain a history of Absorbance spectra
    * for wavelengths 436nm(ChE activity) & 412nm(Hb)
        - how much did it change in the past minute
            - extrapolate from shorter time interval?
                - results can vary wildly. 
                    - 1AU/1ms -> 60kAU/m
                    - .2AU/1s -> 18AU/m
            - find avg derivative, or simply slope endpoints?
                - might be the same due to IVT

MISC:
linear relationship btwn absorbance and enzyme: (1961)
    rate moles/1.  per min = dA/min / 1.36e4

"Yellow" ~= 578 nm light (1961)

1999 paper is explicit: 436nm (blue) for enzyme activity
546 nm (green) absorption for hemoglobin determination

1999:
hemo = A * 1000/10.8
activity = (sample mE - blank mE) / 10.6
AChE = activity * 1.58e3
activity = (sample mE - blank mE) * 1.58e3 / 10.6 
"""

class Worek(EnlightenPluginBase):

    def __init__(self):
        super().__init__()

        self.sampleTimes = []
        self.ChEActivity = []
        self.HbContent = []

        self.startTime = time.time()

    def get_configuration(self):

        fields = []

        # return a Pandas DataFrame for the GUI table
        fields.append(EnlightenPluginField(
            name        = "Output Levels", 
            datatype    = "pandas", 
            direction   = "output"))

        return EnlightenPluginConfiguration(
            name             = "Worek", 
            fields           = fields,
            is_blocking      = False,
            has_other_graph  = True,
            series_names     = ["ChE Activity", "Hb Content"])

    def connect(self, enlighten_info):
        # if enlighten_info.ctl.page_nav.operation_mode != 4: # 4 = ABSORBANCE
        #     # can be found in log:
        #     # enlighten.Plugins.PluginWorker CRITICAL
        #     # does not interrupt plugin connect tho :/
        #     # must set PluginWorker error message somehow
        #     log.critical("Worek plugin requires Non-Raman>Technique>Absorbance")
        #     raise Exception("Worek plugin requires Non-Raman>Technique>Absorbance")

        super().connect(enlighten_info)
        return True

    def process_request(self, request):
        spectrum = request.processed_reading.processed

        self.sampleTimes.append(time.time() - self.startTime)

        # request.settings.wavelengths (&wavenumbers)
        # provide info about X axis
        """
        if unit == "nm":
            series_x = settings.wavelengths
        elif unit == "cm":
            series_x = settings.wavenumbers
        else:
            series_x = list(range(len(spiky_spectra)))
        """

        self.ChEActivity = spectrum
        self.HbContent.append(0)

        # these quantities are 
        # - Hemoglobin concentration
        # - Enzyme Activity (AChE, BChE)
        # - Erythrocyte AChE
        dataframe = pd.DataFrame( 
            [ -1, -1, -1 ],
            index = ["Hb (µmol/l Hb)", "Activity (µmol/l/min)", "AChE (mU/µmol Hb)"]
        )

        dataframe = dataframe.T
        
        return EnlightenPluginResponse(request,
            series = {
                "ChE Activity" : {
                    "x": np.arange(self.sampleTimes),
                    "y": np.arange(self.ChEActivity)
                },
                "Hb Content" : {
                    "x": np.arange(self.sampleTimes),
                    "y": np.arange(self.HbContent)
                }
            },
            outputs = { 
                "Output Levels": dataframe,        # for table
            })

    def disconnect(self):
        super().disconnect()