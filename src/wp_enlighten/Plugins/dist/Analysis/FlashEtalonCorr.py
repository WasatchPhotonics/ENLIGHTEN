import os
import json
import logging
import numpy as np

from wp_enlighten import common
from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class FlashEtalonCorr(EnlightenPluginBase):
    """
    Simple plug-in flash an etalon correction, provided via config/SN.json file,
    to the EEPROM of an XS unit.

    Note that this does expect that the loaded JSON factors represent the full
    detector width (i.e. 1952 for XS), so those factors should already have been
    "padded" with 1.0 outside of the horizontal ROI.
    """

    def get_configuration(self):
        self.name = "Flash Etalon Correction"
        self.correction = None
        self.process_requests = False

        self.field(name="Flash", datatype="button",  callback=self.flash, tooltip = "Click to flash your etalon correction to EEPROM")

    def flash(self):
        log.debug("flash: start")
        spec = self.ctl.multispec.current_spectrometer()
        eeprom = spec.settings.eeprom
        if spec is None:
            self.ctl.marquee.error(f"{self.name} requires a spectrometer")
            return

        if not spec.settings.is_xs():
            self.ctl.marquee.error(f"{self.name} requires an XS spectrometer")
            return

        if spec.settings.etalon_correction is None:
            self.ctl.marquee.error(f"{self.name} requires XS with etalon correction")
            return

        if eeprom.pixel_correction_type == eeprom.PIXEL_CORRECTION_ETALON:
            self.ctl.marquee.error(f"{self.name} requires XS with etalon correction in JSON (not already in EEPROM)")
            return
            
        # To have gotten this far, we must have an XS unit whose etalon 
        # correction was loaded from JSON, and is not [yet] flashed to its 
        # EEPROM. So all we need to do is write those loaded correction factors 
        # to the EEPROM.
        log.debug("flash: calling populate_eeprom_buffers(eeprom)")
        ok = spec.settings.etalon_correction.populate_eeprom_buffers(eeprom=eeprom)
        if not ok:
            self.ctl.marquee.error(f"{self.name} failed to populate EEPROM buffers")
            return
            
        log.debug("flash: sending write_eeprom_no_generate")
        spec.change_device_setting("write_eeprom_no_generate")

        log.debug("flash: done")

    def disconnect(self):
        super().disconnect()
