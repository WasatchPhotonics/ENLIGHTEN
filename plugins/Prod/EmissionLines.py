from EnlightenPlugin import EnlightenPluginBase

import logging
log = logging.getLogger(__name__)

class EmissionLines(EnlightenPluginBase):
    """
    A simple plug-in to add emission lines from standard gas lamps to the current
    spectra.  The lines displayed are limited to those appearing within the current
    spectrometer's configured wavelength calibration.  Lines are scaled to the
    current spectrum, and relative intensities are roughly set to approximate
    typical appearance.
    """
    MIN_REL_INTENSITY = 0.2

    def get_configuration(self):
        """
        These would be better as a single drop-down combo box, but we haven't
        yet added that as a supported plugin input type.
        """
        self.name = "Emission Lines"
        self.auto_enable = True

        self.lamps = self.get_lamps()
        self.field(name="lamp", direction="input", datatype="combobox", choices=[k for k, v in self.lamps.items()])

    def process_request(self, request):
        unit = self.ctl.graph.get_x_axis_unit()
        if unit != "nm":
            self.marquee_message = "Error: EmissionLines requires wavelength axis"
            return

        lamp = request.fields["lamp"]
        if lamp in self.lamps:
            for p in self.generate_points(lamp=lamp):
                self.plot(
                    title = f"{lamp} {p[0]:7.03f}cm⁻¹",
                    x = [p[0], p[0]],
                    y = [min(self.spectrum), p[1]]
                )

    def generate_points(self, lamp):
        """
        Generate a synthetic spectrum, bounded in x to match the specified x-axis
        in wavelengths, bounded in y to match the min/max of the specified
        spectrum, of the specified lamp's emission lines.
        """

        if self.settings.eeprom.has_horizontal_roi():
            roi = self.settings.eeprom.get_horizontal_roi()
            start = roi.start
            end = roi.end
        else:
            start = 0
            end = -1

        wavelengths = self.settings.wavelengths
        x_lo = wavelengths[start]
        x_hi = wavelengths[end]

        # determine the vertical extent of the synthetic spectrum
        y_lo = min(self.spectrum[start:end])
        y_hi = max(self.spectrum[start:end])

        # determine which of this lamp's emission lines to visualize on the graph
        lines = self.lamps[lamp]
        visible = []
        max_rel_intensity = self.MIN_REL_INTENSITY
        for peak in sorted(lines.keys()):
            rel_intensity = lines[peak]
            if peak >= x_lo and peak <= x_hi:
                visible.append(peak)
                max_rel_intensity = max(max_rel_intensity, rel_intensity)

        points = []
        for x in visible:
            rel_intensity = max(lines[x], self.MIN_REL_INTENSITY)
            y = y_lo + (y_hi - y_lo) * rel_intensity / max_rel_intensity
            points.append((x, y))

        return points

    def get_lamps(self):
        """
        Emission lines with relative intensities of 0 appear in literature, but are
        either unverified or hard to see with our spectrometers in empirical usage.

        Relative intensity will realistically vary by model, but these values are a
        reasonable starting point.

        @todo for completeness add He, Rn

        @par Sources

        Data taken from NIST, as well as calibration lamp vendor websites.

        @see https://physics.nist.gov/PhysRefData/ASD/lines_form.html
        @see https://www.oceaninsight.com/products/light-sources/calibration-sources/wavelength-calibration-sources/

        @returns dict of emission lamp sources (Argon etc), each containing a 
                 dict of wavelength with relative intensity (relative to other 
                 lines of the same element)
        """
        return {
            "Ar": {
                 329.3640: 1,
                 330.7228: 1,
                 335.0924: 1,
                 337.6436: 1,
                 338.8531: 1,
                 415.8590: 1,
                 418.1884: 1,
                 420.0674: 1,
                 423.7220: 1,
                 427.7528: 1,
                 430.0650: 1,
                 434.8064: 1,
                 440.0986: 1,
                 442.6001: 1,
                 444.8879: 1,
                 448.1811: 1,
                 451.0733: 1,
                 454.5052: 1,
                 457.9350: 1,
                 458.9898: 1,
                 460.9567: 1,
                 465.7901: 1,
                 472.6868: 1,
                 476.4865: 1,
                 560.6733: 1,
                 565.0704: 1,
                 573.9520: 1,
                 591.2085: 1,
                 603.2127: 1,
                 617.2278: 1,
                 696.5431: 5,
                 706.7218: 3,
                 714.7042: 1,
                 727.2936: 2,
                 738.3980: 3,
                 750.3869: 4,
                 763.5106: 4,
                 794.8176: 1,

                 794.8176: 1,
                 800.616:  1,
                 801.479:  1,
                 810.3693: 2,
                 811.5311: 4,
                 826.4522: 3,
                 840.8210: 3,
                 842.4648: 5,
                 852.1442: 2,
                 866.7944: 1,
                 912.2967: 9,
                 922.4499: 2,

                 935.4220: 1,
                 965.7786: 1,
                 978.4503: 1,
                1047.0054: 1,
                1067.3565: 1,
                1148.8109: 1,
                1166.8710: 1,
                1171.9488: 1,
                1211.2326: 1,
                1213.9738: 1,
                1234.3393: 1,
                1240.2827: 1,
                1243.9321: 1,
                1248.7663: 1,
                1270.2281: 1,
                1273.3418: 1,
                1280.2739: 1,
                1295.6659: 1,
                1300.8264: 1,
                1327.2640: 1,
                1336.7111: 1,
                1350.4191: 1,
                1371.8577: 1,
                1399.9890: 1,
                1409.3640: 1,
                1504.6500: 1,
                1656.0460: 1
            },
            "Hg": {
                 253.652: 0,
                 296.728: 0,
                 302.150: 0,
                 313.155: 0,
                 334.148: 0,
                 365.015: 0,
                 404.656: 1,
                 435.833: 1,
                 546.074: 5,
                 576.960: 1,
                 579.066: 1,
                 696.543: 1,
                 706.722: 1,
                 714.704: 1,
                 727.294: 1,
                 738.398: 1,
                 750.387: 2,
                 763.511: 5,
                 772.376: 2,
                 794.818: 1,
                 800.616: 2,
                 811.531: 4,
                 826.452: 3,
                 842.465: 3,
                 852.144: 1,
                 866.794: 1,
                 912.297: 5,
                 922.450: 1,
                 965.779: 1,
                 978.450: 1,
                1013.976: 1,
            },
            "Kr":  {
                 427.397: 2,
                 428.297: .5,
                 431.958: 3,
                 436.264: .5,
                 437.612: 1,
                 439.997: 1,
                 445.392: .7,
                 446.369: 1.5,
                 450.235: 1,
                 556.222: 3.8,
                 557.029: 4,
                 587.092: 5,
                 758.741: 1,
                 760.155: 10,
                 768.525: 8,
                 769.454: 9,
                 785.482: 7,
                 791.343: 1,
                 805.950: 1,
                 810.437: 1,
                 811.290: 1,
                 819.006: 1,
                 826.324: 1,
                 829.811: 1,
                 850.887: 1,
                 877.675: 1,
                 892.869: 1,
                1181.938: 0,
                1220.353: 0,
                1317.741: 0,
                1363.422: 0,
                1442.679: 0,
                1473.444: 0,
                1520.310: 0,
                1537.204: 0,
                1620.872: 0,
                1689.044: 0,
                1755.350: 0,
                1785.738: 0,
                1800.223: 0,
                1816.732: 0,
            },
            "Ne": {
                 341.790: 0,
                 342.391: 0,
                 344.770: 0,
                 345.076: 0,
                 345.419: 0,
                 346.052: 0,
                 346.658: 0,
                 347.257: 0,
                 349.806: 0,
                 350.121: 0,
                 351.519: 0,
                 352.047: 0,
                 359.353: 0,
                 360.017: 0,
                 363.366: 0,
                 368.573: 0,
                 370.122: 0,
                 503.135: 0,
                 503.775: 0,
                 508.038: 0,
                 511.367: 0,
                 511.650: 0,
                 540.056: 1,
                 576.441: 1,
                 582.015: 1,
                 585.249: 2,
                 588.189: 1,
                 594.483: 2,
                 597.553: 1,
                 603.000: 1,
                 607.433: 2,
                 609.616: 3,
                 612.884: 1,
                 614.306: 4,
                 616.359: 2,
                 621.728: 2,
                 626.649: 3,
                 630.479: 2,
                 633.442: 3,
                 638.299: 5,
                 640.225: 6,
                 650.653: 4,
                 653.288: 3,
                 659.895: 3,
                 667.828: 4,
                 671.704: 2,
                 692.947: 3,
                 703.241: 5,
                 717.394: 1,
                 724.512: 4,
                 743.890: 2,
                 747.244: 1,
                 748.887: 1,
                 753.577: 1,
                 754.404: 1,
                 837.761: 0,
                 849.536: 0,
                 878.375: 0,
                1117.752: 0,
                1152.275: 0,
            },
            "Xe": {
               # 452.186: 1,
               # 462.420: 3,
               # 466.849: 4,
               # 469.097: 0,
               # 469.804: 1,
               # 473.415: 2,
               # 479.262: 0,
               # 480.702: 0,
               # 482.971: 0,
               # 484.329: 0,
               # 491.651: 0,
               # 492.315: 0,

               # 497.271: 1,
               # 508.062: 3,
               # 519.137: 1,
               # 526.044: 1,
               # 526.195: 1,
               # 529.222: 5,
               # 531.387: 3,
               # 533.933: 5,
               # 537.239: 1,
               # 541.915: 5,
               # 543.896: 2,
               # 546.039: 1,
               # 547.261: 3,
               # 553.107: 2,
               # 566.756: 2,
               # 572.691: 1,
               # 575.103: 1,
               # 594.553: 1,
               # 597.646: 5,

               # 603.620: 3,
               # 605.115: 5,
               # 609.350: 2,
               # 609.759: 4,
               # 610.143: 1,
               # 619.407: 1,
               # 627.082: 1,
               # 627.754: 1,
               # 634.396: 1,
               # 635.635: 2,
               # 651.283: 0,
               # 659.501: 3,
               # 659.725: 1,
               # 669.432: 1,
               # 680.574: 3,
               # 694.211: 3,
               # 699.088: 5,
               # 714.903: 0,
               # 716.483: 1,
               # 730.180: 0,
                 
                 733.930: 0,
                 738.600: 0,
                 739.379: 0,
                 740.040: 0,
                 755.979: 0,
                 758.468: 0,
                 764.391: 1,
                 780.265: 0,
                 788.132: 0,
                 796.734: 0,
                 805.726: 0,
                 806.134: 1,
                 823.163: 4,
                 826.652: 3,
                 828.012: 1,
                 834.680: .5,
                 840.920: .5,
                 881.941: 9,
                 895.230: 2,
                 904.545: 3,
                 916.265: 5,
                 979.970: 3,
                 992.319: 2,
                1083.837: 2,
                1262.339: 1,
                1365.706: 1,
                1414.244: 1,
                1473.281: 1,
                1541.839: 1,
                1605.328: 1,
                1647.290: 1,
                1656.023: 1,
                1672.815: 0,
                1763.882: 0,
                1790.450: 0,
                1809.090: 0,
                1832.530: 0,
                1959.940: 0,
                1984.638: 0,
            }
        }
