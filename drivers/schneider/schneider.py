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
import sys
import time
  ############
#### MDI 23 ###################################################################
  ############


# Code translations constants
IO_ERRORS = {
    '6': 'An I/O os a;ready set to this type. Applies to non-General Purpose I/O',
    '8': 'Tried to set an I/O to an incorrect I/O type.',
    '9': 'Tried to write to I/O set as Input or is “TYPED”.',
    '10': 'Illegal I/O number.',
    '11': 'Incorrect CLOCK type.',
    '12': 'Illegal Trip / Capture.'}

DATA_ERRORS = {
    '20': 'Tried to set unknown variable or flag. Trying to set an undefined variable of flag. Also could be a typo.',
    '21': 'Tried to set an incorrect value. Many variables have a range such as the Run Current (RC) which is 1 to 100%. As an example, you cannot set the RC to 110%.',
    '22': 'VI is set greater than or equal to VM. The Initial Velocity is set equal to, or higher than the Maximum Velocity. VI must be less than VM.',
    '23': 'VM is set less than or equal to VI. The Maximum Velocity is set equal to, or lower than the Initial Velocity. VM must be greater than VI.',
    '24': '',
    '25': '',
    '26': '',
    '27': '',
    '28': '',
    '29': '',
    '30': '',
    '31': '',
    '32': '',
    '33': '',
    '34': '',
    '35': '',
    '36': '',
    '37': '',
    '38': '',
    '39': ''
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

    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 RESOURCE_TIMEOUT = 5,
                 TERMINATION_STRING = '\r\n',
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
        
        if RESOURCE_MANAGER == None:
            sys.exit('No VISA resource manager found')
    
    def _init_params(self):
        """"""
        self.instrument.write('VM 10000')
        time.sleep(1)
        print (self.instrument.query('PR VM'))
        time.sleep(1)
        self.instrument.write('S3 1,1,0')
        time.sleep(1)
        print (self.instrument.query('PR S3'))
        time.sleep(1)
    
    def close(self):
        """Stop the connection to the LakeShore"""
        self.socket.close()
        self._connected = False

    def connect(self):
        """Start connection with lakeshore"""
        self.__init__()

    def __test_cmd(self,cmd):
        """Testing command raw output"""
        results = self.instrument.write(cmd)
        return results
        
    def _cr_lf(self, string):
        """Pad line feed to a string

        :param string: String to pad
        :type string: str
        :returns: the padded string
        :rtype: str
        """
        return string + self.CR + self.LF
#        return string + self.CR

    def _send_command(self, command):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """
        data = None
        if self._connected == True:
            self.instrument.write(command)
#            data = self.instrument.read()    
            if ('PR' in command) & ('PR AL' != command):
                data = self.instrument.read()
                if data[:-1] == command:
                    data = self.instrument.read()
#
#            elif ('PR AL' == command):
#                print ('2nd')
#                while True:
#                    data = self.socket.recv(self.BUFFER_SIZE*4)
#                    print (data)
#                    if data == '':
#                        break
#            
            elif ('FD' == command):
                data = self.fact_reset()
#
#            else:
#                print ('4th')
#                return None
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
        
    def fact_reset(self):
        """"""
        if self._connected == True:
            self.socket.send(self._cr_lf('FD').encode())
#            self.socket.recv(self.BUFFER_SIZE).decode('unicode_escape')
            self.socket.close()
            self.__init__()
        return 'pouet'
    
    def dump_sensors(self):
        """"""
        
        results = self._send_command('PR AL')
#        results = {**self.fetch()}

        return results

class FilterWheel(MDI23):
    """Driver for the MDI 23 motor of the filter wheel in CRISLER"""
    def __init__(self, TCP_IP='192.168.33.2', TCP_PORT=503, BUFFER_SIZE=1024):
        """Initialize internal variables and serial connection

        :param port: The COM port to open. See the documentation for
            `pyserial <http://pyserial.sourceforge.net/>`_ for an explanation
            of the possible value. The default value is '/dev/ttyUSB0'.
        :type port: str or int
        :param baudrate: 9600, 19200, 38400 where 9600 is the default
        :type baudrate: int
        """
        super(FilterWheel, self).__init__(TCP_IP      = TCP_IP,
                                    TCP_PORT    = TCP_PORT,
                                    BUFFER_SIZE =BUFFER_SIZE)
        FilterWheel.FILTER_POS = {
            'close': 'HM 4',
            'filter1': 'MA 117600',
            'filter2': 'MA 233600',
            'filter3': 'MA 349200'
        }
        # Initializing Maximum Velocity (VM)
        # And switch trigger
#        self._send_command('VM 10000')
#        self._send_command('S3 1,1,0')

    r"""The Fitler wheel class with specific functions for the filter wheel"""
    def moveto(self, position):
        """"""
        if position in FilterWheel.FILTER_POS.keys():
            self._send_command(FilterWheel.FILTER_POS[position])
            print (self._send_command('PR MV'))
        else:
            return str(position)+': is not a valid position for the motor'   
