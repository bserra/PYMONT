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

    :var LF: Line feed, chr(10), \\n
    """

    LF = chr(10)

    def __init__(self, TCP_IP='169.254.1.5', TCP_PORT=5555, BUFFER_SIZE=1024,**kwargs):
        """Initialize internal variables and ethernet connection

        :param TCP_IP: The adress of the Lakeshore
        :type TCP_IP: str
        :param TCP_PORT: 5555 is the default
        :type TCP_PORT: int
        :param BUFFER_SIZE: 1024
        :type BUFFER_SIZE: int
        """
        # The socket connection for TCP/IP should have a long buffer size
        try:
            self.inst_id = kwargs['type']+kwargs['id']+'_'
        except:
            self.inst_id = ''

        self.BUFFER_SIZE = BUFFER_SIZE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
        self._connected = True
        
        device_type = self._send_command('*IDN?')
        
    def close(self):
        """Stop the connection to the LakeShore"""
        self.socket.close()
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
                    self.socket.send((i+chr(10)).encode())
            else:
                self.socket.send(self._lf(command).encode())
            if '?' in command or '*' in command:
#                time.sleep(0.5)
                data = self.socket.recv(self.BUFFER_SIZE).decode()
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
            results.update({self.inst_id+'Current OUT'+channel:measure[0],
                            self.inst_id+'Voltage OUT'+channel:measure[1],
                            self.inst_id+'Power OUT'+channel:measure[2]})

        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

  #############
#### DG1000Z ################################################################
  #############

class DG1000Z(object):
    r"""Abstract class that implements the common driver for the model DG1000Z
    Programmable waveform generator. The driver implement the following x commands

    * *IDN?: Identifiation query (model identification)

    This class also contains the following class variables, for the specific
    characters that are used in the communication:

    :var LF: Line feed, chr(10), \\n
    """

    LF = chr(10)

    def __init__(self, TCP_IP='192.168.6.10', TCP_PORT=5555, BUFFER_SIZE=1024,**kwargs):
        """Initialize internal variables and ethernet connection

        :param TCP_IP: The adress of the Lakeshore
        :type TCP_IP: str
        :param TCP_PORT: 5555 is the default
        :type TCP_PORT: int
        :param BUFFER_SIZE: 1024
        :type BUFFER_SIZE: int
        """
        # The socket connection for TCP/IP should have a long buffer size
        try:
            self.inst_id = kwargs['type']+kwargs['id']+'_'
        except:
            self.inst_id = ''

        self.BUFFER_SIZE = BUFFER_SIZE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
        self._connected = True
        
        device_type = self._send_command('*IDN?')
        nb_channels = int(self._send_command(':SYST:CHAN:NUM?'))
        
    def close(self):
        """Stop the connection to the LakeShore"""
        self.socket.close()
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
                    self.socket.send((i+chr(10)).encode())
            else:
                self.socket.send(self._lf(command).encode())
            if '?' in command or '*' in command:
                data = self.socket.recv(self.BUFFER_SIZE).decode()
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
        id_channel = 1
        try:
            while id_channel <= 2:
                measure = self._send_command(':SOUR:APPL?')[1:-1].split(',')
                results.update({self.inst_id+'Waveform_CH'+str(id_channel):measure[0],
                                self.inst_id+'Frequency_CH'+str(id_channel)+' [Hz]':measure[1],
                                self.inst_id+'Amplitude_CH'+str(id_channel)+' [Vpp]':measure[2],
                                self.inst_id+'Offset_CH'+str(id_channel)+' [Vdc]':measure[3],
                                self.inst_id+'Start phase_CH'+str(id_channel)+' [deg]':measure[4]})
            
                id_channel += 1        
        except:
            [results.update({self.inst_id+'VAR'+str(idx):value}) for idx, value in enumerate(measure)]
        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results
