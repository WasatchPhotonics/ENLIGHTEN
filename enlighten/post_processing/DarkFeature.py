import datetime
import logging

import pyqtgraph

from enlighten import common

if common.use_pyside2():
    import PySide2
    from PySide2 import QtCore, QtWidgets, QtGui
else:
    import PySide6
    from PySide6 import QtCore, QtWidgets, QtGui

log = logging.getLogger(__name__)

class DarkFeature:

    def __init__(self, ctl):
        """
        Encapsulates storage and display of dark spectra (but not the actual dark
        correction).
        """
        self.ctl = ctl

        cfu = ctl.form.ui
        self.button_toggle = cfu.pushButton_scope_toggle_dark

        self.populate_placeholder_scope_setup()

        self.button_toggle              .clicked    .connect(self.toggle)
        cfu.pushButton_dark_clear       .clicked    .connect(self.clear_callback)
        cfu.pushButton_dark_load        .clicked    .connect(self.load_callback)
        cfu.pushButton_dark_store       .clicked    .connect(self.store_callback)

    # ##########################################################################
    # public methods
    # ##########################################################################

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        self.ctl.gui.colorize_button(self.button_toggle, spec.app_state.has_dark())

    def toggle(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return

        if spec.app_state.dark is None:
            log.debug("toggle: storing")
            self.store()
        else:
            log.debug("toggle: clearing")
            self.clear()

    def store(self, dark=None):
        """
        Store a new dark.  If one was passed, use that; otherwise take the latest
        recordable_dark from the current spectrometer.

        @note While we track reference_excitation for offset, we don't for dark
              because it is assumed that the laser is off.
        
        @note Don't use this function directly for GUI callbacks, as they will pass
              Qt arguments along.  This is what the otherwise-spurious _callback()
              versions are for, to ignore any extra arguments.
        
        @param dark: could come from Reading in BatchCollection
        """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        app_state = spec.app_state

        timestamp = datetime.datetime.now()
        if dark is None:
            pr = app_state.processed_reading
            if pr is not None:
                spectrum = pr.recordable_dark
                if spectrum is not None:
                    dark = spectrum
                    timestamp = pr.reading.timestamp

        if dark is not None:
            app_state.dark = dark
            app_state.dark_timestamp = timestamp
            app_state.dark_integration_time_ms = spec.settings.state.integration_time_ms

            # should overwrite any KIA tips, no need for token
            self.ctl.marquee.info("dark stored")

        self.display()

    def clear(self, quiet=False):
        spec = self.ctl.multispec.current_spectrometer()
        spec.app_state.clear_dark()
        self.display()
        if not quiet:
            self.ctl.marquee.info("dark cleared")

    def display(self):
        lb = self.ctl.form.ui.label_dark_timestamp

        self.update_enable()

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.curve.setData([])
            self.curve.active = False
            lb.setText("")
            self.ctl.gui.colorize_button(self.button_toggle, False)
            return

        if spec.app_state.has_dark():
            x_axis = self.ctl.generate_x_axis(spec=spec)
            self.ctl.set_curve_data(self.curve, x=x_axis, y=spec.app_state.dark, label="display_dark")

            lb.setText(spec.app_state.dark_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.curve.active = True
        else:
            self.curve.setData([])
            lb.setText("")
            self.curve.active = False

        # todo some kind of observers for dark
        self.ctl.save_options.update_widgets()
        self.ctl.raman_intensity_correction.update_visibility()
        self.ctl.gui.colorize_button(self.button_toggle, spec.app_state.has_dark())

    # ##########################################################################
    # callbacks (truncates any widget arguments)
    # ##########################################################################

    def store_callback(self): self.store()
    def clear_callback(self): self.clear()
    def load_callback (self): self.load()

    # ##########################################################################
    # private methods
    # ##########################################################################

    def load(self):
        """
        Prompts the user to select a previously-saved Measurement (from disk, not
        a loaded thumbnail), and pull the "Dark" column from that.
        
        - If no dark is found in the selected measurement, does nothing.
        - If dark is a column of zeros, uses that.
        - If multiple Measurements are in the file, uses the first.
        
        Better design: add drop-down "..." menu to every ThumbnailWidget, to which we
        can add a bunch of functions, including "Load dark" and "Load reference". This
        would provide better support for "Export" files, where the Measurement we want
        actually is buried within a larger set.
        """
        m = self.ctl.measurement_factory.load_interpolated(self.settings())
        if m is None:
            return

        pr = m.processed_reading
        if pr.dark is None or len(pr.dark) == 0:
            return

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return

        spec.app_state.dark = np.copy(pr.dark)
        spec.app_state.dark_timestamp = m.timestamp
        self.ctl.marquee.info("dark loaded")
        self.display()

    def _enable_buttons(self, flag=True, tt=None):
        spec = self.ctl.multispec.current_spectrometer()
        if tt is None:
            tt = "Clear dark" if spec.app_state.has_dark() else "Store dark"

        self.button_toggle.setEnabled(flag)
        self.button_toggle.setToolTip(tt)

    # Note that we never actually disable the Store/Clear buttons on the 
    # Settings page...
    def update_enable(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self._enable_buttons(False, "disabled without spectrometer")
            return

        if self.ctl.raman_intensity_correction and self.ctl.raman_intensity_correction.enabled:
            self._enable_buttons(False, "dark cannot be cleared while Raman Intensity Correction is enabled")
            return

        self._enable_buttons(True)

    def populate_placeholder_scope_setup(self):
        policy = QtWidgets.QSizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Preferred)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)

        chart = pyqtgraph.PlotWidget(name="Recorded dark spectrum")
        chart.setSizePolicy(policy)

        self.curve = chart.plot([], pen=self.ctl.gui.make_pen(widget="dark"))

        sw = self.ctl.form.ui.stackedWidget_scope_setup_dark_spectrum
        sw.addWidget(chart)
        sw.setCurrentIndex(1)
