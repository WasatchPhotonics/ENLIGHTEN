from EnlightenPlugin import EnlightenPluginBase

import wasatch

from wasatch.FeatureIdentificationDevice import FeatureIdentificationDevice

class XSWERS(EnlightenPluginBase):

    def get_configuration(self):
        self.name = "XSWERS"
        spec = self.ctl.multispec.current_spectrometer()
        
        self.field(name = "Toggle Acc State", datatype = "bool", direction = "input", callback = self.ToggleAccState)
        self.field(name = "Toggle GPIO State", datatype = "bool", direction = "input", callback = self.ToggleGPIOState)
        #self.field(name = "Control", datatype="combobox", direction = "input")
          
    def ToggleAccState(self):
        self.ctl.wasatch.set_accessory_enable(self)
        #self
        
    def ToggleGPIOState(self):
        self
