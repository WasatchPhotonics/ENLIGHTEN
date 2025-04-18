import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class MultiWaveCal(EnlightenPluginBase):
    """
    This plugin is provided to demonstrate EEPROM Subformat 5, which allows a 
    multi-wavelength calibration to be stored in the spectrometer for use with 
    dual-wavelength gratings.

    The main purpose of this plugin is to provide a pull-down combobox allowing
    the user to select which calibration (including vertical ROI) to use in the
    spectrometer. This allows the user to switch back and forth between 785nm 
    and 633nm ROIs, automatically updating the "active" set of dependent 
    calibrations, including:

    - vertical ROI (start/stop lines)
    - horizontal ROI (start/stop pixels)
    - wavelength calibration
    - excitation wavelength (for computing wavenumber axis)
    - Raman Intensity Calibration
    - auto-binning mode

    As a visual aid, the plugin also offers an optional second graph which shows
    both excitations (633nm and 785nm) overlaied. 

    Since only one calibration can be in effect at one time, the extra graph 
    displays "cached" data for the unselected excitation. This requires the user
    to build-up the dual-wavelength spectrum by physically switching input fibers
    (or external laser sources), and toggling the plugin when the second set of
    calibrations should be used.

    It is instructive to view the dual graphs from an emission or Raman source
    in pixel, wavelength and wavenumber axes, as each will overlap differently.

    Note that ENLIGHTEN's "Save" function is unaffected by the second graph, and
    still only saves the "live" spectrum in the upper graph.

    For posterity, these were the key settings on the test unit (WP-00860):

    - 633/638nm
        - vertical ROI (700, 875)
        - wavecal 593.1948         0.1359748            -2.853866e-05            6.422492e-09           -6.287138e-13
          coeffs [593.19482421875, 0.13597479462623596, -2.8538659535115585e-05, 6.422491871660441e-09, -6.287138236242551e-13]
    - 785nm
        - vertical ROI (275, 475)
        - wavecal 755.2945 0.1831673 -5.324801e-05 1.981370e-08 -3.651564e-12

    Note that only 2 calibrations are currently supported (the "originals" on 
    EEPROM pages 0-6, and a second on page 7), so unique calibrations for 633nm
    and 638nm are not supported at this time.
    """

    def get_configuration(self):
        self.name = "Multi-Wavelength Calibration"
        self.has_other_graph = True
        self.cache = {}

        ########################################################################
        # Build the Excitation ComboBox
        ########################################################################

        # Iterate through all the excitations stored on the spectrometer, and
        # build a combobox containing the integral excitations of all 
        # calibrations found. Make sure to "default" to the currently-selected
        # calibration, noting that the plugin may have been previous connected,
        # used to change the selected calibration, and then disconnected (for
        # instance to briefly connect the Prod.EmissionLines plugin for a 
        # verification).

        initial = None
        choices = []

        spec = self.ctl.multispec.current_spectrometer()
        if spec is not None:
            for i in range(spec.settings.calibrations()):
                excitation_float = spec.settings.eeprom.multi_wavelength_calibration.get("excitation_nm_float", calibration=i)
                excitation = int(round(excitation_float, 0))
                label = f"{excitation}nm"
                choices.append(label)
                if i == spec.settings.eeprom.multi_wavelength_calibration.selected_calibration:
                    initial = label
        
        self.field(name="Excitation", 
                   datatype="combobox", 
                   direction="input", 
                   choices=choices,
                   initial=initial,
                   callback=self.combo_callback)

    def process_request(self, request):
        settings = request.settings
        pr = request.processed_reading 

        if not settings.is_xs():
            self.marquee_message = f"ERROR: {self.name} requires XS series"
            return

        if not settings.eeprom.subformat == 5:
            self.marquee_message = f"ERROR: {self.name} requires EEPROM subformat 5"
            return

        ########################################################################
        # cache this reading
        ########################################################################

        label = request.fields["Excitation"]
        self.cache[label] = {
            "y": pr.get_processed(),
            "x": { "nm": pr.get_wavelengths(),
                   "cm": pr.get_wavenumbers(),
                   "px": pr.get_pixel_axis() } }

        ########################################################################
        # graph latest spectrum from all excitations
        ########################################################################

        unit = self.ctl.graph.get_x_axis_unit()
        for label in self.cache:
            self.plot(title=label, 
                      y=self.cache[label]["y"],
                      x=self.cache[label]["x"][unit])

    def combo_callback(self):
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        combo = self.get_widget_from_name("Excitation")
        calibration = combo.currentIndex()
        
        # This will update our in-memory wavecal (wavelengths and wavenumbers),
        # SRM factors and so on.
        spec.settings.select_calibration(calibration)

        # The one remaining step is to actually send the new vertical ROI to
        # the spectrometer, since that change has to be applied to the FPGA.
        spec.change_device_setting("update_vertical_roi") 

        # update axis tooltip
        self.ctl.graph.update_visibility()
