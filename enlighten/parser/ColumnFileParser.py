import datetime
import logging
import re
import os

from enlighten.measurement.Measurement import Measurement

from wasatch.SpectrometerSettings import SpectrometerSettings
from wasatch.CSVLoader            import CSVLoader

log = logging.getLogger(__name__)

class ColumnFileParser:
    """
    A file parser to deserialize one ENLIGHTEN-format Measurement from a column-
    ordered CSV file.
    
    Given the similarity between the columnar CSV and "export" file formats, it 
    would be SO TEMPTING to imagine you could easily generalize them.  I thought
    they're just different enough that it would be a nightmare, so here we are.
    
    It is expected that this will be able to handle "raw" columnar CSV formats as
    well, which contain no metadata, but instead begin directly with the header
    row.  In that case, wavelength and wavenumber are used directly from the input
    data, as no wavecal coefficients or excitation are available.

    @see TextFileParser for files with no header row at all.
    """
    def __init__(self, ctl, pathname, save_options=None, encoding="utf-8"):

        self.ctl = ctl

        self.pathname = pathname
        self.save_options = save_options
        self.encoding = encoding

        # default
        self.timestamp = datetime.datetime.now()

        self.csv_loader = CSVLoader(pathname, save_options, encoding)

        self.headers = self.csv_loader.headers
        self.metadata = self.csv_loader.metadata
        self.processed_reading = self.csv_loader.processed_reading
        self.processed_reading.reading = self.csv_loader.processed_reading.reading

    def parse(self) -> Measurement:
        # read through the input file by line, loading data locally
        self.csv_loader.load_data(scalar_metadata=True)

        # put loaded data into where it goes in ENLIGHTEN datatypes
        self.post_process_metadata()

        self.processed_reading.wavelengths = self.settings.wavelengths
        self.processed_reading.wavenumbers = self.settings.wavenumbers
        self.processed_reading.post_load_cleanup()

        # generate a Measurement
        m = Measurement(
            self.ctl,
            source_pathname   = self.pathname, 
            timestamp         = self.timestamp,
            settings          = self.settings,
            processed_reading = self.processed_reading)

        if "Label" in self.metadata:
            m.label = self.metadata["Label"]
        else:
            # this was probably for an external script
            m.label = os.path.splitext(os.path.basename(self.pathname))[0]

        # attributes of Measurement itself
        for k in ["Note", "Prefix", "Suffix"]:
            if k in self.metadata:
                setattr(m, k.lower(), self.metadata[k])

        # this parser only loads a single measurement, so the file is renamable
        m.add_renamable(self.pathname)

        return m

    # ##########################################################################
    # Private methods
    # ##########################################################################

    def get_safe_float(self, field):
        if field not in self.metadata or self.metadata[field] is None:
            return 0

        v = self.metadata[field]
        if isinstance(v, list):
            # if multiple strings were loaded for this field, take the first 
            # non-empty one
            value = None
            for tok in v:
                if value is None and len(tok.strip()):
                    value = tok.strip()
            v = '' if value is None else value

        if len(v.strip()) == 0:
            return 0

        try:
            value = float(v)
            log.debug(f"parsed float {field} as {value}")
            return value
        except:
            log.error(f"failed to convert {field} to float: {v}")
            return 0

    def parse_timestamp(self, ts):
        """
        May be any of these:
        
        - 2021-12-31 16:32:14.012888 (saved from ENLIGHTEN)
        - 12/31/2021 16:32:14 
        - 09:14.9 (re-saved from Excel)
        """
        now = datetime.datetime.now()
        if ts is None:
            return now

        parsed = None
        try:
            parsed = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")
            log.debug(f"parsed timestamp {ts} as {parsed}")
            return parsed
        except:
            # log.debug("parse exception", exc_info=1)
            pass

        try:
            parsed = datetime.datetime.strptime(ts, "%d/%m/%y %H:%M:%S")
            log.debug(f"parsed timestamp {ts} as {parsed}")
            return parsed
        except:
            # log.debug("parse exception", exc_info=1)
            pass

        try:
            # why Excel why?
            pat = r'(\d{2}:\d{2})\.(\d+)'
            m = re.match(pat, ts)
            if m:
                hhmm = m.group(1)
                frac = float("0." + m.group(2))

                new_str = f'{now.strftime("%Y-%m-%d")} {hhmm}'
                # log.debug(f"new_str is [{new_str}], frac is {frac}")

                parsed = datetime.datetime.strptime(new_str, "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=frac)
                log.debug(f"parsed timestamp {ts} as {parsed}")
                return parsed
        except:
            # log.debug("parse exception", exc_info=1)
            pass

        log.error(f"unable to convert to datetime: [{ts}]")
        return now

    def post_process_metadata(self):
        """
        This looks VERY SIMILAR to the DashSpectrometer ctor...except for things 
        like Serial Number.  And ExportFileParser.post_process_metadata...
        
        If we passed-in the metadata dict, and returned a tuple (timestamp, 
        SpectrometerSettings) that might work.  But where to put the function?
        
        Note that currently there is nowhere to put SpectrometerApplicationData 
        that we parsed from the file (like view).
        
        In cases where we're looking for different field spellings, those may 
        have been added to better support other application file formats
        (such as RamanSpecCal).

        Defects:
        
        - we're not currently instantiating a SpectrometerApplicationState so have nowhere to store technique_name
        - we're not loading DeviceID (could)
        """
        metadata = self.metadata

        self.settings = SpectrometerSettings()
        eeprom = self.settings.eeprom
        state = self.settings.state
        reading = self.processed_reading.reading

        # timestamp
        try:
            if "Timestamp" in metadata:
                self.timestamp = self.parse_timestamp(metadata["Timestamp"])
            elif "Date" in metadata and "Time" in metadata:
                ts = "%s %s" % (metadata["Date"], metadata["Time"])
                self.timestamp = self.parse_timestamp(ts)
        except:
            log.error("error parsing timestamp", exc_info=1)

        # pixels (currently ignoring Pixel Count and just using what's in the data columns)
        if False and "Pixel Count" in metadata:
            eeprom.active_pixels_horizontal = int(self.get_safe_float("Pixel Count"))
        else:
            eeprom.active_pixels_horizontal = len(self.processed_reading.processed)
        log.debug("active_pixels_horizontal = %d", eeprom.active_pixels_horizontal)

        # fields where name changed in different versions / generators

        # serial number
        for key in ["Serial Number", "Serial"]:
            if key in metadata:
                eeprom.serial_number = metadata[key]
                
        # boxcar
        for key in ["Boxcar", "Boxcar Half-Width"]:
            if key in metadata:
                state.boxcar_half_width = int(self.get_safe_float(key))

        # detector temperature
        for key in ["Temperature", "Detector Temperature Deg C"]:
            if key in metadata:
                reading.detector_temperature_degC = self.get_safe_float(key)

        # integration time (ms)
        for key in ["Integration Time", "Integration Time MS"]:
            if key in metadata:
                state.integration_time_ms = int(self.get_safe_float(key))

        eeprom.model                      = metadata.get("Model")
        eeprom.detector                   = metadata.get("Detector")
        eeprom.detector_offset            = int(self.get_safe_float("CCD Offset"))
        eeprom.detector_gain              = self.get_safe_float("CCD Gain")
        eeprom.excitation_nm_float        = self.get_safe_float("Laser Wavelength")
        eeprom.excitation_nm              = eeprom.excitation_nm
        eeprom.roi_horizontal_start       = int(self.get_safe_float("ROI Pixel Start"))
        eeprom.roi_horizontal_end         = int(self.get_safe_float("ROI Pixel End"))
                                          
        state.laser_enabled               = metadata.get("Laser Enable", "false").lower().strip() == "true"
        state.scans_to_average            = int(self.get_safe_float("Scan Averaging"))

        self.settings.microcontroller_firmware_version = metadata.get("FW Version")
        self.settings.fpga_firmware_version = metadata.get("FPGA Version")

        reading.laser_temperature_degC    = self.get_safe_float("Laser Temperature")

        if "Laser Power" in metadata:
            state.laser_power_perc        = self.get_safe_float("Laser Power")
            state.laser_power_mW          = 0
        else:
            if "Laser Power %" in metadata:
                state.laser_power_perc    = self.get_safe_float("Laser Power %")
            if "Laser Power mW" in metadata:
                state.laser_power_mW      = self.get_safe_float("Laser Power mW")

        ########################################################################
        # wavecal (after laser excitation)
        ########################################################################

        # grab the coeffs if we find them
        coeffs = self.get_wavecal_coeffs_from_metadata()

        # prefer pre-rendered wavelengths, else generate fresh if we can
        if "wavelength" in metadata \
                and len(metadata["wavelength"]) == eeprom.active_pixels_horizontal:
            log.debug("using pre-rendered wavelengths")
            self.settings.wavelengths = metadata["wavelength"] 
            self.settings.lock_wavecal = True
            log.debug("loaded %d wavelengths (%.2f, %.2f) from file", 
                len(self.settings.wavelengths), self.settings.wavelengths[0], self.settings.wavelengths[-1])
            # Generate fresh, but still store coeffs to preserve metadata if export later
            if coeffs is not None:
                eeprom.wavelength_coeffs = coeffs
        elif coeffs is not None:
            eeprom.wavelength_coeffs = coeffs

            # this will also render wavenumbers if possible
            self.settings.update_wavecal()
            log.debug("regenerated %d wavelengths (%.2f, %.2f) from coeffs", 
                len(self.settings.wavelengths), self.settings.wavelengths[0], self.settings.wavelengths[-1])

        # take pre-generated wavenumbers if we weren't able to generate them ourselves
        if self.settings.wavenumbers is None \
                and "wavenumber" in metadata \
                and len(metadata["wavenumber"]) == eeprom.active_pixels_horizontal:
            log.debug("using pre-rendered wavenumbers")
            self.settings.wavenumbers = metadata["wavenumber"] 
            self.settings.lock_wavecal = True
            log.debug("loaded %d wavenumbers (%.2f, %.2f) from file", 
                len(self.settings.wavenumbers), self.settings.wavenumbers[0], self.settings.wavenumbers[-1])

    def get_wavecal_coeffs_from_metadata(self):
        try:
            c0 = self.get_safe_float("CCD C0")
            c1 = self.get_safe_float("CCD C1")
            c2 = self.get_safe_float("CCD C2")
            c3 = self.get_safe_float("CCD C3")
            c4 = self.get_safe_float("CCD C4")
            if c0 > 0:
                return [ c0, c1, c2, c3, c4 ]
        except Exception as e:
            log.debug(f"get_wavecal_coeffs_from_metadata: ignoring {e}")
            return

    def get_header_col(self, field):
        for i in range(len(self.headers)):
            if field == self.headers[i]:
                return i
