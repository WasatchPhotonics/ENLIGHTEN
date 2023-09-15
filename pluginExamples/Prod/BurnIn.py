from EnlightenPlugin import *

import random

import logging
log = logging.getLogger(__name__)

class BurnIn(EnlightenPluginBase):
    """
    A plug-in to help support "burn-in" of a new spectrometer, AKA "load-test"
    or "robustness validation".

    To be clear, ENLIGHTEN is not envisioned as a manufacturing tool (Wasatch has
    WPSC, QCSV etc for that), and that is not expected to change. However, the 
    plug-in architecture provides a convenient way to add "manufacturing 
    capabilities" to ENLIGHTEN without fundamentally complicating ENLIGHTEN's 
    core customer UI.
    """

    def get_configuration(self):
        self.name = "Burn-In"

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

        self.params = None
        self.last_change = None
        self.params_expiry = None
        self.next_shutdown = None
        self.measurement_count = 0
        self.next_is_dark = False

    def process_request(self, request):

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

        now = datetime.now()
        if self.params_expiry and self.params_expiry < now:
            self.log("keeping old params")
        else:
            self.randomize_params(request)

            # schedule the next randomization
            self.params_expiry = now + datetime.timedelta(minutes=request.fields["Change Min"])
            self.log(f"next randomization scheduled for {self.params_expiry}")

    def randomize_params(self, request):
        """
        Generate and apply randomized new aquisition parameters
        """
        self.log("randomizing acquisition parameters")

        params = AcquisitionParameters()
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return
        eeprom = spec.settings.eeprom

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
