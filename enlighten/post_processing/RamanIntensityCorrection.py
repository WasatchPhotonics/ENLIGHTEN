import logging
import numpy as np

log = logging.getLogger(__name__)

class RamanIntensityCorrection:
    """
    RamanIntensityCorrection uses an EEPROM-stored calibration, generated in the
    factory with NIST SRM standards, to correct intensity (y-axis) on Raman 
    spectra. This is sometimes just called "SRM correction" or just "SRM."

    (Note this is NOT the same as RamanShiftCorrectionFeature, which corrects
    the x-axis rather than the y-axis.)

    Key terms:

    - supported: an SRM calibration is found on the current spectrometer's EEPROM,
        and we're in the Raman or Expert view. "Supported" determines whether the
        widget is even visible in ENLIGHTEN.

    - allowed: given that RamanIntensityCorrection is SUPPORTED, this determines
        whether ENLIGHTEN business logic "allows" SRM to be applied. Currently
        that means that we must have a dark measurement.

    - enabled: whether we are actively applying SRM to new measurements.

    - enabled_when_allowed: whether the user has previously checked "enable", but
        we had to disallow for some reason (like the dark was cleared). This 
        setting is used to automatically re-enable the feature when "supported"
        and "allowed" become true (such as a new dark was successfully stored).
    """
    
    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui
        
        self.cb_enable      = cfu.checkBox_raman_intensity_correction
        self.cb_show_curve  = cfu.checkBox_show_srm
        self.frame          = cfu.frame_srm

        self.supported           = False
        self.allowed             = False
        self.enabled             = False
        self.enable_when_allowed = False
        self.show_curve          = False
        
        self.curve = self.ctl.graph.add_curve("SRM", rehide=False, in_legend=False)
        self.curve.setVisible(False)

        self.cb_enable.stateChanged.connect(self.enable_callback)
        self.cb_show_curve.stateChanged.connect(self.show_callback)

        self.sync_gui()

        self.ctl.presets.register(self, "enabled", getter=self.get_enabled, setter=self.set_enabled)
        self.ctl.page_nav.register_observer("view", self.update_visibility)
        self.ctl.laser_control.register_observer("enabled", self.laser_enabled_callback)

    def is_supported(self):
        """
        Whether Raman Intensity Correction is supported with the current 
        spectrometer, view and technique. This decides whether the widget is even
        visible.

        NOTE: Arguably we could include a check for eeprom.has_horizontal_roi here,
        and even ctl.horiz_roi.enabled.
        """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            log.debug("not supported because no spec")
            self.supported = False
        elif not spec.settings.eeprom.has_raman_intensity_calibration():
            log.debug("not supported because no calibration")
            self.supported = False
        elif not self.ctl.page_nav.doing_raman():
            log.debug("not supported because not doing Raman")
            self.supported = False
        else:
            log.debug("supported because doing Raman and have calibration")
            self.supported = True

        return self.supported

    def is_allowed(self):
        """
        Whether application logic will allow us to enable the feature.
        This decides whether the "[ ] enable" checkbox is clickable.
        """

        def set_allowed(flag, tt):
            log.debug(f"set_allowed: flag {flag}, tt {tt}")
            self.cb_enable.setEnabled(flag)
            self.cb_enable.setToolTip(tt)
            self.allowed = flag
            return flag

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return set_allowed(False, "Raman Intensity Correction requires a spectrometer")
        elif not self.is_supported():
            return set_allowed(False, "Raman Intensity Correction requires an SRM calibration and Raman technique")
        elif spec.app_state.dark is None:
            return set_allowed(False, "Raman Intensity Correction requires a dark measurement")
        else:
            return set_allowed(True, "Apply NIST SRM-calibrated Raman Intensity Correction")

    def update_visibility(self):
        supported = self.is_supported()
        self.frame.setVisible(supported)

        if supported:
            self.curve.setVisible(self.show_curve)

            allowed = self.is_allowed()
            self.cb_enable.setEnabled(allowed)

            if allowed:
                self.cb_enable.setChecked(self.enable_when_allowed)
        else:
            self.enabled = False
            self.cb_enable.setChecked(False)
            self.curve.setVisible(False)

        self.sync_gui()
        
    def laser_enabled_callback(self):            
        log.debug("laser_enabled_callback: start")
        if self.is_allowed():
            log.debug("laser_enabled_callback: apparently we're allowed")
            if not self.enabled:
                log.debug("laser_enabled_callback: trying to suggest tip")
                self.ctl.guide.suggest("Tip: enable Raman Intensity Correction for most accurate Raman intensity", token="enable_raman_intensity_correction")
            else:
                log.debug("laser_enabled_callback: not tipping because enabled {self.enabled}")
        else:
            log.debug("laser_enabled_callback: apparently we're NOT allowed")
        log.debug("laser_enabled_callback: done")

    def show_callback(self):
        self.show_curve = self.cb_show_curve.isChecked()
        log.debug(f"show_callback: show_curve now {self.show_curve}")
        self.update_visibility()

    ## the user manually clicked the enable checkbox
    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()
        self.enable_when_allowed = self.enabled

        if self.enabled:
            self.ctl.guide.clear(token="enable_raman_intensity_correction")
            if not self.ctl.horiz_roi.enabled:
                self.ctl.guide.suggest("Tip: Raman Intensity Correction should only be used with Horizontal ROI enabled", token="srm_roi")

        self.ctl.dark_feature.update_enable()

        self.sync_gui()

    def sync_gui(self):
        # if logic and configuration and past user inputs have enabled the 
        # feature, so indicate on the checkbox; however, disable signals so that
        # a momementary "logic" reason for disabling the feature is not recorded
        # as a user declaration that the feature be disabled.
        if self.enabled != self.cb_enable.isChecked():
            self.cb_enable.blockSignals(True)
            self.cb_enable.setChecked(self.enabled)
            self.cb_enable.blockSignals(False)

    ##
    # @param pr (In/Out) ProcessedReading
    # @param spec (Input) Spectrometer
    #
    # @note supports cropped ProcessedReading (assumes raman intensity correction factors span
    #       the uncorrected raw spectrum)
    def process(self, pr, spec):
        if pr is None or \
           spec is None or \
           not spec.settings.eeprom.has_raman_intensity_calibration():
            return

        factors = spec.settings.raman_intensity_factors
        if factors is None or len(factors) != len(pr.raw):
            return 

        # update visible curve if requested (even if correction is not enabled)
        if self.show_curve and self.ctl.graph.get_x_axis_unit() == "cm":
            if pr.cropped:
                log.debug("displaying normalized SRM curve for ROI")
                roi = spec.settings.eeprom.get_horizontal_roi()
                roi_factors = factors[roi.start:roi.end+1]
                hi = max(roi_factors)
                lo = min(roi_factors)
                norm = np.asarray([ (f - lo) / (hi - lo) for f in roi_factors ], dtype=np.float64)
                self.ctl.set_curve_data(self.curve, y=norm * max(pr.cropped.processed), x=pr.cropped.wavenumbers)
            else:
                log.debug("displaying normalized SRM curve for full detector")
                hi = max(factors)
                lo = min(factors)
                norm = np.asarray([ (f - lo) / (hi - lo) for f in factors ], dtype=np.float64)
                self.ctl.set_curve_data(self.curve, y=norm * max(pr.processed), x=pr.wavenumbers)

        if not self.enabled:
            return

        if pr.interpolated:
            # this shouldn't happen, but just in case
            self.ctl.marquee.error("Raman Intensity Correction cannot be applied AFTER interpolation")
            return

        if pr.cropped:
            log.debug("applying SRM correction to ROI")
            roi = spec.settings.eeprom.get_horizontal_roi()
            for i in range(len(pr.cropped.processed)):
                pr.cropped.processed[i] *= factors[i + roi.start]
        else:
            # note that this scales the entire spectrum, within and without the 
            # ROI, even though the factors are really only applicable/sensible/
            # defined within the ROI
            log.debug("applying SRM correction to full detector")
            self.ctl.marquee.error("Raman Intensity Correction should be performed with ROI enabled")
            pr.processed *= factors

        pr.raman_intensity_corrected = True

    def set_enabled(self, value):
        value = value if isinstance(value, bool) else value.lower() == "true"
        self.cb_enable.setChecked(value)
        self.update_visibility()

    def get_enabled(self):
        return self.cb_enable.isChecked()
