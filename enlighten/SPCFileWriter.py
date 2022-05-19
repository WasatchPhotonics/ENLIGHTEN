# See the following refernces for details on the .spc file format implementation
# https://github.com/bz-dev/spc-sdk
# https://www.yumpu.com/en/document/read/40416248/a-brief-guide-to-spc-file-format-and-using-gspcio
# https://ensembles-eu.metoffice.gov.uk/met-res/aries/technical/GSPC_UDF.PDF

from collections import namedtuple
import os
import sys
import math
import logging
from struct import pack
from datetime import datetime
from enum import IntEnum, IntFlag, Enum

import numpy as np

log = logging.getLogger(__name__)

RES_DESC_LIMIT = 9
SRC_INSTRUMENT_LIMIT = 9
MEMO_LIMIT = 130
AXES_LIMIT = 30
METHOD_FILE_LIMIT = 48
SPARE_LIMIT = 8
RESERVE_LIMIT = 187
LOG_RESERVE_LIMIT = 44

class SPCFileType(IntFlag):
    """
    Describes the various file format flags.
    See the old specification for greater detail on what each setting changes.
    """
    DEFAULT = 0 # Will be 32 bit single file, one trace, with even x values
    SIXTEENPREC = 1	# 32 bit float or 16 bit spc format, currently only support 32 
    TCGRAM = 2	# Enables fexper in older software (not used accroding to old format doc)
    TMULTI = 4	# Multiple traces format (set if more than one subfile), Y vs YYYY, XY vs XYYY/XYXY
    TRANDM = 8	# If TMULTI and TRANDM=1 then arbitrary time (Z) values, must pass full z array
    TORDRD = 16	# If TMULTI and TORDRD=1 then ordered but uneven z, must pass full z array if true, else only z_inc and single z value in z array 
    TALABS = 32	# If true, use the specified custom axes
    TXYXYS = 64	# If true the file is XYXYXY, flase is considered XYYYYYY 
    TXVALS = 128	# Non even X values, must pass full x array 

# From GRAMSDDE.h
# Currenlty only support PPNONE
class SPCProcessCode(IntEnum):
    PPNONE	= 0    # No post processing 
    PPCOMP	= 1    # Compute (run PPCOMP?.ABP) 
    PPDLLC	= 2    # Compute with DLL (run PPCOMP?.DLL) 
    PPTRANS = 4    # Transmission (run PPTRANS?.ABP) 
    PPABSRB = 8    # Absorbance (run PPABSRB?.ABP) 
    PPKMUNK = 12  # Kuebelka-Munk (run PPKMUNK?.ABP) 
    PPPEAK	= 32   # GRAMS built-in peak picking and reporting 
    PPSRCH	= 64   # Library Search associated w/experiment's LIB driver 
    PPUSER	= 128  # General user-written post program (run PPUSER?.ABP) 

class SPCModFlags(IntFlag):
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
    SUBNONE = 0 # No changes flag, this will likely be the ony one used. The others seem to be for software that regularly change .spc files
    SUBCHGD = 1	# Subflags bit if subfile changed 
    SUBNOPT = 8	# Subflags bit if peak table file should not be used 
    SUBMODF = 128	# Subflgs bit if subfile modified by arithmetic 

class SPCDate:
    def __init__(self, time: datetime = None) -> None:
        if time is None:
            time = datetime.datetime.now()

        self.compressed_date = int(0)

        minutes = int(time.minute) 
        hour = int(time.hour) << 6
        day = int(time.day) << 11
        month = int(time.month) << 16
        year = int(time.year) << 20
        
        self.compressed_date = (minutes & hour & day & month & year).to_bytes(32, byteorder = "big")

    def get(self):
        return self.compressed_date

class SPCFileWriter:
    """
    Created based on the spc file format.
    the primary method for writing files is via the write_spc_file method
    x data points and y data points are passed in via 2 different 2d arrays
    Only new format is currently supported.
    """
    def __init__(self,
                 file_type: SPCFileType,
                 num_pts: int = 0, # according to the docs if given num_pts, first_x, and last_x then it will calculate an evenly spaced x axis
                 compress_date: datetime = datetime.now(),
                 file_version: int = 0x4B,
                 experiment_type: SPCTechType = SPCTechType.SPCTechGen,
                 exponent: int = 0, # available but not supported
                 first_x: int = 0,
                 last_x: int = 0,
                 x_units: SPCXType = SPCXType.SPCXArb,
                 y_units: SPCYType = SPCYType.SPCYArb, 
                 z_units: SPCXType = SPCXType.SPCXArb,
                 res_desc: str = "",
                 src_instrument_desc: str = "",
                 custom_units: list[str] = [],
                 memo: str = "",
                 custom_axis_str: str = "",
                 spectra_mod_flag: SPCModFlags = SPCModFlags.Not,
                 z_subfile_inc: float = 1.0,
                 num_w_planes: float = 0,
                 w_plane_inc: float = 1.0,
                 w_units: SPCXType = SPCXType.SPCXArb,
                 log_data: bytes = bytes(),
                 log_text: str = "",
                 )-> None:
        """
        According to the formatting document the following file types are most common.
        For the respective file type, the corresponding initialization parameters 
        and arrays to the write function should be passed at a minimum
        ------------------
        Single File Even X
        ------------------
        Pass num_pts, first_x, last_x, and a 1D numpy array for the Y values

        ------------------
        Multifile Even X
        ------------------
        Pass num_pts, first_x, last_x, and a 2D numpy array for the Y values, each row represents a new subfile

        ------------------
        Single File Uneven X
        ------------------
        Pass a 1D nump array for the X values and a 1D numpy array for the Y values

        ------------------
        Multifile Uneven X common X
        ------------------
        Pass a 1D numpy array for the X values and a 2D numpy array for the Y values

        ------------------
        Multifile Uneven X common X
        ------------------
        Pass a 2D numpy array for the X values and a 2D numpy array for the Y values
        """
        self.file_type = file_type
        self.num_pts = num_pts
        self.compress_date = compress_date
        self.file_version = file_version
        self.experiment_type = experiment_type
        self.exponent = exponent
        self.first_x = first_x
        self.last_x = last_x
        self.x_units = x_units
        self.y_units = y_units
        self.z_units = z_units
        self.res_desc = res_desc
        self.src_instrument_desc = src_instrument_desc
        self.custom_units = custom_units
        self.memo = memo
        self.custom_axis_str = custom_axis_str
        self.spectra_mod_flag = spectra_mod_flag
        self.z_subfile_inc = z_subfile_inc
        self.num_w_planes = num_w_planes
        self.w_plane_inc = w_plane_inc
        self.w_units = w_units
        self.log_data = log_data
        self.log_text = log_text

    def write_spc_file(self,
                       file_name: str, 
                       y_values: np.ndarray,
                       x_values: np.ndarray = np.empty(shape=(0)),
                       z_values: np.ndarray = np.empty(shape=(0)),
                       w_values: np.ndarray = np.empty(shape=(0)),
                       ) -> bool:
        file_output = b""
        if x_values.size == 0:
            first_x = 0
            last_x = 0
        else:
            first_x = np.amin(x_values)
            last_x = np.amax(x_values)
        if not (self.file_type & SPCFileType.TMULTI):
            points_count = len(y_values)
        else:
            # num_points for XYXYXY is instead supposed to be the byte offset to the directory
            # or null and there is no directory
            points_count = 0 
        if len(y_values.shape) == 1:
            num_traces = 1
        else:
            num_traces = y_values.shape[0]

        if w_values.size != 0:
            if num_traces % len(w_values) != 0:
                log.error(f"w_values should divide evenly into the number of sub files")
                raise 

        By_values = self.convert_points(y_values)
        Bx_values = self.convert_points(x_values)

        file_header = self.generate_header(
            file_type = self.file_type,
            num_points = points_count,
            compress_date = SPCDate(self.compress_date),
            experiment_type = self.experiment_type,
            first_x = first_x,
            last_x = last_x,
            num_subfiles = num_traces,
            x_units = self.x_units,
            y_units = self.y_units,
            z_units = self.z_units,
            res_desc = self.res_desc,
            src_instrument_desc = self.src_instrument_desc,
            memo = self.memo,
            custom_axes = self.custom_units,
            spectra_mod_flag = self.spectra_mod_flag,
            z_subfile_inc = self.z_subfile_inc,
            num_w_planes = self.num_w_planes,
            w_plane_inc = self.w_plane_inc,
            w_units = self.w_units,
            )
        file_output = b"".join([file_output, file_header])

        if (self.file_type & SPCFileType.TXVALS) and not (self.file_type & SPCFileType.TXYXYS):
            file_output = b"".join([file_output, Bx_values]) # x values should be a flat array so shouldn't be any issues with this

        dir_pointers = []
        for i in range(num_traces):
            subfile = b""
            w_val = 0
            if w_values.size != 0:
                w_val = w_values[math.floor(i/w_values(len))]
            if SPCFileType.TXYXYS & self.file_type:
                points_count = len(y_values[i]) # inverse from header, header it is 0, here it's the length of a specific y input
            sub_header = b""
            match len(z_values):
                case 0:
                    z_val = 0
                case 1:
                    z_val = z_values[0]
                case _:
                    try:
                        z_val = z_values[i]
                    except:
                        z_val = 0
            sub_head = self.generate_subheader(start_z = z_val,
                                   sub_index = i, 
                                   num_points = points_count,
                                   w_axis_value = w_val)
            if self.file_type & SPCFileType.TXYXYS:
                subfile = b"".join(sub_head, x_values[i], y_values[i])
            else:
                subfile = b"".join(sub_head, y_values[i])

            pointer = self.generate_dir_pointer(len(file_output), len(subfile), z_val)
            dir_pointers.append(pointer)
            file_output = b"".join(file_output, subfile)

        if self.file_type & SPCFileType.TXVALS and self.file_type & SPCFileType.TXYXYS:
            file_output = b"".join(file_output, b"".join(dir_pointers))

        if len(self.log_data) > 0 or len(self.log_text) > 0:
            log = self.generate_log_header(self.log_data, self.log_text)
            file_output = b"".join(file_output, log, self.log_data, self.log_text.encode())

        with open(file_name, 'wb') as f:
            f.write(file_output)
            return True
        return False


    def generate_dir_pointer(self, offset: int, sub_size: int, z_val: float) -> bytes:
        Boffset = offset.to_bytes(4, offset)
        Bsub_size = sub_size.to_bytes(4, offset)
        Bz_value = pack("f", z_val)
        return b"".join([Boffset, Bsub_size, Bz_value])

    def generate_log_header(self, log_data: bytes, log_text: str) -> bytes:
        text_len = len(log_text.encode())
        data_len = len(log_data)
        block_size = 64 + text_len + data_len
        mem_block = 4096 * round(block_size/4096)
        text_offset = 64 + data_len
        Bblock_size = pack("l", block_size)
        Bmem_size = pack("l", mem_block)
        Btext_offset = pack("l", text_offset)
        Bdata_len = pack("l", data_len)
        Bdisk_len = b"\x00\x00\x00\x00"
        Breserved = bytes(bytearray(b"\x00"*LOG_RESERVE_LIMIT))
        return b"".join([Bblock_size, Bmem_size, Btext_offset, Bdata_len, Bdisk_len, Breserved])

    def convert_points(self, data_points: np.ndarray) -> bytes:
        """
        Takes a numpy array of data points and converts them to single precision floats.
        Then converts them to a string of bytes. Currently only supports the single precision.
        Does not support the spc specific exponent representation of floating point numbers.
        """
        data_points = data_points.astype(np.float32)
        return data_points.tobytes()

    def calc_log_offset(self, 
                        file_type: SPCFileType,
                        num_subfiles: int, 
                        num_points: int, 
                        ) -> int:
        """
        Calculates the log offset in bytes,
        assumes no directory present. If there is a directory
        that value is added later in the generate_header function
        """
        log_offset = 0
        log_offset += 512 # length of header
        if file_type & SPCFileType.TXVALS and not (file_type & SPCFileType.TXYXYS):
            log_offset += num_points # number of points for common x axis
        log_offset += num_subfiles * 32 # add 32 bytes for each subheader
        if file_type & SPCFileType.TMULTI and file_type & SPCFileType.TXYXYS:
            log_offset += num_points * num_subfiles # chose clarity over conciseness here
            log_offset += num_points * num_subfiles # first line represnets each x axis in subfile, second is each y
        else:
            log_offset += num_points * num_subfiles # only a y axis in each sub file
        return int(log_offset) # should be int but just to be safe
            
    def fit_byte_block(self, field: bytearray, limit: int) -> bytes:
        while len(field) < limit:
            field.extend(bytearray(b"\x00"))
        if len(field) > limit:
            field = field[:limit]
        return bytes(field)

    def generate_subheader(self,
                           subfile_flags: SPCSubfileFlags = SPCSubfileFlags.SUBNONE,
                           exponent: int = -128, # -128 so it will be an IEEE 32bit float
                           sub_index: int = 0,
                           start_z: float = 0.0, # looking at spc.h, z appears to be a time value so won't pass array of data points like x or y
                           end_z: float = 0.0,
                           noise_value: float = None, # should be null according to old format
                           num_points: int = None, # only needed for xyxy multifile
                           num_coadded: int = None,  # should be null according to old format
                           w_axis_value: float = 0.0,
                           ) -> bytes:
        Bsubfile_flags = subfile_flags.to_bytes(1, byteorder="big")
        Bexponent = pack("b", exponent)
        Bsub_index = pack("H", sub_index)
        Bstart_z = pack("f", start_z)
        Bend_z = pack("f", end_z)
        if noise_value is None:
            Bnoise_value = b"\x00\x00\x00\x00"
        else:
            Bnoise_value = pack("f", noise_value)
        if num_points is None:
            Bnum_points = b"\x00\x00\x00\x00"
        else:
            Bnum_points = pack("l", num_points)
        if num_coadded is None:
            Bnum_coadded = b"\x00\x00\x00\x00"
        else:
            Bnum_coaded = pack("l", num_coadded)
        Bw_axis_value = pack("f", w_axis_value)
        extra = b"\x00\x00\x00\x00" # 4 null bytes for the reserved portion
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
                        first_x: float = 0,
                        last_x: float = 0,
                        num_subfiles: int = 0,
                        x_units: SPCXType = SPCXType.SPCXArb,
                        y_units: SPCYType = SPCYType.SPCYArb, 
                        z_units: SPCXType = SPCXType.SPCXArb,
                        post_disposition: SPCPostDisposition = SPCPostDisposition.PSTDEFT, # should normally be null according to old format doc
                        res_desc: str = "",
                        src_instrument_desc: str = "",
                        peak_point: float = 0, # Interferogram peak point, associated with y_units = 2 
                        memo: str = "",
                        custom_axes: list[str] = [],
                        spectra_mod_flag: SPCModFlags = SPCModFlags.Not,
                        process_code: SPCProcessCode = SPCProcessCode.PPCOMP, # should normally be set to null according to old format file
                        calib_plus_one: int = b"\x00", # old format doc says galactic internal use and should be null
                        sample_inject: int = b"\x00\x00", # spc.h lists 1 as valid, old format doc says only for galactic internal use and should be null
                        data_mul: float = b"\x00\x00\x00\x00", # old format doc says galactic internal use only and should be null
                        method_file: str = b"\x00", # according to pdf it seems to just be the string rep of a file name for program data. Although old doc also says this should be null
                        z_subfile_inc: float = 1.0,
                        num_w_planes: float = 0,
                        w_plane_inc: float = 1.0,
                        w_units: SPCXType = SPCXType.SPCXArb,
                        ) -> bytes:
        Bfile_type = file_type.to_bytes(1, byteorder="big")
        Bfile_version = file_version.to_bytes(1, byteorder = "big")
        Bexperiment_type = experiment_type.to_bytes(1, byteorder = "big")
        Bexponent = exponent.to_bytes(1, byteorder = "big")
        Bnum_points = num_points.to_bytes(4, byteorder="big")
        Bfirst_x = pack("d", first_x)
        Blast_x = pack("d", last_x)
        Bnum_subfiles = pack("l", num_subfiles)
        Bx_units = x_units.to_bytes(1, "big")
        By_units = y_units.to_bytes(1, "big")
        Bz_units = z_units.to_bytes(1, "big")
        Bpost_disposition = post_disposition.to_bytes(1, "big")
        # compress date is already formated to bytes by the object
        Bres_desc = bytearray(res_desc, encoding="utf-8")
        Bres_desc = self.fit_byte_block(Bres_desc, RES_DESC_LIMIT)
        Bsrc_instrument_desc = bytearray(src_instrument_desc, encoding="utf-8")
        Bsrc_instrument_desc = self.fit_byte_block(Bsrc_instrument_desc, SRC_INSTRUMENT_LIMIT)
        Bpeak_point = pack("e", peak_point)
        spare = bytes(bytearray(b"\x00"*SPARE_LIMIT))
        Bmemo = bytearray(memo, encoding="utf-8")
        Bmemo = self.fit_byte_block(Bmemo, MEMO_LIMIT)
        Bcustom_axes = b"\x00".join([bytes(ax, encoding="utf-8") for ax in custom_axes])
        Bcustom_axes = self.fit_byte_block(bytearray(Bcustom_axes), AXES_LIMIT)
        log_offset = self.calc_log_offset(file_type, num_subfiles, num_points)
        if file_type & SPCFileType.TXYXYS:
            Bnum_points = log_offset.to_bytes(4, byteorder="big") # dir offset is log offset without dir since dir comes before log
            log_offset += num_subfiles * 12 # spc.h defines each dir entry as 12 bytes, one entry per subfile
        Blog_offset = pack("l", log_offset)
        Bspectra_mod_flag = pack("l", spectra_mod_flag)
        Bprocess_code = process_code.to_bytes(1, byteorder = "big")
        Bmethod_file = self.fit_byte_block(bytearray(method_file), METHOD_FILE_LIMIT)
        Bz_subfile_inc = pack("f", z_subfile_inc)
        Bnum_w_planes = pack("l", num_w_planes)
        Bw_plane_inc = pack("f", w_plane_inc)
        Bw_units = w_units.to_bytes(1, byteorder="big")
        Breserved = bytes(bytearray(b"\x00"*RESERVE_LIMIT))
        file_header = b"".join([
            Bfile_type, Bfile_version, Bexperiment_type, Bexponent, Bnum_points,
            Bfirst_x, Blast_x, Bnum_subfiles, Bx_units, By_units, Bz_units,
            Bpost_disposition, compress_date.get(), Bres_desc, Bsrc_instrument_desc, 
            Bpeak_point, spare, Bmemo, Bcustom_axes, Blog_offset, Bspectra_mod_flag,
            Bprocess_code, calib_plus_one, sample_inject, data_mul, Bmethod_file,
            Bz_subfile_inc, Bnum_w_planes, Bw_plane_inc, Bw_units, Breserved
            ])

        if len(file_header) < 512:
            log.error(f"file_header length is less than 512") # this shouldn't happen
            raise
        return file_header
