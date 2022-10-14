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

- Scope Technique
    - change integ time
    - laser works
    - change laser power
    - averaging works
    - TEC changes are reflected in Hardware Capture
    - save CSV
- Raman Technique
    - dark works
    - shows peaks
- Reflectance/Transmission Technique
    - reference works
- Absorbance Technique
    - reference works

All of the above with no Traceback or CRITICAL reported in log.
