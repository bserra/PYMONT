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


  ##############
#### HMC 8012 #################################################################
  ##############


# Code translations constants
MM_MODES = {
    'DC_V': 'MEASure:VOLTage:DC?',
    'DC_I': 'MEASure:CURRent:DC?',
    'AC_V': 'MEASure:VOLTage:AC?',
    'AC_I': 'MEASure:CURRent:AC?'
}

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

    def __init__(self, TCP_IP='192.168.6.002', TCP_PORT=5025, BUFFER_SIZE=16*1024,**kwargs):
        """Initialize internal variables and ethernet connection

        :param TCP_IP: The adress of the Lakeshore
        :type TCP_IP: str
        :param TCP_PORT: 5025 is the default
        :type TCP_PORT: int
        :param BUFFER_SIZE: 16*1024
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
        
        self.mode = kwargs['mode']
        device_type = self._send_command('*IDN?')
        self._send_command(MM_MODES[self.mode])

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
            self.socket.send(self._lf(command).encode())
            if '?' in command or '*' in command:
                time.sleep(0.05)
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
        return {self.inst_id+self.mode:self._send_command('FETC?')}
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

  ##############
#### HMC 4040 #################################################################
  ##############

# Code translations constants
MM_MODES = {
    'DC_V': 'MEASure:VOLTage:DC?',
    'DC_I': 'MEASure:CURRent:DC?',
    'AC_V': 'MEASure:VOLTage:AC?',
    'AC_I': 'MEASure:CURRent:AC?'
}


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

    def __init__(self, port='COM6', id='',type=''):
        """Initialize internal variables and ethernet connection

        :param TCP_IP: The adress of the Lakeshore
        :type TCP_IP: str
        :param TCP_PORT: 5025 is the default
        :type TCP_PORT: int
        :param BUFFER_SIZE: 16*1024
        :type BUFFER_SIZE: int
        """
        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below
        
        # If RTS/CTS is not activated you have to be careful about delays
        if id+type == '':
            self.inst_id = ''
        else:
            self.inst_id = type+id+'_'
        self.serial = serial.Serial(port=port, timeout=10, rtscts=True)
        self._connected = True

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
        for i in [1,2,3,4]:
            self._send_command('INST OUT'+str(i))
            self.mode='Volts OUT'+str(i)
            results.update({self.inst_id+self.mode:self._send_command('MEAS:VOLT?')})
            self.mode='Current OUT'+str(i)
            results.update({self.inst_id+self.mode:self._send_command('MEAS:CURR?')})
#            time.sleep(0.05)

        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}

        return results

