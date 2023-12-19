# Overview

We need to capture Order of Operations (OoO) somewhere, starting here.

This used to be reasonably straightforward and uncomplicated until we added 
Horizontal ROI (cropping) and Interpolation.  Those features introduced a lot of
new corner-cases that we didn't adequately think-through at introduction, and
which the legacy ENLIGHTEN measurement architecture of Reading and 
ProcessedReading didn't easily accommodate. In particular, we ended up with a
lot of (inconsistent) copy-pasted code, re-applying HorizROI and Interpolation
in different places (Controller.display, Measurement.save, Measurements.export, 
etc).

I'm trying to straighten some of that out now. In short, this is my current
vision.

## wasatch.Reading

Contains everything we read from the spectrometer (spectrum, temperatures, laser
state), with some modest driver-level corrections applied (even/odd fix, bin2x2,
bad pixel correction), optionally averaged.

## wasatch.ProcessedReading 

Retains handle to the original wasatch.Reading, plus adds these
key attributes:

- processed -- where we apply a series of transforms to the spectrum 
- raw -- basically a copy of Reading.spectrum
- dark -- whatever spectrum was used for dark correction, if any
- reference -- whatever spectrum was used for trans/refl/abs, if any

More recently, we now store a handle to the SpectrometerSettings used to
generate the ProcessedReading, as well as persistent copies of both the 
wavelengths and wavenumbers arrays. 

If enlighten.HorizROIFeature is enabled, it will add a .cropped
attribute to the ProcessedReading, which is itself another ProcessedReading
object with the cropped (shorter) processed, raw, dark, reference, 
wavelengths and wavenumbers arrays.

If enlighten.InterpolationFeature is enabled, it will add an .interpolated
attribute to the ProcessedReading, which again is itself another 
ProcessedReading object with the interpolated (may be longer or shorter)
versions of the (proc/raw/dark/ref/wl/wn) arrays. The assumption is that
if .cropped exists, then .interpolated was built from that, else it was
built from the original arrays.

Provides get_foo() accessors for all arrays (proc/raw/dark/ref/wl/wn), 
which follow the following precedence:

- .interpolated if found, else
- .cropped if found, else
- original arrays

In conclusion, the expectation is that Controller.process_reading will 
apply HorizROIFeature.process (generating .cropped if enabled), then
apply InterpolationFeature.process (generating .interpolated if enabled),
and that all subsequent processing (including Measurement.save, 
Measurements.export etc) should use the ProcessedReading getters.
