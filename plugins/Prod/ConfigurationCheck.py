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
        # Serial / Model
        ########################################################################

        sn = ee.serial_number
        if re.match(r"WP-\d{5}", sn):
            notes.append(f"standard serial number {sn}")
        else:
            bad.append(f"non-standard serial number {sn}")

        ########################################################################
        # Detector Cooling
        ########################################################################

        if ee.has_cooling:
            if is_xs:
                bad.append(f"has_cooling {has_cooling} but is XS")
            else:
                bad.append(f"has_cooling {has_cooling} (typical for non-XS)")
        else:
            if not is_xs:
                bad.append(f"has_cooling {has_cooling} is unusual for non-XS")

        ########################################################################
        # Gain / Offset
        ########################################################################

        gain = ee.detector_gain
        offset = ee.detector_offset
        if is_xs:
            if gain == 8.0:
                notes.append(f"gain {gain} is typical for XS")
            else:
                bad.append(f"gain {gain} is unusual for XS")
        else:
            if gain < 1 or gain > 1.5:
                bad.append(f"gain {gain} is unusual for non-XS")
            else:
                notes.append(f"gain {gain} seems reasonable for non-XS")

        if offset < 0:
            bad.append(f"negative offset {offset} is unusual")
        elif offset > 3000:
            bad.append(f"offset {offset} seems excessive")

        ########################################################################
        # Wavecal
        ########################################################################

        if ee.wavelength_coeffs is None or len(ee.wavelength_coeffs) == 0 or ss.wavelengths is None or len(ss.wavelengths) < ss.pixels():
            bad.append(f"wavecal seems bad or missing")

        ########################################################################
        # Detector
        ########################################################################

        detector = ee.detector
        if is_xs:
            if detector != "IMX385":
                bad.append(f"detector {detector} is unusual for XS")

        ########################################################################
        # Pixels
        ########################################################################

        pixels = ss.pixels()
        if is_xs:
            if pixels != 1952:
                bad.append(f"pixels {pixels} seems unusual for XS")

        ########################################################################
        # Laser / Raman / Excitation
        ########################################################################

        # does this look like it's supposed to be a Raman unit?
        has_laser = ee.has_laser
        intended_for_raman = ss.excitation() > 0 or has_laser or re.search(r"\d+X", model)
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

        if has_laser:
            if ee.disable_laser_armed_indicator and not "DT" in model:
                bad.append(f"laser armed indicator disabled in non-DT model")

            if is_xs:
                laser_tec_setpoint = ee.startup_laser_tec_setpoint
                notes.append(f"laser TEC setpoint {laser_tec_setpoint} raw")
                if laser_tec_setpoint < 700:
                    bad.append(f"laser TEC setpoint {laser_tec_setpoint} seems low")
                elif laser_tec_setpoint > 1000:
                    bad.append(f"laser TEC setpoint {laser_tec_setpoint} seems high")
        else:
            if is_xs:
                bad.append(f"has_laser {has_laser} is unusual for XS")
            else:
                for tok in ["-ILC", "-ILP"]:
                    if tok in model:
                        bad.append(f"has_laser {has_laser} is unusual for model {model}")

        # laser temperature
        if is_xs:
            if has_laser:
                if ee.max_laser_temp_deg_c < 50 or ee.max_laser_temp_deg_c > 60:
                    bad.append(f"max_laser_temp_deg_c {ee.max_laser_temp_deg_c} is unusual for XS (recommend 50-60)")
                else:
                    notes.append(f"max_laser_temp_deg_c {ee.max_laser_temp_deg_c} is reasonable for XS")

            if ee.sig_laser_tec:
                notes.append(f"XS laser TEC enabled (ok)")
            else:
                bad.append(f"XS laser TEC disabled (unusual)")
        else:
            if ee.sig_laser_tec:
                bad.append(f"XS laser TEC enabled on non-XS unit")

        # laser power
        is_xm = any([ext in model for ext in ['XM', 'XR', 'XC']])
        has_laser_power_cal = ee.has_laser_power_calibration()
        if has_laser:
            if is_xs:
                if has_laser_power_cal:
                    bad.append(f"it is unusual for an XS unit to have a laser power calibration")
                elif ee.max_laser_power_mW < 90 or ee.max_laser_power_mW > 110:
                    bad.append(f"max_laser_power_mW {ee.max_laser_power_mW} seems unusual for xs units")
                elif ee.max_laser_power_mW > 90 and ee.max_laser_power_mW < 110:
                    notes.append(f"max_laser_power_mW {ee.max_laser_power_mW} seems reasonable")
            else:
                if has_laser_power_cal:
                    notes.append(f"it seems reasonable for laser-equipped model {model} to have a laser power calibration")
                else:
                    bad.append(f"it seems unusual for laser-equipped model {model} to lack a laser power calibration")
                       
        if has_laser_power_cal:
            if ee.max_laser_power_mW < 3 or ee.max_laser_power_mW > 485:
                bad.append(f"max_laser_power_mW {ee.max_laser_power_mW} seems unusual for units with a laser power calibration")

        # attenuator (XS)
        laser_attenuator = ee.laser_attenuator
        if is_xs:
            if laser_attenuator == 127:
                bad.append("laser attenuator appears non-calibrated")
            elif 10 <= laser_attenuator <= 40:
                notes.append(f"laser attenuator {laser_attenuator} seems reasonable")
            else:
                bad.append(f"laser attenuator {laser_attenuator} seems unreasonable")
        else:
            if laser_attenuator != 0:
                bad.append(f"laser attenuator {laser_attenuator} unusual for non-XS")

        # longpass filter
        if intended_for_raman and not ee.cutoff_filter_installed:
            bad.append("intended for Raman but cutoff filter not installed?")

        # horizontal binning (intended for 633XS and XS-VIS)
        has_horiz_binning = ee.horiz_binning_mode != 0
        if has_horiz_binning:
            if is_xs:
                if std_excitation and std_excitation >= 785:
                    bad.append(f"horizontal binning is not recommended for {std_excitation}nm excitation") 
                else:
                    notes.append(f"horizontal binning is reasonable for {model}")
            else:
                bad.append(f"horizontal binning is enabled on non-XS unit")

        # password
        if is_xs:
            if ee.laser_password:
                if ee.laser_password == sn:
                    notes.append(f"standard laser password is set (ok)")
                else:
                    bad.append(f"custom laser password is set")
            else:
                notes.append(f"no laser password set (ok)")
        else:
            bad.append(f"laser password is set on non-XS unit")
                    
        ########################################################################
        # Integration Time
        ########################################################################

        max_integ = ee.max_integration_time_ms
        if is_xs:
            if max_integ < 5_000:
                bad.append(f"max_integ {max_integ} seems low for XS")
            elif max_integ > 10_000:
                bad.append(f"max_integ {max_integ} seems high for XS")
        else:
            if max_integ < 60_000:
                bad.append(f"max_integ {max_integ} seems low for non-XS")

        ########################################################################
        # Horiz ROI / SRM / DALAI
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

        has_fwhm = ee.avg_resolution != 0.0
        if intended_for_raman:
            if not has_fwhm:
                bad.append(f"intended for Raman but no average resolution (will prevent DALAI deconvolution)")
        
        ########################################################################
        # Battery
        ########################################################################

        has_batt = ee.has_battery

        if ss.is_xs():
            if has_batt:
                notes.append(f"has_battery {has_batt} reasonable for XS")
            else:
                bad.append(f"has_battery {has_batt} unusual for XS")
        else:
            if has_batt:
                bad.append(f"has_battery {has_batt} unusual for non-XS")
            else:
                notes.append(f"has_battery {has_batt} reasonable for non-XS")

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
            if laser_watchdog_sec == 0:
                notes.append(f"laser watchdog is disabled at boot (okay)")
            else:
                bad.append(f"laser watchdog {laser_watchdog_sec}sec is not currently recommended for XS")

            detector_timeout_sec = ee.detector_timeout_sec
            notes.append(f"detector_timeout_sec {detector_timeout_sec}")
            if detector_timeout_sec < 1:
                notes.append(f"detector timeout is disabled at boot (ok)")

            power_timeout_sec = ee.power_timeout_sec
            if power_timeout_sec < 1:
                bad.append(f"power timeout is disabled at boot")
            elif power_timeout_sec < 120:
                bad.append(f"power timeout {power_timeout_sec}sec seems low for XS")
            elif power_timeout_sec > 600: # 10min
                bad.append(f"power timeout {power_timeout_sec}sec seems high for XS")
    
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
        # XS-only stuff
        ########################################################################

        scan_averaging = ee.startup_scans_to_average 
        if scan_averaging > 1:
            if is_xs:
                bad.append(f"startup_scans_to_average {scan_averaging} is unusual on XS")
            else:
                bad.append(f"startup_scans_to_average {scan_averaging} is unusual on non-XS")

        if is_xs:

            assembly_rev = ee.assembly_revision
            if assembly_rev:
                notes.append(f"XS Assembly Revision {assembly_rev}")
            else:
                bad.append(f"XS unit missing assembly revision")

            if ee.has_interlock_feedback:
                notes.append(f"has laser interlock feedback (ok)")
            else:
                bad.append(f"laser interlock feedback disabled (unusual)")

            if ee.disable_ble_power:
                bad.append(f"BLE power disabled (unusual)")

            if ee.ble_door_sensor:
                bad.append("BLE Door Sensor is set (unusual)")
            if ee.ext_laser_control:
                bad.append("External Laser Control is set (unusual)")
            if ee.aux_button_laser_enable:
                bad.append("Auxillary Button can Control Laser is set (unusual)")
            if ee.disable_laser_sub_sys:
                bad.append("Disable Laser Sub-System is set (unusual)")
            if ee.leave_acc_5v_out_powered:
                bad.append("Leave ACC_5V_OUT Powered is set (unusual)")

        ########################################################################
        # Misc
        ########################################################################

        if ee.invert_x_axis:
            if is_xs:
                bad.append("unusual to invert_x_axis on XS")
            notes.append("okay to invert_x_axis on non-XS")

        if ee.horiz_binning_enabled:
            if is_xs:
                notes.append("horiz binning enabled (ok)")
            else:
                bad.append("unusual to enable horiz binning on non-XS")

        if ee.gen15:
            bad.append("unusual to enable Gen1.5 (220190/290)")

        if ee.is_oem:
            bad.append("is_oem set (unusual)")

        if ee.hardware_even_odd:
            bad.append("hardware_even_odd set (unusual)")

        is_xl = "XL" in model
        if ee.has_shutter:
            if is_xl:
                notes.append("has_shutter enabled (ok on XL)")
            else:
                bad.append("has_shutter enabled (unusual on non-XL)")

        if ee.laser_interlock_excluded:
            bad.append("laser interlock is excluded (unusual)")

        if ee.laser_timeout_after_count:
            bad.append("laser timeout configured to use frame-count rather than seconds (unusual)")

        subformat = ee.subformat
        if subformat == 0:
            notes.append(f"subformat {subformat} (User Data) okay")
        elif subformat == 1:
            notes.append(f"subformat {subformat} (SRM) okay")
        elif subformat == 2:
            bad.append(f"subformat {subformat} (spline) unusual")
        elif subformat == 3:
            bad.append(f"subformat {subformat} (untethered) unusual")
        elif subformat == 4:
            bad.append(f"subformat {subformat} (detector regions) unusual")
        elif subformat == 5:
            bad.append(f"subformat {subformat} (multi-wavelength) unusual")
        else:
            bad.append(f"subformat {subformat} (undefined) unusual")

        ########################################################################
        # Pixel Correction
        ########################################################################

        ########################################################################
        # Output report
        ########################################################################

        label_text = f"Configuration check on {model} {sn}:"

        html = ""
        html += self.html_list("Issues", bad)
        html += self.html_list("Notes", notes)
            
        self.ctl.gui.msgbox_with_scrolling_html("Configuration Check", label_text, html)

    def html_list(self, name, a):
        if len(a) == 0:
            return ""
        return f"{name}:<ul><li>" + "</li><li>".join(a) + "</li></ul>"

"""
Reading EEPROM (9 pages)
Parsing EEPROM
               feature_mask_xs 0
                     acc_state 0
               acc_state_gpio1 0
               acc_state_gpio2 0
     acc_cont_strobe_period_us 0
      acc_cont_strobe_width_us 0
      acc_cont_strobe_delay_us 0
         acc_cont_strobe_count 0
        max_battery_temp_deg_c 0
        pixel_calibration_type 0
         usb_manufacturer_name
           aux_button_function 0
              aux_button_param 0
        laser_firing_delay_sec 255
     latched_hardware_failures 255
FeatureMask 0x42a:
Current EEPROM:
  Page 0: 57 50 2d 37 38 35 58 53 2d 4f 45 4d 2d 44 54 34 57 50 2d 54 45 53 54 00 00 00 00 00 00 00 00 00
          2c 01 00 00 00 01 01 2a 04 19 00 01 00 20 03 00 00 00 00 41 00 00 00 00 00 41 00 00 20 03 ff 13
  Page 1: 00 00 00 00 00 00 80 3f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 3f 00 00 00 00 84 03 20 03
          00 00 00 00 00 00 80 3f 00 00 00 00 10 27 7a 0d 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff
  Page 2: 49 4d 58 33 38 35 00 00 00 00 00 00 00 00 00 00 a0 07 00 38 04 00 00 00 00 a0 07 00 00 00 00 00
          00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff
  Page 3: ff ff ff ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
          00 00 00 00 00 40 44 44 01 00 00 00 60 ea 00 00 00 00 00 00 00 00 fe 00 00 00 00 00 ff 7f ff ff
  Page 4: 00 50 50 52 45 4c 49 4d 00 ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
          ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  Page 5: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
          00 00 00 00 00 00 00 00 00 00 00 00 00 00 dd 2e 00 00 00 00 ff ff ff ff ff ff ff ff ff ff ff 01
  Page 6: 00 00 00 00 00 ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
          ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  Page 7: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
          ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  Page 8: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
          00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff ff

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
