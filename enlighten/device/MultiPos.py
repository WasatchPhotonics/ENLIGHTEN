##
# Used for spectrometers with articulated optics.
class MultiPos:
    
    def __init__(self, 
            multispec,
            sb_pos):

        self.multispec = multispec
        self.sb_pos    = sb_pos

        self.sb_pos.valueChanged.connect(self.position_changed)

        self.spec_wavecals = {}

        self.update_visibility()

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
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
        spec = self.multispec.current_spectrometer()
        if not self._has_multi(spec):
            return

        pos = self.sb_pos.value()
        coeffs = spec.settings.eeprom.multi_wavecal.get(pos)
        if coeffs is None:
            log.error("no wavecal for position %d", pos)
            return

        spec.settings.update_wavecal(coeffs)
        spec.settings.state.position = pos
