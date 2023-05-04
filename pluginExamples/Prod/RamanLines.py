import os
import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginDependency, \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# A simple plug-in to add Raman lines from common test samples to the current 
# spectra.  The lines displayed are limited to those appearing within the current
# spectrometer's configured wavenumber calibration.  Lines are scaled to the 
# current spectrum, and relative intensities are roughly set to approximate
# typical appearance.
class RamanLines(EnlightenPluginBase):

    MIN_REL_INTENSITY = 0.2

    def __init__(self, ctl):
        super().__init__(ctl)
        self.samples = self.get_samples()

    def get_configuration(self):
        fields = []

        # These would be better as a single drop-down combo box, but we haven't 
        # yet added that as a supported plugin input type.
        for sample in self.samples:
            fields.append(EnlightenPluginField(name=sample, direction="input", datatype=bool, initial=False))
        return EnlightenPluginConfiguration(
            name            = "RamanLines", 
            series_names    = sorted(self.samples.keys()),
            fields          = fields)

    def connect(self, enlighten_info):
        super().connect(enlighten_info)
        return True

    def disconnect(self):
        super().disconnect()

    def process_request(self, request):
        pr = request.processed_reading
        settings = request.settings

        series_data = {}
        for sample in self.samples:
            if request.fields[sample]:
                series_data[sample] = self.generate_series(sample=sample, wavenumbers=settings.wavenumbers, spectrum=pr.processed)

        return EnlightenPluginResponse(request=request, series=series_data)      

    ## 
    # Generate a synthetic spectrum, bounded in x to match the specified x-axis 
    # in wavenumbers, bounded in y to match the min/max of the specified 
    # spectrum, of the specified sample's Raman lines.
    def generate_series(self, sample, wavenumbers, spectrum):
        
        if wavenumbers is None or len(wavenumbers) == 0:
            return []

        # determine the vertical extent of the synthetic spectrum
        lo = min(spectrum)
        hi = max(spectrum)

        # determine which of this sample's Raman lines to visualize on the graph
        lines = self.samples[sample]
        visible = []
        max_rel_intensity = self.MIN_REL_INTENSITY
        for peak in sorted(lines.keys()):
            rel_intensity = lines[peak]
            if peak >= wavenumbers[0] and peak <= wavenumbers[-1]:
                visible.append(peak)
                max_rel_intensity = max(max_rel_intensity, rel_intensity)

        series_x = [ wavenumbers[0] ]
        series_y = [ lo ]

        log.debug(f"displaying {len(visible)} {sample} peaks")
        for x in visible:
            rel_intensity = max(lines[x], self.MIN_REL_INTENSITY)
            y = lo + (hi - lo) * rel_intensity / max_rel_intensity
            series_x.extend((x - 0.1,  x, x + 0.1))
            series_y.extend((lo,       y,      lo))

        series_x.append(wavenumbers[-1])
        series_y.append(lo)

        return { "x": series_x, "y": series_y }

    def get_samples(self):
        """
        @see https://www.chem.ualberta.ca/~mccreery/ramanmaterials.html
        """
        return {
            "Acetaminophen": {
                390.9: 3,
                651.6: 3,
                857.9: 3,
                1168.5: 3,
                1236.8: 3,
                1323.9: 3,
                1371.5: 3,
                1561.5: 3,
                1648.4: 3,
                2931.1: 3,
                3064.6: 3
            },

            "Air": {
                1552.9: 3, # O2
                2328.4: 3, # N2
            },

            "Aspirin": {
                322: 3,
                424: 3,
                549: 3,
                639: 3,
                703: 3,
                749: 3,
                784: 3,
                1042: 3,
                1053: 3,
                1190: 3,
                1258: 3
            },

            "Benzonitrile": {
                450.9: 1,
                548.5: 1,
                751.3: 1,
                767.1: 1,
                1000.7: 5,
                1026.6: 1,
                1177.9: 2,
                1192.6: 2,
                1598.9: 3,
                2229.4: 4,
                3072.3: 2
            },

            "Cyclohexane": {
                801.3: 5,
                1028.3: 3,
                1157.6: 2,
                1266.4: 3,
                1444.4: 3,
                2664.4: 3,
                2852.9: 5,
                2923.8: 3,
                2938.3: 4 
            },

            "Delrin": {
                540: 3,
                920: 3
            },

            "Ethanol": {
                430: 3,
                880: 5,
                1055: 3,
                1090: 3,
                1280: 3,
                1460: 3
            },

            "IPA": {
                653: 3,
                847: 3,
                880: 3,
                1033: 1,
                1085: 3
            },

            "Polystyrene": {
                620.9: 3,
                795.8: 1, 
                1001.4: 5,
                1031.8: 3,
                1155.3: 1,
                1450.5: 1,
                1583.1: 1,
                1602.3: 3,
                2852.4: 1,
                2904.5: 2,
                3054.3: 3
            },

            "Sulfur": {
                153.8: 3,
                219.1: 5,
                473.2: 3
            },

            "Teflon": {
                292: 4,
                385: 3,
                734: 5,
                1218: 1, 
                1302: 2,
                1382: 3
            },

            "Toluene+Acetonitrile": {
                521.7: 1,
                786.5: 3,
                919.0: 1,
                1003.6: 5,
                1030.6: 2,
                1211.4: 1,
                1605.1: 1,
                2253.7: 4,
                2292.6: 1,
                2940.8: 4,
                3057.1: 3
            }
        }
