# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 16:25:26 2018

@author: bserra
"""
# IMPORTS
#########################
import sumitomo

import visa

# METHODS
#########################


"""
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 RESOURCE_TIMEOUT = 5000,
                 TERMINATION_STRING = '\r',
                 **kwargs):
"""
    
# MAIN
#########################
if __name__ == "__main__":
    print ('Processing...')
    
    rm = visa.ResourceManager('@py')
#    rm.list_resources()
    comp_str = 'ASRL/dev/ttyUSB2::INSTR'
    
    compressor = sumitomo.COMP_F70(comp_str,
                                   RESOURCE_MANAGER = rm,
                                   RESOURCE_ID      = 'C001',
                                   RESOURCE_TIMEOUT = 1000,
                                   TERMINATION_STRING = '\r')
    
    print ('Connected')
    print (compressor.dump_sensors())
    
# GARBAGE
#########################
