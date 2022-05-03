import time
import pytest
import logging

import scripts.Enlighten as enlighten
from wasatch.MockUSBDevice import MockUSBDevice

# The fixture MUST go in this file
# conftest.py provides shared resources to each test file

# An important note for the usb tests
# While watching the GUI it seems as though enlighten is performing actions
# but the Qt main loop is NOT RUNNING
# This means calling certain events that would happen in the loop are required
# This is valuable to keep in mind if for some reason unexpected behavior is occuring
# There is a good chance it is because a timer isn't running 
# and this is resulting in values not being processed

# A slightly frustrating issue is that at some point, Enlighten makes a copy of the usb device
# This means the sim_spec we instantiate is not the same as the one being manipulated by Enlighten
# The work around I found for this was to use app.controller.multispec.get_spectrometer(sim_spec).device.device_id
# This exposes the MockUSBDevice object so you can use it

log = logging.getLogger(__name__)

@pytest.fixture(scope="session",name="app")
def fixture():
    enlighten_app = enlighten.EnlightenApplication(testing=True)
    enlighten_app.create_parser()
    enlighten_app.parse_args(["--log-level","debug","--headless"])#"--headless"
    enlighten_app.run()
    yield enlighten_app

def create_sim_spec(app,name,eeprom,eeprom_overrides=None,spectra_option=None):
    sim_spec = MockUSBDevice(name,eeprom,eeprom_overrides,spectra_option)
    if app.controller.multispec.is_disconnecting(sim_spec):
        app.controller.multispec.set_disconnecting(sim_spec, False)
    app.controller.connect_new(sim_spec)
    res = False
    @wait_until(timeout=5000)
    def check_connect():
        app.controller.check_ready_initialize()
        spec = app.controller.multispec.get_spectrometer(sim_spec)
        if spec:
            return spec.device.device_id
    res = check_connect() # res = wait_until(timeout=9000)(check_connect)()
    spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
    app.controller.attempt_reading(spec_obj)
    app.controller.attempt_reading(spec_obj)
    return res

def disconnect_spec(app,spec):
    spec_obj = app.controller.multispec.get_spectrometer(spec)
    #app.controller.multispec.remove_all()
    app.controller.disconnect_device(spec_obj)
    # clear persistence of sim specs
    app.controller.sim_devices = []
    # equivalent to controller.bus.update()
    # which doesn't occur because not ticks
    app.controller.bus.device_ids = []
    return True


# There is likely a better way to do this, especially since this creates a blocking timeout
# This somewhat jumbled arrangment though is the shared decorator that can be used
# to decorate any function with a custom timeout since some processing for gui events aren't instant
def wait_until(timeout=5000):
    def inner_dec(func):
        def wrapper(*args):
            start_ms = time.time() * 1000
            while True:
                res = func(*args)
                if ((time.time() * 1000) - start_ms) > timeout:
                    return False
                if res:
                    return res
                time.sleep(0.01)
            return res
        return wrapper
    return inner_dec


