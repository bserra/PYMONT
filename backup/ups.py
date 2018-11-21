# -*- coding: utf-8 -*-
import time
import serial
import numpy as np
#
#STX = chr(0x02)
#ETX = chr(0x03)
#ACQ = chr(0x06)
#NAQ = chr(0x15)
#SRC = chr(0x20)
#DEST = chr(0x20)
#
#
def to_bits(hexa):
    return bin(int(hexa, 16))[2:].zfill(8)

a=np.array(['02','30','31','47','49','30','30','30','31','35','31','03'])
test_str = [0x02,0x30,0x31,0x47,0x49,0x30,0x30,0x30,0x31,0x35,0x31,0x03]
test_str = [0x02,0x30,0x31,0x52,0x53,0x30,0x30,0x35,0x3e,0x3d,0x3b,0x03] 
test_str = [0x02,0x30,0x31,0x52,0x53,0x30,0x30,0x30,0x31,0x36,0x36,0x03] 
test = serial.Serial(port='COM5', baudrate=1200, timeout=1)

test.flushInput() #flush input buffer, discarding all its contents
test.flushOutput()#flush output buffer, aborting current output
print (test_str)
print (serial.to_bytes(test_str))

test.write(serial.to_bytes(test_str))
response = test.readline()

print (response)
'''
#for i in a:
#    print (to_bits(i))
#b = ''.join([str(i) for i in a])
#c = ''.join(['0x'+i for i in a])
#for i in test_str:
#    print (to_bits(i))
#    print (i.encode())
#    test.write(i.encode())
#test.write('\r\n'.encode())
#test.write(test_str.encode())    

'''