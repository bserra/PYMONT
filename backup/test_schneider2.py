# -*- coding: utf-8 -*-
"""
Created on Tue May 29 09:39:52 2018

@author: bserra
"""

import schneider as sch
import time

motor = sch.MDI23()


#program = ['VM 9000',
#           'S3 1,1,0',
#           'PG 1',
#           '  S3 1,1,0',
#           '  VM 10000',
#           '  HM 4',
#           '  MR -2350',
#           '  P=0',
#           '  MA 117600',
#           '  H',
#           '  MA 233600',
#           '  H',
#           '  HM 4',
#           'PG']

#program = ['VM 9000',
#           'S3 1,1,0',
#           'PG 1',
#           '  S3 1,1,0',
#           '  VM 10000',
#           '  HM 4',
#           '  MR -2350',
#           '  H',
#           '  P=0',
#           '  MA 117600',
#           '  H',
#           'E',
#           'PG']

program = ['PG 1',
           'LB Ga',
           '  VM 10000',
           '  S3 1,1,0',
           '  HM 4',
           '  H',
           'E',
           'PG']

#a = motor._send_command('PR ER')
#
#print (a)
#motor._send_command('ER 0')
#
#for line in program:
#    print (line)
#    a = motor._send_command(line)
#    print (a)
#    time.sleep(0.05)    

# 35 seconds for a complete rotation of the filter wheel    
a = motor._send_command('VM 10000')
b = motor._send_command('S3 1,1,0')
c = motor._send_command('PR P')
p1 = motor._send_command('P 0')
motor._send_command('HM 4')
#p2 = motor._send_command('PR MV')
#d = motor._send_command('HM 4')
#
#print (p1,p2)
print (a,b,c)
#motor.socket.close()