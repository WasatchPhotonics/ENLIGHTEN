import math
import numpy as np
import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# Migrated the Relative Irradiance view from ENLIGHTEN core to a plugin.
#
# Note that the sample will be dark-corrected if the user has enabled dark
# correction in ENLIGHTEN.  The reference will be dark-corrected if the user
# enabled dark correction before taking the reference.
class RelativeIrradiance(EnlightenPluginBase):

    def __init__(self):
        super().__init__()

    def get_configuration(self):
        fields = []
        fields.append(EnlightenPluginField(
            name="Show Curve", direction="input", datatype=bool,
            tooltip="Show blackbody curve"))
        fields.append(EnlightenPluginField(
            name="Temp (K)", direction="input", datatype="int", 
            minimum=2000, maximum=6000, step=100, initial=3100, 
            tooltip="Temperature (Kelvin)"))

        return EnlightenPluginConfiguration(
            name         = "Relative Irradiance", 
            block_enlighten = True,
            fields       = fields,
            series_names = [ "Blackbody" ])

    def process_request(self, request):
        pr = request.processed_reading
        sample    = np.array(pr.processed, dtype=np.float32)
        reference = np.array(pr.reference, dtype=np.float32)
        temp_kelvin = request.fields["Temp (K)"]
        show_curve  = request.fields["Show Curve"]

        if pr.dark is None:
            return EnlightenPluginResponse(request, message="Relative Irradiance requires dark correction")

        if pr.reference is None:
            return EnlightenPluginResponse(request, message="Relative Irradiance requires reference")

        if not self.enlighten_info.get_reference_is_dark_corrected():
            return EnlightenPluginResponse(request, message="Relative Irradiance requires reference to be dark-corrected")
                
        blackbody = self.generate_blackbody(temp_kelvin, request.settings.wavelengths)
        if blackbody is None:
            return EnlightenPluginResponse(request, message="error computing blackbody")

        # compute transmission = sample / reference (convert divide-by-zero into 0)
        # @see https://stackoverflow.com/a/37977222/6436775
        transmission = np.divide(sample, reference, out=np.zeros_like(sample), where=reference!=0)

        rel_irrad = transmission * blackbody

        self.debug_array("blackbody", blackbody)
        self.debug_array("sample", sample)
        self.debug_array("reference", reference)
        self.debug_array("transmission", transmission)
        self.debug_array("rel_irrad", rel_irrad)

        series = {}
        if show_curve:
            scaled_blackbody = blackbody * max(rel_irrad)
            self.debug_array("scaled_blackbody", scaled_blackbody)
            series["Blackbody"] = scaled_blackbody

        return EnlightenPluginResponse(request, 
            series = series,
            overrides = {
                "processed": rel_irrad 
            }
        )

    def debug_array(self, label, a):
        log.debug("%s: min %.2f, max %.2f", label, min(a), max(a))

    ## 
    # d, e, f variables refer to spreadsheet columns from which I borrowed the math
    #
    # @see https://www.asdlib.org/learningModules/AtomicEmission/BbRadiation.html
    # @see http://scheeline.scs.uiuc.edu/atomic_spectroscopy/BbRadiation.html etc
    def generate_blackbody(self, temp_kelvin, wavelengths):
        e = 1.288e-15 * math.pow(temp_kelvin, 5)
        blackbody = []
        for wavelength in wavelengths:
            f = 0
            try:
                wl_um = wavelength / 1000.0 # nanometers
                d = 37405.0 / (math.pow(wl_um, 5) * (math.exp(14388.0 / (wl_um * temp_kelvin)) - 1))
                f = d / e
            except:
                log.error("error computing blackbody", exc_info=1)
                return None
            blackbody.append(f)
        return np.array(blackbody, dtype=np.float32)
