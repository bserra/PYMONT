"""This module contains drivers for the following equipment from LakeShore cryotonics

* LakeShore Model 336 Temperature Controller

Use of ethernet connection
"""

import socket
import json

# Code translations constants
INPUT_NAMES = {
    0: 'A',
    1: 'B',
    2: 'C',
    3: 'D',
    4: 'D2',
    5: 'D3',
    6: 'D4',
    7: 'D5'
}

class LakeShore33x(object):
    r"""Abstract class that implements the common driver for the model 336 
    temperature controller. The driver implement the following 12 commands out 
    the 97 in the specification:

    * *IDN?: Identifiation query (model identification)
    * *TST?: Self test query
    * KRDG?: Kelvin reading query
    * INCRV?: Input curve query
    * INNAME?: Sensor input name query
    * HTR?: Heater output query
    * HTRSET?: Heater setup query
    * RANGE?: Heater range query
    * RAMP?: Control setpoint ramp parameter query
    * RAMPST?: Control setpoint ramp status query
    * SETP?: Control setpoint query
    * PID?: Control loop PID values query

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

    def __init__(self, TCP_IP='192.168.5.1', TCP_PORT=7777, BUFFER_SIZE=16*1024,**kwargs):
        """Initialize internal variables and ethernet connection

        :param TCP_IP: The adress of the Lakeshore
        :type TCP_IP: str
        :param TCP_PORT: 7777 is the default
        :type TCP_PORT: int
        :param BUFFER_SIZE: 1024
        :type BUFFER_SIZE: int
        """
        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below
        try:
            self.inst_id = kwargs['type']+kwargs['id']+'_'
        except:
            self.inst_id = ''
        self.BUFFER_SIZE = BUFFER_SIZE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
        self._connected = True

        config = open('instrumentation_config_2.json')
        lakeshore_config = json.load(config)
        lakeshoreType = self._send_command('*IDN?')
        self.inputs = lakeshore_config['T'][lakeshoreType]
        
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
        """Pad carriage return and line feed to a string

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
            if '?' in command or '*' in command:
                data = self.socket.recv(self.BUFFER_SIZE).decode()
                data = data.rstrip(self.LF).rstrip(self.CR)
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
        
    def identify(self):
        """"""
        reply = self._send_command('*IDN?')
        return reply
        
    def temperature_probes(self):
        """"""
        results = dict()
        T_K = [self._send_command('KRDG? '+i) for i in self.inputs]
        for idx, i in enumerate(self.inputs):
            results[self.inst_id+self._send_command('INNAME? '+i).strip()]=T_K[idx]
        return results

    def power_heaters(self):
        """"""
#        results = dict()
        results = {self.inst_id+'H1':self._send_command('HTR? 1'),
                   self.inst_id+'H2':self._send_command('HTR? 2')}
        return results

    def setpoints(self):
        """"""
        results = {self.inst_id+'SETP1':self._send_command('SETP? 1'),
                   self.inst_id+'SETP2':self._send_command('SETP? 2')}
        return results        
    
    def dump_sensors(self):
        """"""
        results = {**self.power_heaters(), 
                **self.temperature_probes(),
                **self.setpoints()}

        return results
        
    def curves(self):
        """"""
        reply = self._send_command('INCRV? D')
        return reply