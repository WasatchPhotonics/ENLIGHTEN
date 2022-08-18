# Backlog

## Hotplugs

- Better detection of "duplicate" spectrometers (same serial and same model, 
  different bus/addr, one "live" and one frozen) - delete the frozen one

## Mark

- Should exit faster with long integration times (1min+).  If there is no laser 
  (or no laser enabled), just kill child threads.
- more testing with Andor (multiple XL units, XL with others, etc)

## Architecture

Right now, most "background" activities are actually ticked by QTimers, _which 
fire in the GUI thread_.  This means that the GUI actually _freezes_ during these 
scheduled tasks.  It wasn't really noticable when the tasks were all quite short,
but when we added the External API, which can shuttle quite large volumes of data
around in queued requests and responses, it became apparent that the GUI grows
jerky during these activities (specifically, new spectra is not graphed).

The solution is to reduce utilization of QTimers for anything that might involve
significant processing, serialization, subprocess communications etc.  The most
likely replacement is probably a QThread, noting that these can't directly access
(change? read?) GUI widgets, so any GUI updates resulting from background 
QThreads would need to be dispatched to the GUI thread, probably using Signals 
(the mechanism Qt provides for this purpose), or perhaps thread-safe queues and 
the like.

## Misc

- Marquee methods should queue to a ticker so they aren't frozen during in connection events
- cursor should be tied to subpixel, not percentage of range
- highlight EEPROMEditor values when overridden by .ini or user
- Loaded measurements should have a LoadedXAxis object, which contains everything
  we were able to infer about the loaded spectrum.  If a loaded measurement doesn't
  have enough data to be displayed with the current x-axis, it should quietly 
  disappear, versus the current behavior (defaulting to pixel space regardless of
  selected x-axis).

## For Apps Eng

- add "Cancel" button for KnowItAll to kill long-running ID
- finish "despiking"

## For PM

- changed spectrometer settings not latching when single-stepping through spectra
  using pause / acquire buttons
- on first save, pop-up dialog saying where spectra is saved, and how to change

## Gratings Mfg requests

- click-to-place cursor
- update cursor intensity when moving cursor on paused spectra
- Make individual User Controls collapsible

## User Experience 

- Change Win10 [start tile background](https://www.askvg.com/tip-customize-start-screen-tiles-background-color-text-color-and-logo-in-windows-8-1/)
- Integrate with Microsoft Store to [distribute updates](https://developer.microsoft.com/en-us/windows/bridges/desktop)

## Maintenance 

- resolve "no libusb backend" in Git Bash
- port bootstrap.bat to use Git Bash

## Stretch Goals

- "check for updates"

## Offline Mode

Make ENLIGHTEN more useful without connected spectrometer.  Specifically:

Allow user to load or point to a set of spectra.  Could be a single file 
(multiple appended row-based spectra in one CSV) or a directory containing lots 
of single-file spectra (in either row or column CSV format).  Add a new checkbox
to Scope Setup page "[ ] loop" such that if checked, ENLIGHTEN will sequentially
load and process each spectrum in the file or directory over and over until the 
box is unchecked or the application exits.  

Note that this will also involve applying the saved x-axis from the loaded 
spectrum so that the correct wavelengths, wavenumbers etc are displayed; also, 
that the saved integration time is applied so that the spectra are streamed "at 
the expected rate" on-screen.  Basically, we want to make sure as many settings 
are loaded and re-used from the saved data as possible, but only those which make 
sense.  For instance, we would not want to re-apply boxcar smoothing to spectra 
which was already smoothed when it was saved.  

(Also, we'd want to be careful how we handled the laser: we obviously wouldn't 
want to fire the laser simply because the saved spectra showed the laser enabled
for Raman.  We might want to extend the current color scheme such that a "virtual" 
laser, which was being "replayed" from a saved session, lit the laser button in 
green rather than red...although that could confuse other people thinking the 
button color now indicated excitation wavelength. Just ignore the laser for now.)

This will allow us to record various interesting sessions (785 Raman of 
explosives, 1064 Raman of narcotics, UV-VIS absorbance of vodka, 
512-pixel NIR etc), and then replay and loop them at-will, 
testing different features against myriad different spectrometers 
without actually having access to the device (or laser, or sampling accessories,
or specific chemical compound).

Such functionality should be accessible from the command-line so that 
regression-tests can be run from scripts that point to specific files or 
directories of saved spectra.  (Better, .zip archives of such directories for a 
smaller footprint in our distribution.)  

We should then roll several representative datasets into our standard release so
that not only can any user run our tests, but potential sales customers can 
actually download and run "sample spectra" directly from an ENLIGHTEN install 
*without actually having a physical spectrometer*.  They would be able to 
"experience" what ENLIGHTEN and their spectrometer would do before buying one.  
