import datetime
import logging
import csv

from .Measurement      import Measurement

from wasatch.ProcessedReading import ProcessedReading
from wasatch.SpectrometerSettings import SpectrometerSettings

log = logging.getLogger(__name__)

class DashMeasurement(object):
    """
    Represents data that will go into the next Measurement we generate (or "could",
    for Dash data we don't actually disposition at this time).
    
    The distinction between DashMeasurement and DashSpectrometer is kind of arbitrary,
    (they're all mixed in the Dash metadata prefixes), but helps distinguish 
    "spectrometer" data from "measurement" data.
    
    @todo consider replacing both this and DashSpectrometer with a generalized 
          ExportedMeasurement, containing a generic post_process_metadata() 
          method
    
    @todo instantiate a Reading object and write detector/laser temperature to it
    """
    def __init__(self, row):
        if "Timestamp" in row:
            self.timestamp = datetime.datetime.now()
            ts = row["Timestamp"]
            try:
                if "_" in ts:
                    self.timestamp = datetime.datetime.strptime(row["Timestamp"], "%Y-%m-%d %H_%M_%S.%f")
                else:
                    self.timestamp = datetime.datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            except:
                log.error("unable to parse timestamp: %s", ts, exc_info=1)
                pass

        self.detector_temperature_degC = float(row.get("Temperature", -1))
        self.laser_temperature_degC    = float(row.get("Laser Temperature", -1))

        # these will be populated by update_processed_reading
        self.note = None
        self.processed_reading = None

class DashSpectrometer(object):
    """
    A kind of mini-Spectrometer, holding state about a Spectrometer which will
    go into the next Measurement we generate.  
    
    The distinction between DashMeasurement and DashSpectrometer is kind of arbitrary,
    (they're all mixed in the Dash metadata prefixes), but helps distinguish 
    "spectrometer" data from "measurement" data.
    """

    def __init__(self, row):
        """ @see ColumnFileParser.post_process_metadata """
        self.dash_measurement = DashMeasurement(row)

        self.settings = SpectrometerSettings()
        eeprom = self.settings.eeprom
        state = self.settings.state

        def read_float(field, default=0):
            try:
                return float(row.get(field, default))
            except:
                return default

        # copy fields from Dash CSV fields to their corresponding ENLIGHTEN objects
        eeprom.wavelength_coeffs        = []
        eeprom.wavelength_coeffs.append(read_float("CCD C0"))
        eeprom.wavelength_coeffs.append(read_float("CCD C1", default=1))
        eeprom.wavelength_coeffs.append(read_float("CCD C2"))
        eeprom.wavelength_coeffs.append(read_float("CCD C3"))
        eeprom.serial_number            = row.get("Blank")
        eeprom.detector_offset          = int(read_float("CCD Offset"))
        eeprom.detector_gain            = read_float("CCD Gain")
        eeprom.excitation_nm            = read_float("Laser Wavelength")
        eeprom.excitation               = eeprom.excitation_nm
        eeprom.active_pixels_horizontal = int(read_float("Pixel Count"))
        state.integration_time_ms       = int(read_float("Integration Time"))
        state.laser_enabled             = row.get("Laser Enable", "false").lower().strip() == "true"
        state.laser_power_perc          = read_float("Laser Power") # not sure how to handle this better, but it's a rare case

        self.settings.update_wavecal()

    def update_processed_reading(self, note, spectrum):
        if len(spectrum) != self.settings.pixels():
            log.error("'%s' spectrum had %d elements (expected %d pixels)", note, len(spectrum), self.settings.pixels())
            return

        # treat the first spectrum as 'processed', whatever the note says
        if self.dash_measurement.processed_reading is None:
            self.dash_measurement.note = note
            self.dash_measurement.processed_reading = ProcessedReading()
            self.dash_measurement.processed_reading.processed = spectrum
        elif note.lower() == "raw":
            self.dash_measurement.processed_reading.raw = spectrum
        elif note.lower() == "dark":
            self.dash_measurement.processed_reading.dark = spectrum
        elif note.lower() == "reference":
            self.dash_measurement.processed_reading.reference = spectrum
        else:
            log.error("update_processed_reading has ProcessedReading yet note was '%s'", note)

class DashFileParser(object):
    """
    Load the specified filename into a list of Measurements.
    Expects a historical Dash v2.1 format csv file like the following:
    
    @verbatim
      "Dash Output v2.1","2016-09-30 10:59:55.263000 version: 1036.1","Row","Pixel Data","S-00192"
      "Line Number","Integration Time","Timestamp",              "Blank","Note",   "Temperature","CCD C0","CCD C1","CCD C2",    "CCD C3",    "CCD Offset","CCD Gain","Laser Wavelength","Laser Enable","Laser Power","Laser Temperature","Pixel Count"
      "1",          "100",             "2016-09-30 10:52:42.509","",     "Ethanol",-273.0,       801.591,  0.13999,-3.16859e-06,-1.00352e-08,0,           1.9,       "785.0",           1,             97,           32.56,              1024,        1544,1556,1544...
    @endverbatim
    
    As we step through the rows of the file, we'll need to maintain last-seen
    metadata about each spectrometer.  As we step through the line, we'll 
    generate Measurements from blocks that can be anywhere from individual
    lines (processed) to 7-line blocks:
    
    - pixels        (discard)
    - wavelengths   (discard)
    - wavenumbers   (discard)
    - processed     (note)
    - raw
    - dark
    - reference
    
    Note that technically the expanded pixels, wavelengths and wavenumbers 
    lines are discarded, because the prefixed line metadata contains wavecal
    coeffs, pixel count and excitation wavelength, so lines with a "Note" of
    those values will be discarded.
    
    The all-important "processed" line is assumed to be the FIRST line of a new
    Line Number including prefixed metadata (timestamp etc) which has NOT been 
    discarded (e.g. named pixels/wavelengths/wavenumbers, which seems unlikely).
    
    So we'll maintain state for each spectrometer, generating new Measurements
    from the latest-known spectrometer data each time we encounter a new block.
    
    Technically we never end up re-using old DashSpectrometer objects (we 
    regenerate them from each new 'processed' line), so there's really no need to 
    maintain the self.specs hash...we could just make it self.current_spec.
    
    @par Exploits
    
    If the user has manually assigned a "note" field of "pixels", "wavelengths",
    or "wavenumbers" (unlikely), the given spectrum will not be correctly read.
    (Most likely, the "raw" version will be read and assumed to be "processed",
    which isn't so bad).
    
    I _think_ the algorithm will be fine if the user assigns a note of "raw", 
    "dark", "reference" etc, because the ACTUAL components with those labels
    should be read AFTER the processed row (which can have an arbitrary name,
    including those given).
    """

    def __init__(self, pathname, save_options, encoding="utf-8"):
        self.pathname = pathname
        self.save_options = save_options
        self.encoding = encoding

        # all the DashSpectrometers we've seen in this file
        self.specs = {}
        self.measurements = []

        self.serial = None

    def init_spec(self, row):
        """ Instantiate a new DashSpectrometer from the passed row, and add it to our hash. """
        dash_spec = DashSpectrometer(row)
        serial = dash_spec.settings.eeprom.serial_number

        # Keep the new DashSpectrometer no matter what: could have changed wavecal,
        # gain etc.
        if serial not in self.specs:
            log.debug("storing new DashSpectrometer %s", serial)
        else:
            log.debug("replacing old DashSpectrometer %s", serial)

        self.specs[serial] = dash_spec
        self.serial = serial

    def generate_measurement(self):
        if self.serial is None:
            log.error("generate_measurement: no serial")
            return

        spec = self.specs[self.serial]
        if spec is None:
            log.error("generate_measurement: invalid serial %s", serial)
            return

        log.debug("instantiating new Measurement")
        m = Measurement(
            source_pathname   = self.pathname, 
            timestamp         = spec.dash_measurement.timestamp,
            settings          = spec.settings,
            processed_reading = spec.dash_measurement.processed_reading,
            save_options      = self.save_options)
        self.measurements.append(m)
        m.dump()

        # In normal flow, spec will be recreated immediately after this function 
        # is called, so we don't need to take deepcopies of settings or 
        # processed_reading.  No additional per-spectrometer persistence is 
        # required after a Measurement is generated, because everything important
        # is repeated in the prefixed metadata of each line.  But just to make it
        # perfectly explicit:
        spec.dash_measurement = None
        spec.settings = None
        self.serial = None

    def parse(self):
        log.debug("opening %s", self.pathname)

        # Load the entire file into memory (or maybe it's streaming, who knows).
        # Key thing: the csv_in dictionary will use CSV_HEADER_FIELDS as keys
        # for the prefix metadata fields.  All of the array data (whether pixels,
        # wavelengths or wavenumbers, or processed, raw, dark or reference 
        # spectra) will go into a single array element csv_in['remainder'].
        csv_in = csv.DictReader(open(self.pathname, 'r', encoding=self.encoding), Measurement.CSV_HEADER_FIELDS, 'remainder')

        readcount       =  0 # physical file line 
        last_linenumber = -1 # Line Number

        for row in csv_in:
            
            readcount += 1

            # skip the first two lines
            if readcount == 1:
                value = row['Line Number']
                if not value.lower().startswith("dash output"):
                    raise Exception("first line doesn't look like Dash: %s" % row)
                continue

            elif readcount == 2:
                value = row['Line Number']
                if not value.lower() == "line number":
                    raise Exception("header line doesn't look right: %s" % row)
                continue

            # presumably this is a data line (not one of the two headers anyway)
            else:

                # parse the Line Number
                linenumber = last_linenumber
                if row['Line Number'] is not None and len(row['Line Number'].strip()) > 0:
                    linenumber = int(row['Line Number'])
                if linenumber < 0:
                    log.error("invalid linenumber %d", linenumber)
                    continue

                log.debug("read physical line %d, Line Number %d, note %s", readcount, linenumber, row["Note"])

                # if Line Number changed, dump the last lineset
                if linenumber != last_linenumber:
                    log.debug("line number changed, so generating Measurement")
                    if self.serial is not None:
                        self.generate_measurement()
                    
                    # create a new DashSpectrometer if this is the first time we've
                    # encountered it
                    self.init_spec(row)

                # this is the spectrometer to which the new line pertains
                spec = self.specs[self.serial]

                last_linenumber = linenumber
                    
                # process this line
                note = row["Note"]
                if note in ['pixels', 'wavelengths', 'wavenumbers']:
                    log.debug("load_dash_file: ignoring line %s", note)
                    continue

                # line must be processed/raw/dark/reference
                spectrum = [float(x) for x in row['remainder']]
                spec.update_processed_reading(note, spectrum)

        log.debug("done parsing %s", self.pathname)

        # generate final Measurement from final lineset
        if self.serial is not None:
            self.generate_measurement()

        # IF we only loaded a SINGLE measurement from this file, THEN
        # we can rename the file when the measurement is relabeled
        if len(self.measurements) == 1:
            self.measurements[0].add_renamable(self.pathname)

        log.debug("returning %d Measurements", len(self.measurements))
        return self.measurements
