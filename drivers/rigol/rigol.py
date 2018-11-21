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
import sys

# Code translations constants
MM_MODES = {
    'DC_V': 'MEASure:VOLTage:DC?',
    'DC_I': 'MEASure:CURRent:DC?',
    'AC_V': 'MEASure:VOLTage:AC?',
    'AC_I': 'MEASure:CURRent:AC?'
}

#### DP 831A ##################################################################

class DP831A(object):
    r"""Abstract class that implements the common driver for the model DP831A
    Programmable DC power supply. The driver implement the following x commands

    """

    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 RESOURCE_TIMEOUT = 5,
                 TERMINATION_STRING = '\n',
                 **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the Rigol device
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\n' by default for Rigol
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
        for i in [1,2,3]:
#            self._send_command(':INST CH'+str(i))
#            channel = self._send_command(':INST?')[2]
            channel = str(i)
            measure = self.instrument.query(':MEAS:ALL? CH'+str(i)).split(',')
            results.update({self.inst_id+'curr_OUT'+channel:[measure[0], '[A] Current output '+channel],
                            self.inst_id+'volt_OUT'+channel:[measure[1], '[V] Bias output '+channel],
                            self.inst_id+'pow_OUT'+channel:[measure[2], '[W] Power output '+channel]})

        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

#### DG 1000Z #################################################################

class DG1000Z(object):
    r"""Abstract class that implements the common driver for the model DG1000Z
    Programmable waveform generator. The driver implement the following x commands

    * *IDN?: Identifiation query (model identification)

    This class also contains the following class variables, for the specific
    characters that are used in the communication:

    :var LF: Line feed, chr(10), \\n
    """

    LF = chr(10)

    def __init__(self, 
                 RESOURCE_STRING, 
                 TERMINATION_STRING = '\n',
                 RESOURCE_ID = '',
                 RESOURCE_MANAGER = None,
                 RESOURCE_TIMEOUT = 5,
                 **kwargs):
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the Lakeshore
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\n' by default for Rigol devices
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
        id_channel = 1
        try:
            while id_channel <= 2:
                measure = self.instrument.query(':SOUR:APPL?')[1:-1].split(',')
                results.update({self.inst_id+'wavef_CH'+str(id_channel):[measure[0], '[str] Waveform Channel '+str(id_channel)],
                                self.inst_id+'freq_CH'+str(id_channel):[measure[1], '[Hz] Frequency Channel '+str(id_channel)],
                                self.inst_id+'amp_CH'+str(id_channel):[measure[2], '[V] Amplitude Channel '+str(id_channel)],
                                self.inst_id+'offs_CH'+str(id_channel):[measure[3], '[V] Offset Channel '+str(id_channel)],
                                self.inst_id+'phase_CH'+str(id_channel):[measure[4], '[deg] Phase Channel '+str(id_channel)]})
            
                id_channel += 1        
        except:
            [results.update({self.inst_id+'VAR'+str(idx):value}) for idx, value in enumerate(measure)]
        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

#### DM3068 ##################################################################

class DM3068(object):
    r"""Abstract class that implements the common driver for the model DP831A
    Programmable DC power supply. The driver implement the following x commands

    """
    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 RESOURCE_TIMEOUT = 5,
                 TERMINATION_STRING = '\n',
                 **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the Rigol device
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\n' by default for Rigol
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
        measure = self.instrument.query(':MEASure:VOLTage:DC?')
#        measure = self.instrument.query('*IDN?')
        results.update({self.inst_id+'V_DC':[measure,'[V] V DC']})

        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results