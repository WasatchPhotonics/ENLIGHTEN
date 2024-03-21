import logging
import numpy as np

import pyqtgraph

from enlighten import common
from enlighten.util import unwrap

if common.use_pyside2():
    from PySide2 import QtWidgets
else:
    from PySide6 import QtWidgets

log = logging.getLogger(__name__)

##
# This class is sufficiently close to DarkFeature that it's tempting to make them
# one inherit the other, or derive both from a common ABC.
class ReferenceFeature:

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.lb_timestamp       = cfu.label_reference_timestamp
        self.button_toggle      = cfu.pushButton_scope_toggle_reference

        button_clear            = cfu.pushButton_reference_clear
        button_load             = cfu.pushButton_reference_load
        button_store            = cfu.pushButton_reference_store

        self.populate_placeholder_scope_setup()

        # these should be invisible when feature deemed inappropriate
        self.visibility_widgets = [ cfu.frame_scopeSetup_spectra_reference_white,
                                    self.button_toggle, 
                                    button_store,
                                    self.ctl.save_options.cb_reference ]

        # no _callback functions because no arguments
        button_clear        .clicked    .connect(self.clear)
        button_load         .clicked    .connect(self.load)
        button_store        .clicked    .connect(self.store)
        self.button_toggle  .clicked    .connect(self.toggle)

        for widget in [ button_clear, button_load, button_store, self.button_toggle ]:
            widget.setWhatsThis(unwrap("""
                Many non-Raman spectroscopic techniques involve a "reference"
                spectrum for comparison against the sample. Reference-based
                techniques include absorbance, reflectance and transmission.
                Reference-based techniques still typically benefit from dark
                correction, so ENLIGHLTEN will often use three different spectra
                when processing non-Raman reference-based techniques.

                Similar to dark spectra, users are recommended to "refresh" their
                reference whenever possible to account for thermal drift and
                changes in ambient lighting."""))

    # ##########################################################################
    # public methods
    # ##########################################################################

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        # hide reference widgets in non-referenced mode (basically, Raman)
        if self.ctl.page_nav.doing_raman() and not self.ctl.page_nav.doing_expert():
            [ widget.setVisible(False) for widget in self.visibility_widgets ]
            return

        [ widget.setVisible(True) for widget in self.visibility_widgets ]

        self.ctl.gui.colorize_button(self.button_toggle, spec.app_state.has_reference())

    def toggle(self):
        spec = self.ctl.multispec.current_spectrometer()
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
        spec = self.ctl.multispec.current_spectrometer()
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
                self.ctl.marquee.info("reference stored")

        self.display()

    def clear(self, quiet=False):
        spec = self.ctl.multispec.current_spectrometer()
        spec.app_state.clear_reference()
        self.display()
        if not quiet:
            self.ctl.marquee.info("reference cleared")

    def display(self):
        spec = self.ctl.multispec.current_spectrometer()

        self.update_enable()

        if spec is None:
            self.curve.setData([])
            self.curve.active = False
            self.lb_timestamp.setText("")
            self.ctl.gui.colorize_button(self.button_toggle, False)
            return

        if spec.app_state.has_reference():
            self.ctl.set_curve_data(self.curve, y=spec.app_state.reference, label="display_reference")
            self.lb_timestamp.setText(spec.app_state.reference_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.curve.active = True
        else:
            self.curve.setData([])
            self.lb_timestamp.setText("")
            self.curve.active = False

        # todo some kind of observers for reference
        self.ctl.save_options.update_widgets()
        self.ctl.gui.colorize_button(self.button_toggle, spec.app_state.has_reference())
        self.ctl.graph.update_visibility()  # MZ: why does Reference need this but not Dark?

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
        m = self.ctl.measurement_factory.load_interpolated(self.settings())
        if m is None:
            return

        pr = m.processed_reading
        if pr.reference is None or len(pr.reference) == 0: 
            return

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None or spec.app_state is None:
            return

        spec.app_state.reference = np.copy(pr.reference)
        spec.app_state.reference_timestamp = m.timestamp
        self.ctl.marquee.info("reference loaded")
        self.display()

    def enable_buttons(self, flag=True, tt=None):
        spec = self.ctl.multispec.current_spectrometer()
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
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return self.enable_buttons(False)
        self.enable_buttons(True)

    def populate_placeholder_scope_setup(self):
        policy = QtWidgets.QSizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Preferred)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)

        chart = pyqtgraph.PlotWidget(name="Recorded reference spectrum")
        chart.setSizePolicy(policy)

        self.curve = chart.plot([], pen=self.ctl.gui.make_pen(widget="reference"))

        stacked_widget = self.ctl.form.ui.stackedWidget_scope_setup_reference_spectrum
        stacked_widget.addWidget(chart)
        stacked_widget.setCurrentIndex(1)
