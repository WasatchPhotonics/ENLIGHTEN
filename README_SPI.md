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

## FT232H Pin Assignments

Wasatch.PY (specifically, SPIDevice.py) contains hard-coded assumptions about how
your Adafruit FT232 is wired into the 15-pin Accessory Connector.  

Please note the Accessory Connector pin-out in ENG-0150 includes the 
following pins:

- Pin 5 TRIGGER_IN
- Pin 6 DATA_READY

SPIDevice.py is currently hardcoded to expect these pins to be mapped as follows
on the FT232 (this agrees with spi_console.py):

- D5 DATA_READY
- D6 TRIGGER_IN

If your FT232 was wired differently (for instance with TRIGGER on C0 and READY on C1),
you will need to temporarily edit SPIDevice.py appropriately.
