import logging
import datetime
from dataclasses import dataclass, field
from enlighten import common
log = logging.getLogger(__name__)
from enlighten.scope.Spectrometer import Spectrometer
from wasatch.ProcessedReading import ProcessedReading
from wasatch.SpectrometerSettings import SpectrometerSettings
import numpy as np


class EnlightenPluginBase:

    def __init__(self, ctl):
        self.enlighten_info = None
        self.error_message = None
        self.name = None
        self._fields = []
        self.is_blocking = False
        self.block_enlighten = False
        self.has_other_graph = False
        self.table = None
        self.x_axis_label = None
        self.y_axis_label = None
        self.series = {}
        self.ctl = ctl

    def get_axis(self):
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex(
            ) == common.Axes.WAVELENGTHS:
            return self.settings.wavelengths
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex(
            ) == common.Axes.WAVENUMBERS:
            return self.settings.wavenumbers
        if self.ctl.form.ui.displayAxis_comboBox_axis.currentIndex(
            ) == common.Axes.PIXELS:
            return range(len(self.spectrum))

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
        if x is None:
            x = np.arange(len(y))
        if title is None:
            title = 'untitled'
            in_legend = False
        suffix = ''
        i = 2
        while title + suffix in self.series.keys():
            suffix = str(i)
            i += 1
        title = title + suffix
        self.series[title] = {'x': x, 'y': y, 'color': color, 'title':
            title, 'in_legend': in_legend}

    def to_graph(self, x):
        """

        Undo to_pixel conversion, and set point back to 

        currently selected graph X-Axis

        """
        domain = self.get_axis()
        target_x = round(x)
        roi = self.settings.eeprom.get_horizontal_roi()
        if roi:
            target_x = target_x + roi.start
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
        target_x = min(enumerate(domain), key=lambda P: abs(P[1] - x))[0]
        roi = self.settings.eeprom.get_horizontal_roi()
        if roi:
            return target_x - roi.start
        else:
            return target_x

    def wavelength_to_pixel(self, wavelength):
        return self.to_pixel(wavelength, self.settings.wavelengths)

    def wavenumber_to_pixel(self, wavenumber):
        return self.to_pixel(wavenumber, self.settings.wavenumbers)

    def get_configuration_obj(self):
        config = self.get_configuration()
        if config:
            return config
        return EnlightenPluginConfiguration(name=self.name, fields=self.
            _fields, is_blocking=self.is_blocking, block_enlighten=self.
            block_enlighten, has_other_graph=self.has_other_graph,
            series_names=[], x_axis_label=self.x_axis_label, y_axis_label=
            self.y_axis_label)

    def process_request_obj(self, request):
        self.series = {}
        self.metadata = {}
        response = self.process_request(request)
        if response:
            return response
        outputs = {}
        if self.table is not None:
            outputs = {'Table': self.table}
        log.debug(f'returning metadata = {self.metadata}')
        return EnlightenPluginResponse(request, series=self.series, outputs
            =outputs, metadata=self.metadata)

    def get_configuration(self):
        return None

    def connect(self, enlighten_info):
        log.debug('EnlightenPluginBase.connect')
        self.enlighten_info = enlighten_info
        return True

    def process_request(self, request):
        return EnlightenPluginResponse(request)

    def disconnect(self):
        pass


class EnlightenPluginConfiguration:

    def __init__(self, name, fields=None, has_other_graph=False,
        x_axis_label=None, y_axis_label=None, is_blocking=True,
        block_enlighten=False, streaming=True, events=None, series_names=
        None, multi_devices=False, dependencies=None, graph_type='line'):
        self.name = name
        self.fields = fields
        self.has_other_graph = has_other_graph
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.is_blocking = is_blocking
        self.block_enlighten = block_enlighten
        self.streaming = streaming
        self.events = events
        self.multi_devices = multi_devices
        self.series_names = series_names
        self.dependencies = dependencies
        self.graph_type = graph_type


class EnlightenPluginDependency:

    def __init__(self, name, dep_type=None, persist=False, prompt=None):
        self.name = name
        self.dep_type = dep_type
        self.persist = persist
        self.prompt = prompt


class EnlightenPluginField:

    def __init__(self, name, datatype='string', direction='output', initial
        =None, minimum=0, maximum=100, step=1, precision=2, options=None,
        callback=None, tooltip=None):
        self.name = name
        self.datatype = datatype
        self.direction = direction
        self.initial = initial
        self.maximum = maximum
        self.minimum = minimum
        self.step = step
        self.precision = precision
        self.callback = callback
        self.tooltip = tooltip
        self.options = options


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
    request_id = -1
    spec = field(default_factory=Spectrometer)
    settings = field(default_factory=SpectrometerSettings)
    processed_reading = field(default_factory=ProcessedReading)
    creation_time = datetime.datetime.now()
    fields = field(default_factory=list)

    def __init__(self, request_id=-1, spec=None, settings=None, creation_time=None, fields=None):
        self.request_id = request_id
        if spec:
            self.spec = spec
        if settings:
            self.settings = settings
        if creation_time:
            self.creation_time = creation_time
        if fields:
            self.fields = fields

class EnlightenApplicationInfo:

    def __init__(self):
        pass

    def get_x_axis_unit(self):
        pass

    def get_save_path(self):
        pass

    def reference_is_dark_corrected(self):
        return False

    def read_measurements(self):
        """

        returns a list of dicts of the current measurements in the measurements clipobard.

        """
        return [{}]


class EnlightenPluginResponse:

    def __init__(self, request, commands=None, message=None, metadata=None,
        outputs=None, overrides=None, series=None):
        self.request = request
        self.commands = commands
        self.message = message
        self.metadata = metadata
        self.outputs = outputs
        self.overrides = overrides
        self.series = series
