import logging

from enlighten.util import unwrap

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
        widget and button are even visible in ENLIGHTEN. If not supported, the
        button is not visible.

    - allowed: given that RamanIntensityCorrection is SUPPORTED, this determines
        whether ENLIGHTEN business logic "allows" SRM to be applied. Currently
        that means that we must have a dark measurement, and Horizontal ROI is
        enabled. If allowed, the button will be gray (disabled) or red (enabled).
        If not allowed, the button will be orange.

    - enabled: whether we are actively applying SRM to new measurements (red) or
        not (gray or orange, depending on allowed).

    - enabled_when_allowed: whether the user has previously checked "enable", but
        we had to disallow for some reason (like the dark was cleared). This 
        setting is used to automatically re-enable the feature when "supported"
        and "allowed" become true (such as a new dark was successfully stored).
        This is essentially used to decide whether the button is red (allowed and
        enabled) or orange (disallowed and enabled).
    """
    
    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui
        
        self.button = cfu.pushButton_raman_intensity_correction_tristate

        self.supported           = False
        self.allowed             = False
        self.enabled             = False
        self.enable_when_allowed = False

        self.button.clicked.connect(self.button_callback)

        self.button.setWhatsThis(unwrap("""
            Raman Intensity Correction uses an EEPROM-stored calibration, 
            generated in the factory with NIST SRM standards, to correct 
            intensity (y-axis) on Raman spectra. This is sometimes just 
            called "SRM correction". 

            ENLIGHTEN only allows you enable Raman Intensity Correction when
            in Raman or Expert mode, as it is only applicable to Raman spectra.

            Raman Intensity Correction requires a dark spectrum to be stored.
            Therefore, when Raman Intensity Correction is enabled, clearing
            your dark will turn the Raman Intensity Correction button orange
            to indicate the feature is "requested" but not currently running.
            Taking a fresh dark will turn the button back to red and resume
            Raman Intensity Correction.

            Likewise, Raman Intensity Correction requires that the horizontal
            ROI be enabled. This is because NIST SRM standards are only certified
            within a given spectral range, and it would be invalid to extrapolate
            the correction factors outside the configured ROI."""))

        self.ctl.presets.register(self, "enable_when_allowed", getter=self.get_enable_when_allowed, setter=self.set_enable_when_allowed)
        self.ctl.page_nav.register_observer("view", self.update_visibility)
        self.ctl.page_nav.register_observer("mode", self.update_visibility)
        self.ctl.dark_feature.register_observer(self.update_visibility)
        self.ctl.horiz_roi.register_observer(self.update_visibility)

        self.update_visibility()

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

    def is_allowed(self, update_tooltip=True):
        """
        Whether application logic will allow us to enable the feature.
        This decides whether the "[ ] enable" checkbox is clickable.
        """

        def set_allowed(flag, tt):
            # log.debug(f"set_allowed: flag {flag}, tt {tt}")
            if update_tooltip:
                self.button.setToolTip(tt)
                if not flag:
                    self.ctl.marquee.info(tt)
            self.allowed = flag
            return flag

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return set_allowed(False, "Raman Intensity Correction requires a spectrometer")
        elif not self.is_supported():
            return set_allowed(False, "Raman Intensity Correction requires an SRM calibration and Raman technique")
        elif not self.ctl.horiz_roi.enabled:
            return set_allowed(False, "Raman Intensity Correction requires horizontal ROI to be enabled")
        elif spec.app_state.dark is None:
            return set_allowed(False, "Raman Intensity Correction requires a dark measurement")
        else:
            return set_allowed(True, "Can apply NIST SRM-calibrated Raman Intensity Correction")

    def update_visibility(self):
        # log.debug(f"update_visibility: supported was {self.supported}, allowed was {self.allowed}, enabled was {self.enabled}, enable_when_allowed was {self.enable_when_allowed}")

        self.supported = self.is_supported()
        self.button.setVisible(self.supported)

        if self.supported:
            self.allowed = self.is_allowed()
        else:
            self.enabled = False
            self.allowed = False
            self.enable_when_allowed = False

        if self.enabled and not self.allowed:
            self.enabled = False

        if self.enable_when_allowed and self.allowed:
            self.enabled = True

        # log.debug(f"update_visibility: supported now {self.supported}, allowed now {self.allowed}, enabled now {self.enabled}, enable_when_allowed now {self.enable_when_allowed}")

        if self.enabled:
            # log.debug("setting button red because enabled")
            self.ctl.gui.colorize_button(self.button, True)
            self.button.setToolTip("Applying NIST SRM-calibrated Raman Intensity Correction")
        elif self.enable_when_allowed:
            # log.debug("setting button orange because enable_when_allowed")
            self.ctl.gui.colorize_button(self.button, None, tristate=True)
        else:
            # log.debug("setting button gray because neither enabled nor enable_when_allowed")
            self.ctl.gui.colorize_button(self.button, False)
            self.button.setToolTip("Click to apply NIST SRM-calibrated Raman Intensity Correction")

    def button_callback(self):
        # log.debug(f"button_callback: enabled was {self.enabled}, enable_when_allowed was {self.enable_when_allowed}")
        if self.enabled:
            # log.debug("button_callback: had been enabled, so disabling (also disabling enable_when_allowed)")
            self.enabled = False
            self.enable_when_allowed = False
        else:
            # log.debug(f"button_callback: had been disabled")
            if self.enable_when_allowed:
                # log.debug("button_callback: had been enable_when_allowed, so disabling that too")
                self.enable_when_allowed = False
            else:
                if self.allowed:
                    # log.debug("button_callback: allowed, so setting enabled and enable_when_allowed True")
                    self.enabled = True
                    self.enable_when_allowed = True
                else:
                    # log.debug("button_callback: not allowed, so setting enable_when_allowed True")
                    self.enable_when_allowed = True

        # log.debug(f"button_callback: enabled now {self.enabled}, enable_when_allowed now {self.enable_when_allowed}")

        self.update_visibility()

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

        if not self.is_allowed(update_tooltip=False):
            # log.debug("process: not allowed")
            return

        if not self.enabled:
            # log.debug("process: not enabled")
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
            pr.raman_intensity_corrected = True

    def set_enable_when_allowed(self, value):
        self.enable_when_allowed = value if isinstance(value, bool) else value.lower() == "true"
        self.update_visibility()

    def get_enable_when_allowed(self):
        return self.enable_when_allowed
