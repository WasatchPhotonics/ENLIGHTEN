import pyqtgraph
import logging

from enlighten.scope.Cursor import AxisConverter
from enlighten import common

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
class HorizROIFeature:
    
    def __init__(self, ctl):
        self.ctl = ctl

        self.button = self.ctl.form.ui.pushButton_roi_toggle # compromise

        log.debug("init: defaulting to enabled and user_requested_enabled (i.e. grey)")
        self.enabled = True
        self.user_requested_enabled = True

        self.observers = set()
        self.ctl.graph.register_observer("change_axis", self.change_axis_callback)

        self.converter = AxisConverter(ctl)

        # create lines to manipulate the ROI (could try to make these 
        # actual Cursor objects later, not sure it's worth it now)
        self.start = pyqtgraph.InfiniteLine(movable=True, pen=self.ctl.gui.make_pen(color="lightsalmon"))
        self.end   = pyqtgraph.InfiniteLine(movable=True, pen=self.ctl.gui.make_pen(color="lightsalmon"))
        self.lines = { "start": self.start, "end": self.end }
        for label, line in self.lines.items():
            log.debug(f"instantiated {label}")
            line.setVisible(False)
            self.ctl.graph.add_item(line)

        # self-register with scope.Graph (remove when refactoring Graph)
        self.ctl.graph.horiz_roi = self

        # bindings
        self.button .clicked            .connect(self.toggle)
        self.start  .sigPositionChanged .connect(self.start_moved_callback)
        self.end    .sigPositionChanged .connect(self.end_moved_callback)

        self.update_visibility()

    def toggle(self):
        self.enabled = not self.enabled
        self.user_requested_enabled = self.enabled

        log.debug(f"toggle: user_requested_enabled = {self.user_requested_enabled}, enabled = {self.enabled}")
        
        self.update_visibility()

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
            for label, line in self.lines.items():
                line.setVisible(False)
            return

        log.debug(f"update_visibility: setting enabled to user_requested_enabled {self.user_requested_enabled}")
        self.enabled = self.user_requested_enabled

        if spec is not None and spec.settings.eeprom.has_horizontal_roi():
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

        self.update_line(spec, "end",   spec.settings.eeprom.roi_horizontal_end)
        self.update_line(spec, "start", spec.settings.eeprom.roi_horizontal_start)

        for spec in self.ctl.multispec.get_spectrometers():
            self.ctl.graph.update_roi_regions(spec)

        for callback in self.observers:
            callback()

    def update_line(self, spec, label, pixel):
        """ 
        We're doing update_visibility and we want to make sure each line is set
        to the pixel specified in the ROI.
        """
        axis = self.ctl.graph.current_x_axis
        x_axis = self.ctl.graph.generate_x_axis()
        line = self.lines[label]

        if not self.enabled or x_axis is None or x_axis[-1] - x_axis[0] <= 0:
            log.debug(f"update_line: hiding {label} because enabled {self.enabled} or bad x_axis")
            line.setVisible(False)
            return

        x = self.converter.convert(spec=spec, old_axis=common.Axes.PIXELS, new_axis=axis, x=pixel)
        if x is None:
            log.debug(f"update_line: failed to convert {label} to axis {axis}, pixel {pixel}")
            return

        log.debug(f"update_line: updating {label} from pixel {pixel} to x {x} on axis {axis}")
        line.setValue(x)
        line.setVisible(True)

    def change_axis_callback(self, old_axis, new_axis):
        self.update_visibility()

    def start_moved_callback(self, pos):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        x = self.start.getXPos()
        limit = self.end.getXPos() - 10 # don't really care which unit
        if x > limit:
            log.debug(f"bumping start {x} back down to {limit}")
            self.start.setValue(limit)
            return

        pixel = self.line_moved(spec, self.start)
        if pixel is None:
            return

        log.debug(f"start_moved: setting roi_start to pixel {pixel} based on x {x}")
        spec.settings.eeprom.roi_horizontal_start = pixel
        self.ctl.graph.update_roi_regions(spec)

    def end_moved_callback(self, pos):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        x = self.end.getXPos()
        limit = self.start.getXPos() + 10 # don't really care which unit
        if x < limit:
            log.debug(f"bumping end back up to {limit} from {x}")
            self.end.setValue(limit)
            return

        pixel = self.line_moved(spec, self.end)
        if pixel is None:
            return

        log.debug(f"end_moved: setting roi_end to pixel {pixel} based on x {x}")
        spec.settings.eeprom.roi_horizontal_end = pixel
        self.ctl.graph.update_roi_regions(spec)

    def line_moved(self, spec, line):
        """ 
        The user dragged the line, so lookup the x-coordinate in the Graph 
        axis (wl, wn etc) and convert back to pixels so we can update the 
        EEPROM's ROI 
        """
        x_axis = self.ctl.graph.generate_x_axis() # assume selected spectrometer
        if x_axis is None:
            return

        if x_axis[-1] - x_axis[0] <= 0:
            return

        old_x = line.getXPos()
        pixel = self.converter.convert(spec=spec, old_axis=self.ctl.graph.current_x_axis, new_axis=common.Axes.PIXELS, x=old_x)
        if pixel is None:
            return None

        return round(pixel)

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
