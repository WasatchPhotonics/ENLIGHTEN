import logging
import numpy as np

log = logging.getLogger(__name__)

##
# This object has several states:
#
# Note this is NOT the same as RamanShiftCorrectionFeature!  
# RamanShiftCorrectionFeature uses a single Raman measurement to correct the 
# x-axis on Raman measurements; this uses an EEPROM calibration to correct 
# intensity (y-axis) on Raman spectra.
class RamanIntensityCorrection(object):
    
    def __init__(self, ctl):
        self.ctl = ctl
        
        self.cb_enable = ctl.form.ui.checkBox_raman_intensity_correction

        self.supported           = False # show the checkbox because we have an SRM calibration
        self.allowed             = False # enable the checkbox because we're in Raman mode and we've taken a dark
        self.enabled             = False # checkbox is checked
        self.enable_when_allowed = False # checkbox was checked before we went unallowed / invisible for some reason

        self.cb_enable.stateChanged.connect(self.enable_callback)

        self.sync_gui()

        self.ctl.presets.register(self, ["enabled"])

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

        if self.supported and self.allowed:
            if self.enable_when_allowed:
                self.cb_enable.setChecked(True)
        else:
            self.enabled = False
            self.cb_enable.setChecked(False)

        self.sync_gui()
        
    ## the user manually clicked the enable checkbox
    def enable_callback(self):
        self.enabled = self.cb_enable.isChecked()
        self.enable_when_allowed = self.enabled
        self.check_block_dark()

        if self.enabled:
            self.ctl.guide.clear(token="enable_raman_intensity_correction")

        self.sync_gui()

    def check_block_dark(self):
        spec = self.ctl.multispec.current_spectrometer()
        log.info("checking if need to block dark")
        if spec.app_state.dark is not None and self.enabled:
            log.info("passing block to dark feature")
            self.ctl.dark_feature.handle_blocker(self,"Raman Intensity Correction must be disabled to take a dark")
        if not self.enabled:
            self.ctl.dark_feature.handle_blocker(self,"",removal=True)

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
        if not self.enabled or \
                pr is None or \
                spec is None or \
                not spec.settings.eeprom.has_raman_intensity_calibration():
            return

        factors = spec.settings.raman_intensity_factors
        if factors is None or len(factors) != len(pr.raw):
            return 

        if pr.is_cropped():
            roi = spec.settings.eeprom.get_horizontal_roi()
            # probably a faster Numpy way to do this
            for i in range(len(pr.processed_cropped)):
                pr.processed_cropped[i] *= factors[i + roi.start]
        else:
            # note that this scales the entire spectrum, within and without the 
            # ROI, even though the factors are really only applicable/sensible/
            # defined within the ROI
            pr.processed *= factors

        pr.raman_intensity_corrected = True

    def set_preset(self, attr, value):
        if attr == "enabled":
            self.cb_enable.setChecked(value.lower() == "true")
            self.update_visibility()

    def get_preset(self, attr):
        if attr == "enabled":
            return self.cb_enable.isChecked()
