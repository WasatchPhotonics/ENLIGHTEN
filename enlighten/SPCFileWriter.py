import os
import logging
from ctypes import cdll
from enum import IntEnum

log = logging.getLogger(__name__)

class SPCFileType(IntEnum):
    SPCFileTypeEven	= 0
    SPCFileTypeXYY	= 1
    SPCFileTypeXYXY	= 2

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

class SPCFileWriter:

    def __init__(self) -> None:
        pass


    def __enter__(self, save_filename, file_type = SPCFileType.SPCFileTypeXYY):
        self.SPCIO = self.driver.CreateSPC(file_type)

    def generate_header(self,
                        file_type: SPCFileType,
                        file_version: int = 0x4B,
                        experiment_type: SPCTechType = SPCTechType.SPCTechGen,
                        exponent: int = 0,
                        num_points: int,
                        first_x: int = 0,
                        last_x: int = 0,
                        num_subfiles: int = 0,
                        x_units: SPCXType = SPCXType.SPCXArb,
                        y_units = 
                        ):
        pass


