# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 15:02:58 2018

@author: bserra
"""
# IMPORTS
#########################
import visa


# METHODS
#########################
def connect(resource_manager, protocol, address, port):
    """"""
    instrument = resource_manager.open('::'.join([protocol,
                                                  address,
                                                  port,
                                                  '']))
    
    return instrument



# MAIN
#########################
if __name__ == "__main__":
    print ('Processing...')
    
    
    
    
# GARBAGE
#########################
