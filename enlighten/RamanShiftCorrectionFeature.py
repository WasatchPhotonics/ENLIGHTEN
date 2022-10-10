import logging
import json

import scipy.signal as signal
import numpy as np

from wasatch import utils as wasatch_utils

log = logging.getLogger(__name__)

################################################################################
#                                                                              #
#                                ASTMCompound                                  #
#                                                                              #
################################################################################

##
# An ASTMCompound is a set of ASTMPeaks with one "primary" peak wavenumber
class ASTMCompound(object):
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
class ASTMPeak(object):
    def __init__(self, wavenumber, intensity, primary=False):
        self.wavenumber = wavenumber
        self.intensity = intensity
        self.primary = primary 

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
# @para Workflow
#
# - user clicks button
# - if peaks matched within threshold
#   - compute offset 
#   - update "session" wavenumber_correction
# - otherwise, display error message "can't match ASTM compound <name>"

class RamanShiftCorrectionFeature(object):

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
                    is_primary = rec["Primary"]

                intensity = 5
                if "Intensity" in rec:
                    intensity = rec["Intensity"]

                compound.peaks.append(ASTMPeak(wavenumber, intensity, is_primary))

        # self.log_astm()
        return True
            
    ## (for debugging) dump the parsed JSON data
    def log_astm(self):
        log.debug("ASTM Compounds:")
        for name in sorted(self.astm_compounds):
            compound = self.astm_compounds[name]
            log.debug("  %s", compound.name)
            for peak in compound.peaks:
                log.debug("    %6.1f (relative intensity %d, primary %s)", peak.wavenumber, peak.intensity, peak.primary)

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
        log.debug("updating graph")

        if not self.curve_visible:
            log.debug("not visible")
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
            
        max_intensity = max(pr.processed)
        min_intensity = min(pr.processed)
        log.debug("min = %d, max = %d", min_intensity, max_intensity)

        if len(compound.peaks) == 0:
            self.curve.setData([])
            return

        # relative intensity of 5 should match top of last spectrum
        scalar = (max_intensity - min_intensity) / 5.0 
        x_min_cm = spec.settings.wavenumbers[0]
        x_max_cm = spec.settings.wavenumbers[-1]

        ########################################################################
        # build spectrum
        ########################################################################

        y = []
        x = []

        PEAK_HALF_WIDTH = 1     # cm-1...take from ModelInfo?  Note this is NOT FWHM...it's at the base
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
                log.debug("can't see %s peak at %.2f (too low)", self.compound_name, peak_cm)
                continue
            elif peak_cm > x_max_cm:
                log.debug("can't see %s peak at %.2f (too high)", self.compound_name, peak_cm)
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
        wavenumbers = [x - spec.settings.state.wavenumber_correction for x in spec.settings.wavenumbers]
            
        ########################################################################
        # peakfinding
        ########################################################################

        # Compute min threshold between peaks in pixel space, using compound 
        # data and spectrometer's average wavenumber/pixel resolution.  Also
        # grab primary peak index.
        cm_per_px = (wavenumbers[-1] - wavenumbers[0]) / spec.settings.pixels()
        log.debug("spec has %.2f cm/px", cm_per_px)

        peak_cms = [peak.wavenumber for peak in compound.peaks]
        peak_cms.sort()
        min_gap_cm = None
        for i in range(len(peak_cms)):
            if i + 1 < len(peak_cms):
                gap_cm = peak_cms[i+1] - peak_cms[i]
                if min_gap_cm is None:
                    min_gap_cm = gap_cm
                elif min_gap_cm > gap_cm:
                    min_gap_cm = gap_cm
        if min_gap_cm is None:
            log.error("couldn't determine min_gap_cm for %s", self.compound_name)
            return
        gap_px = round(0.5 * min_gap_cm / cm_per_px)
        log.debug("min_gap_cm %.2f at %.2f cm/px implies gap_px of %d px", min_gap_cm, cm_per_px, gap_px)

        found_peak_indices, peak_properties = signal.find_peaks(
            x            = pr.processed,    # technically "y" :-)
            height       = None, 
            threshold    = None, 
            distance     = None, # gap_px, 
            prominence   = 200,             # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_prominences.html#scipy.signal.peak_prominences
            width        = 3,               # we could derive this from EEPROM's FWHM, but seems a good start
            wlen         = None, 
            rel_height   = 0.5, 
            plateau_size = None)

        log.debug("Found %d peaks:", len(found_peak_indices))
        for px in found_peak_indices:
            log.debug("  pixel %4d: wavenumber %.2f (intensity %d)", px, wavenumbers[px], pr.processed[px])

        if len(found_peak_indices) > self.MAX_PEAKS_FOUND:
            self.marquee.error("Sample is too peaky...ensure laser firing, increase integration or consider boxcar")
            return
        elif len(found_peak_indices) < self.MIN_PEAKS_FOUND:
            self.marquee.error("failed to find sufficient ASTM peaks")
            return

        ########################################################################
        # see how many ASTM peaks we can match
        ########################################################################

        # "shift" means "how much shift should we ADD to correct discrepancy"

        # make a list of the found peak wavenumbers
        found_peak_cms = [wavenumbers[x] for x in found_peak_indices]

        matched_peak_indices = []
        total_shift_cm = 0
        visible_peaks = 0

        for peak in compound.peaks:
            log.debug("trying to match ASTM peak %.2f cm-1", peak.wavenumber)

            if peak.wavenumber <= wavenumbers[0] or peak.wavenumber >= wavenumbers[-1]:
                log.debug("can't see...ignoring")
                continue

            visible_peaks += 1

            # of the peaks we declared in the measurement, find which is closest 
            # to "this expected peak", in wavenumber space, using current wavecal
            index = self.find_nearest_index(found_peak_cms, peak.wavenumber)

            # what pixel is that on the spectrum
            measured_px = found_peak_indices[index]

            # what wavenumber is attached to that in the current wavecal
            measured_cm_old = wavenumbers[measured_px]
            intensity_old = pr.processed[measured_px]

            # experimental: recompute measured_cm via parabolic approximation
            measured_cm, intensity_new = wasatch_utils.parabolic_approximation(measured_px, x=wavenumbers, y=pr.processed)

            log.debug("parabolic approximation: subpixel peak refined from %.2f to %.2f cm-1 (%.4f delta) (intensity %.2f to %.2f)",
                measured_cm_old,
                measured_cm,
                measured_cm - measured_cm_old,
                intensity_old,
                intensity_new)

            # what's our offset in cm (expected - measured)
            shift_cm = peak.wavenumber - measured_cm

            # was this match "good enough"?
            if abs(shift_cm) > self.MAX_WAVENUMBER_SHIFT:

                # it's okay to fail to match any one ASTM peak...
                log.debug("failed to match ASTM peak %.2f to any declared peak in the measurement")
                if not peak.primary:
                    continue

                # ...but not the primary
                self.marquee.error("failed to match primary ASTM peak")
                return

            log.debug("  peak %.2f cm-1 found on pixel %d (%.2f cm-1), for shift of %.2f cm-1",
                peak.wavenumber, measured_px, measured_cm, shift_cm)

            total_shift_cm += shift_cm
            matched_peak_indices.append(index)

        matched_peak_count = len(matched_peak_indices)
        if matched_peak_count < self.MIN_PEAKS_FOUND:
            self.marquee.error("failed to match sufficient ASTM peaks")
            return

        avg_shift_cm = total_shift_cm / matched_peak_count
        
        ########################################################################
        # update correction
        ########################################################################

        # persist message so user can read both it and the pop-up dialog
        self.marquee.info("Set Raman correction to %.2fcm⁻¹ (%d of %d peaks matched)" % (
            avg_shift_cm, matched_peak_count, visible_peaks))
        spec.settings.set_wavenumber_correction(avg_shift_cm)

        self.update_visibility()
        
    def find_nearest_index(self, array, value):
        if len(array) < 1:
            return
        array = np.asarray(array)
        return (np.abs(array - value)).argmin()
