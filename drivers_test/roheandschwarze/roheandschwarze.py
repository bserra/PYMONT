# -*- coding: utf-8 -*-
"""
Created on Wed May  2 17:45:05 2018

@author: bserra

Problem with no backend avalables
https://stackoverflow.com/questions/13773132/pyusb-on-windows-no-backend-available?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
add filter to usb serial device
"""

import json
import time
from numpy import size, unique
import sys

# Code translations constants
MM_MODES = {
    'DC_V': ('MEASure:VOLTage:DC?','[V]'),
    'DC_I': ('MEASure:CURRent:DC?','[A]'),
    'AC_V': ('MEASure:VOLTage:AC?','[V]'),
    'AC_I': ('MEASure:CURRent:AC?','[A]')
}

#### HMC 8012 #################################################################

class HMC8012(object):
    r"""Abstract class that implements the common driver for the model 336 
    temperature controller. The driver implement the following 12 commands out 
    the 97 in the specification:

    * *IDN?: Identifiation query (model identification)

    This class also contains the following class variables, for the specific
    characters that are used in the communication:

    :var ETX: End text (Ctrl-c), chr(3), \\x15
    :var CR: Carriage return, chr(13), \\r
    :var LF: Line feed, chr(10), \\n
    :var ENQ: Enquiry, chr(5), \\x05
    :var ACK: Acknowledge, chr(6), \\x06
    :var NAK: Negative acknowledge, chr(21), \\x15
    """

    LF = chr(10)

    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 TERMINATION_STRING = '\n',
                 RESOURCE_TIMEOUT = 5,
                 **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the agilent
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\n' by default for agilent
        :type TERMINATION_STRING: str
        """
        try:
            self.instrument = RESOURCE_MANAGER.open_resource(RESOURCE_STRING,
                                                             open_timeout = RESOURCE_TIMEOUT)
            self.instrument.read_termination = TERMINATION_STRING
            self.instrument.write_termination = TERMINATION_STRING
            self.instrument.timeout = RESOURCE_TIMEOUT
            self.connected = True
        except:
            self.connected = False

        try:
            self.inst_id = RESOURCE_ID+'_'
        except:
            self.inst_id = ''
        
        self.mode = kwargs['RESOURCE_CONFIG']
        self.instrument.write(MM_MODES[self.mode][0])
        if RESOURCE_MANAGER == None:
            sys.exit('No VISA resource manager found')
        
    def fetch(self):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """   
        return {self.inst_id+self.mode:(self.instrument.query('FETC?'), MM_MODES[self.mode][1]+' '+self.mode)}
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

#### HMP 4040 #################################################################

class HMP4040(object):
    r"""Abstract class that implements the common driver for the model HMC 4040
    power supply. The driver implement the following 12 commands out 
    the 97 in the specification:

    * *IDN?: Identifiation query (model identification)

    This class also contains the following class variables, for the specific
    characters that are used in the communication:

    :var ETX: End text (Ctrl-c), chr(3), \\x15
    :var CR: Carriage return, chr(13), \\r
    :var LF: Line feed, chr(10), \\n
    :var ENQ: Enquiry, chr(5), \\x05
    :var ACK: Acknowledge, chr(6), \\x06
    :var NAK: Negative acknowledge, chr(21), \\x15
    """

    LF = chr(10)

    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 RESOURCE_TIMEOUT = 5,
                 TERMINATION_STRING = '\n',
                 **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the agilent
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\n' by default for agilent
        :type TERMINATION_STRING: str
        """
        try:
            self.instrument = RESOURCE_MANAGER.open_resource(RESOURCE_STRING,
                                                             open_timeout = RESOURCE_TIMEOUT)
            self.instrument.read_termination = TERMINATION_STRING
            self.instrument.write_termination = TERMINATION_STRING
            self.instrument.timeout = RESOURCE_TIMEOUT
            self.connected = True
        except:
            self.connected = False

        try:
            self.inst_id = RESOURCE_ID+'_'
            print (self.inst_id)
        except:
            self.inst_id = ''
        
        if RESOURCE_MANAGER == None:
            sys.exit('No VISA resource manager found')

    def fetch(self):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """   
        results = dict()
        for i in [1,2,3,4]:
            self.instrument.query('INST OUT'+str(i))
            self.mode='Volts OUT'+str(i)
            results.update({self.inst_id+self.mode:(self.instrument.query('MEAS:VOLT?'),'[V] Bias channel '+str(i))})
            self.mode='Current OUT'+str(i)
            results.update({self.inst_id+self.mode:(self.instrument.query('MEAS:CURR?'),'[A] Current channel '+str(i))})
#            time.sleep(0.05)

        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

