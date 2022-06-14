# Ocean Insight Compatability 

## USB CORE

Using usb.core it should just be ensuring that libusb is installed and python-seabreeze is installed. 
Additionally, it is important to make sure that the libusb-1.0 dll is on the computer.

## USB LEGACY

Previously, Wasatch.PY used the pyUSB legacy architecture by using regular 
'import usb'. This means the following steps needed to be setup to get Ocean 
Insight spectrometers to generally work with Enlighten.

- run either bootstrap.bat or activate your conda enviornment
- ensure you have libusb installed with pip
- Install [Zadig](https://zadig.akeo.ie/)
- Use Zadig to replace the driver from any of the Ocean spectrometers with a libusbK driver
- Install the Wasatch [python-seabreeze](https://github.com/WasatchPhotonics/python-seabreeze/tree/master) fork with the branch that contains the modifications for Ocean spectrometers
- set your PYTHONPATH with the following command:

    C:> set PYTHONPATH=.;..\Wasatch.PY;.\pluginExamples;..\python-seabreeze\;..\python-seabreeze\src;

- run enlighten from source as you normally would
