from PySide2 import QtGui

import pyqtgraph.exporters
import pyqtgraph
import logging
import json
import os
import re

from .ColumnFileParser import ColumnFileParser
from .ExportFileParser import ExportFileParser
from .SPCFileParser    import SPCFileParser
from .ThumbnailWidget  import ThumbnailWidget
from .DashFileParser   import DashFileParser
from .Measurement      import Measurement

from wasatch.ProcessedReading import ProcessedReading
from wasatch.SpectrometerSettings import SpectrometerSettings
from wasatch import utils as wasatch_utils

from . import util

log = logging.getLogger(__name__)

##
# This is a Factory used by Measurements to create Measurement objects, each 
# coupled to a ThumbnailWidget.
class MeasurementFactory(object):

    def clear(self):
        self.colors       = None
        self.graph        = None
        self.gui          = None
        self.kia          = None
        self.render_graph = None
        self.render_curve = None
        self.save_options = None
        self.stylesheets  = None
        self.measurements = None
        self.label_suffix = None    # currently set/cleared by BatchCollection, could be others
        self.observers    = set()

    def __init__(self,
            colors,
            file_manager,
            focus_listener,
            graph,
            gui,
            render_graph,
            render_curve,
            save_options,
            stylesheets):

        self.clear()

        self.colors         = colors
        self.file_manager   = file_manager
        self.focus_listener = focus_listener
        self.graph          = graph
        self.gui            = gui
        self.render_graph   = render_graph
        self.render_curve   = render_curve
        self.save_options   = save_options
        self.stylesheets    = stylesheets

        # will receive post-construction
        self.measurements = None    # backreference to Measurements 
        self.kia          = None    # KnowItAll.Feature 

    def register_observer(self, callback):
        self.observers.add(callback)

    def unregister_observer(self, callback):
        try:
            self.observers.remove(callback)
        except:
            pass

    # ##########################################################################
    # Live readings
    # ##########################################################################

    ## Create a Measurement from a Spectrometer, using its most-recent 
    #  ProcessedReading.
    def create_from_spectrometer(self, spec, is_collapsed, technique=None, generate_thumbnail=True, save=True):
        log.debug("creating Measurement from spec %s", spec.label)

        # instantiate the Measurement
        measurement = Measurement(
            save_options = self.save_options,
            spec         = spec,
            technique    = technique,
            measurements = self.measurements)
        log.debug("created Measurement %s from reading %d", measurement.measurement_id, measurement.processed_reading.reading.session_count)

        if generate_thumbnail:
            self.create_thumbnail(measurement, is_collapsed)

        if save:
            measurement.save()
            for observer in self.observers:
                observer(measurement=measurement, event="save")
        
        return measurement
    
    ##
    # Create the ThumbnailWidget for a Measurement, then render and emplace the 
    # rasterized thumbnail image.  Also add Measurements back-reference.
    def create_thumbnail(self, measurement, is_collapsed=False):
        measurement.thumbnail_widget = ThumbnailWidget(
            measurement     = measurement,
            graph           = self.graph,
            gui             = self.gui,
            colors          = self.colors,
            stylesheets     = self.stylesheets,
            is_collapsed    = is_collapsed,
            technique       = measurement.technique,
            focus_listener  = self.focus_listener,
            kia             = self.kia)
        try:
            pixmap = self.render_thumbnail_to_qpixmap(measurement)
            measurement.thumbnail_widget.set_pixmap(pixmap)
        except:
            log.error("error rendering thumbnail to qpixmap", exc_info=1)

    ## Render a Measurement's .processed array into a raster bitmap of the
    # spectrum in a small image suitable for display via a ThumbnailWidget.
    def render_thumbnail_to_qpixmap(self, measurement):

        spectrum = measurement.processed_reading.get_processed()
        if spectrum is None:
            log.error("render_thumbnaiL_to_qpixmap: can't render thumbnail w/o spectrum")
            return

        # apply the spectrum to the curve
        self.render_curve.setData(spectrum)

        # instantiate an exporter (could we re-use one for all thumbnails?)
        exporter = pyqtgraph.exporters.ImageExporter(self.render_graph.plotItem)

        # configure the exporter
        exporter.params.param('width' ).sigValueChanged.disconnect()
        exporter.params.param('height').sigValueChanged.disconnect()

        exporter.params['width' ] = 180
        exporter.params['height'] = 120

        # use the exporter to render the graph as an image
        byte_result = exporter.export(toBytes=True)

        # convert import the binary image into a QPixmap
        pixmap = QtGui.QPixmap(byte_result)

        return pixmap

    # ##########################################################################
    # From other Measurements
    # ##########################################################################

    ##
    # Used by External.Feature to generate a new ENLIGHTEN Measurement from an
    # EnlightenExternalResponse externally produced in response to an
    # EnlightenExternalRequest containing the source Measurement.
    #
    # @param measurement        (Input) to be the source of the cloned Measurement
    # @param changes            (Input) if present, a dict of values to fold-in and replace
    #                           (currently just spectrum, wavelengths and wavenumbers)
    # @param generate_thumbnail (Input) add to the capture bar?
    # @param save               (Input) auto-save to disk?
    #
    # Consider whether this method should be wrapped and called via Measurements.
    def clone(self, measurement, changes=None, generate_thumbnail=True, save=True):
        new = Measurement(measurement=measurement)

        # Fold in changes.  Note this has all kinds of opportunities for
        # error...I'm not currently validating that the returned spectrum has
        # the original number of pixels, that it has the same length as the
        # x-axes, etc.  And obviously it won't actually match the EEPROM
        # wavelength coeffs.  It might actually be safer to just generate an
        # all-new measurement, rather than risk a "broken" Measurement...but 
        # let's go with this for now.
        if changes is not None:
            a = wasatch_utils.dict_get_norm(changes, "Spectrum")
            if a is not None:
                new.processed_reading.processed = a

            a = wasatch_utils.dict_get_norm(changes, "Wavelengths")
            if a is not None:
                new.settings.wavelengths = a

            a = wasatch_utils.dict_get_norm(changes, "Wavenumbers")
            if a is not None:
                new.settings.wavenumbers = a

        if generate_thumbnail:
            self.create_thumbnail(new)

        if save:
            new.save()

        self.measurements.add(new)

        return new

    # ##########################################################################
    # Deserialize from disk
    # ##########################################################################

    ## Note that this always returns a LIST of Measurements, because the user 
    #  may select an Export file, or an appended Dash file, etc.
    def create_from_file(self, pathname, is_collapsed=False, generate_thumbnail=True):
        log.debug("create_from_file: pathname %s, is_collapsed %s", pathname, is_collapsed)

        if pathname is None or len(pathname.strip()) == 0:
            log.error("create_from_file: invalid pathname %s", pathname)
            return

        if not os.path.isfile(pathname):
            log.error("create_from_file: can't find %s", pathname)
            return

        # Some files can hold many Measurements, so even though we're loading
        # one file, we may return a list of Measurements
        measurements = None

        # peek in the file and guess at the format
        try:
            if pathname.lower().endswith(".csv"):
                if self.looks_like_dash(pathname):
                    log.debug("looks_like_dash")
                    measurements = self.create_from_dash_file(pathname)
                elif self.looks_like_raw_columns(pathname):
                    log.debug("looks_like_raw_columns")
                    measurements = [ self.create_from_columnar_file(pathname) ]
                elif self.looks_like_columns(pathname):
                    log.debug("looks_like_columns")
                    measurements = [ self.create_from_columnar_file(pathname) ]
                elif self.looks_like_columns(pathname, test_export=True):
                    log.debug("looks_like_columns(export)")
                    measurements = self.create_from_export_file(pathname)
                else:
                    log.error("unrecognized CSV format %s", pathname)
            elif pathname.lower().endswith(".json"):
                measurements = self.create_from_json_file(pathname)
            elif pathname.lower().endswith(".spc"):
                measurements = self.create_from_spc_file(pathname)
        except:
            log.error("failed to parse file %s", pathname, exc_info=1)

        if measurements is None:
            return

        for m in measurements:
            try:
                m.measurements = self.measurements
                if generate_thumbnail:
                    self.create_thumbnail(m, is_collapsed)
            except:
                log.error("create_from_file: error finalizing measurement", exc_info=1)

        for m in measurements:
            for observer in self.observers:
                observer(measurement=m,event="load")

        return measurements

    ##
    # Determine whether file looks like one of our row-ordered files (whether 
    # individual spectrum, appended spectra, or a row-ordered export)
    def looks_like_dash(self, pathname):
        with open(pathname, "r") as infile:
            return infile.readline().startswith("Dash Output")

    ##
    # Determine whether file looks like a raw columnar CSV with no metadata,
    # such as saved by RamanSpecCal.  The sample input looked like:
    #
    # \verbatim
    #     pixel, wavelength, wavenumber, corrected, raw, dark
    #     0,     802.35,     275.46,     892,       892, 0
    # \endverbatim
    #
    # Essentially, whether the first valid line is an x-axis header
    def looks_like_raw_columns(self, pathname):
        with open(pathname, "r") as infile:
            for line in infile:
                line = line.strip()
                if line.startswith('#') or len(line) == 0:
                    continue
                tok = line.lower().split(",")
                return re.match(r'^(pixel|wavelength|wavenumber)', tok[0])

    ##
    # Determine whether file looks like our individual column-ordered CSV files,
    # i.e. with metadata at the top.
    #
    # Our columnar files start with the list of Measurement.CSV_FILE_HEADER 
    # fields running down the top left (newer files lead with EXTRA_HEADER_FIELDS
    # first).  
    #
    # No Dash file would have a line starting with "Integration Time" (header row
    # starts with Line Number).
    #
    # Export files have very similar formats to columnar, so by adding one
    # parameter we can use the same test for both formats.  (Export files have
    # additional padding due to the leading px/nm/cm columns, so even an export
    # of a single measurement would have more than 2 columns).
    def looks_like_columns(self, pathname, test_export=False):
        linecount = 0
        with open(pathname, "r") as infile:
            for line in infile:
                if line.startswith("Integration Time"):
                    # count how many values (not empty comma-delimited nulls) appear
                    count = sum([1 if len(x.strip()) > 0 else 0 for x in line.split(",")])
                    if test_export:
                        return count > 2
                    else:
                        return count == 2
                linecount += 1
                if linecount > 100:
                    break
            
    def create_from_dash_file(self, pathname):
        parser = DashFileParser(
            pathname     = pathname,
            save_options = self.save_options)
        return parser.parse()

    def create_from_columnar_file(self, pathname):
        parser = ColumnFileParser(
            pathname     = pathname,
            save_options = self.save_options)
        return parser.parse()

    def create_from_export_file(self, pathname):
        parser = ExportFileParser(
            pathname     = pathname,
            save_options = self.save_options)
        return parser.parse()

    def create_from_json_file(self, pathname):
        try:
            with open(pathname) as f:
                data = json.load(f)
        except:
            return log.error("unable to load JSON from %s", pathname, exc_info=1)

        # distinguish between single-Measurement and multi-Measurement json files
        if isinstance(data, dict):
            m_data = { "Measurement": data }
        elif isinstance(data, list):
            m_data = { "Measurements": data }
        else:
            log.error("uncertain how to interpret parsed JSON from %s", pathname)
            return
        
        return self.create_from_dict(m_data)

    def create_from_spc_file(self, pathname):
        parser = SPCFileParser(
            graph = self.graph)
        return parser.parse(pathname)

    def load_interpolated(self, settings):
        pathname = self.file_manager.get_pathname("Select measurement")
        if pathname is None:
            return

        log.debug("loading to interpolate: %s", pathname)
        measurements = self.create_from_file(pathname, generate_thumbnail=False)
        if measurements is None:
            return

        m = measurements[0]

        # Interpolate the loaded spectrum component, because the Measurement we 
        # just loaded may have a different number of pixels than our current 
        # spectrometer, or may have been taken with a different wavecal.
        m.interpolate(settings)
        return m

    # ##########################################################################
    # External API
    # ##########################################################################

    ##
    # Used by External.Feature, also loading .json measurements and exports.
    #
    # @param d (Input) a dict containing either a single "Measurement" or a
    #                  "Measurements" list
    # @returns a list of Measurements (even if only one), or none if invalid input
    def create_from_dict(self, d):
        measurements = []

        try:
            if "Measurements" in d:
                for m_data in d["Measurements"]:
                    m = Measurement(d=m_data, measurements=self.measurements, save_options=self.save_options)
                    if m is not None:
                        measurments.append(m)
            elif "Measurement" in d:
                m = Measurement(d=d["Measurement"], measurements=self.measurements, save_options=self.save_options)
                if m is not None:
                    measurements.append(m)
        except:
            log.error("Error instantiating Measurement(s) from dict)", exc_info=1)

        if len(measurements) > 0:
            return measurements
