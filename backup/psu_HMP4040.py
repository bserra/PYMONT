# -*- coding: utf-8 -*-
"""
Created on Wed May  2 16:50:24 2018

@author: bserra
"""

import serial as serial
import time

psu = serial.Serial(port='COM6', baudrate='9600', timeout=10)
print ('Connected to PSU')
a = '*IDN?'+chr(10)
print ('Command',a.encode())
psu.write(a.encode())
print ('Reading')
test = psu.readline().decode()
print (test)
print ('Sleeping')
time.sleep(5)

psu.close()
