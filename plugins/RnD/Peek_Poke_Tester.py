import usb.core
import argparse
import sys
import logging
import os

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

HOST_TO_DEVICE = 0x40
DEVICE_TO_HOST = 0xC0
Timeout_ms = 1000  

class Peek_Poke_Tester(EnlightenPluginBase):
    """
    Besides meeting an immediate need for technicians and engineers desiring to 
    use the new USB "peek/poke" functionality to directly read and write FPGA 
    registers from ENLIGHTEN, also provides an example of how to directly talk
    to a spectrometer's low-level USB interface from an ENLIGHTEN plugin (not
    that this is something we'd want to commonly do).
    """
    
    def get_configuration(self):         
        self.name = "Register Peek"
        self.process_requests = False
        
        self.field(name = "Address", datatype = str, direction = "input", tooltip="values should be entered in hex (leading 0x optional)") 
        self.field(name = "Length", datatype = int, direction = "input", minimum=1, maximum=64, initial=1) 
        self.field(name = "Value", datatype = str, direction = "output")
        self.field(name = "Peek", datatype = "button", callback = self.run_peek)
        
        self.field(name = "Poke Address", datatype = str, direction = "input", tooltip = "values should be entered in hex (leading 0x optional)")
        self.field(name = "Poke Value", datatype = str, direction = "input", tooltip = "values should be entered in hex (leading 0x optional)")
        self.field(name = "Poke", datatype = "button", callback = self.run_poke)
        
#############################################
# Peek Commands
#############################################
    
    def run_peek(self):               
        ########################################################################
        # get existing handle to usb.core.Device
        ########################################################################

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.ctl.marquee.error("PeekPokeTester requires spectrometer")
            return

        if not spec.settings.is_xs():
            self.ctl.marquee.error("PeekPokeTester requires XS")
            return

        wdw = spec.device # a wasatch.WasatchDeviceWrapper
        worker = wdw.wrapper_worker # a wasatch.WrapperWorker
        wasatch_device = worker.connected_device # a wasatch.WasatchDevice (since we already confirmed it's an XS)
        fid = wasatch_device.hardware # a wasatch.FeatureInterfaceDevice
        usb_core_device = fid.device # a usb.core.Device from pyusb

        ########################################################################
        # get peek address and length
        ########################################################################

        address = int(self.get_widget_from_name("Address").text().lower().removeprefix("0x"), 16)
        length = int(self.get_widget_from_name("Length").value())

        ########################################################################
        # perform the peek
        ########################################################################

        data = self.get_cmd(dev=usb_core_device, cmd=0x91, value=address, length=length)
        if data is None:
            self.ctl.marquee.error("PeekPokeTester peek returned None")
            return

        data_hex = " ".join([f"{v:02x}" for v in data])
        log.debug(f"data: {data}")
        log.debug(f"data_hex: {data_hex}")
        log.debug(f'Result Print: {address} << 0x{data_hex} ({len(data)} bytes)')

        self.get_widget_from_name("Value").setText(f"0x{data_hex}")
        self.ctl.marquee.info(f"Peek 0x{address:02x} -> 0x{data_hex}")
        
    def get_cmd(self, dev, cmd: int, value: int = 0, index: int = 0, length: int = 64, lsb_len: int = None, msb_len: int = None):
        result = None
        
        #log.debug(f"Device: {dev}")
        #log.debug(f"cmd: {cmd}")
        #log.debug(f"value: {value}")
        #log.debug(f"index: {index}")
        #log.debug(f"length: {length}")
        #log.debug(f"lsb_len: {lsb_len}")
        #log.debug(f"msb_len: {msb_len}")
        
        result = dev.ctrl_transfer(
            bmRequestType =     DEVICE_TO_HOST, 
            bRequest =          cmd,
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

#############################################
# Poke Commands
#############################################

    def run_poke(self):
        ########################################################################
        # get existing handle to usb.core.Device
        ########################################################################

        spec = self.ctl.multispec.current_spectrometer()
        if spec is None:
            self.ctl.marquee.error("PeekPokeTester requires spectrometer")
            return

        if not spec.settings.is_xs():
            self.ctl.marquee.error("PeekPokeTester requires XS")
            return

        wdw = spec.device # a wasatch.WasatchDeviceWrapper
        worker = wdw.wrapper_worker # a wasatch.WrapperWorker
        wasatch_device = worker.connected_device # a wasatch.WasatchDevice (since we already confirmed it's an XS)
        fid = wasatch_device.hardware # a wasatch.FeatureInterfaceDevice
        usb_core_device = fid.device # a usb.core.Device from pyusb
        
        
        ########################################################################
        # get poke address and value
        ########################################################################
        
        poke_address = int(self.get_widget_from_name("Poke Address").text().lower().removeprefix("0x"), 16)
        poke_value = [int(self.get_widget_from_name("Poke Value").text().lower().removeprefix("0x"), 16)]
        
        # initialize buffer from values
        buf = [ x for x in poke_value ]

        # ensure at least 8 elements in buffer
        while len(buf) < 8:
            buf.append(0)
        
        data = self.send_cmd(dev = usb_core_device, cmd = 0x90, value = poke_address, index = len(poke_value), buf = buf)
    
    
    def send_cmd(self, dev, cmd, value, index, buf = None):        
        #log.debug(f"Device: {dev}")
        #log.debug(f"cmd: {cmd}")
        #log.debug(f"value: {value}")
        #log.debug(f"index: {index}")
        #log.debug(f"length: {length}")
        #log.debug(f"lsb_len: {lsb_len}")
        #log.debug(f"msb_len: {msb_len}")        
        
        dev.ctrl_transfer(
            HOST_TO_DEVICE, 
            cmd, 
            value, 
            index, 
            buf, 
            Timeout_ms)