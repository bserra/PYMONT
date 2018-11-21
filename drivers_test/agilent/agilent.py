# -*- coding: utf-8 -*-
"""
Created on  17:45:05 2018 18/05/2018 11:12:15

@author: dalvarez
based on: rodheandshwarz.py from bserra

"""
import json
import sys

import time

# METHODS 
#########################

#### DSO 5034A ################################################################

class DSO5034A(object):
    r"""Abstract class that implements the common driver for the model 336 
    temperature controller. The driver implement the following 12 commands out 
    the 97 in the specification:

    * *IDN?: Identifiation query (model identification)

    """

    LF = chr(10)

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
        
    def fetch(self):
        """Send a command :MEAS:RES and parse it into a dictionnary
r
        :returns: the dictionnary of the measurements for all 4 channels
        :rtype: dict
        """   
        response = self.instrument.query(':MEAS:RES?')
        # Splitting with Pk-Pk give a list of 5 elements. First is empty, the 
        # four others are for each channel
        channels = response.split('Pk-Pk')[1:]
        
        # Keywords associated to the values 1 to 5 of each channels
        # See agilent infiniivision 5000 programmers guide p.309
        keyws = ['curr','min','max','mean','std','cnt']
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
            results.update({self.inst_id+keyw.upper()+'OUT'+output:(val, '[V] '+keyw) 
                            for keyw,val in zip(keyws,values[1:])})
        
        return results
        
    def dump_sensors(self):
        """"""
        results = {**self.fetch()}
        return results

