# -*- coding: utf-8 -*-
"""
Created on Fri May 25 11:09:28 2018

@author: irlab
"""
import socket


# Test for the tcp server of the monitoring
#TCP_IP='134.171.36.18'
#TCP_PORT=4500
#BUFFER_SIZE = 1024
#socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket.connect((TCP_IP, TCP_PORT))                
#socket.send('OS001:::MEAS:RES?'.encode())
#data = socket.recv(BUFFER_SIZE).decode()
#print (data)


def params(command):
    lf = chr(10)
    cr = chr(13)
    command = command+cr+lf
    socket.send(command.encode())



TCP_IP='192.168.33.2'
TCP_PORT=503
BUFFER_SIZE = 16*1024
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((TCP_IP, TCP_PORT))      
socket.settimeout(5)          
#data = socket.recv(BUFFER_SIZE).decode()
#print (command,data)
#socket.close()

