import logging
import re

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class ConfigurationCheck(EnlightenPluginBase):
    """
    Quick sanity-check of the connected spectrometer's EEPROM to call-out any 
    unexpected oddities or possibly mis-configured values.

    The general idea is, if something's acting funky with your spectrometer,
    run this before reporting ENLIGHTEN bugs :-)

    This may eventually be made a standard ENLIGHTEN feature, perhaps run by 
    default the first time a new spectrometer is connected, perhaps re-run 
    anytime the EEPROM digest changes. Could alert the user via a (!) on the
    Hardware StatusIndicator or similar.
    """

    def get_configuration(self):
        self.name = "Configuration Check"
        self.process_requests = False

        self.field(name="Run", datatype="button", callback=self.run, tooltip="Sanity-check your EEPROM")

        self.run()

    def run(self):
        """ Activated by button press, so runs in GUI thread """
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        ss = spec.settings
        ee = ss.eeprom
        model = ss.full_model()
        sn = ee.serial_number

        is_xs = ss.is_xs()
        is_ingaas = ss.is_ingaas()

        bad = []
        notes = []

        ########################################################################
        # Laser / Raman / Excitation
        ########################################################################

        # does this look like it's supposed to be a Raman unit?
        intended_for_raman = ss.excitation() > 0 or ee.has_laser or re.search(r"\d+X", model)
        notes.append(f"{'is' if intended_for_raman else 'is not'} intended for Raman")

        # determine closest "official" excitation
        excitation = ss.excitation()
        std_excitation = None
        for nm in [ 532, 633, 638, 785, 830, 1064 ]:
            if abs(excitation - nm) < 1.0:
                std_excitation = nm
                notes.append(f"standard excitation {nm}nm")

        if intended_for_raman and std_excitation is None:
            bad.append("intended for Raman but no standard excitation")

        if std_excitation:
            if str(std_excitation) in model:
                notes.append(f"excitation {excitation} and {std_excitation} in model {model}")
            else:
                bad.append(f"excitation {excitation} but {std_excitation} not in model {model}")

        if ee.has_laser:
            if ee.disable_laser_armed_indicator and not "DT" in model:
                bad.append(f"laser armed indicator disabled in non-DT model")

            if is_xs:
                laser_tec_setpoint = ee.startup_laser_tec_setpoint
                notes.append(f"laser TEC setpoint {laser_tec_setpoint} raw")
                if laser_tec_setpoint < 700:
                    bad.append(f"laser TEC setpoint {laser_tec_setpoint} seems low")
                elif laser_tec_setpoint > 1000:
                    bad.append(f"laser TEC setpoint {laser_tec_setpoint} seems high")

        ########################################################################
        # Horiz ROI / SRM
        ########################################################################

        has_srm = ss.raman_intensity_factors is not None
        notes.append(f"{'does' if has_srm else 'does not'} have SRM calibration")

        if intended_for_raman:
            if has_srm:
                notes.append(f"Raman spectrometer has SRM calibration")
            else:
                bad.append(f"Raman spectrometer has no SRM calibration")

        has_horiz_roi = ee.has_horizontal_roi()
        notes.append(f"{'does' if has_horiz_roi else 'does not'} have horizontal ROI defined")
        if has_srm:
            if has_horiz_roi:
                notes.append(f"has SRM calibration and horiz ROI")
            else:
                bad.append(f"has SRM calibration but no horiz ROI")
        
        ########################################################################
        # Battery
        ########################################################################

        has_batt = ee.has_battery
        notes.append(f"{'does' if has_batt else 'does not'} have battery")

        if has_batt:
            rds = self.ctl.strip_charts.get_rds(sn, "Battery Charge Level")
            if rds is None:
                bad.append(f"Battery charge has not been read")
            else:
                batt_charge = rds.latest_value()
                notes.append(f"Battery charge {batt_charge:.2f}")
                if batt_charge < 1:
                    bad.append(f"Battery charge {batt_charge:.2f} seems unreasonably low")
                elif batt_charge < 15:
                    bad.append(f"Battery charge {batt_charge:.2f} is low")
                elif batt_charge > 101:
                    bad.append(f"Battery charge {batt_charge:.2f} seems high")

            max_batt_temp = ee.max_battery_temp_deg_c
            notes.append(f"Max battery temp {max_batt_temp}°C")
            if max_batt_temp < 40:
                bad.append(f"Max battery temp {max_batt_temp}°C seems low")
            elif max_batt_temp > 65:
                bad.append(f"Max battery temp {max_batt_temp}°C seems high")

        ########################################################################
        # Timeouts and Watchdogs
        ########################################################################

        if is_xs:
            laser_watchdog_sec = ee.laser_watchdog_sec
            notes.append(f"laser_watchdog_sec {laser_watchdog_sec}")
            if laser_watchdog_sec < 1:
                bad.append(f"laser watchdog is disabled at boot")

            detector_timeout_sec = ee.detector_timeout_sec
            notes.append(f"detector_timeout_sec {detector_timeout_sec}")
            if detector_timeout_sec < 1:
                bad.append(f"detector timeout is disabled at boot")

            power_timeout_sec = ee.power_timeout_sec
            notes.append(f"power_timeout_sec {power_timeout_sec}")
            if power_timeout_sec < 1:
                bad.append(f"power timeout is disabled at boot")
    
        ########################################################################
        # Vertical ROI
        ########################################################################

        has_vertical_roi = ss.has_vertical_roi()
        notes.append(f"has_vertical_roi {has_vertical_roi}")
        if is_xs:
            if has_vertical_roi:
                vertical_roi = ss.get_vertical_roi()
                notes.append(f"vertical_roi {vertical_roi}")
            else:
                bad.append(f"XS is missing vertical ROI")

        ########################################################################
        # Detector TEC
        ########################################################################

        if ee.has_cooling:
            startup_detector_temp = ee.startup_temp_degC
            notes.append(f"startup detector temp {startup_detector_temp}")
            if "-R-" in model:
                if startup_detector_temp < 5:
                    bad.append(f"startup detector temp {startup_detector_temp} seems low for regulated")
                elif startup_detector_temp > 10:
                    bad.append(f"startup detector temp {startup_detector_temp} seems high for regulated")
            elif "-C-" in model:
                if startup_detector_temp < -15:
                    bad.append(f"startup detector temp {startup_detector_temp} seems low for cooled")
                elif startup_detector_temp > -12:
                    bad.append(f"startup detector temp {startup_detector_temp} seems high for cooled")
            
        ########################################################################
        # InGaAs
        ########################################################################

        if is_ingaas:
            has_even_odd_calibration = ee.detector_gain_odd != 1.0 or ee.detector_offset_odd != 0
            has_ingaas_correction = ss.ingaas_correction is not None

            notes.append(f"has_even_odd_calibration {has_even_odd_calibration}")
            notes.append(f"has_ingaas_correction {has_ingaas_correction}")

            if not (has_even_odd_calibration or has_ingaas_correction):
                bad.append("InGaAs unit has neither even-odd gain/offset nor InGaAs pixel correction")

        ########################################################################
        # Output report
        ########################################################################

        label_text = f"Configuration check on {model} {sn}:"

        html = ""
        html += self.html_list("Issues", bad)
        html += self.html_list("Notes", notes)
            
        self.ctl.gui.msgbox_with_scrolling_html("Configuration Check", label_text, html)

    def html_list(self, name, a):
        if a is None:
            return ""
        return f"{name}:<ul><li>" + "</li><li>".join(a) + "</li></ul>"

"""
generated 1952 wavelengths from 755.40 to 1017.50
generated 1952 wavenumbers from -497.72 to 2912.35 (after correction 0.00) using excitation 784.907
update_raman_intensity_factors: coeffs [0.4636397957801819, -0.002109522931277752, 2.919365897469106e-06, -9.726768279705311e-10, -1.3242339625026134e-13, 1.1693930405511977e-16]
generated 1952 Raman intensity factors
SpectrometerSettings:
    DeviceID = <DeviceID USB:0x24aa:0x4000:0:1>
    Microcontroller Firmware Version = 1.0.67.3
    FPGA Firmware Version = 03.26.0
    Wavelengths = (755.40, 1017.50)
    Wavenumbers = (-497.72, 2912.35)
    SpectrometerState: None
      Integration Time:       0
      TEC Setpoint:           15.00 degC
      TEC Enabled:            False
      High Gain Mode Enabled: False
      Gain (dB):              8
      Laser Enabled:          False
      Laser Power %:          100.00
      Laser Power mW:         100.00
      Use mW:                 False
      Laser Temp Setpoint:    0x0000
      Selected ADC:           None
      Trigger Source:         INTERNAL
      Area Scan Enabled:      False
      Scans to Average:       1
      Boxcar Half-Width:      0
      Background Subtraction: 0
      Bad Pixel Mode:         AVERAGE
      USB Interval:           (0, 0ms)
      Secondary ADC Enabled:  False
      Position:               0
      Wavenumber Correction:  0
      Laser Watchdog Sec:     0
      Laser TEC Mode:         2
      Laser TEC Setpoint:     818
      Accessory Connector:    XSAccessoryConnector < acc_state XSAccState < gpio enabled False, 5V enabled False, 5V good False >, GPIO1 XSGPIOState < num 1, control MANUAL, direction INPUT, value LOW, func DISABLED >, GPIO2 XSGPIOState < num 2, control MANUAL, direction INPUT, value LOW, func DISABLED >, strobe XSContinuousStrobe < period 2us, width 1us, delay 0us, repeat 0 > >
   FPGA Compilation Options:
     integration time resolution = 1ms
     data header                 = None
     has cf select               = False
     laser type                  = None
     laser control               = Modulation
     has area scan               = False
     has actual integ time       = False
     has horiz binning           = False
    EEPROM settings:
      Model:            WP-785XS-F13-A-I
      Serial Number:    WP-03173
      Has Cooling:      False
      Has Battery:      True
      Has Laser:        True
      Invert X-Axis:    False
      Horiz Bin Enable: True
      Gen 1.5:          False
      Cutoff Filter:    True
      HW Even/Odd:      False
      SiG Laser TEC:    True
      Int'Lck Feedback: False
      Shutter:          False
      Disable BLE Power:False
      Dis Laser Arm Ind:False
      Excitation (f):   784.91 nm
      Laser Warmup Sec: 0
      Laser Watchdog:   0
      Light Source:     0
      Power Timeout:    0
      Detector Timeout: 0
      Horiz Bin Mode:   0
      Startup Scan Avg: 100
      Laser Attenuator: 17
      Slit size:        20 um
      Start Integ Time: 1 ms
      Start Temp:       826.00 degC
      Start Triggering: 0x0000
      Det Gain:         8.000000
      Det Offset:       0
      Det Gain Odd:     8.000000
      Det Offset Odd:   0
      Start Laser TEC:  818 (raw)
      Accessory State:  65535 
      GPIO 1 State:     255 
      GPIO 2 State:     255 
    
      Wavecal coeffs:   [755.3961181640625, 0.18832610547542572, -4.884259033133276e-05, 1.3066880022449823e-08, -1.1349630003182343e-12]
      degCToDAC coeffs: [0.0, 1.0, 0.0]
      adcToDegC coeffs: [0.0, 1.0, 0.0]
      Det temp max:     50 degC
      Det temp min:     50 degC
      TEC R298:         10000
      TEC beta:         3450
      Calibration Date: 05/04/2026
      Calibration By:   CG
    
      Detector name:    IMX385
      Active Px Horiz:  1952
      Active Px Vert:   1080
      Actual Px Horiz:  1952
      Actual Px Vert:   1080
      Min integration:  1 ms
      Max integration:  10000 ms
      ROI Horiz Start:  30
      ROI Horiz End:    1900
      ROI Vert Reg 1:   (100, 900)
      ROI Vert Reg 2:   (0, 0)
      ROI Vert Reg 3:   (0, 0)
    
      Max Laser Temp:   0 degC
      Laser coeffs:     [0.0, 0.0, 0.0, 0.0]
      Max Laser Power:  100.0 mW
      Min Laser Power:  0.0 mW
      Avg Resolution:   12.24
    
      User Text:        
    
      Bad Pixels:       []
      Product Config:   LP-V2
      Assembly Rev:     
    Multi-Wavelength:
      Calibration #0
        excitation_nm_float = 784.906982421875
        wavelength_coeffs = [755.3961181640625, 0.18832610547542572, -4.884259033133276e-05, 1.3066880022449823e-08, -1.1349630003182343e-12]
        roi_horizontal_start = 30
        roi_horizontal_end = 1900
        avg_resolution = 12.239999771118164
        raman_intensity_coeffs = [0.4636397957801819, -0.002109522931277752, 2.919365897469106e-06, -9.726768279705311e-10, -1.3242339625026134e-13, 1.1693930405511977e-16]
        horiz_binning_mode = 0
      Calibration #1
        excitation_nm_float = 200.0
        wavelength_coeffs = [0.0, 0.0, 0.0, 0.0, 0.0]
        roi_horizontal_start = 0
        roi_horizontal_end = 0
        avg_resolution = 0.0
        raman_intensity_coeffs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        horiz_binning_mode = 0
"""
