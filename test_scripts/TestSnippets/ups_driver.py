"""This module contains drivers for the following equipment from Riello

* UPS Vision Dual (VSD 3000) U Power Supply

Use of serial/usb connection
"""

import serial
import json
import collections

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

class UPSVSD3xxx(object):
    r"""Abstract class that implements the common driver for the model 3000 
    of the VSD UPS. The driver implement the following 5 commands out of the 7
    in the UPS communication protocol document:

    * GI: Get Identification (identification query)
    * RS: Request Status (battery/ups status query)
    * CS: Command Shutdown
    * CR: Command shutdown and Restore
    * CD: Command Delete

    This class also contains the following class variables, for the specific
    characters that are used in the communication:

    :var BC: Begin text (Ctrl-c), chr(2), \\x02
    :var ETX: End text (Ctrl-c), chr(3), \\x03
    :var CR: Carriage return, chr(13), \\r
    :var LF: Line feed, chr(10), \\n
    :var ENQ: Enquiry, chr(5), \\x05
    :var ACK: Acknowledge, chr(6), \\x06
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


    def __init__(self, port='COM4', baudrate=1200,id='',type='',**kwargs):
        """Initialize internal variables and serial port connection as 
        described in the UPS Communication protocol manual. 1200 baud, 8 bits
        NO PARITY, 1 stop bit (default parameters for serial connection)

        :param port: Serial USB port used for comm
        :type port: str
        :param baudrate: 1200 is the default
        :type baudrate: int
        """
        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below
        try:
            self.inst_id = kwargs['type']+kwargs['id']+'_'
        except:
            self.inst_id = ''
#        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=1)

        
    def close(self):
        """Stop the connection to the UPS"""
        self.serial.close()
        self._connected = False

    def connect(self):
        """Start connection with UPS"""
        self.__init__()

    def __test_cmd(self,cmd):
        """Testing command raw output"""
        results = self._send_command(cmd)
        return results
        
    def __check_sum(self, hex_string):
        """ Method to return the checksum from the request
        src/dest/request/length/length for sending
        src/dest/request/length/length/data for receiving """
        checksum = sum(hex_string.encode())
        # for each char of the checksum (4 digits)
        for i in f"{checksum:#0{6}x}"[2:]: 
            # add to the hex string, the chr which is equiv. to ascii code
            # 0011+bin(i) [high nibblet always 0011 for the UPS]
            hex_string+=chr(int('3'+i.capitalize(),16))
        return hex_string

    def _fmt_cmd(self, command):
        """Pad carriage return and line feed to a string

        :param request: list with the request
        :type request: list
        :returns: the padded string
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
            is returned
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
        """"""
        GI = '\x47\x49\x30\x30'
        reply = self._send_command(GI)[7:]
        print (self.GET_ID.keys())
        print (reply)
        for key in self.GET_ID.keys():
            print (key)
            print (self.GET_ID[key]['pos'])
            print (key, self.GET_ID[key]['pos'], reply[self.GET_ID[key]['pos']])
            if 'values' in self.GET_ID[key].keys():
                print ('value',self.GET_ID[key]['values'][chr(reply[self.GET_ID[key]['pos']])])

        return reply
        
    def status(self):
        """"""
        RS = '\x52\x53\x30\x30'
        reply = self._send_command(RS)
        data = reply[7:]
        status = dict()
        for key in self.REQ_ST.keys():
            char_str = data[self.REQ_ST[key]['pos']]
            print (key, self.REQ_ST[key]['pos'], char_str)
            
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

        return status
    
    def test_status(self, string):
        """"""
        # b'842001?40>31?40>3001?40>30334641772>'
        data = string[10:]
        print (data)
#        data = string
        status = dict()
        for key in self.REQ_ST.keys():
            char_str = data[self.REQ_ST[key]['pos']]
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

        return status
    
    def shutdown(self):
        """"""
        CS = '\x43\x53\x30\x34\x30\x30\x30\x30'
        reply = self._send_command(CS)
        return reply

    def restart(self):
        """"""
        CR = '\x43\x52\x30\x38\x30\x30\x30\x30\x30\x30\x30\x30'
        reply = self._send_command(CR)
        return reply
    
    def cancel(self):
        """"""
#        C, D
        results = {**self.status()}
        return results   
    
    def dump_sensors(self, string):
        """"""
        results = {**self.test_status(string)}
        results = {keyw:results[keyw] for keyw in ('Batt','BattEstC','BattEstT')}
        return results