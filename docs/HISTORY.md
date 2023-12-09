# Architectural History

Following are major ENLIGHTEN releases and the principal classes added or
re-written during each.

The classes aren't clickable because class names change during refactoring and
current documentation wouldn't apply to old versions anyway.

# ENLIGHTEN 1.0

Basically as-received from Nathan. (View the [rendered version](https://wasatchphotonics.com/api/ENLIGHTEN/md_docs__h_i_s_t_o_r_y.html) of this document.)

\dot
    digraph enlighten_1_0 {
        label = "ENLIGHTEN 1.0"
        node [shape=record, fontname=Helvetica, fontsize=10 ]
        compound = true

        enlighten_py                        [ label="scripts/Enlighten.py" group=1]
        EnlightenApplication                [ group=1]
        Controller                          [ group=1]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_views
        {
            label = "views"

            BasicWindow
            ThumbnailWidget
            ConfirmWidget
            Stylesheets
            ThumbnailWidget -> ConfirmWidget
        }

        Controller -> BasicWindow [lhead=cluster_views]

        WasatchDeviceWrapper                [ group=1]
        WasatchDevice                       [ group=1]
        FeatureIdentificationDevice         [ group=1]
        Reading
        WasatchBus
        USBBus

        WasatchDeviceWrapper -> WasatchDevice -> { FeatureIdentificationDevice StrokerProtocolDevice }
        WasatchBus -> { USBBus SimulationBus }
        WasatchDevice -> Reading
        Controller -> { WasatchDeviceWrapper WasatchBus }
    }
\enddot

# ENLIGHTEN 1.1

- extracted Wasatch.PY into separate open-source driver
- started organizing into classes
    - common
    - Colors
    - RollingDataSet
- first Business Object
    - BatchCollection
- early production support
    - Wavecal
    - EmissionLamps
    - ModelInfo
    - Ramp

\dot
    digraph enlighten_1_1 {
        label = "ENLIGHTEN 1.1"
        node [shape=record, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white]
        compound = true /* lets nodes point to clusters */
        style = filled
        fillcolor = white

        enlighten_py                        [ label="scripts/Enlighten.py" group=1]
        EnlightenApplication                [ group=1]
        Controller                          [ group=1]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_util
        {
            label = "utilities"

            common                          [ fillcolor=gold]
            Colors                          [ fillcolor=gold]
            Ramp                            [ fillcolor=gold]
            RollingDataSet                  [ fillcolor=gold]
        }
        Controller -> common [ lhead=cluster_util ]

        subgraph cluster_views
        {
            label = "views"
            style = filled

            Stylesheets
            BasicWindow
            BasicDialog                 [ fillcolor=gold]
            ThumbnailWidget
            ConfirmWidget

            ThumbnailWidget -> ConfirmWidget
        }
        Controller -> BasicWindow [ lhead=cluster_views ]

        subgraph cluster_driver
        {
            label = "Wasatch.PY"
            style = filled
            fillcolor = lightgray
            node [style=filled, fillcolor=white]

            WasatchDeviceWrapper            [ group=1]
            WasatchDevice                   [ group=1]
            FeatureIdentificationDevice     [ group=1]
            Reading
            WasatchBus
            USBBus

            WasatchDeviceWrapper -> WasatchDevice -> FeatureIdentificationDevice
            WasatchBus -> USBBus
            WasatchDevice -> Reading
        }
        Controller -> { WasatchDeviceWrapper WasatchBus }

        subgraph cluster_features
        {
            label = "Feature Business Objects"
            style = filled

            BatchCollection                 [ fillcolor=gold]
            Wavecal                         [ fillcolor=gold]
            EmissionLamps                   [ fillcolor=gold]
            ModelInfo                       [ fillcolor=gold]

            Wavecal -> { EmissionLamps ModelInfo }
        }
        Controller -> BatchCollection [lhead = cluster_features]
    }
\enddot

# Version 1.2

- pulling functionality out of Controller
    - util
    - Configuration
    - Clipboard
    - Marquee
- early production support
    - LaserCharacterization
    - PeakFinding
- customer requests
    - RamanConcentration
    - RamanMatching
    - RelativeIrradiance

\dot
    digraph enlighten_1_2 {
        label = "ENLIGHTEN 1.2"
        node [shape=record, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white]
        compound = true /* lets nodes point to clusters */
        style = filled
        fillcolor = white

        enlighten_py                        [ label="scripts/Enlighten.py" group=1]
        EnlightenApplication                [ group=1]
        Controller                          [ group=1]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_util
        {
            label = "utilities"

            common
            Colors
            Ramp
            RollingDataSet
            util                            [ fillcolor=gold]
            Configuration                   [ fillcolor=gold]
            ProcessedReading

            Colors                          -> ColorNames
            Configuration                   -> ColorNames
        }
        Controller -> Configuration [ lhead=cluster_util ]

        subgraph cluster_gui
        {
            label = "GUI"
            style = filled

            Stylesheets
            Clipboard                       [ fillcolor=gold]
            Marquee                         [ fillcolor=gold]

            subgraph cluster_views
            {
                label = "views"
                style = filled

                BasicWindow
                BasicDialog
                ThumbnailWidget
                ConfirmWidget

                ThumbnailWidget -> ConfirmWidget
            }
        }
        Controller -> Marquee [ lhead=cluster_gui ]

        subgraph cluster_driver
        {
            label = "Wasatch.PY"
            style = filled
            fillcolor = lightgray
            node [style=filled, fillcolor=white]

            WasatchDeviceWrapper            [ group=1]
            WasatchDevice                   [ group=1]
            FeatureIdentificationDevice     [ group=1]
            Reading
            WasatchBus
            USBBus

            WasatchDeviceWrapper -> WasatchDevice -> FeatureIdentificationDevice
            WasatchBus -> USBBus
            WasatchDevice -> Reading
        }
        Controller -> { WasatchDeviceWrapper WasatchBus }
        ProcessedReading -> Reading

        subgraph cluster_features
        {
            label = "Feature Business Objects"
            style = filled

            BatchCollection
            EmissionLamps
            ModelInfo
            LaserCharacterization           [ fillcolor=gold]
            RamanConcentration              [ fillcolor=gold]
            RamanMatching                   [ fillcolor=gold]
            RelativeIrradiance              [ fillcolor=gold]
            Wavecal

            subgraph cluster_ramanmatching
            {
                label = "raman_matching"
                style = filled

                RM_CompoundDatabase         [ label="CompoundDatabase" fillcolor=gold]
                RM_Compound                 [ label="Compound" fillcolor=gold]
                RM_CompoundID               [ label="CompoundID" fillcolor=gold]
                RM_Peak                     [ label="Peak" fillcolor=gold]
                RM_RecognitionEngine        [ label="RecognitionEngine" fillcolor=gold]

                RM_RecognitionEngine -> RM_CompoundDatabase -> RM_Compound -> RM_Peak
                RM_RecognitionEngine -> RM_CompoundID
            }
            RamanMatching -> RM_RecognitionEngine

            subgraph cluster_ramanconcentration
            {
                label = "raman_concentration"
                style = filled

                RC_CompoundDatabase         [ label="CompoundDatabase" fillcolor=gold]
                RC_Compound                 [ label="Compound" fillcolor=gold]

                RC_CompoundDatabase         -> RC_Compound
            }
            RamanConcentration -> RC_CompoundDatabase
        }
        Controller -> BatchCollection [ lhead=cluster_features ]

        subgraph cluster_peakfinding
        {
            label = "peakfinding"
            style = filled

            Peak                            [ fillcolor=gold]
            PeakFinding                     [ fillcolor=gold]
            PeakFinder                      [ fillcolor=gold]
            PeakFinderBaselineWavelet       [ fillcolor=gold]
            PeakFinderCWT                   [ fillcolor=gold]
            PeakFinderPeakUtils             [ fillcolor=gold]

            PeakFinding                     -> PeakFinder
            PeakFinder                      -> { PeakFinderBaselineWavelet PeakFinderCWT PeakFinderPeakUtils }
            PeakFinderBaselineWavelet       -> Peak
            PeakFinderCWT                   -> Peak
            PeakFinderPeakUtils             -> Peak
        }
        Wavecal -> { EmissionLamps ModelInfo PeakFinding }
        RamanMatching -> PeakFinding
        RamanConcentration -> PeakFinding
    }
\enddot

# Version 1.3

The goal of 1.3 was to get ready for multiple spectrometers, while supporting early SiG integration and some customer requests.

- Refactored spectrometer state
    - SpectrometerApplicationState
    - ProcessedReading
    - EEPROM
    - EEPROMEditor
    - SpectrometerSettings
    - SpectrometerState
    - FPGAOptions
    - Authentication
- Support for ASISpec
    - FileSpectrometer
- Support for early IMX integration
    - Overrides
    - StatusMessage
- Customer requests
    - BalanceAcquisition
    - Sounds

\dot
    digraph enlighten_1_3 {
        label = "ENLIGHTEN 1.3"
        node [shape=record, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white]
        compound = true /* lets nodes point to clusters */
        style = filled
        fillcolor = white

        enlighten_py                        [ label="scripts/Enlighten.py" group=1]
        EnlightenApplication                [ group=1]
        Controller                          [ group=1]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_util
        {
            label = "utilities"

            common
            Colors
            Ramp
            RollingDataSet
            util
            Configuration
            Authentication                  [ fillcolor=gold]
            ProcessedReading                [ fillcolor=gold]

            Colors                          -> ColorNames
            Configuration                   -> ColorNames
        }
        Controller -> Configuration [ lhead=cluster_util ]

        subgraph cluster_gui
        {
            label = "GUI"
            style = filled

            Stylesheets
            Clipboard
            Marquee
            Sounds                          [ fillcolor=gold]

            subgraph cluster_views
            {
                label = "views"
                style = filled

                BasicWindow
                BasicDialog
                ThumbnailWidget
                ConfirmWidget
                ThumbnailWidget -> ConfirmWidget
            }
        }
        Controller -> Marquee [ lhead=cluster_gui ]

        subgraph cluster_devices
        {
            label = "devices"
            style = filled

            SpectrometerApplicationState    [ fillcolor=gold]
            ModelInfo

            Multispec -> Spectrometer
            Spectrometer -> SpectrometerApplicationState
        }
        Controller -> Multispec

        subgraph cluster_driver
        {
            label = "Wasatch.PY"
            style = filled
            fillcolor = lightgray
            node [style=filled, fillcolor=white]

            WasatchDeviceWrapper            [ group=1]
            WasatchDevice                   [ group=1]
            FeatureIdentificationDevice     [ group=1]
            SpectrometerSettings            [ fillcolor=gold group=1]
            SpectrometerState               [ fillcolor=gold group=1]
            EEPROM                          [ fillcolor=gold]
            FPGAOptions                     [ fillcolor=gold]
            Reading
            WasatchBus
            USBBus
            FileBus                         [ fillcolor=gold]
            Overrides                       [ fillcolor=gold]
            BalanceAcquisition              [ fillcolor=gold]
            StatusMessage                   [ fillcolor=gold]
            FileSpectrometer                [ fillcolor=gold]

            WasatchDeviceWrapper -> WasatchDevice -> { FeatureIdentificationDevice FileSpectrometer }
            FeatureIdentificationDevice -> SpectrometerSettings -> { EEPROM FPGAOptions SpectrometerState }
            WasatchBus -> { USBBus FileBus }
            WasatchDevice -> { Reading Overrides BalanceAcquisition }
        }
        Controller -> { WasatchDeviceWrapper WasatchBus }
        ProcessedReading -> Reading
        Spectrometer -> SpectrometerSettings

        subgraph cluster_features
        {
            label = "Feature Business Objects"
            style = filled

            BatchCollection
            EEPROMEditor                    [ fillcolor=gold]
            EmissionLamps
            LaserCharacterization
            RamanConcentration
            RamanMatching
            RelativeIrradiance
            Wavecal

            subgraph cluster_ramanmatching
            {
                label = "raman_matching"
                style = filled

                RM_CompoundDatabase         [ label="CompoundDatabase" ]
                RM_Compound                 [ label="Compound" ]
                RM_CompoundID               [ label="CompoundID" ]
                RM_Peak                     [ label="Peak" ]
                RM_RecognitionEngine        [ label="RecognitionEngine" ]

                RM_RecognitionEngine -> RM_CompoundDatabase -> RM_Compound -> RM_Peak
                RM_RecognitionEngine -> RM_CompoundID
            }
            RamanMatching -> RM_RecognitionEngine

            subgraph cluster_ramanconcentration
            {
                label = "raman_concentration"
                style = filled

                RC_CompoundDatabase         [ label="CompoundDatabase" ]
                RC_Compound                 [ label="Compound" ]

                RC_CompoundDatabase         -> RC_Compound
            }
            RamanConcentration -> RC_CompoundDatabase
        }
        Controller -> BatchCollection [ lhead=cluster_features ]

        subgraph cluster_peakfinding
        {
            label = "peakfinding"
            style = filled

            Peak
            PeakFinding
            PeakFinder
            PeakFinderBaselineWavelet
            PeakFinderCWT
            PeakFinderPeakUtils

            PeakFinding                     -> PeakFinder
            PeakFinder                      -> { PeakFinderBaselineWavelet PeakFinderCWT PeakFinderPeakUtils }
            PeakFinderBaselineWavelet       -> Peak
            PeakFinderCWT                   -> Peak
            PeakFinderPeakUtils             -> Peak
        }
        Wavecal -> { EmissionLamps ModelInfo PeakFinding }
        RamanMatching -> PeakFinding
        RamanConcentration -> PeakFinding
    }
\enddot

# Version 1.4

The goal of version 1.4 was to support multiple spectrometers.

- added multi-spectrometer operation
    - Multispec
    - Spectrometer
    - ColorNames
- customer requests
    - SaveOptions

\dot
    digraph enlighten_1_4 {
        label = "ENLIGHTEN 1.4"
        node [shape=record, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white]
        compound = true /* lets nodes point to clusters */
        style = filled
        fillcolor = white

        enlighten_py                        [ label="scripts/Enlighten.py" group=1]
        EnlightenApplication                [ group=1]
        Controller                          [ group=1]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_util
        {
            label = "utilities"

            common
            Colors
            Ramp
            RollingDataSet
            util
            Configuration
            SaveOptions                     [ fillcolor=gold]
            ColorNames                      [ fillcolor=gold]
            ProcessedReading
            Stylesheets
            Clipboard
            Marquee
            Sounds

            Colors                          -> ColorNames
            Configuration                   -> ColorNames
        }
        Controller -> Configuration [ lhead=cluster_util ]

        subgraph cluster_views
        {
            label = "views"
            style = filled

            BasicWindow
            BasicDialog
            ThumbnailWidget
            ConfirmWidget
            ThumbnailWidget -> ConfirmWidget
        }
        Controller -> BasicWindow [ lhead=cluster_views ]

        subgraph cluster_devices
        {
            label = "devices"
            style = filled

            Multispec                       [ fillcolor=gold]
            Spectrometer                    [ fillcolor=gold]
            SpectrometerApplicationState
            ModelInfo

            Multispec -> Spectrometer
            Spectrometer -> SpectrometerApplicationState
        }
        Controller -> Multispec

        subgraph cluster_driver
        {
            label = "Wasatch.PY"
            style = filled
            fillcolor = lightgray
            node [style=filled, fillcolor=white]

            WasatchDeviceWrapper            [ group=1]
            WasatchDevice                   [ group=1]
            FeatureIdentificationDevice     [ group=1]
            SpectrometerSettings            [ group=1]
            SpectrometerState               [ group=1]
            EEPROM
            FPGAOptions
            Reading
            WasatchBus
            USBBus
            FileBus
            Overrides
            BalanceAcquisition
            StatusMessage
            FileSpectrometer

            WasatchDeviceWrapper -> WasatchDevice -> { FeatureIdentificationDevice FileSpectrometer }
            FeatureIdentificationDevice -> SpectrometerSettings -> { EEPROM FPGAOptions SpectrometerState }
            WasatchBus -> { USBBus FileBus }
            WasatchDevice -> { Reading Overrides BalanceAcquisition }
        }
        Controller -> { WasatchDeviceWrapper WasatchBus }
        ProcessedReading -> Reading
        Spectrometer -> SpectrometerSettings

        subgraph cluster_features
        {
            label = "Feature Business Objects"
            style = filled

            BatchCollection
            EEPROMEditor
            EmissionLamps
            LaserCharacterization
            RamanConcentration
            RamanMatching
            RelativeIrradiance
            Wavecal

            subgraph cluster_ramanmatching
            {
                label = "raman_matching"
                style = filled

                RM_CompoundDatabase         [ label="CompoundDatabase" ]
                RM_Compound                 [ label="Compound" ]
                RM_CompoundID               [ label="CompoundID" ]
                RM_Peak                     [ label="Peak" ]
                RM_RecognitionEngine        [ label="RecognitionEngine" ]

                RM_RecognitionEngine -> RM_CompoundDatabase -> RM_Compound -> RM_Peak
                RM_RecognitionEngine -> RM_CompoundID
            }
            RamanMatching -> RM_RecognitionEngine

            subgraph cluster_ramanconcentration
            {
                label = "raman_concentration"
                style = filled

                RC_CompoundDatabase         [ label="CompoundDatabase" ]
                RC_Compound                 [ label="Compound" ]

                RC_CompoundDatabase         -> RC_Compound
            }
            RamanConcentration -> RC_CompoundDatabase
        }
        Controller -> BatchCollection [ lhead=cluster_features ]

        subgraph cluster_peakfinding
        {
            label = "peakfinding"
            style = filled

            Peak
            PeakFinding
            PeakFinder
            PeakFinderBaselineWavelet
            PeakFinderCWT
            PeakFinderPeakUtils

            PeakFinding                     -> PeakFinder
            PeakFinder                      -> { PeakFinderBaselineWavelet PeakFinderCWT PeakFinderPeakUtils }
            PeakFinderBaselineWavelet       -> Peak
            PeakFinderCWT                   -> Peak
            PeakFinderPeakUtils             -> Peak
        }
        Wavecal -> { EmissionLamps ModelInfo PeakFinding }
        RamanMatching -> PeakFinding
        RamanConcentration -> PeakFinding
    }
\enddot

# Version 1.5

- refactored data management
    - Measurements
    - Measurement
    - MeasurementFactory
    - FileManager
    - DashFileParser
    - ExportFileParser
    - ColumnFileParser
    - Graph
    - Cursor

\dot
    /* TODO: make more UML-like (has-a, made-of etc?) */
    digraph enlighten_1_5 {
        label = "ENLIGHTEN 1.5"
        node [shape=box, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white, height=.25 ]
        compound = true /* lets nodes point to clusters */
        style = filled
        fillcolor = white

        subgraph cluster_util
        {
            label = "utilities"

            Authentication
            Colors
            Configuration
            RollingDataSet
            SaveOptions

            common
            util
            ColorNames
            FileManager                     [ fillcolor=gold]
            Ramp

            Colors                          -> ColorNames
            Configuration                   -> ColorNames

            { rank=same util common ColorNames FileManager Ramp }
        }

        enlighten_py                        [ group=1]
        EnlightenApplication                [ group=1]
        Controller                          [ group=1]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_gui
        {
            label = "GUI"
            style = filled

            GraphClass                      [ label="Graph" fillcolor=gold]
            Clipboard
            Marquee
            Stylesheets

            Cursor                          [ fillcolor=gold]
            Sounds

            GraphClass -> Cursor

            subgraph cluster_views
            {
                label = "views"
                style = filled

                BasicWindow
                BasicDialog
            }

            { rank=same Cursor Sounds BasicDialog BasicWindow }
        }

        BasicDialog-> Controller [ dir=back ltail=cluster_gui  ]
        ColorNames -> Controller [ dir=back ltail=cluster_util ]

        subgraph cluster_devices
        {
            label = "devices"
            style = filled

            Multispec
            Spectrometer
            SpectrometerApplicationState
            ModelInfo

            Multispec -> Spectrometer
            Spectrometer -> SpectrometerApplicationState
        }
        Controller -> Multispec

        subgraph cluster_measurements
        {
            label = "measurements"
            style = filled

            subgraph cluster_file_parsers
            {
                label = "file parsers"
                style = filled
                subgraph cluster_column_parser
                {
                    label = "column-ordered CSV"
                    style = filled
                    ColumnFileParser            [ fillcolor=gold]
                }
                subgraph cluster_dash_parser
                {
                    label = "Dash (row-ordered CSV)"
                    style = filled
                    DashFileParser              [ fillcolor=gold]
                    DashMeasurement             [ fillcolor=gold]
                    DashSpectrometer            [ fillcolor=gold]
                    DashFileParser -> { DashMeasurement DashSpectrometer }
                }
                subgraph cluster_export_parser
                {
                    label = "Export (row-ordered CSV)"
                    style = filled
                    ExportFileParser            [ fillcolor=gold]
                    ExportedMeasurement         [ fillcolor=gold]
                    ExportFileParser -> ExportedMeasurement
                }
            }

            Measurement                     [ fillcolor=gold]
            ProcessedReading
            MeasurementFactory              [ fillcolor=gold]
            Measurements                    [ fillcolor=gold]
            ThumbnailWidget
            ConfirmWidget

            Measurements -> MeasurementFactory -> Measurement -> { ThumbnailWidget ProcessedReading }
            Measurements -> Measurement
            MeasurementFactory -> { DashFileParser ColumnFileParser ExportFileParser }
            ThumbnailWidget -> ConfirmWidget
            FileManager -> Measurements [dir=back]
        }
        Controller -> Measurements

        subgraph cluster_driver
        {
            label = "Wasatch.PY"
            style = filled
            fillcolor = lightgray
            node [style=filled, fillcolor=white]

            WasatchDeviceWrapper
            WasatchDevice
            FeatureIdentificationDevice
            SpectrometerSettings
            SpectrometerState
            EEPROM
            FPGAOptions
            Reading
            WasatchBus
            USBBus
            FileBus
            DeviceFinderUSB                 [ fillcolor=gold]
            DeviceID                        [ fillcolor=gold]
            Overrides
            BalanceAcquisition
            StatusMessage
            FileSpectrometer

            WasatchDeviceWrapper -> WasatchDevice -> { FeatureIdentificationDevice FileSpectrometer }
            FeatureIdentificationDevice -> SpectrometerSettings -> { EEPROM FPGAOptions SpectrometerState }
            WasatchBus -> { USBBus FileBus }
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

            BatchCollection
            EEPROMEditor
            LaserCharacterization
            Wavecal

            EmissionLamps
            RelativeIrradiance
            RamanConcentration
            RamanMatching

            subgraph cluster_ramanmatching
            {
                label = "raman_matching"
                style = filled

                RM_CompoundDatabase         [ label="CompoundDatabase" ]
                RM_Compound                 [ label="Compound" ]
                RM_CompoundID               [ label="CompoundID" ]
                RM_Peak                     [ label="Peak" ]
                RM_RecognitionEngine        [ label="RecognitionEngine" ]

                RM_RecognitionEngine -> RM_CompoundDatabase -> RM_Compound -> RM_Peak
                RM_RecognitionEngine -> RM_CompoundID
            }
            RamanMatching -> RM_RecognitionEngine

            subgraph cluster_ramanconcentration
            {
                label = "raman_concentration"
                style = filled

                RC_CompoundDatabase         [ label="CompoundDatabase" ]
                RC_Compound                 [ label="Compound" ]

                RC_CompoundDatabase         -> RC_Compound
            }
            RamanConcentration -> RC_CompoundDatabase

            subgraph cluster_peakfinding
            {
                label = "peakfinding"
                style = filled

                Peak
                PeakFinding
                PeakFinder
                PeakFinderBaselineWavelet
                PeakFinderCWT
                PeakFinderPeakUtils

                PeakFinding                     -> PeakFinder
                PeakFinder                      -> { PeakFinderBaselineWavelet PeakFinderCWT PeakFinderPeakUtils }
                PeakFinderBaselineWavelet       -> Peak
                PeakFinderCWT                   -> Peak
                PeakFinderPeakUtils             -> Peak
            }
            Wavecal -> { EmissionLamps ModelInfo PeakFinding }
            RamanMatching -> PeakFinding
            RamanConcentration -> PeakFinding

            { rank=same EmissionLamps RelativeIrradiance RamanConcentration RamanMatching }

        }
        Controller -> Wavecal [ lhead=cluster_features ]
    }
\enddot

# Version 1.6

- Python 3.4
- no major rearchitecture

# Version 1.7

- Python 3.7
- Qt 5.13
- KnowItAll
- Raman Intensity Correction
- Baseline Correction
- Richardson-Lucy deconvolution
- VignetteROI
- refactored VCRControls, including TakeOne
- external Raman Identification
- reprocessing loaded spectra

\dot
    digraph enlighten_1_7 {
        label = "ENLIGHTEN 1.7.x"
        node [shape=box, style=filled, fontname=Helvetica, fontsize=10, fillcolor=white, height=.25 ]
        compound = true /* lets nodes point to clusters */
        style = filled
        fillcolor = white

        subgraph cluster_util
        {
            label = "utilities"

            Authentication
            Colors
            Configuration
            RollingDataSet
            SaveOptions

            common
            util
            ColorNames
            FileManager
            Ramp

            Colors                          -> ColorNames
            Configuration                   -> ColorNames

            { rank=same util common ColorNames FileManager Ramp }
        }

        enlighten_py                        [ label="scripts/Enlighten.py" group=1]
        EnlightenApplication                [ group=1]
        Controller                          [ group=1]

        enlighten_py -> EnlightenApplication -> Controller

        subgraph cluster_gui
        {
            label = "GUI"
            style = filled

            VCRControls                     [ fillcolor=gold ]
            GraphClass                      [ label="Graph" ]
            Clipboard
            Marquee
            GUI                             [ fillcolor=gold ]
            Stylesheets

            Cursor
            Sounds

            GraphClass -> Cursor
            VCRControls -> TakeOneFeature
            GUI -> Stylesheets

            subgraph cluster_views
            {
                label = "views"
                style = filled

                BasicWindow
                BasicDialog
            }

            { rank=same Cursor Sounds BasicDialog BasicWindow }
        }

        BasicDialog-> Controller [ dir=back ltail=cluster_gui  ]
        ColorNames -> Controller [ dir=back ltail=cluster_util ]

        subgraph cluster_devices
        {
            label = "devices"
            style = filled

            Multispec
            Spectrometer
            SpectrometerApplicationState
            ModelInfo

            Multispec -> Spectrometer
            Spectrometer -> SpectrometerApplicationState
        }
        Controller -> Multispec

        subgraph cluster_measurements
        {
            label = "measurements"
            style = filled

            subgraph cluster_file_parsers
            {
                label = "file parsers"
                style = filled
                subgraph cluster_column_parser
                {
                    label = "column-ordered CSV"
                    style = filled
                    ColumnFileParser
                }
                subgraph cluster_dash_parser
                {
                    label = "Dash (row-ordered CSV)"
                    style = filled
                    DashFileParser
                    DashMeasurement
                    DashSpectrometer
                    DashFileParser -> { DashMeasurement DashSpectrometer }
                }
                subgraph cluster_export_parser
                {
                    label = "Export (row-ordered CSV)"
                    style = filled
                    ExportFileParser
                    ExportedMeasurement
                    ExportFileParser -> ExportedMeasurement
                }
            }

            Measurement
            ProcessedReading
            MeasurementFactory
            Measurements
            ThumbnailWidget
            ConfirmWidget

            Measurements -> MeasurementFactory -> Measurement -> { ThumbnailWidget ProcessedReading }
            Measurements -> Measurement
            MeasurementFactory -> { DashFileParser ColumnFileParser ExportFileParser }
            ThumbnailWidget -> ConfirmWidget
            FileManager -> Measurements [dir=back]
        }
        Controller -> Measurements

        subgraph cluster_driver
        {
            label = "Wasatch.PY"
            style = filled
            fillcolor = lightgray
            node [style=filled, fillcolor=white]

            WasatchDeviceWrapper
            WasatchDevice
            FeatureIdentificationDevice
            SpectrometerSettings
            SpectrometerState
            EEPROM
            FPGAOptions
            Reading
            WasatchBus
            USBBus
            FileBus
            DeviceFinderUSB
            DeviceID
            Overrides
            BalanceAcquisition
            StatusMessage
            FileSpectrometer

            WasatchDeviceWrapper -> WasatchDevice -> { FeatureIdentificationDevice FileSpectrometer }
            FeatureIdentificationDevice -> SpectrometerSettings -> { EEPROM FPGAOptions SpectrometerState }
            WasatchBus -> { USBBus FileBus }
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

            BatchCollection
            EEPROMEditor
            Wavecal

            TakeOneFeature                  [ fillcolor=gold ]
            ScanAveragingFeature            [ fillcolor=gold ]
            BoxcarFeature                   [ fillcolor=gold ]

            EmissionLamps
            RelativeIrradiance
            RamanConcentration
            RamanMatching

            RichardsonLucy                  [ fillcolor=gold ]
            BaselineCorrection              [ fillcolor=gold ]
            Superman                        [ fillcolor=lightgray ]
            VignetteROIFeature              [ fillcolor=gold ]
            RamanIntensityCorrection        [ fillcolor=gold ]
            BaselineCorrection -> Superman

            subgraph cluster_knowitall
            {
                label = "KnowItAll"
                style = filled

                KIA_Feature [ label="Feature" fillcolor=gold ]
                KIA_Wrapper [ label="Wrapper" fillcolor=gold ]
                KIA_Config  [ label="Config"  fillcolor=gold ]

                subgraph cluster_KnowItAllWrapper
                {
                    label = "KnowItAll Wrapper (C++)"
                    style = filled
                    fillcolor = lightgray

                    KIAConsole [ fillcolor=gold ]
                }

                KIA_Feature -> KIA_Wrapper -> KIAConsole
                KIA_Feature -> KIA_Config
            }

            subgraph cluster_ramanmatching
            {
                label = "raman_matching"
                style = filled

                RM_CompoundDatabase         [ label="CompoundDatabase" ]
                RM_Compound                 [ label="Compound" ]
                RM_CompoundID               [ label="CompoundID" ]
                RM_Peak                     [ label="Peak" ]
                RM_RecognitionEngine        [ label="RecognitionEngine" ]

                RM_RecognitionEngine -> RM_CompoundDatabase -> RM_Compound -> RM_Peak
                RM_RecognitionEngine -> RM_CompoundID
            }
            RamanMatching -> RM_RecognitionEngine

            subgraph cluster_ramanconcentration
            {
                label = "raman_concentration"
                style = filled

                RC_CompoundDatabase         [ label="CompoundDatabase" ]
                RC_Compound                 [ label="Compound" ]

                RC_CompoundDatabase         -> RC_Compound
            }
            RamanConcentration -> RC_CompoundDatabase

            subgraph cluster_peakfinding
            {
                label = "peakfinding"
                style = filled

                Peak
                PeakFinding
                PeakFinder
                PeakFinderBaselineWavelet
                PeakFinderCWT
                PeakFinderPeakUtils

                PeakFinding                     -> PeakFinder
                PeakFinder                      -> { PeakFinderBaselineWavelet PeakFinderCWT PeakFinderPeakUtils }
                PeakFinderBaselineWavelet       -> Peak
                PeakFinderCWT                   -> Peak
                PeakFinderPeakUtils             -> Peak
            }
            Wavecal -> { EmissionLamps ModelInfo PeakFinding }
            RamanMatching -> PeakFinding
            RamanConcentration -> PeakFinding

            { rank=same EmissionLamps RelativeIrradiance RamanConcentration RamanMatching }

        }
        Controller -> Wavecal [ lhead=cluster_features ]

    }
\enddot

# 2.0

See [Architecture](ARCHITECTURE.md) for current version.

