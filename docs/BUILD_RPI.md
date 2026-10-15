# Raspberry Pi

By and large, Raspberry Pi is just an ARM-based Linux variant, and so can
follow the process described in BUILD_LINUX.md (itself now pointing to 
BUILD_PYPI.md).

That said, this addendum to our [Linux Docs](BUILD_LINUX.md) applies to Raspberry
Pi, Odroid and other ARM-based Linux variants following the Debian model.

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
caused the unit to repeatedly freeze during package download / installation. 

The biggest package I struggled with was `tensorflow`, and now that it has been
removed as a dependency (replaced by `ai_edge_litert`), hopefully most of these
problems will go away.

Anyway, when struggling with package installation, I attempted all of the 
following in various combinations. I'm not sure which were the most critical, but
I'm pretty sure the $TMPDIR fix was key.

- change pip's temp dir                 <-- this was critical
    - `mkdir ~/tmp`
    - `export TMPDIR=$HOME/tmp`
- add heat sink to RPi
- add fan pointing to heat sink
- configure rpi-swap to 4GB (up from default 2GB)
    - `sudo apt install rpi-swap`
    - `sudo vi /etc/rpi/swap.conf`
- kill GUI (`sudo systemctl stop lightdm`)
- monitor temperature (`vcgencmd measure_temp`)
- throttle bandwidth 
    - `tc qdisc show dev wlan0`
    - `sudo tc qdisc add dev wlan0 root tbf rate 1mbit burst 10kb latency 70ms`
    - `tc qdisc show dev wlan0`

## Installation Process

    $ mkdir ~/tmp
    $ export TMPDIR=$HOME/tmp           # or someplace with 1GB+ free
    $ mkdir ~/work/code
    $ cd ~/work/code

    $ git clone https://github.com/WasatchPhotonics/Wasatch.PY.git
    $ sudo cp -vf Wasatch.PY/udev/10-wasatch.rules /etc/udev/rules.d 
    (bounce udev or reboot)

    $ cd ~/work/code
    $ git clone https://github.com/WasatchPhotonics/ENLIGHTEN.git
    $ cd ENLIGHTEN

    $ python -m venv venv --system-site-packages
    $ . venv/bin/activate
    $ sudo apt update
    $ sudo apt install -y pkg-config libusb-1.0-0-dev   # for seabreeze?
    $ pip install .                     # installs DEPENDENCIES, including `pyside6-uic` and other things needed by 
                                        # rebuild_resources.sh, plus "dist" wp_enlighten

    $ scripts/rebuild_resources.sh
    $ pip install .                     # re-installs wp_enlighten itself, including newly-built resources

Now you can run ENLIGHTEN itself. There are two different commands you should be
able to use at this point. Both should ideally yield the same result (ENLIGHTEN 
GUI appearing on your screen), but under the hood they get there very different
ways, and technically are running two different copies of the code.

    $ enlighten

This command is technically running `venv/bin/enlighten`, a script automatically 
created by the "hatchling" build engine referenced by pyproject.toml, and 
installed when you run `pip install .`. This script is actually going to run the
ENLIGHTEN PyPi (pip) package under `venv/lib/site-packages/wp_enlighten`, and NOT
the source code under src/wp_enlighten. (It already used that source to create 
the pip package, so the source was an important part of the process.)

...or...

    $ python src/wp_enlighten/app.py

This is ALMOST the same as the previous method. You might THINK this is running
all of ENLIGHTEN from source, including all the many files under src/wp_enlighten,
but...I don't think so. I think app.py's "import" statements are going to pull
their dependencies from `venv/lib/site-packages/wp_enlighten` (populated by 
`pip install .`), and you still won't really be running from source.

## Development Process

You can run from source, if you want, by setting your PYTHONPATH explicitly:

    $ export PYTHONPATH=$HOME/work/code/enlighten/src

Now it will prefer your "source" distribution to the installed packages. Note
that if you make local changes under src/wp_enlighten, you'd need to re-install
them (`pip install .`). 

If you're making a lot of iterative changes in the source, you can save time by
installing the wp_enlighten package in EDITABLE mode:

    $ pip install . -e

This way, changes made to the source are reflected immediately, each time you
run `app.py`.

If you also want to experiment with local changes to Wasatch.PY, you can do
the same tricks there:

    $ export PYTHONPATH=$HOME/work/code/enlighten/src:$HOME/work/code/Wasatch.PY
    $ ( cd ../Wasatch.PY && pip install . -e )

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
