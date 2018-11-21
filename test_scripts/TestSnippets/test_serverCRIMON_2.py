# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 10:18:26 2018

@author: bserra
"""
import socket
import subprocess
import time
import json

me = 'localhost'
port = 1332

test = ['pouet','pouet1','pouet2']
def main():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((me, port))
            break
        except Exception:
            time.sleep(1)
    sock_input = s.makefile('r')
    for command in sock_input:
         try:
             output = subprocess.check_output(command, shell=True)
         except:
             output = 'Could not execute.'
         s.sendall(json.dumps(output)+'\n')
    s.close()


def main():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((me, port))
            break
        except Exception:
            time.sleep(1)
    sock_input = s.makefile('r')
#    for command in sock_input:
#         try:
#             output = subprocess.check_output(command, shell=True)
#         except:
#             output = 'Could not execute.'
#         s.sendall(json.dumps(output)+'\n')
    s.close()



if __name__ == '__main__':
    main()