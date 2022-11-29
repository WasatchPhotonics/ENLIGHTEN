import datetime
import logging

import PySide2
import pyqtgraph
from PySide2 import QtCore, QtWidgets, QtGui

log = logging.getLogger(__name__)

class DarkFeature:

    def __init__(self,
            generate_x_axis,
            gui,
            marquee,
            measurement_factory,
            multispec,
            save_options,
            set_curve_data,
            raman_intensity_correction,
            button_clear,
            button_load,
            button_store,
            button_toggle,
            lb_timestamp,
            stackedWidget_scope_setup_dark_spectrum,
            gui_make_pen):
        """
        Encapsulates storage and display of dark spectra (but not the actual dark
        correction).
        """

        self.generate_x_axis     = generate_x_axis
        self.gui                 = gui
        self.marquee             = marquee
        self.measurement_factory = measurement_factory
        self.multispec           = multispec
        self.save_options        = save_options
        self.set_curve_data      = set_curve_data
        self.raman_intensity_correction = raman_intensity_correction
        self.stackedWidget_scope_setup_dark_spectrum = stackedWidget_scope_setup_dark_spectrum
        self.button_clear        = button_clear
        self.button_load         = button_load
        self.button_store        = button_store
        self.button_toggle       = button_toggle
        self.lb_timestamp        = lb_timestamp
        self.gui_make_pen        = gui_make_pen
        self.blockers            = []
        self.original_tooltip    = None

        self.raman_intensity_correction.dark_feature = self

        self.populate_placeholder_scope_setup()
        self.button_clear   .clicked    .connect(self.clear_callback)
        self.button_load    .clicked    .connect(self.load_callback)
        self.button_store   .clicked    .connect(self.store_callback)
        self.button_toggle  .clicked    .connect(self.toggle)

    # ##########################################################################
    # public methods
    # ##########################################################################

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        self.gui.colorize_button(self.button_toggle, spec.app_state.dark)

    def toggle(self):
        spec = self.multispec.current_spectrometer()
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
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        timestamp = datetime.datetime.now()
        if dark is None:
            pr = spec.app_state.processed_reading
            if pr is not None:
                spectrum = pr.recordable_dark
                if spectrum is not None:
                    dark = spectrum
                    timestamp = pr.reading.timestamp

        if dark is not None:
            spec.app_state.dark = dark
            spec.app_state.dark_timestamp = timestamp

            # should overwrite any KIA tips, no need for token
            self.marquee.info("dark stored")

        self.display()

    def clear(self, quiet=False):
        spec = self.multispec.current_spectrometer()
        spec.app_state.clear_dark()
        self.display()
        if not quiet:
            self.marquee.info("dark cleared")

    def display(self):
        spec = self.multispec.current_spectrometer()

        self.update_enable()

        if spec is None:
            self.curve.setData([])
            self.curve.active = False
            self.lb_timestamp.setText("")
            self.gui.colorize_button(self.button_toggle, False)
            return

        if spec.app_state.has_dark():
            x_axis = self.generate_x_axis(spec=spec)
            self.set_curve_data(self.curve, x=x_axis, y=spec.app_state.dark, label="display_dark")

            self.lb_timestamp.setText(spec.app_state.dark_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.curve.active = True
        else:
            self.curve.setData([])
            self.lb_timestamp.setText("")
            self.curve.active = False

        # todo some kind of observers for dark
        self.save_options.update_widgets()
        self.raman_intensity_correction.update_visibility()
        self.gui.colorize_button(self.button_toggle, spec.app_state.has_dark())

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
        m = self.measurement_factory.load_interpolated(self.settings())
        if m is None:
            return

        pr = m.processed_reading
        if pr.dark is None or len(pr.dark) == 0:
            return

        spec = self.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return

        spec.app_state.dark = np.copy(pr.dark)
        spec.app_state.dark_timestamp = m.timestamp
        self.marquee.info("dark loaded")
        self.display()

    def enable_buttons(self, flag=True, tt=None):
        spec = self.multispec.current_spectrometer()
        if spec is not None:
            default_tt = "Clear dark" if spec.app_state.has_dark() else "Store dark"
        else:
            default_tt = "disabled without spectrometer"

        if tt is not None:
            log.debug("enable_buttons: %s", tt)

        b = self.button_toggle
        b.setEnabled(flag)
        if flag:
            b.setToolTip(default_tt)
        elif tt is not None:
            b.setToolTip(tt)
        else:
            b.setToolTip("disabled")

    def update_enable(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return self.enable_buttons(False)
        self.enable_buttons(True)

    def handle_blocker(self,source,tooltip,removal=False):
        b = self.button_toggle
        if not removal and self.blockers == []:
            self.original_tooltip = b.toolTip()
        if removal:
            if self.blockers == []:
                log.info(f"blockers is empty, setting tooltip to {self.original_tooltip}")
                b.setEnabled(True)
                b.setToolTip(self.original_tooltip)
                return
            self.blockers = [item for item in self.blockers if item[0] != source] # filters out block from source calling for removal
            if self.blockers != []:
                b.setToolTip(self.blockers[0][1])
            else:
                log.info(f"blockers is empty, setting tooltip to {self.original_tooltip}")
                b.setEnabled(True)
                b.setToolTip(self.original_tooltip)
            return
        self.blockers.append((source,tooltip))
        b.setToolTip(tooltip)
        b.setEnabled(False)
        return

    def populate_placeholder_scope_setup(self):
        policy = QtWidgets.QSizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Preferred)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)

        chart = pyqtgraph.PlotWidget(name="Recorded dark spectrum")
        chart.setSizePolicy(policy)

        self.curve = chart.plot([], pen=self.gui_make_pen(widget="dark"))

        placeholder = self.stackedWidget_scope_setup_dark_spectrum
        placeholder.addWidget(chart)
        placeholder.setCurrentIndex(1)
