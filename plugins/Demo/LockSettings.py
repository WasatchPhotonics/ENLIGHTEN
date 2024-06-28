from EnlightenPlugin import EnlightenPluginBase

class LockSettings(EnlightenPluginBase):
    """ Shows how a plugin can lock various standard ENLIGHTEN features.  """

    def get_configuration(self):
        self.ctl.gain_db_feature.set_locked(True)
        self.ctl.laser_control.set_locked(True)
