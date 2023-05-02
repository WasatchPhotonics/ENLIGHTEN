import pyqtgraph
import logging
import numpy as np

from enlighten import util
from enlighten import common
from wasatch import utils as wasatch_utils
from enlighten.ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

class Cursor(object):
    """
    Encapsulates the main "scope capture" cursor (vertical red line) on the
    scope graph.  Note that StatusBar will register as an observer.
    """
    def __init__(self,
            button_dn,
            button_up,
            cb_enable,
            ds_value,
            graph):

        self.button_dn       = button_dn
        self.button_up       = button_up
        self.cb_enable       = cb_enable
        self.ds_value        = ds_value
        self.graph           = graph

        self.multispec       = None
        self.current_percent = None
        self.center()

        self.observers = []

        # place a movable vertical line on the scope graph
        self.cursor = pyqtgraph.InfiniteLine(movable=True, pen=self.graph.gui.make_pen(widget="scope_cursor"))
        self.cursor.setVisible(False)
        self.graph.add_item(self.cursor)

        # bindings
        self.cursor              .sigPositionChanged     .connect(self.moved_callback)
        self.cb_enable           .stateChanged           .connect(self.enable_callback)
        self.ds_value            .valueChanged           .connect(self.cursor.setValue)
        self.ds_value                                    .installEventFilter(ScrollStealFilter(self.ds_value))
        self.button_up           .clicked                .connect(self.up_callback)
        self.button_dn           .clicked                .connect(self.dn_callback)

        self.cb_enable.setChecked(False)

        # add Cursor to Graph
        self.graph.cursor = self

        self.px_to_wavelen = lambda x, spec: wasatch_utils.pixel_to_wavelength(x, spec.settings.eeprom.wavelength_coeffs)
        self.wavelen_to_wavenum = lambda x, spec: wasatch_utils.wavelength_to_wavenumber(x, spec.settings.eeprom.excitation_nm_float)
        self.wavenum_to_wavelen = lambda x, spec: wasatch_utils.wavenumber_to_wavelength(spec.settings.eeprom.excitation_nm_float, x)
        # noticed you could walk the cursor for px_to_wavenum, 
        # think it's an off by 1 error due to the 2 searchsorted
        self.px_to_wavenum = lambda x, spec: wasatch_utils.wavelength_to_wavenumber(self.px_to_wavelen(x-1, spec), spec.settings.eeprom.excitation_nm_float)
        self.conversions = {
            (common.Axes.PIXELS,common.Axes.WAVELENGTHS): self.px_to_wavelen,
            (common.Axes.PIXELS,common.Axes.WAVENUMBERS): self.px_to_wavenum,
            (common.Axes.WAVELENGTHS,common.Axes.PIXELS): self.wavelen_to_pixels,
            (common.Axes.WAVELENGTHS,common.Axes.WAVENUMBERS): self.wavelen_to_wavenum,
            (common.Axes.WAVENUMBERS,common.Axes.PIXELS): self.wavenum_to_pixels,
            (common.Axes.WAVENUMBERS,common.Axes.WAVELENGTHS): self.wavenum_to_wavelen,
            }


    def wavenum_to_pixels(self, x, spec):
        log.debug(f"wave num to pixels called")
        specs = self.multispec.get_spectrometers()
        for spec in specs:
            wavenums = spec.settings.wavenumbers
            log.debug(f"checking spec with wavenums {wavenums[0]} and {wavenums[-1]}")
            if x > wavenums[0] and x <= wavenums[-1]:
                x = np.searchsorted(wavenums, x, side="right")
                log.debug(f"new x value is {x}")
                return x

    def wavelen_to_pixels(self, x, spec):
        log.debug(f"wave len to pixels called for value {x}")
        specs = self.multispec.get_spectrometers()
        for spec in specs:
            wavelengths = spec.settings.wavelengths
            log.debug(f"checking spec with wavelengths {wavelengths[0]} and {wavelengths[-1]}")
            if x > wavelengths[0] and x <= wavelengths[-1]:
                x = np.searchsorted(wavelengths, x, side="right")
                log.debug(f"new x value is {x}")
                return x

    def register_observer(self, callback):
        self.observers.append(callback)

    def deregister_observer(self, callback):
        self.observers.pop(callback, None)

    def set_enabled(self, flag):
        self.cb_enable.setChecked(flag)

    def is_enabled(self):
        return self.cb_enable.isChecked()

    def set_value(self, value):
        self.cursor.setValue(value)

    def set_suffix(self, suffix):
        log.debug(f"set suffix to {suffix}")
        self.ds_value.setSuffix(suffix)

    def set_range(self, array=None):
        if array is not None:
            self.ds_value.setMinimum(array[0])
            self.ds_value.setMaximum(array[-1])

    def recenter(self):
        if self.current_percent is None:
            self.center()
        else:
            self.move_perc(self.current_percent)

    def up_callback(self):
        util.incr_spinbox(self.ds_value)
        self.update()

    def dn_callback(self):
        util.decr_spinbox(self.ds_value)
        self.update()

    def convert_location(self, old_axis, new_axis):
        log.debug(f"convert location from {old_axis} to {new_axis}")
        spec = self.multispec.current_spectrometer()
        if spec is None:
            log.debug(f"spec is none so not updating x")
            return
        x = self.cursor.getXPos()

        conversion_func = self.conversions.get((old_axis,new_axis), None)
        if conversion_func is None:
            log.debug(f"conversion func is none so not updating x")
            return

        new_x = conversion_func(x, spec)
        self.set_value(new_x)
        self.update()
    
    def update(self):
        if not self.cb_enable.isChecked():
            return

        if self.multispec is None:
            return

        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        try:
            # Get precise cursor value as drawn on screen using chart x-axis
            x = self.cursor.getXPos()

            # MZ: Note that we're taking x-axis and spectrum FROM THE GRAPH, not
            #     from "state" or "history" or anything.  That's probably the right
            #     thing to do for a graph cursor.
            curve = spec.curve
            x_axis   = curve.getData()[ 0]
            spectrum = curve.getData()[-1] 
            log.debug(f"in update x axis from graph is len {len(x_axis)}")

            # Find the CLOSEST index on the x-axis to the cursor's x-index
            # https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
            #
            # MZ: seems it would be worth offering interpolation here?
            x = np.abs(x_axis - x).argmin() 
            y = spectrum[x]

            # display the corresponding spectral value
            for callback in self.observers:
                callback(x, y)
        except:
            log.error("Error updating cursor", exc_info=1)

    def enable_callback(self):
        enabled = self.cb_enable.isChecked()
        log.debug("enable_callback: enabled = %s", enabled)

        self.ds_value       .setEnabled(enabled)
        self.button_up      .setEnabled(enabled)
        self.button_dn      .setEnabled(enabled)
        self.cursor         .setVisible(enabled)

        if enabled and self.is_outside_range():
            self.center()

    def moved_callback(self, pos):
        x_axis = self.graph.generate_x_axis() # assume selected spectrometer
        log.debug(f"cursor moved callback x_axis len is {len(x_axis)}")
        if x_axis is None:
            log.error("moved_callback: no x_axis?!")
            self.ds_value.setEnabled(False)
            return

        if x_axis[-1] - x_axis[0] == 0:
            log.error("moved_callback: invalid x_axis: %s", x_axis)
            self.ds_value.setEnabled(False)
            return

        self.ds_value.setEnabled(True)

        x = self.cursor.getXPos()
        self.current_percent = float(x - x_axis[0]) / float(x_axis[-1] - x_axis[0])
        log.debug("moved_callback: x = %.2f (%.2f%%)", x, 100.0 * self.current_percent)

        # a screwy wavecal can cause infinite recursion here
        self.ds_value.blockSignals(True)
        self.ds_value.setValue(x)
        self.ds_value.blockSignals(False)

        self.update()

    def move_perc(self, perc):
        x_axis = self.graph.generate_x_axis() # assume selected
        if x_axis is None:
            return

        x_range = float(x_axis[-1] - x_axis[0])
        x_value = x_axis[0] + x_range * perc
        self.cursor.setValue(x_value)
        log.debug("move_perc: x = %.2f (%.2f%%)", x_value, perc)

    def is_outside_range(self):
        x_axis = self.graph.generate_x_axis() # assume selected
        if x_axis is None:
            return

        value = self.cursor.getXPos()
        return value < x_axis[0] or value > x_axis[-1]

    def center(self):
        x_axis = self.graph.generate_x_axis() # assume selected
        if x_axis is None:
            return

        self.set_range(array=x_axis)

        midpoint = x_axis[0] + (x_axis[-1] - x_axis[0]) / 2
        self.cursor.setValue(midpoint)
        log.debug("centering: midpoint of (%.2f, %.2f) is %.2f", x_axis[0], x_axis[-1], midpoint)
