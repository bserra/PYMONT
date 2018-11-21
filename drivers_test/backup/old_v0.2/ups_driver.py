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
    SRC = '\x30'
    DEST = '\x31'
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
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=1)

        
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
        print (checksum)
        for i in f"{checksum:#0{6}x}"[2:]: 
            hex_string+=i
        print (hex_string)
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
        
        print (command.encode())
        self.serial.write(command.encode())
#        self.serial.write(self._cr_lf(command).encode())
        response = self.serial.readline()
        print (response)
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
        reply = self._send_command(RS)[7:]

        for key in self.REQ_ST.keys():
            char_str = reply[self.REQ_ST[key]['pos']]
            print (key, self.REQ_ST[key]['pos'], char_str)
            
            if isinstance(char_str,int):
                print (bin(char_str & 0x0F))
                
            elif isinstance(char_str,bytes):
                a = 0b0
                for byte in char_str:
                    a = a << 4 | byte & 0x0F
                print (a)
                    
            else:
                print (reply[self.REQ_ST[key]['pos']],' is neither int or bytes')

        return reply

    def shutdown(self):
        """"""
#        C, S
#        RS = '\x52\x53\x30\x30'
        CS = '\x43\x53\x30\x34\x30\x30\x30\x3a'
        reply = self._send_command(CS)
        return reply

    def restart(self):
        """"""
#        C, R
        CR = '\x43\x52\x30\x38\x30\x30\x30\x3a\x30\x30\x30\x3a'
        reply = self._send_command(CR)
        return reply
    def cancel(self):
        """"""
#        C, D
        return results   
    
    def dump_sensors(self):
        """"""
        results = {**self.status()}

        return results
    
"""    
import serial
import numpy as np



test_b = b'\x0210GI38                ULC3            SWM047-01-001211011600000:>=\x03'
test_b = b'                ULC3            SWM047-01-00121101160000'
print ('____ GET IDENTIFICATION ____')
for key in GET_ID.keys():
    print (key, GET_ID[key]['pos'], test_b[GET_ID[key]['pos']])
    if 'values' in GET_ID[key].keys():
        print ('value',GET_ID[key]['values'][chr(test_b[GET_ID[key]['pos']])])
        
        
test_rs = b'842001?40>31?40>3001?40>30334641772>'
print ('____ REQUEST STATUS ____')
for key in REQ_ST.keys():
    char_str = test_rs[REQ_ST[key]['pos']]
    print (key, REQ_ST[key]['pos'], char_str)
    
    if isinstance(char_str,int):
        print (bin(char_str & 0x0F))
        
    elif isinstance(char_str,bytes):
        a = 0b0
        for byte in char_str:
#            print (bin(byte & 0x0F))
            a = a << 4 | byte & 0x0F
        print (a)
            
    else:
        print (test_rs[REQ_ST[key]['pos']],' is neither int or bytes')

"""

'''

send = b'\x0201GI000151\x03'
resp = b'\x0210GI38         ULC3       SWM047-01-001211011600000:>=\x03'



test = [0x02,   #STX
        0x31,   #SRC - CHK BEGIN
        0x30,   #DEST
        0x47,   #G
        0x49,   #I
        0x33,   #3
        0x38,   #8
        0x20,   # Data 1-16 Serial number
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x55,   # Data 17-32 UPS Model
        0x4C,
        0x43,
        0x33,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x20,
        0x53,   # Data 33-44 UPS Soft vers
        0x57,
        0x4D,
        0x30,
        0x34,
        0x37,
        0x2D,
        0x30,
        0x31,
        0x2D,
        0x30,
        0x30,
        0x31,   # 45 Input Output conf.
        0x32,   # 46 UPS type
        0x31,   # 47 Boost configuration
        0x31,   # 48 Buck configuration
        0x30,   # 49 Error control
        0x31,   # 50 Power Share socket
        0x31,   # 51 Battery benches
        0x36,   # 52 Batteries number for bench
        0x30,   # 53 Parallel system
        0x30,   # 54 Unused
        0x30,   # 54 Unused
        0x30,   # 54 Unused - CHK END
        0x30,   # Chk
        0x3A,   # Chk
        0x3E,   # Chk
        0x3D,   # Chk
        0x03]


g = serial.to_bytes(test)

SN = slice(7,23)
UPS = slice(23,39)
SV = slice(39,51)
rest = slice(51,63)

for i in [SN,UPS,SV,rest]:
    print (hex(np.sum(np.array(test)[i])))
    
    
chk = hex(0x200+0x297+0x2ad+0x24d+0x30+0x31+0x47+0x49+0x33+0x38)
'''



