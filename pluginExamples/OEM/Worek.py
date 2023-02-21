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
    [x] graph only shows up sometimes?
        - forgot to "enable"!
    [x] series_names duplicates
        - seems to be caused by bad series_name declarations
    [ ] add clear graph button

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

def remap(x, srcA, srcB, destA, destB):
    i = (x-srcA)/(srcB-srcA)
    return destA + int((destB - destA)*i)

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
            series_names     = ["ChE Activity", "Hb Content"],
            x_axis_label = "time (sec)")

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

        # remap wavelengths from codomain to domain of settings.wavelength (linear fn: pix->nm)
        pixel_412nm = remap(912, request.settings.wavelengths[0], request.settings.wavelengths[-1], 0, len(request.settings.wavelengths))
        pixel_436nm = remap(1014, request.settings.wavelengths[0], request.settings.wavelengths[-1], 0, len(request.settings.wavelengths))

        self.ChEActivity.append(spectrum[pixel_436nm])
        self.HbContent.append(spectrum[pixel_412nm])

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
                    "x": np.array(self.sampleTimes),
                    "y": np.array(self.ChEActivity)
                },
                "Hb Content" : {
                    "x": np.array(self.sampleTimes),
                    "y": np.array(self.HbContent)
                }
            },
            outputs = { 
                "Output Levels": dataframe,        # for table
            })

    def disconnect(self):
        super().disconnect()