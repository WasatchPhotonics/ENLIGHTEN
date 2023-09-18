from EnlightenPlugin import *

import random

import logging
log = logging.getLogger(__name__)

class BurnIn(EnlightenPluginBase):
    """
    A plug-in to help support "burn-in" of a new spectrometer, AKA "load-test"
    or "robustness validation".

    Note that the acquisition parameters in effect when the plugin is enabled 
    will remain in effect until the first scheduled randomization.
    """

    def get_configuration(self):
        self.name = "Burn-In"
        self.autoenable = True

        self.configure_from_ini()

        ########################################################################
        # UI Fields
        ########################################################################

        # [x] Enabled serves as start/stop button

        # @todo would be kind of nice if we could visually "group" these on the 
        # GUI, similar to how they're spaced in code

        self.field(name="Integ Time",    datatype=bool, direction="input",  tooltip="randomize integration time between min and 1sec")
        self.field(name="Gain dB",       datatype=bool, direction="input",  tooltip="randomize gain between 0-24dB")
        self.field(name="TEC Setpoint",  datatype=bool, direction="input",  tooltip="randomize detector TEC setpoint")

        self.field(name="Use Laser",     datatype=bool, direction="input",  tooltip="fire laser (DANGEROUS)")
        self.field(name="Laser Power",   datatype=bool, direction="input",  tooltip="randomize laser power")
        self.field(name="Take Dark",     datatype=bool, direction="input",  tooltip="take fresh dark for each int/gain change")

        self.field(name="Save Each",     datatype=bool, direction="input",  tooltip="save each measurement")
        self.field(name="Export Every",  datatype=int,  direction="input",  tooltip="export and clear clipboard every x measurements (0 for never)", max=500)

        self.field(name="Measurements",  datatype=int,  direction="output", tooltip="measurement count")
        self.field(name="Change Min",    datatype=int,  direction="input",  tooltip="randomize parameters every x min", min=1, max=30)

        self.field(name="Shutdown Min",  datatype=int,  direction="input",  tooltip="shutdown ENLIGHTEN after x minutes (0 for never)", max=60)
        self.field(name="Next Shutdown", datatype=str,  direction="output", tooltip="scheduled shutdown")

        ########################################################################
        # Internal State
        ########################################################################

        self.last_change = None
        self.params_expiry = None
        self.last_shutdown_min = None
        self.next_shutdown = None
        self.measurement_count = 0
        self.next_is_dark = False
        self.header_logged = False

    def process_request(self, request):

        self.log_header(request)

        ########################################################################
        # process this measurement
        ########################################################################

        self.log("processing measurement")

        if self.next_is_dark:
            self.log("storing dark")
            self.ctl.dark_feature.store(request.processed_reading.processed)
            self.next_is_dark = False

            if self.fields["Use Laser"]:
                self.log("firing laser")
                self.ctl.laser_control.set_laser_enable(True)
        
        if self.fields["Save Each"]:
            self.ctl.vcr_controls.save()

        if self.fields["Export Every"] > 0 and self.measurement_count >= self.fields["Export Every"]:
            self.log("exporting session")
            self.ctl.measurements.export_session(prompt=False)

            self.log("clearing clipboard")
            self.ctl.measurements.erase_all()

        self.measurement_count += 1
        self.outputs["Measurements"] = self.measurement_count

        ########################################################################
        # generate params for the next measurements
        ########################################################################

        self.shutdown_check(request)

        now = datetime.now()
        if self.params_expiry is None or self.params_expiry <= now:
            self.randomize_params(request)
            self.params_expiry = now + datetime.timedelta(minutes=request.fields["Change Min"])
            self.log(f"next randomization scheduled for {self.params_expiry}")

    def shutdown_check(self, request):
        now = datetime.now()
        shutdown_min = self.fields["Shutdown Min"]

        # has the user configured a shutdown period?
        if shutdown_min <= 0:
            # a shutdown is not requested via the GUI 
            # (may have been cancelled if previously requested)
            self.shutdown_expiry = None
            self.last_shutdown_min = shutdown_min
        else:
            # is this the FIRST time we've been assigned a shutdown expiry?
            if self.shutdown_expiry is None:
                # schedule future shutdown
                self.shutdown_expiry = now + datetime.timedelta(minutes=shutdown_min)
                self.last_shutdown_min = shutdown_min
                self.log("scheduled shutdown for {self.shutdown_expiry}")
            else:
                # is this a CHANGE from the previous configuration?
                if shutdown_min != self.last_shutdown_min:
                    # the user has changed the previous shutdown expiry,
                    # so recompute
                    self.shutdown_expiry = now + datetime.timedelta(minutes=shutdown_min)
                    self.last_shutdown_min = shutdown_min
                    self.log("changed shutdown to {self.shutdown_expiry}")
                else:
                    # is it time to shutdown?
                    if self.shutdown_expiry <= now:
                        self.log("Shutting down")
                        self.ctl.close("initiated by BurnIn")
                        # enlighten.ini will persist some but not all settings

    def randomize_params(self, request):
        """
        Generate and apply randomized new aquisition parameters
        """
        self.log("randomizing acquisition parameters")

        eeprom = request.settings.eeprom

        if request.fields["Integ Time"]:
            ms = random.randint(eeprom.min_integration_time_ms, 1000)
            self.log(f"randomized integration time to {ms}ms")
            self.ctl.integration_time_feature.set_ms(ms)

        if request.fields["Gain dB"]:
            dB = random.randint(0, 240) / 10.0
            self.log(f"randomized gain to {dB}dB")
            self.ctl.gain_db_feature.set_db(dB)

        if request.fields["TEC Setpoint"]:
            # note, we would probably never want to randomize laser setpoint
            degC = random.randint(eeprom.min_temperature_degC, eeprom.max_temperature_degC)
            self.log(f"randomized detector setpoint to {degC}C")
            self.ctl.detector_temperature_feature.apply_setpoint(degC)

        if request.fields["Laser Power"]:
            if settings.has_laser_power_calibration():
                mW = random.randint(eeprom.min_laser_power_mW, eeprom.max_laser_power_mW)
                self.log(f"randomized laser power to {mW}mW")
                self.ctl.laser_control.set_mW(mW)
            else:
                perc = random.randint(1, 100)
                self.log(f"randomized laser power to {perc}%")
                self.ctl.laser_control.set_perc(perc)

        if request.fields["Use Laser"] and not request.fields["Take Dark"]:
            self.ctl.laser_control.set_laser_enable(True)

        self.next_is_dark = request.fields["Take Dark"]

    def log_header(self, request):
        if self.header_logged:
            return

        eeprom = request.settings.eeprom
        self.log("-"x80)
        self.log(f"{self.name} started with {eeprom.serial_number}")
        self.log("-"x80)
        self.header_logged = True
