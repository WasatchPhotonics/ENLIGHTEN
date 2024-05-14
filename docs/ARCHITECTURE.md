# Architecture

This is a high-level overview of how ENLIGHTEN is structured.

I used to lead-off with a graphical diagram but it's grown a bit unwieldy and 
needs to be re-thunk. For now, get a quick sense from rendered 
[ENLIGHTEN history](https://wasatchphotonics.com/api/ENLIGHTEN/md_docs_2_h_i_s_t_o_r_y.html).

Note that all classes which start with a capital "Q" are part of Qt.

This document is organized as follows:

- [Infrastructure / Scaffolding](#Infrastructure)
    - [scripts/enlighten.py](enlighten.py)
    - [EnlightenApplication](#EnlightenApplication)
    - [BasicWindow](#enlighten.ui.BasicWindow)
    - [enlighten_layout](#enlighten.assets.uic_qrc.enlighten_layout)
    - [scripts/rebuild_resources.sh](#rebuild_resources.sh)
    - [Controller](#Controller)
    - [BusinessObjects](#BusinessObjects)
- [Device Connection](#Device Connection)
- [Data Acquisition](#Data Acquisition)
- [Package Overview](#Package Overview)
    - [enlighten.ui](#enlighten.ui)
    - [enlighten.device](#enlighten.device)
    - [enlighten.post_processing](#enlighten.post_processing)
    - [enlighten.scope](#enlighten.scope)
    - [enlighten.measurements](#enlighten.measurements)
    - [enlighten.file_io](#enlighten.file_io)
    - [enlighten.data](#enlighten.data)
    - [enlighten.network](#enlighten.network)
    - [enlighten.parser](#enlighten.parser)
    - [enlighten.timing](#enlighten.timing)
    - [enlighten.Plugins](#enlighten.Plugins)
    - [enlighten.factory](#enlighten.factory)

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
                   _____________________________  |        |   ________
                  |__________AndorDevice________|-+        +--|_EEPROM_|
                   _____________________________  |        |   ___________________
                  |___________BLEDevice_________|-+        +--|_SpectrometerState_|
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

In the following, important classes are in **bold**.

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
- Stylesheets: convenient access to CSS files for recoloring and styling widget appearance
- **ThumbnailWidget:** responsible for creating the miniature graph "thumbnails" along the left-hand ENLIGHTEN "Clipboard", and responding to button events
- TimeoutDialog
- **VCRControls:** responsible for the "VCR control" buttons atop the control palette (Play/Pause, Stop, Save, Step, Step-and-Save)

### enlighten.device

This package contains classes which track state of individual spectrometers, 
including stateful features corresponding to hardware features implemented in the
firmware of the spectrometer itself.

- AccessoryControlFeature
- AmbientTemperatureFeature
- BatteryFeature
- DetectorTemperatureFeature
- **EEPROMEditor:**
- EEPROMWriter
- ExternalTriggerFeature
- GainDBFeature
- HighGainModeFeature
- **IntegrationTimeFeature:**
- **LaserControlFeature:**
- LaserTemperatureFeature
- LaserWatchdogFeature
- MultiPos
- **Multispec:**
- RegionControlFeature
- **Spectrometer:**
- **SpectrometerApplicationState:**

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

- ColorNames
- ModelFWHM
- ModelInfo

### enlighten.network

- BLEManager
- CloudManager
- UpdateChecker
- awsConnect
- keys

### enlighten.parser

- ColumnFileParser
- DashFileParser
- ExportFileParser
- SPCFileParser
- TextFileParser

### enlighten.timing

- **BatchCollection:**
- Ramp
- RollingDataSet

### enlighten.factory

- DFUFeature
- FactoryStripChartFeature

### enlighten.Plugins

- **PluginController:**
- PluginFieldWidget
- PluginGraphSeries
- PluginModuleInfo
- PluginValidator
- PluginWorker
- TableModel
