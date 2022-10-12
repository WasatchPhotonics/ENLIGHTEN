from PySide2 import QtCore

import datetime
import logging

log = logging.getLogger(__name__)

## 
# Encapsulates the 3 virtual status "LEDs" in the bottom-right of ENLIGHTEN's Scope view:
# 
# - hardware status 
# - lamp/laser status
# - detector temperature status 
#
# Each "LED" has three potential colors / states:
#
# - grey ("disconnected")
# - green ("connected")
# - orange ("warning")
#
# These are the 9 basic options:
#
# @par Hardware Status
#
# - orange/warning if a "critical" error was logged within the last HARDWARE_WARNING_WINDOW_SEC, else
# - green/connected if one or more spectrometers found, else
# - else grey/disconnected (no spectrometers found)
#
# @par Lamp / Laser
#
# - orange/warning if laser / lamp on selected spectrometer illuminated, else
# - grey/disconnected if laser is found but interlock open, else
# - green/connected (no laser/lamp found, or interlock closed but not illuminated)
#
# @par Temperature
#
# - orange/warning if TEC enabled and at least one reading in last 3sec was >1C from setpoint (or unreadable), else
# - grey/disconnected if TEC disabled or no TEC found, else
# - green/connected (TEC enabled and within setpoint during stability window)
#
class StatusIndicators:

    SLEEP_BETWEEN_UPDATES_MS = 250
    HARDWARE_WARNING_WINDOW_SEC = 3
    TEMPERATURE_WINDOW_SEC = 10

    def __init__(self,
             multispec,
             stylesheets,

             button_hardware,
             button_lamp,
             button_temperature):

        self.multispec          = multispec
        self.stylesheets        = stylesheets
        self.button_hardware    = button_hardware
        self.button_lamp        = button_lamp
        self.button_temperature = button_temperature
                
        self.last_hardware_error_time = None

        # don't start on construction
        self.timer = QtCore.QTimer() 
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tick)

        # default to "disconnected"
        self.update_visibility()

    # ##########################################################################
    # public methods
    # ##########################################################################

    def start(self, ms):
        self.timer.start(ms)

    def stop(self):
        self.timer.stop()

    def raise_hardware_error(self):
        self.last_hardware_error_time = datetime.datetime.now()

    ##
    # Control the trio of "connection status" colored buttons (should be QLabels)
    # at the lower-right of the GUI (below control widget column). Also
    # disable indicators if no spectrometer is connected.
    def update_visibility(self):
        spec = self.multispec.current_spectrometer()

        # the existing stylesheets are named "foo_connected" and "foo_disconnected"
        hw   = "disconnected"
        lamp = "disconnected"
        temp = "disconnected"

        hw_tt   = ""
        lamp_tt = ""
        temp_tt = ""

        if spec is not None:
            app_state = spec.app_state
            settings = spec.settings

            reading = None
            if app_state is not None and app_state.processed_reading is not None:
                reading = app_state.processed_reading.reading

            ####################################################################
            # hardware status
            ####################################################################

            if self.last_hardware_error_time is not None:
                elapsed_sec = (datetime.datetime.now() - self.last_hardware_error_time).total_seconds()
                if elapsed_sec <= self.HARDWARE_WARNING_WINDOW_SEC:
                    hw = "warning"
                    hw_tt = f"hardware error logged {elapsed_sec:f2} sec ago"
                else:
                    hw = "connected"
            else:
                hw = "connected"

            ####################################################################
            # Light Source (Lamp, Laser etc)
            ####################################################################

            all_specs = self.multispec.get_spectrometers()
            if settings.eeprom.has_laser and len(all_specs) <= 1:
                
                if reading is None:
                    if settings.state.laser_enabled:
                        lamp = "warning"
                        lamp_tt = "laser enabled"
                    else:
                        lamp = "connected"
                        lamp_tt = "laser not enabled"

                else:
                    if reading.laser_is_firing:
                        lamp = "warning"
                        lamp_tt = "laser is firing"
                    elif reading.laser_can_fire:
                        lamp = "connected"
                        lamp_tt = "laser armed (can fire)"
                    else:
                        lamp = "disconnected"
                        lamp_tt = f"laser disarmed (cannot fire)"
            elif settings.eeprom.gen15 and len(all_specs) <= 1:
                if settings.state.laser_enabled:
                    lamp = "warning"
                    lamp_tt = "lamp enabled"
                else:
                    lamp = "connected"
                    lamp_tt = "lamp disabled"
            else:
                # default behavior should be to do the normal processing
                # Multispec case here checks all and will overwrite if a laser is on
                specs_lasers_on = [s.settings.state.laser_enabled for s in all_specs]
                if any(specs_lasers_on):
                    lamp = "warning"
                    lamp_tt = "laser is firing"

            ####################################################################
            # Detector Temperature
            ####################################################################

            if settings.eeprom.has_cooling:
                setpoint = settings.state.tec_setpoint_degC
                enabled = settings.state.tec_enabled
                latest = app_state.detector_temperature_degC_latest

                if enabled:
                    if latest is not None:
                        if app_state.detector_temperatures_degC.all_within(setpoint, 1.0, window_sec=self.TEMPERATURE_WINDOW_SEC):
                            temp = "connected"
                            temp_tt = "temperature stable"
                        else:
                            temp = "warning" 
                            temp_tt = "temperature stabilizing"
                    else:
                        temp = "warning"
                else:
                    temp = "disconnected" # user disabled TEC
                    temp_tt = "TEC disabled"
            else:
                temp = "connected" # if there is no TEC, leave green
                temp_tt = "ambient detector"

        self.stylesheets.apply(self.button_hardware,    "hardware_%s"    % hw)
        self.stylesheets.apply(self.button_lamp,        "light_%s"       % lamp)
        self.stylesheets.apply(self.button_temperature, "temperature_%s" % temp)

        self.button_hardware    .setToolTip(hw_tt)
        self.button_lamp        .setToolTip(lamp_tt)
        self.button_temperature .setToolTip(temp_tt)

    # ##########################################################################
    # private methods
    # ##########################################################################

    def tick(self):
        self.update_visibility()
        self.timer.start(self.SLEEP_BETWEEN_UPDATES_MS)
