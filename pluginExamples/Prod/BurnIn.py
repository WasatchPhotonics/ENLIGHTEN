from EnlightenPlugin import *

import random
import datetime

import logging
log = logging.getLogger(__name__)

class BurnIn(EnlightenPluginBase):
    """
    A plug-in to help support "burn-in" of a new spectrometer, AKA "load-test"
    or "robustness validation".

    Note that the acquisition parameters in effect when the plugin is enabled 
    will remain in effect until the first scheduled randomization.

    Signals cruft relates to saving spectra (thumbnail widget creation) and 
    anything that emits to the Marquee (which affects QTimers).
    """

    def init_defaults(self):
        """ Initial GUI values, unless overwritten by enlighten.ini """
        self.defaults = {
            "Integ Time": True,
            "Gain dB": False,
            "TEC Setpoint": False,
            "Use Laser": False,
            "Laser Power": False,
            "Laser Duty Cycle": 20,
            "Take Dark": False,
            "Save Each": True,
            "Export Every": 100,
            "Change Min": 1,
            "Shutdown Min": 3 
        }

    def configure_from_ini(self):
        """ Load settings from previous session """
        s = "Plugin.BurnIn"
        config = self.ctl.config # wasatch.Configuration
        self.log("configure_from_ini")
        for k, v in self.defaults.items():
            if config.has_option(s, k):
                self.log(f"found option {s}.{k}")
                if isinstance(v, bool):
                    self.defaults[k] = config.get_bool(s, k)
                elif isinstance(v, int):
                    self.defaults[k] = config.get_int(s, k)
                self.log(f"loaded option {k} = {self.defaults[k]}")

    def cache_config(self, request):
        """ Persist user options so they'll be saved to enlighten.ini at shutdown """
        s = "Plugin.BurnIn"
        config = self.ctl.config # wasatch.Configuration
        for k, v in request.fields.items():
            if k in self.defaults:
                config.set(s, k, v)

    def get_configuration(self):
        self.name = "Burn-In"
        self.auto_enable = True

        self.init_defaults()

        self.configure_from_ini()

        ########################################################################
        # UI Fields
        ########################################################################

        # [x] Enabled serves as start/stop button

        # @todo would be kind of nice if we could visually "group" these on the 
        # GUI, similar to how they're spaced in code

        self.field(name="Integ Time",      datatype=bool, direction="input",  initial=self.defaults["Integ Time"],      tooltip="randomize integration time between min and 1sec")
        self.field(name="Gain dB",         datatype=bool, direction="input",  initial=self.defaults["Gain dB"],         tooltip="randomize gain between 0-24dB")
        self.field(name="TEC Setpoint",    datatype=bool, direction="input",  initial=self.defaults["TEC Setpoint"],    tooltip="randomize detector TEC setpoint")
                                                                                                                        
        self.field(name="Use Laser",       datatype=bool, direction="input",  initial=self.defaults["Use Laser"],       tooltip="fire laser (DANGEROUS)")
        self.field(name="Laser Power",     datatype=bool, direction="input",  initial=self.defaults["Laser Power"],     tooltip="randomize laser power")
        self.field(name="Laser Duty Cycle",datatype=int,  direction="input",  initial=self.defaults["Laser Duty Cycle"],tooltip="% of each session laser should fire", minimum=1, maximum=100)
        self.field(name="Take Dark",       datatype=bool, direction="input",  initial=self.defaults["Take Dark"],       tooltip="take fresh dark for each int/gain change")
                                                                                                                        
        self.field(name="Measurements",    datatype=int,  direction="output",                                           tooltip="measurement count")
        self.field(name="Save Each",       datatype=bool, direction="input",  initial=self.defaults["Save Each"],       tooltip="save each measurement")
        self.field(name="Export Every",    datatype=int,  direction="input",  initial=self.defaults["Export Every"],    tooltip="export and clear clipboard every x measurements (0 for never)", maximum=500)
                                                                                                                        
        self.field(name="Change Min",      datatype=int,  direction="input",  initial=self.defaults["Change Min"],      tooltip="randomize parameters every x min", minimum=1, maximum=30)
        self.field(name="Shutdown Min",    datatype=int,  direction="input",  initial=self.defaults["Shutdown Min"],    tooltip="shutdown ENLIGHTEN after x minutes (0 for never)", maximum=60)
                                           
        self.field(name="Next Change",     datatype=str,  direction="output", tooltip="scheduled randomization")
        self.field(name="Laser Expiry",    datatype=str,  direction="output", tooltip="scheduled laser deactivation")
        self.field(name="Next Shutdown",   datatype=str,  direction="output", tooltip="scheduled shutdown")

        ########################################################################
        # Internal State
        ########################################################################

        self.last_shutdown_min = None
        self.laser_expiry = None        # when to turn off laser
        self.params_expiry = None       # when to randomize acquisition parameters
        self.shutdown_expiry = None     # when to restart ENLIGHTEN
        self.darks_remaining = 0        # measurements before enabling laser
        self.measurement_count = 0
        self.header_logged = False

    def process_request(self, request):

        now = datetime.datetime.now()
        self.log_header(request)
        self.cache_config(request)

        ########################################################################
        # process this measurement
        ########################################################################

        self.log("processing measurement")

        if self.darks_remaining > 0:
            self.log("storing dark")
            # self.ctl.dark_feature.store(request.processed_reading.processed)
            self.signals.append("self.ctl.dark_feature.store()")
            self.darks_remaining -= 1

            if self.darks_remaining == 0 and request.fields["Use Laser"]:
                self.log("firing laser")
                # self.ctl.laser_control.set_laser_enable(True)
                self.signals.append("self.ctl.laser_control.set_laser_enable(True)")
        
        if request.fields["Save Each"]:
            # I dislike using eval(), but I haven't found the "proper" way to get 
            # this event to occur on the GUI thread (required to create a new
            # thumbnail)
            self.signals.append("self.ctl.vcr_controls.save()")

        if request.fields["Export Every"] > 0 and self.ctl.measurements.count() >= request.fields["Export Every"]:
            self.log("exporting session")
            # self.ctl.measurements.export_session(prompt=False)
            self.signals.append("self.ctl.measurements.export_session(prompt=False)")

            self.log("clearing clipboard")
            # self.ctl.measurements.erase_all()
            self.signals.append("self.ctl.measurements.erase_all()")

        self.measurement_count += 1
        self.outputs["Measurements"] = self.measurement_count

        ########################################################################
        # monitor shutdown expiry
        ########################################################################

        if self.shutdown_check(request):
            return

        ########################################################################
        # monitor laser expiry
        ########################################################################

        self.laser_check(request)

        ########################################################################
        # generate params for the next measurements
        ########################################################################

        if self.params_expiry is None or self.params_expiry <= now:
            self.randomize_params(request)
            self.params_expiry = now + datetime.timedelta(minutes=request.fields["Change Min"])
            self.log(f"next randomization scheduled for {self.params_expiry}")

        self.outputs["Next Change"] = str(self.params_expiry-now).split(".")[0] if self.params_expiry else None

    def laser_check(self, request):
        if not request.fields["Use Laser"]:
            self.outputs["Laser Expiry"] = None
            return

        now = datetime.datetime.now()
        shutdown_min = request.fields["Shutdown Min"]
        duty_cycle = request.fields["Laser Duty Cycle"] / 100.0

        if self.laser_expiry is None:
            self.laser_expiry = now + datetime.timedelta(minutes=shutdown_min * duty_cycle)
            self.log(f"scheduled laser shutdown for {self.laser_expiry}")
        elif self.laser_expiry <= now and request.settings.state.laser_enabled:
            self.log(f"time to disable laser")
            self.signals.append("self.ctl.laser_control.set_laser_enable(False)")

        if now < self.laser_expiry:
            self.outputs["Laser Expiry"] = str(self.laser_expiry-now).split(".")[0] 
        else:
            self.outputs["Laser Expiry"] = None

    def shutdown_check(self, request):
        now = datetime.datetime.now()
        shutdown_min = request.fields["Shutdown Min"]

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
                self.log(f"scheduled shutdown for {self.shutdown_expiry}")
            else:
                # is this a CHANGE from the previous configuration?
                if shutdown_min != self.last_shutdown_min:
                    # the user has changed the previous shutdown expiry,
                    # so recompute
                    self.shutdown_expiry = now + datetime.timedelta(minutes=shutdown_min)
                    self.last_shutdown_min = shutdown_min
                    self.laser_expiry = None
                    self.log(f"changed shutdown to {self.shutdown_expiry}")
                else:
                    # is it time to shutdown?
                    if self.shutdown_expiry <= now:
                        self.log("Shutting down")
                        self.signals.append("self.ctl.laser_control.set_laser_enable(False)")
                        self.signals.append("self.ctl.close('initiated by BurnIn')")
                        # enlighten.ini will persist some but not all settings
                        return True

        if self.shutdown_expiry and now < self.shutdown_expiry:
            self.outputs["Next Shutdown"] = str(self.shutdown_expiry-now).split(".")[0]
        else:
            self.outputs["Next Shutdown"] = None

    def randomize_params(self, request):
        self.log("randomizing acquisition parameters")

        eeprom = request.settings.eeprom

        if request.fields["Integ Time"]:
            ms = random.randint(eeprom.min_integration_time_ms, 1000)
            self.log(f"randomized integration time to {ms}ms")
            self.signals.append(f"self.ctl.integration_time_feature.set_ms({ms})")

        if request.fields["Gain dB"] and request.settings.is_xs():
            dB = random.randint(0, 240) / 10.0
            self.log(f"randomized gain to {dB}dB")
            self.signals.append(f"self.ctl.gain_db_feature.set_db({dB})")

        if request.fields["TEC Setpoint"] and eeprom.has_cooling:
            # note, we would probably never want to randomize laser setpoint
            degC = random.randint(eeprom.min_temp_degC, eeprom.max_temp_degC)
            self.log(f"randomized detector setpoint to {degC}C")
            self.signals.append(f"self.ctl.detector_temperature.apply_setpoint({degC})")

        if request.fields["Laser Power"]:
            if eeprom.has_laser_power_calibration():
                mW = random.randint(eeprom.min_laser_power_mW, eeprom.max_laser_power_mW)
                self.log(f"randomized laser power to {mW}mW")
                self.signals.append(f"self.ctl.laser_control.set_mW({mW})")
            else:
                perc = random.randint(1, 100)
                self.log(f"randomized laser power to {perc}%")
                self.signals.append(f"self.ctl.laser_control.set_perc({perc})")

        if request.fields["Use Laser"]:
            if request.fields["Take Dark"]:
                # self.ctl.laser_control.set_laser_enable(False)
                self.signals.append("self.ctl.dark_feature.clear()")
                self.signals.append("self.ctl.laser_control.set_laser_enable(False)")
            else:
                # self.ctl.laser_control.set_laser_enable(True)
                self.signals.append("self.ctl.laser_control.set_laser_enable(True)")

        if request.fields["Take Dark"]:
            self.darks_remaining = 5

    def log_header(self, request):
        """ Make it easy to see ENLIGHTEN restarts in plugin logfile """
        if self.header_logged:
            return

        sn = request.settings.eeprom.serial_number
        self.logfile = os.path.join(common.get_default_data_dir(), f"BurnIn-{sn}.log")

        self.log("-"*80)
        self.log(f"{self.name} started with {sn}")
        self.log("-"*80)

        for k, v in request.fields.items():
            self.log(f"{k} = {v}")
        for i, s in enumerate(request.settings.eeprom.hexbuf):
            self.log(f"EEPROM Page {i}: {s}")

        self.header_logged = True
