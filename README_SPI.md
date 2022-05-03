# SPI Spectrometers

This is assuming the use of the FT232H USB<->Serial converter.

All that should be needed to develop is running bootstrap.bat.
That should have the necessary modules and Enlighten.py has the enviornment variable setting.

If there are any issues connecting though, this tutorial should resolve them.
https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h


While setting up an installed version of enlighten 3.16 on a new windows computer,
Zadig was still required to replace the driver as in the linked tutorial. If the driver wasn't
libusbk then Enlighten wouldn't see the ft232 board.
