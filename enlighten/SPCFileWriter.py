# See the following refernces for details on the .spc file format implementation
# https://github.com/bz-dev/spc-sdk
#
# https://ensembles-eu.metoffice.gov.uk/met-res/aries/technical/GSPC_UDF.PDF


import os
import sys
import struct
import logging
from enum import IntEnum
from datetime import datetime

import numpy as np

log = logging.getLogger(__name__)

class SPCFileType(IntEnum):
    SPCFileTypeEven	= 0 # Y only files YYY
    SPCFileTypeXYY	= 1
    SPCFileTypeXYXY	= 2

# From GRAMSDDE.h
# Currenlty only support PPNONE
class SPCProcessCode(Enum):
    PPNONE	= 0    # No post processing 
    PPCOMP	= 1    # Compute (run PPCOMP?.ABP) 
    PPDLLC	= 2    # Compute with DLL (run PPCOMP?.DLL) 
    PPTRANS = 4    # Transmission (run PPTRANS?.ABP) 
    PPABSRB = 8    # Absorbance (run PPABSRB?.ABP) 
    PPKMUNK = 12  # Kuebelka-Munk (run PPKMUNK?.ABP) 
    PPPEAK	= 32   # GRAMS built-in peak picking and reporting 
    PPSRCH	= 64   # Library Search associated w/experiment's LIB driver 
    PPUSER	= 128  # General user-written post program (run PPUSER?.ABP) 

class SPCModFlags(Enum):
    Not = 0 # unmodified
    A = 2**1 # Averaging (from multiple source traces)
    B = 2**2 # Baseline correction or offset functions
    C = 2**3 # Interferogram to spectrum Computation
    D = 2**4 # Derivative (or integrate) functions
    E = 2**6 # Resolution Enhancement functions (such as deconvolution)
    I = 2**9 # Interpolation functions
    N = 2**14 # Noise reduction smoothing
    O = 2**15 # Other functions (add, subtract, noise, etc.)
    S = 2**19 # Spectral Subtraction
    T = 2**20 # Truncation (only a portion of original X axis remains)
    W = 2**20 # When collected (date and time information) has been modified
    X = 2**24 # X units conversions or X shifting
    Y = 2**25 # Y units conversions (transmission->absorbance, etc.)
    Z = 2**26 # Zap functions (features removed or modified)

# looking at example parsers,
# axes z and w use the same units
class SPCXType(IntEnum):
    SPCXArb	        = 0
    SPCXWaven	    = 1
    SPCXUMetr	    = 2
    SPCXNMetr	    = 3
    SPCXSecs	    = 4
    SPCXMinuts	    = 5
    SPCXHertz	    = 6
    SPCXKHertz	    = 7
    SPCXMHertz	    = 8
    SPCXMUnits	    = 9
    SPCXPPM	        = 10
    SPCXDays	    = 11
    SPCXYears	    = 12
    SPCXRamans	    = 13
    SPCXeV	        = 14
    SPCZTextL	    = 15
    SPCXDiode	    = 16
    SPCXChanl	    = 17
    SPCXDegrs	    = 18
    SPCXDegrF	    = 19
    SPCXDegrC	    = 20
    SPCXDegrK	    = 21
    SPCXPoint	    = 22
    SPCXMSec	    = 23
    SPCXUSec	    = 24
    SPCXNSec	    = 25
    SPCXGHertz	    = 26
    SPCXCM	        = 27
    SPCXMeters	    = 28
    SPCXMMetr	    = 29
    SPCXHours	    = 30
    SPCXAngst	    = 31
    SPCXDblIgm	    = 255

class SPCZIncType(IntEnum):
    SPCZIncTypeNotMulti	= -1
    SPCZIncTypeEven	    = 0
    SPCZIncTypeOrdered	= 1
    SPCZIncTypeRandom	= 2

class SPCTechType(IntEnum):
    SPCTechGen    = 0
    SPCTechGC     = 1
    SPCTechCgm    = 2
    SPCTechHPLC   = 3
    SPCTechFTIR   = 4
    SPCTechNIR    = 5
    SPCTechUV     = 7
    SPCTechXry    = 8
    SPCTechMS     = 9
    SPCTechNMR    = 10
    SPCTechRmn    = 11
    SPCTechFlr    = 12
    SPCTechAtm    = 13
    SPCTechDAD    = 14
    SPCTechThrm   = 15
    SPCTechCD     = 16
    SPCTechCNMR   = 20
    SPCTechHNMR   = 21
    SPCTechDNMR   = 22
    SPCTechANMR   = 23

class SPCYType(IntEnum):
    SPCYArb	        = 0
    SPCYIgram	    = 1
    SPCYAbsrb	    = 2
    SPCYKMonk	    = 3
    SPCYCount	    = 4
    SPCYVolts	    = 5
    SPCYDegrs	    = 6
    SPCYAmps	    = 7
    SPCYMeters      = 8
    SPCYMVolts      = 9
    SPCYLogdr	    = 10
    SPCYPercnt      = 11
    SPCYIntens      = 12
    SPCYRelInt      = 13
    SPCYEnergy      = 14
    SPCYDecbl	    = 16
    SPCYAbund	    = 17
    SPCYRelAbn      = 18
    SPCYDegrF	    = 19
    SPCYDegrC	    = 20
    SPCYDegrK	    = 21
    SPCYIdxRf	    = 22
    SPCYExtCf	    = 23
    SPCYReal	    = 24
    SPCYImag	    = 25
    SPCYCmplx	    = 26
    SPCYMgram	    = 27
    SPCYGram	    = 28
    SPCYKGram	    = 29
    SPCYSRot	    = 30
    SPCYTrans	    = 128
    SPCYReflec      = 129
    SPCYValley      = 130
    SPCYEmisn	    = 131

# From GRAMSDDE.h
# currently only supporting default PSTDEFT
class SPCPostDisposition(IntEnum):
    PSTDEFT = 0    # Use default setting (xfrpost is "unspecified") 
    PSTSAVE = 1    # Save file to disk (but remove from memory) 
    PSTAPPD = 2    # Append to end of #R database or xfrmtd .GDB database 
    PSTMERG = 3    # Merge into current #R database row 
    PSTBACK = 4    # Save as new background for experiment 
    PSTNONE = 5    # Do not save after processing (if any) 
    PSTKEEP = 6    # Do not save and keep in memory as #S 
    PSTBOTH = 7    # Both disk save & keep in #S memory (ABC Driver Only!) 
    PSTASK	= 8    # Query user: save, keep, or both (ABC Driver Only!) 

class SPCSubfileFlags(IntEnum):
    SUBNONE = 0 # No changes flag
    SUBCHGD = 1	# Subflags bit if subfile changed 
    SUBNOPT = 8	# Subflags bit if peak table file should not be used 
    SUBMODF = 128	# Subflgs bit if subfile modified by arithmetic 

class SPCDate:
    def __init__(self, time: datetime = None) -> None:
        if time is None:
            time = datetime.datetime.now()

        self.compressed_date = int(0)

        minutes = (int(time.minute) & 0x3F) 
        hour = (int(time.hour) & 0x1F) << 6
        day = (int(time.day) & 0x1F) << 11
        month = (int(time.month) & 0xF) << 16
        year = (int(time.year) & 0xFFF) << 20
        
        self.compressed_date = (minutes & hour & day & month & year).to_bytes(32, byteorder = "big")

class SPCFileWriter:
    """
    Created based on the spc file format.
    the primary method for writing files is via the write_spc_file method
    x data points and y data points are passed in via 2 different 2d arrays
    Only new format is currently supported.
    """
    def __init__(self) -> None:
        pass

    def write_spc_file(self,
                       file_name: str, 
                       x_values: np.ndarray,
                       y_values: np.ndarray,
                       z_values: np.ndarray = np.empty(shape=(0)),
                       ) -> None:
        pass

    def convert_points(self, data_points: np.ndarray) -> bytes:
        """
        Takes a numpy array of data points and converts them to single precision floats.
        Then converts them to a string of bytes. Currently only supports the single precision.
        Does not support the spc specific exponent representation of floating point numbers.
        """
        data_points = data_points.astype(np.float32)
        return data_points.tobytes()

    def generate_subheader(self,
                           subfile_flags: SPCSubfileFlags.SUBNONE,
                           exponent: int = 1,
                           sub_index: int = 1,
                           start_z: float = 0.0, # looking at spc.h, z appears to be a time value so won't pass array of data points like x or y
                           end_z: float = 0.0,
                           noise_value: float = 0.0,
                           num_points: int = 0, # only needed for xyxy multifile
                           num_coadded: int = 0,
                           w_axis_value: float = 0.0,
                           ) -> bytes:
        Bsubfile_flags = pack("c", subfile_flags)
        Bexponent = pack("B", exponent)
        Bsub_index = pack("H", sub_index)
        Bstart_z = pack("f", start_z)
        Bend_z = pack("f", end_z)
        Bnoise_value = pack("f", noise_value)
        Bnum_points = pack("l", num_points)
        Bnum_coaded = pack("l", num_coadded)
        Bw_axis_value = pack("f", w_axis_value)
        extra = b"    "
        subheader = b''.join([Bsubfile_flags, 
                              Bexponent, 
                              Bsub_index, 
                              Bstart_z, Bend_z, 
                              Bnoise_value, 
                              Bnum_points,
                              Bnum_coaded,
                              Bw_axis_value,
                              extra])
        if len(subheader) < 32:
            log.error(f"sub header was less than 32 bytes. It was {len(subheader)}. This shouldn't happen")
            raise
        return subheader

    def generate_header(self,
                        file_type: SPCFileType,
                        num_points: int, # or directory position for XYXYXY files
                        compress_date: SPCDate,
                        file_version: int = 0x4B,
                        experiment_type: SPCTechType = SPCTechType.SPCTechGen,
                        exponent: int = 0,
                        first_x: int = 0,
                        last_x: int = 0,
                        num_subfiles: int = 0,
                        x_units: SPCXType = SPCXType.SPCXArb,
                        y_units: SPCYType = SPCYType.SPCYArb, 
                        z_units: SPCXType = SPCXType.SPCXArb,
                        post_disposition: SPCPostDisposition = SPCPostDisposition.PSTDEFT,
                        peak_point: bytearray = bytearray(2), # max of 2 bytes
                        memo: str = "",
                        custom_axis_str: str = "",
                        log_offset: float = 0.0,
                        spectra_mod_flag: SPCModFlags = SPCModFlags.Not,
                        process_code: SPCProcessCode = SPCProcessCode.PPNONE,
                        calib_plus_one: int = 1,
                        sample_inject: int = 0, # spc.h lists 1 as valid but currently using 0
                        data_mul: float = 1.0,
                        f_method: list[int] = [0],
                        z_subfile_inc: float = 1.0,
                        num_w_planes: float = 0,
                        w_plane_inc: float = 1.0,
                        w_units: SPCXType = SPCXType.SPCXArb,
                        ) -> bytes:
        pass


