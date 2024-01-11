import logging
import numpy as np

log = logging.getLogger(__name__)

class RamanIntensityCorrection(object):
    """
    Note this is NOT the same as RamanShiftCorrectionFeature!  
    
    RamanIntensityCorrection uses an EEPROM calibration to correct 
    intensity (y-axis) on Raman spectra.
    """
    
    def __init__(self, ctl):
        self.ctl = ctl
        sfu = ctl.form.ui
        
        self.cb_enable      = sfu.checkBox_raman_intensity_correction
        self.cb_show_curve  = sfu.checkBox_show_srm

        self.supported           = False # show the checkbox because we have an SRM calibration
        self.allowed             = False # enable the checkbox because we're in Raman mode and we've taken a dark
        self.enabled             = False # checkbox is checked
        self.enable_when_allowed = False # checkbox was checked before we went unallowed / invisible for some reason
        self.show_curve          = False
        
        self.curve = self.ctl.graph.add_curve("SRM", rehide=False, in_legend=False)
        self.curve.setVisible(False)

        self.cb_enable.stateChanged.connect(self.enable_callback)
        self.cb_show_curve.stateChanged.connect(self.show_callback)

        self.sync_gui()

        self.ctl.presets.register(self, "enabled", getter=self.get_enabled, setter=self.set_enabled)

    ##
    # Whether Raman Intensity Correction is supported with the current spectrometer.
    # This decides whether the "[ ] enable" checkbox is visible.
    def is_supported(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is not None:
            self.supported = spec.settings.eeprom.has_raman_intensity_calibration() 
        else:
            self.supported = False
        return self.supported

    ##
    # Whether application logic will allow us to enable the feature.
    # This decides whether the "[ ] enable" checkbox is enabled.
    def is_allowed(self):
        def set(flag, tt):
            self.cb_enable.setEnabled(flag)
            self.cb_enable.setToolTip(tt)
            self.allowed = flag
            return flag

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return set(False, "Raman Intensity Correction requires a spectrometer")
        elif not self.is_supported():
            return set(False, "Raman Intensity Correction requires an SRM calibration")
        elif spec.app_state.dark is None:
            return set(False, "Raman Intensity Correction requires a dark measurement")
        elif not (self.ctl.page_nav.doing_raman() or self.ctl.page_nav.doing_expert()):
            return set(False, "Raman Intensity Correction is only valid for Raman and Expert Mode")
        else:
            return set(True, "Raman Intensity Correction optimizes peak intensity using SRM calibration")

    def update_visibility(self):
        self.cb_enable.setEnabled(self.is_allowed())

        if self.supported:
            log.debug(f"update_visibility: show = {self.show_curve}")
            self.curve.setVisible(self.show_curve)

            if self.allowed and self.enable_when_allowed:
                self.cb_enable.setChecked(True)
        else:
            self.enabled = False
            self.cb_enable.setChecked(False)
            self.curve.setVisible(False)

        self.sync_gui()
        
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
