# Architecture

Click individual classes in the following diagram to access their individual
documentation pages.

\dot
    /* TODO: make more UML-like (has-a, made-of etc?) */
    digraph enlighten_2_0 {
        label = "ENLIGHTEN 2.6.x"
        node [shape=box, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white, height=.25 ]
        compound = true     /* lets nodes point to clusters */
        style = filled
        fillcolor = white

        subgraph cluster_util
        {
            label = "utilities"

            Authentication                  [ URL="\ref enlighten.Authentication.Authentication" ]
            Colors                          [ URL="\ref enlighten.Colors.Colors" ]
            Configuration                   [ URL="\ref enlighten.Configuration.Configuration" ]
            RollingDataSet                  [ URL="\ref enlighten.RollingDataSet.RollingDataSet" ]
            SaveOptions                     [ URL="\ref enlighten.SaveOptions.SaveOptions" ]

            common                          [ URL="\ref enlighten.common" ]
            util                            [ URL="\ref enlighten.util" ]
            ColorNames                      [ URL="\ref enlighten.ColorNames.ColorNames" ]
            FileManager                     [ URL="\ref enlighten.FileManager.FileManager" ]
            Ramp                            [ URL="\ref enlighten.Ramp.Ramp" ]

            Colors                          -> ColorNames
            Configuration                   -> ColorNames

            { rank=same util common ColorNames FileManager Ramp }
        }

        enlighten_py                        [ group=1 fillcolor="aquamarine" fontsize="14" label="scripts/Enlighten.py" ]
        EnlightenApplication                [ group=1 fillcolor="aquamarine" fontsize="18" URL="\ref scripts.Enlighten.EnlightenApplication" ]
        Controller                          [ group=1 fillcolor="aquamarine" fontsize="24" URL="\ref enlighten.Controller.Controller" ]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_gui
        {
            label = "GUI"
            style = filled

            Clipboard                       [ URL="\ref enlighten.Clipboard.Clipboard" ]
            GUI                             [ URL="\ref enlighten.GUI.GUI" ]
            GraphClass                      [ label="Graph" URL="\ref enlighten.Graph.Graph" ]
            GuideFeature                    [ URL="\ref enlighten.GuideFeature.GuideFeature" ]
            ImageResources                  [ URL="\ref enlighten.ImageResources.ImageResources" ]
            LoggingFeature                  [ URL="\ref enlighten.LoggingFeature.LoggingFeature" ]
            Marquee                         [ URL="\ref enlighten.Marquee.Marquee" ]
            PageNavigation                  [ URL="\ref enlighten.PageNavigation.PageNavigation" ]
            StatusBarFeature                [ URL="\ref enlighten.StatusBarFeature.StatusBarFeature" ]
            StatusIndicators                [ URL="\ref enlighten.StatusIndicators.StatusIndicators" ]
            Stylesheets                     [ URL="\ref enlighten.Stylesheets.Stylesheets" ]
            VCRControls                     [ URL="\ref enlighten.VCRControls.VCRControls" ]

            Cursor                          [ URL="\ref enlighten.Cursor.Cursor" ]
            Sounds                          [ URL="\ref enlighten.Sounds.Sounds" ]

            GraphClass -> Cursor
            VCRControls -> TakeOneFeature
            GUI -> Stylesheets

            subgraph cluster_views
            {
                label = "views"
                style = filled

                BasicWindow                 [ URL="\ref enlighten.BasicWindow.BasicWindow" ]
                BasicDialog                 [ URL="\ref enlighten.BasicDialog.BasicDialog" ]
            }

            { rank=same Cursor Sounds BasicDialog BasicWindow }
        }

        BasicDialog-> Controller [ dir=back ltail=cluster_gui  ]
        ColorNames -> Controller [ dir=back ltail=cluster_util ]

        subgraph cluster_devices
        {
            label = "devices"
            style = filled

            Multispec                       [ URL="\ref enlighten.Multispec.Multispec" ]
            Spectrometer                    [ URL="\ref enlighten.Spectrometer.Spectrometer" ]
            SpectrometerApplicationState    [ URL="\ref enlighten.SpectrometerApplicationState.SpectrometerApplicationState" ]
            ModelInfo                       [ URL="\ref enlighten.ModelInfo.ModelInfo" ]
            ModelFWHM                       [ URL="\ref enlighten.ModelFWHM.ModelFWHM" ]

            Multispec -> Spectrometer
            Spectrometer -> SpectrometerApplicationState
        }
        Controller -> Multispec

        subgraph cluster_plugin_system
        {
            label = "Plugin Architecture"
            style = filled

            subgraph cluster_plugin_external
            {
                label = "EnlightenPlugin"
                style = filled

                EnlightenPluginBase             [ URL="\ref EnlightenPlugin.EnlightenPluginBase" ]
                EnlightenPluginConfiguration    [ URL="\ref EnlightenPlugin.EnlightenPluginConfiguration" ]
                EnlightenPluginDependency       [ URL="\ref EnlightenPlugin.EnlightenPluginDependency" ]
                EnlightenPluginField            [ URL="\ref EnlightenPlugin.EnlightenPluginField" ]
                EnlightenApplicationInfo        [ URL="\ref EnlightenPlugin.EnlightenApplicationInfo" ]

                EnlightenApplicationInfo -> EnlightenPluginBase
                EnlightenPluginBase -> EnlightenPluginConfiguration 
                EnlightenPluginConfiguration -> { EnlightenPluginField, EnlightenPluginDependency }
            }

            EnlightenPluginRequest          [ URL="\ref EnlightenPlugin.EnlightenPluginRequest" ]
            EnlightenPluginResponse         [ URL="\ref EnlightenPlugin.EnlightenPluginResponse" ]

            subgraph cluster_plugin_internal
            {
                {
                    rank = same
                    PluginController                [ URL="\ref enlighten.Plugins.PluginController.PluginController" ]
                    PluginWorker                    [ URL="\ref enlighten.Plugins.PluginWorker.PluginWorker" ]
                }
                PluginFieldWidget               [ URL="\ref enlighten.Plugins.PluginFieldWidget.PluginFieldWidget" ]
                PluginGraphSeries               [ URL="\ref enlighten.Plugins.PluginGraphSeries.PluginGraphSeries" ]
                PluginModuleInfo                [ URL="\ref enlighten.Plugins.PluginModuleInfo.PluginModuleInfo" ]
                PluginValidator                 [ URL="\ref enlighten.Plugins.PluginValidator.PluginValidator" ]
                TableModel                      [ URL="\ref enlighten.Plugins.TableModel.TableModel" ]
                EnlightenApplicationInfoReal    [ URL="\ref enlighten.Plugins.EnlightenApplicationInfoReal.EnlightenApplicationInfoReal" ]


                edge [style="invis"] PluginFieldWidget -> PluginGraphSeries -> PluginModuleInfo -> PluginValidator -> TableModel
            }

            EnlightenApplicationInfoReal -> EnlightenApplicationInfo

        }
        Controller -> PluginController -> PluginWorker -> EnlightenPluginRequest -> EnlightenPluginBase
        PluginController -> { PluginModuleInfo, PluginFieldWidget, PluginGraphSeries, TableModel, PluginValidator, EnlightenApplicationInfoReal }
        EnlightenPluginResponse -> EnlightenPluginBase [dir=back]
        PluginWorker -> EnlightenPluginResponse [dir=back]
        
        subgraph cluster_measurements
        {
            label = "measurements"
            style = filled

            subgraph cluster_file_parsers
            {
                label = "file parsers"
                style = filled

                ColumnFileParser            [ URL="\ref enlighten.ColumnFileParser.ColumnFileParser" ]

                DashFileParser              [ URL="\ref enlighten.DashFileParser.DashFileParser" ]
                DashMeasurement             [ URL="\ref enlighten.DashFileParser.DashMeasurement" ]
                DashSpectrometer            [ URL="\ref enlighten.DashFileParser.DashSpectrometer" ]
                DashFileParser -> { DashMeasurement DashSpectrometer }

                ExportFileParser            [ URL="\ref enlighten.ExportFileParser.ExportFileParser" ]
                ExportedMeasurement         [ URL="\ref enlighten.ExportFileParser.ExportedMeasurement" ]
                ExportFileParser -> ExportedMeasurement

                SPCFileParser               [ URL="\ref enlighten.SPCFileParser.SPCFileParser" ]
            }

            Measurement                     [ URL="\ref enlighten.Measurement.Measurement" ]
            ProcessedReading                [ URL="\ref enlighten.ProcessedReading.ProcessedReading" ]
            MeasurementFactory              [ URL="\ref enlighten.MeasurementFactory.MeasurementFactory" ]
            Measurements                    [ URL="\ref enlighten.Measurements.Measurements" ]
            ThumbnailWidget                 [ URL="\ref enlighten.ThumbnailWidget.ThumbnailWidget" ]
            ConfirmWidget                   [ URL="\ref enlighten.ConfirmWidget.ConfirmWidget" ]
            FocusListener                   [ URL="\ref enlighten.FocusListener.FocusListener" ]

            Measurements -> MeasurementFactory -> Measurement -> { ThumbnailWidget ProcessedReading }
            Measurements -> Measurement
            MeasurementFactory -> { DashFileParser ColumnFileParser ExportFileParser SPCFileParser }
            ThumbnailWidget -> ConfirmWidget
            ThumbnailWidget -> FocusListener

            FileManager -> Measurements [dir=back]
        }
        Controller -> Measurements

        subgraph cluster_driver
        {
            label = "Wasatch.PY"
            style = filled
            fillcolor = lightgray
            node [style=filled, fillcolor=white]

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

            WasatchDeviceWrapper -> WrapperWorker -> WasatchDevice -> { FeatureIdentificationDevice }
            FeatureIdentificationDevice -> SpectrometerSettings -> { EEPROM FPGAOptions SpectrometerState }
            WasatchBus -> { USBBus }
            USBBus -> DeviceFinderUSB -> DeviceID
            FileBus -> DeviceID
            WasatchDevice -> { DeviceID Reading Overrides BalanceAcquisition }

            { rank=same USBBus FileBus }
        }
        Controller -> WasatchBus
        ProcessedReading -> Reading
        Spectrometer -> WasatchDeviceWrapper
        Measurement -> SpectrometerSettings

        subgraph cluster_features
        {
            label = "Feature Business Objects"
            style = filled

            subgraph cluster_features_post_processing
            {
                label = "Post-Processing"
                color = white
                style = filled
                
                AbsorbanceFeature               [ URL="\ref enlighten.AbsorbanceFeature.AbsorbanceFeature" ]
                BaselineCorrection              [ URL="\ref enlighten.BaselineCorrection.BaselineCorrection" ]
                BoxcarFeature                   [ URL="\ref enlighten.BoxcarFeature.BoxcarFeature" ]
                DarkFeature                     [ URL="\ref enlighten.DarkFeature.DarkFeature" ]
                RamanShiftCorrectionFeature     [ URL="\ref enlighten.RamanShiftCorrectionFeature.RamanShiftCorrectionFeature" ]
                RamanIntensityCorrection        [ URL="\ref enlighten.RamanIntensityCorrection.RamanIntensityCorrection" ]
                ReferenceFeature                [ URL="\ref enlighten.ReferenceFeature.ReferenceFeature" ]
                RichardsonLucy                  [ URL="\ref enlighten.RichardsonLucy.RichardsonLucy" ]
                ScanAveragingFeature            [ URL="\ref enlighten.ScanAveragingFeature.ScanAveragingFeature" ]
                TransmissionFeature             [ URL="\ref enlighten.TransmissionFeature.TransmissionFeature" ]
                VignetteROIFeature              [ URL="\ref enlighten.VignetteROIFeature.VignetteROIFeature" ]

                Superman                        [ URL="https://github.com/all-umass/superman/" fillcolor=lightgray ]
                BaselineCorrection -> Superman

                AbsorbanceFeature -> TransmissionFeature -> ReferenceFeature

                edge [style="invis"] DarkFeature -> ScanAveragingFeature -> BoxcarFeature -> RamanCorrectionFeature -> RamanIntensityCorrection -> RichardsonLucy -> VignetteROIFeature
            }

            subgraph cluster_feature_device_control
            {
                label = "Device Control"
                color = white
                style = filled

                AccessoryControlFeature         [ URL="\ref enlighten.AccessoryControlFeature.AccessoryControlFeature" ]
                BatteryFeature                  [ URL="\ref enlighten.BatteryFeature.BatteryFeature" ]
                DetectorTemperatureFeature      [ URL="\ref enlighten.DetectorTemperatureFeature.DetectorTemperatureFeature" ]
                EEPROMEditor                    [ URL="\ref enlighten.EEPROMEditor.EEPROMEditor" ]
                EEPROMWriter                    [ URL="\ref enlighten.EEPROMWriter.EEPROMWriter" ]
                ExternalTriggerFeature          [ URL="\ref enlighten.ExternalTriggerFeature.ExternalTriggerFeature" ]
                GainDBFeature                   [ URL="\ref enlighten.GainDBFeature.GainDBFeature" ]
                IntegrationTimeFeature          [ URL="\ref enlighten.IntegrationTimeFeature.IntegrationTimeFeature" ]
                LaserControlFeature             [ URL="\ref enlighten.LaserControlFeature.LaserControlFeature" ]
                LaserTemperatureFeature         [ URL="\ref enlighten.LaserTemperatureFeature.LaserTemperatureFeature" ]
                MultiPos                        [ URL="\ref enlighten.MultiPos.MultiPos" ]
                RamanModeFeature                [ URL="\ref enlighten.RamanModeFeature.RamanModeFeature" ]

                EEPROMEditor -> EEPROMWriter 

                edge [style="invis"] IntegrationTimeFeature -> GainDBFeature -> DetectorTemperatureFeature -> AccessoryControlFeature -> RamanModeFeature -> MultiPos
            }

            subgraph cluster_features_automation
            {
                label = "Automation"
                color = white
                style = filled

                BatchCollection                 [ URL="\ref enlighten.BatchCollection.BatchCollection" ]
                ManufacturingFeature            [ URL="\ref enlighten.ManufacturingFeature.ManufacturingFeature" ]
                ResourceMonitorFeature          [ URL="\ref enlighten.ResourceMonitorFeature.ResourceMonitorFeature" ]
                TakeOneFeature                  [ URL="\ref enlighten.TakeOneFeature.TakeOneFeature" ]

                edge [style="invis"] TakeOneFeature -> BatchCollection -> ManufacturingFeature -> ResourceMonitorFeature
            }

            subgraph cluster_knowitall
            {
                label = "KnowItAll"
                style = filled

                KIA_Feature [ label="Feature" URL="\ref enlighten.KnowItAll.Feature.Feature"  ]
                KIA_Wrapper [ label="Wrapper" URL="\ref enlighten.KnowItAll.Wrapper.Wrapper"  ]
                KIA_Config  [ label="Config"  URL="\ref enlighten.KnowItAll.Config.Config"    ]

                subgraph cluster_KnowItAllWrapper
                {
                    label = "KnowItAll Wrapper (C++)"
                    style = filled
                    fillcolor = lightgray

                    KIAConsole
                }

                KIA_Feature -> KIA_Wrapper -> KIAConsole
                KIA_Feature -> KIA_Config
            }
        }
        BusinessObjects [ URL="\ref enlighten.BusinessObjects.BusinessObjects" ]

        Controller -> BusinessObjects 
        BusinessObjects -> IntegrationTimeFeature [ lhead=cluster_features ]
    }
\enddot

(Earlier versions of the architecture are captured at [History (Graphical)](README_HISTORY.md).)

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
