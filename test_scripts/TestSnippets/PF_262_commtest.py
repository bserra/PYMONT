# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 11:13:01 2018

@author: irlab
"""

import time
import serial

ser = serial.Serial('COM1')  # open serial port
print(ser.name)         # check which port was really used
ser.write('PRX\r\n')
a = ser.readline().rstrip(chr(10)).rstrip(chr(3))
print a
ser.write(chr(5))
b = ser.readline().rstrip(chr(10)).rstrip(chr(3))
print b
ser.close()
