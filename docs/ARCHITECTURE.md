# Architecture

This file represents an "ENLIGHTEN 101" for new developers planning to work in 
the codebase.

_Note that all classes which start with a capital "Q" are part of Qt._

## Infrastructure

The following files and classes represent the overall skeletal structure and 
scaffolding of ENLIGHTEN "as a generic Qt GUI application" (irrespective of 
domain particulars like spectroscopy concepts or spectrometer hardware). 
Basically these are all the things which are involved in bringing the program up
and showing the initial (blank) graph.

### enlighten.py

At its heart, ENLIGHTEN is a Python script. When you "run ENLIGHTEN," you are 
literally running the script `scripts/enlighten.py`.

(If you installed ENLIGHTEN from a binary Windows installer, you may be running a
program called "enlighten.exe", but that's just the compiled form of this script.)

This script does these things:

- instantiates an [EnlightenApplication](#EnlightenApplication)
- parses command-line arguments
- tries to hide the Windows console window from the compiled .exe (currently broken)
- calls EnlightenApplication.run()

### EnlightenApplication

This class encapsulates state within `Enlighten.py`. Only one instance is ever 
created during an application session, and it was made a class for consistency 
and to simplify sharing state and arguments between methods.

It does these things:

- instantiates a `QApplication`, which will hold the "run loop"
- instantiates a [BasicWindow](#BasicWindow), which is the GUI you see on-screen
  (see below)
- instantiates a `wasatch.applog`, which handles all application logging
- displays a pretty `QSplashScreen` for you to look at while everything else loads
- instantiates a [Controller](#Controller), passing in all the above
- calls `QApplication.exec()`, which basically means "display the form and keep 
  ticking all threads until the form is closed"

Note that no particular method is called on the `Controller`. It doesn't have to, 
because the `Controller` constructor kicks off various threads (`QTimers`) which go 
and look for spectrometers to graph, poll data from previously-connected 
spectrometers, and otherwise wait for you to click things on the GUI.

### BasicWindow

`enlighten.ui.BasicWindow` is an important class in constructing the GUI. It 
extends `QMainWindow`, meaning it is "the main window" of the running
`QApplication`.

The main thing it does is import [enlighten_layout](#enlighten_layout), 
which you will see referenced throughout the code-base as `Controller.form.ui` 
(sometimes abbreviated as `cfu`).

### enlighten_layout

`enlighten.assets.uic_qrc.enlighten_layout` is the all-important file which defines
"the ENLIGHTEN GUI" -- all the `QFrames`, `QPushButtons` and pretty much everything 
you see on-screen.

The "source code" for this file is:

    enlighten/assets/uic_qrc/enlighten_layout.ui

It is literally an XML file, and often I do tweak it directly in the XML.

.ui files are normally edited using [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html).
The path at which that utility is installed on your system varies with OS and Qt
version and seems to change over time. Currently if using PySide6 and `venv` it 
lands in `VENV_ROOT/Scripts/pyside6-designer`. If not using `venv`, it could be in
`/usr/local/bin` (at writing on MacOS).

(My one bit of advice regarding Designer is to watch some YouTube videos on
"Qt designer layouts", including breaking layouts. There's a reason I often cheat
to the XML.)

This file is converted into `enlighten_layout.py` by 
[rebuild_resources.sh](#rebuild_resources.sh). It is that "Python" version of
the file which gets imported by [BasicWindow](#BasicWindow)
and referenced as `Controller.form.ui`.

#### CSS

Note that `enlighten_layout.ui` contains a large CSS stylesheet at the top
of the XML. 

**DO NOT EDIT THIS STYLESHEET.** 

Instead, edit the file `enlighten/assets/stylesheets/dark/enlighten.css`. 
`rebuild_resources.sh` calls another script (`embed_stylesheet.sh`) to 
automatically update the stylesheet in `enlighten_layout.ui` with the one from 
`enlighten.css`.

### rebuild_resources.sh

If you're reading this straight-through, now is the right time to address 
`scripts/rebuild_resources.sh`.

A lot of Qt resources, including GUI icons and the all-important 
[enlighten_layout](#enlighten_layout), are edited / managed as text files, and 
then converted into Python modules which can be imported and referenced directly
by Python code.

The conversion is performed by two programs which come as part of the PySide
distribution, `rcc` and `uic` (current names are `pyside6-rcc` and `pyside6-uic`).

The actual names and location of these programs varies from release to release,
and finding / obtaining them is historically one of the thornier bits of porting
ENLIGHTEN to a new OS.

This script needs to be run when:

- first cloning an ENLIGHTEN distribution 
- changing branches or going back to an earlier tag
- adding or editting any icons (.qrc)
- editing [enlighten_layout](#enlighten_layout)
- editing `enlighten.css`

It is a Bash shell script, which means you may have to run it different ways on 
different operating systems (in a Git Cmd shell on Windows, I use 
`sh scripts\rebuild_resources.sh`).

Note that PySide2 generated Python 2 source, which needed to be converted through
`2to3`.

### Controller

Fundamentally, the `enlighten.Controller` is responsible for four things:

1. Calls [BusinessObjects](#BusinessObjects) to instantiate a long list
   of "feature objects" which individually represent specific ENLIGHTEN features.
2. Instantiates a bunch of periodic `QTimers` that go off and do application-level
   things like monitor status. (Individual business objects may encapsulate their
   own internal `QTimers` for feature-specific things.)
3. Handles connection and initialization of newly-detected [Spectrometer](#Spectrometer)s.
4. Polls connected spectrometers for new spectra to graph.

By and large, anything in the `Controller` which isn't in direct support of one of 
those things may be legacy from the original "everything goes into the Controller" 
architecture which simply hasn't been refactored out into business objects yet.

This "refactor" is not yet done, and there remain more things we might extract 
out of the `Controller`, to improve encapsulation, readability and maintainability:

- Move `bus_timer`, `connect_new`, `initialize_new_device`, `set_from_ini_file` 
  etc into a hypothetical `enlighten.DeviceConnection` class which is solely 
  responsible for finding and connecting to new `Spectrometers`.
- Move `attempt_reading`, `acquire_reading`, `update_scope_graphs`, 
  `process_reading` etc to a hypothetical `enlighten.DataAcquisition`.

### BusinessObjects

`enlighten.BusinessObjects` exists to make the `Controller`'s constructor 
shorter.  Basically it's just encapsulating construction of all the various 
"feature objects" which individually encapsulate specific application and 
spectrometer functions.

Note that we would probably benefit from an ABC (Abstract Base Class) 
`enlighten.FeatureObject` with virtual methods like:

- `update_visibility`
- `init_hotplug` (anything required when a new `Spectrometer` is connected)
- `register_observer`
- `close` (prepare for application shutdown)

## Timing Loops

These are the major event timers that "tick" important ENLIGHTEN activities.

Note that `QTimers` call their "tick" function _on the GUI thread,_ meaning they
can do what they want with Qt widgets. In contrast, `threading.Threads` are not
on the GUI thread, and can't change Qt objects. This gets a little weird in
plugins. 

**We should consider changing all `threading.Threads` to `QThreads`.**

- `Controller.bus_timer` (~1Hz) - checks for newly-connected USB spectrometers, 
  newly discovered BLE spectrometers, and unplugged (missing) spectrometers
- `Controller.hard_strip_timer` - drives the "strip-charts" in the Factory view
  (`QTimer` should be encapsulated into `StripChartFeature`)
- `Controller.acquisition_timer` (~10Hz) - polls each connected `Spectrometer` for 
  latest spectrum. Note this means that, **regardless of integration time or
  USB speed or anything else, ENLIGHTEN does not read or graph spectra faster
  than 10Hz.** That is deliberate and in line with its human-centric performance
  goals.
- `Controller.status_timer` (~1Hz) - checks memory usage, sends a heartbeat to
  each `Spectrometer` (probably unneeded now that we're multithreaded), polls
  for any "status messages" flowed back from 'Spectrometer` threads, updates
  laser status display, checks for any asynchronous plugin responses, and ticks
  KnowItAll.

Other BusinessObjects encapsulate internal `QTimers` for their own purposes,
including:

- `enlighten.ui.Marquee` encapsulates its own `QTimer` to decide when to hide 
  messages and `Toasts`
- `enlighten.ui.GuideFeature` has a `QTimer` which probably isn't used ATM
- `enlighten.measurement.AreaScanFeature` has a `QTimer` to show its own
  `QProgressBar` (and should probably be moved to `ui` or `factory`)
- `enlighten.Plugins.PluginController` has a `QTimer` used in auto-loading a
  plugin at startup
- `enlighten.file_io.LoggingFeature` uses a `QTimer` to update the scrolling 
  colorized view on the logfile
- `enlighten.file_io.FileManager` uses a `QTimer` to spread-out large load 
  operations (when a hundred measurements are being loaded at once) over time
- `enlighten.timing.BatchCollection` uses one `QTimer` for batches, and a 
  separate one for measurements within a batch

Note that most `QTimers` are configured as "SingleShot" deliberately, meaning
they complete a tick, _then_ schedule their next tick after a fixed "sleep"
time. That means bus_timer for instance isn't really 1Hz, because ticks don't
_start_ at 1-sec intervals, but rather the next tick _starts_ 1sec after the
previous tick _ended._ This is deliberate and makes it impossible for any tick 
to ever extend into another, and helps the application gracefully adapt to 
increased load / slower CPUs / multiple spectrometers.

## Device Connection

This is basically what happens when you connect a spectrometer:

The `Controller` has a `QTimer` called `bus_timer`. At 1Hz, it calls `tick_bus_listener`.
That function refreshes a list of visible USB and BLE spectrometers. It then calls
`connect_new` to see if any of the devices are "new" to the list, and if so, pick one
_(one)_ and try to connect to it.

It attempts to connect to the device by passing the `wasatch.DeviceID` of the "new"
device to a new `wasatch.WasatchDeviceWrapper` and calling that object's `connect()`
method.

If `WasatchDeviceWrapper.connect` returns true, that indicates Wasatch.PY now has
an active `wasatch.WrapperWorker` object _running in a new thread._

The new `WrapperWorker` has a `WasatchDevice`. The `WasatchDevice` has a `.hardware`
attribute which is usually a `wasatch.FeatureIdentificationDevice` (a Wasatch 
Photonics USB spectrometer supporting the "FID" protocol defined in ENG-0001), 
but sometimes may be a `wasatch.AndorDevice` or `wasatch.BLEDevice` or whatever).

After successful `WasatchDeviceWrapper.connect()`, the `WasatchDeviceWrapper` is 
handed to `enlighten.device.Multispec`, which is responsible for keeping track of 
all currently-connected spectrometers. `Multispec` uses the `WasatchDeviceWrapper`
to instantiate an `enlighten.device.Spectrometer`.

Going forward, ENLIGHTEN will primarily communicate with the spectrometer through
the `Spectrometer` object, which will internally communicate through its
`WasatchDeviceWrapper`'s `WrapperWorker`'s `WasatchDevice`.

Conceptually, for any one spectrometer:

     _____________________________________________________   _______________________________________________
    |____________________Child_Thread_____________________| |__________________Main_Thread__________________|
     _______________________________________________________________________________   _____________________
    |________________________________Wasatch.PY_____________________________________| |______ENLIGHTEN______|
                                                                                               ____________
                                                                                              |_Controller_|
                                                                                                    | has-a 
                                       __________________                                      _____v______ 
                                      |_threading.Thread_|                                    |_Multispec__|
                                                  /\                                                | has-many      
                                                  \/          ______________________   has-a  ______v_______
                                              is-a|          |_WasatchDeviceWrapper_|<-------|_Spectrometer_|
                                            ______|________     |                                   |
                                           |_WrapperWorker_|<---' has-a                             | convenience
                                                  | has-a                                           | handle
                                           _______v_______                                          |
                                          |_WasatchDevice_|                                         |
                   _____________________________  |   |  ______________________                     |
                  |_FeatureIdentificationDevice_|-+   +-|_SpectrometerSettings_|<-------------------'
                                   _____________  |        |  ________
                                  |_AndorDevice_|-+        +-|_EEPROM_|
                                     ___________  |        |  ___________________
                                    |_BLEDevice_|-+        +-|_SpectrometerState_|
                                                  |
                                                 etc

Note that the `wasatch.WasatchDeviceWrapper` is part of Wasatch.PY, but is 
instantiated by ENLIGHTEN's `Controller` in the main thread. The `wasatch.WrapperWorker`
and "everything else" in Wasatch.PY is instantiated in the child thread.

`enlighten.Spectrometer` receives a "convenience handle" to `wasatch.SpectrometerSettings`, 
which was instantiated and populated down in Wasatch.PY, and passed back up through the
`WrapperWorker`.

### Multi-Process Legacy

If some of the above seems a little overly complex and heavy-handed, you're right.
Part of that is because ENLIGHTEN was originally designed as a _multi-process_ 
rather than _multi-threaded_ application. That meant that everything which passed
between the "spectrometer process" and the "GUI process" (or the "logging process")
had to be _pickled._ That also meant no (easy) "shared memory" or shared object
handles.

One obvious part of that multi-process "pickling" architecture meant that most 
spectrometer settings are set by ENLIGHTEN as key-value pairs, where the key
is a string ("integration_time_ms") and the value is a Python-native scalar (400).
Such tuples were easy to pickle and send across `multiprocessing.Queues`.

Also, at some point we turned every `FeatureIdentificationDevice` method response 
into a `SpectrometerResponse`. That was done in an attempt to provide a "wrapping
message frame" which could stream error responses and other metadata back 
upstream to ENLIGHTEN. That has grown unnecessarily bulky and could be made much
more lightweight.

Now that ENLIGHTEN is properly multi-threaded, Some of this could definitely be 
simplified and cleaned-up, we just haven't yet taken the time.

## Data Acquisition

This is how ENLIGHTEN reads and processes spectral data:

As described above, when a spectrometer is connected, it gets its own 
`wasatch.WrapperWorker` whose `run` method is running in a new thread.
That `run` method has an infinite loop, which continually does the following:

1. generates and applies a [dedupped](#Dedupping) queue of new settings
2. checks to see if any of the applied commands failed in a way that would
   indicate serious hardware / firmware failure and we should disconnect
   the spectrometer
3. sends an "acquire_data" `SpectrometerRequest` into the `connected_device`
   (typicall a `WasatchDevice`, though could be `AndorDevice`, `OceanDevice`, 
   `BLEDevice`, `SPIDevice` etc).

...the more I look into this, the more I realize the current state of
data acquisition in ENLIGHTEN / Wasatch.PY is a nightmare. There are numerous
classes containing out-of-date documentation. This section of the architecture
does indeed need documenting, but rather than just documenting "what currently 
happens" in this ARCHITECTURE.md file, we need to take the time to update the
class and method documentation across Wasatch.PY itself.

**...TO BE CONTINUED...**

### Dedupping

ENLIGHTEN does not send every command the user clicks downstream. Since the 
spectrometer is operating in "free-running" mode, and new settings are only 
applied "between" spectra, we only bother to apply "the most-recent" command of 
any given type.

Say that, since the last integration (1000ms ago), the user repeatedly hammered 
the "integration time" down-arrow, changing to values 999, 998, all the way down
to 974ms. When we're next ready to apply new settings to the spectrometer, we
only bother to send the most-recent tuple ("integration_time_ms", 974), and 
discard the others.

## GUI Philosophy

### Views

ENLIGHTEN has a pull-down menu offering five operational Views. Fundamentally 
none change behavior, just which "screen" or "page" is being shown. 

Note that in `enlighten_layout.ui`, all five screens are "stacked" in the Z-axis
in one big `QStackedWidget`, and all `enlighten.ui.PageNav` does is move the 
selected page to top.

- **Scope:** main real-time live spectral graph
- **Settings:** ENLIGHTEN application settings
- **Hardware:** `EEPROMEditor` mostly, plus firmware versions and some other bits at the bottom
- **Log:** honestly not often used; scrolling color-coded "tail" of enlighten.log
- **Factory:** normally-hidden screen, enabled via `Authentication`, providing Area 
  Scan and some hardware strip-charts. Honestly, when all these features are 
  working well and reliably, we can enable Factory at default (or move some of
  these to Hardware).
    
### Operating Modes

If Views determine which "page" is shown, Mode determines which widgets are 
actually visible across those pages. There are currently three Modes, which were
selected more from use-case pragmatism and workflow optimization than any 
taxonomic completeness.

- **Raman:** features relevant to Raman measurements are visible; features mainly 
  used for non-Raman techniques are hidden. X-axis defaults to _wavenumber._
- **Non-Raman:** features relevant to non-Raman techniques like absorbance, 
  reflectance, transmission, emission, irradiance, color etc are visible; 
  features mainly used for Raman are hidden. X-axis defaults to _wavelength._
- **Expert** all features are visible; if the user wishes to perform Raman 
  absorbance or graph emission spectra in wavenumbers, it's assumed that they 
  know what they're doing. Also exposes additional controls that aren't normally
  visualized in either Raman or non-Raman mode, like laser TEC mode, or setting 
  laser power in duty cycle percentage rather than calibrated mW).

It will often be a matter of opinion as to whether a given feature should be 
hidden behind a password (like the Factory view), or require Expert mode (like 
Peak Sharpening), or removed from ENLIGHTEN proper and offered as a plugin. In 
different cases we have deliberately exercised all three options, in part "to 
show we can" (demonstrate different ways the application can be dynamically 
reconfigured to support different skill-levels and use-cases).

### Design Philosophy

Some random thoughts about why ENLIGHTEN was designed the way it was.

- **Performance:** ENLIGHTEN should prioritize "feeling fast" over "doing everything
  it possibly can." One way it does that is by ticking key loops at a languid 
  rate based on user-perception (considering that most monitors only refresh at 
  60Hz, and even movies are shot at 24fps), rather than maximizing 
  data-acquisition rate.
- **Cross-Platform:** Obviously most customers will use Windows, but supporting our 
  POSIX cousins is important to many customers. And developers...
- **Open-Source:** ENLIGHTEN is by-and-for scientists. We should prioritize openness
  and transparency.
- **Raw data:** we should always prefer offering unprocessed, raw data. We don't
  entirely do that right now (2x2 binning, dark pixel correction etc all happen
  automatically if configured in the EEPROM).
- **File formats:** first priority is to be able to open/load anything; I'm less
  worried about being able to save in every format. Our current CSV and Export
  formats are optimized for Excel; data analysts wishing to parse data in 
  scripts are encouraged to use the JSON format provided for that purpose.
- **Marquee:** this should ALWAYS be visible, so there is always a standard place to
  display status messages and alerts. It should not be animated in a way that 
  moves other controls, such that a user might mis-click on the wrong button.
- **Control Palette:** all standard spectrometer controls should be accessed from the
  scrolling palette to the right. It would be a valuable nice-to-have if users 
  could drag-and-move widgets up and down across the palette to their preferred 
  ordering (persisted in enlighten.ini).
- **StatusIndicators:** I guess the concept was that the three "virtual LEDs" at the
  bottom-right of the screen should show a quick "all is well" (green status) or
  "alert" indicators. I'm not sure the motif is entirely effective, and for a few
  years they were largely ignored, but we've recently tried to ensure their 
  coloration and tooltips are sensible.
- **StatusBar:** important scalar metrics (including hardware states relevant to the
  currently selected spectrometer) should be added as selectable options on the 
  StatusBar for quick reference.
- **Multispec:** ENLIGHTEN should theoretically be able to control up to 127 
  connected USB spectrometers in parallel. I think the current record is
  12 or 14. Note the "Lock" feature of Multispec, allowing you to simultaneously
  fire all their lasers, or change integration time en masse.
- **Help:** we have added MANY ways for ENLIGHTEN to actively teach / guide / nudge
  users toward spectroscopic best practices (DidYouKnow, Tooltips, WhatsThis, F1,
  GuideFeature etc). Most end-users won't know as much about spectroscopy as our
  best spectroscopists. ENLIGHTEN has a key role as a teaching tool to teach our
  users while they take spectra.
- **Palette:** we didn't pick "dark mode" to be cool -- in real spectroscopic labs,
  they work with the lights off and want as few bright light sources as possible;
  that includes laptop GUIs.
- **Skinnable:** the stylesheet hierarchy and "theme" options were provided to 
  encourage customization in student labs, helping to make spectroscopy "fun".
  (Yes this was a customer-requested feature.)

## Package Overview

In the following, important classes are in **bold** (fundamental to operation or
heavily-used).

### enlighten.ui

The enlighten.ui package contains classes controlling major aspects of the user interface.

- **`Authentication`**: handles when user "authenticates" with a password (ctrl-A)
- `BasicDialog`: is this even used?
- **`BasicWindow`**: used exclusively(?) by [enlighten_layout](#enlighten_layout)
- `Clipboard`: responsible for interacting with the OS _system_ clipboard for 
  copy-paste (_not_ the set of Measurement thumbnails)
- `Colors`: encapsulates colors for graph traces
- `DidYouKnowFeature`: responsible for the pop-up tutorial at launch
- `FocusListener`: used in detecting when QLineEdit fields are changed
- `GUI`: utility methods relating to the GUI; should probably either grow or shrink
- `GuideFeature`: currently deprecated, idea is to interactively prompt user with 
  "good spectroscopy practices" (think Microsoft's "Clippy")
- `HelpFeature`: responsible for online help
- `ImageResources`: used to access the various icons and images compiled-in from .rc files via rcc
- **`Marquee`**: responsible for the "message bar" at the top of the screen
- `MouseWheelFilter`: prevents "mouse-wheel" events from affecting QVerticalSliders
- **`PageNavigation`**: used for moving between Views (Scope, Settings, Hardware, 
  Log, Factory) and Modes (Raman, Non-Raman, Expert)
- `ResourceMonitorFeature`: added to track down a memory leak
- `ScrollStealFilter`: helps detatch "mouse-wheel" events from accidentally 
  scrolling QSpinBoxes and QComboBoxes
- `Sounds`: encapsulates ENLIGHTEN's (currently-limited) array of sound effects
- **`StatusBarFeature`**: responsible for the configurable status bar at the bottom
  of the scope, showing spectral max, temperature, battery, etc
- **`StatusIndicators`**: responsible for the 3 "virtual LEDs" at the bottom-right
  of the screen (hardware, laser, temperature)
- **`Stylesheets`**: convenient access to CSS files for recoloring and styling widget appearance
- **`ThumbnailWidget`**: responsible for creating the miniature graph "thumbnails"
  along the left-hand ENLIGHTEN "Clipboard", and responding to button events
- TimeoutDialog
- **`VCRControls`**: responsible for the "VCR control" buttons atop the control 
  palette (Play/Pause, Stop, Save, Step, Step-and-Save)

### enlighten.device

This package contains classes which track state of individual spectrometers, 
including stateful features corresponding to hardware features implemented in the
firmware of the spectrometer itself.

- `AccessoryControlFeature`: not currently used; created for 220190 / 220290 USB 
  boards with OEM Accessory Connector
- `AmbientTemperatureFeature`: used for boards with ambient thermistor (typically STM32 ARM)
- `BatteryFeature`: used on XS spectrometers with batteries
- `DetectorTemperatureFeature`: used on Regulated and Cooled spectrometers with a detector TEC
- **`EEPROMEditor`**: used to display EEPROM contents (if not authenticated), or 
  edit them (if logged-in)
- `EEPROMWriter`: encapsulates function to send an EEPROM to Wasatch.PY for writing
  to non-volitile storage
- `ExternalTriggerFeature`: not recently tested, as most models lack an external
  triggering connector
- `GainDBFeature`: control gain (dB) in XS spectrometers
- `HighGainModeFeature`: toggle high-gain mode on InGaAs spectrometers
- **`IntegrationTimeFeature`**: control integration time
- **`LaserControlFeature`**: control laser (dis/enable and power via PWM)
- `LaserTemperatureFeature`: monitor laser temperature and (if supported) control setpoint
- `LaserWatchdogFeature`: configure / enable laser watchdog on XS spectrometers
- `MultiPos`: experimental class to support spectrometers with multiple grating positions
- **`Multispec`**: encapsulate management, selection, display and settings across 
  multiple connected spectrometers
- `RegionControlFeature`: experimental class to support multiple ROI on 2D detectors
- **`Spectrometer`**: standard class to control and encapsulate settings/state 
  for a single spectrometer; contains .settings (SpectrometerSettings) and 
  .app_state (SpectrometerApplicationState)
- **`SpectrometerApplicationState`**: holds state relating to a single spectrometer
  which is only relevant to the ENLIGHTEN application (as opposed to the driver-level 
  SpectrometerSettings, EEPROM and SpectrometerState of Wasatch.PY, which are 
  applicable to _any_ spectrometer user and are not "ENLIGHTEN-specific")

### enlighten.post_processing

This package contains classes used to post-process raw spectra received from 
spectrometers.

- `AbsorbanceFeature`: used for Beer's Law absorbance (builds on TransmissionFeature)
- `AutoRamanFeature`: a software-driven autonomous "Raman Mode" (averaged dark, 
  laser enable, laser warmup, averaged sample, laser disable, dark subtraction)
- `BaselineCorrection`: wraps numerous baseline correction algorithms offered by 
  the open-source superman package
- `BoxcarFeature`: offers a moving-average convolution to smooth spectra at the 
  cost of broadened peaks
- `DarkFeature`: encapsulates dark-correction (aka ambient subtraction)
- `DespikingFeature`: experimental feature to remove cosmic rays; not currently 
  usable with Raman (should probably be a plugin at this point)
- `ElectricalDarkCorrectionFeature`: uses "optically masked" black pixels on the 
  edges of XS detectors to automatically subtract electrical readout noise
- `HorizROIFeature`: handles cropping the spectra to the configured horizontal 
  start/stop pixels
- `InterpolationFeature`: allows interpolating a spectrum to a fixed (regular 
  incremental) x-axis to ease comparison across units with different wavecals
- **`RamanIntensityCorrection`**: applies the y-axis intensity correction calibrated 
  with NIST SRM standards
- `ReferenceFeature`: similar to DarkFeature, responsible for the reference 
  measurement used in many non-Raman techniques
- `RichardsonLucy`: a [peak-sharpening deconvolution](https://en.wikipedia.org/wiki/Richardson%E2%80%93Lucy_deconvolution) 
  which reshapes peaks to closer to their "ideal" FWHM (experimental)
- `ScanAveragingFeature`: responsible for managing scan averaging; note that scan 
  averaging itself is currently performed in `wasatch.WasatchDevice`
- **`TakeOneFeature`**: a class responsible for taking a single, optionally averaged, 
  optionally laser-illuminated, optionally dark-corrected measurement from 
  ENLIGHTEN's perspective. Primarily used by `VCRControls`' "Step" and "Step-and-Save"
  buttons (taking a single measurement at a button click), `BatchCollection` 
  (taking a sequence of measurements at a defined interval), `AutoRamanMode` 
  (taking a single dark-corrected Raman `Measurement`). Basically, whereas most 
  of ENLIGHTEN was originally conceived to be "free-running," this was a means
  to support "operational oddballs" which wanted to work with individual 
  on-demand measurements. `wasatch.TakeOneRequest` was a recently-added 
  improvement to simplify specifying what features and settings were to be used 
  with an individual measurement. As with much soft clay, currently messy.
- `TransmissionFeature`: provides the basic processing used for both transmission 
  and reflectance measurements, and also the first stage of computing absorbance.

### enlighten.scope

This package contains classes relating to the primary on-screen graph in Scope 
view (more-or-less).

- `Cursor`: supports a single red vertical "cursor" which can be dragged back and 
  forth across the graph, providing the exact x-coordinate on the StatusBar and 
  y-coordinate on the widget. We should probably make _both_ coordinates optional
  fields on the StatusBar, and display both on the widget.
- `EmissionLamps`: not sure if this is actually used -- was for an earlier version
  with built-in wavelength calibration. That was deliberately removed so that all
  units would be calibrated through one process (WPSC). Most of what this provided
  is now available through plugins/Prod/EmissionLines anyway.
- **`Graph`**: encapsulates control of the center-screen graph, so was originally
  essentially a Singleton. More recently, I think it now also controls the optional 
  "Plugin" graph, meaning there may be two instances. Hasn't really been refactored
  to make that more obvious / convenient.
- `GridFeature`: AKA "Caleb's Feature", a quick shortcut to enable the graph grid
  (otherwise available by right-clicking on the pyqtgraph)
- `PresetFeature`: a new feature allowing the current settings of a half-dozen 
  "Feature" objects providing various acquisition parameters and post-processing
  options to be saved under a handy label (i.e. "Clear liquid vials", "White 
  powder stand-off" etc). Note that plug-ins can register too, such that plugin
  state can be instantly reset to one of several named presets.
- `RamanShiftCorrectionFeature`: responsible for applying 
  [ASTM E1840-96(2022)](https://www.astm.org/e1840-96r22.html), a session-level 
  x-axis offset correction which is deliberately not persisted to either EEPROM
  or enlighten.ini (and only affects the wavenumber axis, not wavelength).

### enlighten.measurement

This package contains classes involved in saving and graphing individual spectra.

- `AreaScanFeature`: responsible for the little-used and probably-broken ENLIGHTEN
  area scan image on the Factory view; should maybe be moved to `enlighten.factory`?
- **`Measurement`**: encapsulate a single measurement which has been saved to disk
  (optionally to multiple file extensions) with a `ThumbnailWidget` on the 
  scrolling "Clipboard".
- **`MeasurementFactory`**: responsible for generating new `Measurement` instances
- **`Measurements`**: encapsulates the set of all `Measurement` instances on the
  scrolling "Clipboard" (i.e., the set of `Measurement` objects which would be
  exported to a single file if "Export" was clicked).
- **`SaveOptions`**: the set of x-axes (pixel, wavelength, wavenumber) and
  `ProcessedReading` components (raw, dark, reference, processed) which should
  be saved in a new `Measurement`, along with the different output formats (CSV,
  JSON, SPC etc) desired

### enlighten.file_io

This package contains classes relating to file storage other than spectral 
measurements (handled in [Measurements](#measurement).

- **`Configuration`**: wraps `enlighten.ini`, the file responsible for persisting 
  various application settings across executions
- `FileManager`: general-purpose utilities for working with the external filesystem
- `HardwareFileOutputManager`: used when logging strip-charts (temperature, battery etc) to file
- `LoggingFeature`: although the logfile is primarily generated by `wasatch.applog`, 
  this class controls viewing and display of that logfile through ENLIGHTEN

### enlighten.data

These are classes that provide structured hard-coded data for use by the 
application. Any or all of them could have been represented by JSON files to load
at startup (like the ASTM file for Raman Wavenumber Correction). I have no strong
opinion on which is better.

- `ColorNames`: a list of named RGB shades that seemed handy (probably not needed)
- `ModelFWHM`: probably used to provide default optical resolution for older units
  before that was calibrated in the EEPROM
- `ModelInfo`: metadata about WP models that can't be readily inferred from the EEPROM

### enlighten.network

Classes and files used for network communication. (Not a big thing in ENLIGHTEN to date.)

- `BLEManager`: connect to BLE spectrometers (hasn't been tested in awhile)
- `CloudManager`: connect to AWS to download XL (Andor) virtual EEPROM files
- `UpdateChecker`: check for ENLIGHTEN updates? I forgot this was here. Probably not working...
- `awsConnect`: probably used with CloudManager? dunno
- `keys`: this file is not checked into the distribution, but must be present when
  building installers for AWS to work

### enlighten.parser

These are classes used in loading spectra files.

- `ColumnFileParser`: loads column-ordered single-measurement CSV files generated
  from the "Save" button
- `DashFileParser`: loads the older row-ordered CSV files used by Dash (ENLIGHTEN's
  predecessor)
- `ExportFileParser`: loads the column-ordered "export" multi-measurement CSV files
  generated from the "Export" button
- `SPCFileParser`: loads Thermo-Galactic GRAMS .SPC files
- `TextFileParser`: loads dirt-simple 2-column x/y files

_We need to add a DXFileParser._

### enlighten.timing

These are classes used to control (or monitor) measurement timing.

- **`BatchCollection`** used to configure autonomous measurement "Batches" at some
  interval, with configured actions to occur before and after each measurement 
  (or each batch)
- `Ramp`: not currently used?
- `RollingDataSet`: a data collection which automatically maintains a "moving 
  window" and "current moving average," used for smoothing noisy readings like 
  detector or laser temperature

### enlighten.factory

These are features only available on the password-protected "Factory" view, not 
normally visible on the GUI.

- `DFUFeature`: put an ARM-based spectrometer (XS) into DFU (Device Firmware Update) mode
- `FactoryStripChartFeature`: generate "strip-charts" (a single scalar graphed over
  "time" as the x-axis) for detector temperature, laser temperature, battery etc

### enlighten.Plugins

Classes related to plug-ins, from ENLIGHTEN's side. Note that [plugins](#plugins)
is a different namespace (below).

- **`PluginController`**: primary controller for all plugins
- `PluginFieldWidget`: a single GUI field (either output or input) generated by a 
  plugin (may be `str`/`QLineEdit`, `bool`/`QCheckbox`, `QComboBox` etc); maps to exactly 
  one `plugins.EnlightenPluginField` object
- `PluginGraphSeries`: a graph trace generated by a plugin for display on primary 
  or plugin graph
- `PluginModuleInfo`: Python metadata about a dynamically imported plugin (Python 
  module)
- `PluginValidator`: class to validate plugin configuration, fields etc at load time
- `PluginWorker`: for plugins which run in their own thread, the interface between
  `PluginController1 and the plugin
- `TableModel`: for plugins which generate a Pandas `DataFrame`, used to display 
  scrollable table in Qt

### plugins

Some points about this directory:

- `plugins/` is currently a directory, _not_ a package. What's the difference?
    - If you look in the `PYTHONPATH` set in `scripts/bootstrap.bat` and various 
      build instructions, it includes both "." (the repo root, parent of 
      `enlighten/Controller.py`) and `plugins`.
    - That was arguably a mistake; we could remove "plugins" from our `PYTHONPATH`,
      which would make "plugins" a package under the repo root, just like 
      "enlighten" is a package. 
        - This would change the current `EnlightenPlugin` module into 
          `plugins.EnlightenPlugin`, and `Prod.EmissionLines` into 
          `plugins.Prod.EmissionLines`, etc.
        - We would then need to change the import statement in `PluginController`
          to `from plugins.EnlightenPlugin import *`.
        - I have no strong opinion on this.
- There is only one module (.py file) in this package (directory) which is 
  automatically imported by ENLIGHTEN: `EnlightenPlugin`
- Every other directory under plugins/ is treated as a top-level package
  (Prod, Raman, RnD, OEM etc)
- Within a single package directory, every *.py file is assumed to be
  an ENLIGHTEN plugin (so `./plugins/Raman/RamanLines.py` is the plugin
  Raman.RamanLines).
- If you want to stick random files with different extensions in those
  directories that's fine; `PluginController` only scans for *.py files.
- If you have a "complex" plugin that would benefit from multiple files,
  even a whole directory tree of sub-classes, JSON configuration data and
  whatever, you're free to put additional subdirectories within packages.
      - That is, `PluginController` does not recursively "walk" ./plugins;
        it only scans for .py files within direct 1st-level subdirectories
        of ./plugins.
- Note that when installed on Windows, this whole directory tree gets copied to 
  EnlightenSpectra/plugins, so technically there is a runtime Python package tree 
  in the user's Documents folder.
    - That was so that plugin authors always have access to the _source code_ of
      their parent base class, and key objects they were expected to parse or 
      generate. 
    - Now that ENLIGHTEN itself is open-source, this makes less sense, and it 
      would be valid to consider moving the plugins.* classes under 
      enlighten.Plugins (physically and lexically).

That said, these are the classes currently defined within the EnlightenPlugin 
module:

- `EnlightenPluginBase`: Abstract Base Class (ABC) for all plugins
- `EnlightenPluginConfiguration`: when a plugin is "connected" (instantiated and
  loaded), its `get_configuration` method returns this back to the `PluginController` 
  to configure GUI fields and other plugin features
- `EnlightenPluginField`: the back-end datatype and field configuration which 
  generates an on-screen `PluginFieldWidget`
- `EnlightenPluginRequest`: the `Controller` automatically passes new spectra 
  (`ProcessedReadings`) to `PluginController`, which wraps them into 
  `EnlightenPluginRequests` and sends them down through `PluginWorker` to the 
  loaded plugin
- `EnlightenPluginResponse`: after a plugin has finished processing an 
  `EnlightenPluginRequest`, it should return an `EnlightenPluginResponse`. The 
  new "functional" plugin API does this automatically.
- `EnlightenApplicationInfo`: this can be be deprecated. It had been used when 
  ENLIGHTEN was closed-source to provide a handful of key ENLIGHTEN attributes or
  methods that plugins could access. Now that they have their own handle to the 
  `Controller`, it's moot.
