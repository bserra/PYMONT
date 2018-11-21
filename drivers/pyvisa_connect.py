# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 14:55:04 2018

@author: bserra
"""
# IMPORTS
#########################
import sys

# METHODS
#########################
class connect(object):
    """Class called by each instrument when trying to connect"""
    
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
        if RESOURCE_MANAGER == None:
            sys.exit('No VISA resource manager found')
        
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
        
        self.mode = kwargs['RESOURCE_CONFIG']

# MAIN
#########################
    
# GARBAGE
#########################
