from EnlightenPlugin import EnlightenPluginBase

import logging
log = logging.getLogger(__name__)

class RamanLines(EnlightenPluginBase):
    """
    A simple plug-in to add Raman lines from common test samples to the current 
    spectra.  The lines displayed are limited to those appearing within the current
    spectrometer's configured wavecal and ROI.  Lines are scaled to the 
    current spectrum, and relative intensities are roughly set to approximate
    typical appearance against common transmission curves.
    """
    MIN_REL_INTENSITY = 0.2

    def get_configuration(self):
        """
        These would be better as a single drop-down combo box, but we haven't 
        yet added that as a supported plugin input type.
        """
        self.name = "Raman Lines"
        self.samples = self.get_samples()
        self.field(name="sample", direction="input", datatype="combobox", choices=[k for k, v in self.samples.items()])

    def process_request(self, request):
        unit = self.ctl.graph.get_x_axis_unit()
        if unit != "cm":
            self.marquee_message = "Error: RamanLines requires wavenumber axis"
            return

        sample = request.fields["sample"]
        if sample in self.samples:
            for p in self.generate_points(sample=sample):
                self.plot(title = f"{sample} {p[0]:7.03f}cm⁻¹",
                          x = [p[0], p[0]],
                          y = [min(self.spectrum), p[1]])

    def generate_points(self, sample):
        """
        Generate Raman lines as a list of (x, y) tuples, where x is the Raman shift
        in wavenumbers and y is the relative intensity scaled to the current 
        spectrum, cropping to only those points visible within the horizontal ROI.
        """
        wavenumbers = self.settings.wavenumbers

        lft = wavenumbers[0]
        rgt = wavenumbers[-1]
        roi = self.settings.eeprom.get_horizontal_roi()
        if roi:
            lft = wavenumbers[roi.start]
            rgt = wavenumbers[roi.end]

        # determine the vertical extent of the synthetic spectrum
        lo = min(self.spectrum)
        hi = max(self.spectrum)

        # determine which peaks should be visible
        peaks = self.samples[sample]
        visible = []
        max_rel_intensity = self.MIN_REL_INTENSITY
        for peak in sorted(peaks.keys()):
            if peak >= lft and peak <= rgt:
                visible.append(peak)
                max_rel_intensity = max(max_rel_intensity, peaks[peak])

        # scale peaks to current spectrum
        points = []
        for x in visible:
            rel_intensity = max(peaks[x], self.MIN_REL_INTENSITY)
            y = lo + (hi - lo) * rel_intensity / max_rel_intensity
            points.append( (x, y) )

        return points

    def get_samples(self):
        """
        @see https://www.chem.ualberta.ca/~mccreery/ramanmaterials.html
        """
        return {
            # note, synonym for 4-Acetamidophenol and Paracetamol
            "Acetaminophen": {
                 213.3: 1,
                 329.2: 1,
                 390.9: 2,
                 465.1: 1,
                 504.0: 1,
                 651.6: 2,
                 710.8: 1,
                 797.2: 2,
                 834.5: 5,
                 857.9: 3,
                 968.7: 1,
                1105.5: 1,
                1168.5: 3,
                1236.8: 3,
                1278.5: 2,
                1323.9: 4,
                1371.5: 2,
                1515.1: 1,
                1561.6: 2,
                1648.4: 3,
                2931.1: 2,
                3064.6: 2,
                3102.4: 2,
                3326.6: 1
            },

            "Acetone": {
                788: 4,
                1067.4: 2,
                1222.8: 2,
                1440: 3,    # 1430.5?
                1727: 2,    # 1711?
                2920: 5     # unverified
            },

            "Acetonitrile": {
                378.5: 1,
                919.0: 2,
                2253.7: 4,
                2292.6: 1,
                2940.8: 5
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

            "Calcium Carbonate": {
                280: 2,
                712: 1,
                1085: 5 # EU Pharmacopoeia
            },

            "Cyclohexane": {
                384.1: 1,
                426.3: 1,
                801.3: 5,
                1028.3: 2,
                1157.6: 0.5,
                1266.4: 1.5,
                1444.4: 1,
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

            "Methanol": {
                1060: 3,
                1481: 2,
                2840: 4,
                2950: 5
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

            "Silicon": {
                521: 5
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

            "Toluene": {
                521.7: 1,
                786.5: 3,
                1003.6: 5,
                1030.6: 2,
                1211.4: 1,
                1605.1: 1,
                3057.1: 3
            },

            "Toluene+Acetonitrile": {
                378.5: 1,
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
