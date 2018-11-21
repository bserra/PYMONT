# -*- coding: utf-8 -*-
"""
Created on Wed May  2 17:45:05 2018

@author: bserra

Problem with no backend avalables
https://stackoverflow.com/questions/13773132/pyusb-on-windows-no-backend-available?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
add filter to usb serial device
"""

import socket
import json

import serial as serial
import time


  ############
#### DP831A #################################################################
  ############

# Code translations constants
MM_MODES = {
    'DC_V': 'MEASure:VOLTage:DC?',
    'DC_I': 'MEASure:CURRent:DC?',
    'AC_V': 'MEASure:VOLTage:AC?',
    'AC_I': 'MEASure:CURRent:AC?'
}

class DP831A(object):
    r"""Abstract class that implements the common driver for the model DP831A
    Programmable DC power supply. The driver implement the following x commands
    out of the 97 in the specification:

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

    def __init__(self, port='COM7',**kwargs):
        """Initialize internal variables and ethernet connection

        :param port: The communication serial port of the RIGOL
        :type TCP_IP: str
        """
        # The socket connection for TCP/IP should have a long buffer size
        try:
            self.inst_id = kwargs['type']+kwargs['id']+'_'
        except:
            self.inst_id = ''

        self.serial = serial.Serial(port=port, timeout=5, rtscts=True)
        self._connected = True
        
#        device_type = self._send_command('*IDN?')
        
    def close(self):
        """Stop the connection to the LakeShore"""
        self.serial.close()
        self._connected = False

    def connect(self):
        """Start connection with lakeshore"""
        self.__init__()

    def __test_cmd(self,cmd):
        """Testing command raw output"""
        results = self._send_command(cmd)
        return results
        
    def _lf(self, string):
        """Pad line feed to a string

        :param string: String to pad
        :type string: str
        :returns: the padded string
        :rtype: str
        """
        return string + self.LF

    def _send_command(self, command):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """
        if self._connected == True:
            if ';' in command:
                for i in command.split(';'):
                    self.serial.write((i+chr(10)).encode())
            else:
                self.serial.write(self._lf(command).encode())
            if '?' in command or '*' in command:
#                time.sleep(0.5)
                data = self.serial.readline().decode()
                data = data.rstrip(self.LF)
            else:
                data = 'Not a query'
        else:
            data = 'Not Connected'
            
        return data
        '''
        is there a error code for non valide command
        if response == self._cr_lf(self.NAK):
            message = 'Serial communication returned negative acknowledge'
            raise IOError(message)
        elif response != self._cr_lf(self.ACK):
            message = 'Serial communication returned unknown response:\n{}'\
                ''.format(repr(response))
            raise IOError(message)
        '''
        
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
            measure = self._send_command(':MEAS:ALL? CH'+str(i)).split(',')
            print (measure)
            results.update({self.inst_id+'Current OUT'+channel:measure[0],
                            self.inst_id+'Voltage OUT'+channel:measure[1],
                            self.inst_id+'Power OUT'+channel:measure[2]})

        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

