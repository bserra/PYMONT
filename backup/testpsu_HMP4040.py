# -*- coding: utf-8 -*-
"""
Created on Wed May  2 16:50:24 2018

@author: bserra
"""

import serial as serial
import time

psu = serial.Serial(port='COM6', timeout=10)
print ('Connected to PSU')
a = 'INST OUT1;VOLT?'

for i in a.split(';'):
    psu.write((i+chr(10)).encode())

print ('Command',a.encode())
psu.write(a.encode())
print ('Reading')
test = psu.readline().decode()
print (test)
print ('Sleeping')
time.sleep(1)

psu.close()
