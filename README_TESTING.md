# Regression Testing

This module uses pytest in order to run tests.

To run the tests in the /test folder from the CLI call:

	pytest .\test

## Writing a Test

The short summary is classes start with Test, functions start with test_. Pytest also uses python's assert statements for testing.

- https://docs.pytest.org/en/6.2.x/getting-started.html#create-your-first-test
- https://docs.pytest.org/en/6.2.x/example/markers.html#mark-examples

To run only the release tests use ```pytest .\test -m release```

## User Testing

- 1920x1080 resolution (production)

## Initial Test Plan

- Scope View
    - change integ time
    - laser works
    - change laser power
    - averaging works
    - TEC changes are reflected in Hardware Capture
    - save CSV
- Raman View
    - dark works
    - shows peaks
- Reflectance/Transmission View
    - reference works
- Absorbance View
    - reference works

All of the above with no Traceback reported in log.
