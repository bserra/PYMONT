# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 10:32:53 2018

@author: bserra
"""
# IMPORTS
#########################
import lakeshore as ls
import vacuumgauge as vg
import roheandschwarze as rs
import rigol_tcp as rig
import agilent as agi

import json

# METHODS
#########################
def select_instrument(identifier):
    """"""
    instruments = {'Lakeshore336':ls.LakeShore33x,
                   'HMC8012':rs.HMC8012,
                   'DP831A':rig.DP831A,
                   'TPG262':vg.TPG262,
                   'DSO5034':agi.DSO5034A}
    
    return instruments[identifier]



# MAIN
#########################
if __name__ == "__main__":
    print ('Processing...')
    file_config = open('instrumentation_config_2.json')
    dict_config = json.load(file_config)
    
    for instrument_type in dict_config:
        instrument = dict_config[instrument_type]
        print(select_instrument(instrument['ident'])) 
        for idx,i in enumerate(instrument['Comm']):
            if i[0] == 'TCP':
                print (instrument_type+str('{:03d}'.format(idx+1)),i[0],i[1])
                if 'Opts' in instrument.keys():
                    print (instrument['Opts'])
            if i[0] == 'Serial':
                print (instrument_type+str('{:03d}'.format(idx+1)),i[0],i[1])    
    
# GARBAGE
#########################
