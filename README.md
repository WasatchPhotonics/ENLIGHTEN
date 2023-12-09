\mainpage
![Logo](docs/images/logo-1000px.png)

# ENLIGHTEN Product Pages

If you are new to ENLIGHTEN and want to learn about *using* the software, versus
"building" or "maintaining" the software, please start with our *Operating Manual:*

- [ENLIGHTEN Manual](https://wasatchphotonics.com/wp-content/uploads/ENLIGHTEN-Manual-3.0.pdf)

For more information about ENLIGHTEN, please see the product home page on 
Wasatch Photonics' website:

- [ENLIGHTEN Homepage](https://wasatchphotonics.com/product-category/software/)

If you'd rather download pre-compiled installers for Windows, MacOS or Linux, find
the latest released versions here:

- [ENLIGHTEN Installers](https://wasatchphotonics.com/binaries/apps/enlighten/)

If you'd like to see the "rendered Doxygen" version of these pages, with the "dot 
graphs" converted into actual clickable / zoomable UML image-maps, and the "ref"
links expanded into active hypertext, click here:

- [Rendered Doxygen](https://wasatchphotonics.com/api/ENLIGHTEN/)

For more information about our GitHub source code distribution, read on...

# ENLIGHTEN Source Distribution

**ENLIGHTEN&trade;** (the registered [trademark](https://trademarks.justia.com/873/08/enlighten-87308319.html)
is in all-caps) is Wasatch Photonics' standard desktop GUI tool for controlling 
spectrometers, reading and graphing spectra, and performing basic analytic and 
utility tasks.

It is _not_ an advanced production or manufacturing platform for assembly,
alignment, focus, QC etc -- see WPSpecCal for those functions.

It is also not an end-all / be-all "perform everything you might ever want to
do with a spectrometer" tool -- if we were to invest in creating that, we 
probably wouldn't give it away for free :-)  (But give 
[Spectragryph](https://www.effemm2.de/spectragryph/) or 
[Panorama](https://www.labcognition.com/en/panorama.html) a try!)

ENLIGHTEN is committed to providing convenient graphical desktop support for
accessing, testing and controlling the most common functions supported by 
Wasatch Photonics spectrometers.  Some higher-level aggregate / analytic 
functions are left for customers or 3rd-party tools to provide, and our
[plug-in architecture](docs/PLUGINS.md) makes it simple for users to
extend ENLIGHTEN in countless ways we never imagined.

# Table of Contents

- [Contents](docs/CONTENTS.md) - overview of the distribution structure
- Development Environment Setup
    - [Windows](docs/BUILD_WINDOWS.md)
    - [Mac OS](docs/BUILD_MACOS.md)
    - [Ubuntu Linux](docs/BUILD_LINUX.md)
    - [Raspberry Pi](docs/BUILD_RPI.md)
- Developer Guides
    - [Architecture](docs/ARCHITECTURE.md)
    - [Plugins](docs/PLUGINS.md) 
    - [Maintenance](docs/MAINTENANCE.md)
    - [Documentation](docs/DOCUMENTATION.md)
    - [Testing](docs/TESTING.md)
- Technical Notes
    - [Qt](docs/QT.md)
    - [CSS](docs/CSS.md)
- [Backlog](docs/BACKLOG.md)
- [History](docs/HISTORY.md)
- [Changelog](CHANGELOG.md)
