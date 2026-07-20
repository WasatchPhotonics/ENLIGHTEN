import usb.core
import argparse
import sys
import logging
import os
import platform
from EnlightenPlugin import EnlightenPluginBase
log = logging.getLogger(__name__)
#from wasatch.FeatureIdentificationDevice import FeatureIdentificationDevice

#pid = 0x4000
dev = usb.core.find(idVendor = 0x24aa, idProduct = 0x4000)
HOST_TO_DEVICE = 0x40
DEVICE_TO_HOST = 0xC0
TIMEOUT_MS = 1000  


class Peek_Poke_Tester(EnlightenPluginBase):    
    
    def get_configuration(self):        
        self.name = "Registrar Peek"
        self.process_requests = False
        
        self.field(name = "Address", datatype = str, direction = "input")
        self.field(name = "Length", datatype = str, direction = "input")
        self.field(name = "Peek", datatype = "button", callback = self.run_peek)
        
        #self.run_peek()
        
    def process_request(self, request):        
        self.address = str(request.fields["Address"])
        self.length = str(request.fields["Length"])
    
    def run_peek(self):
        values = []
        
        progname = sys.argv.pop(0)
        
        #data = self.get_cmd(0x91, self.address, length = self.length)
        data = self.get_cmd(address = self.address, length = self.length)
        data_hex = " ".join([f"{v:02x}" for v in data])
        values = f"0x{self.address:02x} << 0x{data_hex} ({len(data)} bytes)"
        
        
        ########################################################################
        # Output report
        ########################################################################
        
        
        label_text = f"Registrar peek on {model} {sn} at {self.address}:"

        html = ""
        html += self.html_list("Notes", values)
            
        self.ctl.gui.msgbox_with_scrolling_html("Registry Check", label_text, html)

    def get_cmd(self, address, value = 0, index = 0, length = 64, lsb_len=None, msb_len=None):
        
        log.debug(f"Device: {DEVICE_TO_HOST}")
        log.debug(f"Address: {address}")
        log.debug(f"value: {value}")
        log.debug(f"index: {index}")
        log.debug(f"length: {length}")
        log.debug(f"lsb_len: {lsb_len}")
        log.debug(f"msb_len: {msb_len}")
        
        result = dev.ctrl_transfer(
            bmRequestType = DEVICE_TO_HOST, 
            bRequest = address, 
            wValue = value, 
            wIndex = index, 
            data_or_wLength = length, 
            timeout = TIMEOUT_MS)              

        value = 0
        if msb_len is not None:
            for i in range(msb_len):
                value = value << 8 | result[i]
            return value
        elif lsb_len is not None:
            for i in range(lsb_len):
                value = (result[i] << (8 * i)) | value
            return value
        else:
            return result

    def html_list(self, name, a):
        if len(a) == 0:
            return ""
        return f"{name}:<ul><li>" + "</li><li>".join(a) + "</li></ul>"
