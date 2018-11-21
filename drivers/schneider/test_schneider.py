# -*- coding: utf-8 -*-
"""
Created on Tue May 29 09:39:52 2018

@author: bserra
"""

import schneider as sch
import time

filt_wheel = sch.FilterWheel()

checks = ['PR P',
          'PR VM',
          'PR S3']
#init = ['VM 10000',
#        'S3 1,1,0']
#
for i in checks:
    response = filt_wheel._send_command(i)
    print (response)
    
filt_wheel.close()

# Programs
program = ['PG 1',
           'LB Ga',
           '  VM 10000',
           '  S3 1,1,0',
           '  HM 4',
           '  H',
           'E',
           'PG']
