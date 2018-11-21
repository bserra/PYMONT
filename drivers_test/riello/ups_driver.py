"""This module contains the driver for the following equipment from Riello

* UPS Vision Dual (VSD 3000) U Power Supply

Use of serial/usb connection
"""

import serial
import json
import collections
import sys

# Code translations constants
GET_ID = collections.OrderedDict()

GET_ID.update(SerialNumber={'pos':slice(0,15),
                            'comms':'Serial Number (Ascii chars from 20hex to \
                                     7Fhex)'},
              UPSModel={'pos':slice(16,31),
                        'comms':'UPS Model (Ascii chars from 20 hex to 7Fhex)'},
              UPSSoft={'pos':slice(32,44),
                       'comms':'UPS Software version (Ascii chars from 20hex to 7Fhex)'},
              InOutConf={'pos':44,
                         'comms':'Input/Ouput config.',
                         'values':{'1':'Single Phase IN > Single Phase OUT',
                                   '2':'Single Phase IN > Tri Phase OUT',
                                   '3':'Tri Phase IN > Single Phase OUT',
                                   '4':'Tri Phase IN > Tri Phase OUT'}},
              UPSType={'pos':45,
                       'comms':'UPS type',
                       'values':{'1':'Line interactive w. Step Wave Output',
                                 '2':'Line interactive w. Sinus Wave Output',
                                 '3':'On Line',
                                 '4':'On Line and Line Interactive (Double Function)'}},
              BoostConf={'pos':46,
                         'comms':'Boost configuration',
                         'values':{'0':'No Boost',
                                   '1':'Boost',
                                   '2':'Double Boost'}},
              BuckConf={'pos':47,
                        'comms':'Buck configuration',
                        'values':{'0':'No Buck',
                                  '1':'Buck',
                                  '2':'Double Buck'}},
              Error={'pos':48,
                     'comms':'Error Control',
                     'values':{'0':'16 bits checksum',
                               '1':'CRC'}},
              PowerShare={'pos':49,
                          'comms':'Power Share sockets',
                          'values':{'0':'No Power Share function',
                                    '1':'1 Socket'}},
              BatteryBenches={'pos':50,
                              'comms':'Battery Benches',
                              'values':{'1':'One Bench (0>+)',
                                        '2':'Two Benches (-<0>+)'}},
              BatteryNumber={'pos':51,
                             'comms':'if "0" then calculate the Batteries\
                                      Number using the formula: Nominal Battery\
                                      Voltage (G/N command)/12 V'},
              ParallSystem={'pos':52,
                            'comms':'Parallel System',
                            'values':{'0':'Single UPS',
                                      '1':'Parallel UPS - Slave',
                                      '2':'Parallel UPS - Master'}},
              Unused1={'pos':53,
                       'comms':'For future purpose'},
              Unused2={'pos':54,
                       'comms':'For future purpose'},
              Unused3={'pos':55,
                       'comms':'For future purpose'},
              )


REQ_ST = collections.OrderedDict()

REQ_ST.update(UPS={'pos':0,
                   'comms':'4 Bits status flags (low nibble,high fix to 0011)',
                   'values':{'Bit3':'Output Powered [0=No,1=Yes]',
                             'Bit2':'UPS Locked [0=No,1=Yes]',
                             'Bit1':'Battery Working [0=No,1=Yes]',
                             'Bit0':'Battery Low [0=No,1=Yes]'}},
              Conf={'pos':1,
                    'comms':'4 Bits status flags (low nibble,high fix to 0011)',
                    'values':{'Bit3':'On Bypass [0=No,1=Yes]',
                              'Bit2':'O.L./L.I. function [0=No,1=Yes]',
                              'Bit1':'Boost Activated [0=No,1=Yes]',
                              'Bit0':'Buck Active [0=No,1=Yes]'}},
              Batt={'pos':2,
                    'comms':'4 Bits status flags (low nibble,high fix to 0011)',
                    'values':{'Bit3':'Bypass Bad [0=No,1=Yes]',
                              'Bit2':'Battery Charging [0=No,1=Yes]',
                              'Bit1':'Battery Charged [0=No,1=Yes]',
                              'Bit0':'Replace Battery [0=No,1=Yes]'}},
              Action={'pos':3,
                      'comms':'4 Bits status flags (low nibble,high fix to 0011)',
                      'values':{'Bit3':'Shutdown Active [0=No,1=Yes]',
                                'Bit2':'Shutdown Imminent [0=No,1=Yes]',
                                'Bit1':'Test in Progress [0=No,1=Yes]',
                                'Bit0':'Beeper On [0=No,1=Yes]'}},
              Alarm={'pos':4,
                     'comms':'4 Bits status flags (low nibble,high fix to 0011)',
                     'values':{'Bit3':'UPS Failure [0=No,1=Yes]',
                               'Bit2':'Alarm Overload [0=No,1=Yes]',
                               'Bit1':'Alarm Temperature [0=No,1=Yes]',
                               'Bit0':'Nothing here'}},
              InFreq={'pos':slice(5,8),
                      'comms':'Input freq. in .1 Hz, 3 bytes'},
              InVolt={'pos':slice(8,11),
                      'comms':'Input volt. in Volts rms, 3 bytes'},                           
              OutFreq={'pos':slice(11,14),
                       'comms':'Output freq. in .1 Hz, 3 bytes'},
              OutVolt={'pos':slice(14,17),
                       'comms':'Output volt. in Volts rms, 3 bytes'},
              OutLoad={'pos':slice(17,19),
                       'comms':'Output Load in %, 2 bytes'},
              ByPFreq={'pos':slice(19,22),
                       'comms':'Bypass freq. in .1 Hz, 3 bytes'},
              ByPVolt={'pos':slice(22,25),
                       'comms':'Bypass volt. in Volts rms, 3 bytes'},
              BattVolt={'pos':slice(25,29),
                       'comms':'Battery volt. in .1 V, 4 bytes'},
              BattEstC={'pos':slice(29,31),
                        'comms':'Battery estimated charge in %, 2 bytes'},
              BattEstT={'pos':slice(31,34),
                        'comms':'Battery estimated time in mins, 3 bytes'},
              UPSTemp={'pos':slice(34,36),
                        'comms':'System temperature in Celsius, 2 bytes'},
                       )

#### UPSVSD3xxx ###############################################################

class UPSVSD3xxx(object):
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

    BC = chr(2)   # \x02
    ETX = chr(3)  # \x03
    SRC = chr(48)
    DEST = chr(49)
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
       
    def close(self):
        """Stop the connection to the UPS"""
        self.serial.close()
        self._connected = False

    def connect(self):
        """Start connection with UPS"""
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
        
    def __check_sum(self, hex_string):
        """ Method to return the checksum from the request
        src/dest/request/length/length for sending
        src/dest/request/length/length/data for receiving 
        
        :param hex_string: The hex string to check
        :type hex_string: str
        """
        checksum = sum(hex_string.encode())
        # for each char of the checksum (4 digits)
        for i in f"{checksum:#0{6}x}"[2:]: 
            # add to the hex string, the chr which is equiv. to ascii code
            # 0011+bin(i) [high nibblet always 0011 for the UPS]
            hex_string+=chr(int('3'+i.capitalize(),16))
        
        return hex_string

    def _fmt_cmd(self, command):
        """Pad carriage return and line feed to a string

        :param command: raw command
        :type command: str
        :returns: command with checksum and begin/end chars
        :rtype: str
        """
        
        return self.BC+\
               self.__check_sum(self.SRC+self.DEST+command)+\
               self.ETX
        
    def _send_command(self, command):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned #TBI
        """
        command = self._fmt_cmd(command)
        
        self.serial.write(command.encode())
        response = self.serial.readline()
        
        return response
#        if response == self._cr_lf(self.NAK):
#            message = 'Serial communication returned negative acknowledge'
#            raise IOError(message)
#        elif response != self._cr_lf(self.ACK):
#            message = 'Serial communication returned unknown response:\n{}'\
#                ''.format(repr(response))
#            raise IOError(message)
        
    def identify(self):
        """Send a Get Identification command and parse the output
        :returns: dictionary of the Get Identification reformatted
        :rtype: dict
        """
        GI = '\x47\x49\x30\x30'
        reply = self._send_command(GI)
        data = reply[7:]
        identification = dict()
        
        for key in GET_ID.keys():
            if 'values' in GET_ID[key].keys():
                identification.update({key:GET_ID[key]['values'][chr(data[GET_ID[key]['pos']])]})
            else:
                identification.update({key:data[GET_ID[key]['pos']]})


        return reply
        
    def status(self):
        """Send a Request Status command and parse the output
        :returns: dictionary of the Request Status reformatted
        :rtype: dict
        """
        RS = '\x52\x53\x30\x30'
        reply = self._send_command(RS)
        data = reply[7:]
        status = dict()
        
        for key in REQ_ST.keys():
            char_str = data[REQ_ST[key]['pos']]
            
            if isinstance(char_str,int):
                value = (bin(char_str & 0x0F))
                status.update({key:value})
            elif isinstance(char_str,bytes):
                value = 0b0
                for byte in char_str:
                    value = value << 4 | byte & 0x0F
                status.update({key:value})
                    
            else:
                print (char_str,' is neither int or bytes')

        return status.update({'UPS_reply':reply})
    
    def shutdown(self):
        """Send a Command Shutdown command
        :returns: reply from the UPS
        :rtype: str
        """
        CS = '\x43\x53\x30\x34\x30\x30\x30\x30'
        reply = self._send_command(CS)
        
        return reply

    def restart(self):
        """Send a Command Restart command
        :returns: reply from the UPS
        :rtype: str
        """
        CR = '\x43\x52\x30\x38\x30\x30\x30\x30\x30\x30\x30\x30'
        reply = self._send_command(CR)
        
        return reply
    
    def cancel(self):
        """"""
#        C, D
        results = {**self.status()}
        
        return results   
    
    def dump_sensors(self, string):
        """Send a Request Status command and parse the output
        :returns: sub-dictionary of the Request Status output
        :rtype: dict
        """
        results = {**self.status()}
        results = {keyw:results[keyw] for keyw in ('Batt','BattEstC','BattEstT')}
        
        return results
    
#    def test_status(self, string):
#        """"""
#        # b'842001?40>31?40>3001?40>30334641772>'
#        data = string[10:]
#        print (data)
##        data = string
#        status = dict()
#        for key in self.REQ_ST.keys():
#            char_str = data[self.REQ_ST[key]['pos']]
#            if isinstance(char_str,int):
#                value = (bin(char_str & 0x0F))
#                status.update({key:value})
#            elif isinstance(char_str,bytes):
#                value = 0b0
#                for byte in char_str:
#                    value = value << 4 | byte & 0x0F
#                status.update({key:value})
#                    
#            else:
#                print (char_str,' is neither int or bytes')
#
#        return status
#    
#    def test_dump_sensors(self, string):
#        """"""
#        results = {**self.test_status(string)}
#        results = {keyw:results[keyw] for keyw in ('Batt','BattEstC','BattEstT')}
#        return results