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

program = ['VM 9000',
           'S3 1,1,0',
           'PG 1',
           '  S3 1,1,0',
           '  VM 10000',
           '  HM 4',
           '  MR -2350',
           '  H',
           '  P=0',
           '  MA 117600',
           '  H',
           '  E',
           'PG']

#program = ['PG 100',
#           'VM 10000',
#           'PR VM',
#           'S3 1,1,0',
#           'PR S3',
#           'HM 4',
#           'MA 10000',
#           'H',
#           'PR P',
#           'PG']

motor._send_command('ER=0')
a = motor._send_command('PR ER')

print (a)

for line in program:
    print (line)
    a = motor._send_command(line)
    print (a)
    time.sleep(0.05)    
    
a = motor._send_command('PR ER')
b = motor._send_command('PR VM')
c = motor._send_command('PR I3')
p1 = motor._send_command('PR P')
motor._send_command('HM 4')
p2 = motor._send_command('PR P')
d = motor._send_command('PR ER')

print (p1,p2)
print (a,b,c,d)
motor.socket.close()