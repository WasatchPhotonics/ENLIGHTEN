import datetime
import logging
import json
import csv
import os

import numpy as np

from SPyC_Writer import SPCFileWriter
from SPyC_Writer.SPCEnums import SPCFileType, SPCXType, SPCYType, SPCTechType

from enlighten import util
from enlighten import common
from enlighten.common import msgbox
from enlighten.measurement.Measurement import Measurement

if common.use_pyside2():
    from PySide2 import QtWidgets
else:
    from PySide6 import QtWidgets

log = logging.getLogger(__name__)

##
# This class represents the set of Measurement objects which have been saved
# during this session via the Acquire button or BatchCollection, or which have
# been loaded from disk via the Load button.  It can be considered to be the set
# of ThumbnailWidgets which fill the left-hand capture column in the GUI.
class Measurements:

    MAX_MEASUREMENT_COUNT = 500

    # I see no need to deepcopy this Singleton (and this allows us to deepcopy
    # Measurements freely).
    def __deepcopy__(self, memo):
        log.debug("blocking deep-copy")

    def __init__(self, ctl):

        self.ctl = ctl

        cfu = self.ctl.form.ui

        self.measurements = []

        self.is_collapsed = False
        self.insert_top = True

        # observers
        self.observers = {
            "export": []
        }

        # binding
        cfu.pushButton_erase_captures      .clicked    .connect(self.erase_all_callback)
        cfu.pushButton_export_session      .clicked    .connect(self.export_callback)
        cfu.pushButton_scope_capture_load  .clicked    .connect(self.load_callback)
        cfu.pushButton_resize_captures     .clicked    .connect(self.resize_callback)
        cfu.pushButton_resort_captures     .clicked    .connect(self.resort_callback)

        cfu.pushButton_erase_captures      .setWhatsThis("Erase the current Clipboard, without deleting any files from disk")
        cfu.pushButton_scope_capture_load  .setWhatsThis("Load spectra from disk for display on the graph")
        cfu.pushButton_resize_captures     .setWhatsThis("Expand or collapse the Clipboard thumbnails for simplified viewing")
        cfu.pushButton_resort_captures     .setWhatsThis("Switch the order of Clipboard spectra, changing whether new spectra are added at the top (default) or bottom")
        cfu.pushButton_export_session      .setWhatsThis(util.unwrap("""
            Save all spectra on the Clipboard to a single file. The export file 
            may be CSV, JSON and/or SPC as configured in Save Options. You will 
            be prompted to either export all Clipboard measurements, or just those
            currently displayed on the graph."""))

        # Drop an expanding spacer into the layout, which will force all
        # ThumbnailWidgets to hold a fixed size and align at one end.  (Could
        # this not be done in Designer?)
        spacer = QtWidgets.QSpacerItem(20, 1024, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        cfu.verticalLayout_scope_capture_save.addItem(spacer)

        self.update_count()

    # ##########################################################################
    #                                                                          #
    #                               Callbacks                                  #
    #                                                                          #
    # ##########################################################################

    ## called by KnowItAll.Feature on receiving a MatchResponse from KIA.Wrapper
    # which correponds to a MeasurementID.
    def id_callback(self, measurement_id, declared_match):
        for m in self.measurements:
            if m.measurement_id == measurement_id:
                m.id_callback(declared_match)
                return
        log.error("received DeclaredMatch for missing measurement %s", measurement_id)

    def export_callback(self):
        self.export_session()

    ## display a file selection dialog, let the user select one or more files,
    # then load them up (including thumbnail generation)
    def load_callback(self):
        self.ctl.file_manager.select_files_to_load(callback=self.create_from_file)

    def resize_callback(self):
        log.debug("re-sizing ThumbnailWidgets (collapsed was %s)", self.is_collapsed)
        for measurement in self.measurements:
            thumbnail_widget = measurement.thumbnail_widget
            if thumbnail_widget is not None:
                if self.is_collapsed:
                    thumbnail_widget.expand()
                else:
                    thumbnail_widget.collapse()

        self.is_collapsed = not self.is_collapsed
        self.update_buttons()

    ## Essentially, cfu.verticalLayout_scope_capture_save.reverse()
    def resort_callback(self):
        cfu = self.ctl.form.ui
        log.debug("re-sorting captures (insert_top was %s)", self.insert_top)
        items = []
        while True:
            try:
                item = cfu.verticalLayout_scope_capture_save.takeAt(0)
                if item is None:
                    break
                items.append(item)
            except:
                log.warn("resort: popping layout", exc_info=1)
                break

        for item in items:
            cfu.verticalLayout_scope_capture_save.insertItem(0, item)

        self.insert_top = not self.insert_top
        self.update_buttons()

    def erase_all_callback(self):
        result = msgbox(prompt = "Do you wish to erase all measurements from the Clipboard?", 
                        informative_text="This will not delete any files from disk.",
                        buttons="Yes|No")
        if result.lower() != "yes":
            log.debug("erase_all_callback: user changed their mind")
            return

        log.debug("erase_all_callback: user confirmed erasure")
        self.erase_all()

    # ##########################################################################
    #                                                                          #
    #                                Methods                                   #
    #                                                                          #
    # ##########################################################################

    ##
    # Register the given callback (typically an instance method) if the named
    # event occurs.
    #
    # @param event    (Input) a string (supported values: Measurements.observers.keys())
    # @param callback (Input) a func or method to call if the named event occurs
    def register_observer(self, event, callback):
        if event in self.observers:
            self.observers[event].append(callback)
        else:
            log.error("Measurements has no observable event %s", event)

    ##
    # Enable or disable the Identification button on all Measurement ThumbnailWidgets.
    #
    # @todo fold into observers?
    def update_kia(self):
        for m in self.measurements:
            m.thumbnail_widget.update_kia()

    ##
    # This is the callback which the FileManager will call, one at a time, with
    # delays, with each pathname selected by the user.  Note that a given
    # pathname may contain multiple spectra, which is why
    # MeasurementFactory.create_from_file returns a list of Measurements rather
    # than a single reference.
    def create_from_file(self, pathname):

        # if we're reprocessing loaded measurements, don't bother creating
        # thumbnails on instantiation; we'll do that after re-processing the
        # spectra
        generate_thumbnail = not self.ctl.save_options.load_raw()

        log.debug("create_from_file: calling MeasurementFactory.create_from_file with %s", pathname)
        measurements = self.ctl.measurement_factory.create_from_file(
            pathname = pathname,
            is_collapsed = self.is_collapsed,
            generate_thumbnail = generate_thumbnail)

        if measurements is None:
            log.debug("create_from_file: no Measurements parsed from %s", pathname)
            return

        for m in measurements:
            log.debug("create_from_file: completing new measurement")

            # reprocess if requested
            if self.ctl.save_options.load_raw():

                log.debug("reprocessing measurement %s", m.measurement_id)

                # TODO: can this method be moved into Measurements class?
                new_pr = self.ctl.reprocess(m)

                if new_pr is None:
                    log.error("failed to reprocess %s", m.measurement_id)
                    return

                log.debug("updating ProcessedReading in %s", m.measurement_id)
                m.replace_processed_reading(new_pr)

                log.debug("generating thumbnail for updated %s", m.measurement_id)
                self.ctl.measurement_factory.create_thumbnail(m)

                log.debug("resaving %s", m.measurement_id)
                m.save()

            self.add(m)

    def rename_last_measurement(self):
        if self.measurements:
            self.measurements[-1].thumbnail_widget.rename_callback()

    ##
    # Use the MeasurementFactory to instantiate a new Measurement, including
    # ThumbnailWidget, from the given spectrometer's latest ProcessedReading.
    def create_from_spectrometer(self, spec, label=None):
        if spec is None or spec.app_state.processed_reading is None:
            msgbox("No spectra to save.", "Error")
            return

        log.debug("creating Measurement from spec %s", spec.label)

        # create a Measurement from this Spectrometer's last ProcessedReading,
        # using the current "collapsed" state
        measurement = self.ctl.measurement_factory.create_from_spectrometer(
            spec = spec,
            is_collapsed = self.is_collapsed,
            label = label)

        self.add(measurement)

    ##
    # Add the new measurement to our on-screen list.  Kick-off old measurement
    # if necessary.
    def add(self, measurement):
        cfu = self.ctl.form.ui
        if measurement.thumbnail_widget is None:
            log.error("unable to add Measurement w/o ThumbnailWidget")
            return

        # enforce resource limits
        while self.count() >= Measurements.MAX_MEASUREMENT_COUNT:
            log.debug("enforcing resource limits")
            self.delete_oldest()

        # add to layout
        log.debug("adding ThumbnailWidget to layout")
        if self.insert_top:
            cfu.verticalLayout_scope_capture_save.insertWidget( 0, measurement.thumbnail_widget)
        else:
            cfu.verticalLayout_scope_capture_save.insertWidget(-1, measurement.thumbnail_widget)

        self.measurements.append(measurement)
        self.update_count()

    def count(self):
        return len(self.measurements)

    def get(self, measurement_id):
        for m in self.measurements:
            if m.measurement_id == measurement_id:
                return m

    def erase_all(self):
        """ Clears the list of Measurements (does not delete from disk). """
        log.debug("erasing all Measurements")
        while self.count():
            self.delete_oldest()
        log.debug("done erasing")

    ## Delete the oldest Measurement (Thumbnail layout can be inverted, not
    #  array order).
    def delete_oldest(self):
        if self.count():
            measurement = self.measurements[0]
            log.debug("delete_oldest: deleting %s", measurement.measurement_id)
            self.delete_measurement(measurement)

    ##
    # The user has clicked the "trash" icon on a ThumbnailWidget, or the "eraser"
    # icon at the top of the capture layout, or we're doing a massive collection
    # and the ringbuffer overflowed, so the Measurement is being destroyed.
    #
    # It DOES NOT delete anything from disk.
    #
    # Measurements can only be deleted from disk by clicking on their individual
    # Trash icons, which logic is entirely encapsulated within Measurement and
    # ThumbnailWidget.  
    #
    # @see https://stackoverflow.com/a/20167458 re: deleteLater()
    def delete_measurement(self, measurement):
        if measurement is None or measurement not in self.measurements:
            return

        log.debug("delete_measurement: %s", measurement.measurement_id)
        measurement.delete()
        measurement.clear()
        self.measurements.remove(measurement)
        self.update_count()

    ##
    # Update the "X spectra" label on the GUI, and dis/enable buttons
    def update_count(self):
        cfu = self.ctl.form.ui

        # update the text counter
        count = self.count()
        cfu.label_session_count.setText(util.pluralize_spectra(count))

        # update buttons
        enabled = count > 0
        for b in [ cfu.pushButton_erase_captures,
                   cfu.pushButton_export_session,
                   cfu.pushButton_resize_captures,
                   cfu.pushButton_resort_captures ]:
            b.setEnabled(enabled)

    # Think this is internal-only
    def update_buttons(self):
        self.ctl.gui.colorize_button(self.ctl.form.ui.pushButton_resize_captures,     self.is_collapsed)
        self.ctl.gui.colorize_button(self.ctl.form.ui.pushButton_resort_captures, not self.insert_top)

    # ##########################################################################
    #                                                                          #
    #                              Session Export                              #
    #                                                                          #
    # ##########################################################################

    ##
    # The user clicked the "Export" button at the bottom of the Thumbnail layout
    # and wants to export every current Measurement into a single CSV (either
    # row- or column-ordered, per SaveOptions).  (Can also be triggered at end
    # of BatchCollection batch, or perhaps from a future plugin.)
    #
    # @param filename: BatchCollection generates one so we needn't prompt user
    # @param prompt: prompt for verification (False for unattended operation)
    def export_session(self, filename=None, prompt=True):

        if not self.count():
            log.warn("no measurements to export")
            return

        ########################################################################
        # Generate pathname
        ########################################################################

        visible_only = False
        if filename is None:
            now = datetime.datetime.now()

            default_filename = f"{self.ctl.save_options.prefix()}-" if self.ctl.save_options.has_prefix() else "Session-"
            default_filename += now.strftime("%Y%m%d-%H%M%S")
            default_filename += f"-{self.ctl.save_options.suffix()}" if self.ctl.save_options.has_suffix() else ""

            default_filename = self.measurements[-1].expand_template(default_filename)

            if not prompt:
                filename = default_filename
            else:
                # prompt the user to override the default filename
                result = self.ctl.gui.msgbox_with_lineedit_and_checkbox(
                    title = "Export",
                    label_text = "Enter export filename",
                    lineedit_text = default_filename,
                    checkbox_text = "Only export displayed traces")
                log.debug(f"msgbox result: {result}")
                filename = result["lineedit"]
                visible_only = result["checked"]
                if not (result["ok"] and filename):
                    log.info("cancelling export")
                    return

        # currently, all Sessions are stored in ~/EnlightenSpectra
        directory = common.get_default_data_dir()

        # warn user if they are about to overwrite an existing file
        # it looks like only risk is for .csv and .json extensions
        file_exists = (os.path.exists(os.path.join(directory, f'{filename}.csv'))
                       or os.path.exists(os.path.join(directory, f'{filename}.json'))
                       or os.path.exists(os.path.join(directory, f'{filename}.spc')))

        log.info(f"checking for: {os.path.join(directory, filename)}, file exists={file_exists}")

        if file_exists:
            should_overwrite = msgbox(prompt=f"Do you wish to overwrite the existing file: {filename}?",
                                      informative_text="All data in the previous file will be lost.",
                                      buttons="Yes|No") == "Yes"
        else:
            should_overwrite = False

        if not file_exists or should_overwrite:
            # doesn't use the dict
            if self.ctl.save_options.save_csv():
                self.export_session_csv(directory, filename, visible_only=visible_only)

            # cache export dictionary so we can re-use it between JSON and ExternalAPI
            if self.ctl.save_options.save_json() or len(self.observers["export"]) > 0:
                export = self.generate_export_dict(visible_only=visible_only)

            if self.ctl.save_options.save_json():
                self.export_session_json(directory, filename, export)

            if self.ctl.save_options.save_spc():
                self.export_session_spc(directory, filename, visible_only=visible_only)

        for callback in self.observers["export"]:
            callback(export, visible_only)

    def read_measurements(self):
        return self.generate_export_dict()

    def generate_export_dict(self, visible_only=False) -> list[dict]:
        if visible_only:
            export = [ m.to_dict() for m in self.measurements if m.is_displayed() ]
        else:
            export = [ m.to_dict() for m in self.measurements ]
        return export

    def export_session_spc(self, directory, filename, visible_only=False):
        if not filename.endswith(".spc"):
            filename += ".spc"
        pathname = os.path.join(directory, filename)

        devices = []
        xs = []
        ys = []
        x_units = SPCXType.SPCXArb
        y_units = SPCYType.SPCYArb
        experiment_type = SPCTechType.SPCTechRmn
        current_x = self.ctl.graph.current_x_axis
        file_type = SPCFileType.TMULTI | SPCFileType.TXVALS | SPCFileType.TXYXYS | SPCFileType.TCGRAM

        if visible_only:
            export_measurements = [ m for m in self.measurements if m.is_displayed() ]
        else:
            export_measurements = self.measurements

        for m in export_measurements:
            devices.append(m.spec.label)
            if current_x == common.Axes.WAVELENGTHS:
                x_units = SPCXType.SPCXNMetr
                y_units = SPCYType.SPCYCount
                xs.append(m.spec.settings.wavelengths)
            elif current_x == common.Axes.WAVENUMBERS:
                x_units = SPCXType.SPCXCM
                y_units = SPCYType.SPCYCount
                xs.append(m.spec.settings.wavelengths)
            elif current_x == common.Axes.PIXELS:
                y_units = SPCYType.SPCYCount
                xs.append(list(range(m.spec.settings.eeprom.active_pixels_horizontal)))
            else:
                log.error(f"current x axis {current_x} doesn't match any valid values, returning without export")
                return False
            ys.append(m.processed_reading.processed)
        devices = list(set(devices)) # remove duplicates
        log_label = f"Exported from Wasatch Photonics ENLIGHTEN. Measurement devices were {' '.join(devices)}"
        np_xs = np.asarray(xs)
        np_ys = np.asarray(ys)

        writer = SPCFileWriter.SPCFileWriter(file_type = file_type,
                                             experiment_type = experiment_type,
                                             x_units = x_units,
                                             y_units = y_units,
                                             log_text = log_label)
        try:
            writer.write_spc_file(pathname, y_values = np_ys, x_values = np_xs)
            return True
        except Exception as e:
            log.error(f"failed to write session to spc file due to error {e}. Returning without exporting.")
            return False

    ##
    # Should this generate a JSON dict of Measurements (keyed on MeasurementID)
    # or a JSON list of Measurements?  Could argue either way, but I'm defaulting
    # to list as it's slightly simpler for sender and receiver both.
    def export_session_json(self, directory, filename, export):
        if not filename.endswith(".json"):
            filename += ".json"
        pathname = os.path.join(directory, filename)

        s = json.dumps(export, sort_keys=True, indent=2)
        with open(pathname, "w") as f:
            f.write(util.clean_json(s))

    def export_session_csv(self, directory, filename, visible_only=False):
        if not filename.endswith(".csv"):
            filename += ".csv"
        pathname = os.path.join(directory, filename)

        order = "row" if self.ctl.save_options.save_by_row() else "column"

        if visible_only:
            export_measurements = [ m for m in self.measurements if m.is_displayed() ]
        else:
            export_measurements = self.measurements

        log.info("exporting %d measurements in %s order to %s", len(export_measurements), order, pathname)

        ########################################################################
        # Generate the export
        ########################################################################

        try:
            with open(pathname, "w", newline="") as f:
                csv_writer = csv.writer(f)
                if order == "row":
                    self.export_by_row(csv_writer, visible_only)
                else:
                    self.export_by_column(csv_writer, visible_only)

            self.ctl.marquee.info("exported %d spectra" % len(export_measurements))
            log.info("exported %d measurements in %s order to %s", self.count(), order, pathname)

        except Exception:
            log.critical("exception exporting session", exc_info=1)
            os.remove(pathname)

    def _get_spectrometer_settings(self, visible_only=False):
        """
        Returns a list of all SpectrometerSettings (unique by serial_number)
        contributing to our current set of saved measurements, in order of initial
        appearance.

        To be perfectly clear, this returns a dictionary of
        wasatch.SpectrometerSettings by serial number.  Be aware that different
        Measurement objects generated from the same spectrometer serial number
        may have different ROI and interpolation settings.

        @note This method has a fundamental weakness if something, say a plugin,
              changes the SpectrometerSettings (say wavelengths/wavenumbers) for
              some measurements OF THE SAME SERIAL NUMBER. We are fundamentally
              assuming that SpectrometerSettings (and x-axis) does not change
              FOR A GIVEN SERIAL NUMBER across the course of the export. What we
              really should do is track "unique x-axes" across all Measurements,
              regardless of serial number.
        """
        settingss = []
        seen_sn = set()
        for m in self.measurements:
            if visible_only and not m.is_displayed():
                continue
            if m.settings is not None and m.settings.eeprom.serial_number not in seen_sn:
                settingss.append(m.settings)
                seen_sn.add(m.settings.eeprom.serial_number)

        return settingss

    def incompatible_axes(self, export_measurements):
        specs = {}

        # group by serial
        for m in export_measurements:
            sn = "default"
            if m.settings and m.settings.eeprom:
                sn = m.settings.eeprom.serial_number
            if sn not in specs:
                specs[sn] = []
            specs[sn].append(m)

        # check each serial
        for sn in specs:
            if len(specs[sn]) < 2:
                continue
            first_pr = specs[sn][0].processed_reading
            first_wl = first_pr.get_wavelengths()
            for i in range(1, len(specs[sn])):
                this_pr = specs[sn][i].processed_reading
                this_wl = this_pr.get_wavelengths()
                # log.debug(f"incompatible_axes: first_wl {first_wl}")
                # log.debug(f"incompatible_axes:  this_wl {this_wl}")
                # first_pr.dump()
                # this_pr.dump()
                if len(first_wl) != len(this_wl):
                    log.debug(f"incompatible_axes: bad: {sn} measurements 0 and {i} had different wavelength axis lengths ({len(first_wl)} != {len(this_wl)})")
                    return True

                # MZ: I tried 'first_wl != this_wl' but it raised...?
                for a, b in zip(first_wl, this_wl):
                    if a != b:
                        log.debug(f"incompatible_axes: bad: {sn} measurements 0 and {i} had different wavelength axes ({a} != {b})")
                        return True
                        
                log.debug(f"incompatible_axes: good: {sn} measurements 0 and {i} had identical wavelengths ({first_wl[0]:.2f}, {first_wl[-1]:0.2f}) ({this_wl[0]:.2f}, {this_wl[-1]:0.2f})")
        return False

    ##
    # Export each Measurement in turn in a columnar CSV.
    #
    # You might wonder if it's worth re-exporting every CSV_HEADER_FIELD atop
    # each colujmn of spectra, given that so many of the values (wavecal coeffs,
    # etc) don't change.  The thing is, some do (integration time, note,
    # detector and laser temperature, laser power, laser enabled etc).  So bite
    # the bullet and export them all for consistency.
    #
    # If we're going to export data for 3 Measurements (A, B, C) taken from 2
    # spectrometers (S1 -> A, B; S2 -> C), and we're showing x-axis fields
    # (px, wl) and ProcessedReading fields (proc, raw, dark), then we'd output
    # this (m# indicating various metadata fields).
    #
    # \verbatim
    # Enlighten ver
    # MeasID      A        B        C           <-- Measurement.measurement_id
    # Serial      S1       S1       S2
    # Label       Aa       Bb       Cc          <-- so good it's printed twice
    # m1          x        y        z
    # m2          x        y        z
    #
    # S1    S2    Aa       Bb       Cc          <-- Measurement.label
    # px wl px wl pr rw dk pr rw dk pr rw dk
    # \endverbatim
    #
    # @note If I'd known about Pandas when I wrote this, I might have done it
    #       differently :-/
    #
    # @par Collated
    #
    # By default, exports are "collated" (grouped by MEASUREMENT).
    #
    # If NOT SaveOptions.save_collated(), then the columns are grouped by each
    # "subspectrum" (processed, raw, dark, reference etc). This changes the basic
    # layout above to:
    #
    # \verbatim
    # Enlighten ver
    # MeasID         A  B  C     A  B  C     A  B  C    <-- metadata repeated for each subspectrum
    # Serial         S1 S1 S2    S1 S1 S2    S1 S1 S2
    # Label          Aa Bb Cc    Aa Bb Cc    Aa Bb Cc
    # m1             x  y  z     x  y  z     x  y  z
    # m2             x  y  z     x  y  z     x  y  z
    #
    # S1    S2    Pr          Rw          Dk            <-- a "blank column" is inserted between each grouping, with the label of that subspectrum
    # px wl px wl    Aa Bb Cc    Aa Bb Cc    Aa Bb Cc   <-- the Measurement.label is used as the header within each grouping
    # \endverbatim
    #
    # @par Known Issues
    #
    # There is a fundamental weakness here that we are assuming:
    #
    # (1) SpectrometerSettings will not change for a given serial number over the
    #     course of the measurements, and 
    # (2) individual Measurement's ProcessedReading get_wavelengths() etc 
    #     actually reflect the current SpectrometerSettings (and weren't trumped
    #     along the line by a plugin or whatever).
    def export_by_column(self, csv_writer, visible_only=False):

        # could output some "Session" stuff up here

        ########################################################################
        # components
        ########################################################################

        # count spectrometers (S1, S2)
        settingss = self._get_spectrometer_settings(visible_only)

        # count x-axis headers (px, wl)
        x_headers = []
        if self.ctl.save_options.save_pixel():
            x_headers.append("Pixel")
        if self.ctl.save_options.save_wavelength():
            x_headers.append("Wavelength")
        if self.ctl.save_options.save_wavenumber():
            x_headers.append("Wavenumber")

        # count ProcessedReading subspectra headers (pr, rw, dk)
        pr_headers = []
        if self.ctl.save_options.save_processed():
            pr_headers.append("Processed")
        if self.ctl.save_options.save_raw():
            pr_headers.append("Raw")
        if self.ctl.save_options.save_dark():
            pr_headers.append("Dark")
        if self.ctl.save_options.save_reference():
            pr_headers.append("Reference")

        # @todo: it would be cool if plugins could add their own subspectra
        #        (new columns in the saved files)

        BLANK = ['']

        # default to 5-digit precision for all spectral columns if a reference
        # component is being exported
        prec = 5 if 'Reference' in pr_headers else 2
        max_pixels = max([settings.pixels() for settings in settingss])

        ########################################################################
        # metadata
        ########################################################################

        # EnlightenVer                      <==
        # MeasID      A        B        C   <==
        # Serial      S1       S1       S2  <==
        # Label       Aa       Bb       Cc  <==
        # m1          x        y        z   <==
        # m2          x        y        z   <==
        #
        # S1    S2    Aa       Bb       Cc
        # px wl px wl pr rw dk pr rw dk pr rw dk

        fields = self.measurements[0].get_extra_header_fields()
        fields.extend(Measurement.CSV_HEADER_FIELDS)

        if visible_only:
            export_measurements = [ m for m in self.measurements if m.is_displayed() ]
        else:
            export_measurements = self.measurements

        if not self.ctl.interp.enabled and self.incompatible_axes(export_measurements):
            msg = "The selected measurements include differing ROI and/or " \
                + "interpolation settings for the same spectrometer. Please " \
                + "enable interpolation to export these measurements as a group."
            common.msgbox(msg)
            raise ValueError(msg)

        # roll-in any plugin metadata appearing in any measurement
        for m in export_measurements:
            m.processed_reading.dump()
            if m.processed_reading.plugin_metadata is not None:
                for k in sorted(m.processed_reading.plugin_metadata.keys()):
                    if k not in fields:
                        fields.append(k)

        # actually output the metadata to the CSV
        for field in fields:
            if field in Measurement.ROW_ONLY_FIELDS:
                continue
            elif field.lower() == "enlighten version":
                # MZ: note version is always in 2nd column
                csv_writer.writerow(['ENLIGHTEN Version', common.VERSION])
            else:

                # first start with the metadata field name
                row = [ field ]

                # now insert blanks to skip past the x-axes to the first measurement
                row.extend(BLANK * (len(settingss) * len(x_headers) - 1))

                # now output the metadata atop the data columns
                if not self.ctl.save_options.save_collated():
                    for header in pr_headers:
                        row.extend(BLANK) # for the subspectrum name
                        # now re-write the value above every measurement for this subspectrum
                        for m in export_measurements:
                            value = m.get_metadata(field)
                            row.append(value)
                else:
                    for m in export_measurements:
                        value = m.get_metadata(field)
                        row.append(value)
                        row.extend(BLANK * (len(pr_headers) - 1))
                csv_writer.writerow(row)

        csv_writer.writerow([])

        ########################################################################
        # Header One
        ########################################################################

        # EnlightenVer
        # MeasID      A        B        C
        # Serial      S1       S1       S2
        # Label       Aa       Bb       Cc
        # m1          x        y        z
        # m2          x        y        z
        #
        # S1    S2    Aa       Bb       Cc <=== (serial, label)
        # px wl px wl pr rw dk pr rw dk pr rw dk
        row = []
        for settings in settingss:
            # It's important that we use the serial_number (not spec.label) here,
            # so that parsers who read the list of serial_numbers from the
            # metadata line will be able to associate the prefix headers with
            # serial numbers.  That said, ExportFileParser IGNORES the prefix
            # columns (px/nm/cm can be regenerated), so we're just being nice to
            # other consumers.
            row.append(settings.eeprom.serial_number)
            row.extend(BLANK * (len(x_headers) - 1))
        if not self.ctl.save_options.save_collated():
            for header in pr_headers:
                row.append(header)
                row.extend(BLANK * len(export_measurements))
        else:
            for m in export_measurements:
                row.append(m.label)
                row.extend(BLANK * (len(pr_headers) - 1))
        csv_writer.writerow(row)

        ########################################################################
        # Header Two
        ########################################################################

        # EnlightenVer
        # MeasID      A        B        C
        # Serial      S1       S1       S2
        # Label       Aa       Bb       Cc
        # m1          x        y        z
        # m2          x        y        z
        #
        # S1    S2    Aa       Bb       Cc
        # px wl px wl pr rw dk pr rw dk pr rw dk <===

        row = []
        for settings in settingss:
            for header in x_headers:
                row.append(header)
        if not self.ctl.save_options.save_collated():
            for header in pr_headers:
                row.extend(BLANK)
                for m in export_measurements:
                    row.append(m.label)
        else:
            for m in export_measurements:
                for header in pr_headers:
                    row.append(header)
        csv_writer.writerow(row)

        ########################################################################
        # Spectral Data
        ########################################################################

        # after this point, all headers can be lowercase
        x_headers  = [ s.lower() for s in  x_headers ]
        pr_headers = [ s.lower() for s in pr_headers ]

        def get_x_header_value(wavelengths, wavenumbers, header, pixel):
            result = ""
            if header == "pixel":
                result = str(pixel)
            elif header == "wavelength":
                if wavelengths is not None and pixel < len(wavelengths):
                    result = f"{wavelengths[pixel]:.2f}"
            elif header == "wavenumber":
                if wavenumbers is not None and pixel < len(wavenumbers):
                    result = f"{wavenumbers[pixel]:.2f}"
            # log.debug(f"get_x_header_value: header {header}, pixel {pixel}, result {result}")
            return result

        def get_pr_header_value(m, header, pixel, pr=None):
            if pr is None:
                pr = m.processed_reading
            if pr is None:
                return None

            a = None
            if header == "processed":
                a = pr.get_processed()
            elif header == "reference":
                a = pr.get_reference()
            elif header == "dark":
                a = pr.get_dark()
            elif header == "raw":
                a = pr.get_raw()        

            if a is None:
                return "NA"

            if pr.is_interpolated():
                # for interpolated, just output what we have
                if pixel < len(a):
                    value = a[pixel]
                else:
                    return "NA"
            else:
                # for non-interpolated, allow processed to be cropped, but full data for other components
                if header == "processed":
                    roi = m.settings.eeprom.get_horizontal_roi()
                    if roi and pr.is_cropped():
                        if roi.start <= pixel and pixel <= roi.end:
                            value = a[pixel - roi.start]
                        else:
                            return "NA"
                    else:
                        if pixel < len(a):
                            value = a[pixel]
                        else:
                            return "NA"
                else:
                    if pixel < len(a):
                        value = a[pixel]
                    else:
                        return "NA"

            # Override default precision (which was based on whether a "reference" column
            # is being exported) with this indication of whether a reference component was
            # used in the measurement.
            use_prec = prec
            if pr.reference is not None:
                use_prec = 5

            return '%.*f' % (use_prec, value)

        if self.ctl.interp.enabled:

            log.debug(f"export_by_column: interpolation enabled")

            #####################################################################
            # Export Interpolated
            #####################################################################

            # Generate TEMPORARY interpolation of each Measurement (don't change
            # clipboard object). Keep handle to "first" Measurement, for use in
            # exporting the x-axis.
            first = None
            interpolated = {}
            for m in export_measurements:
                interpolated[m] = self.ctl.interp.process(m.processed_reading, save=False)
                if first is None:
                    first = interpolated[m]

            for pixel in range(self.ctl.interp.total_pixels()):
                row = []
                for settings in settingss:
                    for header in x_headers:
                        row.append(get_x_header_value(first.get_wavelengths(), first.get_wavenumbers(), header, pixel))
                if not self.ctl.save_options.save_collated():
                    for header in pr_headers:
                        row.extend(BLANK)
                        for m in export_measurements:
                            row.append(get_pr_header_value(m, header, pixel, pr=interpolated[m]))
                else:
                    for m in export_measurements:
                        for header in pr_headers:
                            row.append(get_pr_header_value(m, header, pixel, pr=interpolated[m]))
                csv_writer.writerow(row)

        else:

            #####################################################################
            # Export Non-Interpolated
            #####################################################################

            # Note that if some of these measurements were interpolated WHEN THEY
            # WERE COLLECTED, they will be exported interpolated, even if
            # interpolation was subsequently disabled before the export. We
            # could change this by adding a "no_interpolation=False" default
            # param to ProcessedReading.get_foo() methods, but I don't currently
            # see it as a problem.

            log.debug(f"export_by_column: interpolation not enabled")

            for pixel in range(max_pixels):

                row = []
                for settings in settingss:
                    if pixel < settings.pixels():
                        for header in x_headers:
                            row.append(get_x_header_value(settings.wavelengths, settings.wavenumbers, header, pixel))
                    else:
                        row.extend(BLANK * len(x_headers))

                if not self.ctl.save_options.save_collated():
                    for header in pr_headers:
                        row.extend(BLANK)
                        for m in export_measurements:
                            if pixel < m.settings.pixels():
                                row.append(get_pr_header_value(m, header, pixel))
                            else:
                                row.extend("NA")
                else:
                    for m in export_measurements:
                        if pixel < m.settings.pixels():
                            for header in pr_headers:
                                row.append(get_pr_header_value(m, header, pixel))
                        else:
                            row.extend(BLANK * len(pr_headers))
                csv_writer.writerow(row)

    ##
    # In the row-based export, try to follow historical Dash conventions, as
    # there's no obvious justification not to.
    #
    # Note that the Dash format didn't fully anticipate multiple spectrometers,
    # so typically only listed one serial number on the file header.  Just list
    # them all.
    #
    # A naive implementation of this would just be to re-save the first
    # Measurement as csv_by_row, then forcibly append all the others atop it.
    # However, that would go into the wrong directory, with the wrong filename.
    # This is short enough that it doesn't matter.
    #
    # It is believed that this exported file will match what you would have
    # generated if you had initially saved the first Measurement as a row-ordered
    # CSV, then appended subsequent Measurements.
    def export_by_row(self, csv_writer, visible_only=False):
        settingss = self._get_spectrometer_settings(visible_only)

        file_header = Measurement.generate_dash_file_header(
            [settings.eeprom.serial_number for settings in settingss])

        csv_writer.writerow(file_header)
        csv_writer.writerow(Measurement.CSV_HEADER_FIELDS)

        # cache a copy of the current line number, in case we later want to
        # continue appending to the current open row-ordered file -- this
        # is currently stored as an instance attribute in the SaveOptions
        # singleton, meaning it will get trampled in the row-ordered export.
        save_line_number = self.ctl.save_options.line_number
        self.ctl.save_options.line_number = 0

        if visible_only:
            export_measurements = [ m for m in self.measurements if m.is_displayed() ]
        else:
            export_measurements = self.measurements

        for m in export_measurements:
            if visible_only and not m.is_displayed():
                continue
            m.write_x_axis_lines(csv_writer)
            m.write_processed_reading_lines(csv_writer)
            self.ctl.save_options.line_number += 1

        # restore the saved line number
        self.ctl.save_options.line_number = save_line_number
