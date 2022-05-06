import datetime
import logging
import csv
import re

from .Measurement      import Measurement

from wasatch.SpectrometerSettings import SpectrometerSettings
from wasatch.ProcessedReading     import ProcessedReading
from wasatch.Reading              import Reading

log = logging.getLogger(__name__)

class TextFileParser(object):
    """
    A file parser to deserialize one Measurement from a column-ordered CSV file
    with no header data.  Infers unit of x-axis from current graph settings.
    Added to support Andor Solis .asc files.
    """

    def __init__(self, pathname, graph):
        self.pathname = pathname
        self.graph = graph

        self.timestamp = datetime.datetime.now()
        self.processed_reading = ProcessedReading()
        self.processed_reading.reading = Reading(device_id = "LOAD:" + self.pathname)
        self.settings = SpectrometerSettings()

    def parse(self) -> Measurement:
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
            log.debug("assuming wavelengths")
            self.settings.wavelengths = x
        elif self.graph.in_wavenumbers():
            log.debug("assuming wavenumbers")
            self.settings.wavenumbers = x

        self.processed_reading.post_load_cleanup()

        m = Measurement(
            source_pathname   = self.pathname, 
            timestamp         = self.timestamp,
            processed_reading = self.processed_reading,
            settings          = self.settings)

        m.add_renamable(self.pathname)

        return m
