import datetime 
import logging
import numpy
import xlwt
import json
import copy
import csv
import re
import os

from wasatch.ProcessedReading import ProcessedReading

from . import common
from . import util
from SPyC_Writer import SPCFileWriter
from SPyC_Writer.SPCEnums import SPCFileType, SPCXType, SPCYType, SPCTechType

from wasatch.SpectrometerSettings import SpectrometerSettings
from wasatch import utils as wasatch_utils

log = logging.getLogger(__name__)

##
# Encapsulates a single saved measurement from one spectrometer, comprising
# a ProcessedReading (optionally containing the original Reading object that 
# generated it), metadata (Settings), as well as a ThumbnailWidget for display 
# on the capture bar.  Note that other than the ProcessedReading, 
# SpectrometerApplicationState is NOT retained in the Measurement.
#
# A Measurement object is created when:
#
# - the user clicks the "Acquire" button on the GUI
# - a BatchCollection triggers one or more Acquire events
# - the user loads a spectrum from disk
#
# If a Measurement is loaded from disk, it will not contain the original Reading
# object.  Also, the metadata may be limited.
#
# If a Measurement is generated live, it will also have a reference to the 
# spectrometer which generated it.
#
# Regardless of whether the Measurement was generated from a live capture 
# (Acquire) or loaded from disk, a ThumbnailWidget will be generated (not 
# necessarily instantly) for visualization.
#
# As some Measurements may be displayed in different x-axis coordinates, we need
# to store the "current / selected / displayed" x-axis for the Measurement. I'm
# tentatively thinking to do that in the ThumbnailWidget, as it's kind of an 
# attribute of the trace, but we'll see.
#
# I am not sure whether we really need separate Thumbnail and ThumbnailWidget
# classes, other than that they are literally very different things (the one
# is a pyqtgraph export, the other is a QWidget), even though one is typically
# displayed within the other.
#
# Given that there are multiple ways to create a Measurement, with somewhat
# different attributes and controlled background timing, a MeasurementFactory
# is provided to separately encapsulate the process of construction.
#
# Each Measurement has a .measurement_id, which is permanent.  The id is used 
# as the default label attribute (both for file basenames and for on-screen 
# display), but the label may be subsequently changed by the user.  
#
# @par Pathnames and Persistence
#
# There is no simple .pathname attribute for the Measurement, as one Measurement 
# may have been saved to any or all of several different file types.  
# 
# AT PRESENT, it is assumed that the creation of a Measurement will include 
# saving the Measurement to one or more output files at creation, but this is not 
# a long-term requirement (we may decide to support "session traces" which are 
# never actually persisted to disk; Spectrasuite and OceanView have these).
#
# There is a .pathnames set which aggregates all the pathnames which are known 
# related to this Measurement, though it is not guaranteed complete in the case 
# of loaded files from other sessions.  (Ideally all such files would contain
# the original measurement_id somewhere within them, though not necessarily in 
# the pathname.)
#
# If a Measurement has been deserialized from disk, it will have a 
# .source_pathname attribute to indicate the source file from which it was
# instantiated.
#
# Note that the application caps how many Measurements are visible in the
# Thumbnail bar at any given time, and currently ENLIGHTEN's file-management
# operations (rename, delete etc) only function on visible Thumbnails, so if
# you're streaming vast BatchCollections to disk such that they get rotated out
# of our buffer, you'll have to rename / delete them through other means.
#
# @par Renaming Measurements
#
# Renaming Measurements is a potentially thorny issue.  Early versions of
# ENLIGHTEN renamed the output file(s) when you changed the label of on-screen 
# thumbnail, and customers wish to retain that ability (ticket from 2019-07-19).
#
# However, there is all kinds of ugliness down this hole: 
#
# - What if you were appending measurements to one big CSV? 
# - What if you loaded the measurement for comparison from archival spectra? 
# - What if you loeaded the measurement from a big export file?
#
# My current decision is that we will retain the historical ability to rename
# any file(s) saved from the given Measurement IFF the files were CREATED
# by the CURRENT ENLIGHTEN session; OR if the spectrum was loaded from a 
# single file (not an export or appended collection).
#
# This distinction is made when Measurements are loaded or saved, and 
# tracked via a renameable_files list.  It's not as simple as checking
# whether the spectrum was created or loaded, because it matters what
# type of file it was loaded from, or which type of file it was saved to.
#
# A consequence of this design is that if you initially have CSV and XLS
# files saved, you can rename the thumbnail to "apple" and both CSV and XLS
# files will be renamed to apple.csv and apple.xls.  However, if you then
# clear your thumbnails (or quit / relaunch ENLIGHTEN) and load apple.csv
# from disk, if you then rename the file to banana.csv, it will NOT likewise
# rename apple.xls to banana.xls.
#
# Also, relabeling the Measurement on-screen, and even renaming the underlying
# file artifacts DOES NOT re-write or update the file contents.  The "label"
# field in the file metadata is not updated.  It would not be particularly hard 
# to re-save the file, but this seems like it would have many risks if a newer
# version of ENLIGHTEN changed the file format, or if there had been extra data
# in the file (ignored during a load operation, or added by the user post-save)
# which would then be destroyed.
#
# @par Thumbnails and resources
#
# Originally, ENLIGHTEN had no "Measurements", only "Thumbnails" -- the 
# spectra was literally stored (only) as the y-values of the thumbnail
# graph, with no x-axis, no metadata etc.  So it was an improvement to
# move forward to "Measurements with Thumbnails".  But there is a resource
# issue with EVERY Measurement having a ThumbnailWidget...what if we run
# a weekend collection taking 250,000 samples?
#
# A better architecture might be just "Measurements" (the data), plus
# a ThumbnailBar able to dynamically generate and display ThumbnailWidgets
# on scroll events (similar to a Swift TableView, where cells are populated
# as they scroll into view, and are released when offscreen).
#
# And possibly move away from the heavy "Widget" (with a couple Frames, 
# Buttons, the pyqtgraph etc) to a simpler table or tree view which would 
# probably use less memory.
#
# For now, I'm compromising by treating the on-screen thumbnails as a ringbuffer,
# and kicking-off old Measurements (from memory, not disk) when we exceed a
# limit.
#
# Note that the MeasurementFactory automatically saves new Measurements to disk
# (per SaveOptions) as they are created from Spectrometers, BEFORE they are 
# handed to Measurements for addition to the Thumbnail bar.  The process of
# creating a Measurement (from Spectrometer) and saving it to disk is atomic,
# so there is no need to worry that automatic deletion of Measurements for
# resource management will cause data to be lost.
#
# @par Exploits
#
# It is ASSUMED that the user used the same Settings (integration time, boxcar 
# smoothing, scan averaging etc) when taking the 'raw', 'dark' and 'reference'
# component spectra in generation of the 'processed' component.  Only a single
# Settings object is retained for the entire ProcessedReading, which is copied
# when the Measurement is created.  
#
# That is, if the user does something like this, the wrong integration time would
# be stored with the Measurement:
#
# 1. set integration time 100ms
# 2. pause scope
# 3. set integration time 200ms
# 4. click "Acquire" to save the current on-screen (paused) measurement
#
# There are various ways we could address this weakness (e.g., snap a Deep Copy 
# of Settings on pause()), but it's not a priority at this time.
#
# @todo more robust / defined behavior with duplicate labels across Measurements
#       (currently has some graphing glitches when adding / removing traces)
class Measurement(object):

    ##
    # These appear in legacy saved spectra files as-written (Dash format), so 
    # don't casually screw with them (could break customer applications).
    #
    # Note that all are scalars (no lists).
    CSV_HEADER_FIELDS = ['Line Number',
                         'Integration Time',
                         'Timestamp',
                         'Blank',
                         'Note',
                         'Temperature',
                         'CCD C0',
                         'CCD C1',
                         'CCD C2',
                         'CCD C3',
                         'CCD Offset',
                         'CCD Gain',
                         'CCD Offset Odd',
                         'CCD Gain Odd',
                         'Laser Wavelength',
                         'Laser Enable',
                         'Laser Power %',
                         'Laser Temperature',
                         'Pixel Count']
    CSV_HEADER_FIELDS_SET = set(CSV_HEADER_FIELDS)
    
    ## These CSV_HEADER_FIELDS only need to be used for row-ordered files
    ROW_ONLY_FIELDS = ['Blank', 'Line Number']

    ## These fields weren't in the original Dash file format, so only use for
    # the new "column-ordered" formats (including 'export')
    EXTRA_HEADER_FIELDS = ['ENLIGHTEN Version',
                           'Measurement ID',
                           'Serial Number',
                           'Model',
                           'Detector',
                           'Label',
                           'Declared Match',
                           'Declared Score',
                           'Scan Averaging',
                           'Boxcar',
                           'Technique',
                           'Baseline Correction Algo',
                           'ROI Pixel Start',
                           'ROI Pixel End',
                           'CCD C4',
                           'Slit Width',
                           'Vignetted',
                           'Interpolated',
                           'Wavenumber Correction',
                           'Raman Intensity Corrected',
                           'Deconvolved',
                           'Region',
                           'Laser Power mW',
                           'Battery %',
                           'Device ID',
                           'FW Version',
                           'FPGA Version']
    EXTRA_HEADER_FIELDS_SET = set(EXTRA_HEADER_FIELDS)

    def clear(self):
        self.appending                = False
        self.baseline_correction_algo = None
        self.basename                 = None
        self.declared_match           = None
        self.declared_score           = 0
        self.label                    = None
        self.measurement_id           = None
        self.measurements             = None 
        self.processed_reading        = None
        self.renamable_files          = set()
        self.renamed_manually         = False
        self.save_options             = None
        self.settings                 = None
        self.source_pathname          = None
        self.spec                     = None
        self.thumbnail_widget         = None
        self.timestamp                = None
        self.technique                = None

    ##
    # There are three valid instantiation patterns:
    #
    # - with spec (take latest from that Spectrometer)
    # - with source_pathname (deserializing from disk)
    def __init__(self, 
            processed_reading   = None,
            save_options        = None,
            settings            = None,
            source_pathname     = None,
            technique           = None,
            timestamp           = None,
            spec                = None,
            measurement         = None,
            measurements        = None,
            d                   = None):

        self.clear()

        self.save_options       = save_options
        self.measurements       = measurements

        if spec:
            log.debug("instantiating from spectrometer %s", str(spec))
            self.spec = spec

            # Use deepcopy() to ensure that subsequent changes to integration 
            # time, laser power, excitation etc do not retroactively change the 
            # historical state of the shared Spectrometer objects.  This also 
            # ensures that "live" Measurements always have a copy of the Settings 
            # of the spectrometer from which they were collected (including 
            # EEPROM etc).  It also helps with the case when a spectrometer
            # was disconnected (and optionally reconnected) after the Measurement
            # was saved, but before it was exported.
            self.settings = copy.deepcopy(spec.settings)

            # Copy things we want from SpectrometerApplicationState.
            #
            # Original thought was to deepcopy SpectrometerApplicationState, but 
            # the waterfall instances could get large.  And has duplicates of 
            # reference and dark, plus SIX RollingDataSet histories of detector 
            # and laser temperature.  For now, assuming we DON'T, and just taking 
            # the ProcessedReading. (Taking a deepcopy, because with plug-ins who
            # knows...)
            self.processed_reading  = copy.deepcopy(spec.app_state.processed_reading)
            self.technique          = spec.app_state.technique_name
            self.timestamp          = datetime.datetime.now()
            self.baseline_correction_algo = spec.app_state.baseline_correction_algo

        elif source_pathname:
            log.debug("instantiating from source pathname %s", source_pathname)            
            self.processed_reading  = processed_reading
            self.source_pathname    = source_pathname
            self.timestamp          = timestamp
            self.settings           = settings

        elif measurement:
            log.debug("instantiating from existing measurement %s", measurement.measurement_id)
            self.settings          = copy.deepcopy(measurement.settings)
            self.processed_reading = copy.deepcopy(measurement.processed_reading)
            self.measurements      = measurement.measurements
            self.save_options      = measurement.save_options
            self.timestamp         = datetime.datetime.now()

        elif d:
            log.debug("instantiating from dict")
            self.init_from_dict(d)

        else:
            raise Exception("Measurement requires exactly one of (spec, source_pathname, measurement, dict)")

        self.generate_id()

    ##
    # Called by PluginWidget
    def clone(self):
        # start with shallow copy
        m = copy.copy(self)

        # clean for exporting
        m.measurements = None
        m.save_options = None
        m.thumbnail_widget = None
        m.settings = copy.deepcopy(self.settings)
        m.processed_reading = copy.deepcopy(self.processed_reading)
        
        return m

    ##
    # This is experimental.  Eventually we want to be able to load Measurements 
    # saved as JSON.  We should also be able to receive externally-generated 
    # Measurements sent via JSON via the External API.  This is reasonably key
    # to both.  Also it's handy to use this as a free-form intermediate format 
    # for parsing external formats like SPC.
    def init_from_dict(self, d):

        if "Label" in d:
            self.label = d["Label"]

        # timestamp
        self.timestamp = datetime.datetime.now()
        if "Timestamp" in d:
            try:
                self.timestamp = datetime.datetime.strptime(d["Timestamp"], '%Y-%m-%d %H:%M:%S.%f')
            except:
                self.timestamp = datetime.datetime.now()
        else:
            self.timestamp = datetime.datetime.now()

        # SpectrometerSettings
        self.settings = SpectrometerSettings(d=wasatch_utils.dict_get_norm(d, "SpectrometerSettings"))

        # ProcessedReading
        self.processed_reading = ProcessedReading(d=wasatch_utils.dict_get_norm(d, ["ProcessedReading", "Spectrum", "Spectra"]))

        # how/where to do this properly?
        if len(self.processed_reading.processed) < len(self.settings.wavelengths):
            self.processed_reading.processed_vignetted = self.processed_reading.processed

    ##
    # We presumably loaded a measurement from disk, reprocessed it, and are now 
    # replacing the contents of the Measurement object with the reprocessed 
    # spectra, preparatory to re-saving (with a new timestamp and measurement_id.
    def replace_processed_reading(self, pr):
        self.processed_reading = pr
        self.timestamp = datetime.datetime.now()
        self.renamable_files = set()
        self.generate_id()

    def add_renamable(self, pathname):
        self.renamable_files.add(pathname)

    def generate_id(self):
        # It is unlikely that the same serial number will ever generate multiple 
        # measurements at the same timestamp in microseconds.
        sn = self.settings.eeprom.serial_number

        # can happen on loading malformed CSV files
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()

        ts = self.timestamp.strftime("%Y%m%d-%H%M%S-%f")

        self.measurement_id = "%s-%s" % (ts, sn)

        self.basename = self.measurement_id # use this as the original base filename

        # the ID is too long for on-screen display, so shorten it
        if self.label is None:
            self.label = "%s %s" % (self.timestamp.strftime("%H:%M:%S"), self.settings.eeprom.serial_number)

            self.label = self.generate_label()

            # append optional suffix
            # log.debug("checking for label_suffix")
            if self.measurements is not None and \
                    self.measurements.factory is not None and \
                    self.measurements.factory.label_suffix is not None:
                self.label += " %s" % self.measurements.factory.label_suffix
                # log.debug("applying label_suffix (%s): %s", self.measurements.factory.label_suffix, self.label)

                # this complicates saving from multiple spectrometers 
                # during batch collection
                self.measurements.factory.label_suffix = None

    def generate_label(self):
        try:
            label = self.save_options.label_template()
        except:
            label = "{time}"
        log.debug(f"generate_label: starting with template {label}")

        while True:
            m = re.search(r"{([a-z0-9_]+)}", label, re.IGNORECASE)
            if m is None:
                return label

            code = m.group(1)
            value = None
            if code == "time":
                value = self.timestamp.strftime("%H:%M:%S")
            elif hasattr(self.settings.eeprom, code):
                value = getattr(self.settings.eeprom, code)
            elif hasattr(self.settings.state, code):
                value = getattr(self.settings.state, code)
            else:
                value = self.get_metadata(code)

            if isinstance(value, float):
                value = f"{value:.3f}"

            label = label.replace("{%s}" % code, str(value))
            log.debug(f"generate_label: {code} -> {value} (label now {label})")

    def generate_basename(self):
        if self.save_options is None:
            return self.measurement_id
        else:
            if self.renamed_manually and self.save_options.allow_rename_files():
                return util.normalize_filename(self.label)
            else:
                return self.save_options.wrap_name(self.measurement_id)

    def dump(self):
        log.debug("Measurement:")
        log.debug("  measurement_id:        %s", self.measurement_id)
        log.debug("  label:                 %s", self.label)
        log.debug("  basename:              %s", self.basename)
        log.debug("  timestamp:             %s", self.timestamp)
        log.debug("  settings:              %s", self.settings)
        log.debug("  source_pathname:       %s", self.source_pathname)
        log.debug("  renamable_files:       %s", self.renamable_files)

        pr = self.processed_reading
        if pr is not None:
            log.debug("  processed_reading:")
            log.debug("    processed_vignetted: %s", pr.processed_vignetted[:5] if pr.processed_vignetted is not None else None)
            log.debug("    processed:           %s", pr.processed[:5] if pr.processed is not None else None)
            log.debug("    raw:                 %s", pr.raw      [:5] if pr.raw       is not None else None)
            log.debug("    dark:                %s", pr.dark     [:5] if pr.dark      is not None else None)
            log.debug("    reference:           %s", pr.reference[:5] if pr.reference is not None else None)

    ##
    # Display on the graph, if not already shown.
    def display(self):
        if self.thumbnail_widget is not None: 
            self.thumbnail_widget.add_curve_to_graph()

    ## 
    # Release any resources associated with this Measurement.  Note that this 
    # will automatically delete the ThumbnailWidget from its parent layout (if
    # emplaced), and mark the object tree for garbage collection within PySide/Qt.
    def delete(self, from_disk=False, update_parent=False):
        log.debug("deleting Measurement %s (from_disk %s, update_parent %s)", 
            self.measurement_id, from_disk, update_parent)

        if from_disk:
            for pathname in self.renamable_files:
                try:
                    os.remove(pathname)
                    log.debug("removed %s", pathname)
                except:
                    pass
            self.renamable_files = set()
                
        if update_parent:
            # This deletion request came from within the Measurement (presumably
            # from the ThumbnailWidget's Trash or Erase icons), so re-invoke the
            # deletion request through our parent, so that parent resources are 
            # likewise deleted.  We do NOT need to pass the from_disk flag, as 
            # we've already executed that, and we haven't given Measurements the 
            # ability to pass that down anyway.
            #
            # MZ: this feels a bit kludgy?
            
            if self.measurements is not None:
                self.measurements.delete_measurement(measurement=self)
                return

        # Take extra care releasing Qt resources associated with the ThumbnailWidget
        if self.thumbnail_widget is not None:
            # remove the trace from the graph
            self.thumbnail_widget.remove_curve_from_graph()

            # delete from Qt
            layout = self.thumbnail_widget.layout()
            if layout is not None:
                layout.removeWidget(self.thumbnail_widget)

            # pyqtgraph objects don't need this, but this is NOT a pyqtgraph
            # object: it's a PySide object, which does need this.
            self.thumbnail_widget.deleteLater()

        self.spec               = None
        self.settings           = None
        self.thumbnail_widget   = None
        self.processed_reading  = None

    def update_label(self, label, manual=False):
        if self.renamed_manually and not manual:
            log.debug("declining to automatically relabel a manually named measurement")
            return

        old_label = self.label

        # drop old trace (technically all we need to do is rename the label)
        was_displayed = False
        if self.thumbnail_widget:
            self.thumbnail_widget.rename(label)
            was_displayed = self.thumbnail_widget.is_displayed
            self.thumbnail_widget.remove_curve_from_graph(label=old_label) # remove using the old value

        # if they removed the label, nothing more to do
        if label is None:
            self.label = label
            return

        self.label = label

        # rename the underlying file(s)
        if self.save_options.allow_rename_files():
            self.rename_files()

        # re-apply trace with new legend
        if was_displayed:
            self.thumbnail_widget.add_curve_to_graph()

        if manual:
            self.renamed_manually = True

        # re-save (update metadata on disk)
        self.save()

    ##
    # The measurement has been relabled (say, "cyclohexane").  So if 
    # pathnames contains "old.csv" and "old.xls", we want to rename them to 
    # "cyclohexane.csv" and "cyclohexane.xls".  However, if those files 
    # already exist, we don't want to overwrite them (maybe the user is
    # looking at a lot of cyclohexane).  So if cyclohexane.csv already
    # exists, just make cyclohexane-1.csv, etc.  Whatever number we pick,
    # apply it to all the pathnames (cyclohexane-1.xls, even if there wasn't
    # already a cyclohexane.xls).
    #
    # Also note that there are at least four ways this Measurement could have been 
    # instantiated:
    # 1. It could have been loaded from ONE individual CSV (not necessarily within 
    #    EnlightenSpectra/YYYY-MM-DD).  
    #    - Renaming possible, but possibly not a good idea? <-- supported
    #
    # 2. It could have been one of a SET of Measurements loaded from a big CSV
    #    (an appended row-order or an exported column-order CSV).  
    #    - Renaming considered NOT POSSIBLE.
    #
    # 3. It could have been generated from live data and saved to one or more 
    #    single-spectrum files with various extensions (csv, xls, json, png etc).
    #    - Renaming possible and apparently customer desirable <-- supported
    #
    # 4. It could have been generated from live data and APPENDED to an
    #    existing file (typically row-ordered CSV).
    #    - Renaming considered NOT POSSIBLE
    def rename_files(self):
        if not self.renamable_files:
            return log.error("Measurement %s has no renamable files", self.measurement_id)

        exts = {}
        for pathname in self.renamable_files:
            m = re.match(r"^(.*[/\\])?([^/\\]+)\.([^./\\]+)$", pathname)
            if m:
                basedir  = m.group(1)
                basename = m.group(2)
                ext      = m.group(3)
                if ext in exts:
                    return log.error("found multiple renamable_files with extension %s: %s", ext, self.renamable_files)
                exts[ext] = (basedir, basename)
            else:
                return log.error("renamable_file w/o extension: %s", pathname)

        # determine what suffix we're going to use, if any

        n = 0 # potential suffix 
        while True:
            conflict = False
            for ext in exts:
                (basedir, basename) = exts[ext]

                if n == 0:
                    new_pathname = "%s%s.%s" % (basedir, self.label, ext)
                else:
                    new_pathname = "%s%s-%d.%s" % (basedir, self.label, n, ext)

                if os.path.exists(new_pathname):
                    conflict = True
                    break

            if not conflict:
                break

            n += 1

        # apparently there's no conflict for any extension using suffix 'n'
        self.renamable_files = set()
        for ext in exts:
            (basedir, basename) = exts[ext]

            old_pathname = "%s%s.%s" % (basedir, basename, ext)
            if n == 0:
                new_pathname = "%s%s.%s" % (basedir, self.label, ext)
            else:
                new_pathname = "%s%s-%d.%s" % (basedir, self.label, n, ext)

            try:
                os.rename(old_pathname, new_pathname)
                self.add_renamable(new_pathname)
            except:
                return log.error("Failed to rename %s -> %s", old_pathname, new_pathname, exc_info=1)

    ## @todo cloud etc
    def save(self):
        if self.save_options.save_csv():
            self.save_csv_file()

        if self.save_options.save_text():
            self.save_txt_file()

        if self.save_options.save_excel():
            self.save_excel_file()

        if self.save_options.save_json():
            self.save_json_file()

        if self.save_options.save_spc():
            self.save_spc_file()

    def save_csv_file(self):
        if self.save_options is not None and self.save_options.save_by_row():
            self.save_csv_file_by_row()
        else:
            self.save_csv_file_by_column()

    ##
    # This function is provided because legacy Dash and ENLIGHTEN saved row-
    # ordered CSV files with very specific column headers and sequence which we 
    # don't want to casually break.
    #
    # @todo Note that temperature fields come from the underlying Reading object,
    #       and in the case that we loaded previously-saved spectra from disk, 
    #       we're not currently re-instantiating Reading objects (only the 
    #       ProcessedReading, which is all that's needed for on-screen traces), 
    #       so currently those output a deliberately-suspicious -99.
    #
    # @todo replace if/elif with dict of lambdas
    def get_metadata(self, field):
        field = field.lower()

        # allow plugins to stomp metadata 
        if self.processed_reading.plugin_metadata is not None:
            pm = self.processed_reading.plugin_metadata
            for k, v in pm.items():
                if field == k.lower():
                    return v

        wavecal = self.settings.get_wavecal_coeffs()

        if field == "enlighten version":         return common.VERSION
        if field == "measurement id":            return self.measurement_id
        if field == "serial number":             return self.settings.eeprom.serial_number
        if field == "model":                     return self.settings.full_model()
        if field == "label":                     return self.label
        if field == "detector":                  return self.settings.eeprom.detector
        if field == "scan averaging":            return self.settings.state.scans_to_average
        if field == "boxcar":                    return self.settings.state.boxcar_half_width
        if field == "line number":               return self.save_options.line_number if self.save_options is not None else 0
        if field == "integration time":          return self.settings.state.integration_time_ms
        if field == "timestamp":                 return self.timestamp
        if field == "blank":                     return self.settings.eeprom.serial_number # for Multispec
        if field == "note":                      return self.save_options.note() if self.save_options is not None else ""
        if field == "temperature":               return self.processed_reading.reading.detector_temperature_degC if self.processed_reading.reading is not None else -99
        if field == "technique":                 return self.technique
        if field == "baseline correction algo":  return self.baseline_correction_algo
        if field == "ccd c0":                    return wavecal[0]
        if field == "ccd c1":                    return wavecal[1]
        if field == "ccd c2":                    return wavecal[2]
        if field == "ccd c3":                    return wavecal[3]
        if field == "ccd c4":                    return 0 if len(wavecal) < 5 else wavecal[4]
        if field == "ccd offset":                return self.settings.eeprom.detector_offset # even
        if field == "ccd gain":                  return self.settings.state.gain_db if self.settings.is_sig() else self.settings.eeprom.detector_gain # even
        if field == "ccd offset odd":            return self.settings.eeprom.detector_offset_odd
        if field == "ccd gain odd":              return self.settings.eeprom.detector_gain_odd
        if field == "laser wavelength":          return self.settings.excitation()
        if field == "laser enable":              return self.settings.state.laser_enabled or self.settings.state.acquisition_laser_trigger_enable
        if field == "laser temperature":         return self.processed_reading.reading.laser_temperature_degC if self.processed_reading.reading is not None else -99
        if field == "pixel count":               return self.settings.pixels()
        if field == "declared match":            return str(self.declared_match) if self.declared_match is not None else None
        if field == "declared score":            return self.declared_match.score if self.declared_match is not None else 0
        if field == "roi pixel start":           return self.settings.eeprom.roi_horizontal_start
        if field == "roi pixel end":             return self.settings.eeprom.roi_horizontal_end
        if field == "vignetted":                 return self.processed_reading.is_cropped()
        if field == "interpolated":              return self.save_options.interp.enabled if self.save_options is not None else False
        if field == "raman intensity corrected": return self.processed_reading.raman_intensity_corrected
        if field == "deconvolved":               return self.processed_reading.deconvolved
        if field == "region":                    return self.settings.state.region
        if field == "slit width":                return self.settings.eeprom.slit_size_um
        if field == "wavenumber correction":     return self.settings.state.wavenumber_correction
        if field == "battery %":                 return self.processed_reading.reading.battery_percentage if self.processed_reading.reading is not None else 0
        if field == "fw version":                return self.settings.microcontroller_firmware_version
        if field == "fpga version":              return self.settings.fpga_firmware_version 
        if field == "laser power %":             return self.processed_reading.reading.laser_power_perc if self.processed_reading.reading is not None else 0
        if field == "device id":                 return str(self.settings.device_id)

        if field == "laser power mw":            
            if self.processed_reading.reading is not None and \
                self.processed_reading.reading.laser_power_mW is not None and \
                self.processed_reading.reading.laser_power_mW > 0:
                return self.processed_reading.reading.laser_power_mW 
            else:
                return ""

        log.error("Unknown CSV header field: %s", field)
        return ""

    def get_extra_header_fields(self):
        fields = copy.copy(Measurement.EXTRA_HEADER_FIELDS)

        # if self.spec is not None:
        #     if self.settings.eeprom.multi_wavecal is not None:
        #         fields.append("Position")
            
        return fields
        
    # ##########################################################################
    # Excel
    # ##########################################################################

    ## 
    # Save the spectra in xls format (currently, one worksheet per x-axis)
    #
    # As with save_csv_file_by_column(), currently disregarding SaveOptions
    # selections of what x-axis and ProcessedReading fields to include, because
    # there is little benefit to removing them from individual files. We can
    # always add this later if requested.
    # 
    # @note Only saving one column of data at this time. Make sure to
    # limit the total columns to 255 when saving multiple spectra.
    def save_excel_file(self):
        pr          = self.processed_reading
        wavelengths = self.settings.wavelengths
        wavenumbers = self.settings.wavenumbers
        pixels      = len(pr.raw)

        wbk = xlwt.Workbook()
        sheet_summary    = wbk.add_sheet('Summary')
        sheet_spectrum   = wbk.add_sheet('Spectrum')

        style_f2 = xlwt.XFStyle()
        style_f2.num_format_str = '0.00'

        style_f5 = xlwt.XFStyle()
        style_f5.num_format_str = '0.00000'

        style_datetime = xlwt.easyxf(num_format_str='D/M/YY h:mm:ss')

        ########################################################################
        # Populate spectra
        ########################################################################

        # header row
        sheet_spectrum.write(0, 0, "Pixel")
        sheet_spectrum.write(0, 1, "Wavelength")
        sheet_spectrum.write(0, 2, "Wavenumber")
        sheet_spectrum.write(0, 3, "Processed")
        sheet_spectrum.write(0, 4, "Raw")
        sheet_spectrum.write(0, 5, "Dark")
        sheet_spectrum.write(0, 6, "Reference")

        # when making relative measurements against a reference, we typically
        # need more digits of precision to avoid "stair-stepping"
        style = style_f2
        if pr.reference is not None:
            style = style_f5

        roi = None
        if self.settings is not None:
            roi = self.settings.eeprom.get_horizontal_roi()
        cropped = roi is not None and pr.is_cropped()

        # interpolation
        interp = self.save_options.interp if self.save_options is not None else None
        if interp is not None and interp.enabled:
            ipr = interp.interpolate_processed_reading(pr, wavelengths=wavelengths, wavenumbers=wavenumbers, settings=self.settings)
            if ipr is not None:
                wavelengths = ipr.wavelengths
                wavenumbers = ipr.wavenumbers
                pixels = ipr.pixels
                pr = ipr.processed_reading

        # spectra (float() calls because library gets confused by Numpy types)
        first_row = 1
        row_count = 0
        for pixel in range(pixels):
            if roi is not None and not roi.contains(pixel):
                continue

            row = first_row + row_count
            sheet_spectrum.write        (row, 0, pixel)
            sheet_spectrum.write        (row, 1, float(wavelengths  [pixel]), style_f2)
            if wavenumbers is not None:
                sheet_spectrum.write    (row, 2, float(wavenumbers  [pixel]), style_f2)
            sheet_spectrum.write        (row, 4, float(pr.raw       [pixel]), style)
            if pr.dark is not None:
                sheet_spectrum.write    (row, 5, float(pr.dark      [pixel]), style)
            if pr.reference is not None:
                sheet_spectrum.write    (row, 6, float(pr.reference [pixel]), style)

            if not cropped:
                sheet_spectrum.write    (row, 3, float(pr.processed [pixel]), style)
            elif interp.enabled:
                sheet_spectrum.write    (row, 3, float(pr.processed_vignetted[pixel]), style)
            elif roi.contains(pixel):
                sheet_spectrum.write    (row, 3, float(pr.processed_vignetted[pixel - roi.start]), style)

            row_count += 1

        ########################################################################
        # Populate Summary
        ########################################################################

        sheet_summary.col(1).width = 40 * 256 # MZ: unit?

        ## @see https://stackoverflow.com/a/26059224
        def write_pair(label, value, style=None):
            log.debug("write_pair: label %s, value %s, style %s, row %d", label, value, style, write_pair.row)
            sheet_summary.write(write_pair.row, 0, label)
            if style is None:
                sheet_summary.write(write_pair.row, 1, value)
            else:
                sheet_summary.write(write_pair.row, 1, value, style)
            write_pair.row += 1
        write_pair.row = 1

        write_pair("", "ENLIGHTEN Summary Report")

        fields = self.get_extra_header_fields()
        fields.extend(Measurement.CSV_HEADER_FIELDS)
        for field in fields:
            if field == "Timestamp":
                write_pair(field, self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"), style=style_datetime)
            elif field not in Measurement.ROW_ONLY_FIELDS:
                value = self.get_metadata(field)
                write_pair(field, value)

        if self.processed_reading.plugin_metadata is not None:
            for k, v in self.processed_reading.plugin_metadata.items():
                if k not in fields:
                    write_pair(k, v)

        ########################################################################
        # Done
        ########################################################################

        today_dir = self.generate_today_dir()
        pathname = os.path.join(today_dir, "%s.xls" % self.generate_basename())
        try:
            wbk.save(pathname)
            log.info("saved %s", pathname)
            self.add_renamable(pathname)
        except Exception as exc:
            log.critical("Problem saving workbook: %s", pathname, exc_info=1)

    def generate_today_dir(self):
        return "." if self.save_options is None else self.save_options.generate_today_dir()

    # ##########################################################################
    # JSON
    # ##########################################################################

    ##
    # Express the current Measurement as a single JSON-compatible dict.  Use this 
    # for both save_json_file and External.Feature.
    def to_dict(self):
        pr          = self.processed_reading
        wavelengths = self.settings.wavelengths
        wavenumbers = self.settings.wavenumbers
        pixels      = len(pr.processed)
        
        m = {                   # m = Measurement
            "metadata": {},
            "spectrum": {},
        }
        md = m["metadata"]      # md = Metadata
        sp = m["spectrum"]      # sp = Spectrum (should have used spectra?)

        # output additional (name, value) metadata pairs at the top,
        # not included in row-ordered CSV
        for field in self.get_extra_header_fields():
            md[field] = self.get_metadata(field)

        # output (name, value) metadata pairs at the top,
        # using the same names and order as our row-ordered CSV
        for field in Measurement.CSV_HEADER_FIELDS:
            if field not in Measurement.ROW_ONLY_FIELDS:
                if field == "Timestamp":
                    md["Timestamp"] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
                else:
                    md[field] = self.get_metadata(field)

        if self.processed_reading.plugin_metadata is not None:
            for k, v in self.processed_reading.plugin_metadata.items():
                if k not in md:
                    md[k] = v

        # interpolation
        ipr = None
        interp = self.save_options.interp if self.save_options is not None else None
        if interp is not None and interp.enabled:
            ipr = interp.interpolate_processed_reading(pr, wavelengths=wavelengths, wavenumbers=wavenumbers, settings=self.settings)
            if ipr is not None:
                pixels = ipr.pixels
                pr = ipr.processed_reading

        # same capitalization as CSV per request
        if self.save_options.save_processed()   and pr.processed is not None: sp["Processed"] = util.clean_list(pr.get_processed())
        if self.save_options.save_raw()         and pr.raw       is not None: sp["Raw"]       = util.clean_list(pr.raw)
        if self.save_options.save_dark()        and pr.dark      is not None: sp["Dark"]      = util.clean_list(pr.dark)
        if self.save_options.save_reference()   and pr.reference is not None: sp["Reference"] = util.clean_list(pr.reference)

        m["spectrometerSettings"] = self.settings.to_dict()

        if ipr is not None:
            m["spectrometerSettings"]["wavelengths"] = ipr.wavelengths
            m["spectrometerSettings"]["wavenumbers"] = ipr.wavenumbers

        return m

    ##
    # Render the current Measurement to JSON.  Use this for both save_json_file
    # and External.Feature.
    def to_json(self):
        m = self.to_dict()
        s = json.dumps(m, sort_keys=True, indent=2)
        return util.clean_json(s)

    def save_spc_file(self, use_basename=False) -> None:
        today_dir = self.generate_today_dir()
        current_x = self.save_options.multispec.graph.current_x_axis # a round about way to get the x axis, but it works
        log_text = f"Exported from Wasatch Photonics ENLIGHTEN.\nDevice {self.spec.label}"
        if use_basename:
            pathname = "%s.spc" % self.basename
        else:
            pathname = os.path.join(today_dir, "%s.spc" % self.generate_basename())
        if current_x == common.Axes.WAVELENGTHS:
            spc_writer = SPCFileWriter.SPCFileWriter(SPCFileType.TXVALS,
                                      x_units = SPCXType.SPCXNMetr,
                                      y_units = SPCYType.SPCYCount,
                                      experiment_type = SPCTechType.SPCTechRmn,
                                      log_text = log_text,
                                      )
            spc_writer.write_spc_file(pathname, 
                                      self.processed_reading.processed, 
                                      numpy.asarray(self.spec.settings.wavelengths), 
                                      )
        elif current_x == common.Axes.WAVENUMBERS:
            spc_writer = SPCFileWriter.SPCFileWriter(SPCFileType.TXVALS,
                                      x_units = SPCXType.SPCXWaven,
                                      y_units = SPCYType.SPCYCount,
                                      experiment_type = SPCTechType.SPCTechRmn,
                                      log_text = log_text,
                                      )
            spc_writer.write_spc_file(pathname, 
                                      self.processed_reading.processed, 
                                      numpy.asarray(self.spec.settings.wavenumbers),
                                      )
        elif current_x == common.Axes.PIXELS:
            spc_writer = SPCFileWriter.SPCFileWriter(SPCFileType.DEFAULT,
                                      experiment_type = SPCTechType.SPCTechRmn,
                                      log_text = log_text,
                                      )
            spc_writer.write_spc_file(pathname, 
                                      self.processed_reading.processed,
                                      y_units = SPCYType.SPCYCount,
                                      )
        else :
            log.error(f"current x axis doesn't match vaild values. Aborting SPC save")
            return

    ##
    # Save the Measurement in a JSON file for simplified programmatic parsing.
    # in the next column and so on (similar layout as the Excel output).
    #
    # As with save_excel_file(), currently disregarding SaveOptions selections 
    # of what x-axis and ProcessedReading fields to include, because there is 
    # little benefit to removing them from individual files. We can always add 
    # this later if requested.
    def save_json_file(self, use_basename=False):
        today_dir = self.generate_today_dir()
        if use_basename:
            pathname = "%s.json" % self.basename
        else:
            pathname = os.path.join(today_dir, "%s.json" % self.generate_basename())

        s = self.to_json()
        with open(pathname, "w", encoding='utf-8') as f:
            f.write(s)

        log.info("saved JSON %s", pathname)
        self.add_renamable(pathname)
    
    # ##########################################################################
    # Column-ordered CSV
    # ##########################################################################

    ##
    # Save the Measurement in a CSV file with the x-axis in one column, spectra 
    # in the next column and so on (similar layout as the Excel output).
    #
    # Note that currently this is NOT writing UTF-8 / Unicode, although KIA-
    # generated labels are Unicode.  (Dieter doesn't seem to like Unicode CSV)
    def save_csv_file_by_column(self, use_basename=False, ext="csv", delim=",", include_header=True, include_metadata=True):
        pr          = self.processed_reading
        wavelengths = self.settings.wavelengths
        wavenumbers = self.settings.wavenumbers
        pixels      = len(pr.raw)
        
        today_dir = self.generate_today_dir()
        if use_basename:
            pathname = "%s.%s" % (self.basename, ext)
        else:
            pathname = os.path.join(today_dir, "%s.%s" % (self.generate_basename(), ext))

        # vignetting
        roi = None
        if self.settings is not None:
            roi = self.settings.eeprom.get_horizontal_roi()
        cropped = roi is not None and pr.is_cropped()

        # interpolation
        interp = self.save_options.interp if self.save_options is not None else None
        if interp is not None and interp.enabled:
            ipr = interp.interpolate_processed_reading(pr, wavelengths=wavelengths, wavenumbers=wavenumbers, settings=self.settings)
            if ipr is not None:
                wavelengths = ipr.wavelengths
                wavenumbers = ipr.wavenumbers
                pixels = ipr.pixels
                pr = ipr.processed_reading

        with open(pathname, "w", newline="", encoding='utf-8') as f:

            out = csv.writer(f, delimiter=delim)

            if include_metadata:
                # output additional (name, value) metadata pairs at the top,
                # not included in row-ordered CSV
                outputted = set()
                for field in self.get_extra_header_fields():
                    value = self.get_metadata(field)
                    out.writerow([field, value])
                    outputted.add(field)

                # output (name, value) metadata pairs at the top,
                # using the same names and order as our row-ordered CSV
                for field in Measurement.CSV_HEADER_FIELDS:
                    if field not in Measurement.ROW_ONLY_FIELDS:
                        value = self.get_metadata(field)
                        out.writerow([field, value])
                        outputted.add(field)
                out.writerow([])

                if self.processed_reading.plugin_metadata is not None:
                    for k, v in self.processed_reading.plugin_metadata.items():
                        if k not in outputted:
                            out.writerow([k, v])

            headers = []
            if self.save_options is not None:
                if self.save_options.save_pixel()      : headers.append("Pixel")         
                if self.save_options.save_wavelength() : headers.append("Wavelength")    
                if self.save_options.save_wavenumber() : headers.append("Wavenumber")    
                if self.save_options.save_processed()  : headers.append("Processed")     
                if self.save_options.save_raw()        : headers.append("Raw")           
                if self.save_options.save_dark()       : headers.append("Dark")          
                if self.save_options.save_reference()  : headers.append("Reference")     
            else:
                headers.append("Wavenumber")
                headers.append("Processed")     

            if include_header:
                out.writerow(headers)

            def formatted(prec, array, pixel):
                if array is None:
                    return
                value = array[pixel]
                return '%.*f' % (prec, value)

            # store extra precision for relative measurements
            precision = 5 if pr.reference is not None else 2

            for pixel in range(pixels):

                # don't output cropped rows
                if roi is not None and not roi.contains(pixel):
                    continue

                values = []
                if self.save_options is not None:
                    if self.save_options.save_pixel()      : values.append(pixel)
                    if self.save_options.save_wavelength() : values.append(formatted(2,         wavelengths,  pixel))
                    if self.save_options.save_wavenumber() : values.append(formatted(2,         wavenumbers,  pixel))

                    if self.save_options.save_processed(): 
                        if not cropped:
                            values.append(formatted(precision, pr.processed, pixel)) 
                        elif interp.enabled:
                            values.append(formatted(precision, pr.processed_vignetted, pixel))
                        elif roi.contains(pixel):
                            values.append(formatted(precision, pr.processed_vignetted, pixel - roi.start))
                        else:
                            # this is a cropped pixel, so arguably it could be None (,,), @na, -1
                            # or various other things, but this will probably break the least downstream
                            values.append(0)

                    if self.save_options.save_raw()        : values.append(formatted(precision, pr.raw,       pixel))
                    if self.save_options.save_dark()       : values.append(formatted(precision, pr.dark,      pixel))
                    if self.save_options.save_reference()  : values.append(formatted(precision, pr.reference, pixel))
                else:
                    values.append(formatted(2, wavenumbers,  pixel))
                    values.append(formatted(precision, pr.processed, pixel)) 

                out.writerow(values)
        log.info("saved columnar %s", pathname)
        self.add_renamable(pathname)

    # ##########################################################################
    # TXT
    # ##########################################################################

    ##
    # This is essentially the same as column-ordered CSV, but with no metadata,
    # no header row and no commas. (per proj "Pioneer")
    def save_txt_file(self, use_basename=False):
        self.save_csv_file_by_column(use_basename, ext="txt", delim=" ", include_header=False, include_metadata=False)

    # ##########################################################################
    # Row-ordered CSV
    # ##########################################################################

    ## generate a legacy Dash file header with one or more serial numbers
    #
    # @note left static for Measurements.export_by_row
    @staticmethod
    def generate_dash_file_header(serial_numbers):
        header = [ "Dash Output v2.1", 
                   "ENLIGHTEN version: %s" % common.VERSION,
                   "Row", 
                   "Pixel Data" ]
        header.extend(serial_numbers)
        return header
    
    ##
    # Save a spectrum in CSV format with the whole spectrum on one line,
    # such that multiple acquisitions could be appended with one line
    # per spectrum.  
    #
    # This is was the ONLY supported save format in Dash and legacy ENLIGHTEN, 
    # and still makes great sense for batch collections (it's much easier to 
    # append lines than columns to an existing file).
    #
    # At the moment, this method is also being used to append new measurements
    # to existing files.
    #
    # Right now, we're using serial number in a new Measurement's measurement_id,
    # hence label, hence filename.  Having serial_number in a row-ordered CSV 
    # which aggregates multiple spectrometers is potentially confusing, but when
    # we save the first spectrum we don't know that's the intention.
    #
    # Note that currently this is NOT writing UTF-8 / Unicode, although KIA-
    # generated labels are Unicode.
    #
    # Note that Measurements saved while "appending" are NOT considered renamable
    # at the file level, while Measurements saved to individual files are.
    #
    # @todo support processed_vignetted
    def save_csv_file_by_row(self):
        sn = self.settings.eeprom.serial_number

        if self.save_options.append() and self.save_options.append_pathname is not None and os.path.exists(self.save_options.append_pathname):
            # continue appending to the current target
            pathname = self.save_options.append_pathname
            log.debug("save_csv_file_by_row: re-using append pathname %s", pathname)
            self.appending = True
        else:
            # anytime we save a CSV by-row, it becomes the implicit target for
            # subsequent appendage
            today_dir = self.generate_today_dir()
            pathname = os.path.join(today_dir, "%s.csv" % self.generate_basename())
            log.debug("save_csv_file_by_row: creating pathname %s", pathname)

            self.save_options.reset_appendage(pathname)

            if os.path.exists(pathname):
                os.remove(pathname)
            self.appending = False
            self.add_renamable(pathname)

        file_header = Measurement.generate_dash_file_header([sn])

        try:
            # are we appending or creating?
            if self.appending:
                # we're appending to an existing file
                verb = "appended"
                with open(pathname, "a", newline="") as f:
                    csv_writer = csv.writer(f)

                    # initialize the x-axis lines, if they haven't been done yet
                    # for this spectrometer
                    self.write_x_axis_lines(csv_writer)

                    # write the spectral lines
                    self.write_processed_reading_lines(csv_writer)

                # you can neither delete nor rename spectra which were appended
                # to an existing file
                self.thumbnail_widget.disable_edit()
                self.thumbnail_widget.disable_trash()
            else:
                # we're creating a new file
                verb = "saved"
                with open(pathname, "w", newline="") as f: 
                    csv_writer = csv.writer(f)

                    # write the full header anytime the target does not yet exist
                    csv_writer.writerow(file_header)
                    csv_writer.writerow(self.CSV_HEADER_FIELDS)

                    # initialize the x-axis lines
                    self.write_x_axis_lines(csv_writer)

                    # write the spectral lines
                    self.write_processed_reading_lines(csv_writer)
        except Exception as exc:
            log.critical("Exception writing row-ordered CSV file: %s", pathname, exc_info=1)
            return

        # append
        self.save_options.line_number += 1
        self.save_options.set_appended_serial(sn)

        log.info("Successfully %s row-ordered %s", verb, pathname)

    ##
    # For row-ordered CSVs, output any x-axis fields that have been selected.
    # Only do this if they have not yet been output for a given spectrometer.
    # 
    # To support multiple spectrometers, we're adding the spectrometer's serial
    # number (as well as the x-axis unit) to the Notes field.
    #
    # @note the Dash file format reprints wavecal coeffs and excitation in every 
    #       line, so technically the recipient could regenerate pixels, 
    #       wavelengths and wavenumbers for every spectrum anyway.  These are 
    #       just convenience rows.
    #
    def write_x_axis_lines(self, csv_writer):
        sn = self.settings.eeprom.serial_number

        if self.save_options.have_appended_serial(sn):
            return

        if self.save_options.save_pixel():
            self.write_row(csv_writer, "pixels")
        if self.save_options.save_wavelength():
            self.write_row(csv_writer, "wavelengths")
        if self.save_options.save_wavenumber():
            self.write_row(csv_writer, "wavenumbers")

    ##
    # For row-ordered CSVs, output any ProcessedReading fields which have been
    # selected.
    # 
    # In column-ordered files, it's not a big deal to always store dark / 
    # reference / raw, because they're easy to ignore if you're not using them.  
    # However, in row-ordered files, those extra lines can be really confusing, 
    # partly because of the "prefix columns" enforced by the file format 
    # (repeating wavecal coeffs etc), but also because when "appending" to 
    # existing files, it becomes very hard to tell which lines are spectrum-vs-
    # component.  So anyway, be careful not to print extra lines here that the 
    # user didn't request.
    #
    # Regardless, there's no "caching" these across Measurements, because 
    # technically the user could have (and often would) take a new dark and 
    # reference repeatedly during a session. (They're not 'reasonably persistent' 
    # as with the x-axis.)
    def write_processed_reading_lines(self, csv_writer):
        if self.save_options.save_processed():
            self.write_row(csv_writer, "Processed")
        if self.save_options.save_raw():
            self.write_row(csv_writer, "Raw")
        if self.save_options.save_dark():
            self.write_row(csv_writer, "Dark")
        if self.save_options.save_reference():
            self.write_row(csv_writer, "Reference")

    ##
    # @see Scooby-Doo
    def write_row(self, csv_writer, field):
        row = self.build_row(field)
        if row is not None:
            csv_writer.writerow(row)

    ##
    # Generate a single row of output for row-ordered CSV files.  The contents 
    # of the generated row depend on the 'field' parameter.  
    #
    # Metadata is only populated for x-axis fields and the FIRST ProcessedReading 
    # array.
    def build_row(self, field):
        field = field.lower()

        a = None
        pr = self.processed_reading
        prec = 5 if pr.reference is not None else 2
        prefix_metadata = False

        if field.lower() == "pixels":
            a = list(range(self.settings.pixels()))
            prec = 0
        elif field.lower() == "wavelengths":
            a = self.settings.wavelengths
            prec = 2
        elif field.lower() == "wavenumbers":
            if self.settings.wavenumbers is None:
                raise Exception("can't save wavenumbers without excitation")
            a = self.settings.wavenumbers
            prec = 2
        elif field.lower() == "processed":
            a = pr.processed
        elif field.lower() == "dark":
            a = pr.dark
        elif field.lower() == "reference":
            a = pr.reference
        elif field.lower() == "raw":
            a = pr.raw
        else:
            log.error("build_row: unknown field %s" % field)

        if a is None:
            return None
            
        row = []

        # don't repeat metadata for spectrum components
        prefix_metadata = field.lower() not in ["dark", "reference", "raw"]

        # populate the prepended metadata fields per Dash format
        for header in self.CSV_HEADER_FIELDS:
            if header == "Note" and field.lower() != "processed":
                row.append(field)
            elif prefix_metadata or header in [ "Line Number" ]:
                row.append(self.get_metadata(header))
            else:
                # skip these fields on spectrum components
                # (we don't actually track the integration time, laser status etc for
                # dark and referenced spectra, and for raw it's the same as processed)
                row.append('')

        # append the selected array
        row.extend(['%.*f' % (prec, value) for value in a])

        return row

    ## Called (by way of ThumbnailWidget -> KnowItAll.Feature -> Measurements) 
    # when KnowItAll has generated a KnowItAll.DeclaredMatch for this Measurement.
    def id_callback(self, declared_match):
        # store the match
        self.declared_match = declared_match
        
        # re-save files using current SaveOptions (will store new label, overwriting old files with old name)
        # (these will definitely be in TODAY directory, regardless of where they were loaded from)
        self.save()

        # close-out the pending button click on the thumbnail (basically just 
        # turns the button back from red to gray)
        if self.thumbnail_widget is not None:
            self.thumbnail_widget.id_complete_callback()

    ## Not currently used
    def has_component(self, component):
        pr = self.processed_reading
        if pr is None:
            return False

        component = component.lower()
        if component.startswith("raw"):
            a = pr.raw
        elif component.startswith("dark"):
            a = pr.dark
        elif component.startswith("reference"):
            a = pr.reference
        elif component.startswith("processed"):
            a = pr.processed
        else:
            return False
        
        return a is not None and len(a) > 0

    ## 
    # Passed a SpectrometerSettings object (containing wavelengths, wavenumbers
    # etc), return a copy of this Measurement's ProcessedReading which has been
    # interpolated to the passed x-axis.  
    #
    # Interpolate on wavelength if available, otherwise wavenumbers, otherwise 
    # just copy the uninterpolated pixel data.
    #
    # Who calls this?
    def interpolate(self, new_settings):
        log.debug("interpolating %s", self.measurement_id)
        if new_settings is None:
            return

        pr = self.processed_reading

        if self.settings.wavelengths is not None and len(self.settings.wavelengths) and \
            new_settings.wavelengths is not None and len( new_settings.wavelengths):
           old_x = self.settings.wavelengths
           new_x =  new_settings.wavelengths
        elif self.settings.wavenumbers is not None and len(self.settings.wavenumbers) and \
              new_settings.wavenumbers is not None and len( new_settings.wavenumbers):
           old_x = self.settings.wavenumbers
           new_x =  new_settings.wavenumbers
        else:
            log.error("no interpolation possible")
            return 

        log.debug("interpolating from (%.2f, %.2f) to (%.2f, %.2f)", 
            old_x[0], old_x[-1], new_x[0], new_x[-1]);
        
        if pr.raw is not None and len(pr.raw) > 0:
            pr.raw = numpy.interp(new_x, old_x, pr.raw)

        if pr.dark is not None and len(pr.dark) > 0:
            pr.dark = numpy.interp(new_x, old_x, pr.dark)

        if pr.reference is not None and len(pr.reference) > 0:
            pr.reference = numpy.interp(new_x, old_x, pr.reference)

        if pr.processed is not None and len(pr.processed) > 0:
            pr.processed = numpy.interp(new_x, old_x, pr.processed)
        
        log.debug("interpolation complete")
