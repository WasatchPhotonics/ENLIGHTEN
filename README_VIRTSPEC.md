## Introduction

"Virtspec" is a short-name for [PyUsb-virtSpec](https://github.com/WasatchPhotonics/pyusb-virtSpec). 
It is a project, separate from Enlighten, that provides an imaginary spectrometer connected via USB.
It provides a bare-bones implementation of a spectrometer, including EEPROM and spectra, that is suitable for testing plugins or Measurements, for example.

It is not to be confused with virtSpec-GUI or MockDevice. Some old commits/branches/code may be talking about virtual spectrometers, but anything before 2023 
is not related to PyUSB-virtSpec. Likewise, anything virtspec 2023+ _is_ about PyUsb-virtSpec. Previous work on this topic should be deprecated due to timing and the 
fact that previous attempts at virtual devices involved modifying our own source programs. That added to architectural bloat and impeded both virtual and real 
device testing.

This module is intended for in-house testing, and while it is possible to produce a build containing it, I don't recommend that without careful consideration
and likely some additional engineering. When the virtual spectrometer is enabled, real ones are ignored (see pyusb-virtSpec's README for work-around). 
Obviously no real spectrometer needs to be connected in order to use the real one--the purpose is easy testing on the go.

The following is a guide on how to get started. It's mostly just cloning the repository in a folder next to Enlighten, but there's also a hint for using
virtSpec on an old (pre-2023) version of Enlighten.

## Local "Installation"
    
    pwd # path/to/Enlighten
    cd ..
    git clone git@github.com:WasatchPhotonics/pyusb-virtSpec.git

## Usage

Now "virtspec" can be added to the end of any bootstrap command.

```
scripts\bootstrap activate virtspec
```

To go back to using a real one:

```
scripts\bootstrap activate
```

## Note

Because of how it's kept outside of the Enlighten codebase, pyusb-virtspec will work with (probably) any version of Enlighten. To do so easily, you may want to patch the build script to your working tree:

```
git checkout <past version>
git checkout main scripts/bootstrap.bat
```
