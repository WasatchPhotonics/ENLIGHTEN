import logging
import json
import os

from enlighten.EnlightenFeature import EnlightenFeature

from enlighten import common

log = logging.getLogger(__name__)

class EtalonCorrectionFeature(EnlightenFeature):

    def __init__(self, ctl):
        super().__init__(ctl)
        
        cfu = ctl.form.ui
        self.cb_enable = cfu.checkBox_etalon_correction
        
        self.enabled = False
        self.calibrations = {}

        self.cb_enable.stateChanged.connect(self._enable_callback)

    def update_visibility(self):
        """ Called by Controller.update_feature_visibility"""
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        sn = spec.settings.eeprom.serial_number

        # lazy-load etalon correction if we haven't already checked for this unit
        if sn not in self.calibrations:
            self._lazy_load_calibration(sn)

        calibration = self.calibrations.get(sn, None)
        self.cb_enable.setVisible(calibration is not None)

    def process(self, pr):
        """ Called by Controller.process_reading """
        if not self.enabled:
            return

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        sn = spec.settings.eeprom.serial_number
    
        calibration = self.calibrations.get(sn, None)
        if calibration is None:
            return 

        proc = pr.get_processed()
        if len(proc) != len(calibration):
            self.ctl.marquee.error("Etalon calibration does not match spectrum length ({len(calibration)} != {len(proc)})")
            return

        log.debug("applying etalon correction")
        corrected = np.array(proc) / calibration
        pr.set_processed(corrected)

    def _lazy_load_calibration(self, sn):
        if sn in self.calibrations:
            return

        # search for matching "serial_number.json" file in EnlightenSpectra/config
        calibration = None
        search_dir = os.path.join(common.get_default_data_dir(), "config")
        config_pathname = os.path.join(search_dir, f"{sn}.json")
        if os.path.exists(config_pathname):
            with open(config_pathname, "r", encoding="utf-8") as infile:
                config = json.load(infile)
                if "etalon_correction" in config:
                    calibration = np.array(config["etalon_correction"])
                else:
                    log.debug(f"missing etalon_correction: {config_pathname}")
        else:
            log.debug(f"not found: {config_pathname}")

        if calibration is None:
            self.ctl.marquee.error(f"unable to find etalon calibration for {sn}")

        # note that if none was found, None will be added to the dict, avoiding 
        # future searches
        self.calibrations[sn] = calibration

    def _enable_callback(self):
        self.enabled = self.cb_enable.isChecked()
