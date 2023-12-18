import pyqtgraph.exporters
import pyqtgraph
import logging
import json
import os
import re

from enlighten.measurement.Measurement import Measurement
from enlighten.parser.ColumnFileParser import ColumnFileParser
from enlighten.parser.ExportFileParser import ExportFileParser
from enlighten.parser.TextFileParser import TextFileParser
from enlighten.parser.DashFileParser import DashFileParser
from enlighten.parser.SPCFileParser import SPCFileParser
from enlighten.ui.ThumbnailWidget import ThumbnailWidget

import traceback

from enlighten.common import msgbox

from wasatch.ProcessedReading import ProcessedReading
from wasatch.SpectrometerSettings import SpectrometerSettings
from wasatch import utils as wasatch_utils

from enlighten import util, common

if common.use_pyside2():
    from PySide2 import QtGui
else:
    from PySide6 import QtGui

log = logging.getLogger(__name__)

##
# This is a Factory used by Measurements to create Measurement objects, each 
# coupled to a ThumbnailWidget.
class MeasurementFactory(object):

    def clear(self):
        pass

    def __init__(self, ctl):
        self.ctl = ctl

        self.observers = set()

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
    def create_from_spectrometer(self, spec, is_collapsed, generate_thumbnail=True, save=True):
        log.debug("creating Measurement from spec %s", spec.label)

        # instantiate the Measurement
        try:
            measurement = Measurement(self.ctl, spec = spec)
        except:
            msgbox("Failed to create measurement\n\n"+traceback.format_exc(), "Error")

        log.debug("created Measurement %s from reading %d", measurement.measurement_id, measurement.processed_reading.reading.session_count)

        if generate_thumbnail:
            try:
                self.create_thumbnail(measurement, is_collapsed)
            except:
                msgbox("Failed to create thumbnail.\n\n"+traceback.format_exc(), "Error")

        if save:
            try:
                for observer in self.observers:
                    observer(measurement=measurement, event="pre-save")
                measurement.save()
                for observer in self.observers:
                    observer(measurement=measurement, event="save")
            except:
                msgbox("Failed to dispatch save file.\n\n"+traceback.format_exc(), "Error")
        
        return measurement
    
    ##
    # Create the ThumbnailWidget for a Measurement, then render and emplace the 
    # rasterized thumbnail image.  Also add Measurements back-reference.
    def create_thumbnail(self, measurement, is_collapsed=False):
        if measurement.plugin_name == "":
            graph = self.ctl.graph
        else:
            log.debug(f"graph is plugin so sending plugin graph")
            graph = self.ctl.get_plugin_graph()

        measurement.thumbnail_widget = ThumbnailWidget(
            ctl             = self.ctl,
            measurement     = measurement,
            graph           = graph,        
            is_collapsed    = is_collapsed)

        try:
            pixmap = self.render_thumbnail_to_qpixmap(measurement)
            measurement.thumbnail_widget.set_pixmap(pixmap)
        except:
            log.error("error rendering thumbnail to qpixmap", exc_info=1)

    ## Render a Measurement's .processed array into a raster bitmap of the
    # spectrum in a small image suitable for display via a ThumbnailWidget.
    #
    # @todo seems like this should be in ThumbnailWidget?
    def render_thumbnail_to_qpixmap(self, measurement):

        spectrum = measurement.processed_reading.get_processed()
        if spectrum is None:
            log.error("render_thumbnaiL_to_qpixmap: can't render thumbnail w/o spectrum")
            return

        # apply the spectrum to the curve
        self.ctl.thumbnail_render_curve.setData(spectrum)

        # instantiate an exporter (could we re-use one for all thumbnails?)
        exporter = pyqtgraph.exporters.ImageExporter(self.ctl.thumbnail_render_graph.plotItem)

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
        new = Measurement(self.ctl, measurement=measurement)

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

        self.ctl.measurements.add(new)

        return new

    # ##########################################################################
    # Deserialize from disk
    # ##########################################################################

    ## Note that this always returns a LIST of Measurement, because the user 
    #  may select an Export file, or an appended Dash file, etc.
    def create_from_file(self, pathname, is_collapsed=False, generate_thumbnail=True):
        log.debug("create_from_file: pathname %s, is_collapsed %s", pathname, is_collapsed)

        if pathname is None or len(pathname.strip()) == 0:
            log.error("create_from_file: invalid pathname %s", pathname)
            return

        if not os.path.isfile(pathname):
            log.error("create_from_file: can't find %s", pathname)
            return

        # Some files can hold many Measurement, so even though we're loading
        # one file, we may return a list of Measurement
        measurements = None

        # peek in the file and guess at the format
        try:
            encoding = util.determine_encoding(pathname)
            log.debug(f"create_from_file: encoding {encoding} ({pathname})")
            if pathname.lower().endswith(".csv"):
                if self.looks_like_dash(pathname, encoding=encoding):
                    log.debug("looks_like_dash")
                    measurements = self.create_from_dash_file(pathname, encoding=encoding)
                elif self.looks_like_labeled_columns(pathname, encoding=encoding):
                    log.debug("looks_like_labeled_columns")
                    measurements = [ self.create_from_columnar_file(pathname, encoding=encoding) ]
                elif self.looks_like_enlighten_columns(pathname, encoding=encoding):
                    log.debug("looks_like_enlighten_columns")
                    measurements = [ self.create_from_columnar_file(pathname, encoding=encoding) ]
                elif self.looks_like_enlighten_columns(pathname, test_export=True, encoding=encoding):
                    log.debug("looks_like_enlighten_columns(export)")
                    measurements = self.create_from_export_file(pathname, encoding=encoding)
                elif self.looks_like_simple_columns(pathname, encoding=encoding):
                    log.debug("looks_like_simple_columns")
                    measurements = [ self.create_from_simple_columnar_file(pathname, encoding=encoding) ]
                else:
                    log.error("unrecognized CSV format %s", pathname)
            elif pathname.lower().endswith(".asc"):
                if self.looks_like_simple_columns(pathname, encoding=encoding):
                    log.debug("looks_like_simple_columns")
                    measurements = [ self.create_from_simple_columnar_file(pathname, encoding=encoding) ]
                else:
                    log.error("unrecognized ASC format %s", pathname)
            elif pathname.lower().endswith(".json"):
                measurements = self.create_from_json_file(pathname, encoding=encoding)
            elif pathname.lower().endswith(".spc"):
                measurements = self.create_from_spc_file(pathname)
        except:
            msgbox("failed to parse file %s" % pathname)
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
    def looks_like_dash(self, pathname, encoding="utf-8"):
        with open(pathname, "r", encoding=encoding) as infile:
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
    # Essentially, whether the FIRST valid (non-blank, non-column) line is an x-axis header
    def looks_like_labeled_columns(self, pathname, encoding="utf-8"):
        result = False
        first_line = None
        with open(pathname, "r", encoding=encoding) as infile:
            for line in infile:
                line = line.strip()
                if line.startswith('#') or len(line) == 0:
                    continue
                tok = line.lower().split(",")
                if re.match(r'^(pixel|wavelength|wavenumber)', tok[0]):
                    result = True
                first_line = line
                break

        log.debug(f"looks_like_labeled_columns: result {result}, first_line: {first_line}")
        return result

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
    def looks_like_enlighten_columns(self, pathname, test_export=False, encoding="utf-8"):
        linecount = 0
        with open(pathname, "r", encoding=encoding) as infile:
            for line in infile:
                # not all "ENLIGHTEN-style" files will necessarily have any one 
                # metadata field; check a couple common ones (that are unlikely 
                # to include embedded commas)
                for field in ["Integration Time", "Pixel Count", "Serial Number", "Model", "Laser Wavelength"]:
                    if line.startswith(field):
                        # count how many values (not empty comma-delimited nulls) appear
                        count = sum([1 if len(x.strip()) > 0 else 0 for x in line.split(",")])
                        if test_export:
                            result = count > 2
                            log.debug(f"looks_like_enlighten_columns: {result} (count {count}, required >2, line {line})")
                            return count > 2
                        else:
                            result = count == 2
                            log.debug(f"looks_like_enlighten_columns: {result} (count {count}, required 2, line {line})")
                            return count == 2
                linecount += 1
                if linecount > 100:
                    log.debug(f"looks_line_enlighten_columns: false because no typical metadata in {linecount} lines")
                    break
            
    def looks_like_simple_columns(self, pathname, encoding="utf-8") -> bool:
        """
        Determine whether file looks like a simple 2-column set of (x, y) pairs
        (floats, ints, whatever) with no metadata.  Supports tab- or comma-
        delimited files.
        
        Ignores anything AFTER the first blank line (Solis .asc files put metadata
        there).
        """
        with open(pathname, "r", encoding=encoding) as infile:
            for line in infile:
                line = line.strip()
                if len(line) == 0:
                    break

                if "\t" in line:
                    tok = [v.strip() for v in line.split("\t")]
                else:
                    tok = [v.strip() for v in line.split(",")]

                if len(tok) != 2:
                    log.debug(f"not a simple column file: {line}")
                    return False
                for v in tok:
                    try:
                        float(v)
                    except:
                        log.debug(f"not a simple column file: {line}")
                        return False
        log.debug(f"seems a simple column file")
        return True

    def create_from_dash_file(self, pathname, encoding="utf-8"):
        parser = DashFileParser(
            pathname     = pathname,
            save_options = self.ctl.save_options,
            encoding     = encoding)
        return parser.parse()

    def create_from_columnar_file(self, pathname, encoding="utf-8"):
        parser = ColumnFileParser(
            self.ctl, # needs a ctl because it creates a Measurement
            pathname     = pathname,
            save_options = self.ctl.save_options,
            encoding     = encoding)
        return parser.parse()

    def create_from_export_file(self, pathname, encoding="utf-8"):
        parser = ExportFileParser(
            pathname     = pathname,
            save_options = self.ctl.save_options,
            encoding     = encoding)
        return parser.parse()

    def create_from_json_file(self, pathname, encoding="utf-8"):
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
            pathname = pathname,
            graph = self.ctl.graph)
        return parser.parse()

    def create_from_simple_columnar_file(self, pathname, encoding="utf-8"):
        parser = TextFileParser(
            pathname = pathname,
            graph = self.ctl.graph)
        return parser.parse()

    def load_interpolated(self, settings):
        pathname = self.ctl.file_manager.get_pathname("Select measurement")
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

    ##
    # Used when loading .json measurements and exports.
    #
    # @param d (Input) a dict containing either a single "Measurement" or a
    #                  "Measurements" list
    # @returns a list of Measurement (even if only one), or none if invalid input
    def create_from_dict(self, d):
        measurements = []

        try:
            if "Measurements" in d:
                for m_data in d["Measurements"]:
                    m = Measurement(self.ctl, d=m_data)
                    if m is not None:
                        measurments.append(m)
            elif "Measurement" in d:
                m = Measurement(self.ctl, d=d["Measurement"])
                if m is not None:
                    measurements.append(m)
        except:
            log.error("Error instantiating Measurement(s) from dict)", exc_info=1)

        if len(measurements) > 0:
            return measurements
