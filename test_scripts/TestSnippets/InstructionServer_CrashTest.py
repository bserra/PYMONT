# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 12:48:28 2018

@author: bserra

v0.1 - First draft for examples of the instruction server
       Might want to migrate this to a python notebook
       
"""
# IMPORTS
#########################
import socket
import json
import numpy as np
import time

# METHODS
#########################
def InstructionClient(TCP_IP, PORT):
    """"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((TCP_IP, PORT))
    client.settimeout(5)

    return client

# MAIN
#########################
if __name__ == "__main__":
    print ('Processing...')
 
    # Constants
    BUFFER_SIZE = 2048
    TCP_IP = '134.171.36.18'
    PORT = 4500

    # Connecting to the instruction server
    client = InstructionClient(TCP_IP, PORT)
#    '''
#    Example 2 : Wrong command
#    '''
#    instruction = 'INST|READINST|READ'
#    client.sendall(instruction.encode())
#    # Read the output from the server
#    output = client.recv(BUFFER_SIZE)
#    # Try to convert the string output to dictionnary
#    try:
#        output = json.loads(output.decode())
#    # If not a dictionnary, just dump the string
#    except:
#        output = output.decode()
#                
#    # Print the output and print their associated type
#    print (output, type(output))
#    time.sleep(5)    
#    
    '''
    Example 1 : Asynchronous reading
    '''
    # Loop over instructions, hardcoded 1s delay betw. instruction in the
    # server side (CRISLER_Monitoring_v04.4 - l244)
    instruction = 'INST|READ'
    for i in np.arange(0,10000):
        # Encode in bytes the instruction and send it to the server
        client.sendall(instruction.encode())
        # Read the output from the server
        output = client.recv(BUFFER_SIZE)
        # Try to convert the string output to dictionnary
        try:
            output = json.loads(output.decode())
        # If not a dictionnary, just dump the string
        except:
            output = output.decode()
                    
        # Print the output and print their associated type
        print (output, type(output))
        time.sleep(5)
# GARBAGE
#########################

