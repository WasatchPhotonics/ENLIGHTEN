import logging
import numpy as np
import copy

from wasatch.ProcessedReading import ProcessedReading

from wasatch import utils as wasatch_utils
from enlighten.ScrollStealFilter import ScrollStealFilter
from enlighten import common

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

class InterpolatedProcessedReading:
    # Note ProcessedReading includes dark and reference, so this implicitly does too
    def __init__(self):
        self.wavelengths = None
        self.wavenumbers = None
        self.pixels = 0
        self.processed_reading = ProcessedReading()

    def set_wavelengths(self, a):
        self.wavelengths = a
        self.pixels = len(a)

    def set_wavenumbers(self, a):
        self.wavenumbers = a
        self.pixels = len(a)

##
# I'm not sure we've fully thunk-out all the interpolation use-cases.
#
# @par Processing Pipeline
#
# Currently we interpolate only when we save to disk, and graphing on-screen.
# We don't interpolate what gets sent to Raman matching algorithms, etc.  
# With regard to ENLIGHTEN, we don't interpolate from Wasatch.PY to the GUI 
# (although a limited capability exists within the driver for outside callers).
# 
# @par Saved Measurements
#
# When saving measurements, we still have a column called "pixel".  However, it's
# very much a "virtual" or "interpolated" pixel, which still has some value as
# the "index" of the other axes.  I suppose you could say it's "the pixel on 
# which the interpolated intensity of the interpolated wavelength would presumably
# have fallen in a hypothesized ideal unit spectrometer."  
#
class InterpolationFeature(object):
    def __init__(self, ctl):
        self.ctl = ctl

        sfu = self.ctl.form.ui
        self.bt_toggle      = sfu.pushButton_interp_toggle
        self.cb_enabled     = sfu.checkBox_save_interpolation_enabled
        self.dsb_end        = sfu.doubleSpinBox_save_interpolation_end
        self.dsb_incr       = sfu.doubleSpinBox_save_interpolation_incr
        self.dsb_start      = sfu.doubleSpinBox_save_interpolation_start
        self.rb_wavelength  = sfu.radioButton_save_interpolation_wavelength
        self.rb_wavenumber  = sfu.radioButton_save_interpolation_wavenumber

        self.mutex = QtCore.QMutex()
        self.new_axis = None

        self.init_from_config()

        self.bt_toggle          .clicked            .connect(self._toggle_callback)
        self.cb_enabled         .stateChanged       .connect(self._update_widgets)
        self.dsb_end            .valueChanged       .connect(self._update_widgets)
        self.dsb_incr           .valueChanged       .connect(self._update_widgets)
        self.dsb_start          .valueChanged       .connect(self._update_widgets)
        self.rb_wavelength      .toggled            .connect(self._update_widgets)
        self.rb_wavenumber      .toggled            .connect(self._update_widgets)

        self._update_widgets()

        self.update_visibility()

        # disable scroll stealing
        for widget in [ self.dsb_end, self.dsb_incr, self.dsb_start ]:
            widget.installEventFilter(ScrollStealFilter(widget))

    def total_pixels(self):
        return 0 if self.new_axis is None else len(self.new_axis) 

    def update_visibility(self):
        pass

    def _toggle_callback(self):
        enabled = not self.cb_enabled.isChecked()
        self.cb_enabled.setChecked(enabled)

    def _update_widgets(self):
        """
        Called once at init to set internal state (and apply NOOP to config).
        Called again on widget interaction to update state and config.
        """
        
        self.mutex.lock()

        self.enabled         = self.cb_enabled.isChecked()
        self.use_wavelengths = self.rb_wavelength.isChecked()
        self.use_wavenumbers = self.rb_wavenumber.isChecked()
        self.start           = self.dsb_start.value()
        self.end             = self.dsb_end.value()
        self.incr            = self.dsb_incr.value()

        self.ctl.gui.colorize_button(self.bt_toggle, self.enabled)
        if self.enabled:
            self.bt_toggle.setToolTip(f"Disable x-axis interpolation")
        else:
            self.bt_toggle.setToolTip(f"Enable x-axis interpolation")

        # invalidate stored dark/references
        #
        # MZ: why were we doing this? I don't think we need to do this.
        #     commenting out for now.
        # for spec in self.ctl.multispec.get_spectrometers():
        #     spec.app_state.clear_dark()
        #     spec.app_state.clear_reference()

        s = "interpolation"
        for name in [ "enabled", "use_wavelengths", "use_wavenumbers", "start", "end", "incr" ]:
            self.ctl.config.set(s, name, getattr(self, name))

        self.new_axis = self._generate_axis()

        self.mutex.unlock()

    def _generate_axis(self):
        if not self.enabled:
            return

        if self.end <= self.start:
            log.debug("invalid interpolation endpoints")
            return

        if self.incr <= 0:
            log.debug("invalid interpolation increment")
            return

        log.debug("generating interpolated axis from %.2f to %.2f", self.start, self.end)

        value = self.start

        values = [ value ]
        value += self.incr
        while value <= self.end:
            values.append(value)
            value += self.incr

        return values

    def generate_excitation(self, wavelengths, wavenumbers, settings):
        if settings is not None:
            excitation = settings.excitation()
            if excitation is not None and excitation > 0:
                return excitation
        return wasatch_utils.generate_excitation(wavelengths=wavelengths, wavenumbers=wavenumbers)

    def interpolate_processed_reading(self, pr, wavelengths=None, wavenumbers=None, settings=None):
        """ This does dark and reference as well as processed and raw """
        if self.new_axis is None:
            log.error("new axis not provided, returning none")
            return 

        if pr is None:
            log.error("Interpolation was called without a pr, returning none.")
            return 

        if wavelengths is None and settings is not None:
            wavelengths = settings.wavelengths

        if wavenumbers is None and settings is not None:
            wavenumbers = settings.wavenumbers

        if wavelengths is None and wavenumbers is None:
            log.error("Wavelengths and wavenumbers were none, returning none.")
            return

        if not (self.use_wavelengths or self.use_wavenumbers):
            log.error("Not using wavelengths and not using wavenumbers were none, returning none.")
            return 

        log.debug("interpolating processed reading")

        ipr = InterpolatedProcessedReading()
        old_axis = None

        if self.use_wavelengths:
            ipr.set_wavelengths(self.new_axis)
            old_axis = wavelengths

            # generate wavenumbers if we can
            excitation = self.generate_excitation(wavelengths, wavenumbers, settings)
            if excitation is not None:
                ipr.set_wavenumbers(wasatch_utils.generate_wavenumbers(
                    excitation  = excitation, 
                    wavelengths = ipr.wavelengths))

        elif self.use_wavenumbers:
            ipr.set_wavenumbers(self.new_axis)
            old_axis = wavenumbers

            # generate wavelengths if we can
            excitation = self.generate_excitation(wavelengths, wavenumbers, settings)
            if excitation is not None:
                ipr.set_wavelengths(wasatch_utils.generate_wavelengths_from_wavenumbers(
                    excitation  = excitation, 
                    wavenumbers = ipr.wavenumbers))

        if old_axis is None:
            log.error("Old axis was none, returning none.")
            return None

        if pr.processed is not None:
            ipr.processed_reading.processed = np.interp(self.new_axis, old_axis, pr.processed)

        if pr.raw is not None:
            if len(pr.raw) == len(old_axis):
                ipr.processed_reading.raw = np.interp(self.new_axis, old_axis, pr.raw)
            else:
                log.error(f"ipr: len(old_axis) {len(old_axis)} != len(pr.raw) ({len(pr.raw)})")
                ipr.processed_reading.raw = None

        if pr.dark is not None:
            if len(pr.dark) == len(old_axis):
                ipr.processed_reading.dark = np.interp(self.new_axis, old_axis, pr.dark)
            else:
                log.error(f"ipr: len(old_axis) {len(old_axis)} != len(pr.dark) ({len(pr.dark)})")
                ipr.processed_reading.dark = None

        if pr.reference is not None:
            ipr.processed_reading.reference = np.interp(self.new_axis, old_axis, pr.reference)

        # The weird case of extrapolating a cropped ROI.  Consider that we had
        # an original spectrum "abcdefghijklmnopqrstuvwxyz".  We then cropped
        # it to "ghijklmnopqrstu".  We are now extrapolating it out to
        # "ggggggggggggGHIJKLMNOPQRSTUuuuuuuuuuuu".  Even if we've cropped it
        # down, we're still obliged to extrapolate out to the newly defined range,
        # and the only pixels we have "qualified" as being valid to extrapolate
        # are those within the ROI.
        roi = settings.eeprom.get_horizontal_roi()
        log.debug("processed_cropped is %s and settings is %s and roi is %s",
            pr.processed_cropped is not None,
            settings is not None,
            roi is not None)
        if pr.processed_cropped is not None and settings is not None and roi is not None:
            log.debug("interpolating cropped spectrum to new axis of %d pixels", len(self.new_axis))
            old_axis_cropped = self.ctl.horiz_roi.crop(old_axis, roi=roi)
            ipr.processed_reading.processed_cropped = np.interp(self.new_axis, old_axis_cropped, pr.processed_cropped)

        return ipr

    def init_from_config(self):
        log.debug("init_from_config")
        s = "interpolation"

        self.cb_enabled.setChecked(self.ctl.config.get_bool(s,"enabled"))
        self.dsb_end.setValue(self.ctl.config.get_float(s, "end"))
        self.dsb_incr.setValue(self.ctl.config.get_float(s, "incr"))
        self.dsb_start.setValue(self.ctl.config.get_float(s, "start"))
        self.rb_wavelength.setChecked(self.ctl.config.get_bool(s, "use_wavelengths"))
        self.rb_wavenumber.setChecked(self.ctl.config.get_bool(s, "use_wavenumbers"))
