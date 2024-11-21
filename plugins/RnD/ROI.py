import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class ROI(EnlightenPluginBase):
    """
    Plugin goals:

    - allow the top chart spectra to be selectable between 785 and 633nm regions
      (but only one at a time)
    - allow the bottom chart to show both spectra (will overlap to different 
      degrees whether pixel, wavelength or wavenumber axis in effect)
    - both charts will use the same "currently selected" x-axis (allow user to change)
    - note the "unselected" wavelength will be "frozen" on the bottom graph, while the 
      "selected" wavelength will remain live
    - pressing "Save" will just save whatever is shown in the top graph

      +------------------------+
      |                        | 
      |        Top Chart       | Either 785 or 633 (not both)
      |                        |
      +------------------------+
      |                        | 
      |      Bottom Chart      | display both series (current x-axis)
      |                        |
      +------------------------+

    Cached calibration for test unit (WP-00860):

    - 785nm
        - vertical ROI (275, 475)
        - wavecal 755.2945 0.1831673 -5.324801e-05 1.981370e-08 -3.651564e-12
    - 633nm
        - vertical ROI (700, 875)
        - wavecal 593.1948 0.1359748 -2.853866e-05 6.422492e-09 -6.287138e-13
    """

    def get_configuration(self):
        self.name = "ROI"
        self.has_other_graph = True
        self.field(name="Excitation", datatype="combobox", direction="input", choices=['785nm', '633nm'], callback=self.combo_callback)
        self.cached_data = {}

    def process_request(self, request):
        settings = request.settings
        if not settings.is_micro():
            self.marquee_message = "ROI plugin requires XS series"
            return

        if not settings.eeprom.subformat == 5:
            self.marquee_message = "ROI plugin requires EEPROM subformat 5"
            return

        ########################################################################
        # cache this reading
        ########################################################################

        pr = request.processed_reading 
        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()

        excitation = round(settings.excitation(), 0)
        label = f"{excitation}nm"

        unit = self.ctl.graph.get_x_axis_unit()
        if   unit == "nm": x = pr.get_wavelengths()
        elif unit == "cm": x = pr.get_wavenumbers()
        else:              x = pr.get_pixel_axis()

        self.cached_data[label] = (x, pr.get_processed())

        ########################################################################
        # graph latest spectrum from all excitations
        ########################################################################

        for label, spectrum in self.cached_data.items():
            self.plot(title=label, x=spectrum[0], y=spectrum[1])

    def save_callback(self):
        log.info("save_callback: here")

    def combo_callback(self):
        log.debug("combo_callback: here")

        combo = self.get_widget_from_name("Excitation")
        calibration = combo.currentIndex()
        log.debug(f"combo_callback: index {calibration}")
        
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        ########################################################################
        # We could (and should) just do:
        #
        #    spec.change_device_setting("update_vertical_roi") 
        #
        # but I want it to happen immediately for debugging purposes
        ########################################################################

        log.debug("combo_callback: wavelength range was ({spec.settings.wavelengths[0]:.2f}, {spec.settings.wavelengths[-1]:.2f})")
        spec.settings.select_calibration(calibration)
        fid = spec.device.wrapper_worker.connected_device.hardware
        fid.update_vertical_roi()
        log.debug("combo_callback: wavelength range now ({spec.settings.wavelengths[0]:.2f}, {spec.settings.wavelengths[-1]:.2f})")
