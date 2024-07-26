import logging
import numpy as np

from wasatch.ProcessedReading import ProcessedReading

from wasatch.utils import generate_excitation, generate_wavenumbers, generate_wavelengths_from_wavenumbers
from enlighten.ui.ScrollStealFilter import ScrollStealFilter
from enlighten import common
from enlighten.util import unwrap

if common.use_pyside2():
    from PySide2 import QtCore
else:
    from PySide6 import QtCore

log = logging.getLogger(__name__)

##
# Encapsulates interpolation of a ProcessedReading.
#
# @see ORDER_OF_OPERATIONS.md
class InterpolationFeature:
    def __init__(self, ctl):
        self.ctl = ctl

        cfu = self.ctl.form.ui
        self.bt_toggle      = cfu.pushButton_interp_toggle
        self.cb_enabled     = cfu.checkBox_save_interpolation_enabled
        self.dsb_end        = cfu.doubleSpinBox_save_interpolation_end
        self.dsb_incr       = cfu.doubleSpinBox_save_interpolation_incr
        self.dsb_start      = cfu.doubleSpinBox_save_interpolation_start
        self.rb_wavelength  = cfu.radioButton_save_interpolation_wavelength
        self.rb_wavenumber  = cfu.radioButton_save_interpolation_wavenumber

        self.mutex = QtCore.QMutex()
        self.new_axis = None
        self.allowed = False

        self.init_from_config()

        self.bt_toggle          .clicked            .connect(self._toggle_callback)
        self.cb_enabled         .stateChanged       .connect(self._update_widgets)
        self.dsb_end            .valueChanged       .connect(self._update_widgets)
        self.dsb_incr           .valueChanged       .connect(self._update_widgets)
        self.dsb_start          .valueChanged       .connect(self._update_widgets)
        self.rb_wavelength      .toggled            .connect(self._update_widgets)
        self.rb_wavenumber      .toggled            .connect(self._update_widgets)

        for widget in [ self.bt_toggle, self.cb_enabled, self.dsb_end, self.dsb_incr, 
                        self.dsb_start, self.rb_wavelength, self.rb_wavenumber ]:
            widget.setWhatsThis(unwrap("""
                The interpolation icon is chosen to look like a small ruler.
                Like a rule, interpolation generates a fixed, evenly-spaced x-axis
                which allows spectra from different units and different models to
                be easily compared and graphed side-by-side with a single common
                axis. 

                Even with a single spectrometer, this can be useful if your
                x-axis changes periodically, for instance when using Raman Shift
                Correction (as you should!), or if you are using different external
                lasers with slightly different excitation wavelengths.

                Interpolated axes are defined with a starting x-coordinate, 
                ending coordinate, and increment. A real-world analog might be
                a yardstick starting at 0", ending at 36", and incrementing
                by 1/16" steps.

                Note that interpolation is performed AFTER the horizontal ROI is
                cropped."""))

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

        # #431 -- validate interpolation settings
        self.allowed = self.start < self.end and self.incr > 0 and (self.use_wavelengths or self.use_wavenumbers)
        if not self.allowed:
            self.ctl.gui.colorize_button(self.bt_toggle, False)
            self.bt_toggle.setEnabled(False)
            self.bt_toggle.setToolTip("Interpolation cannot be enabled until configured in Settings")
            self.new_axis = None
            self.mutex.unlock()
            return

        self.bt_toggle.setEnabled(True)
        self.ctl.gui.colorize_button(self.bt_toggle, self.enabled)
        if self.enabled:
            self.bt_toggle.setToolTip(f"Disable x-axis interpolation")
        else:
            self.bt_toggle.setToolTip(f"Enable x-axis interpolation")

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
        return generate_excitation(wavelengths=wavelengths, wavenumbers=wavenumbers)

    def process(self, pr, save=True):
        """ 
        This does dark and reference as well as processed and raw.
        """

        if self.new_axis is None:
            log.error("new axis not provided, returning none")
            return 

        if pr is None:
            log.error("Interpolation requires a ProcessedReading")
            return 

        if not (self.use_wavelengths or self.use_wavenumbers):
            log.error("Using neither wavelengths nor wavenumbers, returning none.")
            return 

        old_interpolated = None
        if pr.interpolated:
            if not save:
                old_interpolated = pr.interpolated
            log.debug("re-interpolating (deleting previous interpolation results)")
            pr.interpolated = None

        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()

        interpolated = ProcessedReading()
        old_cropped_axis = None
        old_detector_axis = None

        if self.use_wavelengths:
            if wavelengths is None:
                log.error("Missing required wavelengths")
                return

            interpolated.wavelengths = self.new_axis
            old_cropped_axis = wavelengths
            old_detector_axis = pr.get_wavelengths("orig")

            # generate corresponding wavenumbers if we can
            excitation = self.generate_excitation(wavelengths, wavenumbers, pr.settings)
            if excitation:
                interpolated.wavenumbers = generate_wavenumbers(excitation=excitation, wavelengths=interpolated.wavelengths)

        elif self.use_wavenumbers:
            if wavenumbers is None:
                log.error("Missing required wavenumbers")
                return

            interpolated.wavenumbers = self.new_axis
            old_cropped_axis = wavenumbers
            old_detector_axis = pr.get_wavenumbers("orig")

            # generate corresponding wavelengths if we can
            excitation = self.generate_excitation(wavelengths, wavenumbers, pr.settings)
            if excitation is not None:
                interpolated.wavelengths = generate_wavelengths_from_wavenumbers(excitation=excitation, wavenumbers=interpolated.wavenumbers)

        if old_cropped_axis is None or old_detector_axis is None:
            log.error("Old axis was none, returning none.")
            return None

        processed = pr.get_processed()
        if processed is not None:
            interpolated.processed = np.interp(self.new_axis, old_cropped_axis, processed)
            log.debug(f"interpolated processed to {len(interpolated.processed)} ({self.new_axis[0]:.2f}, {self.new_axis[-1]:.2f})")

        # Note that we are choosing to interpolate raw. That means this is no longer
        # really "raw". However, we're storing it in the ".interpolated" record of
        # ProcessedReading, so that should be fairly clear; they can always access
        # ProcessedReading.raw directly to get the original data.
        raw = pr.get_raw()
        if raw is not None:
            if len(raw) == len(old_detector_axis):
                interpolated.raw = np.interp(self.new_axis, old_detector_axis, raw)
                log.debug(f"interpolated raw to {len(interpolated.raw)}")
            else:
                log.error(f"process: len(old_detector_axis) {len(old_detector_axis)} != len(raw) ({len(raw)})")
                interpolated.raw = None

        dark = pr.get_dark()
        if dark is not None:
            if len(dark) == len(old_detector_axis):
                interpolated.dark = np.interp(self.new_axis, old_detector_axis, dark)
                log.debug(f"interpolated dark to {len(interpolated.dark)}")
            else:
                log.error(f"process: len(old_detector_axis) {len(old_detector_axis)} != len(dark) ({len(dark)})")
                interpolated.dark = None

        reference = pr.get_reference()
        if reference is not None:
            if len(reference) == len(old_detector_axis):
                interpolated.reference = np.interp(self.new_axis, old_detector_axis, reference)
                log.debug(f"interpolated reference to {len(interpolated.reference)}")
            else:
                log.error(f"process: len(old_detector_axis) {len(old_detector_axis)} != len(reference) ({len(reference)})")
                interpolated.reference = None

        if save:
            pr.interpolated = interpolated
        else:
            pr.interpolated = old_interpolated
        return interpolated

    def init_from_config(self):
        log.debug("init_from_config")
        s = "interpolation"

        self.cb_enabled    .setChecked (self.ctl.config.get_bool  (s, "enabled"))
        self.dsb_end       .setValue   (self.ctl.config.get_float (s, "end"))
        self.dsb_incr      .setValue   (self.ctl.config.get_float (s, "incr"))
        self.dsb_start     .setValue   (self.ctl.config.get_float (s, "start"))
        self.rb_wavelength .setChecked (self.ctl.config.get_bool  (s, "use_wavelengths"))
        self.rb_wavenumber .setChecked (self.ctl.config.get_bool  (s, "use_wavenumbers"))
