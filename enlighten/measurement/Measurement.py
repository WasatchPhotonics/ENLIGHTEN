import datetime
import logging
import numpy as np
import jcamp
import xlwt
import json
import copy
import csv
import re
import os

from wasatch.ProcessedReading import ProcessedReading

from enlighten import common
from enlighten import util
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
# - What if you loaded the measurement from a big export file?
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
class Measurement:

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
                           'ROI Start Line',
                           'ROI Stop Line',
                           'CCD C4',
                           'Slit Width',
                           'Cropped',
                           'Interpolated',
                           'Wavenumber Correction',
                           'Raman Intensity Corrected',
                           'Deconvolved',
                           'Region',
                           'High Gain Mode',
                           'Laser Power mW',
                           'Electrical Dark Correction',
                           'Battery %',
                           'Device ID',
                           'FW Version',
                           'FPGA Version',
                           'BLE Version',
                           'Prefix',
                           'Suffix',
                           'Preset',
                           'Auto-Raman',
                           'Session Count',
                           'Plugin Name']

    EXTRA_HEADER_FIELDS_SET = set(EXTRA_HEADER_FIELDS)

    def clear(self):
        self.appending                = False
        self.baseline_correction_algo = None
        self.basename                 = None
        self.declared_match           = None
        self.declared_score           = 0
        self.label                    = None
        self.measurement_id           = None
        self.processed_reading        = None
        self.pathname_by_ext          = {}
        self.renamed_manually         = False
        self.settings                 = None
        self.source_pathname          = None
        self.spec                     = None
        self.thumbnail_widget         = None
        self.timestamp                = None
        self.technique                = None
        self.roi_active               = False
        self.note                     = ""
        self.prefix                   = ""
        self.suffix                   = ""
        self.plugin_name              = ""

        # cache of metadata only generated / rendered at save
        self.metadata                 = {}

    ##
    # There are three valid instantiation patterns:
    #
    # - with spec (take latest from that Spectrometer)
    # - with source_pathname (deserializing from disk)
    # - with data (for instance, from processed plugin spectra)
    def __init__(self, 
            ctl                 = None,
            processed_reading   = None,
            settings            = None,
            source_pathname     = None,
            timestamp           = None,
            spec                = None,
            measurement         = None,
            d                   = None):

        self.ctl = ctl

        self.clear()
        self.roi_active         = False

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

            if self.ctl:
                # do these AFTER we have a processed_reading
                self.note   = self.expand_template(self.ctl.save_options.note())
                self.prefix = self.expand_template(self.ctl.save_options.prefix())
                self.suffix = self.expand_template(self.ctl.save_options.suffix())

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
            self.ctl               = measurement.ctl
            self.timestamp         = datetime.datetime.now()

        elif d:
            log.debug("instantiating from dict")
            self.init_from_dict(d)

        else:
            raise Exception("Measurement requires exactly one of (spec, source_pathname, measurement, dict)")

        if self.ctl.interp.enabled:
            self.ctl.interp.process(self.processed_reading)

        self.generate_id()
        self.generate_label()

    ##
    # Called by PluginWidget
    def clone(self):
        # start with shallow copy
        m = copy.copy(self)

        # clean for exporting
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

        self.label = d.get("Label", None)
        self.plugin_name = d.get("Plugin Name", None)

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
        pr_d = wasatch_utils.dict_get_norm(d, ["ProcessedReading", "Spectrum", "Spectra"])
        self.processed_reading = ProcessedReading(d=pr_d, settings=self.settings)

    ##
    # We presumably loaded a measurement from disk, reprocessed it, and are now
    # replacing the contents of the Measurement object with the reprocessed
    # spectra, preparatory to re-saving (with a new timestamp and measurement_id).
    def replace_processed_reading(self, pr):
        self.processed_reading = pr
        self.timestamp = datetime.datetime.now()
        self.pathname_by_ext = {}
        self.generate_id()
        self.generate_label()

    def add_pathname(self, pathname):
        ext = pathname.split(".")[-1]
        self.pathname_by_ext[ext] = pathname

    def generate_id(self):
        # It is unlikely that the same serial number will ever generate multiple
        # measurements at the same timestamp in microseconds.
        sn = self.settings.eeprom.serial_number

        # can happen on loading malformed CSV files
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()

        ts = self.timestamp.strftime("%Y%m%d-%H%M%S-%f")
        self.measurement_id = f"{ts}-{sn}"

        # Note that this is the wrapped filename exclusive of extension 
        # ({prefix}-{filename_template}-{suffix}). If the user later renames
        # the thumbnail, the manually-entered label (possibly suffixed with -n
        # in case of duplicates) will be stored as the new self.basename.
        self.generate_basename() 

    def generate_label(self):
        if self.label is not None:
            log.debug(f"generate_label: retaining existing label {self.label}")
            return

        if self.ctl:
            if self.ctl.save_options.filename_as_label():
                # note this will be wrapped with prefix and suffix
                self.label = self.basename 
            else:
                self.label = self.expand_template(self.ctl.save_options.label_template())
                if self.ctl.save_options.multipart_suffix:
                    self.label += f" {self.ctl.save_options.multipart_suffix}"

    def expand_template(self, template):
        """
        Some GUI text fields allow the user to enter strings containining "macro 
        templates" which are dynamically expanded and evaluated at runtime.

        Macros look like "{field_name}", where field_name can be any object 
        attribute in wasatch.EEPROM, wasatch.SpectrometerState, or Measurement
        metadata (any field supported by Measurement.get_metadata). As a 
        convenience some hardcoded macros are also supported, such as {time}.

        @todo We can't easily expand the set of objects whose attributes can
              be used (like BatchCollection) without running into potential
              namespace collisions (different objects can have identically-
              named attributes, leading to ambiguity).  Templates should
              move toward a prefixed notation like "m.measurement_id",
              "b.current_batch_count" etc.  This could then be implemented
              within a call to string.format(), giving users access to
              full precision controls etc.

              Also I'd pull this out into a TemplateFeature.
        """
        log.debug(f"expand_template: starting with template {template}")
        while True:
            # macros look like {integration_time_ms} or {gain_db:0.1f}
            m = re.search(r"{([a-z0-9_ ]+)(:\d*\.\d*f)?}", template, re.IGNORECASE)
            if m is None:
                return template

            orig = m.group(0)
            macro = m.group(1)
            fmt = "{0:%s}" % m.group(2)[1:] if m.group(2) else None
            value = None

            ####################################################################
            # macro-only fields (don't map to existing data)
            ####################################################################

            if   macro == "time": value = self.timestamp.strftime("%H_%M_%S")
            elif macro == "date": value = self.timestamp.strftime("%Y-%m-%d")
            elif macro == "file_timestamp": value = self.timestamp.strftime("%Y-%m-%d_%H_%M_%S%f")

            # note all date components are upper-case and times are lower-case 
            # for consistency (may confuse C programmers, should make sense to 
            # spectroscopists)
            elif macro == "YYYY": value = self.timestamp.strftime("%Y")
            elif macro == "MM": value = self.timestamp.strftime("%m")
            elif macro == "DD": value = self.timestamp.strftime("%d")
            elif macro == "hh": value = self.timestamp.strftime("%H")
            elif macro == "mm": value = self.timestamp.strftime("%M")
            elif macro == "ss": value = self.timestamp.strftime("%S")
            elif macro == "ffffff": value = self.timestamp.strftime("%f")
            elif macro == "integration_time_sec": value = self.settings.state.integration_time_ms / 1000.0

            ####################################################################
            # pull from measurement data
            ####################################################################

            elif self.processed_reading and self.processed_reading.reading and hasattr(self.processed_reading.reading, macro):
                value = getattr(self.processed_reading.reading, macro)
            elif hasattr(self.settings.eeprom, macro):
                value = getattr(self.settings.eeprom, macro)
            elif hasattr(self.settings.state, macro):
                value = getattr(self.settings.state, macro)
            else:
                value = self.get_metadata(macro)

            if isinstance(value, float):
                if fmt is None:
                    if macro in ['gain_db']:
                        fmt = "{0:.1f}"
                    elif 'excitation' in macro or macro in ["integration_time_sec"]:
                        fmt = "{0:.3f}"
                    else:
                        fmt = "{0:.2f}"
                try:
                    value = fmt.format(value)
                except ValueError:
                    log.error(f"unable to format value {value} as {fmt}", exc_info=1)
                    value = macro

            template = template.replace(orig, str(value))
            log.debug(f"expand_template: {orig} -> {value} (now {template})")

    # Note that this wraps the prefix and suffix around the expanded template.
    # Prefix and Suffix are not retained in manually-renamed measurements (ctrl-E).
    #
    # YOU ARE HERE - bar-2 is not being saved as self.basename.
    #                self.label is "bar", and subsequent calls
    #                to "resave" are going to overwrite / recreate bar.csv, not 
    #                bar-2.csv.
    def generate_basename(self):
        if self.basename is None:
            if self.ctl is None or self.ctl.save_options is None:
                self.basename = self.measurement_id

            elif self.renamed_manually and self.ctl.save_options.allow_rename_files() and len(self.pathname_by_ext) > 0:
                # return whatever we last used when saving the file
                ext = sorted(keys(self.pathname_by_ext))[0]
                pathname = self.pathname_by_ext[ext]
                _, filename = os.path.split(pathname)
                self.basename, _ = os.path.splitext(filename)
                
            else:
                basename = self.expand_template(self.ctl.save_options.filename_template())
                self.basename = self.ctl.save_options.wrap_name(basename, self.prefix, self.suffix)
        return self.basename

    def dump(self):
        log.debug("Measurement:")
        log.debug("  measurement_id:        %s", self.measurement_id)
        log.debug("  label:                 %s", self.label)
        log.debug("  basename:              %s", self.basename)
        log.debug("  timestamp:             %s", self.timestamp)
        log.debug("  settings:              %s", self.settings)
        log.debug("  source_pathname:       %s", self.source_pathname)
        log.debug("  pathnames:             %s", self.pathname_by_ext)

        pr = self.processed_reading
        if pr is not None:
            proc = pr.get_processed()
            raw  = pr.get_raw()
            dark = pr.get_dark()
            ref  = pr.get_reference()

            log.debug("  processed_reading:")
            log.debug("    processed:           %s", proc[:5] if proc is not None else None)
            log.debug("    raw:                 %s", raw [:5] if raw  is not None else None)
            log.debug("    dark:                %s", dark[:5] if dark is not None else None)
            log.debug("    reference:           %s", ref [:5] if ref  is not None else None)

    ##
    # Display on the graph, if not already shown.
    def display(self):
        if self.thumbnail_widget is not None:
            self.thumbnail_widget.add_curve_to_graph()

    def is_displayed(self):
        if self.thumbnail_widget is not None:
            return self.thumbnail_widget.is_displayed

    ##
    # Release any resources associated with this Measurement.  Note that this
    # will automatically delete the ThumbnailWidget from its parent layout (if
    # emplaced), and mark the object tree for garbage collection within PySide/Qt.
    def delete(self, from_disk=False, update_parent=False):
        log.debug("deleting Measurement %s (from_disk %s, update_parent %s)",
            self.measurement_id, from_disk, update_parent)

        if from_disk:
            for ext, pathname in self.pathname_by_ext.items():
                try:
                    os.remove(pathname)
                    log.debug("removed %s %s", ext.upper(), pathname)
                except:
                    pass
            self.pathname_by_ext = {}

        if update_parent:
            # This deletion request came from within the Measurement (presumably
            # from the ThumbnailWidget's Trash or Erase icons), so re-invoke the
            # deletion request through our parent, so that parent resources are
            # likewise deleted.  We do NOT need to pass the from_disk flag, as
            # we've already executed that, and we haven't given Measurements the
            # ability to pass that down anyway.
            #
            # MZ: this feels a bit kludgy?

            if self.ctl and self.ctl.measurements is not None:
                self.ctl.measurements.delete_measurement(measurement=self)
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

        # drop old trace (technically all we need to do is rename the label)
        was_displayed = False
        if self.thumbnail_widget:
            self.thumbnail_widget.rename(label)
            was_displayed = self.thumbnail_widget.is_displayed
            self.thumbnail_widget.remove_curve_from_graph()

        # if they removed the label, nothing more to do
        if label is None:
            self.label = label
            return

        self.label = label

        # rename the underlying file(s)
        if self.ctl:
            if self.ctl.save_options.allow_rename_files() or self.ctl.save_options.filename_as_label():
                if not self.rename_files():
                    return

        # re-apply trace with new legend
        if was_displayed:
            self.thumbnail_widget.add_curve_to_graph()

        if manual:
            self.renamed_manually = True

        # re-save (update metadata on disk)
        self.save(resave=True)

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
    #
    # @returns True on success
    def rename_files(self):
        if not self.pathname_by_ext:
            log.error("Measurement %s has no renamable files", self.measurement_id)
            return False

        exts = {}
        for ext, pathname in self.pathname_by_ext.items():
            m = re.match(r"^(.*[/\\])?([^/\\]+)\.[^./\\]+$", pathname)
            if m:
                basedir  = m.group(1)
                basename = m.group(2)
                exts[ext] = (basedir, basename)

        # determine what suffix we're going to use, if any

        n = 0 # potential suffix
        while True:
            conflict = False
            for ext in exts:
                (basedir, basename) = exts[ext]

                new_basename = util.normalize_filename(self.label)
                if n > 0:
                    new_basename += f"-{n}"
                new_pathname = os.path.join(basedir, f"{new_basename}.{ext}")

                if os.path.exists(new_pathname):
                    conflict = True
                    break

            if not conflict:
                break
            n += 1

        # apparently there's no conflict for any extension using suffix 'n'
        self.pathname_by_ext = {}
        for ext in exts:
            (basedir, basename) = exts[ext]

            new_basename = util.normalize_filename(self.label)
            if n > 0:
                new_basename += f"-{n}"

            old_pathname = os.path.join(basedir, f"{basename}.{ext}")
            new_pathname = os.path.join(basedir, f"{new_basename}.{ext}")

            try:
                log.debug(f"renaming {old_pathname} -> {new_pathname}")
                os.rename(old_pathname, new_pathname)
                self.add_pathname(new_pathname)
            except:
                log.error("Failed to rename %s -> %s", old_pathname, new_pathname, exc_info=1)
                return False

        log.debug(f"rename_files: saving new basename {new_basename}")
        self.basename = new_basename

        return True

    ## @todo cloud etc
    def save(self, resave=False):
        saved = False
        if not self.ctl:
            return

        if self.ctl.save_options.save_csv():
            self.save_csv_file(resave=resave)
            saved = True

        if self.ctl.save_options.save_text():
            self.save_txt_file(resave=resave)
            saved = True

        if self.ctl.save_options.save_excel():
            self.save_excel_file(resave=resave)
            saved = True

        if self.ctl.save_options.save_json():
            self.save_json_file(resave=resave)
            saved = True

        if self.ctl.save_options.save_spc():
            self.save_spc_file(resave=resave)
            saved = True

        if self.ctl.save_options.save_dx():
            self.save_dx_file(resave=resave)
            saved = True

        if not saved:
            if self.ctl.measurements:
                self.ctl.measurements.ctl.marquee.error("No save formats selected -- spectrum not saved to disk")

    def save_csv_file(self, resave=False):
        if self.ctl is None:
            self.save_csv_file_by_column(resave=resave)
        else:
            if self.ctl.save_options is not None and self.ctl.save_options.save_by_row():
                self.save_csv_file_by_row(resave=resave)
            else:
                self.save_csv_file_by_column(resave=resave)

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
        orig = field
        field = field.lower()

        # allow plugins to stomp standard metadata
        if self.processed_reading.plugin_metadata is not None:
            pm = self.processed_reading.plugin_metadata
            for k, v in pm.items():
                if field == k.lower():
                    log.debug(f"get_metadata: stomping {k} from plugin metadata {v}")
                    return v

        # if this field has already been computed, use cached
        if orig in self.metadata:
            return self.metadata[orig]

        wavecal = self.settings.get_wavecal_coeffs()

        # use Auto-Raman settings, even if not "retained"
        if (self.processed_reading.reading and
            self.processed_reading.reading.take_one_request and
            self.processed_reading.reading.take_one_request.auto_raman_request):
            if field == "auto-raman":            return True
            if field == "integration time":      return self.processed_reading.reading.new_integration_time_ms
            if field == "scan averaging":        return self.processed_reading.reading.sum_count
            if field == "ccd gain":              return self.processed_reading.reading.new_gain_db if self.settings.is_sig() else self.settings.eeprom.detector_gain
        else: 
            if field == "auto-raman":            return False
            if field == "integration time":      return self.settings.state.integration_time_ms
            if field == "scan averaging":        return self.settings.state.scans_to_average
            if field == "ccd gain":              return self.settings.state.gain_db if self.settings.is_sig() else self.settings.eeprom.detector_gain

        if field == "enlighten version":         return common.VERSION
        if field == "measurement id":            return self.measurement_id
        if field == "serial number":             return self.settings.eeprom.serial_number
        if field == "model":                     return self.settings.full_model()
        if field == "label":                     return self.label
        if field == "detector":                  return self.settings.eeprom.detector
        if field == "boxcar":                    return self.settings.state.boxcar_half_width
        if field == "line number":               return self.ctl.save_options.line_number if (self.ctl and self.ctl.save_options) else 0
        if field == "timestamp":                 return self.timestamp
        if field == "blank":                     return self.settings.eeprom.serial_number # for Multispec
        if field == "temperature":               return self.processed_reading.reading.detector_temperature_degC if self.processed_reading.reading is not None else -99
        if field == "technique":                 return self.technique
        if field == "baseline correction algo":  return self.baseline_correction_algo
        if field == "ccd c0":                    return 0 if len(wavecal) < 1 else wavecal[0]
        if field == "ccd c1":                    return 0 if len(wavecal) < 2 else wavecal[1]
        if field == "ccd c2":                    return 0 if len(wavecal) < 3 else wavecal[2]
        if field == "ccd c3":                    return 0 if len(wavecal) < 4 else wavecal[3]
        if field == "ccd c4":                    return 0 if len(wavecal) < 5 else wavecal[4]
        if field == "ccd offset":                return self.settings.eeprom.detector_offset # even
        if field == "ccd offset odd":            return self.settings.eeprom.detector_offset_odd
        if field == "ccd gain odd":              return self.settings.eeprom.detector_gain_odd
        if field == "high gain mode":            return self.settings.state.high_gain_mode_enabled
        if field == "laser wavelength":          return self.settings.excitation()
        if field == "laser enable":              return self.settings.state.laser_enabled 
        if field == "laser temperature":         return self.processed_reading.reading.laser_temperature_degC if self.processed_reading.reading is not None else -99
        if field == "pixel count":               return self.settings.pixels()
        if field == "declared match":            return str(self.declared_match) if self.declared_match is not None else None
        if field == "declared score":            return self.declared_match.score if self.declared_match is not None else 0
        if field == "roi pixel start":           return self.settings.eeprom.roi_horizontal_start
        if field == "roi pixel end":             return self.settings.eeprom.roi_horizontal_end
        if field == "roi start line":            return self.settings.eeprom.roi_vertical_region_1_start
        if field == "roi stop line":             return self.settings.eeprom.roi_vertical_region_1_end
        if field == "cropped":                   return self.processed_reading.is_cropped()
        if field == "interpolated":              return self.ctl.interp.enabled if self.ctl else False
        if field == "raman intensity corrected": return self.processed_reading.raman_intensity_corrected
        if field == "deconvolved":               return self.processed_reading.deconvolved
        if field == "region":                    return self.settings.state.region
        if field == "slit width":                return self.settings.eeprom.slit_size_um
        if field == "wavenumber correction":     return self.settings.state.wavenumber_correction
        if field == "electrical dark correction":return self.ctl.edc.enabled
        if field == "battery %":                 return self.processed_reading.reading.battery_percentage if self.processed_reading.reading is not None else 0
        if field == "fw version":                return self.settings.microcontroller_firmware_version
        if field == "fpga version":              return self.settings.fpga_firmware_version
        if field == "ble version":               return self.settings.ble_firmware_version
        if field == "laser power %":             return self.processed_reading.reading.laser_power_perc if self.processed_reading.reading is not None else 0
        if field == "device id":                 return str(self.settings.device_id)
        if field == "note":                      return self.note.replace(",", ";")
        if field == "prefix":                    return self.prefix
        if field == "suffix":                    return self.suffix
        if field == "session count":             return self.processed_reading.reading.session_count if self.processed_reading.reading is not None else 0
        if field == "plugin name":               return self.plugin_name
        if field == "preset":                    return self.ctl.presets.selected_preset

        if field == "laser power mw":
            if (self.processed_reading.reading is not None and 
                    self.processed_reading.reading.laser_power_mW is not None and 
                    self.processed_reading.reading.laser_power_mW > 0):
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

    def get_all_metadata(self) -> dict:
        md = {}

        for field in self.get_extra_header_fields():
            md[field] = self.get_metadata(field)

        for field in Measurement.CSV_HEADER_FIELDS:
            if field not in Measurement.ROW_ONLY_FIELDS:
                if field == "Timestamp":
                    md["Timestamp"] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
                else:
                    md[field] = self.get_metadata(field)

        if self.processed_reading.plugin_metadata is not None:
            for k, v in self.processed_reading.plugin_metadata.items():
                md[k] = v

        return md

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
    #
    # @par Horizontal ROI
    #
    # Note that the data output is a little different from 
    # save_csv_file_by_column. This format probably should match that other 
    # format, but right now it doesn't.
    #
    # A key difference is cropped (but not interpolated) ProcessedReadings. 
    # CSV files output every PHYSICAL pixel for most fields (pixel, wavelength, 
    # wavenumber, raw), and only substitute the "NA" for cropped values in 
    # "processed." Instead, this currently just outputs the cropped versions of 
    # everything.
    def save_excel_file(self, resave=False):
        pr          = self.processed_reading

        processed   = pr.get_processed()
        raw         = pr.get_raw()
        dark        = pr.get_dark()
        reference   = pr.get_reference()
        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()

        pixels      = len(wavelengths)
        roi         = self.settings.eeprom.get_horizontal_roi()

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

        # spectra (float() calls because library gets confused by Numpy types)
        first_row = 1
        row_count = 0
        for pixel in range(pixels):
            row = first_row + row_count

            sheet_spectrum.write        (row, 0, pixel + roi.start if roi else pixel)

            if wavelengths is not None and self.ctl.save_options.save_wavelength():
                sheet_spectrum.write    (row, 1, float(wavelengths  [pixel]), style_f2)

            if wavenumbers is not None and self.ctl.save_options.save_wavenumber():
                sheet_spectrum.write    (row, 2, float(wavenumbers  [pixel]), style_f2)

            if processed is not None:
                sheet_spectrum.write    (row, 3, float(processed    [pixel]), style)

            if raw is not None and self.ctl.save_options.save_raw():
                sheet_spectrum.write    (row, 4, float(raw          [pixel]), style)

            if dark is not None and self.ctl.save_options.save_dark():
                sheet_spectrum.write    (row, 5, float(dark         [pixel]), style)

            if reference is not None and self.ctl.save_options.save_reference():
                sheet_spectrum.write    (row, 6, float(reference    [pixel]), style)

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
        md = self.get_all_metadata()

        fields = self.get_extra_header_fields()
        fields.extend(Measurement.CSV_HEADER_FIELDS)
        for field in fields:
            if field == "Timestamp":
                write_pair(field, self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"), style=style_datetime)
            elif field not in Measurement.ROW_ONLY_FIELDS and field in md:
                value = md[field]
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
        if not self.verify_pathname(pathname, resave):
            return

        try:
            wbk.save(pathname)
            log.info("saved %s", pathname)
            self.add_pathname(pathname)
        except Exception:
            log.critical("Problem saving workbook: %s", pathname, exc_info=1)

    def generate_today_dir(self):
        return self.ctl.save_options.generate_today_dir() if (self.ctl and self.ctl.save_options) else "."

    # ##########################################################################
    # JSON
    # ##########################################################################

    ##
    # Express the current Measurement as a single JSON-compatible dict.  Use this
    # for both save_json_file and External.Feature.
    def to_dict(self):
        pr = self.processed_reading

        m = { # Measurement
            "spectrum": {},
            "metadata": self.get_all_metadata(),
            "spectrometerSettings": self.settings.to_dict()
        }

        # interpolation
        if self.ctl.interp.enabled:
            self.ctl.interp.process(pr)
            # note we don't update active_pixels_horizontal, etc
            m["spectrometerSettings"]["wavelengths"] = pr.get_wavelengths()
            m["spectrometerSettings"]["wavenumbers"] = pr.get_wavenumbers()

        # same capitalization as CSV per request
        if self.ctl:
            if self.ctl.save_options.save_processed():
                a = pr.get_processed()
                if a is not None:
                    m["spectrum"]["Processed"] = util.clean_list(a)

            if self.ctl.save_options.save_raw():
                a = pr.get_raw()
                if a is not None:
                    m["spectrum"]["Raw"] = util.clean_list(a)

            if self.ctl.save_options.save_dark():
                a = pr.get_dark()
                if a is not None:
                    m["spectrum"]["Dark"] = util.clean_list(a)

            if self.ctl.save_options.save_reference():
                a = pr.get_reference()
                if a is not None:
                    m["spectrum"]["Reference"] = util.clean_list(a)

        return m

    ##
    # Render the current Measurement to JSON.  Use this for both save_json_file
    # and External.Feature.
    def to_json(self):
        m = self.to_dict()
        s = json.dumps(m, sort_keys=True, indent=2, default=str)
        return util.clean_json(s)

    def save_spc_file(self, use_basename=False, resave=False):
        today_dir = self.generate_today_dir()
        current_x = self.ctl.graph.current_x_axis
        log_text = f"Exported from Wasatch Photonics ENLIGHTEN.\nDevice {self.spec.label}"
        if use_basename:
            pathname = "%s.spc" % self.basename
        else:
            pathname = os.path.join(today_dir, "%s.spc" % self.generate_basename())
        if not self.verify_pathname(pathname, resave):
            return

        if current_x == common.Axes.WAVELENGTHS:
            spc_writer = SPCFileWriter.SPCFileWriter(SPCFileType.TXVALS,
                                      x_units = SPCXType.SPCXNMetr,
                                      y_units = SPCYType.SPCYCount,
                                      experiment_type = SPCTechType.SPCTechRmn,
                                      log_text = log_text,
                                      )
            spc_writer.write_spc_file(pathname,
                                      self.processed_reading.processed,
                                      np.asarray(self.spec.settings.wavelengths),
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
                                      np.asarray(self.spec.settings.wavenumbers),
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
        else:
            log.error(f"current x axis doesn't match vaild values. Aborting SPC save")
            return

        self.add_pathname(pathname)

    ##
    # Save the Measurement in a JSON file for simplified programmatic parsing.
    # in the next column and so on (similar layout as the Excel output).
    #
    # As with save_excel_file(), currently disregarding SaveOptions selections
    # of what x-axis and ProcessedReading fields to include, because there is
    # little benefit to removing them from individual files. We can always add
    # this later if requested.
    def save_json_file(self, use_basename=False, resave=False):
        today_dir = self.generate_today_dir()
        if use_basename:
            pathname = "%s.json" % self.basename
        else:
            pathname = os.path.join(today_dir, "%s.json" % self.generate_basename())
        if not self.verify_pathname(pathname, resave):
            return

        s = self.to_json()
        with open(pathname, "w", encoding='utf-8') as f:
            f.write(s)

        log.info("saved JSON %s", pathname)
        self.add_pathname(pathname)

    def save_dx_file(self, use_basename=False, resave=False):
        if use_basename:
            pathname = self.basename + ".dx"
        else:
            today_dir = self.generate_today_dir()
            pathname = os.path.join(today_dir, self.generate_basename() + ".dx")
        if not self.verify_pathname(pathname, resave):
            return

        data = {
            'title': self.label,
            'cross reference': self.measurement_id,
            'owner': "Wasatch Photonics",
            '$software version': f'ENLIGHTEN {common.VERSION}',
            'end': ''
        }

        if self.settings and self.settings.eeprom:
            data['SPECTROMETER/DATA SYSTEM'] = f"{self.settings.eeprom.serial_number} {self.settings.eeprom.model}"

        current_x = self.ctl.graph.current_x_axis 
        if current_x == common.Axes.WAVELENGTHS:
            data['y']        = np.array(self.processed_reading.processed)
            data['x']        = np.asarray(self.settings.wavelengths)
            data['xunits']   = 'WAVELENGTH (NM)'
            data['yunits']   = 'ARBITRARY UNITS'
            data['data type']= 'INFRARED SPECTRUM'
        elif current_x == common.Axes.WAVENUMBERS:
            data['y']        = np.array(self.processed_reading.processed)
            data['x']        = np.asarray(self.settings.wavenumbers)
            data['xunits']   = "1/CM"
            data['yunits']   = "RAMAN INTENSITY"
            data['data type']= "RAMAN SPECTRUM"
        else:
            common.msgbox("unsupported x-axis for JCAMP-DX")
            return
            
        # not sure these should be required?
        data['maxx'] = np.amax(data['x'])
        data['minx'] = np.amin(data['x'])
        data['maxy'] = np.amax(data['y'])
        data['miny'] = np.amin(data['y'])

        # throw in all our metadata for funz
        for k, v in self.get_all_metadata().items():
            k_ = re.sub(r'[^A-Z0-9_]', '_', k.replace("%", "perc").upper())
            data[f"$enlighten.{k_}"] = v

        jcamp.jcamp_writefile(pathname, data)

        log.info("saved JCAMP-DX %s", pathname)
        self.add_pathname(pathname)

        return pathname

    # ##########################################################################
    # Column-ordered CSV
    # ##########################################################################

    def csv_formatted(self, roi, prec, array, pixel, obey_roi=False):
        """ Used by save_csv_file_by_column and save_csv_file_by_row """
        if array is None:
            return
        if roi and obey_roi:
            if pixel < roi.start or pixel > roi.end:
                return "NA"
            else:
                pixel -= roi.start

        if pixel < 0 or pixel >= len(array):
            return "na"

        value = array[pixel]
        return '%.*f' % (prec, value)

    def get_csv_data(self, pr):
        """ Used by save_csv_file_by_column and save_csv_file_by_row """
        roi = None
        stage = None
        if pr.interpolated:
            # If we're saving interpolated data, we don't care what the ROI was,
            # or how many physical pixels are on the detector. We won't display 
            # "NA" for any values, because interpolation includes extrapolation 
            # at the range ends.
            pass
        else:
            # We're not outputting extrapolated data, so we will output as many
            # rows (pixels) as there are active pixels on the detector. Pixels
            # outside the ROI will receive "NA" for "processed", but should 
            # include wavelength/wavenumber axis values, and might as well include
            # raw, dark and reference.
            if self.ctl.horiz_roi.enabled:
                # We're setting stage to "orig" to indicate we don't want to load
                # the "cropped" component versions -- we want the original full-
                # detector spectrum components. (We'll still use the cropped/final
                # processed spectrum.)
                stage = "orig"
                if self.settings and self.settings.eeprom:
                    roi = self.settings.eeprom.get_horizontal_roi()

        wavelengths = pr.get_wavelengths(stage)
        wavenumbers = pr.get_wavenumbers(stage)
        processed = pr.get_processed() # no stage
        raw = pr.get_raw(stage)
        dark = pr.get_dark(stage)
        reference = pr.get_reference(stage)

        if wavelengths is not None:
            pixels = len(wavelengths)
        elif wavenumbers is not None:
            pixels = len(wavenumbers)
        else:
            pixels = len(processed)

        return roi, wavelengths, wavenumbers, processed, raw, dark, reference, pixels

    ##
    # Save the Measurement in a CSV file with the x-axis in one column, spectra
    # in the next column and so on (similar layout as the Excel output).
    #
    # Note that currently this is NOT writing UTF-8 / Unicode, although KIA-
    # generated labels are Unicode.  (Dieter doesn't seem to like Unicode CSV)
    def save_csv_file_by_column(self, use_basename=False, ext="csv", delim=",", include_header=True, include_metadata=True, resave=False):
        pr = self.processed_reading

        if not self.ctl or not self.ctl.save_options:
            log.error("Measurement.save* requires SaveOptions")
            return

        today_dir = self.generate_today_dir()
        if use_basename:
            pathname = "%s.%s" % (self.basename, ext)
        else:
            pathname = os.path.join(today_dir, "%s.%s" % (self.generate_basename(), ext))

        if not self.verify_pathname(pathname, resave):
            return

        roi, wavelengths, wavenumbers, processed, raw, dark, reference, pixels = self.get_csv_data(pr)

        with open(pathname, "w", newline="", encoding='utf-8') as f:

            out = csv.writer(f, delimiter=delim)

            if include_metadata:
                md = self.get_all_metadata()

                # output additional (name, value) metadata pairs at the top,
                # not included in row-ordered CSV
                outputted = set()
                for field in self.get_extra_header_fields():
                    if field in md:
                        out.writerow([field, md[field]])
                        outputted.add(field)

                # output (name, value) metadata pairs at the top,
                # using the same names and order as our row-ordered CSV
                for field in Measurement.CSV_HEADER_FIELDS:
                    if field not in Measurement.ROW_ONLY_FIELDS and field in md:
                        out.writerow([field, md[field]])
                        outputted.add(field)

                if self.processed_reading.plugin_metadata is not None:
                    for field in self.processed_reading.plugin_metadata.keys():
                        if field not in outputted:
                            out.writerow([field, md[field]])
                            outputted.add(field)

                out.writerow([])

            headers = []
            if self.ctl.save_options.save_pixel():       headers.append("Pixel")
            if self.ctl.save_options.save_wavelength():  headers.append("Wavelength")
            if self.ctl.save_options.save_wavenumber():  headers.append("Wavenumber")
            if self.ctl.save_options.save_processed():   headers.append("Processed")
            if self.ctl.save_options.save_raw():         headers.append("Raw")
            if self.ctl.save_options.save_dark():        headers.append("Dark")
            if self.ctl.save_options.save_reference():   headers.append("Reference")

            if include_header:
                out.writerow(headers)

            # store extra precision for relative measurements
            precision = 5 if pr.reference is not None else 2

            for pixel in range(pixels):
                values = []
                if self.ctl.save_options.save_pixel():       values.append(pixel)
                if self.ctl.save_options.save_wavelength():  values.append(self.csv_formatted(roi, 2,         wavelengths, pixel))
                if self.ctl.save_options.save_wavenumber():  values.append(self.csv_formatted(roi, 2,         wavenumbers, pixel))
                if self.ctl.save_options.save_processed():   values.append(self.csv_formatted(roi, precision, processed,   pixel, obey_roi=True))
                if self.ctl.save_options.save_raw():         values.append(self.csv_formatted(roi, precision, raw,         pixel))
                if self.ctl.save_options.save_dark():        values.append(self.csv_formatted(roi, precision, dark,        pixel))
                if self.ctl.save_options.save_reference():   values.append(self.csv_formatted(roi, precision, reference,   pixel))
                out.writerow(values)

        log.info("saved columnar %s", pathname)
        self.add_pathname(pathname)

    # ##########################################################################
    # TXT
    # ##########################################################################

    ##
    # This is essentially the same as column-ordered CSV, but with no metadata,
    # no header row and no commas. (per proj "Pioneer")
    def save_txt_file(self, use_basename=False, resave=False):
        self.save_csv_file_by_column(use_basename=use_basename, ext="txt", delim=" ", include_header=False, include_metadata=False, resave=resave)

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
    # @todo support .cropped, .interpolated
    # @todo consider how to properly support verify_pathname and resave
    def save_csv_file_by_row(self, resave=False):
        sn = self.settings.eeprom.serial_number

        if self.ctl.save_options.append() and self.ctl.save_options.append_pathname is not None and os.path.exists(self.ctl.save_options.append_pathname):
            # continue appending to the current target
            pathname = self.ctl.save_options.append_pathname
            log.debug("save_csv_file_by_row: re-using append pathname %s", pathname)
            self.appending = True
        else:
            # anytime we save a CSV by-row, it becomes the implicit target for
            # subsequent appendage
            today_dir = self.generate_today_dir()
            pathname = os.path.join(today_dir, "%s.csv" % self.generate_basename())
            log.debug("save_csv_file_by_row: creating pathname %s", pathname)

            self.ctl.save_options.reset_appendage(pathname)

            if os.path.exists(pathname):
                os.remove(pathname)
            self.appending = False
            self.add_pathname(pathname)

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
                reason = "disabled when appending to existing file"
                self.thumbnail_widget.disable_edit(reason=reason)
                self.thumbnail_widget.disable_trash(reason=reason)
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
        except Exception:
            log.critical("Exception writing row-ordered CSV file: %s", pathname, exc_info=1)
            return

        # append
        self.ctl.save_options.line_number += 1
        self.ctl.save_options.set_appended_serial(sn)

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

        if self.ctl.save_options.have_appended_serial(sn):
            return

        if self.ctl.save_options.save_pixel():
            self.write_row(csv_writer, "pixels")
        if self.ctl.save_options.save_wavelength():
            self.write_row(csv_writer, "wavelengths")
        if self.ctl.save_options.save_wavenumber():
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
        if self.ctl.save_options.save_processed():
            self.write_row(csv_writer, "Processed")
        if self.ctl.save_options.save_raw():
            self.write_row(csv_writer, "Raw")
        if self.ctl.save_options.save_dark():
            self.write_row(csv_writer, "Dark")
        if self.ctl.save_options.save_reference():
            self.write_row(csv_writer, "Reference")

    ##
    # @see Scooby-Doo
    def write_row(self, csv_writer, field):
        log.debug(f"write_row: field {field}")
        row = self.build_row(field)
        log.debug(f"write_row: field {field} row {row}")
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
        pr = self.processed_reading

        roi, wavelengths, wavenumbers, processed, raw, dark, reference, pixels = self.get_csv_data(pr)
        prec = 5 if pr.reference is not None else 2

        a = None
        fmt = None
        if field == "pixels":
            a = pr.get_pixel_axis()
            fmt = lambda pixel: pixel
        elif field == "wavelengths":
            a = wavelengths
            fmt = lambda pixel: self.csv_formatted(roi, 2, a, pixel)
        elif field == "wavenumbers":
            a = wavenumbers
            fmt = lambda pixel: self.csv_formatted(roi, 2, a, pixel)
        elif field == "processed":
            a = processed
            fmt = lambda pixel: self.csv_formatted(roi, prec, a, pixel, obey_roi=True)
        elif field == "dark":
            a = dark
            fmt = lambda pixel: self.csv_formatted(roi, prec, a, pixel)
        elif field == "reference":
            a = reference
            fmt = lambda pixel: self.csv_formatted(roi, prec, a, pixel)
        elif field == "raw":
            a = raw
            fmt = lambda pixel: self.csv_formatted(roi, prec, a, pixel)
        else:
            log.error(f"build_row: unknown field {field}")

        if a is None or fmt is None:
            return None

        row = []

        # don't repeat metadata for spectrum components
        prefix_metadata = field not in ["dark", "reference", "raw"]

        # populate the prepended metadata fields per Dash format
        for header in self.CSV_HEADER_FIELDS:
            if header == "Note": # and field != "processed":
                if field == 'processed':
                    note = self.get_metadata(header).strip()
                    row.append(f"{field} ({note})" if note else field)
                else:
                    row.append(field)
            elif prefix_metadata or header in [ "Line Number" ]:
                row.append(self.get_metadata(header))
            else:
                # skip these fields on spectrum components
                # (we don't actually track the integration time, laser status etc for
                # dark and referenced spectra, and for raw it's the same as processed)
                row.append('')

        # append the selected array
        for pixel in range(pixels):
            row.append(fmt(pixel))

        return row

    ## Called (by way of ThumbnailWidget -> KnowItAll.Feature -> Measurements)
    # when KnowItAll has generated a KnowItAll.DeclaredMatch for this Measurement.
    def id_callback(self, declared_match):
        # store the match
        self.declared_match = declared_match

        # re-save files using current SaveOptions (will store new label, overwriting old files with old name)
        # (these will definitely be in TODAY directory, regardless of where they were loaded from)
        self.save(resave=True)

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

        if (self.settings.wavelengths is not None and len(self.settings.wavelengths) and 
             new_settings.wavelengths is not None and len( new_settings.wavelengths)):
           old_x = self.settings.wavelengths
           new_x =  new_settings.wavelengths
        elif (self.settings.wavenumbers is not None and len(self.settings.wavenumbers) and
               new_settings.wavenumbers is not None and len( new_settings.wavenumbers)):
           old_x = self.settings.wavenumbers
           new_x =  new_settings.wavenumbers
        else:
            log.error("no interpolation possible")
            return

        log.debug("interpolating from (%.2f, %.2f) to (%.2f, %.2f)",
            old_x[0], old_x[-1], new_x[0], new_x[-1])

        if pr.raw is not None and len(pr.raw) > 0:
            pr.raw = np.interp(new_x, old_x, pr.raw)

        if pr.dark is not None and len(pr.dark) > 0:
            pr.dark = np.interp(new_x, old_x, pr.dark)

        if pr.reference is not None and len(pr.reference) > 0:
            pr.reference = np.interp(new_x, old_x, pr.reference)

        if pr.processed is not None and len(pr.processed) > 0:
            pr.processed = np.interp(new_x, old_x, pr.processed)

        log.debug("interpolation complete")

    def verify_pathname(self, pathname, resave=False):
        if resave:
            return True
        if not os.path.exists(pathname):
            return True

        if self.ctl.config.has_option("Measurement", "overwrite_existing"):
            return self.ctl.config.get_bool("Measurement", "overwrite_existing")

        result = self.ctl.gui.msgbox_with_checkbox(
            title="Confirm Overwrite",
            text=f"The following pathname already exists. Do you wish to overwrite it?\n{pathname}",
            checkbox_text="Never show again")

        if not result["ok"]:
            return False

        if result["checked"]:
            self.ctl.config.set("Measurement", "overwrite_existing", True)

        return True
