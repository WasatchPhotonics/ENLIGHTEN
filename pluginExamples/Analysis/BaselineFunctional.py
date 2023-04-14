import pandas as pd
import numpy as np
import logging

import time

from EnlightenPlugin import *

log = logging.getLogger(__name__)

class BaselineFunctional(EnlightenPluginBase):

    def get_configuration(self):

        self.name = "Baseline"

        self.field(
            name = "wavelength", 
            initial = 1000, minimum = 0, maximum = 10000,
            datatype = "float", direction = "input"
        )
        
        self.field(
            name = "inner radius", 
            initial = 10, minimum = 0, maximum = 10000,
            datatype = "float", direction = "input"
        )

        self.field(
            name = "outer radius", 
            initial = 20, minimum = 0, maximum = 10000,
            datatype = "float", direction = "input"
        )

        self.is_blocking = False
        self.has_other_graph = False

    def process_request(self, request):
        pr = request.processed_reading
        spectrum = pr.get_processed()
        
        wavelength = self.get_widget_from_name("wavelength").value()
        inner_radius = self.get_widget_from_name("inner radius").value()
        outer_radius = self.get_widget_from_name("outer radius").value()

        # TODO: plot wrt to wavelengths (use self.wavelength_to_pixels)

        self.plot(
            title="Wavelength",
            color="red",
            x=[wavelength, wavelength],
            y=[min(spectrum), max(spectrum)]
        )

        self.plot(
            title="Inner Radius",
            color="yellow",
            x=[wavelength-inner_radius, wavelength-inner_radius],
            y=[min(spectrum), max(spectrum)]
        )
        self.plot(
            color="yellow",
            x=[wavelength+inner_radius, wavelength+inner_radius],
            y=[min(spectrum), max(spectrum)]
        )

        self.plot(
            title="Outer Radius",
            color="blue",
            x=[wavelength-outer_radius, wavelength-outer_radius],
            y=[min(spectrum), max(spectrum)]
        )
        self.plot(
            color="blue",
            x=[wavelength+outer_radius, wavelength+outer_radius],
            y=[min(spectrum), max(spectrum)]
        )

        mean_baseline = 0

        self.plot(
            title="Baseline",
            color="orange",
            x=[wavelength-outer_radius, wavelength-inner_radius],
            y=[mean_baseline, mean_baseline]
        )
        self.plot(
            color="orange",
            x=[wavelength+inner_radius, wavelength+outer_radius],
            y=[mean_baseline, mean_baseline]
        )

        self.table = pd.DataFrame( 
            [ mean_baseline ],
            index = ["Baseline"]
        ).T