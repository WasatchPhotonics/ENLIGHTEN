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

##
# Encapsulates interpolation of a ProcessedReading.
#
# @see ORDER_OF_OPERATIONS.md
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

    def __repr__(self):
        s = "InterpolationFeature<enabled %s, use %s, start %s, end %s, incr %s, axis %s>" % (
            self.enabled,
            'wavelengths' if self.use_wavelengths else 'wavenumbers', 
            self.start,
            self.end,
            self.incr,
            "None" if self.new_axis is None else f"({self.new_axis[0]}, {self.new_axis[-1]})")
        return s

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

    def process(self, pr):
        """ This does dark and reference as well as processed and raw """

        if self.new_axis is None:
            log.error("new axis not provided, returning none")
            return 

        if pr is None:
            log.error("Interpolation requires a ProcessedReading")
            return 

        if not (self.use_wavelengths or self.use_wavenumbers):
            log.error("Using neither wavelengths nor wavenumbers, returning none.")
            return 

        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()

        log.debug("interpolating processed reading")

        interpolated = ProcessedReading()
        old_axis = None

        if self.use_wavelengths:
            if wavelengths is None:
                log.error("Missing required wavelengths")
                return

            interpolated.wavelengths = self.new_axis
            old_axis = wavelengths

            # generate corresponding wavenumbers if we can
            excitation = self.generate_excitation(wavelengths, wavenumbers, pr.settings)
            if excitation:
                interpolated.wavenumbers = wasatch_utils.generate_wavenumbers(excitation=excitation, wavelengths=interpolated.wavelengths)

        elif self.use_wavenumbers:
            if wavenumbers is None:
                log.error("Missing required wavenumbers")
                return

            interpolated.wavenumbers = self.new_axis
            old_axis = wavenumbers

            # generate corresponding wavelengths if we can
            excitation = self.generate_excitation(wavelengths, wavenumbers, pr.settings)
            if excitation is not None:
                interpolated.wavelengths = wasatch_utils.generate_wavelengths_from_wavenumbers(excitation=excitation, wavenumbers=interpolated.wavenumbers)

        if old_axis is None:
            log.error("Old axis was none, returning none.")
            return None

        processed = pr.get_processed()
        if processed is not None:
            interpolated.processed = np.interp(self.new_axis, old_axis, processed)

        raw = pr.get_raw()
        if raw is not None:
            if len(raw) == len(old_axis):
                interpolated.raw = np.interp(self.new_axis, old_axis, raw)
            else:
                log.error(f"process: len(old_axis) {len(old_axis)} != len(raw) ({len(raw)})")
                interpolated.raw = None

        dark = pr.get_dark()
        if dark is not None:
            if len(dark) == len(old_axis):
                interpolated.dark = np.interp(self.new_axis, old_axis, dark)
            else:
                log.error(f"process: len(old_axis) {len(old_axis)} != len(dark) ({len(dark)})")
                interpolated.dark = None

        reference = pr.get_reference()
        if reference is not None:
            if len(reference) == len(old_axis):
                interpolated.reference = np.interp(self.new_axis, old_axis, reference)
            else:
                log.error(f"process: len(old_axis) {len(old_axis)} != len(reference) ({len(reference)})")
                interpolated.dark = None

        pr.interpolated = interpolated

    def init_from_config(self):
        log.debug("init_from_config")
        s = "interpolation"

        self.cb_enabled    .setChecked (self.ctl.config.get_bool  (s, "enabled"))
        self.dsb_end       .setValue   (self.ctl.config.get_float (s, "end"))
        self.dsb_incr      .setValue   (self.ctl.config.get_float (s, "incr"))
        self.dsb_start     .setValue   (self.ctl.config.get_float (s, "start"))
        self.rb_wavelength .setChecked (self.ctl.config.get_bool  (s, "use_wavelengths"))
        self.rb_wavenumber .setChecked (self.ctl.config.get_bool  (s, "use_wavenumbers"))
