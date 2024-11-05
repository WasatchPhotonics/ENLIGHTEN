import os
import json
import logging

from enlighten import common

log = logging.getLogger(__name__)

class PixelCalibration:
    """
    Support any additional pixel calibrations we may want to create which for 
    whatever reason need an external file and can't be kept on the EEPROM.

    @todo persist enable in enlighten.ini
    """

    def __init__(self, ctl):
        self.ctl = ctl
        cfu = ctl.form.ui

        self.cb_enable = cfu.checkBox_enable_pixel_correction

        self.enable_func = None
        self.disable_func = None

        self.cb_enable.stateChanged.connect(self.enable_callback)

    def update_visibility(self):
        self.enable_func = None
        self.disable_func = None

        spec = self.ctl.multispec.current_spectrometer()
        if spec:
            pathname = os.path.join(common.get_default_data_dir(), "config", f"{spec.settings.eeprom.serial_number}.json")
            if os.path.exists(pathname):
                self.load_config(pathname, spec)

        visible = self.enable_func is not None
        self.cb_enable.setVisible(visible)
                
    def enable_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if not spec or not self.enable_func:
            return

        if self.cb_enable.isChecked():
            self.enable_func()
        else:
            self.disable_func()

    def load_config(self, pathname, spec):
        """
        Kind of an odd approach...we want to be able to support various different
        PixelCalibration algorithms in the future. I'm not sure what arguments
        each might use, or what ENLIGHTEN classes or Wasatch.PY settings they
        might talk to. For now, successful parsing of the configuration file
        will populate enable_func and disable_func.

        Also, if we're going to break ground on a per-spectrometer configuration 
        file (holding "factory" config data as opposed to "session" data stored
        in enlighten.ini), potentially for various different calibrations that
        for whatever reason don't fit / belong in the EEPROM, then let's keep
        it flexible and store this class's stuff under a PixelCalibration
        header.
        """
        log.debug(f"loading calibration from {pathname}")
        try:
            with open(pathname, encoding='utf-8') as infile:
                text = infile.read()
            doc = json.loads(text)
            if "PixelCalibration" in doc:
                config = doc["PixelCalibration"]
                if "method" in config:
                    method = config["method"]
                    if method == "linear":
                        try:
                            slopes = config["slopes"]
                            offsets = config["offsets"]
                        except:
                            raise ValueError(f"{method} requires slopes and offsets")
                        if len(slopes) != len(offsets) or len(slopes) != spec.settings.pixels():
                            raise ValueError(f"{method} length mismatch: slopes {len(slopes)}, offsets {len(offsets)}, pixels {spec.settings.pixels()}")
                        self.enable_func  = lambda: spec.change_device_setting("linear_pixel_calibration", (slopes, offsets))
                        self.disable_func = lambda: spec.change_device_setting("linear_pixel_calibration", None)
                    else:
                        raise ValueError(f"unsupported method {method}")
                    log.debug(f"successfully loaded {method} calibration")
                else:
                    raise ValueError("invalid calibration: no method")
            else:
                raise ValueError(f"no PixelCalibration in {pathname}")
        except:
            log.error(f"failed to parse calibration from {pathname}", exc_info=1)
            self.enable_func = None
            self.disable_func = None
