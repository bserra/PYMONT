# -*- coding: utf-8 -*-
"""
Created on  17:45:05 2018 18/05/2018 11:12:15

@author: dalvarez
based on: rodheandshwarz.py from bserra

"""

import socket
import json

import time


  ##############
#### DSO 5034A #################################################################
  ##############



class DSO5034A(object):
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

    def __init__(self, TCP_IP='134.171.5.184', TCP_PORT=5025, BUFFER_SIZE=16*1024,**kwargs):
        """Initialize internal variables and ethernet connection

        :param TCP_IP: The adress of the Agilent
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
        
        #self.mode = kwargs['mode']
        device_type = self._send_command('*IDN?')
        #self._send_command(MM_MODES[self.mode])

    def close(self):
        """Stop the connection to the oscilloscope"""
        self.socket.close()
        self._connected = False

    def connect(self):
        """Start connection with the oscilloscope"""
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
                #data = self.socket.recv(self.BUFFER_SIZE).decode()
                #data = data.rstrip(self.LF)

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
        """Send a command :MEAS:RES and parse it into a dictionnary
r
        :returns: the dictionnary of the measurements for all 4 channels
        :rtype: dict
        """   
        response = self._send_command(':MEAS:RES?')
        # Splitting with Pk-Pk give a list of 5 elements. First is empty, the 
        # four others are for each channel
        channels = response.split('Pk-Pk')[1:]
        
        # Keywords associated to the values 1 to 5 of each channels
        # See agilent infiniivision 5000 programmers guide p.309
        keyws = ['current','min','max','mean','std','count']
        results = dict()
        # For each channels
        for chan in channels:
            # If comma at the end of the string
            if chan[-1] == ',':
                values = chan[:-1].split(',')
            else:
                chan = chan.split(',')
                
            # The output number is the first argument and between ()     
            output = str(values[0][values[0].find("(")+1:values[0].find(")")])
            # Update dictionnary with the comb. keyw -> value
            results.update({self.inst_id+keyw.upper()+'OUT'+output:val 
                            for keyw,val in zip(keyws,values[1:])})
        
        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}
        return results

