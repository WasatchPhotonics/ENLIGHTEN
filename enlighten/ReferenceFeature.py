import datetime
import logging
import numpy as np

import PySide2
import pyqtgraph
from PySide2 import QtCore, QtWidgets, QtGui

log = logging.getLogger(__name__)

##
# This class is sufficiently close to DarkFeature that it's tempting to make them
# one inherit the other, or derive both from a common ABC.
class ReferenceFeature:

    def __init__(self,
            graph,
            gui,
            marquee,
            measurement_factory,
            multispec,
            page_nav,
            save_options,
            set_curve_data,
            button_clear,
            button_load,
            button_store,
            button_toggle,
            frame_setup,
            lb_timestamp,
            stacked_widget,
            gui_make_pen):

        self.graph               = graph
        self.gui                 = gui
        self.marquee             = marquee
        self.measurement_factory = measurement_factory
        self.multispec           = multispec
        self.page_nav            = page_nav
        self.save_options        = save_options
        self.set_curve_data      = set_curve_data

        self.button_clear        = button_clear
        self.button_load         = button_load
        self.button_store        = button_store
        self.button_toggle       = button_toggle
        self.frame_setup         = frame_setup
        self.lb_timestamp        = lb_timestamp
        self.gui_make_pen        = gui_make_pen
        self.stacked_widget      = stacked_widget

        self.populate_placeholder_scope_setup()

        # these should be invisible when feature deemed inappropriate
        self.visibility_widgets = [ self.frame_setup, 
                                    self.button_toggle, 
                                    self.button_store,
                                    self.save_options.cb_reference ]

        # no _callback functions because no arguments
        self.button_clear   .clicked    .connect(self.clear)
        self.button_load    .clicked    .connect(self.load)
        self.button_store   .clicked    .connect(self.store)
        self.button_toggle  .clicked    .connect(self.toggle)

    # ##########################################################################
    # public methods
    # ##########################################################################

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        if spec is None:
            return

        # hide reference widgets in non-referenced mode (basically, Raman)
        if self.page_nav.doing_raman():
            [ widget.setVisible(False) for widget in self.visibility_widgets ]
            return

        [ widget.setVisible(True) for widget in self.visibility_widgets ]

        self.gui.colorize_button(self.button_toggle, spec.app_state.has_reference())

    def toggle(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return

        if spec.app_state.reference is None:  # diff: not app_state_has_array()
            log.debug("toggle: setting")
            self.store()
        else:
            log.debug("toggle: clearing")
            self.clear()

    ##
    # Take the last scan-averaged, boxcar-smoothed, dark-corrected
    # processed spectrum we have (before post-processing was applied).
    #
    # Note that while DarkFeature.store() can take an argument, this method
    # doesn't.  That's because we have a use-case for automatically generated/
    # passed darks (BatchCollection), but currently don't for references (but
    # could add one later).  Eventually we should make this method match
    # DarkFeature.store() in structure.
    def store(self): 
        spec = self.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return

        app_state = spec.app_state

        pr = app_state.processed_reading
        if pr is not None:
            spectrum = pr.recordable_reference
            if spectrum is not None:
                app_state.reference = np.copy(spectrum)
                app_state.reference_timestamp = pr.reading.timestamp
                app_state.reference_is_dark_corrected = pr.dark_corrected
                app_state.reference_excitation = spec.settings.excitation()
                app_state.reference_integration_time_ms = spec.settings.state.integration_time_ms
                self.marquee.info("reference stored")

        self.display()

    def clear(self, quiet=False):
        spec = self.multispec.current_spectrometer()
        spec.app_state.clear_reference()
        self.display()
        if not quiet:
            self.marquee.info("reference cleared")

    def display(self):
        spec = self.multispec.current_spectrometer()

        self.update_enable()

        if spec is None:
            self.curve.setData([])
            self.curve.active = False
            self.lb_timestamp.setText("")
            self.gui.colorize_button(self.button_toggle, False)
            return

        if spec.app_state.has_reference():
            x_axis = self.graph.generate_x_axis(spec=spec)
            self.set_curve_data(self.curve, x=x_axis, y=spec.app_state.reference, label="display_reference")

            self.lb_timestamp.setText(spec.app_state.reference_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.curve.active = True
        else:
            self.curve.setData([])
            self.lb_timestamp.setText("")
            self.curve.active = False

        # todo some kind of observers for reference
        self.save_options.update_widgets()
        self.gui.colorize_button(self.button_toggle, spec.app_state.has_reference())
        self.graph.update_visibility()  # MZ: why does Reference need this but not Dark?

    # ##########################################################################
    # private methods
    # ##########################################################################

    ##
    # Prompts the user to select a previously-saved Measurement (from disk, not
    # a loaded thumbnail), and pull the "Dark" column from that.
    #
    # - If no dark is found, does nothing.
    # - If dark is a column of zeros, uses that.
    # - If multiple Measurements are in the file, uses the first.
    #
    # Better design: add drop-down "..." menu to every ThumbnailWidget, to which we
    # can add a bunch of functions, including "Load dark" and "Load reference". This
    # would provide better support for "Export" files, where the Measurement we want
    # actually is buried within a larger set.
    def load(self): 
        m = self.measurement_factory.load_interpolated(self.settings())
        if m is None:
            return

        pr = m.processed_reading
        if pr.reference is None or len(pr.reference) == 0: 
            return

        spec = self.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return

        spec.app_state.reference = np.copy(pr.reference)
        spec.app_state.reference_timestamp = m.timestamp
        self.marquee.info("reference loaded")
        self.display()

    def enable_buttons(self, flag=True, tt=None):
        spec = self.multispec.current_spectrometer()
        if spec is not None:
            default_tt = "Clear reference" if spec.app_state.has_reference() else "Store reference" # diff: self.generate_toggle_tooltip()
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

    def populate_placeholder_scope_setup(self):
        policy = QtWidgets.QSizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Preferred)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)

        chart = pyqtgraph.PlotWidget(name="Recorded reference spectrum")
        chart.setSizePolicy(policy)

        self.curve = chart.plot([], pen=self.gui_make_pen(widget="reference"))

        self.stacked_widget.addWidget(chart)
        self.stacked_widget.setCurrentIndex(1)
