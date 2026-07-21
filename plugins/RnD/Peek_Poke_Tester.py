import usb.core
import argparse
import sys
import logging
import os
from EnlightenPlugin import EnlightenPluginBase
log = logging.getLogger(__name__)

#pid = 0x4000
dev = usb.core.find(idVendor = 0x24aa, idProduct = 0x4000)
HOST_TO_DEVICE = 0x40
DEVICE_TO_HOST = 0xC0
Timeout_ms = 1000  


class Peek_Poke_Tester(EnlightenPluginBase):    
    
    def get_configuration(self):         
        self.name = "Register Peek"
        self.process_requests = False
        
        self.field(name = "Address", datatype = str, direction = "input") 
        self.field(name = "Length", datatype = str, direction = "input") 
        self.field(name = "Value", datatype = str, direction = "output")
        self.field(name = "Peek", datatype = "button", callback = self.run_peek)
        
    def process_request(self, request):        
        self.address = request.fields["Address"]
        self.length = request.fields["Length"]
    
    def run_peek(self):               
        data = self.get_cmd(address = self.address, length = self.length)
        data_hex = " ".join([f"{v:02x}" for v in data])
        log.debug(f"data: {data}")
        log.debug(f"data_hex: {data_hex}")
        log.debug(f'Result Print: {self.address} << 0x{data_hex} ({len(data)} bytes)')
        self.outputs["Value"] = f'0x{data_hex}'
        
    def get_cmd(self, address: int, value: int = 0, index: int = 0, length: int = 64, lsb_len: int = None, msb_len: int = None):
        result = None
        
        log.debug(f"Device: {DEVICE_TO_HOST}")
        log.debug(f"Address: {address}")
        log.debug(f"value: {value}")
        log.debug(f"index: {index}")
        log.debug(f"length: {length}")
        log.debug(f"lsb_len: {lsb_len}")
        log.debug(f"msb_len: {msb_len}")
        
        result = dev.ctrl_transfer(
            bmRequestType =     DEVICE_TO_HOST, 
            bRequest =          int(address, 16),
            wValue =            value, 
            wIndex =            index, 
            data_or_wLength =   length,
            timeout =           Timeout_ms)
        
        log.debug(f"Result: {result}")

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
