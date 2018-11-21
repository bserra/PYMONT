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


  ############
#### MDI 23 ###################################################################
  ############


# Code translations constants
MM_MODES = {
    'DC_V': 'MEASure:VOLTage:DC?',
    'DC_I': 'MEASure:CURRent:DC?',
    'AC_V': 'MEASure:VOLTage:AC?',
    'AC_I': 'MEASure:CURRent:AC?'
}

class MDI23(object):
    r"""Abstract class that implements the common driver for the model MDrive
    23 control drive. The driver implement the following x commands out 
    the x in the specification:

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

    ETX = chr(3)  # \x03
    CR = chr(13)
    LF = chr(10)
    ENQ = chr(5)  # \x05
    ACK = chr(6)  # \x06
    NAK = chr(21)  # \x15

    def __init__(self, TCP_IP='192.168.33.2', TCP_PORT=503, BUFFER_SIZE=16*1024,**kwargs):
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
        self.socket.settimeout(5)
        self._connected = True
        
#        self.mode = kwargs['mode']
#        device_type = self._send_command('*IDN?')
#        self._send_command(MM_MODES[self.mode])

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
        
    def _cr_lf(self, string):
        """Pad line feed to a string

        :param string: String to pad
        :type string: str
        :returns: the padded string
        :rtype: str
        """
        return string + self.CR + self.LF

    def _send_command(self, command):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """
        if self._connected == True:
            self.socket.send(self._cr_lf(command).encode())
            if ('PR' in command):
                data = self.socket.recv(self.BUFFER_SIZE).decode()
#            if ('PR AL' == command):
#                while True:
#                    data = self.socket.recv(self.BUFFER_SIZE)
#                    print (data)
#                    if data == '':
#                        break
                
            #                data = data.rstrip(self.LF)
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
                
    def dump_sensors(self):
        """"""
        
        results = self._send_command('PR AL')
#        results = {**self.fetch()}

        return results

