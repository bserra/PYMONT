# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 14:55:28 2018

@author: bserra
"""

# test script to contact the UPS using the pyvisa library

import visa

rm = visa.ResourceManager('@py')

print (rm.list_resources())

UPS_str = 'ASRLCOM8::INSTR'

def __check_sum(hex_string):
    """ Method to return the checksum from the request
    src/dest/request/length/length for sending
    src/dest/request/length/length/data for receiving """
    checksum = sum(hex_string.encode())
#    print (checksum)
    for i in f"{checksum:#0{6}x}"[2:]: 
        hex_string+=i
#    print (hex_string)
    return hex_string

def fmt_ups(command):
    """Pad carriage return and line feed to a string

    :param request: list with the request
    :type request: list
    :returns: the padded string
    :rtype: str
    """
    BC, SRC, DEST, ETX = chr(2), '\x30', '\x31', chr(3)
    
    return BC+\
           __check_sum(SRC+DEST+command)+\
           ETX
           
GI = '\x47\x49\x30\x30'
SU = '\x52\x53\x30\x30'
UPS = rm.open_resource(UPS_str)
UPS.baud_rate = 1200
UPS.read_termination = '\x03'
UPS.write_termination = ''
print ('Termination',UPS.read_termination, UPS.write_termination)
print (fmt_ups(GI).encode())
test = UPS.query(fmt_ups(SU))
print (test)