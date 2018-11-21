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
class connector(object):
    """Class called by each instrument when trying to connect"""
    
    def __init__(self, connection_infos):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the agilent
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\n' by default for agilent
        :type TERMINATION_STRING: str
        """
        
        if connection_infos['RES_MANAGER'] == None:
            sys.exit('No VISA resource manager found')
        
        try:
            self.instrument = connection_infos['RES_MANAGER'].open_resource(connection_infos['RES_STRING'],
                                                             open_timeout = connection_infos['RES_TIMEOUT'])
            self.instrument.read_termination = connection_infos['TERMINATION_STRING']
            self.instrument.write_termination = connection_infos['TERMINATION_STRING']
            self.instrument.timeout = connection_infos['RES_TIMEOUT']
            self.connected = True
        except:
            self.connected = False
            self.instrument = None
            self.inst_id = None

        try:
            self.inst_id = connection_infos['RES_ID']+'_'
        except:
            self.inst_id = ''
        
        self.mode = connection_infos['RES_CONFIG']

    def connect(self):
        """"""
        return self.instrument, self.inst_id, self.connected

# MAIN
#########################
    
# GARBAGE
#########################
