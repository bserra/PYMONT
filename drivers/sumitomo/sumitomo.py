"""This module contains the driver for the following equipment from Riello

* UPS Vision Dual (VSD 3000) U Power Supply

Use of serial/usb connection
"""

import serial
import json
import collections
import sys

# Code translations constants
status_f70 = {0:{
                 'pos':0,
                 'info':{True:'System On',
                         False:'System Off'}
                 },
              1:{'pos':1,
                 'info':{True:'Motor Temperature alarm',
                   False:'no alarm'}},
              2:{'pos':2,
                 'info':{True:'Phase Sequence/Fuse alarm',
                   False:'no alarm'}},
              3:{'pos':3,
                'info':{True:'Helium Temperature alarm',
                   False:'no alarm'}},                 
              4:{'pos':4,
                 'info':{True:'Water Temperature alarm',
                   False:'no alarm'}},                 
              5:{'pos':5,
                 'info':{True:'Water Flow alarm',
                   False:'no alarm'}},
              6:{'pos':6,
                 'info':{True:'Oil Level alarm',
                   False:'no alarm'}},
              7:{'pos':7,
                 'info':{True:'Pressure alarm',
                   False:'no alarm'}},
              8:{'pos':8,
                 'info':{True:'Solenoid on',
                   False:'Solenoid off'}},
              9:{'pos':slice(9,12),
                 'info':{0:'Local Off',
                 1:'Local On',
                 2:'Remote Off',
                 3:'Remote On',
                 4:'Cold Head Run',
                 5:'Cold Head Pause',
                 6:'Fault Off',
                 7:'Oil Fault Off'}},
              10:{'pos':12,
                  'info':{True:'spare',
                          False:'spare'}},
              11:{'pos':13,
                  'info':{True:'spare',
                          False:'spare'}},
              12:{'pos':14,
                  'info':{True:'spare',
                          False:'spare'}},
              13:{'pos':15,
                  'info':{True:'Configuration 1',
                    False:'Configuration 2'}}}

#### UPSVSD3xxx ###############################################################

class COMP_F70(object):
    r"""Abstract class that implements the common driver for the model 3000 
    of the VSD UPS. The driver implement the following 5 commands out of the 7
    in the UPS communication protocol document:

    * GI: Get Identification (identification query)
    * RS: Request Status (battery/ups status query)
    * CS: Command Shutdown                  # Fixed time
    * CR: Command shutdown and Restore      # Fixed time
    * CD: Command Delete                    # TBI

    This class also contains the following class variables, for the specific
    characters that are used in the communication:

    :var BC: Begin text, chr(2), \\x02
    :var ETX: End text (Ctrl-c), chr(3), \\x03
    :var CR: Carriage return, chr(13), \\r
    :var LF: Line feed, chr(10), \\n
    :var NAK: Negative acknowledge, chr(21), \\x15
    """

    CR = chr(13)
    LF = chr(10)

    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 RESOURCE_TIMEOUT = 5000,
                 TERMINATION_STRING = '\r',
                 **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the Sumitomo device
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\r' by default for sumitomo F70
        :type TERMINATION_STRING: str
        """
        try:
            self.instrument = RESOURCE_MANAGER.open_resource(RESOURCE_STRING,
                                                             open_timeout = RESOURCE_TIMEOUT)
            self.instrument.read_termination = TERMINATION_STRING
            self.instrument.write_termination = TERMINATION_STRING
            self.instrument.timeout = RESOURCE_TIMEOUT
            #self.instrument.baud_rate = 9600
            self.connected = True
        except:
            self.connected = False

        try:
            self.inst_id = RESOURCE_ID+'_'
        except:
            self.inst_id = ''
        
        if RESOURCE_MANAGER == None:
            sys.exit('No VISA resource manager found')
       
    def close(self):
        """Stop the connection to the compressor"""
        self.serial.close()
        self._connected = False

    def connect(self):
        """Start connection with compressor"""
        self.__init__()

    def __test_cmd(self,command):
        """Testing command raw output
        :param command: raw command
        :type command: str
        :returns: reply string from the UPS
        :rtype: str
        """
        command = self._fmt_cmd(command)
        self.serial.write(command.encode())
        response = self.serial.readline()
        
        return response
        
    def __compute_crc(self, cmd_string):
        """ Method to compute CRC-16 Modbus for sending data to compressor
        CRC-16-ModBus Algorithm
        
        :param hex_string: The hex string to check
        :type hex_string: str
        """
        data = bytearray(cmd_string.encode())
        # Polynom used for crc computation
        poly = 0xA001
        # CRC started with 16 bit with all 1's (F = '1111')
        crc = 0xFFFF
        # For each byte of the data
        for b in data:
    		# Apply 8 bit bytes of the  message (b) to the register (crc)
            crc ^= (0xFF & b)
            # For each bit
            for _ in range(0, 8):
    			# If the LSB is 0x0001 
                if (crc & 0x0001):
    				# Result is shifted towards the LSB , XOR with the polynom (^)
                    crc = ((crc >> 1) & 0xFFFF) ^ poly
                else:
    				# Result is shifted towards the LSB , No XOR
                    crc = ((crc >> 1) & 0xFFFF)
    
        # crc & 0xFFFF returns an integer
        # str(hex(x))[2:] will convert to hex and strip the '0x' at the beginning
        # x.upper() will write a4b9 in capital letters (a4b9 =/= A4B9)
        hex_string = str(hex(crc & 0xFFFF))[2:].upper()
        return hex_string   

    def _fmt_cmd(self, command):
        """Pad carriage return and line feed to a string

        :param command: raw command
        :type command: str
        :returns: command with checksum and begin/end chars
        :rtype: str
        """
        
        return command+\
               self.__compute_crc(command)
               
    def _send_command(self, command):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned #TBI
        """
        command = self._fmt_cmd(command)
        
        response = self.instrument.query(command)
        
        return response
#        if response == $???,3278
        
    def identify(self):
        """Send a Get Identification command and parse the output
        :returns: dictionary of the Get Identification reformatted
        :rtype: dict
        """
        GI = '\x47\x49\x30\x30'
        print (self._fmt_cmd(GI))
        reply = self._send_command(GI)
        print (reply)
        data = reply[7:]
        print (data)
        identification = dict()
        
        for key in GET_ID.keys():
            print (key)
            if 'values' in GET_ID[key].keys():
                identification.update({key:GET_ID[key]['values'][str(data[int(GET_ID[key]['pos'])])]})
            else:
                identification.update({key:data[GET_ID[key]['pos']]})

        return identification
        
    def _get_temperatures(self):
        """ Send a $TEA request to retrieve all temperatures of the compressor
        :returns: dictionnary of the four temperatures
        :rtype: dict
        """
        temperatures = dict()

        command = '$TEA'
        response = self.instrument.query(command+self.__compute_crc(command))
        print (self.__compute_crc(command))
        response = response.split(',')[1:-1]

        comments = ["[C] Compressor capsule helium discharge temperature",
                    "[C] Water outlet temperature",
                    "[C] Water inlet temperature"]
        
        print (response)
        # Loop over three first temps because the fourth temperature is deactivated
        for idx, temperature in enumerate(response[:3]):
            temperatures.update({self.inst_id+"temp"+str(idx+1):[str(temperature), comments[idx]]})
            
        return temperatures
            
    def _get_pressure(self):
        """ Send a $PRA request to retrieve all temperatures of the compressor
        :returns: dictionnary of the only pressure
        :rtype: dict
        """
        pressures = dict()

        command = '$PRA'
        response = self.instrument.query(command+self.__compute_crc(command))
        response = response.split(',')[1:-1]

        comments = ["[psi] Helium pressure",
                    "[psi] Deactivated"]
        
        # Loop over first two pressures
        for idx, pressure in enumerate(response):
            pressures.update({self.inst_id+"press"+str(idx+1):[str(pressure), comments[idx]]})

        return pressures

#    def _get_status(self):
#
#        status = dict()
#
#        command = '$STA'
#        response = self.instrument.query(command+self.__compute_crc(command))
#        response = response.split(',')[1:-1]
        
    def _get_status(self):
        """ Send a request status $STA to retrieve the flags raised by the compressor
        :returns: dictionnary of the alarm codes
        :rtype: dict
        """
        status_dict = dict()

        command = '$STA'
        response = self.instrument.query(command+self.__compute_crc(command))
        response = response.split(',')[1:-1][0]
        print (response)
        test = ''.join(['{:4b}'.format(int(char)).replace(' ','0') for char in response])[::-1]
        status = status_f70
        status = [status[i]['info'][int(test[status[i]['pos']],2)] for i in status.keys()]
        comments = ';'.join(status)
        
        status_dict.update({self.inst_id+"status":[str(response), comments]})
        return status_dict
    
    def dump_sensors(self):
        """Send a Request Status command and parse the output
        :returns: sub-dictionary of the Request Status output
        :rtype: dict
        """
        results = {**self._get_temperatures(),
                   **self._get_pressure(),
                   **self._get_status()}


        return results