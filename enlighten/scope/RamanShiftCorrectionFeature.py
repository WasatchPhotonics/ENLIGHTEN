import logging
import json

import scipy.signal as signal
import numpy as np

from enlighten.util import unwrap
from wasatch import utils as wasatch_utils

log = logging.getLogger(__name__)

################################################################################
#                                                                              #
#                                ASTMCompound                                  #
#                                                                              #
################################################################################

##
# An ASTMCompound is a set of ASTMPeaks with one "primary" peak wavenumber
class ASTMCompound:
    def __init__(self, name):
        self.name = name
        self.peaks = []         # list of ASTMPeak

################################################################################
#                                                                              #
#                                 ASTMPeak                                     #
#                                                                              #
################################################################################

##
# One peak of an ASTMCompound.  Intensity is a relative value from 1-5 (5 being 
# the "primary" peak).
class ASTMPeak:
    def __init__(self, wavenumber, intensity, primary=False):
        self.wavenumber = wavenumber
        self.intensity = intensity
        self.primary = primary 

    def __repr__(self):
        return f"ASTMPeak <{self.wavenumber:.1f}cm⁻¹, intensity {self.intensity}, primary {self.primary}>"

################################################################################
#                                                                              #
#                           RamanShiftCorrectionFeature                        #
#                                                                              #
################################################################################

##
# Implement ASTM 1840-96 (2014) by generating a scalar offset which will be 
# applied to the wavenumber X-axis by taking a live measurement of a known Raman
# sample and comparing it to the "expected" peak x-coordinates.
#
# Note this is NOT the same as RamanIntensityCorrection!  RamanIntensityCorrection
# uses an EEPROM calibration to correct intensity (y-axis) on Raman spectra; this
# uses a single Raman measurement to correct the x-axis on all measurements 
# (Raman and otherwise).
#
# Note that we are NOT actually changing the wavecal (wavelengths in nm are not
# affected, nor are we changing the configured laser excitation): we are actually
# changing the equation used to generate wavenumbers, which normally (in "physics
# textbooks" and the like) is merely a factor of excitation and peak wavelength,
# to a custom new-fangled computation involving excitation wavelength, peak
# wavelength, and...this new wavenumber correction we're generating.  I mentally
# blanch at the approach, but if Dieter's cool with it, okay...
#
# Note that if the measured ASTM peaks are offset from the expected peaks,
# there are really a couple things that could physically be off: the WAVECAL 
# could be shifted (what we're correcting here), or the LASER EXCITATION 
# WAVELENGTH could be off (thermals etc).  We are not, in this module, 
# considering the possibility that the laser excitation might be the value 
# needing correction.  To ascertain that, we would realistically want to use an 
# emission lamp as well.  (If the emission peaks were bang-on but the Raman peaks
# were off, then presumably the excitation is what really needs corrected.)
#
# @par Workflow
#
# - user clicks button
# - if peaks matched within threshold
#   - compute offset 
#   - update "session" wavenumber_correction
# - otherwise, display error message "can't match ASTM compound <name>"

class RamanShiftCorrectionFeature:

    ## This file is installed as part of the ENLIGHTEN distribution and contains
    #  our supported compounds and their peaks
    ASTM_PATHNAME = "enlighten/assets/example_data/ASTM-E1840-96.json"

    ## if calibration is off by more than this, display error message
    MAX_WAVENUMBER_SHIFT = 20 

    ## if we find more than this many peaks in the Raman spectra, it's too peaky
    #  (Tylenol has 24 ASTM peaks)
    MAX_PEAKS_FOUND = 50

    ## require that we match at least this many ASTM peaks
    MIN_PEAKS_FOUND = 4
    
    ## constructor
    def __init__(self,
            button,
            cb_visible,
            combo,
            config,
            frame,
            graph,
            gui,
            marquee,
            multispec,
            page_nav):

        self.button         = button
        self.cb_visible     = cb_visible     # whether CURVE is visible, not widget
        self.combo          = combo
        self.config         = config
        self.frame          = frame
        self.gui            = gui
        self.marquee        = marquee
        self.multispec      = multispec
        self.page_nav       = page_nav

        self.astm_compounds = None
        self.compound_name = None
        self.cb_visible.setChecked(False)

        self.widgets_visible = False        # whether the "Scope Settings" frame and "Scope Capture" button are visible
        self.curve_visible = False          # whether the selected compound curve is graphed

        self.curve = graph.add_curve("raman_shift_correction", rehide=False, in_legend=False)
        self.curve.setVisible(False)

        if not self.load_astm():
            self.update_visibility() # hide widget
            return 

        self.compound_name = self.get_names()[0]
        self.init_from_config()
        self.init_combo()

        # bindings
        self.button     .clicked                .connect(self.button_callback)
        self.combo      .currentIndexChanged    .connect(self.combo_callback)
        self.cb_visible .stateChanged           .connect(self.checkbox_callback)

        self.update_visibility()

        self.button.setWhatsThis(unwrap("""
            Apply ASTM E1840-96 (2014) Raman shift correction to the active 
            wavenumber axis. Use the Settings view to select an approved ASTM 
            1840-96 compound, place it in the sample holder, and enable the laser
            to generate a dark-corrected Raman spectrum. 

            You can optionally enable a visual overlay of the 'expected' Raman 
            peak for the selected sample, as a 'sanity-check' against your current 
            x-axis.

            When you can see the measured Raman spectrum on-screen, click this 
            button to generate an "averaged offset" between the measured peaks 
            and expected peak values. This offset will be automatically used to 
            optimize your x-axis values in wavenumber space. 

            Note this is a 'session' correction performed at runtime which is 
            deliberately not stored in the enlighten.ini file or spectrometer 
            EEPROM. The point of this correction is to make a snapshot, 
            instantaneous correction to account for prevailing temperature, air 
            pressure, humidity etc, and therefore storing it over time would be 
            counter-productive."""))

    ## @returns sorted list of configured ASTM compound names
    def get_names(self):
        return sorted(list(self.astm_compounds.keys()))

    ## determine whether widget is visible and usable
    def update_visibility(self):
        self.widgets_visible = False
        spec = self.multispec.current_spectrometer()

        self.widgets_visible = self.astm_compounds is not None and \
                               spec is not None and \
                               spec.settings.has_excitation() and \
                               self.page_nav.doing_raman()

        self.frame.setVisible(self.widgets_visible)
        self.button.setVisible(self.widgets_visible)

        if self.widgets_visible:
            self.gui.colorize_button(self.button, spec.settings.state.wavenumber_correction != 0)

        self.checkbox_callback()

        # Note that this method will get called if we change the selected 
        # spectrometer.  Therefore, at this point, if the curve is visible,
        # we need to update the curve.  We will also need to ensure this
        # is called if the current excitation or wavecal is updated...this
        # could get tricky. Really need an observer pattern here.
        
    ## load previous session's selected compound, if any
    def init_from_config(self):
        s = "RamanShiftCorrection"
        if self.config.has_option(s, "CompoundName"):
            self.compound_name = self.config.get(s, "CompoundName")

    ## initialize the comboBox from the loaded ASTM compound names
    def init_combo(self):
        self.combo.clear()
        for name in sorted(self.astm_compounds):
            self.combo.addItem(name)
            if self.compound_name is not None and self.compound_name == name:
                self.combo.setCurrentIndex(self.combo.count() - 1)

    ## the selected compound in the comboBox was changed, so do something
    def combo_callback(self):
        name = self.combo.currentText()
        if name in self.astm_compounds:
            self.compound_name = name
            self.config.set("RamanShiftCorrection", "CompoundName", self.compound_name)
        else:
            self.compound_name = None
        log.debug("compound = %s", self.compound_name)
        self.update()

    ## the user toggled whether the selected ASTM compound graph should be visualized
    def checkbox_callback(self):
        self.curve_visible = self.cb_visible.isChecked()
        self.curve.setVisible(self.curve_visible)
        if self.curve_visible:
            self.update()

    ## load and parse the JSON file containing supported ASTM compounds and their peaks
    def load_astm(self):
        path = self.ASTM_PATHNAME
        try:
            with open(path) as f:
                doc = json.load(f)
                data = doc["Compounds"]
            log.debug(f"loaded JSON from {path}")
        except:
            log.error("unable to load JSON from %s", path, exc_info=1)
            return

        ########################################################################
        # parse loaded JSON into internal data structure
        ########################################################################

        # note: this currently assumes peaks are in sorted order in the input JSON

        self.astm_compounds = {}
        for name in data:
            compound = ASTMCompound(name)
            self.astm_compounds[name] = compound
            for wn_str in data[name]:
                rec = data[name][wn_str]
                wavenumber = float(wn_str)

                # skip peaks we're told not to load
                if "Ignore" in rec:
                    if rec["Ignore"]:
                        continue

                is_primary = False
                if "Primary" in rec:
                    is_primary = rec["Primary"] # json library converts to bool 

                intensity = 5
                if "Intensity" in rec:
                    intensity = rec["Intensity"]

                compound.peaks.append(ASTMPeak(wavenumber, intensity, primary=is_primary))

        # self.log_astm()
        return True
            
    ## (for debugging) dump the parsed JSON data
    def log_astm(self):
        log.debug("ASTM Compounds:")
        for name in sorted(self.astm_compounds):
            compound = self.astm_compounds[name]
            log.debug("  %s", compound.name)
            for peak in compound.peaks:
                log.debug(f"    {peak}")

    # ##########################################################################
    # ASTM Curve
    # ##########################################################################

    ## 
    # This is the method normally called by Controller when a new spectrum has
    # been processed and we need to update business objects. 
    def update(self):
        self.update_graph()

    ##
    # Updates the displayed ASTM peaks overlayed atop the Scope Capture screen. 
    # In this case, we get called after each new processed_reading so we can 
    # re-scale the peaks against the current maxima.
    def update_graph(self):
        # log.debug("updating graph")

        if not self.curve_visible:
            # log.debug("not visible")
            return

        if self.compound_name is None:
            log.debug("no compound_name")
            self.curve.setData([])
            return

        compound = self.astm_compounds[self.compound_name]
        if len(compound.peaks) < 1:
            log.debug("no peaks")
            self.curve.setData([])
            return

        ########################################################################
        # get min/max intensity
        ########################################################################

        spec = self.multispec.current_spectrometer()
        if spec is None:
            log.debug("no spec")
            self.curve.setData([])
            return

        pr = spec.app_state.processed_reading
        if pr is None:
            log.debug("no pr")
            self.curve.setData([])
            return
            
        spectrum = pr.get_processed()
        wavenumbers = pr.get_wavenumbers()

        max_intensity = max(spectrum)
        min_intensity = min(spectrum)
        # log.debug("min = %d, max = %d", min_intensity, max_intensity)

        if len(compound.peaks) == 0:
            self.curve.setData([])
            return

        # relative intensity of 5 should match top of last spectrum
        scalar = (max_intensity - min_intensity) / 5.0 
        x_min_cm = wavenumbers[0]
        x_max_cm = wavenumbers[-1]

        ########################################################################
        # build spectrum
        ########################################################################

        y = []
        x = []

        PEAK_HALF_WIDTH = spec.fwhm/2 if spec.fwhm else 1     
        BASE = min_intensity 

        # beginning of range
        try:
            if x_min_cm < compound.peaks[0].wavenumber - PEAK_HALF_WIDTH:
                x.append(x_min_cm)
                y.append(BASE)
        except:
            log.error("something wrong with compound.peaks[0]: %s", str(compound))
            return

        # iterate over the peaks
        for peak in compound.peaks:

            peak_cm = peak.wavenumber
            if peak_cm < x_min_cm:
                # log.debug("can't see %s peak at %.2f (too low)", self.compound_name, peak_cm)
                continue
            elif peak_cm > x_max_cm:
                # log.debug("can't see %s peak at %.2f (too high)", self.compound_name, peak_cm)
                continue

            intensity = peak.intensity
            if intensity is None:
                intensity = 0.5

            # point before the peak
            x.append(peak_cm - PEAK_HALF_WIDTH)
            y.append(BASE)

            # the peak
            x.append(peak_cm)
            y.append(BASE + intensity * scalar)

            # point after the peak
            x.append(peak_cm + PEAK_HALF_WIDTH)
            y.append(BASE)

        # extend the graph after the last peak
        x.append(x_max_cm)
        y.append(BASE)

        self.curve.setData(x, y)

    # ##########################################################################
    # Calibration
    # ##########################################################################

    def button_callback(self):
        if not self.widgets_visible:
            return

        if self.compound_name is None:
            return
        compound = self.astm_compounds[self.compound_name]
        if len(compound.peaks) < 1:
            return

        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        pr = spec.app_state.processed_reading
        if pr is None:
            return

        ########################################################################
        # are we setting or clearing the correction?
        ########################################################################

        if spec.settings.state.wavenumber_correction != 0:
            self.marquee.info("Cleared wavenumber correction")
            spec.settings.set_wavenumber_correction(0)
            self.update_visibility()
            return

        ########################################################################
        # we need to perform the peak association in UNCORRECTED space, as the
        # new correction will REPLACE rather than ADD to any current correction
        ########################################################################

        log.debug("starting wavenumber_correction")

        spectrum = pr.get_processed()
        wavenumbers = pr.get_wavenumbers()
        wavelengths = pr.get_wavelengths()

        log.debug(f"using processed spectrum of {len(spectrum)} pixels from ({wavenumbers[0]:.2f}, {wavenumbers[-1]:.2f}cm⁻¹)")

        ########################################################################
        # peakfinding
        ########################################################################

        # Compute min threshold between peaks in pixel space, using compound 
        # data and spectrometer's average wavenumber/pixel resolution. 
        cm_per_px = (wavenumbers[-1] - wavenumbers[0]) / spec.settings.pixels()
        log.debug("spec has %.2f cm/px", cm_per_px)

        if not hasattr(spec, "fwhm") or not spec.fwhm:
            spec.fwhm = 3
            log.debug(f"unspecified FWHM, defaulting to {spec.fwhm}")
        width_px = round(spec.fwhm / cm_per_px)
        log.debug(f"using FWHM {spec.fwhm} (width {width_px}px)")

        found_peak_indices, _ = signal.find_peaks(
            x            = spectrum,
            height       = None, 
            threshold    = None, 
            distance     = None,            # gap_px
            prominence   = 200,             # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_prominences.html#scipy.signal.peak_prominences
            width        = [ 0.5 * width_px, 2 * width_px ],
            wlen         = None, 
            rel_height   = 0.5,  
            plateau_size = None)

        log.debug(f"found the following {len(found_peak_indices)} peaks within the measured spectrum of {len(spectrum)} pixels from ({wavenumbers[0]:.2f}, {wavenumbers[-1]:.2f}cm)")
        for px in found_peak_indices:
            log.debug(f"  pixel {px:4d}: wavenumber {wavenumbers[px]:.2f} (intensity {spectrum[px]:.2f})")
        log.debug(f"spectrum: {list(spectrum)}")
        log.debug(f"wavenumbers: {list(wavenumbers)}")

        if len(found_peak_indices) > self.MAX_PEAKS_FOUND:
            self.marquee.error("Sample is too peaky...ensure laser on, increase integration time or enable boxcar")
            return
        elif len(found_peak_indices) < self.MIN_PEAKS_FOUND:
            self.marquee.error(f"failed to find sufficient peaks ({len(found_peak_indices)} < {self.MIN_PEAKS_FOUND}), increase integration time")
            return

        ########################################################################
        # see how many ASTM peaks we can match
        ########################################################################

        # "shift" = "Raman shift in wavenumbers ADDED to correct discrepancy"

        # make a list of the found peak wavenumbers
        found_peak_cms = [wavenumbers[px] for px in found_peak_indices]

        matched_peak_indices = []
        total_shift_cm = 0
        total_shift_nm = 0
        visible_peaks = 0

        # iterate through the EXPECTED ASTM compound peaks, trying to match each
        # against the closest MEASURED spectrum peak.
        for peak in compound.peaks:
            log.debug(f"trying to match {peak}")

            if peak.wavenumber <= wavenumbers[0] or peak.wavenumber >= wavenumbers[-1]:
                log.debug("  can't see...ignoring")
                continue

            visible_peaks += 1

            # of the peaks we declared in the measurement, find which is closest 
            # to "this expected peak", in wavenumber space, using current wavecal
            index = self.find_nearest_index(found_peak_cms, peak.wavenumber)

            # what pixel is that on the spectrum
            measured_px = found_peak_indices[index]

            # experimental: recompute measured_cm via parabolic approximation
            measured_cm, _ = wasatch_utils.parabolic_approximation(measured_px, x=wavenumbers, y=spectrum)
            measured_nm, _ = wasatch_utils.parabolic_approximation(measured_px, x=wavelengths, y=spectrum)

            # what's our offset in cm (expected - measured)
            shift_cm = peak.wavenumber - measured_cm

            peak_wavelength = wasatch_utils.wavenumber_to_wavelength(spec.settings.excitation(), peak.wavenumber)
            shift_nm = peak_wavelength - measured_nm

            log.debug(f" closest match to ASTM peak {peak.wavenumber:.2f}cm⁻¹ was found at measured_cm {measured_cm:.2f}cm⁻¹, a shift of {shift_cm:.2f}cm⁻¹")

            # was this match "good enough"?
            if abs(shift_cm) > self.MAX_WAVENUMBER_SHIFT:

                # it's okay to fail to match any one ASTM peak...
                log.debug(f"failed to find {peak} in the spectrum")
                if not peak.primary:
                    continue

                # ...but not the primary
                self.marquee.error(f"failed to match primary ASTM peak at {peak.wavenumber:.1f}cm⁻¹")
                return

            log.debug(f"  peak {peak.wavenumber:.2f}cm-1 found on pixel {measured_px} ({measured_cm:.2f}cm⁻¹, {measured_nm:.2f}nm), "
                    + f"for shift of {shift_cm:.2f}cm⁻¹ ({shift_nm:.2f}nm)")

            total_shift_cm += shift_cm
            total_shift_nm += shift_nm

            matched_peak_indices.append(index)

        matched_peak_count = len(matched_peak_indices)
        if matched_peak_count < self.MIN_PEAKS_FOUND:
            self.marquee.error(f"failed to match sufficient ASTM peaks ({matched_peak_count} < {self.MIN_PEAKS_FOUND})")
            return

        avg_shift_cm = total_shift_cm / matched_peak_count
        avg_shift_nm = total_shift_nm / matched_peak_count
        
        ########################################################################
        # update correction
        ########################################################################

        # persist message so user can read both it and the pop-up dialog
        self.marquee.info(f"Set Raman correction to {avg_shift_cm:.2f}cm⁻¹ ({matched_peak_count} of {visible_peaks} peaks matched, ~{avg_shift_nm:.2f}nm)")
        spec.settings.set_wavenumber_correction(avg_shift_cm)

        self.update_visibility()
        
    def find_nearest_index(self, array, value):
        if len(array) < 1:
            return
        array = np.asarray(array)
        return (np.abs(array - value)).argmin()
