import re
import numpy as np
import logging

from .ModelFWHM import ModelFWHM

from wasatch import utils as wasatch_utils

log = logging.getLogger(__name__)

# ##############################################################################
#                                                                              #
#                                  ModelInfo                                   #
#                                                                              #
# ##############################################################################

## 
# Convenience class providing access to pre-built subtypes of WpModelInfo, plus
# ModelFWHM.
class ModelInfo(object):
    def __init__(self, ctl):
        self.ctl = ctl

        self.model_fwhm = ModelFWHM()

        self.models = {}
        for obj in [ WP_UV_VIS  (), 
                     WP_VIS     (),
                     WP_VIS_NIR (),
                     WP_NIR_1   (),
                     WP_248     (),
                     WP_405     (),
                     WP_532     (),
                     WP_532_ER  (),
                     WP_633     (),
                     WP_638     (),
                     WP_785     (),
                     WP_785_ER  (),
                     WP_830     (),
                     WP_830XL   (),
                     WP_1064    (),
                     SiG_633    (),
                     SiG_785    (),
                     SiG_830    (),
                     SiG_VIS    () ]:
            self.models[obj.name] = obj

    def get_names(self):
        return sorted(self.models.keys())

    def get_by_name(self, name):
        if name in self.models:
            return self.models[name]
        return None

    def get_by_model(self, full_model):
        model = full_model.lower()
        info = None

        # order matters here (note all are lowercase!)
        if   re.search('sig.*vis',    model): info = self.models["SiG-VIS"]
        elif re.search('sig.*830',    model): info = self.models["SiG-830"]
        elif re.search('sig.*633',    model): info = self.models["SiG-633"]
        elif re.search('sig.*785',    model): info = self.models["SiG-785"]
        elif re.search('sig',         model): info = self.models["SiG-785"]
        elif re.search('uv.*vis',     model): info = self.models["WP-UV-VIS"]
        elif re.search('vis.*nir',    model): info = self.models["WP-VIS-NIR"]
        elif re.search('vis',         model): info = self.models["WP-VIS"]
        elif re.search('nir',         model): info = self.models["WP-NIR-1"]
        elif re.search('405',         model): info = self.models["WP-405"]
        elif re.search('532.*er',     model): info = self.models["WP-532-ER"]
        elif re.search('532',         model): info = self.models["WP-532"]
        elif re.search('633',         model): info = self.models["WP-633"]
        elif re.search('638',         model): info = self.models["WP-638"]
        elif re.search('785.*er',     model): info = self.models["WP-785-ER"]
        elif re.search('785',         model): info = self.models["WP-785"]
        elif re.search('830xl',       model): info = self.models["WP-830XL"]
        elif re.search('830',         model): info = self.models["WP-830"]
        elif re.search('248',         model): info = self.models["WP-248"]
        elif re.search('1064',        model): info = self.models["WP-1064"]

        return info

# ##############################################################################
#                                                                              #
#                            ABC and Concrete Classes                          #
#                                                                              #
# ##############################################################################

##
# Abstract Base Class (ABC) for actual per-model concrete classes.
#
# FWHM is not addressed in these classes, because it varies so much by sub-configuration
# (slit, detector etc).  That is handled separately in ModelFWHM.
class WpModelInfo(object):

    def __init__(self, 
            name=None, 
            wavelength_min=0, 
            wavelength_max=0, 
            wavenumber_min=None, 
            wavenumber_max=None, 
            excitation=0, 
            pixels=1024, 
            color=None,
            image_basename=None):

        if wavenumber_min is not None:
            wavelength_min = wasatch_utils.wavenumber_to_wavelength(excitation=excitation, wavenumber=wavenumber_min)
        if wavenumber_max is not None:
            wavelength_max = wasatch_utils.wavenumber_to_wavelength(excitation=excitation, wavenumber=wavenumber_max)

        self.excitation = excitation
        self.wavelength_min = wavelength_min
        self.wavelength_max = wavelength_max
        self.pixels = pixels
        self.color = color
        self.image_basename = image_basename if image_basename is not None else name

        if name is not None:
            self.name = name
        else:
            self.name = re.sub("_", "-", type(self).__name__)
        # log.debug("WpModelInfo: instantiated %s", self.name)

        self.has_laser = excitation != 0

        # could compute default wavelength min/max here if excitation provided (3000cm-1)

        if self.wavelength_min >= self.wavelength_max:
            log.error("bad WpModelInfo: min exceeds max")

        if self.has_laser and self.wavelength_min <= self.excitation:
            log.error(f"WpModelInfo: {self.name} can see {self.excitation} laser from spectral range (%.2f, %.2f)",
                self.wavelength_min, self.wavelength_max)

    def dump(self):
        log.debug("WpModelInfo:")
        log.debug("  name           = %s", self.name)
        log.debug("  excitation     = %s", self.excitation)
        log.debug("  wavelength_min = %s", self.wavelength_min)
        log.debug("  wavelength_max = %s", self.wavelength_max)
        log.debug("  pixels         = %s", self.pixels)
        log.debug("  color          = %s", self.color)
        log.debug("  image_basename = %s", self.image_basename)
        log.debug("  has_laser      = %s", self.has_laser)

    def __str__(self):
        return "WpModelInfo { name %s, excitation %s, pixels %s, color %s, image_basename %s }" % (self.name, self.excitation, self.pixels, self.color, self.image_basename)

class WP_UV_VIS(WpModelInfo):
    def __init__(self):
        super(WP_UV_VIS, self).__init__(wavelength_min=280, wavelength_max=950, color="#bdb427")

class WP_VIS(WpModelInfo):
    def __init__(self):
        super(WP_VIS, self).__init__(wavelength_min=400, wavelength_max=800, color="#57a0c3")

class WP_VIS_NIR(WpModelInfo):
    def __init__(self):
        super(WP_VIS_NIR, self).__init__(wavelength_min=400, wavelength_max=1080, color="#325b93")

class WP_NIR_1(WpModelInfo):
    def __init__(self):
        super(WP_NIR_1, self).__init__(wavelength_min=400, wavelength_max=1080, pixels=512, color="#bdbfbc")

class WP_248(WpModelInfo):
    def __init__(self):
        super(WP_248, self).__init__(wavelength_min=249, wavelength_max=268, excitation=248, color="#a32d90")

class WP_405(WpModelInfo):
    def __init__(self):
        super(WP_405, self).__init__(wavelength_min=409, wavelength_max=477, excitation=405, color="#8f47ae")

class WP_532(WpModelInfo):
    def __init__(self):
        super(WP_532, self).__init__(wavelength_min=535, wavelength_max=641, excitation=532, color="#009e51")

class WP_532_ER(WpModelInfo):
    def __init__(self):
        super(WP_532_ER, self).__init__(wavelength_min=539, wavelength_max=690, excitation=532, color="#009e51")

class WP_633(WpModelInfo):
    def __init__(self):
        super(WP_633, self).__init__(wavelength_min=643, wavelength_max=747, excitation=633, color="#fd8e25")

class WP_638(WpModelInfo):
    def __init__(self):
        super(WP_638, self).__init__(wavelength_min=648, wavelength_max=754, excitation=638, image_basename="WP-633", color="#fd8e25")

class WP_785(WpModelInfo):
    def __init__(self):
        super(WP_785, self).__init__(wavelength_min=802, wavelength_max=931, excitation=785, color="#d53242")

class WP_785_ER(WpModelInfo):
    def __init__(self):
        super(WP_785_ER, self).__init__(wavelength_min=802, wavelength_max=1144, excitation=785, color="#d53242")

class WP_830(WpModelInfo):
    def __init__(self):
        super(WP_830, self).__init__(wavelength_min=844, wavelength_max=981, excitation=830, color="#666660")
 
class WP_830XL(WpModelInfo):
    def __init__(self):
        super(WP_830XL, self).__init__(wavenumber_min=158, wavenumber_max=2017, excitation=830, color="#666660")
 
class WP_1064(WpModelInfo):
    def __init__(self):
        super(WP_1064, self).__init__(wavelength_min=1093, wavelength_max=1325, excitation=1064, pixels=512, color="#cbc392")

class SiG_633(WpModelInfo):
    def __init__(self):
        super(SiG_633, self).__init__(wavelength_min=595, wavelength_max=800, excitation=633, pixels=1952, color="#da613e")

class SiG_785(WpModelInfo):
    def __init__(self):
        super(SiG_785, self).__init__(wavelength_min=802, wavelength_max=931, excitation=785, pixels=1952, color="#d53242")

class SiG_830(WpModelInfo):
    def __init__(self):
        super(SiG_830, self).__init__(wavelength_min=844, wavelength_max=981, excitation=830, pixels=1952, image_basename="SiG-785", color="#666660")

class SiG_VIS(WpModelInfo):
    def __init__(self):
        super(SiG_VIS, self).__init__(wavelength_min=400, wavelength_max=800, pixels=1952, color="#57a0c3")

# UV-VIS-NIR   00a5b5
# back-up teal 36b0c9

