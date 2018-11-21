# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:15:28 2018

@author: bserra
"""

import socket

CR = chr(13)
LF = chr(10)
BUFFER_SIZE = 1024
TCP_IP, TCP_PORT = '192.168.33.2', 502

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((TCP_IP, TCP_PORT))

command = 'PR I3'+CR+LF
socket.send(command.encode())
resp = socket.recv(BUFFER_SIZE).decode()

print (resp)