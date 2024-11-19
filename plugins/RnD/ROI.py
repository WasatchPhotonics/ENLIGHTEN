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

    - top 785nm: (275, 475) (DB: 300-500), 755.2945 0.1831673 -5.324801e-05 1.981370e-08 -3.651564e-12 (or 759.2180 0.1659797 -2.717170e-05 3.396489e-09)
    - bot 633nm: (700, 875) (DB: 700-900), 593.1948 0.1359748 -2.853866e-05 6.422492e-09 -6.287138e-13 (or 593.7395 0.1334855 -2.456576e-05 3.772129e-09)
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
