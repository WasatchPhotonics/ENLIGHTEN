# Regression Testing

This module uses pytest in order to run tests.  Mocks are provided by wasatch.MockUSBDevice.

## Running Tests

To run all tests in the /test folder from the CLI call:

	pytest .\test

To run only the release tests:

    pytest .\test -m release

To run a single test:

    pytest -v .\test\test_usb.py::TestUSB::test_set_int_time_enlighten

## Writing a Test

The short summary is classes start with Test, functions start with test_. Pytest also uses python's assert statements for testing.

- https://docs.pytest.org/en/6.2.x/getting-started.html#create-your-first-test
- https://docs.pytest.org/en/6.2.x/example/markers.html#mark-examples

## Initial Test Plan

- Scope View
    - change integ time
    - laser works
    - change laser power
    - averaging works
    - TEC changes are reflected in Hardware Capture
    - save CSV
- Raman Mode
    - dark works
    - shows peaks
- Reflectance/Transmission Technique
    - reference works
- Absorbance Technique
    - reference works

All of the above with no Traceback or CRITICAL reported in log.

## Enlighten Testing Reboot of 2023-03-28

Testing was paused from 2022-10-26 until now.

Testing is being rebooted because a few features that had worked in the past were found broken in late versions of Enlighten:
- CSV file reader
- Plugin local import

## Test Results

We have 30 existing tests and 10 of them are failing.

`test\test_gui.py::TestGUI::test_init_tech_and_play`

This tests that the initial view is SCOPE and that the interface starts out set to play.

I suspect that the initial view is what's causing this to fail, but this should be broken into two tests to make it more clear.

`test\test_gui.py::TestGUI::test_hidden_advanced`

This fails with an attribute error, hints that it's caused by a renaming

`test\test_gui.py::TestGUI::test_enable_hidden_advanced`

attribute error

`test\test_gui.py::TestGUI::test_laser_default_mW`

attribute error

`test\test_usb.py::TestUSB::test_set_startup_settings`

fails on sim_spec.got_start_int ??

`test\test_usb.py::TestUSB::test_laser_shutdown`

fails, with and expression

`test\test_usb.py::TestUSB::test_temp`

fails because UI now contains degrees Celcius symbols

`test\test_usb.py::TestUSB::test_gain_set`

???

`test\test_usb.py::TestUSB::test_tec_toggle`

attribute error

`test\test_usb.py::TestUSB::test_set_tec`

attribute error

## Synopsis

6 errors seem to be caused by renaming

test_temp is similar to renaming, but it fails because of change in output format

test_set_startup_settings, test_gain_set, test_laser_shutdown seems to be related to sim_spec

## Coverage

- CSV Save/Load
- Clipboard Save
- Switch to view: Scope/Settings/etc...
- CombinedPlugin Connect