import logging

import pyqtgraph

from enlighten import common
from enlighten.ui.ScrollStealFilter import ScrollStealFilter

if common.use_pyside2():
    from PySide2 import QtWidgets
else:
    from PySide6 import QtWidgets

log = logging.getLogger(__name__)

##
# Encapsulate the large graph in the center of ENLIGHTEN's Scope Capture screen.
#
# This was intended to be a singleton, as the ENLIGHTEN GUI was basically written
# around one large central graph, but there can now be a second instance of this
# object used to control the "plugin graph" used by Plugin.PluginController.  
#
# We probably want to look into refactoring something (maybe split this class in 
# half?), as some of these attributes / methods could be applied to "any graph",
# while others were intended to be specific to the main Scope Capture graph.
#
# We are not making full use of pyqtgraph's power, in part because it turns out
# that surprisingly little of pyqtgraph is documented online.  To get a better
# sense of its power, you should install and run the examples as described:
#
# @see http://www.pyqtgraph.org/documentation/introduction.html#examples
#
# In particular, we should:
#
# - consider using CurvePlotItem's sigClicked event, which would let the user
#   change Multispec selected spectrometer (or select a ThumbnailWidget, if that
#   was useful) by clicking a curve on-screen
#
class Graph:

    ##
    # This can be constructed in two ways. By default, the Graph populates its
    # own chart and legend (the one used by most of ENLIGHTEN). However, it
    # also allows an external caller (like PluginController) to pass-in an
    # already-constructed chart and legend. Perhaps we need a GraphFactory?
    def __init__(self,
            ctl,
            name,

            legend                      = None,
            lock_marker                 = False, # for 'xy' graphs
            plot                        = None,  # pyqtgraph.PlotWidget
            ):               

        self.ctl                        = ctl
        self.name                       = name
        self.legend                     = legend
        self.lock_marker                = lock_marker
        self.plot                       = plot

        # for now, retain legacy widget aliases
        cfu = ctl.form.ui
        self.button_copy                = cfu.pushButton_copy_to_clipboard
        self.button_invert              = cfu.pushButton_invert_x_axis
        self.button_lock_axes           = cfu.pushButton_lock_axes
        self.button_zoom                = cfu.pushButton_zoom_graph
        self.cb_marker                  = cfu.checkBox_graph_marker
        self.combo_axis                 = cfu.displayAxis_comboBox_axis

        # these are the "main graph" widgets we will populate IFF no ready-made 
        # plot was provided (e.g. by PluginController)
        self.layout                     = cfu.layout_scope_capture_graphs
        self.stacked_widget             = cfu.stackedWidget_scope_setup_live_spectrum

        self.hide_when_zoomed           = [ cfu.frame_new_save_col_holder, cfu.controlWidget ]

        self.current_x_axis = self.combo_axis.currentIndex()
        self.current_y_axis = common.Axes.COUNTS
        self.intended_y_axis= common.Axes.COUNTS

        self.zoomed         = False
        self.y_axis_locked  = False
        self.x_axis_locked  = False  # EnlightenPluginConfiguration specified an x_axis_label
        self.show_marker    = False
        self.inverted       = False

        self.observers = {}

        self.combo_axis.setCurrentIndex(self.current_x_axis)

        # if we weren't passed a pre-populated plot, then create one
        if not self.plot:
            self.populate_scope_setup()
            self.populate_scope_capture()

        # bindings
        self.combo_axis                             .currentIndexChanged    .connect(self.update_axis_callback)
        self.combo_axis                                                     .installEventFilter(ScrollStealFilter(self.combo_axis))
        self.button_invert                          .clicked                .connect(self.invert_x_axis)
        self.cb_marker                              .stateChanged           .connect(self.update_marker)
        self.button_lock_axes                       .clicked                .connect(self.toggle_lock_axes)
        self.button_zoom                            .clicked                .connect(self.toggle_zoom)
        self.button_copy                            .clicked                .connect(self.copy_to_clipboard_callback)

        self.update_marker()

    # ##########################################################################
    # Populate placeholders (if called by BusinessObjects for main GUI)
    # ##########################################################################

    # PluginController doesn't use these (passes own chart and legend)

    def populate_scope_setup(self):
        log.debug("populate_scope_setup: start")

        policy = QtWidgets.QSizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Preferred)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)

        self.live_plot = pyqtgraph.PlotWidget(name="Live Scope")
        self.live_plot .setSizePolicy(policy)
        self.live_curve = self.live_plot.plot([], pen=self.ctl.gui.make_pen(widget="live"))

        self.stacked_widget.addWidget(self.live_plot)
        self.stacked_widget.setCurrentIndex(1)

    def populate_scope_capture(self):
        log.debug("populate_scope_capture: start")

        self.plot = pyqtgraph.PlotWidget(name="Scope Capture")

        self.plot.setLabel(axis="bottom", text=common.AxesHelper.get_pretty_name(common.Axes.WAVELENGTHS))
        self.plot.setLabel(axis="left",   text=common.AxesHelper.get_pretty_name(common.Axes.COUNTS))

        self.legend = self.plot.addLegend() # returns a LegendItem

        # populate the spectrum curve placeholder last, so it's "on top of" the others in Z-axis
        # Note: we'll create the curves themselves from initialize_new_device(hotswap)
        #
        # For PluginController, the following is very important: note that although this is an 
        # EMPTY QGridLayout, we're adding the ONLY element at 0-indexed position (1, 1). This 
        # allows the PluginController to place other elements at any of these spots:
        #
        #     0   1   2
        #   +---+---+---+
        # 0 |   | T |   |   T = Top
        #   +---+---+---+   L = Left
        # 1 | L | G | R |   G = Graph
        #   +---+---+---+   R = Right
        # 2 |   | B |   |   B = Bottom
        #   +---+---+---+
        #
        self.layout.addWidget(self.plot, 1, 1)

    ## called by Cursor to add its InfiniteLine to the graph
    def add_item(self, item):
        self.plot.addItem(item)

    ## @todo merge with common suffixes
    def get_x_axis_unit(self):
        if self.current_x_axis == common.Axes.WAVENUMBERS: return "cm"
        if self.current_x_axis == common.Axes.WAVELENGTHS: return "nm"
        return "px"

    def in_pixels     (self): return self.current_x_axis == common.Axes.PIXELS
    def in_wavelengths(self): return self.current_x_axis == common.Axes.WAVELENGTHS
    def in_wavenumbers(self): return self.current_x_axis == common.Axes.WAVENUMBERS

    def update_axis_callback(self):
        if self.x_axis_locked:
            return
        self.set_x_axis(self.combo_axis.currentIndex())
        if self.ctl.multispec and self.ctl.horiz_roi:
            for spec in self.ctl.multispec.get_spectrometers():
                self.ctl.horiz_roi.update_regions(spec)

    def update_marker(self):
        self.show_marker = self.cb_marker.isChecked()
        self.rescale_curves()

    def register_observer(self, event, callback):
        if event not in self.observers:
            self.observers[event] = set()
        self.observers[event].add(callback)

    ## extra <BR> provides margin from the frame bottom...probably would be better with CSS
    def set_x_axis_label(self, text, locked=False):
        self.plot.setLabel(text=text+"<br>", axis="bottom")
        self.x_axis_locked = locked

    ## when the Mode changes, update axis as appropriate 
    def set_x_axis(self, enum):
        log.debug("set_x_axis: %s", enum)
        old_axis = self.current_x_axis
        self.current_x_axis = enum
        self.set_x_axis_label(common.AxesHelper.get_pretty_name(enum))

        try:

            # update the widget
            self.combo_axis.setCurrentIndex(enum)

            # if we were zoomed into a portion of the graph, changing x-axis will "display all"
            self.reset_axes()

            # update any spectra currently displayed on the graph (Measurement
            # traces or paused acquisition)
            self.rescale_curves()

            if "change_axis" in self.observers:
                for callback in self.observers["change_axis"]:
                    callback(old_axis, enum)
        except:
            log.error("Error setting suffix", exc_info=1)
            pass

    def reset_axes(self):
        if not self.y_axis_locked:
            self.toggle_lock_axes()
        self.toggle_lock_axes()

    def toggle_lock_axes(self):
        box = self.plot.getViewBox()

        if self.y_axis_locked:
            box.enableAutoRange()
        else:
            box.disableAutoRange()

        self.y_axis_locked = not self.y_axis_locked
        self.ctl.gui.colorize_button(self.button_lock_axes, self.y_axis_locked)

    def toggle_zoom(self):
        self.zoomed = not self.zoomed
        self.ctl.gui.colorize_button(self.button_zoom, self.zoomed)

        for widget in self.hide_when_zoomed:
            widget.setVisible(not self.zoomed)

    def enable_axis_selection(self, flag):
        self.combo_axis.setEnabled(flag)

    def enable_wavenumbers(self, flag):
        if flag:
            if self.combo_axis.count() == 2:
                self.combo_axis.addItem("Wavenumber")
        else:
            if self.combo_axis.count() == 3:
                self.combo_axis.removeItem(2)

    ##
    # Only sets the "intention" to use the specified axis label; in reference-
    # based modes, don't actually switch to the target axis until processing
    # requirements are met (i.e., a reference has been taken).
    def set_y_axis(self, enum):
        self.intended_y_axis = enum
        self.reset_axes()
        self.update_visibility()

    def update_visibility(self):
        self.current_y_axis = common.Axes.COUNTS
        if self.ctl.multispec and self.intended_y_axis in [common.Axes.PERCENT, common.Axes.AU]:
            spec = self.ctl.multispec.current_spectrometer()
            if spec and spec.app_state.reference is not None:
                self.current_y_axis = self.intended_y_axis

        self.plot.setLabel(axis="left", text=common.AxesHelper.get_pretty_name(self.current_y_axis))

    ## 
    # This was originally used used by ThumbnailWidget, when clicking the "show 
    # trace" thumbnail button. It's now also being used by 
    # BaselineCorrectionFeature, RamanShiftCorrection, etc.
    #
    # @todo we should probably create a Curve class to encapsulate data 
    #       associated with a particular on-screen trace, rather than hanging 
    #       attributes off a library class
    def add_curve(self, name, y=[], x=None, pen=None, spec=None, measurement=None, rehide=True, in_legend=True):
        # I am not 100% sure what datatype is returned from 
        # pyqtgraph.PlotWidget.plot()...presumably a CurvePlotItem?
        # SB. actually it returns a PlotDataItem

        if x is not None:
            if len(y) < len(x):
                if self.ctl.horiz_roi and measurement:
                    roi = measurement.settings.eeprom.get_horizontal_roi()
                    if roi:
                        # force cropping, as clearly y is cropped (likely loaded 
                        # from external file), and we really have no choice but to 
                        # use what was in effect when the Measurement was taken
                        x = self.ctl.horiz_roi.crop(x, roi=roi, force=True)

            if len(y) != len(x):
                log.error("unable to correct thumbnail widget by cropping (len(x) %d != len(y) %d)", len(x), len(y))
                return

        if pen is None:
            log.debug(f"making pen for {name}")
            pen = self.ctl.gui.make_pen(widget=name)

        if in_legend:
            curve = self.plot.plot(
                y=y,
                x=x,
                pen=pen,
                name=name
            )
        else:
            curve = self.plot.plot(
                y=y,                                                                                                                                                                                                                                         
                x=x,
                pen=pen,
            )

        self.update_curve_marker(curve)
        log.debug("add_curve: added a %s (%s)", type(curve), str(curve))

        # if this new curve is tied to a live Spectrometer or a captured Measurement, 
        # store a lookup ID as a backreference
        if spec is not None:
            curve.device_id = spec.device_id
            log.debug("added curve %s for device %s", name, curve.device_id)

        if measurement is not None:
            # used so we can re-scale displayed thumbnail traces when the current x-axis changes
            curve.measurement_id = measurement.measurement_id
            log.debug("added curve %s for measurement %s", name, curve.measurement_id)

        if spec is None and measurement is None:
            log.debug("added raw curve '%s'", name)

        if rehide:
            self.ctl.update_feature_visibility()

        return curve

    ## 
    # If nobody else persists the curve, this will delete the curve object
    # itself from memory, as well removing it from the graph.
    # 
    # @note apparently we don't need to call deleteLater() with pyqtgraph objects
    # @see https://github.com/pyqtgraph/pyqtgraph/issues/524#issuecomment-319860256
    def remove_curve(self, name=None, measurement_id=None):
        for curve in self.plot.listDataItems():
            if (measurement_id is not None and hasattr(curve, "measurement_id") and measurement_id == curve.measurement_id) or \
               (name is not None and name == curve.name()):
                self.plot.removeItem(curve)
                self.legend.removeItem(curve)
                return 

    def remove_from_legend(self, name=None, measurement_id=None):
        if name is None and measurement_id is None:
            return False

    def update_curve_marker(self, curve):
        if self.lock_marker:
            return

        if self.show_marker:
            if curve.opts['symbol'] is None:
                curve.setSymbol('o')
                curve.setSymbolBrush(self.ctl.colors.color_names.get("enlighten_name_n1"))
        else:
            curve.setSymbol(None)

    ##
    # @see http://www.pyqtgraph.org/documentation/graphicsItems/plotdataitem.html
    def set_data(self, curve, y=None, x=None):
        if x is not None:
            log.debug(f"plotting {len(x)} x values {x[:3]} .. {x[-3:]}")

        if y is not None:
            log.debug(f"plotting {len(y)} y values {y[:3]} .. {y[-3:]}")
        self.update_curve_marker(curve)
        curve.setData(y=y, x=x)

    def invert_x_axis(self):
        self.inverted = not self.inverted
        self.plot.getPlotItem().invertX(self.inverted)
        self.ctl.gui.colorize_button(self.button_invert, self.inverted)

    ##
    # Iterates through all the curves currently shown on the graph and updates
    # them to the correct x-axis.
    def rescale_curves(self):
        if not self.ctl.measurements:
            return

        axis = self.current_x_axis

        # handle live spectrometers
        if self.ctl.multispec is not None:
            for spec in self.ctl.multispec.get_spectrometers():
                curve = spec.curve
                if curve is None:
                    continue
                (xData, yData) = curve.getData()
                xData = self.ctl.generate_x_axis(spec=spec)
                if xData is not None and yData is not None:
                    if len(yData) < len(xData) and self.ctl.horiz_roi:
                        roi = spec.settings.eeprom.get_horizontal_roi()
                        if roi is not None:
                            xData = self.ctl.horiz_roi.crop(xData, roi=roi)
                    if len(xData) == len(yData):
                        self.set_data(curve=curve, y=yData, x=xData)

        # handle Measurements on the capture bar (should we then be actually iterating Measurements...?)
        for curve in self.plot.listDataItems():
            name = curve.name()

            # ignore live spectrometers (already did those)
            if hasattr(curve, "device_id"):
                continue

            # just process these
            if hasattr(curve, "measurement_id"):
                measurement_id = getattr(curve, "measurement_id")
                log.debug("curve %s is from measurement %s", name, measurement_id)

                (xData, yData) = curve.getData()
                if yData is None:
                    continue

                m = self.ctl.measurements.get(measurement_id)
                if m is None:
                    log.error("graph is displaying trace of measurement %s which is missing from Measurements", measurement_id)
                    continue

                if axis == common.Axes.WAVELENGTHS:
                    xData = m.settings.wavelengths
                elif axis == common.Axes.WAVENUMBERS:
                    xData = m.settings.wavenumbers
                else:
                    xData = list(range(len(yData)))

                if xData is not None:
                    if len(yData) < len(xData) and self.ctl.horiz_roi:
                        roi = m.settings.eeprom.get_horizontal_roi()
                        if roi is not None:
                            xData = self.ctl.horiz_roi.crop(xData, roi=roi)

                    if len(yData) == len(xData):
                        self.set_data(curve=curve, y=yData, x=xData)

    def copy_to_clipboard_callback(self):
        if not self.ctl.multispec:
            return

        if self.ctl.multispec.count() < 2:
            # one spectrometer
            x_axis = self.ctl.generate_x_axis() # whichever spec is selected I guess
            spectra = [ x_axis ]

            # iterate over every curve on the graph
            for curve in self.plot.listDataItems():
                spectrum = curve.getData()[-1]
                if spectrum is not None and len(spectrum) == len(x_axis):
                    spectra.append(spectrum)
        else:
            # multiple spectrometers, so x-axis and lengths can vary
            spectra = []
            for curve in self.plot.listDataItems():
                spectra.append(curve.getData()[0])
                spectra.append(curve.getData()[-1])

        self.ctl.clipboard.copy_spectra(spectra)

    ############################################################################
    # 
    #                             Horizontal ROI
    # 
    ############################################################################

    def add_roi_region(self, region):
        self.plot.addItem(region)

    def remove_roi_region(self, region):
        self.plot.removeItem(region)

