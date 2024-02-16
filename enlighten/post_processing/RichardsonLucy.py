import logging
import numpy as np
import math

from enlighten.util import unwrap

log = logging.getLogger(__name__)

##
# This class provides a deconvolution filter which sharpens peaks back to their 
# original optical resolution by removing the Gaussian blur point-spread function.
#
# This class is responsible for the "[x] Sharpen Peaks" checkbox on the KnowItAll
# settings.
#
# @see https://en.wikipedia.org/wiki/Richardson%E2%80%93Lucy_deconvolution
class RichardsonLucy:

    SECTION = "RichardsonLucy"

    ##
    # @param iterations how many Richardson-Lucy iterations to run
    # @param downgrade how much to downgrade the spectrometer's spec'd (claimed) resolution
    # 
    # Last updated from "Turn Raman Sample Library into KIA Input Files WP-00413.Rmd" received
    # 30-Sep-2019 from Dieter.

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_richardson_lucy

        self.reset()

        self.update_from_config()
        self.update_from_gui()

        self.cb_enable.toggled.connect(self.update_from_gui)
        self.cb_enable.setToolTip("apply Richardson-Lucy focal deconvolution")
        self.cb_enable.setWhatsThis(unwrap("""
            Peak Sharpening uses the Richardson-Lucy algorithm to apply
            a physics-based sharpening deconvolution to spectral peaks,
            essentially correcting for detector pixel spacing and non-linearities
            in the wavelength calibration to normalize optical resolution
            across the detector.

            That said, it is an experimental feature and currently only 
            recommended for advanced users who understand its limitations
            and limited scope of applicability."""))

        # ModelInfo may not have "ideal" FHWM for each unit (nm, cm-1, px etc)
        # for each spectrometer, so if we change the x-axis unit, determine if
        # we're able to deconvolve using that axis.
        #
        # MZ: This seems questionable.  The spectrum is physically in pixel space.
        # Whether we are graphing in wavelengths or wavenumbers, we should be able
        # to perform the deconvolution in whatever axis matches the configured 
        # ideal resolution.  Not sure what I was thinking here.
        self.ctl.graph.register_observer("change_axis", self.change_axis_callback)

        # If the user dis/enables or changes cropping, re-generate guassian.  
        # (Alternative design would be to include ROI tuple in the cache key.)
        self.ctl.horiz_roi.register_observer(self.reset)

    def update_from_config(self):
        # when are these actually set?
        self.iterations = self.ctl.config.get_int  (self.SECTION, "iterations", default=5)
        self.downgrade  = self.ctl.config.get_float(self.SECTION, "downgrade",  default=1.0)

    def update_from_gui(self):
        self.enabled = self.cb_enable.isChecked()

    def change_axis_callback(self, old_axis, new_axis):
        self.update_visibility()

    def update_visibility(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        supported = self.is_supported(spec)
        self.cb_enable.setVisible(supported)

    def is_supported(self, spec):
        return spec.fwhm is not None and spec.fwhm > 0

    ##
    # @param pr (In/Out) ProcessedReading
    # @param spec (Input) Spectrometer
    # @see Dieter for algorithm explanation
    #
    # @note supports cropped ProcessedReading if available
    def process(self, pr, spec):
        if not self.enabled:
            return 

        # generate convolution
        resolution_h = self.get_gaussian(spec)
        if resolution_h is None:
            return 

        spectrum = pr.get_processed()

        # prepare to apply convolution
        orig = np.array(spectrum, dtype=np.double)
        deconvolved = np.copy(orig)

        # stay positive (and non-zero)! :-)
        eps = 1e-5 # very small on 65K dynamic range
        deconvolved[deconvolved < eps] = eps 

        # apply convolution
        for _ in range(self.iterations):
            h_times_x = np.matmul(resolution_h, deconvolved)
            y_over_h_times_x = orig / h_times_x
            full_sum = np.matmul(np.transpose(resolution_h), y_over_h_times_x)
            deconvolved = deconvolved * full_sum
            deconvolved[deconvolved < eps] = eps 
        
        pr.set_processed(deconvolved)
        pr.deconvolved = True

    ##
    # There are various ways we could decide what unit to use for average 
    # FWHM. We could just use whatever was currently displayed on-screen 
    # (graph.get_x_axis_unit), but the on-screen x-asis is essentially 
    # irrelevant to the calculation. Since this feature is basically being 
    # provided for Raman, let's just say use wavenumbers for Raman models 
    # -- regardless of whether the laser is engaged, or we're looking at 
    # an emission source (like we'd know) -- and wavelengths otherwise.
    def get_gaussian(self, spec):
        unit = "cm" if spec.has_excitation() else "nm"
        key = spec.label + unit

        # check to see if we've already generated the Gaussian for this 
        # spectrometer in this unit
        if key not in self.cache:
            log.debug("generating Gaussian for key %s", key)
            self.cache[key] = self.generate_gaussian(spec, unit)

        return self.cache[key]

    ##
    # Generating the Gaussian is somewhat intensive, so cache it.
    # However, when an input to the Guassian changes (like the user
    # has changed the ROI), flush so it will be regenerated.
    def reset(self):
        log.debug("flushing cache")
        self.cache = {}

    def generate_gaussian(self, spec, unit):
        if spec is None:
            return

        x_axis = self.ctl.graph.generate_x_axis(unit=unit, cropped=True)
        if x_axis is None:
            log.debug("no x-axis")
            return 

        resolution_per_unit = spec.fwhm
        if resolution_per_unit is None or resolution_per_unit == 0:
            log.debug("can't apply Richardson-Lucy without estimated optical resolution in FWHM (%s)", unit)
            return

        num_pixels = len(x_axis)
        pixel_range = np.arange(num_pixels)

        unit_per_pixel = np.diff(x_axis)
        unit_per_pixel = np.insert(unit_per_pixel, 0, unit_per_pixel[0])
        pixel_fwhm = resolution_per_unit / unit_per_pixel

        pixel_sigma = pixel_fwhm / (2.0 * math.sqrt(2.0 * math.log(2.0)))
        pixel_sigma *= self.downgrade
        pixel_sigma_2 = pixel_sigma * pixel_sigma
        resolution_h = np.zeros((num_pixels, num_pixels))

        for row in pixel_range:
            tmp = (pixel_range - row).astype(np.double)
            tmp = tmp * tmp
            tmp *= -0.5 
            tmp /= pixel_sigma_2[row]
            resolution_spectrum = np.exp(tmp)
            resolution_h[row] = resolution_spectrum / sum(resolution_spectrum)

        return resolution_h
