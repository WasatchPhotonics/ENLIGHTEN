import spc_spectra as spc
import datetime
import logging
import re
import os

import numpy as np

from enlighten.measurement.Measurement import Measurement

log = logging.getLogger(__name__)

##
# This is an SPC file parser, used to load and read SPC files in the ThermoScientific
# "Galactic" GRAMS SPC format.
#
# It cannot be used for writing SPC files.  For that we probably need the GSpcIOSDK
# available from the GRAMS sales team.  Note that this reader should be cross-platform,
# while the writer would likely be a Windows-only DLL.  We could alternately make our
# own native Python writer using the "Galactic Universal Data Format Specification,"
# but I haven't tracked down a copy of that.
#
# @see https://en.wikipedia.org/wiki/SPC_file_format
# @see https://github.com/NickMacro/spc-spectra
class SPCFileParser:

    RESCALE_TARGET_COUNTS = 30000.0

    ##
    # Graph is used to determine the current x-axis, if we are unable to determine
    # the file's x-axis (wavelength vs wavenumber) and default to simply load into the
    # current coordinate space.
    def __init__(self, pathname, graph):
        self.pathname = pathname
        self.graph = graph

    ## 
    # Given an SPC file, load it and return a list of Measurement
    # objects parsed from that one SPC file.
    # 
    # @todo think about other things we could import from the file
    def parse(self):

        basename = os.path.basename(self.pathname)

        ########################################################################
        # load the SPC file
        ########################################################################

        log.debug("instantiating spc.File from %s", self.pathname)
        data = spc.File(self.pathname)
        log.debug(f"spc parse atts are {data.__dict__}")
        #for key, value in data.__dict__:
        #    log.debug(f"spc parse attrs are {key}: {value}")

        ########################################################################
        # determine the SPC format
        ########################################################################

        fmt = data.dat_fmt
        log.debug("loaded SPC format: %s", fmt)
        #self.dump(data)

        ########################################################################
        # parse the timestamp
        ########################################################################

        timestamp = None
        if hasattr(data, "year") and data.year > 0:
            timestamp = datetime.datetime(data.year, data.month, data.day, data.hour, data.minute)

        ########################################################################
        # determine the x-axis (wavelength or wavenumber)
        ########################################################################

        unit = None
        if data.fxtype in [1, 13]:
            # if hasattr(data, "xlabel") and re.search("raman|shift|wavenumber", data.xlabel, re.IGNORECASE):
            # spc_spectra should return "Raman Shift (cm-1)" for spcioXType.spcioXRamans (0x0d) and
            # "Wavenumber (cm-1)" for spcioXWavn (0x01)
            # per SpcIOdll.h and https://github.com/NickMacro/spc-spectra/blob/master/spc/spc.py#L418
            # This should be equivalent to: data.fxtype in [1, 13]
            unit = "cm"
        elif data.fxtype == 3:
            # elif hasattr(data, "xlabel") and re.search("nanometer", data.xlabel, re.IGNORECASE):
            # spc_spectra should return "Nanometers (nm)" for spcioXType.spcioXNMetr (0x03)
            # This should be equivalent to: data.fxtype == 3
            unit = "nm"
        else:
            # assume the user knows what they're doing and load into the currently selected x-axis
            unit = self.graph.get_x_axis_unit()

        ########################################################################
        # instantiate each sub-file into a Measurement (some have own x-axis)
        ########################################################################
        is_xyxy = data.txyxys

        measurements = []
        for sub in data.sub:
            x = sub.x if fmt.endswith('-xy') else data.x
            log.debug(f"parse sub data is {sub.__dict__}")
            if is_xyxy:
                # spc_spectra library appears abandoned and has a few bugs
                # here the issue is ONLY for XYXY files they interpret them as Galactic floats
                # The standard seems to imply they are always IEEE floats
                # this block converts them back to IEEE floats and reads them
                x_to_raw = np.vectorize(lambda x: x/(2**(data.fexp-32)))
                x_raw = x_to_raw(x)
                x = np.frombuffer(x_raw.astype("<i4").tobytes(), "<f4")
            label = basename if data.fnsub == 1 else ("%s-%02d" % (basename, sub.subindx))
            measurements.append(self.create_measurement_from_sub(x, sub.y, unit=unit, timestamp=timestamp, label=label))

        return measurements

    ## 
    # Given arrays of x-axis and y (intensities) and the x-axis unit ("cm" or "nm"),
    # return a single Measurement from that data.
    def create_measurement_from_sub(self, x, y, unit="nm", timestamp=None, label=None):

        ########################################################################
        # force x-axis in ascending order (list.reverse() barfed on some files)
        ########################################################################

        if x[0] > x[1]:
            x = [ i for i in reversed(x) ]
            y = [ i for i in reversed(y) ]

        ########################################################################
        # some SPC files have intensity way outside our bounds, so rescale
        ########################################################################

        maxOrig = max(y)
        try:
            if len(maxOrig) > 1:
                maxOrig = max(maxOrig)
        except:
            pass

        if maxOrig < 100 or maxOrig > 0xffff:
            log.debug("scaling from %e to %e", maxOrig, self.RESCALE_TARGET_COUNTS)
            y = [ self.RESCALE_TARGET_COUNTS * i / maxOrig for i in y ]
        log.debug("maxOrig %e scaled max %e", maxOrig, max(y))

        ########################################################################
        # there are a couple different ways to instantiate a Measurement...for 
        # now, re-use the dictionary constructor used with JSON files
        ########################################################################

        d = {
            "ProcessedReading": {
                "Processed": y, 
            },
            "SpectrometerSettings": {}
        }

        if unit == "cm":
            d["SpectrometerSettings"]["wavenumbers"] = x

            # assign a fake wavelength array in pixel space, because we don't currently
            # handle Measurements that don't have a wavelength x-axis
            d["SpectrometerSettings"]["wavelengths"] = [ i for i in range(len(x)) ]
        else:
            d["SpectrometerSettings"]["wavelengths"] = x

        if timestamp is not None:
            d["Timestamp"] = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')

        if label is not None:
            d["Label"] = label

        # instantiate the Measurement from the generated dictionary
        return Measurement(d=d)

    ## log all the attributes of the generated SPC object for debugging
    def dump(self, obj):
        log.debug("SPC:")
        for attr in obj.__dict__:
            log.debug("  %30s: %s", attr, getattr(obj, attr))
