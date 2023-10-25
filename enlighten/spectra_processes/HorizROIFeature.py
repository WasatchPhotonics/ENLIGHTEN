import pyqtgraph
import logging

log = logging.getLogger(__name__)

class HorizROIFeature:
    """
    Encapsulate the Horizontal ROI feature.
    
    It is very important to understand what it means for this feature to be 
    "enabled," and how that is visualized.
    
    By default, Wasatch software should show all data. Given the choice, we should
    default to exposing the raw, grainy, noisy truth, while giving users access to
    convenient tools to smooth, crop, normalize etc.
    
    Therefore, by default the Horizontal ROI feature is OFF (the full spectrum is
    shown), even if a horizontal ROI is configured in the spectrometer's EEPROM.
    
    If a horizontal ROI is configured, the button is ENABLED (clickable); if no
    ROI is configured, the button is DISABLED (unclickable). In either case, a
    ToolTip should explain the current status.

    If the user clicks the button and enables the Horiz ROI, what will happen 
    depends on whether the user is in Expert Mode or not.


                    ROI in EEPROM           No ROI in EEPROM
    At launch:      - button enabled        - button disabled
                    - button off (grey)     - button off (grey)
                    - ToolTip "click to     - ToolTip "no horiz ROI"
                      crop to horiz ROI"

    

    """
    
    def __init__(self, ctl):
        self.ctl = ctl

        self.button = self.ctl.form.ui.pushButton_roi_toggle 
        self.cb_editing = self.ctl.form.ui.checkBox_edit_horiz_roi

        log.debug("init: defaulting to enabled and user_requested_enabled (i.e. grey)")
        self.enabled = True
        self.user_requested_enabled = True

        self.observers = set()
        self.ctl.graph.register_observer("change_axis", self.change_axis_callback)

        self.button.clicked.connect(self.button_callback)
        self.cb_editing.stateChanged.connect(self.cb_editing_callback)

        self.update_visibility()

    def change_axis_callback(self, old_axis_enum, new_axis_enum):
        self.update_regions()

    def button_callback(self):
        self.enabled = not self.enabled
        self.user_requested_enabled = self.enabled

        log.debug(f"toggle: user_requested_enabled = {self.user_requested_enabled}, enabled = {self.enabled}")
        
        self.update_visibility()

    def cb_editing_callback(self):
        for spec in self.ctl.multispec.get_spectrometers():
            self.update_regions(spec)

    ## provided for RichardsonLucy to flush its Gaussian cache
    def register_observer(self, callback):
        self.observers.add(callback)

    def init_hotplug(self):
        """ auto-enable for spectrometers with ROI """
        spec = self.ctl.multispec.current_spectrometer()
        self.enabled = spec is not None and spec.settings.eeprom.has_horizontal_roi() and self.user_requested_enabled
        log.debug(f"init_hotplug: enabled = {self.enabled}")

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        # disable for now -- still testing
        self.cb_editing.setVisible(False and self.ctl.page_nav.doing_expert())

        log.debug(f"update_visibility: setting enabled to user_requested_enabled {self.user_requested_enabled}")
        self.enabled = self.user_requested_enabled

        # disable for now -- still testing
        if False and spec is not None and spec.settings.eeprom.has_horizontal_roi():
            log.debug(f"update_visibility: showing because spec and ROI")
            self.button.setVisible(True)

            if self.enabled:
                self.ctl.stylesheets.apply(self.button, "gray_gradient_button") 
                self.button.setToolTip("spectra cropped per horizontal ROI")
            else:
                self.ctl.stylesheets.apply(self.button, "red_gradient_button")
                self.button.setToolTip("uncropped spectra shown (curtains indicate ROI limits)")

        else:
            log.debug(f"update_visibility: hiding because no spec or no ROI")
            if spec:
                log.debug(f"update_visibility: roi = {spec.settings.eeprom.get_horizontal_roi()}")
            self.button.setVisible(False)
            self.enabled = False

        log.debug(f"update_visibility: user_requested_enabled = {self.user_requested_enabled}, enabled = {self.enabled}")

        for spec in self.ctl.multispec.get_spectrometers():
            self.update_regions(spec)

        for callback in self.observers:
            callback()

    def is_editing(self):
        return self.cb_editing.isChecked()

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
                spec = self.ctl.multispec.current_spectrometer()
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
            spec = self.ctl.multispec.current_spectrometer()
            if spec is not None:
                settings = spec.settings
        if settings is None:
            return

        roi = settings.eeprom.get_horizontal_roi()
        if roi is None:
            return 
            
        pr.processed_cropped = self.crop(pr.processed, roi=roi)

    def update_regions(self, spec=None):
        if spec is None:
            spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        # only show the curtains if we're editing the ROI
        if not self.is_editing():
            self.ctl.graph.remove_roi_region(spec.roi_region_left)
            self.ctl.graph.remove_roi_region(spec.roi_region_right)
            return

        roi = spec.settings.eeprom.get_horizontal_roi()
        if roi:
            start = roi.start
            end = roi.end
        else:
            start = 0
            end = spec.settings.pixels()

        axis = self.ctl.generate_x_axis(cropped=False)

        log.debug(f"update_regions: roi {roi}, axis {len(axis)} elements, start {start}, end {end}")

        spec.roi_region_left.setRegion((axis[0], axis[start]))
        spec.roi_region_right.setRegion((axis[end], axis[-1]))

        # automatically make regions invisible if they actually extend to/past 
        # the detector edge
        #
        # MZ: how is setOpacity(0) different from remote_roi_region()?
        #     why are we ADDING an opaque region, if I'm reading this
        #     right?
        #
        # MZ: disabling this for now until I understand what it was for.
        #
        # if roi.start <= 0:
        #     spec.roi_region_left.setOpacity(0)
        # else:
        #     spec.roi_region_left.setOpacity(1)
        # 
        # if roi.end >= len(axis):
        #     spec.roi_region_right.setOpacity(0)
        # else:
        #     spec.roi_region_right.setOpacity(1)

        self.ctl.graph.add_roi_region(spec.roi_region_left)
        self.ctl.graph.add_roi_region(spec.roi_region_right)
