import pandas as pd
import numpy as np
import logging

from EnlightenPlugin import EnlightenPluginBase,        \
                            EnlightenPluginField,       \
                            EnlightenPluginResponse,    \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

"""
HEMO-PLUGIN by s.bee

Currently outputs three labeled scalars using dataframe

TODO: enable-able only in non-Raman mode
TODO: actually compute the scalars
TODO: actually compute AU/min
    * maintain a history of Absorbance spectra
    * for each wavelength:  
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
        self.time = 0

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
            series_names     = ['AU/min'])

    def connect(self, enlighten_info):
        super().connect(enlighten_info)
        return True

    def process_request(self, request):
        spectrum = request.processed_reading.processed
        self.time += 1

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
                "AU/min" : np.arange(1000)
            },
            outputs = { 
                "Output Levels": dataframe,        # for table
            })

    def disconnect(self):
        super().disconnect()