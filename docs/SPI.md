# SPI Spectrometers

This is assuming the use of the FT232H USB&lt;--&gt;Serial converter.

All that should be needed to develop is running bootstrap.bat.

That should have the necessary modules and Enlighten.py has the environment variable setting, i.e.:

    C:> set BLINKA_FT232H="1"

# libusbK Driver Setup via Zadig (Windows-only)

If there are any issues connecting though, this tutorial should resolve them:

- https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h

While setting up an installed version of ENLIGHTEN 3.x on a new Windows computer,
Zadig was still required to replace the driver as in the linked tutorial. If the driver wasn't
libusbk then Enlighten wouldn't see the FT232 board.

Typical sequence:

- download Zadig from https://zadig.akeo.ie/
- run Zadig
- Options -> List all Devices
- Pull-down the main combo box and select "USB Serial Converter"
- Select driver "libusbK"
- Click "Replace Driver"

# Troubleshooting

## Environment Variables

    $ export BLINKA_FT232H=1

## Missing backend

MacOS:
    $ export DYLD_LIBRARY_PATH=/usr/local/lib

## Environment Variables

Wasatch.PY (specifically, SPIDevice.py) contains default assumptions about how
your Adafruit FT232H is wired into the 15-pin Accessory Connector, as well as the 
baud rate and USB block-size for communicating with the FT232H.

You can override those defaults by setting environment variables before running
ENLIGHTEN.  See here for more information:

- https://github.com/WasatchPhotonics/Wasatch.PY/blob/master/README.md#environment-variables

