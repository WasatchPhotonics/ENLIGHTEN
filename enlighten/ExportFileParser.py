import datetime
import logging
import csv
import re

from .Measurement      import Measurement

from wasatch.ProcessedReading import ProcessedReading
from wasatch.SpectrometerSettings import SpectrometerSettings

log = logging.getLogger(__name__)

## 
# A temporary pre-Measurement object built-up while reading an export file.
#
# @todo this can probably be generalized and re-used for ColumnFileParser at 
#       least, and likely DashFileParser as well.
# @todo populate temperature and laser temperature
class ExportedMeasurement(object):
    def __init__(self):
        self.headers = []
        self.header_count = 1
        self.metadata = {}
        self.processed_reading = ProcessedReading()
##
# A file parser to deserialize multiple Measurement objects from a column-ordered
# export file.
#
# Given the similarity between the columnar CSV and "export" file formats, it 
# would be SO TEMPTING to imagine you could easily generalize them.  I think
# they're just different enough that it would be a nightmare, so here we are.
# (They are probably more easily mergable now that we're supporting format 1
# exports, which look very like columnar CSV files.)
#
# The way we are currently exporting Measurements, EVERY spectrometer has the
# same prefix fields (px/nm/cm) and EVERY measurement has the same headers
# (pr/raw/dk/ref).  So there is some room for optimization there, but it's 
# almost as easy to just parse them directly (e.g., in case someone deleted 
# columns from the CSV in Excel).
# 
# Note that we completely ignore the pixel/wavelength/wavenumber columns (via 
# skip_fields), instead using the "Pixel Count", "Wavecal Coeff" and "Laser 
# Wavelength" metadata fields to regenerate from scratch.
#
# A unit-test of sorts for this class can be found in 
# enlighten/scripts/split-spectra.py.
#
class ExportFileParser(object):

    def __init__(self, pathname, save_options):
        self.pathname = pathname
        self.save_options = save_options

        self.spectrometers = {}
        self.measurements  = []

        # how many fields to skip at the beginning of each data line read
        # (pixel, wavelength, wavenumber for various spectrometers)
        self.skip_fields = 0 
        self.exported_measurements = []

        self.global_metadata = {} # for format 1

        # Autodetect in process_metadata.
        # 1 = the "old" export format used through ENLIGHTEN 1.4.
        # 2 = the "new" export format added in ENLIGHTEN 1.5.  
        self.format = None 

    def parse(self):
        # read through the input file by line, loading data into local list of
        # ExportedMeasurement objects
        self.load_data()

        # convert ExportedMeasurements to Measurements
        self.generate_measurements()

        return self.measurements

    # ##########################################################################
    # Private methods
    # ##########################################################################

    ##
    # @see ColumnFileParser.post_process_metadata
    def post_process_metadata(self, em):
        if self.format == 1:
            metadata = self.global_metadata
            log.debug("post-processing metadata: %s" % metadata)
        else:
            metadata = em.metadata

        em.settings = SpectrometerSettings()
        eeprom = em.settings.eeprom
        state = em.settings.state

        # timestamp funz
        em.timestamp = None
        try:
            if self.format == 1:
                em.timestamp = datetime.datetime.strptime(metadata["Timestamp"], "%Y-%m-%d %H_%M_%S.%f")
            else:
                em.timestamp = datetime.datetime.strptime(metadata["Timestamp"], "%Y-%m-%d %H:%M:%S.%f") 
        except:
            log.error("unable to parse metadata timestamp: %s", metadata["Timestamp"])
            pass

        try:
            if em.timestamp is None and "Measurement ID" in metadata:
                m = re.match(r"\d{8}-\d{6}-\d{6}", metadata["Measurement ID"])
                if m:
                    em.timestamp = datetime.datetime.strptime(m.group(0), "%Y%m%d-%H%M%S-%f")
                    log.debug("parsed timestamp from Measurement ID")
        except:
            log.error("unable to parse timestamp from Measurement ID: %s", metadata["Measurement ID"])
            pass

        if em.timestamp is None:
            log.error("adding new timestamp")
            em.timestamp = datetime.datetime.now()

        # handle empty strings
        def get_float(key):
            try:
                return float(metadata.get(key, 0))
            except:
                log.debug(f"get_float: can't find {key} in metadata")
                return 0

        def get_int(key):
            try:
                return int(metadata.get(key, 0))
            except:
                log.debug(f"get_int: can't find {key} in metadata")
                return 0

        def get_string(key):
            return metadata.get(key, "")
            

        # TODO: add get_metadata with try-except
        eeprom.wavelength_coeffs        = []
        eeprom.wavelength_coeffs.append(get_float("CCD C0"))
        eeprom.wavelength_coeffs.append(get_float("CCD C1"))
        eeprom.wavelength_coeffs.append(get_float("CCD C2"))
        eeprom.wavelength_coeffs.append(get_float("CCD C3"))
        eeprom.serial_number            = metadata["Serial Number"] if "Serial Number" in metadata else "unknown"
        eeprom.model                    = metadata["Model"] if "Model" in metadata else "unknown"
        eeprom.detector_offset          = get_int("CCD Offset")
        eeprom.detector_gain            = get_float("CCD Gain")
        eeprom.excitation_nm            = get_float("Laser Wavelength")
        eeprom.excitation               = eeprom.excitation_nm
        eeprom.active_pixels_horizontal = get_int("Pixel Count")
        eeprom.roi_horizontal_start     = get_int("ROI Pixel Start")
        eeprom.roi_horizontal_end       = get_int("ROI Pixel End")

        state.integration_time_ms       = get_int("Integration Time")
        state.laser_enabled             = get_string("Laser Enable").lower().strip() == "true"
        state.scans_to_average          = get_int("Scan Averaging") 
        state.boxcar_half_width         = get_int("Boxcar")

        if "Laser Power" in metadata:
            state.laser_power_perc      = get_float("Laser Power")
            state.laser_power_mW        = 0
        else:
            state.laser_power_perc      = get_float("Laser Power %")
            state.laser_power_mW        = get_float("Laser Power mW")

        log.debug("generating wavecal from coeffs: %s" % eeprom.wavelength_coeffs)
        em.settings.update_wavecal()

    def generate_measurements(self):
        log.debug("generate_measurements: %d ExportedMeasurements to convert" % len(self.exported_measurements))
        for em in self.exported_measurements:
            self.post_process_metadata(em)
            em.processed_reading.post_load_cleanup()

            if em.processed_reading.processed is None:
                log.critical("ignoring malformed ExportMeasurement missing processed array")
                continue

            m = Measurement(
                source_pathname   = self.pathname, 
                timestamp         = em.timestamp,
                settings          = em.settings,
                processed_reading = em.processed_reading,
                save_options      = self.save_options)
            if "Label" in em.metadata:
                m.label = em.metadata["Label"]
            self.measurements.append(m)

        # if only a single Measurement was found within the export (rare),
        # the file is renamable
        if len(self.measurements) == 1:
            self.measurements[0].add_renamable(self.pathname)

    ##
    # The first "Metadata" line of the Export file format which contains
    # per-Measurement data is Measurement ID or Serial Number, so use that to 
    # infer sizing and counts of all the Measurements in the file.
    #
    # Specifically, we're going to see how many nulls follow the initial
    # metadata name, as that tells us how many px/nm/cm columns we can skip at 
    # the beginning of each line.
    #
    # Then for each value we find, we're going to count how many nulls follow
    # _it_, which will tell us how many header fields (pr/raw/dk/ref)
    # that Measurement uses.
    #
    # All this information will go into the ExportMeasument object we'll 
    # instantiate for each value we find in this row.
    #
    # \verbatim
    # EnlightenVer
    # MeasID      A        B        C   <==
    # Serial      S1       S1       S2      
    # Label       Aa       Bb       Cc      
    # m1          x        y        z 
    # m2          x        y        z
    #
    # S1    S2    Aa       Bb       Cc
    # px wl px wl pr rw dk pr rw dk pr rw dk 
    # \endverbatim
    #
    def process_first_metadata(self, values):
        field = values.pop(0)   # may be "Measurement ID" or "Serial Number" depending on format
        self.skip_fields = 1    # skip the field we just read

        # where we'll stub the data we're infering as we traverse the line
        em = None

        # iterate over the remaining values
        for value in values:
            if len(value) > 0:
                # we just found a serial number, so instantiate an ExportedMeasurement
                # which we'll populate as we read the remaining lines
                em = ExportedMeasurement()
                em.metadata[field] = value # store the value for this EM
                self.exported_measurements.append(em)
            else:
                if em:
                    em.header_count += 1
                else:
                    # we haven't seen any values yet, so this is just 
                    # another prefix header to skip over (px/nm/cm)
                    self.skip_fields += 1
        log.debug("instantiated %d ExportMeasurements from first line", len(self.exported_measurements))

    ##
    # Read a metadata line from the file (Measurement ID, Integration Time, Note
    # etc), storing values in the appropriate ExportedMeasurement object.
    #
    # \verbatim
    # EnlightenVer
    # MeasID      A        B        C       <==
    # Serial      S1       S1       S2      <== 
    # Label       Aa       Bb       Cc      <==
    # m1          x        y        z       <==
    # m2          x        y        z       <==
    #
    # S1    S2    Aa       Bb       Cc
    # px wl px wl pr rw dk pr rw dk pr rw dk 
    # \endverbatim
    #
    def process_metadata(self, values):
        field = values[0]

        # determine format on first line
        if self.format is None:
            if field.lower() == "wpspeccal version":
                self.format = 3
            elif field.lower() == "enlighten version":
                self.format = 2
            else:
                self.format = 1
            log.debug("parsing export format %d", self.format)
            if self.format > 1:
                return
            
        if self.format == 1:
            # old format only had one metadata block for all measurements
            try:
                value = values[1]
            except:
                value = None
            self.global_metadata[field] = value
            # we can't instantiate ExportedMeasurements yet, because we don't yet know how many there will be
        else:
            # new format has a metadata block for each measurement
            if len(self.exported_measurements) == 0:
                # in format 2, use the first metadata field after "ENLIGHTEN Version"
                # (probably "Measurement ID" or "Serial Number") to instantiate ExportedMeasurements
                self.process_first_metadata(values)
            else:
                values = values[self.skip_fields:] # toss the leading px/nm/cm fields
                for em in self.exported_measurements:
                    if len(values):
                        em.metadata[field] = values[0]  # store this key-value pair
                        values = values[em.header_count:] # toss the nulls expected to follow
    ##
    # Read the "labels" line from the file (Cyclohexane, Container, etc)
    # storing values in the appropriate ExportedMeasurement object.
    #
    # \verbatim
    # EnlightenVer
    # MeasID      A        B        C     
    # Serial      S1       S1       S2       
    # Label       Aa       Bb       Cc      <-- not this
    # m1          x        y        z      
    # m2          x        y        z       
    #
    # S1    S2    Aa       Bb       Cc      <== this
    # px wl px wl pr rw dk pr rw dk pr rw dk 
    # \endverbatim
    #
    # @note The "Label" field is experimentally also being added to Metadata, 
    #       making processing of this line (and perhaps the line itself) 
    #       superfluous.
    def process_labels(self, values):
        field = "Label"
        values = values[self.skip_fields:] # toss the leading px/nm/cm fields
        for em in self.exported_measurements:
            if len(values):
                em.metadata[field] = values[0]  # store this key-value pair
                values = values[em.header_count:] # toss the nulls expected to follow
    ##
    # Read the header row topping the data block, storing each header by position
    # in the appropriate ExportedMeasurement.
    #
    # \verbatim
    # EnlightenVer
    # MeasID      A        B        C       
    # Serial      S1       S1       S2       
    # Label       Aa       Bb       Cc 
    # m1          x        y        z       
    # m2          x        y        z       
    #
    # S1    S2    Aa       Bb       Cc      
    # px wl px wl pr rw dk pr rw dk pr rw dk <== 
    # \endverbatim
    def process_header(self, values):
        if self.format == 1:
            # instantiate ExportedMeasurements from header fields
            self.skip_fields = 0
            exported_measurement = None

            # iterate over values
            for value in values:
                if value.lower() in ["pixel", "wavelength", "wavenumber"]:
                    self.skip_fields += 1
                else:
                    em = ExportedMeasurement()
                    self.exported_measurements.append(em)

                    # assuming format 1 exports only have one column per measurement
                    em.headers.append("Processed") 
                    em.processed_reading.processed = []
                    em.metadata["Label"] = value

            log.debug("instantiated %d ExportMeasurements from header line", len(self.exported_measurements))
        else:
            # in format 2, ExportedMeasurements have already been instantiated by process_first_metadata
            values = values[self.skip_fields:] # toss the leading px/nm/cm fields
            for em in self.exported_measurements:
                for i in range(em.header_count):
                    if len(values):
                        header = values.pop(0)
                        em.headers.append(header)
                        header = header.lower()
                        if   header == "processed": em.processed_reading.processed = []
                        elif header == "raw":       em.processed_reading.raw       = []
                        elif header == "dark":      em.processed_reading.dark      = []
                        elif header == "reference": em.processed_reading.reference = []
                        else:
                            log.error("process_header: unknown header %s", header)

    ##
    # Read a data line from the file, storing values in the appropriate 
    # ExportedMeasurement object.
    #
    # \verbatim
    # EnlightenVer
    # MeasID      A        B        C       
    # Serial      S1       S1       S2       
    # Label       Aa       Bb       Cc 
    # m1          x        y        z      
    # m2          x        y        z     
    #
    # S1    S2    Aa       Bb       Cc       
    # px wl px wl pr rw dk pr rw dk pr rw dk 
    # 0  1  0  2  1  2  1  2  3  2  5  6  1  <==
    # \endverbatim
    #
    def process_data(self, values):
        values = values[self.skip_fields:] # toss the leading px/nm/cm fields
        for em in self.exported_measurements:
            for i in range(em.header_count):
                try:
                    header = em.headers[i].lower()
                except:
                    continue

                if len(values):
                    value = values.pop(0)
                    array = None

                    # skip nulls
                    if len(value) == 0:
                        continue

                    if   header == "processed": array = em.processed_reading.processed
                    elif header == "raw":       array = em.processed_reading.raw      
                    elif header == "dark":      array = em.processed_reading.dark     
                    elif header == "reference": array = em.processed_reading.reference
                    
                    if array is not None:
                        array.append(float(value))

    ##
    # Read in the export file line-by-line, slurping in data for later filing.
    def load_data(self):
        state = "reading_metadata"
        log.debug("loading %s", self.pathname)
        line_count = 0
        with open(self.pathname, "r") as infile:
            for line in infile:
                line = line.strip()
                values = [ x.strip() for x in line.split(",") ]
                field = values[0].lower()

                if line_count < 25:
                    log.debug("load_data: [%s] line = %s", state, line)
                line_count += 1

                if state == "reading_metadata":

                    if len(field) == 0:
                        state = "looking_for_header"

                    else:
                        self.process_metadata(values)
                
                elif state == "looking_for_header":
                    if field == "pixel":
                        self.process_header(values)
                        state = "reading_data"
                    elif self.format > 1 and len(field) > 0:
                        # assume this is the label row
                        self.process_labels(values)
                        # keep looking for the actual header row

                elif state == "reading_data":
                    self.process_data(values)
