# Architecture

This file represents an "ENLIGHTEN 101" for new developers planning to work in 
the codebase.

_Note that all classes which start with a capital "Q" are part of Qt._

## Infrastructure

The following files and classes represent the overall skeletal structure and 
scaffolding of ENLIGHTEN "as a generic Qt GUI application", irrespective of 
domain particulars like spectroscopy concepts or spectrometer hardware. 
Basically these are all the things which are involved in bringing the program up
and showing the initial (blank) graph.

Although this section is important for understanding how ENLIGHTEN is launched,
these files are almost never touched. Most actual day-to-day ENLIGHTEN development
occurs completely within EnlightenFeatures and EnlightenPlugins, so you can skip
ahead to there if you like.

### enlighten.py

At its heart, ENLIGHTEN is a Python script. When you "run ENLIGHTEN," you are 
literally running the script `scripts/enlighten.py`.

If you installed ENLIGHTEN from a binary Windows installer, you may be running an
executable called "enlighten.exe", but that's still just the same script after it 
got run through pyinstaller.

This script basically does this:

- parses command-line arguments
- instantiates an [EnlightenApplication](#EnlightenApplication)
- calls EnlightenApplication.run()

### EnlightenApplication

This class encapsulates state within `Enlighten.py`. Only one instance is ever 
created during an application session, and it was made a class for consistency 
and to simplify sharing state and arguments between methods.

It does these things:

- instantiates a `QApplication`, which will hold the "run loop"
- instantiates a [BasicWindow](#BasicWindow), which is the GUI you see on-screen
- instantiates a `wasatch.applog`, which handles all application logging
- displays a pretty `QSplashScreen` for you to look at while everything else loads
- instantiates a [Controller](#Controller), passing in handles to all the above
- calls `QApplication.exec()`, which basically means "display the form and keep 
  ticking all threads until the form is closed"

Note that no particular method is called on the `Controller`. It doesn't have to, 
because the `Controller` constructor kicks off various threads (`QTimers`) which go 
and look for spectrometers to connect, poll data from previously-connected 
spectrometers, and otherwise wait for you to click things on the GUI.

### BasicWindow

`enlighten.ui.BasicWindow` is an important class in constructing the GUI. It 
extends `QMainWindow`, meaning it is "the main window" of the running
`QApplication`.

The main thing it does is import [enlighten_layout](#enlighten_layout), 
which you will see referenced throughout the code-base as `ctl.form.ui` 
(sometimes abbreviated as `cfu`).

### enlighten_layout

`enlighten.assets.uic_qrc.enlighten_layout` is the all-important Python object 
which defines "the ENLIGHTEN GUI" -- all the `QFrames`, `QPushButtons` and pretty
much everything you see on-screen.

The "source code" for this file is:

    enlighten/assets/uic_qrc/enlighten_layout.ui

It is literally an ordinary XML file, and increasingly I just update it and add 
new GUI components directly within the XML.

.ui files can also be created and edited using 
[Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html).
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
of the XML. **DO NOT EDIT THE STYLESHEET IN THE .UI**

Instead, if you want to change the overall look-and-feel, edit the "master"
stylesheet `enlighten/assets/stylesheets/dark/enlighten.css`. This file gets
automatically prepended to `enlighten_layout.ui` during the build process, by
`rebuild_resources.sh` (via the script `embed_stylesheet.sh`).

Therefore, any edits you make to the CSS in `enlighten_layout.ui` will be 
automatically reset the next time you rebuild the GUI. To make permanent edits,
those need to be made in `enlighten.css`.

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
and finding / obtaining them can sometimes be challenging.

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

Happily, `rebuild_resources.sh` is now run _automagically_ (when necessary), by 
Samie's wonderful `scripts/bootstrap/win11/bootstrap.sh`, which is far and away 
the best way to run ENLIGHTEN at the moment.

### Controller

Okay, so we've talked about some XML and Bash...when do we get back to Python?

enlighten/Controller.py is the closest thing ENLIGHTEN has to a "main()". It was
named in the vein of "Model-View-Controller," and it's the big class which pretty
much kicks-off and runs everything else in the application.

Fundamentally, the `enlighten.Controller` is responsible for four things:

1. Calls [BusinessObjects](#BusinessObjects) to instantiate the lengthy (and
   growing!) list of EnlightenFeature objects which individually implement 
   specific ENLIGHTEN features.
2. Instantiates a handful of periodic `QTimers` that go off and do 
   application-level things like check for new spectrometers, read data from
   connected spectrometers, and update displays of battery, temperature and 
   the like.
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

This has become less important as we simplified business objects by giving
them all a handle to the Controller, and by having them all extend EnlightenFeature.

## Timing Loops

These are the major event timers that "tick" important ENLIGHTEN activities.

Note that `QTimers` call their "tick" function _on the GUI thread,_ meaning they
can do what they want with Qt widgets. In contrast, standard Python 
`threading.Threads` are _not_ on the GUI thread, and can't change Qt objects. 

This gets a little weird in plugins, as some plugin methods are called on the
GUI thread (`get_configuration`), while others aren't (`process_request`).

- `Controller.bus_timer` (~1Hz) - checks for newly-connected USB spectrometers, 
  newly discovered BLE spectrometers, and unplugged (missing) spectrometers.

- `Controller.hard_strip_timer` - drives the "strip-charts" in the Factory view
  (this `QTimer` should be moved into `StripChartFeature`)

- `Controller.acquisition_timer` (~20Hz) - polls each connected `Spectrometer` 
  for latest Reading. Note this means that, **regardless of integration time or
  USB speed or anything else, ENLIGHTEN does not read or graph spectra faster
  than 20Hz.** That is deliberate and in line with its human-centric performance
  goals.

- `Controller.status_timer` (~1Hz) - checks memory usage, sends a heartbeat to
  each `Spectrometer` (probably unneeded now that we're multithreaded), polls
  for any "status messages" flowed back from 'Spectrometer` threads, updates
  laser status display, checks for any asynchronous plugin responses, and ticks
  KnowItAll. _IMHO, LaserControlFeature, PluginController, KnowItAll etc should 
  all encapsulate their own timers and not lean on Controller for this._

Other BusinessObjects encapsulate internal `QTimers` for their own purposes,
including:

- `enlighten.ui.MarqueeFeature` encapsulates its own `QTimer` to decide when to 
  hide messages and `Toasts`

- `enlighten.ui.GuideFeature` has a `QTimer` which probably isn't used ATM

- `enlighten.measurement.AreaScanFeature` has a `QTimer` to show its own
  `QProgressBar` (and should probably be moved to `ui` or `factory`)

- `enlighten.Plugins.PluginControllerFeature` has a `QTimer` used in auto-loading
  a plugin at startup

- `enlighten.file_io.LoggingFeature` uses a `QTimer` to update the scrolling 
  colorized view on the logfile

- `enlighten.file_io.FileManagerFeature` uses a `QTimer` to spread-out large load 
  operations (when a hundred measurements are being loaded at once) over time

- `enlighten.timing.BatchCollectionFeature` uses one `QTimer` for batches, and a 
  separate one for measurements within a batch

- `enlighten.ui.CorrectionStatusFeature` uses one to dispatch GUI events

Note that most `QTimers` are configured as "SingleShot" deliberately, meaning
they complete a tick, _then_ schedule their next tick after a fixed "sleep"
time (or not). That means bus_timer for instance isn't really 1Hz, because ticks
don't _start_ at 1-sec intervals, but rather the next tick _starts_ 1sec after 
the previous tick _ended._ This is deliberate and makes it impossible for any 
tick to ever extend into another, and helps the application gracefully adapt to 
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

The new `WrapperWorker` has a `wasatch.InterfaceDevice`, which represents a high-
level abstract interface to a spectrometer of some type. Common InterfaceDevice
subclasses include:

- WasatchDevice (used by X, XM, XS and most Wasatch Photonics spectrometers)
- BLEDevice (used by Bluetooth XS spectrometers)
- AndorDevice (used by XL)
- IDSDevice (used for STARVIS prototypes)
- TCPDevice (used for WISP / LTS)
- OceanDevice (used for another vendor's spectrometers)
- etc

After successful `WasatchDeviceWrapper.connect()`, the `WasatchDeviceWrapper` is 
handed to `enlighten.device.Multispec`, which is responsible for keeping track of 
all currently-connected spectrometers. `Multispec` uses the `WasatchDeviceWrapper`
to instantiate an `enlighten.device.Spectrometer`.

Going forward, ENLIGHTEN will primarily communicate with the spectrometer through
the `Spectrometer` object, which will internally communicate through its
`WasatchDeviceWrapper`'s `WrapperWorker`'s `WasatchDevice`.

## Spectrometer Entity-Relationship Diagram

This is a conceptual Entity-Relationship diagram for where classes live 
(Wasatch.PY vs ENLIGHTEN) and run (child thread vs main thread) for any one
spectrometer:

     _____________________________________   _______________________________________________
    |____________Child_Thread_____________| |__________________Main_Thread__________________|
     _______________________________________________________________   _____________________
    |________________________Wasatch.PY_____________________________| |______ENLIGHTEN______|
                                                                                ____________
                                                                               |_Controller_|
                                                                                     | has-a 
                          __________________                                    _____v______ 
                         |_threading.Thread_|                                  |_Multispec__|
                                   /\                                                | has-many      
                                   \/          ______________________   has-a  ______v_______
                               is-a|          |_WasatchDeviceWrapper_|<-------|_Spectrometer_|
                             ______|________     |                                   |
                            |_WrapperWorker_|<---' has-a                             | convenience
                                   | has-a                                           | handle
                           ________v________                                         |
                          |_InterfaceDevice_|                                        |
                                   /\  |                                             |
                               is-a\/  | has-a                                       |
                  _______________  |   |  ______________________                     |
                 |_WasatchDevice_|-+   +-|_SpectrometerSettings_|<-------------------'
       _______________|________    |  _____________       |  ________
      |_FeatureInterfaceDevice_|---+-|_AndorDevice_|      +-|_EEPROM_|
                      ___________  |  ___________         |  ___________________
                     |_BLEDevice_|-+-|_TCPDevice_|        +-|_SpectrometerState_|
                      ___________  |  _____________
                     |_SPIDevice_|-+-|_OceanDevice_|

There a number of things worth observing about that diagram:

- `wasatch.WasatchDeviceWrapper` is part of Wasatch.PY, but is instantiated by 
  ENLIGHTEN's `Controller` in the main thread. The `wasatch.WrapperWorker` and 
  "everything else" in Wasatch.PY is instantiated in the per-spectrometer child 
  thread.

- `enlighten.Spectrometer` receives a "convenience handle" to 
  `wasatch.SpectrometerSettings`, which was instantiated and populated down in 
  Wasatch.PY, and passed back up through the `WrapperWorker`.

- ENLIGHTEN (Spectrometer) and Wasatch.PY aren't just re-using the same class
  definitions for SpectrometerSettings, SpectrometerState, EEPROM etc -- they
  are sharing the same object instances. Changes in one appear directly in the
  other. By and large, this is not deliberately done as a means of communication,
  but it could be. This is significant because up through ENLIGHTEN 2.4.3, the
  application was multi-process (not multi-threaded), and so each layer (driver
  and application) actually held different instances of the same class. This 
  legacy is still visible in some places.

- The relationship between WasatchDevice and FeatureInterfaceDevice is confusing,
  especially since both extend InterfaceDevice. This needs to be refactored.
  All other spectrometer types are implemented with a single FooDevice class
  (Andor, BLE, TCP, SPI etc). However, standard Wasatch Photonics spectrometers
  are unfortunately split across two classes (WasatchDevice and 
  FeatureInterfaceDevice) for historical reasons. WasatchDevice controls higher-
  level functions (scan averaging), and FeatureInterfaceDevice does the lower-
  level hardware communication. They can and should be merged. 

### Spectrometer Dataflow Diagram

There are five queues used to communicate across the four layers of spectrometer
communication:

        _____________________________________    __
       |_____________Controller______________|     |
         |          |          ^           ^       | main 
         |     _____v__________|_____      |       | thread
         |    |_WasatchDeviceWrapper_|     |     __|
         |          |          ^ settings  |
   alert |  command |          | queue     | message  
   queue |    queue |          | response  | queue   
         |          |          | queue     |        
         |       ___v__________|__         |     __
         |      |__WrapperWorker__|        |       |
         |          |          ^           |       | child
        _v__________v__________|___________|_      | thread
       |__________InterfaceDevice____________|   __|
        
Two queues go downward, from ENLIGHTEN to the InterfaceDevice:

- command_queue - (name, value) settings like integration_time_ms and laser_enable
- alert_queue (alert_name)) interrupts from ENLIGHTEN to cancel long-running blocking tasks

Three queues go upward from InterfaceDevice back to ENLIGHTEN:

- settings_queue (a single SpectrometerSettings object, confirming successful connection)
- response_queue (Readings, containing spectra, temperature, battery etc)
- message_queue (quick messages for the GUI and various EnlightenFeatures)

#### command_queue (downstream, ControlObject(name, value))

This is used to pass (name, value) settings from ENLIGHTEN to the spectrometer, like:

    - ("laser_enable", True)
    - ("integration_time_ms", 100)
    - ("vertical_roi", (350, 750))

These commands are ONLY applied (passed from WrapperWorker to InterfaceDevice)
BETWEEN acquisitions. A WrapperWorker is single-threaded, within its own thread,
and it only does one thing at a time. If it's taking a spectrum, then it sends
an ACQUIRE to the spectrometer, and it waits (blocks) until it gets the spectrum.

At that point it wraps the spectrum in a Reading object (along with battery,
temperatures, and other miscellaneous system state), and pushes the new
Reading back up the response_queue.

Only after sending the Reading, does WrapperWorker then look at any newly 
queued commands. Before passing them down to the Interface, WrapperWorker
"de-dupes" them. That is, if the user clicked the Integration Time down-arrow
5 times while the last measurement was being collected, generating 5 individual
integration_time_ms commands, WrapperWorker automatically discards all but the 
newest command of any given type (so as to not cause the InterfaceDevice to
send 5 redundant commands over USB or BLE or whatever).

#### alert_queue (downstream, str)

Alerts are a faster way ENLIGHTEN can notify Wasatch.PY about something
urgent, which otherwise would have been "blocked" by WrapperWorker's single-
threaded nature. The only alert currently implemented is from ENLIGHTEN's 
AutoRamanFeature, which can raise an "auto_raman_cancel" alert if the user
clicks "Stop" during a long-running (30sec+) Auto-Raman measurement because
they need to shutoff the laser.

Alerts are not currently (name, value). They each just have a name, and
any code in the InterfaceDevice can check to see if a given alert has been
raised (and can then clear it after responding).

As shown in the diagram, alerts bypass WrapperWorker, and are sent passed
instantly from WasatchDeviceWrapper (say, via an EnlightenFeature call to
enlighten.Spectrometer) to the associated alert_queue.

Long-running Wasatch.PY code, such as wasatch.AutoRaman or a get_spectrum()
call looping over timeouts while waiting for an external trigger, can read
the queue (check for alerts) at any time, even while "blocked" on a high-level
command or data collection process from WrapperWorker.

#### settings_queue (upstream, SpectrometerSettings)

This queue is only used exactly once per spectrometer connection, so arguably
it could be merged into response_queue or message_queue. However, it has 
different timeout behavior, so it's just as easy to keep it distinct.

This queue is used at initial spectrometer connection to indicate if a newly
detected spectrometer was successfully connected. If connection was successful,
the InterfaceDevice will pass-up a fully-populated SpectrometerSettings object
including a parsed EEPROM, rendered wavelength and wavenumber axes, SRM
correction factors and the works.

If connection fails, WrapperWorker will push up...something else. Looking at
the code, for various failure modes it could be None, could be a caught
exception, could be a SpectrometerResponse object with populated error_msg...
there's not a lot of consistency.

But basically, if it's anything other than SpectrometerSettings, something
went awry, and WasatchDeviceWrapper / Controller abort the connection.

Note that the passed SpectrometerSettings object, being passed by reference,
is thenceforth shared by both the InterfaceDevice in the child thread, and
ENLIGHTEN in the main thread. As this object contains the wavecal, all
calibrations, all EEPROM settings, and tracks dynamic SpectrometerState,
it is probably the single most important object in the application.

So yeah, it deserves its own Queue :-)

#### response_queue (upstream, Reading)

By far the busiest and highest-volume queue is the response_queue, which
carries wasatch.Reading objects up from Wasatch.PY into the Controller, where
they become wasatch.ProcessedReadings and represent the lifeblood of the
application.

Readings started as a place to hold a spectrum, but have grown over time
to include temperature data at the time of the measurement (detector temp,
laser temp, ambient temp, now even battery temp), battery charge state,
laser and interlock state...basically anything that ENLIGHTEN might want
to know about "what was going on at the time the spectrum was collected"
gets rolled into the Reading. 

If Area Scan is enabled, a Reading may include a wasatch.AreaScanImage,
which can include an entire frame of image data. 

If BatchCollection is enabled, in which a potentially complicated TakeOneRequest
was sent downstream by ENLIGHTEN, each Reading will be returned with a handle to
the original TakeOneRequest that generated it, so ENLIGHTEN's Controller will 
know which EnlightenFeature (or plugin?) requested that measurement.

This pipeline is pumped by InterfaceDevice.acquire_data(), which WrapperWorker 
essentially calls in an endless loop while a spectrometer is connected.

#### message_queue (upstream, StatusMessage(name, value))

This kind of the upstream equivalent of the downstream alert_queue, similarly
provided as a lightweight way for InterfaceDevices to flow-up quick status updates
to the Controller so the GUI can show timely progress indications even while 
blocked on long-running operations such as AutoRaman, scan averaging, etc.

At writing, according to Controller.process_status_message, these are the currently 
supported StatusMessage types:

- marquee_info
- marquee_error
- scan_averaging
- progress_bar (Auto-Raman)
- laser_status_indicators
- received_ble_firwmare_version
- firmware_log

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
