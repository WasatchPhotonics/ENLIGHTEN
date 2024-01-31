import re
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
class ModelInfo:
    def __init__(self, ctl):
        self.ctl = ctl

        self.model_fwhm = ModelFWHM()

        self.models = {}
        for obj in [ WP_UV_VIS      (), 
                     WP_VIS         (),
                     WP_VIS_NIR     (),
                     WP_NIR_1       (),
                     WP_248         (),
                     WP_405         (),
                     WP_532         (),
                     WP_532X_IC     (),
                     WP_532_ER      (),
                     WP_633         (),
                     WP_638         (),
                     WP_638X_IC     (),
                     WP_638X_ILP    (),
                     WP_638X_ILC    (),
                     WP_785         (),
                     WP_785_ER      (),
                     WP_785X_IC     (),
                     WP_785X_ILP    (),
                     WP_785X_ILC    (),
                     WP_830         (),
                     WP_830X_IC     (),
                     WP_830X_ILP    (),
                     WP_830X_ILC    (),
                     WP_830XL       (),
                     WP_1064        (),
                     SiG_633        (),
                     SiG_785        (),
                     SiG_830        (),
                     SiG_VIS        () ]:
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
        elif re.search('830xs',       model): info = self.models["SiG-830"]
        elif re.search('785xs',       model): info = self.models["SiG-785"]
        elif re.search('633xs',       model): info = self.models["SiG-633"]
        elif re.search('sig',         model): info = self.models["SiG-785"]
        elif re.search('uv.*vis',     model): info = self.models["WP-UV-VIS"]
        elif re.search('vis.*nir',    model): info = self.models["WP-VIS-NIR"]
        elif re.search('vis',         model): info = self.models["WP-VIS"]
        elif re.search('nir',         model): info = self.models["WP-NIR-1"]
        elif re.search('405',         model): info = self.models["WP-405"]
        elif re.search('532x.*ic',    model): info = self.models["WP-532X-IC"]
        elif re.search('532.*er',     model): info = self.models["WP-532-ER"]
        elif re.search('532',         model): info = self.models["WP-532"]
        elif re.search('633',         model): info = self.models["WP-633"]
        elif re.search('638x.*ic',    model): info = self.models["WP-638X-IC"]
        elif re.search('638x.*ilc',   model): info = self.models["WP-638X-ILC"]
        elif re.search('638x.*ilp',   model): info = self.models["WP-638X-ILP"]
        elif re.search('638',         model): info = self.models["WP-638"]
        elif re.search('785x.*ic',    model): info = self.models["WP-785X-IC"]
        elif re.search('785x.*ilc',   model): info = self.models["WP-785X-ILC"]
        elif re.search('785x.*ilp',   model): info = self.models["WP-785X-ILP"]
        elif re.search('785.*er',     model): info = self.models["WP-785-ER"]
        elif re.search('785',         model): info = self.models["WP-785"]
        elif re.search('830x.*ic',    model): info = self.models["WP-830X-IC"]
        elif re.search('830x.*ilc',   model): info = self.models["WP-830X-ILC"]
        elif re.search('830x.*ilp',   model): info = self.models["WP-830X-ILP"]
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
class WpModelInfo:

    def __init__(self, 
            name=None, 
            wavelength_min=0, 
            wavelength_max=0, 
            wavenumber_min=None, 
            wavenumber_max=None, 
            excitation=0, 
            pixels=1024, 
            color=None,
            image=None):

        self.wavenumber_min = wavenumber_min
        self.wavenumber_max = wavenumber_max
        self.excitation = excitation
        self.pixels = pixels
        self.color = color
        self.image = image if image is not None else name

        if wavenumber_min is not None:
            self.wavenumber_min = wavenumber_min
            wavelength_min = wasatch_utils.wavenumber_to_wavelength(excitation=excitation, wavenumber=wavenumber_min)
        if wavenumber_max is not None:
            self.wavenumber_max = wavenumber_max
            wavelength_max = wasatch_utils.wavenumber_to_wavelength(excitation=excitation, wavenumber=wavenumber_max)

        self.wavelength_min = wavelength_min
        self.wavelength_max = wavelength_max

        if name is not None:
            self.name = name
        else:
            self.name = re.sub("_", "-", type(self).__name__)
        log.debug("WpModelInfo: instantiated %s", self.name)

        self.has_excitation = excitation != 0

        if self.wavelength_min >= self.wavelength_max:
            log.error("bad WpModelInfo: min exceeds max")

        if self.has_excitation and self.wavelength_min <= self.excitation:
            log.error(f"WpModelInfo: {self.name} can see {self.excitation} laser " + 
                      f"from spectral range ({self.wavelength_min:.2f}, {self.wavelength_max:.2f})")

    def dump(self):
        log.debug("WpModelInfo:")
        log.debug("  name           = %s", self.name)
        log.debug("  excitation     = %s", self.excitation)
        log.debug("  wavelengths    = (%s, %s)", self.wavelength_min, self.wavelength_max)
        log.debug("  wavenumbers    = (%s, %s)", self.wavenumber_min, self.wavenumber_max)
        log.debug("  pixels         = %s", self.pixels)
        log.debug("  color          = %s", self.color)
        log.debug("  image          = %s", self.image)
        log.debug("  has_excitation = %s", self.has_excitation)

    def __str__(self):
        return "WpModelInfo { name %s, excitation %s, pixels %s, color %s, image %s }" % (self.name, self.excitation, self.pixels, self.color, self.image)

class WP_UV_VIS   (WpModelInfo): 
    def __init__(self): super(WP_UV_VIS,   self).__init__(wavelength_min= 280, wavelength_max= 950, color="#bdb427")
class WP_VIS      (WpModelInfo): 
    def __init__(self): super(WP_VIS,      self).__init__(wavelength_min= 400, wavelength_max= 800, color="#57a0c3")
class WP_VIS_NIR  (WpModelInfo): 
    def __init__(self): super(WP_VIS_NIR,  self).__init__(wavelength_min= 400, wavelength_max=1080, color="#325b93")
class WP_NIR_1    (WpModelInfo): 
    def __init__(self): super(WP_NIR_1,    self).__init__(wavelength_min= 400, wavelength_max=1080, color="#bdbfbc",                   pixels=512)
class WP_248      (WpModelInfo): 
    def __init__(self): super(WP_248,      self).__init__(wavelength_min= 249, wavelength_max= 268, color="#a32d90", excitation= 248)
class WP_405      (WpModelInfo): 
    def __init__(self): super(WP_405,      self).__init__(wavelength_min= 409, wavelength_max= 477, color="#8f47ae", excitation= 405)
class WP_532X_IC  (WpModelInfo): 
    def __init__(self): super(WP_532X_IC,  self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 532, pixels=2048)
class WP_532      (WpModelInfo): 
    def __init__(self): super(WP_532,      self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 532)
class WP_532_ER   (WpModelInfo): 
    def __init__(self): super(WP_532_ER,   self).__init__(wavelength_min= 539, wavelength_max= 690, color="#009e51", excitation= 532)
class WP_633      (WpModelInfo): 
    def __init__(self): super(WP_633,      self).__init__(wavelength_min= 643, wavelength_max= 747, color="#fd8e25", excitation= 633)
class WP_638X_IC  (WpModelInfo): 
    def __init__(self): super(WP_638X_IC,  self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 638, pixels=2048)
class WP_638X_ILC (WpModelInfo): 
    def __init__(self): super(WP_638X_ILC, self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 638, pixels=2048)
class WP_638X_ILP (WpModelInfo): 
    def __init__(self): super(WP_638X_ILP, self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 638, pixels=2048)
class WP_638      (WpModelInfo): 
    def __init__(self): super(WP_638,      self).__init__(wavelength_min= 648, wavelength_max= 754, color="#fd8e25", excitation= 638, image="WP-633")
class WP_785X_IC  (WpModelInfo): 
    def __init__(self): super(WP_785X_IC,  self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 785, pixels=2048)
class WP_785X_ILC (WpModelInfo): 
    def __init__(self): super(WP_785X_ILC, self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 785, pixels=2048)
class WP_785X_ILP (WpModelInfo): 
    def __init__(self): super(WP_785X_ILP, self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 785, pixels=2048)
class WP_785      (WpModelInfo): 
    def __init__(self): super(WP_785,      self).__init__(wavelength_min= 802, wavelength_max= 931, color="#d53242", excitation= 785)
class WP_785_ER   (WpModelInfo): 
    def __init__(self): super(WP_785_ER,   self).__init__(wavelength_min= 802, wavelength_max=1144, color="#d53242", excitation= 785, pixels=2048)
class WP_830X_IC  (WpModelInfo): 
    def __init__(self): super(WP_830X_IC,  self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 830, pixels=2048)
class WP_830X_ILC (WpModelInfo): 
    def __init__(self): super(WP_830X_ILC, self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 830, pixels=2048)
class WP_830X_ILP (WpModelInfo): 
    def __init__(self): super(WP_830X_ILP, self).__init__(wavelength_min= 535, wavelength_max= 641, color="#009e51", excitation= 830, pixels=2048)
class WP_830      (WpModelInfo): 
    def __init__(self): super(WP_830,      self).__init__(wavelength_min= 844, wavelength_max= 981, color="#666660", excitation= 830)
class WP_830XL    (WpModelInfo): 
    def __init__(self): super(WP_830XL,    self).__init__(wavenumber_min= 158, wavenumber_max=2017, color="#666660", excitation= 830)
class WP_1064     (WpModelInfo): 
    def __init__(self): super(WP_1064,     self).__init__(wavelength_min=1093, wavelength_max=1325, color="#cbc392", excitation=1064, pixels= 512)
class SiG_633     (WpModelInfo): 
    def __init__(self): super(SiG_633,     self).__init__(wavelength_min= 595, wavelength_max= 800, color="#da613e", excitation= 633, pixels=1952, image="SiG-633-FS")
class SiG_785     (WpModelInfo): 
    def __init__(self): super(SiG_785,     self).__init__(wavelength_min= 802, wavelength_max= 931, color="#d53242", excitation= 785, pixels=1952, image="SiG-785-FS")
class SiG_830     (WpModelInfo): 
    def __init__(self): super(SiG_830,     self).__init__(wavelength_min= 844, wavelength_max= 981, color="#666660", excitation= 830, pixels=1952, image="SiG-785-FS") # no 830 image yet
class SiG_VIS     (WpModelInfo): 
    def __init__(self): super(SiG_VIS,     self).__init__(wavelength_min= 400, wavelength_max= 800, color="#57a0c3",                  pixels=1952)
