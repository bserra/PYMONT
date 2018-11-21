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

    def __init__(self, TCP_IP='192.168.33.2', TCP_PORT=503, BUFFER_SIZE=1024,**kwargs):
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
    
    def _init_params(self):
        """"""
        self._send_command('VM 10000')
        self._send_command('S3 1,1,0')
    
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
#        return string + self.CR + self.LF
        return string + self.CR

    def _send_command(self, command):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """
        if self._connected == True:
            self.socket.send(self._cr_lf(command).encode())
            data = self.socket.recv(self.BUFFER_SIZE).decode('unicode_escape')    
#            if ('PR' in command) & ('PR AL' != command):
#                print ('1st')
#                print (self._cr_lf(command).encode())
#                data = self.socket.recv(self.BUFFER_SIZE)
#                print (data, command)
#                if data[:-1] == command:
#                    data = self.socket.recv(self.BUFFER_SIZE).decode()
#
#            elif ('PR AL' == command):
#                print ('2nd')
#                while True:
#                    data = self.socket.recv(self.BUFFER_SIZE*4)
#                    print (data)
#                    if data == '':
#                        break
#            
#            elif ('FD' == command):
#                print ('3rd')
#                print ('here')
#                data = self.fact_reset()
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
    def __init__(self, TCP_IP='192.168.33.2', TCP_PORT=503, BUFFER_SIZE=16*1024):
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
