# Architecture

This is a high-level overview of how ENLIGHTEN is structured.

I used to lead-off with a graphical diagram but it's grown a bit unwieldy and 
needs to be re-thunk. For now, get a quick sense from rendered 
[ENLIGHTEN history](https://wasatchphotonics.com/api/ENLIGHTEN/md_docs_2_h_i_s_t_o_r_y.html).

Note that all classes which start with a capital "Q" are part of Qt.

## Infrastructure

The following files and classes represent the overall skeletal structure and 
scaffolding of ENLIGHTEN "as a Qt GUI application". These are all the things
which are involved in bringing the program up and showing the initial (blank)
graph.

### enlighten.py

At its heart, ENLIGHTEN is a Python script. When you "run ENLIGHTEN," you are 
literally running scripts/enlighten.py.

(If you installed ENLIGHTEN from a compiled Windows installer, you may be running
a file called "enlighten.exe", but it's just the compiled form of this script.)

This script does these things:

- instantiates an [EnlightenApplication](#EnlightenApplication)
- parses command-line arguments
- tries to hide the Windows console window from the compiled .exe (used to work, currently broken)
- calls EnlightenApplication.run()

### EnlightenApplication

This class is just there to encapsulate state within Enlighten.py. Only one is ever 
created, and it was made a class for consistency and to simplify passing state
and arguments between methods.

It does these things:

- instantiates a QApplication, which will hold the "run loop"
- instantiates a [BasicWindow](#BasicWindow), which is the GUI you see on-screen (see below)
- instantiates a wasatch.applog, which handles all application logging
- throws up a pretty QSplashScreen for you to look at while everything else loads
- instantiates an [enlighten.Controller](#Controller), passing in all the above
- calls QApplication.exec(), which basically means "keep ticking all threads until your exit signal is raised"

Note that no particular method is called on the Controller. It doesn't have to, 
because the Controller constructor kicks off various threads which go and look 
for spectrometers to graph, and otherwise waits for you to click things on the 
GUI.

### BasicWindow

enlighten.ui.BasicWindow is an important class in constructing the GUI. It 
extends QMainWindow, meaning it is "the main window" of the runningQApplication.

The main thing it does is import [enlighten_layout](#enlighten_layout), 
which you will see referenced throughout the codebase as Controller.form.ui (or 
abbreviated as cfu).

### enlighten_layout

enlighten.assets.uic_qrc.enlighten_layout is the all-important file which defines
"the ENLIGHTEN GUI" -- all the QFrames, QPushButtons and pretty much everything 
you see on-screen.

The "source code" for this file is:

    enlighten/assets/uic_qrc/enlighten_layout.ui

It is literally an XML file, and often I do tweak it directly in the XML.

.ui files are normally editted using [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html).
Where that utility is installed on your system varies with OS and Qt version
and seems to change over time. Currently if using PySide6 and venv it lands
in VENV_ROOT/Scripts/pyside6-designer, and if not using venv (MacOS) /usr/local/bin.

(My one bit of advice regarding Designer is to watch some YouTube videos on
editing layouts, including breaking layouts. There's a reason I often cheat to 
the XML.)

This file gets "compiled" (converted) into enlighten_layout.py by 
[rebuild_resources.sh](#rebuild_resources.sh). It is that "Python" version of
the file which gets imported by [BasicWindow](#BasicWindow)
and referenced as Controller.form.ui.

### rebuild_resources.sh

If you're reading this straight-through, this is the right time to address 
scripts/rebuild_resources.sh.

A lot of Qt resources, including GUI icons and the all-important 
[enlighten_layout](#enlighten_layout), are editted / managed
as text files, and then converted into Python modules which can be imported and
referenced directly by Python code.

The conversion is performed by two programs which come as part of the PySide
distribution, rcc and uic (current names are pyside6-rcc and pyside6-uic).

The actual names and location of these programs varies from release to release,
and finding / obtaining them is historically one of the thornier bits of porting
ENLIGHTEN to a new OS.

This script needs to be run when:

- first cloning an ENLIGHTEN distribution 
- changing branches or going back to an earlier tag
- adding or editting any icons (.qrc)
- editing [enlighten_layout](#enlighten_layout)

It is a Bash script, which means you may have to run it different ways on different
operating systems (in a Git Cmd shell on Windows, I use "sh scripts\rebuild_resources.sh").

Note that PySide2 generated Python 2 source, which needed to be converted through 2to3.

### Controller

Fundamentally, the Controller is [now] responsible for four things:

1. Calls [BusinessObjects](#BusinessObjects) to instantiate a long list
   of "feature objects" which individually represent specific ENLIGHTEN features.
2. Instantiates a bunch of periodic QTimers that go off and do application-level
   things like monitor status. (Individual business objects may encapsulate their
   own internal QTimers for feature-specific things.)
3. Handles connection and initialization of newly-detected 
   [Spectrometer](#Spectrometer)s.
4. Polls connected spectrometers for new spectra to graph.

By and large, anything in the Controller which isn't in direct support of one of 
those things may be legacy from the original "everything goes into the Controller" 
architecture which simply hasn't been refactored out into business objects yet.

And I could see moving some of those things out too, to make things a little more
encapsulated in the future:

- Move bus_timer, connect_new, initialize_new_device, set_from_ini_file etc
  into a hypothetical enlighten.DeviceConnection class which is solely responsible
  for finding and connecting to new Spectrometers.
- Move attempt_reading, acquire_reading, update_scope_graphs, process_reading etc
  to a hypothetical enlighten.DataAcquisition.

### BusinessObjects

This class exists to make the Controller's constructor shorter. Basically it's just
encapsulating construction of all the various "feature objects" which individually
encapsulate specific application and spectrometer functions.

Note that we would probably benefit from an ABC (Abstract Base Class) enlighten.FeatureObject
with virtual methods like:

- update_visibility 
- init_hotplug (anything required when a new spectrometer is connected)
- register_observer
- close (prepare for application shutdown)

## Timing Loops

These are the major event timers that "tick" important ENLIGHTEN activities.

Note that QTimers call their "tick" function _on the GUI thread,_ meaning they
can do what they want with Qt widgets. In contrast, threading.Threads are not
on the GUI thread, and can't change Qt objects. This gets a little weird in
plugins. We should consider changing all threading.Threads to QThreads.

- ... (TBD)

## Device Connection

This is basically what happens when you connect a spectrometer.

The Controller has a QTimer called bus_timer. At 1Hz, it calls tick_bus_listener.
That function refreshes a list of visible USB and BLE spectrometers. It then calls
connect_new to see if any of the devices are "new" to the list, and if so, pick one
(ONE) and try to connect to it.

It attempts to connect to the device by passing the wasatch.DeviceID of the "new"
device to a new wasatch.WasatchDeviceWrapper and calling that object's connect()
method.

If WasatchDeviceWrapper.connect returns true, that indicates Wasatch.PY now has
an active wasatch.WrapperWorker object *running in a new thread.* 

The new WrapperWorker has a WasatchDevice. The WasatchDevice has a .hardware 
attribute which is usually a wasatch.FeatureIdentificationDevice (a Wasatch 
Photonics USB spectrometer supporting the "FID" protocol defined in ENG-0001), 
but sometimes may be a wasatch.AndorDevice or wasatch.BLEDevice or whatever).

After successful WasatchDeviceWrapper.connect(), the WasatchDeviceWrapper is 
handed to enlighten.device.Multispec, which is responsible for keeping track of 
all currently-connected spectrometers. Multispec uses the WasatchDeviceWrapper 
to instantiate an enlighten.device.Spectrometer.

Going forward, ENLIGHTEN will primarily communicate with the spectrometer through
the Spectrometer object, which will internally communicate through its
WasatchDeviceWrapper's WrapperWorker's WasatchDevice.

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

Note that the wasatch.WasatchDeviceWrapper is part of Wasatch.PY, but is 
instantiated by ENLIGHTEN's Controller in the main thread. The wasatch.WrapperWorker 
and "everything else" in Wasatch.PY is instantiated in the child thread.

enlighten.Spectrometer receives a "convenience handle" to wasatch.SpectrometerSettings, 
which was instantiated and populated down in Wasatch.PY, and passed back up through the
WrapperWorker.

## Data Acquisition

This is how ENLIGHTEN reads and processes spectral data:

...TBD

## Package Overview

In the following, important classes are in **bold** (fundamental to operation or
heavily-used).

### enlighten.ui

The enlighten.ui package contains classes controlling major aspects of the user interface.

- **Authentication:** handles when user "authenticates" with a password (ctrl-A)
- BasicDialog
- BasicWindow: used exclusively(?) by [enlighten_layout](#enlighten_layout)
- Clipboard: responsible for interacting with the OS _system_ clipboard for copy-paste (_not_ the set of Measurement thumbnails)
- Colors: encapsulates colors for graph traces
- DidYouKnowFeature: responsible for the pop-up tutorial at launch
- FocusListener: used in detecting when QLineEdit fields are changed
- GUI: utility methods relating to the GUI; should either grow or shrink
- GuideFeature: currently deprecated, idea is to interactively prompt user with "good spectroscopy practices" (think Microsoft's "Clippy")
- HelpFeature: responsible for online help
- ImageResources: used to access the various icons and images compiled-in from .rc files via rcc
- **Marquee:** responsible for the "message bar" at the top of the screen
- MouseWheelFilter: prevents "mouse-wheel" events from affecting QVerticalSliders
- **PageNavigation:** used for moving between Views (Scope, Settings, Hardware, Log, Factory) and Modes (Raman, Non-Raman, Expert)
- ResourceMonitorFeature: added to track down a memory leak
- ScrollStealFilter: helps detatch "mouse-wheel" events from accidentally scrolling QSpinBoxes and QComboBoxes
- Sounds: encapsulates ENLIGHTEN's (currently-limited) array of sound effects
- **StatusBarFeature:** responsible for the configurable status bar at the bottom of the scope, showing spectral max, temperature, battery, etc
- **StatusIndicators:** responsible for the 3 "virtual LEDs" at the bottom-right of the screen (hardware, laser, temperature)
- **Stylesheets:** convenient access to CSS files for recoloring and styling widget appearance
- **ThumbnailWidget:** responsible for creating the miniature graph "thumbnails" along the left-hand ENLIGHTEN "Clipboard", and responding to button events
- TimeoutDialog
- **VCRControls:** responsible for the "VCR control" buttons atop the control palette (Play/Pause, Stop, Save, Step, Step-and-Save)

### enlighten.device

This package contains classes which track state of individual spectrometers, 
including stateful features corresponding to hardware features implemented in the
firmware of the spectrometer itself.

- AccessoryControlFeature: not currently used; created for 220190 / 220290 USB boards with OEM Accessory Conector
- AmbientTemperatureFeature: used for boards with ambient thermistor (typically STM32 ARM)
- BatteryFeature: used on XS spectrometers with batteries
- DetectorTemperatureFeature: used on Regulated and Cooled spectrometers with a detector TEC
- **EEPROMEditor:** used to display EEPROM contents (if not authenticated), or edit them (if logged-in)
- EEPROMWriter: encapsulates function to send an EEPROM to Wasatch.PY for writing to non-volitile storage
- ExternalTriggerFeature: 
- GainDBFeature: control gain (dB) in XS spectrometers
- HighGainModeFeature: toggle high-gain mode on InGaAs spectrometers
- **IntegrationTimeFeature:** control integration time
- **LaserControlFeature:** control laser (dis/enable and power via PWM)
- LaserTemperatureFeature: monitor laser temperature and (if supported) control setpoint
- LaserWatchdogFeature: configure / enable laser watchdog on XS spectrometers
- MultiPos: experimental class to support spectrometers with multiple grating positions
- **Multispec:** encapsulate management, selection, display and settings across multiple connected spectrometers
- RegionControlFeature: experimental class to support multiple ROI on 2D detectors
- **Spectrometer:** standard class to control and encapsulate settings/state 
  for a single spectrometer; contains .settings (SpectrometerSettings) and 
  .app_state (SpectrometerApplicationState)
- **SpectrometerApplicationState:** holds state relating to a single spectrometer
  which is only relevant to the ENLIGHTEN application (as opposed to the driver-level 
  SpectrometerSettings, EEPROM and SpectrometerState of Wasatch.PY, which are 
  applicable to _any_ spectrometer user and are not "ENLIGHTEN-specific")

### enlighten.post_processing

This package contains classes used to post-process raw spectra received from 
spectrometers.

- AbsorbanceFeature
- AutoRamanFeature
- BaselineCorrection
- BoxcarFeature
- DarkFeature
- DespikingFeature
- ElectricalDarkCorrectionFeature
- HorizROIFeature
- InterpolationFeature
- RamanIntensityCorrection
- ReferenceFeature
- RichardsonLucy
- ScanAveragingFeature
- TakeOneFeature
- TransmissionFeature

### enlighten.scope

This package contains classes relating to the primary on-screen graph in Scope 
view (more-or-less).

- Cursor
- EmissionLamps
- **Graph:**
- GridFeature
- PresetFeature
- RamanShiftCorrectionFeature

### enlighten.measurement

This package contains classes involved in saving and graphing individual spectra.

- AreaScanFeature
- **Measurement:**
- **MeasurementFactory:**
- **Measurements:**
- **SaveOptions:**

### enlighten.file_io

This package contains classes relating to file storage other than spectral measurements (handled in [Measurements](#measurement).

- **Configuration:**
- FileManager
- HardwareFileOutputManager
- LoggingFeature

### enlighten.data

These are classes that provide structured hard-coded data for use by the 
application. Any or all of them could have been represented by JSON files to load
at startup (like the ASTM file for Raman Wavenumber Correction). I have no strong
opinion on which is better.

- ColorNames: a list of named RGB shades that seemed handy (probably not needed)
- ModelFWHM: probably used to provide default optical resolution for older units before that was calibrated in the EEPROM
- ModelInfo: metadata about WP models that can't be readily inferred from the EEPROM

### enlighten.network

Classes and files used for network communication. (Not a big thing in ENLIGHTEN to date.)

- BLEManager: connect to BLE spectrometers (hasn't been tested in awhile)
- CloudManager: connect to AWS to download XL (Andor) virtual EEPROM files
- UpdateChecker: check for ENLIGHTEN updates? I forgot this was here. Probably isn't working...
- awsConnect: probably used with CloudManager? dunno
- keys: this file is not checked into the distribution, but must be present when building installers for AWS to work

### enlighten.parser

These are classes used in loading spectra files.

- ColumnFileParser: loads column-ordered single-measurement CSV files generated from the "Save" button
- DashFileParser: loads the older row-ordered CSV files used by Dash (ENLIGHTEN's predecessor)
- ExportFileParser: loads the column-ordered "export" multi-measurement CSV files generated from the "Export" button
- SPCFileParser: loads Thermo-Galactic GRAMS .SPC files
- TextFileParser: loads dirt-simple 2-column x/y files

### enlighten.timing

These are classes used to control (or monitor) measurement timing.

- **BatchCollection:** used to configure autonomous measurement "Batches" at some interval, with configured actions to occur before and after each measurement (or each batch)
- Ramp: not currently used?
- RollingDataSet: a data collection which automatically maintains a "moving window" and "current moving average," used for smoothing noisy readings like detector or laser temperature

### enlighten.factory

These are features only available on the password-protected "Factory" view, not 
normally visible on the GUI.

- DFUFeature: put an ARM-based spectrometer (XS) into DFU (Device Firmware Update) mode
- FactoryStripChartFeature: generate "strip-charts" (a single scalar graphed over
  "time" as the x-axis) for detector temperature, laser temperature, battery etc

### enlighten.Plugins

Classes related to plug-ins, from ENLIGHTEN's side. Note that [plugins](#plugins) is a different namespace (below).

- **PluginController:** primary controller for all plugins
- PluginFieldWidget: a single GUI field (either output or input) generated by a 
  plugin (may be str/QLineEdit, bool/QCheckbox, ComboBox etc); maps to exactly 
  one plugins.EnlightenPluginField object
- PluginGraphSeries: a graph trace generated by a plugin for display on primary or plugin graph
- PluginModuleInfo: Python metadata about a dynamically imported plugin (Python module)
- PluginValidator: class to validate plugin configuration, fields etc at load time
- PluginWorker: for plugins which run in their own thread, the interface between PluginController and the plugin
- TableModel: for plugins which generate a Pandas DataFrame, used to display scrollable table in Qt

### plugins

Some points about this directory:

- plugins/ is currently a directory, _not_ a package. What's the difference?
    - If you look in the PYTHONPATH set in scripts/bootstrap.bat and various 
      build instructions, it includes both "." (the repo root, parent of 
      ./enlighten/Controller.py) and "plugins". 
    - That was arguably a mistake; we could remove "plugins" from our PYTHONPATH,
      which would make "plugins" a package under the repo root, just like 
      "enlighten" is a package. 
        - This would change the current EnlightenPlugin module into 
          plugins.EnlightenPlugin, and Prod.EmissionLines into 
          plugins.Prod.EmissionLines.
        - We would then need to change the import statement in PluginController 
          to "from plugins.EnlightenPlugin import *".
        - I have no strong opinion on this.
- There is only one module (.py file) in this package (directory) which is 
  automatically imported by ENLIGHTEN: EnlightenPlugin
- Every other directory under plugins/ is treated as a top-level package
  (Prod, Raman, RnD, OEM etc)
- Within a single package directory, every *.py file is assumed to be
  an ENLIGHTEN plugin (so ./plugins/Raman/RamanLines.py is the plugin
  Raman.RamanLines).
- If you want to stick random files with different extensions in those
  directories that's fine; PluginController only scans for *.py files.
- If you have a "complex" plugin that would benefit from multiple files,
  even a whole directory tree of sub-classes, JSON configuration data and
  whatever, you're free to put additional subdirectories within packages.
      - That is, PluginController does not recursively "walk" ./plugins;
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

- EnlightenPluginBase: Abstract Base Class (ABC) for all plugins
- EnlightenPluginConfiguration: when a plugin is "connected" (instantiated and 
  loaded), its get_configuration method returns this back to the PluginController
  to configure GUI fields and other plugin features
- EnlightenPluginField: the back-end datatype and field configuration which generates an on-screen PluginFieldWidget 
- EnlightenPluginRequest: the Controller automatically passes new spectra (ProcessedReadings) to PluginController, which wraps them into EnlightenPluginRequests and sends them down through PluginWorker to the loaded plugin
- EnlightenPluginResponse: after a plugin has finished processing an EnlightenPluginRequest, it should return an EnlightenPluginResponse. The new "functional" plugin API does this automatically.
- EnlightenApplicationInfo: this can be be deprecated. It had been used when ENLIGHTEN was closed-source to provide a handful of key ENLIGHTEN attributes or methods that plugins could access. Now that they have their own handle to the Controller, it's moot.
