# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 16:39:17 2018

@author: bserra
"""

import ups_driver as ups_d
import numpy as np

filename = 'log_ups_rs.txt' 

data_array = np.genfromtxt(filename,dtype='|S60')
ups = ups_d.UPSVSD3xxx()
print (data_array)


for string in data_array:
    result = ups.dump_sensors(string)
    print (result)
#    print (result['UPS'], result['BattEstC'])