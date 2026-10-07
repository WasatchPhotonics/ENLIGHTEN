# Raspberry Pi

This addendum to our [Linux Docs](BUILD_LINUX.md) applies to Raspberry Pi, 
Odroid and other ARM-based Linux variants following the Debian model.

See [MAINTENANCE](MAINTENANCE.md) for temporary changes or workarounds to
the build process.

# Raspberry Pi Zero 

To be completely upfront: the Raspberry Pi Zero 2 W is NOT a suitable runtime 
platform for ENLIGHTEN, due to its limitation to no more than 512MB (0.5GB) RAM.
ENLIGHTEN will only run "well" on Raspberry Pi models with 4-8GB RAM (RPi 4/5+). 
That said, I was able to run ENLIGHTEN on a Pi Zero and take some spectra before
the kernel's Out-of-Memory (OOM) killer shut it down.

These setup notes were taken on an RPi Zero 2 W in Oct 2026 with the following
configuration:

    PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
    NAME="Debian GNU/Linux"
    VERSION_ID="13"
    VERSION="13 (trixie)"
    VERSION_CODENAME=trixie
    DEBIAN_VERSION_FULL=13.2
    ID=debian

## System Preparation

I had a lot of overheating? swap? disk space? issues on my RPi Zero 2 W, which 
caused the unit to repeatedly freeze during package download / installation. To 
address those, I attempted all of the following in various combinations. I'm not
sure which were the most critical, but I'm pretty sure the $TMPDIR fix was part
of it.

- change pip's temp dir (this was critical)
    - mkdir ~/tmp
    - export TMPDIR=$HOME/tmp
- add heat sink to RPi
- add fan pointing to heat sink
- install rpi-swap
- configure rpi-swap to 4GB (up from default 2GB)
    - sudo apt install rpi-swap
    - sudo vi /etc/rpi/swap.conf
- kill GUI (sudo systemctl stop lightdm)
- monitor temperature (vcgencmd measure_temp)
- throttle bandwidth 
    - tc qdisc show dev wlan0
    - (qdisc fq_codel 0: root refcnt 2 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb ecn drop_batch 64)
    - sudo tc qdisc add dev wlan0 root tbf rate 1mbit burst 10kb latency 70ms

## Installation Process

    $ mkdir ~/tmp
    $ export TMPDIR=$HOME/tmp       # or someplace with 1GB+ free
    $ mkdir ~/work/code
    $ cd ~/work/code
    $ git clone https://github.com/WasatchPhotonics/ENLIGHTEN.git
    $ git clone https://github.com/WasatchPhotonics/Wasatch.PY.git
    $ cd ENLIGHTEN

    $ python -m venv venv --system-site-packages
    $ . venv/bin/activate
    $ sudo apt update
    $ sudo apt install -y pkg-config libusb-1.0-0-dev   # for seabreeze?
    $ pip download tensorflow --timeout 60              # can possibly skip
    $ pip install -r requirements.txt

    $ scripts/rebuild_resources.sh

Add the following to your path:

    $ export PYTHONPATH=".:plugins:../Wasatch.PY:enlighten/assets/uic_qrc"

Copy the `10-wasatch.rules` rules file to set appropriate permissions for usb access 
(you will need to restart or reload after this):

    $ sudo cp -vf ../Wasatch.PY/udev/10-wasatch.rules /etc/udev/rules.d

Launch ENLIGHTEN:

    $ python -u scripts/Enlighten.py

## OOM-Killer

The Linux kernel has a feature called the OOM-Killer designed to automatically 
shutdown programs consuming dangerous levels of memory. If ENLIGHTEN abruptly 
terminates on your Raspberry Pi, run the following command to confirm it was the 
OMM-Killer responsible, and not a software bug:

    $ sudo dmesg -T | egrep -i 'killed process|out of memory'

# Appendix: Resetting USB Ports

Raspberry Pi have a unique ability to power-cycle the entire internal USB hub, 
forcing re-enumeration on all devices, and power-cycling those which are powered
via USB.  This can be done with commands like:

    $ sudo uhubctl -l 2 -a 0 && sleep 2 && uhubctl -l 2 -a 1 

or

    $ sudo uhubctl --action 2 --location 2 --repeat 2 --delay 5 --wait 1000
