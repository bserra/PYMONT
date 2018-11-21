# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 15:30:12 2018

@author: irlab
"""

#!/usr/bin/env python

import socket


TCP_IP = '192.168.5.1'
TCP_PORT = 7777
BUFFER_SIZE = 16*1024
MESSAGE = '*IDN?\r\n'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'connecting'
s.connect((TCP_IP, TCP_PORT))
#s.settimeout(5)
print 'sending mess'
s.send(MESSAGE)
print 'receive'
data = s.recv(BUFFER_SIZE)
print 'data',data
s.close()

print "received data:", data