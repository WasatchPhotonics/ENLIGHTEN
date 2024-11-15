import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class ROI(EnlightenPluginBase):
    """
    Plugin goals:

    - allow the top chart spectra to be toggled between 785 and 633nm regions
    - allow the bottom chart to show both spectra (stitched in wavelength axis, 
      or overlapped in pixel or wavenumber axis)
      +------------------------+
      |                        | 
      |        Top Chart       | Options: 785 or 633
      |                        |
      +------------------------+
      |                        | 
      |      Bottom Chart      | Options: both (pixel, wavelength or wavenumber axis)
      |                        |
      +------------------------+
    - pressing "Save" will just save whatever is shown in the top graph
    - see ENG-0034 Rev 17+ for Subformat 5: Dual-Wavelength Raman
    """

    def get_configuration(self):
        self.name = "ROI"
        self.has_other_graph = True

        self.field(name="Excitation", datatype="combo", direction="input", choices=['785nm', '633nm'], callback=self.combo_callback)
        self.field(name="Save", datatype="button", callback=self.save)

        self.last_data = {}

    def process_request(self, request):
        settings = request.settings
        if not settings.is_micro():
            self.marquee_message = "ROI plugin requires XS series"
            return

        pr = request.processed_reading 
        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()

    def save_callback(self):
        log.info("save_callback: here")

    def combo_callback(self):
        log.debug("combo_callback: here")

        combo = self.get_widget_from_name("Excitation"):
        index = combo.currentIndex()
        log.debug(f"combo_callback: index {index}")
        
        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            return

        log.debug("wavelength range was ({spec.settings.wavelengths[0]:.2f}, {spec.settings.wavelengths[-1]:.2f})")
        spec.settings.set_selected_multi_wavelength_index(index)
        log.debug("wavelength range now ({spec.settings.wavelengths[0]:.2f}, {spec.settings.wavelengths[-1]:.2f})")
