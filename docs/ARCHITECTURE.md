# Architecture

Click individual classes in the following diagram to access their individual
documentation pages.

\dot
    digraph enlighten_4_1 {
        label = "ENLIGHTEN 4.1.0"
        node [shape=box, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white, height=.25 ]
        style = filled
        fillcolor = white

        layout = twopi 
        overlap_scaling = 4
        overlap = prism

        /********************************* main *********************************/

        enlighten_py           [ fillcolor="aquamarine" label="scripts/Enlighten.py" ]
        EnlightenApplication   [ fillcolor="aquamarine" URL="\ref scripts.Enlighten.EnlightenApplication" ]
        Controller             [ fillcolor="aquamarine" URL="\ref enlighten.Controller.Controller" ]
        BusinessObjects        [ fillcolor="aquamarine" URL="\ref enlighten.BusinessObjects.BusinessObjects" ]
        common                 [ URL="\ref enlighten.common" ]
        util                   [ URL="\ref enlighten.util" ]

        enlighten_py -> EnlightenApplication -> Controller -> BusinessObjects

        /********************************** ui **********************************/

        Authentication         [ URL="\ref enlighten.ui.Authentication.Authentication" ]
        BasicDialog            [ URL="\ref enlighten.ui.BasicDialog.BasicDialog" ]
        BasicWindow            [ URL="\ref enlighten.ui.BasicWindow.BasicWindow" ]
        Clipboard              [ URL="\ref enlighten.ui.Clipboard.Clipboard" ]
        Colors                 [ URL="\ref enlighten.ui.Colors.Colors" ]
        ConfirmWidget          [ URL="\ref enlighten.ui.ConfirmWidget.ConfirmWidget" ]
        FocusListener          [ URL="\ref enlighten.ui.FocusListener.FocusListener" ]
        GUI                    [ URL="\ref enlighten.ui.GUI.GUI" ]
        GuideFeature           [ URL="\ref enlighten.ui.GuideFeature.GuideFeature" ]
        HelpFeature            [ URL="\ref enlighten.ui.HelpFeature.HelpFeature" ]
        ImageResources         [ URL="\ref enlighten.ui.ImageResources.ImageResources" ]
        Marquee                [ URL="\ref enlighten.ui.Marquee.Marquee" ]
        MouseWheelFilter       [ URL="\ref enlighten.ui.MouseWheelFilter.MouseWheelFilter" ]
        PageNavigation         [ URL="\ref enlighten.ui.PageNavigation.PageNavigation" ]
        ResourceMonitorFeature [ URL="\ref enlighten.ui.ResourceMonitorFeature.ResourceMonitorFeature" ]
        ScrollStealFilter      [ URL="\ref enlighten.ui.ScrollStealFilter.ScrollStealFilter" ]
        Sounds                 [ URL="\ref enlighten.ui.Sounds.Sounds" ]
        StatusBarFeature       [ URL="\ref enlighten.ui.StatusBarFeature.StatusBarFeature" ]
        StatusIndicators       [ URL="\ref enlighten.ui.StatusIndicators.StatusIndicators" ]
        Stylesheets            [ URL="\ref enlighten.ui.Stylesheets.Stylesheets" ]
        ThumbnailWidget        [ URL="\ref enlighten.ui.ThumbnailWidget.ThumbnailWidget" ]
        TimeoutDialog          [ URL="\ref enlighten.ui.TimeoutDialog.TimeoutDialog" ]
        VCRControls            [ URL="\ref enlighten.ui.VCRControls.VCRControls" ]
        
        qt_helpers -> { FocusListener MouseWheelFilter ScrollStealFilter ImageResources Stylesheets BasicWindow BasicDialog Colors }
        Controller -> ui -> { qt_helpers Authentication Clipboard ConfirmWidget GUI GuideFeature HelpFeature Marquee PageNavigation ResourceMonitorFeature Sounds StatusBarFeature StatusIndicators ThumbnailWidget TimeoutDialog VCRControls }

        /**************************** post_processing ***************************/

        AbsorbanceFeature          [ URL="\ref enlighten.post_processing.AbsorbanceFeature.AbsorbanceFeature" ]
        AutoRamanFeature           [ URL="\ref enlighten.post_processing.AutoRamanFeature.AutoRamanFeature" ]
        BaselineCorrection         [ URL="\ref enlighten.post_processing.BaselineCorrection.BaselineCorrection" ]
        BoxcarFeature              [ URL="\ref enlighten.post_processing.BoxcarFeature.BoxcarFeature" ]
        DarkFeature                [ URL="\ref enlighten.post_processing.DarkFeature.DarkFeature" ]
        DespikingFeature           [ URL="\ref enlighten.post_processing.DespikingFeature.DespikingFeature" ]
        HorizROIFeature            [ URL="\ref enlighten.post_processing.HorizROIFeature.HorizROIFeature" ]
        InterpolationFeature       [ URL="\ref enlighten.post_processing.InterpolationFeature.InterpolationFeature" ]
        RamanIntensityCorrection   [ URL="\ref enlighten.post_processing.RamanIntensityCorrection.RamanIntensityCorrection" ]
        ReferenceFeature           [ URL="\ref enlighten.post_processing.ReferenceFeature.ReferenceFeature" ]
        RichardsonLucy             [ URL="\ref enlighten.post_processing.RichardsonLucy.RichardsonLucy" ]
        ScanAveragingFeature       [ URL="\ref enlighten.post_processing.ScanAveragingFeature.ScanAveragingFeature" ]
        TakeOneFeature             [ URL="\ref enlighten.post_processing.TakeOneFeature.TakeOneFeature" ]
        TransmissionFeature        [ URL="\ref enlighten.post_processing.TransmissionFeature.TransmissionFeature" ]

        Controller -> post_processing -> { AbsorbanceFeature AutoRamanFeature BaselineCorrection BoxcarFeature DarkFeature DespikingFeature HorizROIFeature InterpolationFeature RamanIntensityCorrection ReferenceFeature RichardsonLucy ScanAveragingFeature TakeOneFeature TransmissionFeature }

        /****************************** KnowItAll *****************************/

        KIAConfig   [ label="Config" URL="\ref enlighten.KnowItAll.Config.Config" ]
        KIAFeature  [ label="Feature" URL="\ref enlighten.KnowItAll.Feature.Feature" ]
        KIAWrapper  [ label="Wrapper" URL="\ref enlighten.KnowItAll.Wrapper.Wrapper" ]

        Controller -> KIAFeature -> { KIAConfig KIAWrapper }

        /***************************** measurement ****************************/

        AreaScanFeature    [ URL="\ref enlighten.measurement.AreaScanFeature.AreaScanFeature" ]
        Measurement        [ URL="\ref enlighten.measurement.Measurement.Measurement" ]
        MeasurementFactory [ URL="\ref enlighten.measurement.MeasurementFactory.MeasurementFactory" ]
        Measurements       [ URL="\ref enlighten.measurement.Measurements.Measurements" ]
        SaveOptions        [ URL="\ref enlighten.measurement.SaveOptions.SaveOptions" ]

        Controller -> measurement -> { Measurement Measurements MeasurementFactory SaveOptions AreaScanFeature } 

        /******************************* plugins ******************************/

        EnlightenApplicationInfoReal [ URL="\ref enlighten.Plugins.EnlightenApplicationInfoReal.EnlightenApplicationInfoReal" ]
        PluginController             [ URL="\ref enlighten.Plugins.PluginController.PluginController" ]
        PluginFieldWidget            [ URL="\ref enlighten.Plugins.PluginFieldWidget.PluginFieldWidget" ]
        PluginGraphSeries            [ URL="\ref enlighten.Plugins.PluginGraphSeries.PluginGraphSeries" ]
        PluginModuleInfo             [ URL="\ref enlighten.Plugins.PluginModuleInfo.PluginModuleInfo" ]
        PluginValidator              [ URL="\ref enlighten.Plugins.PluginValidator.PluginValidator" ]
        PluginWorker                 [ URL="\ref enlighten.Plugins.PluginWorker.PluginWorker" ]
        TableModel                   [ URL="\ref enlighten.Plugins.TableModel.TableModel" ]

        Controller -> PluginController -> { PluginFieldWidget PluginGraphSeries PluginModuleInfo PluginValidator PluginWorker TableModel EnlightenApplicationInfoReal }

        /******************************* network ******************************/

        BLEManager    [ URL="\ref enlighten.network.BLEManager.BLEManager" ]    
        CloudManager  [ URL="\ref enlighten.network.CloudManager.CloudManager" ]
        UpdateChecker [ URL="\ref enlighten.network.UpdateChecker.UpdateChecker" ]
        awsConnect    [ URL="\ref enlighten.network.awsConnect" ]

        Controller -> network -> { BLEManager CloudManager UpdateChecker awsConnect }

        /****************************** file_io *******************************/

        Configuration                   [ URL="\ref enlighten.file_io.Configuration.Configuration" ]
        FileManager                     [ URL="\ref enlighten.file_io.FileManager.FileManager" ]
        HardwareCaptureControlFeature   [ URL="\ref enlighten.file_io.HardwareCaptureControlFeature.HardwareCaptureControlFeature" ]
        HardwareFileOutputManager       [ URL="\ref enlighten.file_io.HardwareFileOutputManager.HardwareFileOutputManager" ]
        LoggingFeature                  [ URL="\ref enlighten.file_io.LoggingFeature.LoggingFeature" ]                  

        Controller -> file_io -> { Configuration FileManager HardwareCaptureControlFeature HardwareFileOutputManager LoggingFeature }

        /******************************* scope ********************************/

        Cursor                      [ URL="\ref enlighten.scope.Cursor.Cursor" ]
        EmissionLamps               [ URL="\ref enlighten.scope.EmissionLamps.EmissionLamps" ]
        GraphClass                  [ label="Graph" URL="\ref enlighten.scope.Graph.Graph" ]
        GridFeature                 [ URL="\ref enlighten.scope.GridFeature.GridFeature" ]
        PresetFeature               [ URL="\ref enlighten.scope.PresetFeature.PresetFeature" ]
        RamanShiftCorrectionFeature [ URL="\ref enlighten.scope.RamanShiftCorrectionFeature.RamanShiftCorrectionFeature" ]

        Controller -> scope -> { Cursor EmissionLamps GraphClass GridFeature PresetFeature RamanShiftCorrectionFeature }

        /******************************* parser *******************************/

        ColumnFileParser [ URL="\ref enlighten.parser.ColumnFileParser.ColumnFileParser" ] 
        DashFileParser   [ URL="\ref enlighten.parser.DashFileParser.DashFileParser" ]
        ExportFileParser [ URL="\ref enlighten.parser.ExportFileParser.ExportFileParser" ]
        SPCFileParser    [ URL="\ref enlighten.parser.SPCFileParser.SPCFileParser" ]
        TextFileParser   [ URL="\ref enlighten.parser.TextFileParser.TextFileParser" ]

        MeasurementFactory -> parser -> { ColumnFileParser DashFileParser ExportFileParser SPCFileParser TextFileParser }

        /******************************* timing *******************************/

        BatchCollection [ URL="\ref enlighten.timing.BatchCollection.BatchCollection" ]
        Ramp            [ URL="\ref enlighten.timing.Ramp.Ramp" ]
        RollingDataSet  [ URL="\ref enlighten.timing.RollingDataSet.RollingDataSet" ]

        Controller -> timing -> { BatchCollection Ramp RollingDataSet }

        /******************************* device *******************************/

        AccessoryControlFeature      [ URL="\ref enlighten.device.AccessoryControlFeature.AccessoryControlFeature" ]
        BatteryFeature               [ URL="\ref enlighten.device.BatteryFeature.BatteryFeature" ]
        DetectorTemperatureFeature   [ URL="\ref enlighten.device.DetectorTemperatureFeature.DetectorTemperatureFeature" ]
        EEPROMEditor                 [ URL="\ref enlighten.device.EEPROMEditor.EEPROMEditor" ]
        EEPROMWriter                 [ URL="\ref enlighten.device.EEPROMWriter.EEPROMWriter" ]
        ExternalTriggerFeature       [ URL="\ref enlighten.device.ExternalTriggerFeature.ExternalTriggerFeature" ]
        GainDBFeature                [ URL="\ref enlighten.device.GainDBFeature.GainDBFeature" ]
        HighGainModeFeature          [ URL="\ref enlighten.device.HighGainModeFeature.HighGainModeFeature" ]
        IntegrationTimeFeature       [ URL="\ref enlighten.device.IntegrationTimeFeature.IntegrationTimeFeature" ]
        LaserControlFeature          [ URL="\ref enlighten.device.LaserControlFeature.LaserControlFeature" ]
        LaserTemperatureFeature      [ URL="\ref enlighten.device.LaserTemperatureFeature.LaserTemperatureFeature" ]
        LaserWatchdogFeature         [ URL="\ref enlighten.device.LaserWatchdogFeature.LaserWatchdogFeature" ]
        ManufacturingFeature         [ URL="\ref enlighten.device.ManufacturingFeature.ManufacturingFeature" ]
        MultiPos                     [ URL="\ref enlighten.device.MultiPos.MultiPos" ]
        Multispec                    [ URL="\ref enlighten.device.Multispec.Multispec" ]
        RegionControlFeature         [ URL="\ref enlighten.device.RegionControlFeature.RegionControlFeature" ]
        Spectrometer                 [ URL="\ref enlighten.device.Spectrometer.Spectrometer" ]
        SpectrometerApplicationState [ URL="\ref enlighten.device.SpectrometerApplicationState.SpectrometerApplicationState" ]

        EEPROMEditor -> EEPROMWriter
        LaserControlFeature -> LaserWatchdogFeature
        Multispec -> Spectrometer -> SpectrometerApplicationState
        Controller -> device -> { AccessoryControlFeature BatteryFeature DetectorTemperatureFeature EEPROMEditor ExternalTriggerFeature GainDBFeature HighGainModeFeature IntegrationTimeFeature LaserControlFeature LaserTemperatureFeature ManufacturingFeature MultiPos Multispec RegionControlFeature }

        /******************************* data *********************************/

        ColorNames [ URL="\ref enlighten.data.ColorNames.ColorNames" ]
        ModelFWHM  [ URL="\ref enlighten.data.ModelFWHM.ModelFWHM" ]                               
        ModelInfo  [ URL="\ref enlighten.data.ModelInfo.ModelInfo" ]

        Controller -> data -> { ColorNames ModelFWHM ModelInfo }

        /******************************* wasatch ******************************/

        WasatchDeviceWrapper            [ URL="\ref wasatch.WasatchDeviceWrapper.WasatchDeviceWrapper" ]
        WrapperWorker                   [ URL="\ref wasatch.WrapperWorker" ]
        WasatchDevice                   [ URL="\ref wasatch.WasatchDevice.WasatchDevice" ]
        FeatureIdentificationDevice     [ URL="\ref wasatch.FeatureIdentificationDevice.FeatureIdentificationDevice" ]
        SpectrometerSettings            [ URL="\ref wasatch.SpectrometerSettings.SpectrometerSettings" ]
        SpectrometerState               [ URL="\ref wasatch.SpectrometerState.SpectrometerState" ]
        EEPROM                          [ URL="\ref wasatch.EEPROM.EEPROM" ]
        FPGAOptions                     [ URL="\ref wasatch.FPGAOptions.FPGAOptions" ]
        Reading                         [ URL="\ref wasatch.Reading.Reading" ]
        WasatchBus                      [ URL="\ref wasatch.WasatchBus.WasatchBus" ]
        USBBus                          [ URL="\ref wasatch.WasatchBus.USBBus" ]
        DeviceFinderUSB                 [ URL="\ref wasatch.DeviceFinderUSB.DeviceFinderUSB" ]
        DeviceID                        [ URL="\ref wasatch.DeviceID.DeviceID" ]
        BalanceAcquisition              [ URL="\ref wasatch.BalanceAcquisition.BalanceAcquisition" ]
        StatusMessage                   [ URL="\ref wasatch.StatusMessage.StatusMessage" ]
        ProcessedReading                [ URL="\ref wasatch.ProcessedReading.ProcessedReading" ]

        ProcessedReading -> Reading
        WasatchBus -> { DeviceFinderUSB USBBus DeviceID }
        SpectrometerSettings -> SpectrometerState
        WasatchDeviceWrapper -> WrapperWorker 
        Controller -> wasatch -> { WasatchDeviceWrapper WasatchDevice FeatureIdentificationDevice SpectrometerSettings EEPROM FPGAOptions WasatchBus BalanceAcquisition StatusMessage ProcessedReading }
    }
\enddot

(Earlier versions of the architecture are captured at [History (Graphical)](HISTORY.md).)

## Key Files and Classes

The script you actually run to launch the ENLIGHTEN application
is scripts/Enlighten.py.

This script defines an EnlightenApplication object which instantiates a
Controller instance, which is the real heart of the show.  This remains a somewhat
bloated class and it remains a goal to continue shrinking it down into a
more maintainable set of encapsulated objects.  Milestones toward achieving that
refactoring are the many "Business Objects" which increasingly encapsulate key
functions.

The GUI itself is defined in enlighten/assets/enlighten\_layout.ui, an XML file
you will rarely (but occasionally) want to edit by-hand.  Typically you edit it
graphically using the Qt Designer utility ("make designer").

- https://doc.qt.io/archives/qt-4.8/designer-manual.html

(Watch some YouTube videos on "Qt layouts" if you're new to this tool.)

## Business Object Architecture

The goal is for a business object to "own" its own GUI elements, which is
why many of them take long lists of QWidgets in their constructor.  Once passed
to the business object, that class is expected to:

- bind widget callbacks to its own local functions
- initialize widget values from enlighten.Configuration.Configuration, and
  save updated values back to that config so they're persisted at shutdown
