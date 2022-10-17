import sys
import time
import copy
import struct
import pytest
import random
import logging
import threading
from PySide2 import QtCore
from PySide2.QtTest import QTest

import numpy

from wasatch.Reading import Reading
from enlighten import common
from wasatch.ProcessedReading import ProcessedReading
import scripts.Enlighten as enlighten
from wasatch.MockUSBDevice import MockUSBDevice
from conftest import wait_until, create_sim_spec, disconnect_spec

log = logging.getLogger(__name__)

class TestUSB:

    ############
    # Test Cases
    ############

    # description: verifies a sim spec's eeprom values are loaded properly and match the object's eeprom values
    # author: Evan Dort
    def test_eeprom_fields(self,app):
        sim_spec = create_sim_spec(app,"SiG_785","EEPROM-EM-9c65d19f4c.json")
        app_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        keys_to_check = ["format",
                         "subformat",
                         "tec_beta",
                         "model",
                         "excitation_nm",
                         "bin_2x2",
                         "detector",
                         "max_laser_power_mW",
                         "serial_number",
                         "tec_r298",
                         ]
        for key in keys_to_check:
            sim_eeprom = sim_spec.eeprom[key]
            obj_eeprom = getattr(app_spec_obj.settings.eeprom,key)
            if sim_eeprom != obj_eeprom:
                try:
                    if abs((sim_eeprom-obj_eeprom)/sim_eeprom) < 0.01:
                        continue
                except:
                    pass
                log.error(f"Key {key},sim and app object, eeprom values don't match {sim_eeprom} NOT {obj_eeprom}")
                assert False, f"Key {key},sim and app object, eeprom values don't match {sim_eeprom} NOT {obj_eeprom}"
        assert True
        disconnect_spec(app,sim_spec)

    # description: test that a mock usb device is created
    # author: Evan Dort
    def test_fake_connect(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json") 
        assert type(sim_spec) is MockUSBDevice
        disconnect_spec(app,sim_spec)

    @wait_until(timeout=5000)
    def disconnect_complete(self, caplog):
        if "exiting because of downstream poison-pill command from ENLIGHTEN" in caplog.text:
            return True

    # description: a release test that checks the gui change results in the 
    #              SPECTROMETER_SETTINGS integration time changing 
    # author: Mark Zieg
    #
    # This is an example test that shows how to write tests which are validated 
    # against spectrometer state within ENLIGHTEN (as opposed to within the Mock
    # spectrometer itself).
    #
    @pytest.mark.release
    def test_set_int_time_enlighten(self, app, caplog):
        sim_spec = create_sim_spec(app, "WP-00887", "WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)

        @wait_until(timeout=3000)
        def check():
            value = sim_spec_obj.settings.state.integration_time_ms
            return value

        if sim_spec:
            init_int = app.controller.form.ui.spinBox_integration_time_ms.value()
            int_up_btn = app.controller.form.ui.pushButton_integration_time_ms_up
            int_up_btn.click()

            res = check()
            assert res == init_int + 1

            disconnect_spec(app, sim_spec)
            assert self.disconnect_complete(caplog)
        else:
            assert False, f"No sim_spec, received {sim_spec} for sim_spec"

    # description: a release test that checks the GUI change results in the 
    #              MOCK DEVICE integration time changing
    # author: Evan Dort
    #
    # This is an example test that shows how to write tests which are validated 
    # against the Mock spectrometer (virtual hardware) in the Wasatch.PY driver, 
    # as opposed to within ENLIGHTEN's "application state".
    #
    @pytest.mark.release
    def test_set_int_time_mock(self, app, caplog):
        sim_spec = create_sim_spec(app, "WP-00887", "WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)

        @wait_until(timeout=5000)
        def check(expected):
            # first make sure the command has actually made it downstream to the mock
            if f"MockUSBDevice.set_int_time: value now {expected}" not in caplog.text:
                return

            # now make sure the mock has been properly updated
            mock = sim_spec_obj.get_mock()
            value = mock.int_time
            return value

        if sim_spec:
            init_int = app.controller.form.ui.spinBox_integration_time_ms.value()
            int_up_btn = app.controller.form.ui.pushButton_integration_time_ms_up
            int_up_btn.click()

            res = check(init_int + 1)
            assert res == init_int + 1

            disconnect_spec(app, sim_spec)
            assert self.disconnect_complete(caplog)
        else:
            assert False, f"No sim_spec, received {sim_spec} for sim_spec"

    # description: test that the mock device indicates it received the start up write values for integration, gain, and offset
    # author: Evan Dort
    def test_set_startup_settings(self,app):
        sim_spec = create_sim_spec(app,"SiG_785","EEPROM-EM-9c65d19f4c.json")
        assert sim_spec.got_start_int \
            and sim_spec.got_start_detector_gain \
            and sim_spec.got_start_detector_offset
        disconnect_spec(app,sim_spec)

    # description: test that multiple mock devices can be created
    # author: Evan Dort
    def test_multispec_connnect(self,app):
        sim_spec1 = create_sim_spec(app,"WP-00913","WP-00913-mock.json")
        sim_spec2 = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        assert type(sim_spec1) is MockUSBDevice and type(sim_spec2) is MockUSBDevice
        disconnect_spec(app,sim_spec1)
        disconnect_spec(app,sim_spec2)

    # description: test that for a multispec changing the combo box changes the current spec
    # author: Evan Dort
    def test_multispec_select(self,app):
        sim_spec1 = create_sim_spec(app,"WP-00913","WP-00913-mock.json")
        sim_spec2 = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_obj1 = app.controller.multispec.get_spectrometer(sim_spec1)
        sim_obj2 = app.controller.multispec.get_spectrometer(sim_spec2)
        sim1_idx = app.controller.multispec.get_combo_index(sim_obj1)
        sim2_idx = app.controller.multispec.get_combo_index(sim_obj2)
        app.controller.multispec.combo_spectrometer.setCurrentIndex(sim1_idx)
        current_index = app.controller.multispec.combo_spectrometer.currentIndex()
        app.controller.multispec.combo_callback()
        current_spec = app.controller.multispec.current_spectrometer()
        change1 = app.controller.multispec.is_current_spectrometer(sim_obj1)
        app.controller.multispec.combo_spectrometer.setCurrentIndex(sim2_idx)
        current_index = app.controller.multispec.combo_spectrometer.currentIndex()
        app.controller.multispec.combo_callback()
        current_spec = app.controller.multispec.current_spectrometer()
        change2 = app.controller.multispec.is_current_spectrometer(sim_obj2)
        assert change1 and change2
        disconnect_spec(app,sim_spec1)
        disconnect_spec(app,sim_spec2)

    # description: test that a sim spec returns a spectra, which is a numpy array of floats
    # author: Evan Dort
    def test_acquire_spectra(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        app.controller.attempt_reading(sim_spec_obj)
        graph_readings = app.controller.graph.plot.getPlotItem().listDataItems()
        eeprom = sim_spec_obj.settings.eeprom
        spec_reading = [reading for reading in graph_readings if reading.name() == f"{eeprom.serial_number} ({eeprom.model})"][0]
        spec_intensities = spec_reading.getData()[0]
        float_check = [isinstance(value,float) for value in spec_intensities]
        assert isinstance(spec_intensities,numpy.ndarray) and all(float_check), type(spec_intensities)
        disconnect_spec(app,sim_spec)

    # description: test that toggling the laser button changes the mock device laser
    # author: Evan Dort
    @pytest.mark.release
    def test_laser_toggle(self, app, caplog):
        sim_spec = create_sim_spec(app,"WP-00887", "WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)

        @wait_until(timeout=2000)
        def check(expected_value):
            # first make sure the command has actually made it downstream to the mock
            # if f"MockUSBDevice.cmd_toggle_laser: setting {expected_value}" not in caplog.text:
            #     return

            # now make sure the mock was correctly updated
            mock = sim_spec_obj.get_mock()
            return mock.laser_enable == expected_value

        laser_btn = app.controller.form.ui.pushButton_laser_toggle 

        laser_btn.click()
        laser_enabled = check(True)

        laser_btn.click()
        laser_disabled = check(False)

        assert laser_enabled and laser_disabled

        disconnect_spec(app, sim_spec)
        assert self.disconnect_complete(caplog)

    # description: test that on disconnect the mock device receives a request to shut down its laser
    # author: Evan Dort
    def test_laser_shutdown(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)

        @wait_until(timeout=2000)
        def check(expected_value):
            if sim_spec.laser_enable == expected_value:
                return True

        laser_btn = app.controller.form.ui.pushButton_laser_toggle
        laser_btn.click()
        laser_enabled = check(True)
        disconnect_spec(app,sim_spec)
        laser_disabled = check(False)
        assert laser_enabled and laser_disabled

    # description: test that on start up the tec is enabled
    # author: Evan Dort
    @pytest.mark.release
    def test_tec_init_enable(self,app):

        @wait_until(timeout=3000)
        def check():
            mock = sim_spec_obj.get_mock()
            return mock.detector_tec_enable 

        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        res = check()
        assert res
        disconnect_spec(app,sim_spec)

    # description: test that on disconnect the mock device tec is disabled
    # author: Evan Dort
    def test_tec_disable_shutdown(self,app):

        @wait_until(timeout=3000)
        def check():
            if not sim_spec.detector_tec_enable:
                return True

        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        disconnect_spec(app,sim_spec)
        res = check()
        assert res
        disconnect_spec(app,sim_spec)

    # description: test that the displayed temp matches the mock device temp
    # author: Evan Dort
    @pytest.mark.release
    def test_temp(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        display_temp = float(app.controller.form.ui.label_StatusBar_temp_value.text())
        raw = sim_spec.cmd_get_detector_temp()
        temp_raw = int.from_bytes(raw,byteorder='big')
        detector_temp = sim_spec.eeprom["adc_to_degC_coeffs"][0] \
            + sim_spec.eeprom["adc_to_degC_coeffs"][1] * temp_raw \
            + sim_spec.eeprom["adc_to_degC_coeffs"][2] * temp_raw**2
        app.controller.tick_acquisition()
        last_read = app.controller.get_last_reading()
        per_diff = abs((last_read.detector_temperature_degC-detector_temp)/detector_temp)
        assert per_diff < 0.1
        disconnect_spec(app,sim_spec)

    # description: test that changing the gain results in a mock device gain change
    # author: Evan Dort
    def test_gain_set(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        gain_up = app.controller.form.ui.pushButton_gain_up
        init_gain = app.controller.form.ui.doubleSpinBox_gain.value()
        gain_up.click()

        @wait_until(timeout=2000)
        def check():
            per_diff = abs((init_gain+1-sim_spec.detector_gain)/sim_spec.detector_gain)
            if per_diff < 0.1:
                return True

        res = check()
        assert res
        disconnect_spec(app,sim_spec)

    # description: test that changing the tec results in a change for the mock device
    # author: Evan Dort
    def test_tec_toggle(self,app):

        @wait_until(timeout=2000)
        def check(status):
            if sim_spec.detector_tec_enable == status:
                return True

        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        option_cb = app.controller.form.ui.checkBox_AdvancedOptions
        option_cb.click() 
        tec_cb = app.controller.form.ui.checkBox_AdvancedOptions_TECControl
        tec_cb.click()
        btn_tec_enable = app.controller.form.ui.checkBox_tec_enabled
        init_state_enable = check(True)
        btn_tec_enable.click()
        tec_disabled = check(False)
        btn_tec_enable.click()
        log.info(f"init_state_enable is {init_state_enable} and tec dis {tec_disabled}")
        assert init_state_enable and tec_disabled
        disconnect_spec(app,sim_spec)

    # description: test that changing the tec setpoint is reflected in the mock device
    # author: Evan Dort
    def test_set_tec(self,app):
        sim_spec = create_sim_spec(app,"WP-00887","WP-00887-mock.json")
        sim_spec_obj = app.controller.multispec.get_spectrometer(sim_spec)
        option_cb = app.controller.form.ui.checkBox_AdvancedOptions
        option_cb.click() 
        tec_cb = app.controller.form.ui.checkBox_AdvancedOptions_TECControl
        tec_cb.click()
        tec_init_val = app.controller.form.ui.spinBox_detector_setpoint_degC.value()
        btn_tec_up = app.controller.form.ui.temperatureWidget_pushButton_detector_setpoint_up
        btn_tec_up.click()

        @wait_until(timeout=2000)
        def check():
            set_raw = sim_spec.eeprom["degC_to_dac_coeffs"][0] \
                + sim_spec.eeprom["degC_to_dac_coeffs"][1] * (tec_init_val + 1) \
                + sim_spec.eeprom["degC_to_dac_coeffs"][2] * (tec_init_val + 1)**2 
            if round(set_raw) == sim_spec.detector_setpoint:
                return True

        res = check()
        assert res
        disconnect_spec(app,sim_spec)
