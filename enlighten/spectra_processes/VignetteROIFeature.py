import logging

log = logging.getLogger(__name__)

##
# Encapsulate the horizontal ROI feature.
#
# It is very important to understand what it means for this feature to be 
# "enabled," and how that is visualized.
#
# BY DEFAULT, spectrometers with "cropped" spectra (spectrometers with valid 
# horizontal_roi_start/stop fields populated in the EEPROM) DO NOT show the 
# cropped "wings" of the spectra in ENLIGHTEN.  The whole purpose of configuring
# a horizontal ROI is to NOT SHOW those noisy, filtered, useless fringes.
#
# Therefore, the DEFAULT mode is to crop the ROI.  This means the CropROIFeature 
# is ENABLED, and the button is visualized in a non-scary "gray" style.
#
# The RARE case is for a user to wish to see those low-signal fringes, and 
# therefore we visualize that mode (with "curtains" on the ends) with the RED,
# SCARY style.
#           
#     enabled:       True        False
#     button CSS:    gray        red
#     crop:          yes         no
#
class CropROIFeature(object):
    
    def __init__(self,
            graph,
            multispec,
            stylesheets,
            button):
        self.graph = graph
        self.multispec = multispec
        self.stylesheets = stylesheets

        self.button = button

        self.enabled = True
        self.user_requested_enabled = True

        self.observers = set()

        # self-register with Graph
        self.graph.crop_roi = self

        self.button.clicked.connect(self.toggle)

        self.update_visibility()

    def toggle(self):
        self.enabled = not self.enabled
        self.user_requested_enabled = self.enabled

        log.debug(f"toggle: user_requested_enabled = {self.user_requested_enabled}, enabled = {self.enabled}")
        
        # re-center cursor if disabling ROI made current position fall off the graph
        self.graph.cursor.set_range(self.graph.generate_x_axis())
        if self.graph.cursor.is_outside_range():
            self.graph.cursor.center()

        self.update_visibility()

    ## provided for RichardsonLucy to flush its Gaussian cache
    def register_observer(self, callback):
        self.observers.add(callback)

    def init_hotplug(self):
        """ auto-enable for spectrometers with ROI """
        spec = self.multispec.current_spectrometer()
        self.enabled = spec is not None and spec.settings.eeprom.has_horizontal_roi() and self.user_requested_enabled
        log.debug(f"init_hotplug: enabled = {self.enabled}")

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()

        self.enabled = self.user_requested_enabled

        if spec is not None and spec.settings.eeprom.has_horizontal_roi():
            self.button.setVisible(True)

            if self.enabled:
                self.stylesheets.apply(self.button, "gray_gradient_button") 
                self.button.setToolTip("spectra cropped per EEPROM horizontal ROI")
            else:
                self.stylesheets.apply(self.button, "red_gradient_button")
                self.button.setToolTip("uncropped spectra shown (curtains indicate ROI limits)")

        else:
            self.button.setVisible(False)
            self.enabled = False

        log.debug(f"update_visibility: user_requested_enabled = {self.user_requested_enabled}, enabled = {self.enabled}")

        for spec in self.multispec.get_spectrometers():
            self.graph.update_roi_regions(spec)

        for callback in self.observers:
            callback()

    ##
    # Called by LOTS of classes :-(
    #
    # @param spectrum (Input) Note this is really "array" or "data", as this can 
    #                      be (and often is) used to crop an x-axis of wavelengths 
    #                      or wavenumbers.
    # @param force (Input) if we've loaded a saved spectrum from disk, and the 
    #                      "processed" array literally has fewer values than the 
    #                      x-axes, and the Measurement metadata clearly shows
    #                      an ROI, then we can assume that the Measurement was
    #                      cropped when it was saved / generated, and we really
    #                      have no choice to un-crop it now (other than by
    #                      prefixing/suffixing zeros or something).  
    # @returns cropped spectrum
    # @note does not currently check .enabled
    def crop(self, spectrum, spec=None, roi=None, force=False):
        if spectrum is None:
            return

        if roi is None:
            if spec is None:
                spec = self.multispec.current_spectrometer()
            if spec is not None:
                roi = spec.settings.eeprom.get_horizontal_roi()

        if roi is None:
            return spectrum

        orig_len = len(spectrum)

        if not roi.valid() or roi.start >= orig_len or roi.end >= orig_len:
            return spectrum

        # log.debug("crop: cropping spectrum of %d pixels to %d (%s)", orig_len, roi.len, roi)
        return roi.crop(spectrum)
        
    ##
    # Called by Controller.
    # 
    # @param pr (In/Out) ProcessedReading
    # @param settings (Input) SpectrometerSettings
    #
    # @returns Nothing (side-effect: populates pr.processed_cropped)
    def process(self, pr, settings=None):
        if not self.enabled:
            return

        if pr is None or pr.processed is None:
            return

        if settings is None:
            spec = self.multispec.current_spectrometer()
            if spec is not None:
                settings = spec.settings
        if settings is None:
            return

        roi = settings.eeprom.get_horizontal_roi()
        if roi is None:
            return 
            
        pr.processed_cropped = self.crop(pr.processed, roi=roi)
