# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 14:52:26 2018

@author: bserra
"""
# IMPORTS
#########################
import pyvisa_connect as pyvisa


# METHODS
#########################
class LockInAmplifierInterface():
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
        
    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 TERMINATION_STRING = '\n',
                 RESOURCE_TIMEOUT = 5,
                 **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the agilent
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\n' by default for agilent
        :type TERMINATION_STRING: str
        """
        
        self.instrument, 
        self.inst_id, 
        self.connected = pyvisa.connect(RESOURCE_STRING, 
                                         RESOURCE_MANAGER = None,
                                         RESOURCE_ID = '',
                                         TERMINATION_STRING = '\n',
                                         RESOURCE_TIMEOUT = 5,
                                         **kwargs)

    def __del__(self):
            self.serialport.close()

    # Open serial comms port to Stanford Research Systems SR810 lock in amplifier, return port name or -1 in case of error
    # Note that the serial port can also be an FTDI-style USB virtual coms port
    def connect(self):
            # CB #
            # Works perfectly fine with windows, on unix system this
            # will not work.
            portlist=["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10","COM11","COM12"]
            self.open_flag=False
            for x in portlist:
                    try:
                        self.serialport=serial.Serial(x,9600,timeout=0.05)
                        # now see if the SR810 is present
                        self.serialport.write("*IDN?\r")
                        time.sleep(0.1)
                        response=self.serialport.readline()
                        if  response.count("SR810") == 0 :
                            self.serialport.close()
                            continue
                        else :
                            self.open_flag=True
                            break
                    except:
                            continue
            if (self.open_flag==False):
                    return(-1)
            else:
                    return(x)
            
    # Close serial comms
    def disconnect(self):
            if self.open_flag:
                self.serialport.close()

                
    ## Basic Setup of lock in amplifier
    def setupLockIn(self):
            self.serialport.write("DDEF 1\r")  # left hand display shows magnitude of signal
            self.serialport.write("OFLT 11\r")  # set time constant to 100ms.9=300ms,10=1s,11=3s
            self.serialport.write("IGND 1\r")  # Input shield grounding float=0, ground=1
            self.serialport.write("ILIN 1\r")  # Line notch filter in, 0=out
            self.serialport.write("FMOD 0\r")  # take freq ref from the chopper wheel cable
            self.serialport.write("APHS\r")    # autophase
            self.serialport.write("AGAN\r")    # autogain
            self.serialport.write("SRAT 3\r")  # sample rate 5=2Hz,4=1Hz,3=0.5Hz
            self.serialport.write("SYNC 1\r")  # synchronous filtering on
            time.sleep(1)

    ## Read signal voltage amplitude      
    def readVolts(self):
              #self.serialport.write("OUTR?\r") # read volts  (actually left hand display)
              time.sleep(3)
              self.serialport.write("OUTP? 3\n") # read volts
              time.sleep(0.2)
              res=self.serialport.readline()
              try:
                      resf=float(res)
              except:
                      resf=0.0
              return(resf)

    ## Read signal phase 
    def readPhase(self):
              self.serialport.write("PHAS?\r") # read phase          
              res=self.serialport.readline()
              try:
                      resf=float(res)
              except:
                      resf=0.0
              return(resf)

    ## Read reference frequency     
    def readFreq(self):
              self.serialport.write("FREQ?\r") # read frequency          
              res=self.serialport.readline()
              try:
                      resf=float(res)
              except:
                      resf=0.0
              return(resf)

            
    ## set the time constant
    def setTau(self,Tau):
            cstring="OFLT"+Tau+"\r"
            y=self.serialport.write(cstring.encode())
            
    ## get the time constant
    def getTau(self):
            y=self.serialport.write("OFLT?")
            res=self.serialport.readline()
            return(res)

    ## set the sample rate
    def setSampleRate(self,SR):
            cstring="SRAT"+SR+"\r"
            y=self.serialport.write(cstring.encode())
            
    ## get the sample rate
    def getSampleRate(self):
            y=self.serialport.write("SRAT?")
            res=self.serialport.readline()
            return(res)



# MAIN
#########################
if __name__ == "__main__":
    print ('Processing...')
    
    
    
    
# GARBAGE
#########################
