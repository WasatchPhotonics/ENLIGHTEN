import logging

log = logging.getLogger(__name__)

## 
# @file EmissionLamps.py
#
# This class was originally used for an earlier ENLIGHTEN "wavelength calibration"
# feature, which allowed full wavelength calibration from within ENLIGHTEN. 
# However, that feature wasn't particularly well-designed, and we opted to move
# that capability to WPSpecCal in any event.  However, I'm retaining this class
# should we want to use it for a non-Raman, emission-based equivalent of the 
# RamanShiftCorrection "single-point x-axis correction".  
#
# Note that the tables defining which peaks should be visible from which 
# models are probably dated with respect to spectral range.  You may also 
# consider that they could be easily replaced by a simple range query; however,
# in wavelength calibration, it is often desired to explicitly choose which 
# peaks are used for wavecal (avoiding split peaks, balancing the spread across
# the detector, etc).

# ##############################################################################
#                                                                              #
#                              Accessor Class                                  #
#                                                                              #
# ##############################################################################

## convenience class: instantiate one of these to get access to each EmissionLamp 
class EmissionLamps(object):
    def __init__(self,
            model_info):

        self.model_info = model_info

        self.lamps = { 'Ar':   ArLamp   (model_info),
                       'HgAr': HgArLamp (model_info), # e.g., Hg-1
                       'Kr':   KrLamp   (model_info),
                       'Ne':   NeLamp   (model_info),
                       'Xe':   XeLamp   (model_info) }

# ##############################################################################
#                                                                              #
#                                Base Class                                    #
#                                                                              #
# ##############################################################################

## 
# Encapsulates static product data about a gas emission lamp for use by the
# Wavecal business object. 
#
# All data taken from Ocean Optics website for their excellent line of gas
# emission lamps, which Wasatch Photonics enthusiastically endorses for all your 
# spectrometer calibration needs. 
#
# @note Relative intensities are extremely nominal, given grating transmission
#       curves; small peaks on one spectrometer may be huge on another. Peaks
#       with intensity of 'zero' I simply haven't seen, don't know, and should
#       probably be displayed as '1' but perhaps in a different color. Intensities
#       should be based on VIS-NIR or VIS if available.
#
class EmissionLamp(object):
    def __init__(self, model_info, element=None):
        self.model_info = model_info

        self.urls = []
        self.visible = {}
        self.intensity = {}
        self.wavelengths = []
        self.element = element

    def get_peaks_by_model(self, model):
        log.debug("get_peaks_by_model: getting %s peaks for %s", self.element, model.name)
        if model.name in self.visible:
            log.debug("get_peaks_by_model: returning all visible %s peaks for %s", self.element, model.name)
            wavelengths = self.visible[model.name]
        else:
            log.debug("get_peaks_by_model: generating list of %s peaks in %s's range", self.element, model.name)
            wavelengths = []
            for wavelength in self.wavelengths:
                if model.wavelength_min <= wavelength and wavelength <= model.wavelength_max:
                    wavelengths.append(wavelength)
        return wavelengths

    def parse_data(self, data):
        self.visible = {}
        self.intensity = {}
        self.wavelengths = []

        for wavelength in sorted(data):
            self.wavelengths.append(wavelength)

            attr = data[wavelength]
            self.intensity[wavelength] = attr.pop(0)

            # remaining attributes are presumably ModelInfo names that can "see" the peak
            while attr:
                name = attr.pop()
                self.set_visible(name, wavelength)
    
    def set_visible(self, name, wavelength):
        model = self.model_info.get_by_name(name)
        if not name in self.visible:
            self.visible[name] = []
        #log.debug("EmissionLamp.set_visible: %s %.2f is visible to %s", self.element, wavelength, model.name)
        self.visible[name].append(wavelength)

    def get_intensity(self, wavelength):
        if wavelength in self.intensity:
            if self.intensity[wavelength] > 0:
                return self.intensity[wavelength]
        return None

    def get_intensity_scalar(self, max_intensity):
        max_relative_intensity = 0.5
        for wl in self.intensity:
            if max_relative_intensity < self.intensity[wl]:
                max_relative_intensity = self.intensity[wl]
        return max_intensity / max_relative_intensity

# ##############################################################################
#                                                                              #
#                              Emission Lamps                                  #
#                                                                              #
# ##############################################################################

##
# AR-1 (argon)
class ArLamp(EmissionLamp):
    def __init__(self, model_info):
        super(ArLamp, self).__init__(model_info, element='Ar')
        self.urls = [ 'http://oceanoptics.com/wp-content/uploads/AR-1_spectra-01.jpg',
                      'http://bwtek.com/wp-content/uploads/2012/05/scl100_ar.jpg' ]
        data = {     696.543: [1,                    "WP-VIS", "WP-VIS-NIR"],
                     706.722: [.5,                   "WP-VIS", "WP-VIS-NIR"],
                     794.818: [1,                    "WP-VIS", "WP-VIS-NIR"],
                     800.616: [1, "WP-785",                    "WP-VIS-NIR"],
                     801.479: [1, "WP-785"],                  
                     810.369: [2, "WP-785",                    "WP-VIS-NIR"],
                     811.531: [4, "WP-785"],                  
                     826.452: [3, "WP-785",                    "WP-VIS-NIR"],
                     840.821: [3, "WP-785",                    "WP-VIS-NIR"],
                     842.465: [5, "WP-785",                    "WP-VIS-NIR"],
                     852.144: [2, "WP-785",                    "WP-VIS-NIR"],
                     866.794: [1, "WP-785",                    "WP-VIS-NIR"],
                     876.058: [0],                       
                     879.947: [0],                       
                     894.310: [0],                       
                     912.297: [9, "WP-785",                    "WP-VIS-NIR"],
                     922.450: [2, "WP-785"],     
                     935.422: [0],                       
                     965.779: [1,                              "WP-VIS-NIR"],
                     978.450: [0],
                    1047.005: [0],
                    1066.660: [0],
                    1110.646: [0],
                    1148.811: [0, "WP-1064"],
                    1166.871: [0, "WP-1064"],
                    1171.949: [0, "WP-1064"],
                    1211.233: [0, "WP-1064"],
                    1213.974: [0, "WP-1064"],
                    1234.339: [0, "WP-1064"],
                    1240.283: [0, "WP-1064"],
                    1243.932: [0, "WP-1064"],
                    1248.766: [0, "WP-1064"],
                    1270.288: [0, "WP-1064"],
                    1273.342: [0, "WP-1064"],
                    1280.274: [0, "WP-1064"],
                    1295.666: [0, "WP-1064"],
                    1300.826: [0, "WP-1064"],
                    1322.811: [0, "WP-1064"],
                    1327.264: [0, "WP-1064"],
                    1331.321: [0],
                    1336.711: [0],
                    1350.419: [0],
                    1362.266: [0],
                    1367.855: [0],
                    1371.858: [0],
                    1382.572: [0],
                    1390.748: [0],
                    1409.364: [0],
                    1504.650: [0],
                    1517.269: [0],
                    1532.934: [0],
                    1598.949: [0],
                    1694.058: [0],
                    1704.288: [0],
               }
        self.parse_data(data)

##
# Hg-1 (mixture of argon and mercury)
class HgArLamp(EmissionLamp):
    def __init__(self, model_info):
        super(HgArLamp, self).__init__(model_info, element='HgAr')
        self.urls = [ 'http://oceanoptics.com/wp-content/uploads/HG-1-spectrum-with-USB2000-XR1-2.png',
                      'http://bwtek.com/wp-content/uploads/2012/05/scl100_mer.jpg' ]
        data = {
                   253.652: [0],
                   296.728: [0],
                   302.150: [0],
                   313.155: [0],
                   334.148: [0],
                   365.015: [0],
                   404.656: [1,                             "WP-VIS", "WP-VIS-NIR"],
                   435.833: [1,                             "WP-VIS", "WP-VIS-NIR"],
                   546.074: [5, "WP-532",                   "WP-VIS", "WP-VIS-NIR"],
                   576.960: [1, "WP-532",                   "WP-VIS"],
                   579.066: [1, "WP-532",                   "WP-VIS", "WP-VIS-NIR"],
                   696.543: [1, "WP-532",         "WP-638", "WP-VIS", "WP-VIS-NIR"],
                   706.722: [1,                   "WP-638", "WP-VIS", "WP-VIS-NIR"],
                   714.704: [1,                   "WP-638", "WP-VIS", "WP-VIS-NIR"],
                   727.294: [1,                   "WP-638", "WP-VIS", "WP-VIS-NIR"],
                   738.398: [1,                   "WP-638", "WP-VIS", "WP-VIS-NIR"],
                   750.387: [2,                   "WP-638", "WP-VIS", "WP-VIS-NIR"],
                   763.511: [5,                             "WP-VIS", "WP-VIS-NIR"],
                   772.376: [2,                             "WP-VIS", "WP-VIS-NIR"],
                   794.818: [1,                             "WP-VIS", "WP-VIS-NIR"],
                   800.616: [2,                             "WP-VIS", "WP-VIS-NIR"],
                   811.531: [4,                                       "WP-VIS-NIR"],
                   826.452: [3,                                       "WP-VIS-NIR"],
                   842.465: [3,                                       "WP-VIS-NIR"],
                   852.144: [1, "WP-830",                             "WP-VIS-NIR"],
                   866.794: [1, "WP-830",                             "WP-VIS-NIR"],
                   912.297: [5, "WP-830",                             "WP-VIS-NIR"],
                   922.450: [1, "WP-830",                             "WP-VIS-NIR"],
                   965.779: [1, "WP-830",                             "WP-VIS-NIR"],
                   978.450: [1, "WP-830",                             "WP-VIS-NIR"],
                  1013.976: [1,                                       "WP-VIS-NIR"],
               }
        self.parse_data(data)

## Kr-1 (krypton)
class KrLamp(EmissionLamp):
    def __init__(self, model_info):
        super(KrLamp, self).__init__(model_info, element='Kr')
        self.urls = [ 'http://oceanoptics.com/wp-content/uploads/KR-1-spectral-range-web.jpg',
                      'http://bwtek.com/wp-content/uploads/2012/05/scl100_kr.jpg' ]
        data = {  
                     427.397: [2,   "WP-405",                      "WP-VIS"],
                     428.297: [.5,  "WP-405"],                     
                     431.958: [3,   "WP-405",                      "WP-VIS"],
                     436.264: [.5,  "WP-405"],
                     437.612: [1,   "WP-405",                      "WP-VIS"],
                     439.997: [1,   "WP-405"],                     
                     445.392: [.7,  "WP-405"],                     
                     446.369: [1.5, "WP-405",                      "WP-VIS"],
                     450.235: [1,   "WP-405",                      "WP-VIS"],
                     556.222: [3.8, "WP-532"],
                     557.029: [4,   "WP-532", "WP-532-ER",         "WP-VIS"],
                     587.092: [5,   "WP-532", "WP-532-ER",         "WP-VIS"],
                     758.741: [1],
                     760.155: [10,                                 "WP-VIS"],
                     768.525: [8],
                     769.454: [9,                                  "WP-VIS"],
                     785.482: [7,                                  "WP-VIS"],
                     791.343: [1,                                  "WP-VIS"],
                     805.950: [1,   "WP-785"],
                     810.437: [1,   "WP-785"],    
                     811.290: [1,   "WP-785"],    
                     819.006: [1,   "WP-785"],    
                     826.324: [1,   "WP-785"],    
                     829.811: [1,   "WP-785"],
                     850.887: [1,   "WP-785", "WP-830"], 
                     877.675: [1,   "WP-785", "WP-830"], 
                     892.869: [1,   "WP-785", "WP-830"], 
                    1181.938: [0],
                    1220.353: [0],
                    1317.741: [0],
                    1363.422: [0],
                    1442.679: [0],
                    1473.444: [0],
                    1520.310: [0],
                    1537.204: [0],
                    1620.872: [0],
                    1689.044: [0],
                    1755.350: [0],
                    1785.738: [0],
                    1800.223: [0],
                    1816.732: [0],
               }
        self.parse_data(data)

## Ne-1 (neon)
class NeLamp(EmissionLamp):
    def __init__(self, model_info):
        super(NeLamp, self).__init__(model_info, element='Ne')
        self.urls = [ 'http://oceanoptics.com/wp-content/uploads/NE-1-spectral-range-web.jpg',
                      'http://bwtek.com/wp-content/uploads/2012/05/scl100_neon.jpg' ]
        data = {
                    341.790: [0],
                    342.391: [0],
                    344.770: [0],
                    345.076: [0],
                    345.419: [0],
                    346.052: [0],
                    346.658: [0],
                    347.257: [0],
                    349.806: [0],
                    350.121: [0],
                    351.519: [0],
                    352.047: [0],
                    359.353: [0],
                    360.017: [0],
                    363.366: [0],
                    368.573: [0],
                    370.122: [0],
                    503.135: [0],
                    503.775: [0],
                    508.038: [0],
                    511.367: [0],
                    511.650: [0],
                    540.056: [1, "WP-532", "WP-532-ER"],
                    576.441: [1, "WP-532", "WP-532-ER"],
                    582.015: [1, "WP-532", "WP-532-ER"],
                    585.249: [2, "WP-532", "WP-532-ER"],
                    588.189: [1, "WP-532", "WP-532-ER"],
                    594.483: [2, "WP-532", "WP-532-ER"],
                    597.553: [1, "WP-532", "WP-532-ER"],
                    603.000: [1, "WP-532", "WP-532-ER"],
                    607.433: [2, "WP-532", "WP-532-ER"],
                    609.616: [3, "WP-532", "WP-532-ER"],
                    612.884: [1, "WP-532", "WP-532-ER"],
                    614.306: [4, "WP-532", "WP-532-ER"],
                    616.359: [2, "WP-532", "WP-532-ER"],
                    621.728: [2, "WP-532", "WP-532-ER"],
                    626.649: [3, "WP-532", "WP-532-ER"],
                    630.479: [2, "WP-532", "WP-532-ER"],
                    633.442: [3, "WP-532", "WP-532-ER"],
                    638.299: [5, "WP-532", "WP-532-ER"],
                    640.225: [6, "WP-532", "WP-532-ER"],
                    650.653: [4,           "WP-532-ER", "WP-633", "WP-638"],
                    653.288: [3,           "WP-532-ER", "WP-633", "WP-638"],
                    659.895: [3,           "WP-532-ER", "WP-633", "WP-638"],
                    667.828: [4,           "WP-532-ER", "WP-633", "WP-638"],
                    671.704: [2,           "WP-532-ER", "WP-633", "WP-638"],
                    692.947: [3,                        "WP-633", "WP-638"],
                    703.241: [5,                        "WP-633", "WP-638"],
                    717.394: [1,                        "WP-633", "WP-638"],
                    724.512: [4,                        "WP-633", "WP-638"],
                    743.890: [2,                        "WP-633", "WP-638"],
                    747.244: [1,                                  "WP-638"],
                    748.887: [1,                                  "WP-638"],
                    753.577: [1,                                  "WP-638"],
                    754.404: [1,                                  "WP-638"],
                    837.761: [0],
                    849.536: [0],
                    878.375: [0],
                   1117.752: [0],
                   1152.275: [0],
               }
        self.parse_data(data)

## Xe-1 (xenon)
class XeLamp(EmissionLamp):
    def __init__(self, model_info):
        super(XeLamp, self).__init__(model_info, element='Xe')
        self.urls = [ 'http://oceanoptics.com/wp-content/uploads/XE-1_spectra-01.jpg' ]
        data = {  452.186: [1, "WP-405"],  
                  462.420: [3, "WP-405"],  
                  466.849: [4, "WP-405"],  
                  469.097: [0],  
                  469.804: [1, "WP-405"],  
                  473.415: [2, "WP-405"], 
                  479.262: [0],  
                  480.702: [0],  
                  482.971: [0],  
                  484.329: [0],  
                  491.651: [0],  
                  492.315: [0], 
                  733.930: [0],  
                  738.600: [0],  
                  739.379: [0],  
                  740.040: [0],  
                  755.979: [0],  
                  758.468: [0], 
                  764.391: [1,                                               "WP-VIS-NIR"],  
                  780.265: [0],                                                                              
                  788.132: [0],                                                                              
                  796.734: [0],                                                                              
                  805.726: [0],                                                                              
                  806.134: [1],                                                                              
                  823.163: [4,  "WP-785", "WP-785-ER",                       "WP-VIS-NIR"],  
                  826.652: [3,  "WP-785", "WP-785-ER",                       "WP-VIS-NIR"],  
                  828.012: [1],
                  834.680: [.5, "WP-785", "WP-785-ER"],  
                  840.920: [.5, "WP-785", "WP-785-ER"],  
                  881.941: [9,  "WP-785", "WP-785-ER", "WP-830", "WP-NIR-1", "WP-VIS-NIR"],
                  895.230: [2,  "WP-785", "WP-785-ER", "WP-830", "WP-NIR-1", "WP-VIS-NIR"],
                  904.545: [3,  "WP-785", "WP-785-ER", "WP-830", "WP-NIR-1", "WP-VIS-NIR"],
                  916.265: [5,  "WP-785", "WP-785-ER", "WP-830", "WP-NIR-1", "WP-VIS-NIR"],
                  979.970: [3,            "WP-785-ER", "WP-830", "WP-NIR-1", "WP-VIS-NIR"],
                  992.319: [2,            "WP-785-ER",           "WP-NIR-1", "WP-VIS-NIR"],
                 1083.837: [2,                                   "WP-NIR-1"], 
                 1262.339: [1,                                   "WP-NIR-1"], 
                 1365.706: [1,                                   "WP-NIR-1"], 
                 1414.244: [1,                                   "WP-NIR-1"], 
                 1473.281: [1,                                   "WP-NIR-1"], 
                 1541.839: [1,                                   "WP-NIR-1"], 
                 1605.328: [1,                                   "WP-NIR-1"], 
                 1647.290: [1,                                   "WP-NIR-1"], 
                 1656.023: [1,                                   "WP-NIR-1"], 
                 1672.815: [0], 
                 1763.882: [0], 
                 1790.450: [0], 
                 1809.090: [0], 
                 1832.530: [0], 
                 1959.940: [0], 
                 1984.638: [0],
               }
        self.parse_data(data)
