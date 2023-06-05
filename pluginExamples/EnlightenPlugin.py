##
# @file     EnlightenPlugin.py
# @brief    Contains all the classes exchanged with ENLIGHTEN plug-ins, including
#           the EnlightenPluginBase which all plug-ins should extend.

import logging
import datetime
from dataclasses import dataclass, field

from enlighten import common

log = logging.getLogger(__name__)

from enlighten.scope.Spectrometer import Spectrometer
from wasatch.ProcessedReading import ProcessedReading
from wasatch.SpectrometerSettings import SpectrometerSettings

import numpy as np
import os

##
# Abstract Base Class (ABC) for all ENLIGHTEN-compatible plug-ins.
#
# Plug-ins extending this class will be imported and instantiated by the 
# ENLIGHTEN PluginController.  
#
# Note that your plugin classname MUST match its module name 
# (e.g. "class Foo(EnlightenPluginBase)" inside "Foo.py").
#
# @par Key Attributes
#
# - enlighten_info will be passed to connect() (and stored, if you call the 
#   superclass method)
# - error_message can be set by the plug-in if they wish a user-visible error 
#   string or stacktrace to be displayed to the user in a message box (e.g.
#   following a failure in connect)
class EnlightenPluginBase:
    
    def __init__(self, ctl):
        self.enlighten_info = None
        self.error_message = None

        # these can be set by functional-plugins to autogenerate EPC
        self.name = None
        self._fields = []
        self.is_blocking = False
        self.has_other_graph = False
        self.table = None
        self.x_axis_label = None
        self.y_axis_label = None

        self.series = {}

        # plugins can do everything
        self.ctl = ctl

    def get_axis(self):
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVELENGTHS:
            return self.settings.wavelengths
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVENUMBERS:
            return self.settings.wavenumbers
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.PIXELS:
            return range(len(self.spectrum))
        
    def get_axis_name(self):
        """
        Printable axis name
        """
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVELENGTHS:
            return "Wavelengths (cm⁻¹)"
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.WAVENUMBERS:
            return "Wavenumbers (nm)"
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex() == common.Axes.PIXELS:
            return "Pixels (px)"

    ### Begin functional-plugins backend ###

    def log(self, *msgs):
        # initially made this because the regular logger wasn't working
        # but it actually makes sense for plugins to have their own log separate from enlighten
        with open(common.get_default_data_dir()+os.sep+'plugin_log.txt', 'at') as pl:
            pl.write(' '.join([str(msg) for msg in msgs]) + "\n")

    def reset_configuration(self):
        plugin_name = self.ctl.form.ui.comboBox_plugin_module.currentText()
        self.ctl.plugin_controller.configure_gui_for_module(plugin_name)

    def field(self, **kwargs):
        self._fields.append(EnlightenPluginField(**kwargs))

    def get_widget_from_name(self, name):
        widget = None
        for elem in self.enlighten_info.plugin_fields():
            if elem.field_name == name:
                widget = elem
        return widget.field_widget

    def plot(self, y, x=None, title=None, color=None):
        """
        When plotting on the main scope graph
        the (co)domain matches that existing graph.

        Set self.x_axis_label or self.y_axis_label to
        provide your own axis labels when plotting
        to a secondary graph.

        @param x x values
        @param y y values
        @param title plot title, shown in legend
        @param color color of plot line
        """
        in_legend = True

        if x is None: x = np.arange(len(y))

        if title is None: 
            title = "untitled"
            in_legend = False

        # create titles for untitled graphs: untitled, untitled2, untitled3
        suffix = ""
        i = 2
        while title+suffix in self.series.keys():
            suffix = str(i)
            i += 1
        title = title+suffix

        self.series[title] = {
            "x": x,
            "y": y,
            "color": color,
            "title": title,
            "in_legend": in_legend
        }

    def to_graph(self, x):
        """
        Undo to_pixel conversion, and set point back to 
        currently selected graph X-Axis
        """
        domain = self.get_axis()

        target_x = round(x)

        roi = self.settings.eeprom.get_horizontal_roi()

        if roi:
            target_x = target_x+roi.start

        return domain[target_x]

    def to_pixel(self, x, domain=None):
        """
        domain is an array where the index corresponds to a detector pixel number.
        
        if x occurs once in domain, this is like domain.index(x)
        otherwise a most sensible index is selected

        if domain is unspecified, the selected axis is used
        """
        if domain is None:
            domain = self.get_axis()

        # select the index whose value is closest to x
        target_x = min(enumerate(domain), key=lambda P: abs(P[1]-x))[0]

        roi = self.settings.eeprom.get_horizontal_roi()

        if roi:
            # |-----|-----------target_x
            # 0     roi.start

            # to_pixel output is used to index spectrum
            # which already has roi trimmed, so we must subtract roi.start
            return target_x-roi.start
        else:
            return target_x

    def wavelength_to_pixel(self, wavelength):
        return self.to_pixel(wavelength, self.settings.wavelengths)

    def wavenumber_to_pixel(self, wavenumber):
        return self.to_pixel(wavenumber, self.settings.wavenumbers)

    #### End functional-plugins backend ####

    ### Begin backwards compatible object-returning wrappers ###
    def get_configuration_obj(self):
        config = self.get_configuration()
        if config: return config

        return EnlightenPluginConfiguration(
            name = self.name, 
            fields = self._fields,
            is_blocking = self.is_blocking,
            block_enlighten = self.block_enlighten,
            has_other_graph = self.has_other_graph,
            series_names = [], # functional plugins define this on a frame-by-frame basis
            x_axis_label = self.x_axis_label,
            y_axis_label = self.y_axis_label
        )
    
    def process_request_obj(self, request):

        # clear series each frame
        self.series = {}
        self.metadata = {}

        response = self.process_request(request)
        if response: return response

        # if not yet returned, we are running a functional plugin,
        # and so we want Enlighten to construct the EnlightenPluginResponse for us

        outputs = {}
        if self.table is not None:
            outputs = {
                # table (looks like a spreadsheet under the graph)
                "Table": self.table,
            }

        log.debug(f"returning metadata = {self.metadata}")
        return EnlightenPluginResponse(
            request,
            series = self.series,
            outputs = outputs,
            metadata = self.metadata
        )
    #### End backwards compatible object-returning wrappers #####

    ##
    # Can be called BEFORE or AFTER connect. Should be idempotent. Ideally should
    # return same object on multiple calls, but at least should be "equivalent" 
    # objects.
    #
    # @return an EnlightenPluginConfiguration 
    def get_configuration(self):
        return None

    ##
    # Do whatever you have to do to prepare for processing measurements.  This 
    # may be a one-time setup operation taking 15sec, or it may be a no-op.  
    #
    # This will be called each time the "[x] connected" checkbox is ticked on the
    # ENLIGHTEN Plug-In Setup GUI.  Neither this method nor stop() will be called
    # when the "[x] Enabled" checkbox is ticked.
    #
    # @param enlighten_info: EnlightenApplicationInfo
    # @return True if initialization is successful, False otherwise
    def connect(self, enlighten_info):
        log.debug("EnlightenPluginBase.connect")
        self.enlighten_info = enlighten_info
        return True

    # ENLIGHTEN will call this method when it has a new ProcessedReading for your 
    # plug-in to process.  
    #
    # @param request: an EnlightenPluginRequest
    # @returns an EnlightenPluginResponse
    def process_request(self, request):
        return EnlightenPluginResponse(request)
        
    ##
    # Called when ENLIGHTEN is shutting down.  Release any resources you have.
    # The next time you're needed, there will be a new call to connect().
    def disconnect(self):
        pass

##
# This class specifies the configuration of an entire EnlightenPlugin.
#
# ------------------------------------------------------------------------------
# @par Graph Output
#
# A plug-in can return series to be graphed in ENLIGHTEN.  There are three 
# options:
#
# 1. The series can be ADDED to the "main graph" (default)
# 2. A SECOND graph can be added to contain the plug-in output 
#    (has_other_graph=True)
# 3. The plugin can REPLACE the existing "processed" series in the original
#    ProcessedReading via overrides (requires block_enlighten=True)
#
# All the graph series from your plugin should be either "line" (default) or "xy", 
# configured via "graph_type".  Processing for both graph types is the same; it
# only changes whether datapoints are displayed via markers or line segments.
#
# In both graph types, you can supply multiple data series to be graphed.  In the
# EnlightenPluginConfiguration object, you should declare the name of each series
# in the series_names array.  When processing EnlightenPluginResponses, only series
# declared in series_names will be displayed.
#
# Graph data is returned from the plugin to ENLIGHTEN via the Response's 'series' 
# dictionary.  Each series to be updated should have a dict key matching 
# the series name, pointing to either:
#
# - a one-dimensional array of y-values, or
# - a dict with 'y' and optional 'x' arrays
#
# That is, these are equivalent:
# 
# \verbatim
# response = EnlightenPluginResponse(request, series = { 'Foo': y_values })
# response = EnlightenPluginResponse(request, series = { 'Foo': { 'y': y_values }})
# \endverbatim
# 
# If no 'x' element is provided, a default will be inferred using the following
# rules:
#
# - IF an x_axis_label is defined, AND the series length matches the request's 
#   processed spectrum length, THEN case-insensitive regular expressions are used 
#   to check for the following key terms and units:
#   - r"wavelength|nm": use current spectrometer's wavelength axis
#   - r"wavenumber|cm|shift": use current spectrometer's wavenumber axis
#   - r"pixel|px": use current spectrometer's pixel axis
# - if NO x_axis_label is defined AND the length of returned data matches the 
#   length of the request spectrum, it is assumed returned data should be graphed
#   against the same x_axis as the "live" ENLIGHTEN data, and will use whatever
#   x-axis the user has currently selected in ENLIGHTEN.
# - otherwise the x-axis will default to integral datapoints (0, 1, 2...). Note
#   that this will not "look good" on the ENLIGHTEN "main graph" unless the user
#   has set the x-axis to "pixel".
#
# Examples: BlockNullOdd, MakeOddNegative, PeakFinding, SegmentSpectrum, 
#           SimpleScaling, SineAndScale, StripChart
#
# ------------------------------------------------------------------------------
# @par Events
# 
# Events allow your plug-in to receive real-time notifications when certain 
# things happen in ENLIGHTEN.
#
# In a sense, the most basic event is pre-configured for every plugin: when 
# a new ProcessedReading is read from the spectrometer and graphed, the plugin's
# process_reading() callback is called with that reading.
#
# A major difference between processed_reading and other callbacks, though, is
# that processed_readings are deliberately passed through ENLIGHTEN's 
# PluginWorker in a threading.Thread via Python queue.Queues.  Event callbacks
# (like button callbacks) occur in the main Qt GUI thread.  
#
# That means that if a plug-in takes 3sec to handle a callback event, the 
# ENLIGHTEN GUI will "freeze" for 3 seconds.
#
# Supported events include:
#
# - "save": the user clicked the "Save" button 
#
# - under consideration:
#   - "load": a measurement was loaded from disk 
#   - "export": all thumbnails are exported to a single file
#
# Examples: SaveAsAngstrom
#
# ------------------------------------------------------------------------------
# @par Streaming
#
# By default, all plug-ins support "streaming" spectra, which is what happens
# when click the "[x] Enable" checkbox in ENLIGHTEN's Plugin Control widget.
# However, some plug-ins may not be designed or intended for that data rate
# and prefer to be individually triggered by the "Process" button or other 
# events.
#
# Examples: SaveAsAngstrom
#
# @see EnlightenPluginField
class EnlightenPluginConfiguration:

    ##
    # @param name: a string for labeling and debugging
    # @param fields: ordered list of EnlightenPluginField to display on the GUI
    # @param has_other_graph: whether ENLIGHTEN should display a second graph 
    #        solely to contain the processed results of the plug-in 
    # @param x_axis_label: graph axis label (ignored unless has_other_graph).
    # @param y_axis_label: graph axis label (ignored unless has_other_graph)
    # @param series_names: ordered list of legend labels for graph series 
    #        (must match series names in EnlightenPluginReponse.data)
    # @param graph_type: "line" or "xy" (scatter)
    # @param streaming: if True (default), display the "[x] Enable" checkbox
    # @param is_blocking: ENLIGHTEN should not send any further requests to the
    #        plug-in until the Response to the previous Request is received
    # @param block_enlighten: this is much more severe than is_blocking (which 
    #        merely blocks THE PLUGIN until a request is processed); if true, 
    #        this will let the plugin BLOCK ENLIGHTEN until a request is done.
    #        ENLIGHTEN currently enforces a hard 1sec timeout on blocking
    #        plugins.
    # @param multi_devices: True if the plug-in is designed to handle spectra 
    #        from multiple spectrometers (tracks requests by serial_number etc)
    # @param dependencies: optional array of EnlightenPluginDependency
    # @param events: a hash of supported event names to callbacks
    def __init__(self, 
            name, 
            fields          = None, 
            has_other_graph = False, 
            x_axis_label    = None, 
            y_axis_label    = None, 
            is_blocking     = True,
            block_enlighten = False,
            streaming       = True,
            events          = None,
            series_names    = None,
            multi_devices   = False,
            dependencies    = None,
            graph_type      = "line"):  # "line" or "xy"

        self.name            = name
        self.fields          = fields
        self.has_other_graph = has_other_graph
        self.x_axis_label    = x_axis_label
        self.y_axis_label    = y_axis_label
        self.is_blocking     = is_blocking
        self.block_enlighten = block_enlighten
        self.streaming       = streaming
        self.events          = events
        self.multi_devices   = multi_devices
        self.series_names    = series_names
        self.dependencies    = dependencies
        self.graph_type      = graph_type

class EnlightenPluginDependency:
    ##
    # @param name: identifying string
    # @param dep_type: currently supported values are: "existing_directory"
    # @param persist: save and use previous values as defaults across sessions
    # @param prompt: if user interaction is involved, use this as prompt / tooltip
    def __init__(self,
            name,
            dep_type    = None,
            persist     = False,
            prompt      = None):
        self.name       = name
        self.dep_type   = dep_type
        self.persist    = persist
        self.prompt     = prompt

##
# Each ENLIGHTEN plug-in will be visualized in the ENLIGHTEN GUI via a dynamically
# generated widget in the right-hand scrolling control list.  That widget will 
# include a vertical stack of these EnlightenPluginFields.  
#
# Each field will have a direction, either "input" (from ENLIGHTEN to the plugin)
# or "output" (from the plugin to ENLIGHTEN).
#
# - "input" fields are populated by the user via the ENLIGHTEN GUI and passed to
#   the plug-in via an EnlightenPluginRequest (e.g. "matchingThreshold" or 
#   "targetPeakCounts")
# - "output" fields are populated by the plug-in and passed via EnlightenPluginResponse
#   back to the ENLIGHTEN GUI for display to the user.
# 
# Fields can optionally be given a "tooltip" string for mouseOvers.
#
# @par Input Fields
#
# Input fields support these datatypes: string, int, float, bool, button.
#
# The plug-in author can determine what QWidget will be used for different "Input" 
# fields by specifying the datatype:
#
# - string -> QLineEdit 
# - int    -> QSpinBox
# - float  -> QDoubleSpinBox
# - bool   -> QCheckBox
# - button -> QPushButton
#
# All fields can be given an "initial" value.
#
# @par Numeric Input Fields
#
# Int and float input fields support "minimum", "maximum" and "step" (increment)
# settings.  Float fields also support decimal-point "precision".
#
# @par Button Input Fields
#
# Fields with datatype "button" should include a callback handle to a function,
# instance method or lambda.
#
# @par Output Fields
#
# Output fields support these datatypes: string, int, float, bool, pandas.
#
# Regardless of type, all output fields will be rendered on the GUI as a string 
# (QLabel), with the exception of "pandas".
#
# @par Pandas Output Fields
#
# Any given plugin can only declare ONE "pandas" output field, which is expected
# to contain all the tabular data output by that plugin.
#
# Pandas fields will be rendered to a QTableView.
#
class EnlightenPluginField:

    ##
    # @param name: identifying string
    # @param datatype: string (default), int, float, bool, pandas, button
    # @param direction: "output" (default) or "input" (from plugin's POV)
    # @param initial: initial value
    # @param minimum: lower bound (int/float only)
    # @param maximum: upper bound (int/float only)
    # @param step: increment (int/float only)
    # @param precision: digits past decimal place (float only)
    # @param callback: function reference if button clicked (button only)
    # @param tooltip: mouseover string
    def __init__(self, 
            name, 
            datatype    = "string", 
            direction   = "output", 
            initial     = None,
            minimum     = 0,
            maximum     = 100,
            step        = 1,
            precision   = 2,
            options     = None,
            callback    = None,
            tooltip     = None):

        self.name       = name
        self.datatype   = datatype
        self.direction  = direction
        self.initial    = initial
        self.maximum    = maximum
        self.minimum    = minimum
        self.step       = step
        self.precision  = precision
        self.callback   = callback
        self.tooltip    = tooltip
        self.options    = options

##
# This is a "request" object sent by the ENLIGHTEN GUI to the plug-in, containing
# a fresh measurement to be processed.  Each Request will have a unique request_id,
# which should be included in the associated EnlightenPluginResponse.
#
# This class is being defined here so users can understand exactly what a request
# looks like (also, to encapsulate all exchanged message types together). However, 
# ENLIGHTEN plug-ins will not themselves be expected to create Requests; instead,
# they should instantiate and return EnlightenPluginResponse.
#
# Note that enlighten.ProcessedReading objects the original wasatch.Reading, as 
# well as processed, dark, reference, and raw arrays.
#
@dataclass
class EnlightenPluginRequest:
    """
    @param request_id: an integral auto-incrementing id
    @param settings: a copy of wasatch.SpectrometerSettings
    @param processed_reading: a copy of enlighten.ProcessedReading
    @param fields: a key-value dictionary corresponding to the 
           EnlightenPluginFields (EPF) declared by the EnlightenPluginConfiguration.
           Note these aren't the EPF objects themselves; just the string
           names, and current scalar values.
    """
    request_id: int = -1
    spec: Spectrometer = field(default_factory=Spectrometer)
    settings: SpectrometerSettings = field(default_factory=SpectrometerSettings)
    processed_reading: ProcessedReading = field(default_factory=ProcessedReading)
    creation_time: datetime.datetime = datetime.datetime.now()
    fields: list[EnlightenPluginField] = field(default_factory=list)

##
# This abstract base class provides information to the plugin about the current 
# application state of ENLIGHTEN.  An instance of a concrete subclass of this
# will be passed to connect().
class EnlightenApplicationInfo:

    def __init__(self):
        pass

    ## @return currently selected x-axis ("px", "nm" or "cm")
    def get_x_axis_unit(self):
        pass

    ## @return e.g. C:\Users\mzieg\Documents\EnlightenSpectra
    def get_save_path(self):
        pass

    def reference_is_dark_corrected(self):
        return False

    def read_measurements(self):
        """
        returns a list of dicts of the current measurements in the measurements clipobard.
        """
        return [{}]

##
# After a plug-in has received an EnlightenPluginRequest and processed it, the 
# plug-in should instantiate and send an EnlightenPluginResponse in reply.  
#
# @par Commands
#
# An array of (setting, value) tuples to send to the currently selected
# spectrometer (or multiple spectrometers if controls are locked?)
#
# @par Metadata
#
# Key-value scalar pairs will be added to the "metadata" saved with each 
# .CSV or .JSON Measurement (requires block_enlighten=True).
#
# @par Overrides
#
# Currently limited to "processed", "recordable_dark" and "recordable_reference".  
# May someday include wavelengths, wavenumbers etc.
#
# @todo add metadata arrays as CSV columns
class EnlightenPluginResponse:

    ##
    # @param request:   handle to the originiating EnlightenPluginRequest 
    # @param commands:  array of (setting, value) tuples for spectrometer
    # @param message:   string to display on scope marquee
    # @param metadata:  dict added to any Measurements saved from this
    #                   ProcessedReading (requires block_enlighten)
    # @param outputs:   dict of configured EnlightenPluginField "output" values
    # @param overrides: dict of replacement arrays for ProcessedReading etc
    # @param series:    a dict of series names to series x/y data
    def __init__(self, 
            request,
            commands    = None,
            message     = None,
            metadata    = None,
            outputs     = None,
            overrides   = None,
            series      = None):   

        self.request    = request
        self.commands   = commands
        self.message    = message
        self.metadata   = metadata
        self.outputs    = outputs
        self.overrides  = overrides
        self.series     = series
