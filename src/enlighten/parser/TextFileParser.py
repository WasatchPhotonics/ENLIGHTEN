import datetime
import logging

from enlighten.measurement.Measurement import Measurement

from wasatch.SpectrometerSettings import SpectrometerSettings
from wasatch.ProcessedReading     import ProcessedReading
from wasatch.Reading              import Reading

log = logging.getLogger(__name__)

class TextFileParser:
    """
    A file parser to deserialize one Measurement from a column-ordered CSV file
    with no header data.  Infers unit of x-axis from current graph settings.
    Added to support Andor Solis .asc files.

    @todo consider parsing metadata found below the spectrum, including the following
          from Andor Solis .asc files:

          Date and Time:                Fri May  6 12:08:48 2022
          Temperature (C):              -60
          Model:                        DV416_LD
          Data Type:                    Counts
          Exposure Time (secs):         0.05667
          Horizontally flipped:         false
          Serial Number:                27239
          Pre-Amplifier Gain:           1x

    @todo given Andor serial number, consider using ENLIGHTEN's configured 
          excitation for that unit as the excitation — or even for full x-axis?
    """

    def __init__(self, ctl, pathname, graph):
        self.ctl = ctl
        self.pathname = pathname
        self.graph = graph

        self.timestamp = datetime.datetime.now()
        self.processed_reading = ProcessedReading()
        self.processed_reading.reading = Reading(device_id = "LOAD:" + self.pathname)
        self.settings = SpectrometerSettings()

    def parse(self):
        x = []
        y = []

        with open(self.pathname, "r") as infile:
            for line in infile:
                line = line.strip()
                if len(line) == 0:
                    break

                if "\t" in line:
                    tok = line.split("\t")
                else:
                    tok = line.split(",")

                x.append(float(tok[0].strip()))
                y.append(float(tok[1].strip()))

        self.settings.eeprom.active_pixels_horizontal = len(x)

        self.processed_reading.processed = y

        if self.graph.in_wavelengths():
            self.settings.wavelengths = x
        elif self.graph.in_wavenumbers():
            self.settings.wavenumbers = x

        self.processed_reading.post_load_cleanup(self.settings)
        self.ctl.horiz_roi.process(self.processed_reading)

        m = Measurement(
            ctl               = self.ctl,
            source_pathname   = self.pathname, 
            timestamp         = self.timestamp,
            processed_reading = self.processed_reading,
            settings          = self.settings)

        m.add_pathname(self.pathname)

        return m
