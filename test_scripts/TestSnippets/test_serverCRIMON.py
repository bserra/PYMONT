# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 10:18:26 2018

@author: bserra
"""
import socket
import subprocess
import time
import json

me = '134.171.36.18'
port = 4500

#test = ['pouet','pouet1','pouet2']
#
#
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((me, port))
s.settimeout(5)
s.sendall('INST|READ'.encode())
a = s.recv(2048)
print (a)

s.sendall('INST|LIST'.encode())
a = s.recv(2048)
print (a)

s.sendall('INST|T001|KRDG? 0'.encode())
a = s.recv(2048)
print (a)

s.sendall('INST|OS001|:MEAS:RES?'.encode())
a = s.recv(2048)
print (a)


s.close()


#s.sendall(':READ:ALL'.encode())
#a = s.recv(2048)
#
#print (a)
#a = s.recv(1024)
#print (a)
#s.sendall((json.dumps('pouet')+'\n').encode())
#a = s.recv(1024)
#print (a)
#s.close()
#def main():
#    while True:
#        try:
#            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#            s.connect((me, port))
#            break
#        except Exception:
#            time.sleep(1)
#    sock_input = s.makefile('r')
#    for command in sock_input:
#         try:
#             output = subprocess.check_output(command, shell=True)
#         except:
#             output = 'Could not execute.'
#         s.sendall((json.dumps(output)+'\n').encode())
#    s.close()

#if __name__ == '__main__':
#    main()