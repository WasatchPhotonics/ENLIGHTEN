#!/usr/bin/env python
# coding: utf-8

# # Motor Interface

# Here we define the helper functions and import the libraries needed to control the 
# Arduino for dual stepper motors X/Y easily
# 

# This module defines the following functions.
# The first returns the serial interface object, all others return a string with an error message,
# the value, or 'ok'
# 
# * ser = openSerial()
# * closeSerial(ser)
#

#
# DualStepperTestWithLibraryAndUSB.ino
#

##
##Welcome to the Dual Stepper Controller
##For all Commands, specify the stepper with ^ = 'X' or 'Y' (^ symbolizes direction)
##For some Commands add '###' = the desired number (any number of digits)
##Possible Commands are:
##sM^###  = set_max_speed(float new_max_speed)
##sP^###  = set_position(long new_position)
##sS^###  = set_speed(float new_speed)
##sA^###  = set_acceleration(float new_acceleration)
##rM^     = float read_max_speed()
##rP^     = long read_position()
##rS^     = float read_speed()
##rA^     = float read_acceleration()
##rT^     = long read_target_position()
##fH^     = find_home_position()
#
# after every completion (travel stopped) the Arduino sends an 'OK'
#


# ## Installation

# Requires
# 
# * sudo python3 -m pip install pyserial
# 
# Also, add user to group tty and dialout with
# 
# * sudo usermod -a -G dialout username
# * sudo usermod -a -G tty username
#     
# for access to USB port
# 



import os
import re
import time
import logging

import warnings
import serial
# the following really only needed for Windows...
# but - maybe the same code also works for UNIX?
import serial.tools.list_ports

log = logging.getLogger(__name__)

# expected Arduino port - UNIX
# PORT = "ttyACM.*"
# DEV_DIR = '/dev'

# in Windows
#ARDUINO = "USB-SERIAL CH340"
ARDUINO = "Arduino"

# code for Windows - skip for UNIX
arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if ARDUINO in p.description  # may need tweaking to match new arduinos
]
if not arduino_ports:
    raise IOError("No Arduino found")
if len(arduino_ports) > 1:
    warnings.warn('Multiple Arduinos found - using the first')


# this holds for both steppers:
# given the spindles (5 mm per rev)
# and quarter steps jumpers in CNC shield
# and 200 (full) steps per revolution for stepper motor
# --> 5000 um per 800 steps:

MICRONS_PER_STEP = 6.25



class Mapper(object):

    # this is two steppers, one X, one Y
    # this will connect to serial and
    # generate two stepper objects

    def __init__(self):
        self.device = None
        self.ser = None
        if self.connect():   # this opens port and defines self.ser
            self.device = True
            self.x = Stepper(self.ser, 'X')
            self.y = Stepper(self.ser, 'Y')

    def get_serial_line(self):
        data = self.ser.readline()
        return data.decode().rstrip()

    def connect(self):
        print("Connecting to Arduino...")
        # this is for UNIX - maybe also use Windows code?
#        r = re.compile(PORT)
#        all_interfaces = os.listdir(DEV_DIR)
#        serial_interfaces = list(filter(r.match, all_interfaces))
        # for UNIX replace 'arduino_ports' with serial_interfaces
        if len(arduino_ports) == 0:
            return False
        else:
            print(f"Interface: {arduino_ports[0]}")
            self.ser = self.open_port(arduino_ports[0])
            time.sleep(3)
            resp = self.get_serial_line()
            while not resp == 'OK':
#                print(resp)
                time.sleep(0.1)
                resp = self.get_serial_line()
            print("Connected to Mapper")
            return True

    def open_port(self, serial_interface):
        # this is for UNIX
#         ser = serial.Serial(port='/dev/{}'.format(serial_interface))
        # this is for Windows
        ser = serial.Serial(serial_interface)
        ser.baudrate = 115200
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.bytesize = serial.EIGHTBITS
        ser.timeout = 1
        return ser

    def disconnect(self):
        if self.ser:
            self.ser.close()
            self.ser = None
        if self.device:
            self.device = None
            del self.x
            del self.y
        print("Disconnected from Mapper")
        return True


class Stepper(object):

    def __init__(self, ser, direction):
        if ser is None:
            raise ValueError("Serial Port must be provided for Stepper")
        self.ser = ser  # serial port
        if not direction in ['X', 'Y']:
            raise ValueError("Stepper Direction must be 'X' or 'Y'")
        self.direction = direction  # a single letter 'X' or 'Y'
        self.microns_per_step = MICRONS_PER_STEP  # we simply use the global default here

    def um_to_steps(self, um):
        return round(um / self.microns_per_step)

    def mm_to_steps(self, mm):
        um = 1000 * mm
        return self.um_to_steps(um)

    def steps_to_um(self, steps):
        return steps * self.microns_per_step

    def steps_to_mm(self, steps):
        um = self.steps_to_um(steps)
        return um / 1000

    def get_serial_line(self):
        data = self.ser.readline()
        return data.decode().rstrip()

    def read_resp(self):
        full_resp = ""
        resp = self.get_serial_line()
        while not resp == 'OK':
            full_resp = full_resp + resp
            resp = self.get_serial_line()
        return full_resp        

    def send_cmd(self, cmd):
        code_to_send = cmd + '\r\n'
        data = bytearray(code_to_send.encode('utf-8'))
        No = self.ser.write(data)
        if No == len(code_to_send):
            # get response
            resp = self.read_resp()
        else:
            resp = 'read response error'
        return resp

# For all Commands, specify the stepper with ^ = 'X' or 'Y' (^ symbolizes direction)
# For some Commands add '###' = the desired number (any number of digits)
# Possible Commands are:

# sM^###  = set_max_speed(float new_max_speed)

    def set_max_speed(self, new_max_speed):
        cmd = "sM" + self.direction + str(new_max_speed)
        resp = self.send_cmd(cmd)
        return resp


# sP^###  = set_position(long new_position)

    def set_position(self, new_position):
        cmd = "sP" + self.direction + str(new_position)
        resp = self.send_cmd(cmd)
        return resp

    def set_position_mm(self, new_position_mm):
        new_position = self.mm_to_steps(new_position_mm)
        return self.set_position(new_position)

    def set_position_um(self, new_position_um):
        new_position = self.um_to_steps(new_position_um)
        return self.set_position(new_position)

# sS^###  = set_speed(float new_speed)

    def set_speed(self, new_speed):
        cmd = "sS" + self.direction + str(new_speed)
        resp = self.send_cmd(cmd)
        return resp


# sA^###  = set_acceleration(float new_acceleration)

    def set_acceleration(self, new_acceleration):
        cmd = "sA" + self.direction + str(new_acceleration)
        resp = self.send_cmd(cmd)
        return resp


# rM^     = float read_max_speed()

    def read_max_speed(self):
        cmd = "rM" + self.direction
        resp = self.send_cmd(cmd)
        return resp


# rT^     = long read_target_position()

    def read_position(self):
        cmd = "rP" + self.direction
        resp = self.send_cmd(cmd)
        return resp

    def read_position_um(self):
        position = int(self.read_position())
        return round(self.steps_to_um(position))

    def read_position_mm(self):
        return round(self.read_position_um() / 1000, 3)


# rS^     = float read_speed()

    def read_speed(self):
        cmd = "rS" + self.direction
        resp = self.send_cmd(cmd)
        return resp


# rA^     = float read_acceleration()

    def read_acceleration(self):
        cmd = "rA" + self.direction
        resp = self.send_cmd(cmd)
        return resp

# rT^     = long read_target_position()

    def read_target_position(self):
        cmd = "rT" + self.direction
        resp = self.send_cmd(cmd)
        return resp

    def read_target_position_um(self):
        target_position = int(self.read_target_position())
        return round(self.steps_to_um(target_position))

    def read_target_position_mm(self):
        return round(self.read_target_position_um() / 1000, 3)


# fH^     = find_home_position()

    def find_home_position(self):
        cmd = "fH" + self.direction
        resp = self.send_cmd(cmd)
        return resp


# mH^     = move_to_home_position()

    def move_to_home_position(self):
        cmd = "mH" + self.direction
        resp = self.send_cmd(cmd)
        return resp


# mA^###  = move_absolute(long new_target)

    def move_absolute(self, new_target):
        cmd = "mA" + self.direction + str(new_target)
        resp = self.send_cmd(cmd)
        return resp

    def move_absolute_um(self, new_target_um):
        new_target = self.um_to_steps(new_target_um)
        return self.move_absolute(new_target)

    def move_absolute_mm(self, new_target_mm):
        new_target = self.mm_to_steps(new_target_mm)
        return self.move_absolute(new_target)


# mR^###  = move_relative(long distance)

    def move_relative(self, distance):
        cmd = "mR" + self.direction + str(distance)
        resp = self.send_cmd(cmd)
        return resp

    def move_relative_um(self, distance_um):
        distance = self.um_to_steps(distance_um)
        return self.move_relative(distance)

    def move_relative_mm(self, distance_mm):
        distance = self.mm_to_steps(distance_mm)
        return self.move_relative(distance)



# Test

#if __name__ == "__main__":

    #mapper = Mapper()
    #if mapper.device:
        #print("Current Position: ", mapper.x.read_position(), mapper.y.read_position())
        #print("Move 2000 Steps in X... ", mapper.x.move_relative(2000))
        #print("Move 1000 Steps in Y... ", mapper.y.move_relative(1000))
        #print("Current Position: ", mapper.x.read_position(), mapper.y.read_position())
        #print("Current Position (mm): ", mapper.x.read_position_mm(), mapper.y.read_position_mm())
        #print("Find Home Position in X... ", mapper.x.find_home_position())
        #print("Find Home Position in Y... ", mapper.y.find_home_position())
        #print("Current Position: ", mapper.x.read_position(), mapper.y.read_position())
        #print("Move 5000 Steps in X... ", mapper.x.move_relative(5000))
        #print("Move 20 mm in Y... ", mapper.y.move_relative_mm(20))
        #print("Current Position: ", mapper.x.read_position(), mapper.y.read_position())
        #print("Current Position (mm): ", mapper.x.read_position_mm(), mapper.y.read_position_mm())
        #print("Move 100 um in X... ", mapper.x.move_relative_um(100))
        #print("Current Position (mm): ", mapper.x.read_position_mm(), mapper.y.read_position_mm())
        #print("Closing...: ", mapper.disconnect())
    #else:
        #print("Mapper not found!")

    #print('### DONE ###')

