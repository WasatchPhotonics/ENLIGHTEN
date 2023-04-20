import logging

import PySide2
import pyqtgraph
from PySide2 import QtCore, QtWidgets, QtGui

from enlighten import common
from enlighten.ScrollStealFilter import ScrollStealFilter

from wasatch import utils

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
class Graph(object):

    ##
    # This can be constructed in two ways.  The Controller passes in the
    # StackedWidget and expects the Graph to populate its own chart and legend.
    # In contrast, PluginController creates the chart and legend itself, and
    # passes them in.  Perhaps we need a GraphFactory?
    def __init__(self,
            clipboard                   = None,
            gui                         = None,
                                        
            button_copy                 = None,
            button_invert               = None,
            button_lock_axes            = None,
            button_zoom                 = None,
            cb_marker                   = None,
            combo_axis                  = None,
            generate_x_axis             = None, # Graph makes this available to many other classes
            hide_when_zoomed            = None,
            init_graph_axis             = True,   
            layout                      = None, # passed by Controller/BusinessObjects
            legend                      = None, # passed by PluginController
            lock_marker                 = False,# passed by PluginController (for 'xy' graphs)
            plot                        = None, # passed by PluginController (pyqtgraph.PlotWidget)
            rehide_curves               = None,     
            stacked_widget              = None, # by Controller/BusinessObjects
            ):               

        self.clipboard                  = clipboard
        self.gui                        = gui

        self.button_copy                = button_copy
        self.button_invert              = button_invert
        self.button_lock_axes           = button_lock_axes
        self.button_zoom                = button_zoom
        self.cb_marker                  = cb_marker
        self.combo_axis                 = combo_axis
        self.generate_x_axis            = generate_x_axis
        self.hide_when_zoomed           = hide_when_zoomed
        self.layout                     = layout
        self.legend                     = legend
        self.lock_marker                = lock_marker
        self.plot                       = plot
        self.rehide_curves              = rehide_curves
        self.stacked_widget             = stacked_widget

        # these are passed post-construction, or not at all (could add to ctor parameters anyway)
        self.cursor         = None
        self.multispec      = None 
        self.vignette_roi   = None 
        self.measurements   = None

        if init_graph_axis:
            self.current_x_axis = common.Axes.WAVELENGTHS
        else:
            self.current_x_axis = self.combo_axis.currentIndex()
        self.current_y_axis = common.Axes.COUNTS
        self.intended_y_axis= common.Axes.COUNTS

        self.zoomed         = False
        self.y_axis_locked  = False
        self.x_axis_locked  = False  # EnlightenPluginConfiguration specified an x_axis_label
        self.show_marker    = False
        self.inverted       = False

        self.axis_observers = set()

        self.combo_axis.setCurrentIndex(self.current_x_axis)

        # populate placeholders if requested
        if stacked_widget:
            self.populate_scope_setup()
        if layout:
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
        self.live_curve = self.live_plot.plot([], pen=self.gui.make_pen(widget="live"))

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
        if not (self.multispec is None):
            for spec in self.multispec.get_spectrometers():
                self.update_roi_regions(spec)

    def update_marker(self):
        self.show_marker = self.cb_marker.isChecked()
        self.rescale_curves()

    ##
    # About time we started an actual observer pattern...
    def register_axis_observer(self, callback):
        self.axis_observers.add(callback)

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
            # re-initialize cursor position (BUG: re-centers, doesn't stay on previous peak)
            if self.cursor is not None:
                self.cursor.convert_location(old_axis, enum)
            # Controller.generate_x_axis() actually uses Graph.current_x_axis to 
            # determine the current axis enum, so we can be confident this will 
            # return the appropriate array...IF a spectrometer is connected
            x_axis = self.generate_x_axis()

            if self.cursor is not None:
                suffix = " %s" % common.AxesHelper.get_suffix(enum) # note space
                log.debug(f"setting Cursor suffix to {suffix} (enum {enum})")
                self.cursor.set_suffix(suffix)

                if x_axis is not None:
                    # update the Cursor's range (not value)
                    self.cursor.set_range(array=x_axis)

            # update the widget
            self.combo_axis.setCurrentIndex(enum)

            # if we were zoomed into a portion of the graph, changing x-axis will "display all"
            self.reset_axes()

            # update any spectra currently displayed on the graph (Measurement
            # traces or paused acquisition)
            self.rescale_curves()

            for callback in self.axis_observers:
                callback()
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
        self.gui.colorize_button(self.button_lock_axes, self.y_axis_locked)

    def toggle_zoom(self):
        self.zoomed = not self.zoomed
        self.gui.colorize_button(self.button_zoom, self.zoomed)

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
        if self.multispec is not None and self.intended_y_axis in [common.Axes.PERCENT, common.Axes.AU]:
            spec = self.multispec.current_spectrometer()
            if spec and spec.app_state.reference is not None:
                self.current_y_axis = self.intended_y_axis

        self.plot.setLabel(axis="left", text=common.AxesHelper.get_pretty_name(self.current_y_axis))

    def add_roi_region(self, region):
        self.plot.addItem(region)

    def remove_roi_region(self, region):
        self.plot.removeItem(region)

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
                if self.vignette_roi and measurement:
                    roi = measurement.settings.eeprom.get_horizontal_roi()
                    if roi:
                        # force vignetting, as clearly y is cropped (likely loaded 
                        # from external file), and we really have no choice but to 
                        # use what was in effect when the Measurement was taken
                        x = self.vignette_roi.crop(x, roi=roi, force=True)

            if len(y) != len(x):
                log.error("unable to correct thumbnail widget by vignetting (len(x) %d != len(y) %d)", len(x), len(y))
                return

        if pen is None:
            log.debug(f"making pen for {name}")
            pen = self.gui.make_pen(widget=name)

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

        if rehide and self.rehide_curves is not None:
            self.rehide_curves()

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
                curve.setSymbolBrush(self.gui.colors.color_names.get("enlighten_name_n1"))
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
        self.gui.colorize_button(self.button_invert, self.inverted)

    ##
    # Iterates through all the curves currently shown on the graph and updates
    # them to the correct x-axis.
    def rescale_curves(self):
        if self.measurements is None:
            return

        axis = self.current_x_axis

        # handle live spectrometers
        if self.multispec is not None:
            for spec in self.multispec.get_spectrometers():
                curve = spec.curve
                if curve is None:
                    continue
                (xData, yData) = curve.getData()
                xData = self.generate_x_axis(spec=spec)
                if xData is not None and yData is not None:
                    if len(yData) < len(xData) and self.vignette_roi is not None:
                        roi = spec.settings.eeprom.get_horizontal_roi()
                        if roi is not None:
                            xData = self.vignette_roi.crop(xData, roi=roi)
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

                m = self.measurements.get(measurement_id)
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
                    if len(yData) < len(xData) and self.vignette_roi is not None:
                        roi = m.settings.eeprom.get_horizontal_roi()
                        if roi is not None:
                            xData = self.vignette_roi.crop(xData, roi=roi)

                    if len(yData) == len(xData):
                        self.set_data(curve=curve, y=yData, x=xData)

    def copy_to_clipboard_callback(self):
        if self.multispec is None:
            return

        if self.multispec.count() < 2:
            # one spectrometer
            x_axis = self.generate_x_axis() # whichever spec is selected I guess
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

        self.clipboard.copy_spectra(spectra)

    def update_roi_regions(self, spec):
        # Here there shouldn't be a default, spec should be explicit
        if spec is None:
            return

        # by default, hide the curtains
        self.remove_roi_region(spec.roi_region_left)
        self.remove_roi_region(spec.roi_region_right)

        if not spec.settings.eeprom.has_horizontal_roi():
            # log.debug("hiding curtains (no ROI to show)")
            return

        if not self.vignette_roi:
            # log.debug("hiding curtains (no VigentteROI object)")
            return

        if self.vignette_roi.enabled:
            # log.debug("hiding curtains (VignetteROI.enabled True), meaning finges should be hid")
            return

        # log.debug("showing curtains, because VignetteROI.enabled False")

        roi = spec.settings.eeprom.get_horizontal_roi()
        axis = self.generate_x_axis(vignetted=False)

        log.debug(f"update_roi_regions: roi {roi}, axis {len(axis)} elements")

        spec.roi_region_left .setRegion((axis[0],       axis[roi.start]))
        spec.roi_region_right.setRegion((axis[roi.end], axis[-1]       ))

        if roi.start == 0:
            spec.roi_region_left.setOpacity(0)
        else:
            spec.roi_region_left.setOpacity(1)

        if roi.end >= len(axis):
            spec.roi_region_right.setOpacity(0)
        else:
            spec.roi_region_right.setOpacity(1)

        self.add_roi_region(spec.roi_region_left)
        self.add_roi_region(spec.roi_region_right)
