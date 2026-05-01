import logging

from enlighten.EnlightenFeature import EnlightenFeature

log = logging.getLogger(__name__)

class MultiPos(EnlightenFeature):
    """ Used for spectrometers with articulated optics. """
    
    def __init__(self, ctl):
        super().__init__(ctl)

        # need to point these to new widgets
        self.sb_pos    = sb_pos

        self.sb_pos.valueChanged.connect(self.position_changed)

        self.spec_wavecals = {}

        self.update_visibility()

    def update_visibility(self):
        spec = self.ctl.multispec.current_spectrometer()
        visible = self._has_multi(spec)
        self.sb_pos.setVisible(visible)

        # trigger event to ensure displayed position is active wavecal
        if visible:
            self.position_changed()

    def _has_multi(self, spec):
        if spec is None:
            return False
        return spec.settings.eeprom.multi_wavecal is not None

    ##
    # The caller wishes to reset the wavelength calibration of the given spectrometer to
    # that associated with the given grating position.
    def position_changed(self):
        spec = self.ctl.multispec.current_spectrometer()
        if not self._has_multi(spec):
            return

        pos = self.sb_pos.value()
        coeffs = spec.settings.eeprom.multi_wavecal.get(pos)
        if coeffs is None:
            log.error("no wavecal for position %d", pos)
            return

        spec.settings.update_wavecal(coeffs)
        spec.settings.state.position = pos
