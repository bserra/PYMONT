# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 11:12:03 2018

@author: serra

v0.1 -  Embedding pyqtgraph in the interface, communication tab with each
instrument
v0.2 -  Changing layout to add a splitter in order to resize the graph/commands
v0.3 -  Add support for second lakeshore controller
        Added a configuration file (instrumentation_config.json)
        Added dynamical pen, linestyle change with type of instr., color change
        for different sensors

    corrections
    ---------
    sending commands to lakeshore crashed the program
    cause:
    in sendLakeshore method
         if (self.LakeShoreSend.text()) != '' & (self.dc._STARTED==True):

    (self.LakeShoreSend.text()) != ''
    replaced by
    (self.LakeShoreSend.text() != '')
    ---------
    was not communicating to the vacuum gauge with the serial/USB adapter added
    cause:
    the adapter port is COM4 not COM1
    change :self.vg = vg.TPG262(port='COM4',id='001',type='P')
    ---------
    lakeshore.py Changing input in instrument config file is not dynamic
    change:
    results = dict()
    T_K = [self._send_command('KRDG? '+i) for i in self.inputs]
    for idx, i in enumerate(self.inputs):
        results[self.inst_id+self._send_command('INNAME? '+i).strip()]=T_K[idx]
    return results
    ---------
v0.3.1 - Pressure Y axis now in log scale
         Line width set to 3
         Adding a more appropriate message to the About info box
         Status bar now display name+version of soft
         X grid displayed on plots init

    corrections
    ---------
    Two files were created, one on initialization, one on "start" monitoring
    the start method of the comm class is to blame for the extra file on
    initialization, commenting the line
    #        self.comm.start()
    ---------
    Couldn't access the menu bar (clicking on it no effect)
    No layout to main_widget, self.l end up being on top, preventing menubar to
    receive signals
    Adding a layout to main_widget which contains the splitter l widget
    change:
    self.main_widget.layout = QVBoxLayout(self)
    self.main_widget.layout.addWidget(self.l)
    self.main_widget.setLayout(self.main_widget.layout)

v0.4 - Adding UPS communication

    corrections
    ---------
    Timestamp human do have millisecond, never used in anything else.
    Creating a common datetime format which should replace any format in prog
    change:
    self.DATETIME_FMT = '%d-%m-%Y_%H-%M-%S'
    ---------
    Notes and Commands are in one the data columns, the tabulations used for
    writing was static (14?).
    Changed to dynamic with the size of the header
    change:
    (len(self.dc.header.keys())+1)*'\t'
    ---------
    Two tabs (\t\t) between datetime and reading #
    change:
    self.datatime = datetime.datetime.utcnow().strftime(self.comm.df)+'\t'
    to
    self.datatime = datetime.datetime.utcnow().strftime(self.comm.df)

v0.4.1 - Adding Multimeter rhode&schwarze communication (HMC8012)
         Adding Power Supply rhode&schwarze communication (HMP4040)

    known issues
    ---------
    Slow application:
        1. Too much data to plot over more than a day, significant updating
        time for the plot:
            possible solution - restrict data displayed to 1 day
        2. Line thickness is a limiting factor for speed, initial width of 3
            possible solution - reduce line width (1.5 for now)

    corrections
    ---------

v0.4.2 - Adding switching mechanism for choosing which instrument we want to use

    known issues
    ---------
    Cannot put more than 2 instrument in each category, will need to create an
    iterator over all instrument where the choosen instrument will be selected
    by using the qpushbutton and the next() method

v0.4.3 - Adding a last cooldown directory creation in the file menu for support
         of the bokeh server
         Adding an instruction server which redirect request to instruments
         on a separate thread [class InstructionServer():]
             host='134.171.36.18', port=4500
         Adding oscilloscope Agilent DSO5034A
             host='134.171.5.184', port=5025
         Adding power supply Rigol DP831A (replacing R&S HMP4040)
             serial COMx?

v0.4.4 - Instruction server functions:
             - INST|READ: dict. of all instruments as define in _dump_sensors
             - INST|LIST: dict. of all instrument tags <TAG> and their resp. class
             - INST|<TAG>|<CMD>: raw output of the <CMD> for inst <TAG>
v0.4.4.1 - Rigol library to use TCP instead of serial (dalvarez)

v0.4.5 - Configuration file instrumentation_config_2 json file with proper structure
         Communication will loop over every entry and configure the communication to the instrument
         Addint timestamp to the dictionnary of the datapoint, switching reading # and time in log files
         
         Only ONE real time process at a time. Either the monitoring from CRIMON and the only data available would be the 
         last point
         Or the instruction server is running and monitoring is not and full real time is available
         
         On a longer time scale, when acquiring data with less than a second DIT will not give enough time to the
         instruction server to request a whole new set of data. With this solution the response time is much faster

v0.5 - Dynamical graphical interface from the json file.
# Stop support for windows GUI


v1.0 - Porting software to command line interface (windows and UNIX) using PYVISA for communication
       with USB, GPIB, Serial and Ethernet.
       Porting to raspberry Pi 3 with custom python environnement
       Changing all time stamps to UTC
           - datetime.datetime.now() changed to datetime.datetime.utcnow()
       Adding a description for values returned by the drivers
       Adding a header in the data log file with the descriptions
       Adding STOP/START/CLOSE/COMMENT/HELP functionnalities to IS
           - START/STOP: starting and stoping the monitoring of instruments
           - CLOSE: 	closing the communication and save file
           - COMMENT: 	add a comment to the log file with a timestamp
           - HELP: 		print instructions that are supported by the IS
           - EXIT: 		close client connection
           - INFOS: 	start/savepath infos
           - STATUS: 	monitoring status
       Changing configuration file format
       

"""

# PYMONT_Monitoring.py --- Simple application for monitoring Cryostats
#
# Copyright (C) 2018 Benoit Serra
#
# This file is a program monitoring the instruments connected to it. 
# It may be used and modified with no restriction; raw copies as well 
# as modified versions may be distributed without limitation.

# IMPORTS
#########################
from __future__ import unicode_literals
import sys
import os
import time, datetime
import signal
#import matplotlib
import itertools
# Make sure that we are using QT5
#matplotlib.use('Qt5Agg')

#from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtWidgets import QWidget, QTabWidget,QVBoxLayout
#from PyQt5.QtCore import pyqtSlot

import numpy as np
#import pyqtgraph as pg
from collections import defaultdict

import drivers.lakeshore.lakeshore as ls
import drivers.pfeiffer.vacuumgauge as vg
import drivers.roheandschwarze.roheandschwarze as rs
import drivers.rigol.rigol as rig
import drivers.agilent.agilent as agi
import drivers.riello.ups_driver as riello
import drivers.sumitomo.sumitomo as sumitomo

import visa
import socket
import threading
import json

import glob

progname = os.path.basename(sys.argv[0])
progversion = "1.1.0"

# METHODS
#########################
def select_instrument(identifier):
    """"""
    instruments = {'Lakeshore336':ls.LakeShore33x,
                   'Lakeshore340':ls.LakeShore34x,
                   'HMC8012':rs.HMC8012,
                   'DP831A':rig.DP831A,
                   'TPG262':vg.TPG262,
                   'DSO5034':agi.DSO5034A,
                   'DG1062Z':rig.DG1000Z,
                   'DM3068':rig.DM3068,
                   'UPS_VSD3x':riello.UPSVSD3xxx,
                   'COMP_F70':sumitomo.COMP_F70}
    
    print (identifier)
    return instruments[identifier]

def stop_communication(CommServ):
    """"""
    CommServ.close()

class InstructionServer():
    '''demonstration class only
      - coded for clarity, not efficiency
    '''

    def __init__(self, monitoring):#CommServ, MonitServ, ip_address, sock=None):
        try:
            self.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
        except:
            self.socket = None
        if self.socket is not None:
            self.socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            # Bind the socket to the port
            self.CS = monitoring.comm
            self.MS = monitoring
            self.ip_address = monitoring.config_file["GLOBAL_CONFIG"]["host"].split(':')
            self.thread = threading.Thread(target=self.inst_server)
            self.thread.daemon = True
            self.thread.start()
            self.helper="""
_____________________________
\x1b[44m                             \x1b[0m
\x1b[44m  Instruction server help    \x1b[0m
\x1b[44m_____________________________\x1b[0m        
Commands:
    - HELP:     print this help
    - SAVEPATH: change the path where the data is saved to the string after the pipe
    - START:    start the monitoring, creating a [date]_[time].txt log file with 
                the UTC time.
    - INFOS:	print the starting time of the monitoring [UTC] and the save file path
    - STOP:     stop the monitoring, closing properly the log file
    - EXIT:		close the current connection to the monitoring. 
    - CLOSE:    close every connection and the resource manager from pyvisa
				and then stop the python script properly.
    - INST:     the INST command allows to access the instruments connected through
                the communication server.
                Syntax:
                -------
                INST|LIST: Instruments connected and their associated TAG value
                           (T001, PSU002,...)
                INST|READ: Reading of all connected instrument using the dump_sensors
                           from each driver
                INST|[TAG]|[COMMAND]: Send COMMAND to the instrument TAG, careful with
                           the string formatting, no protection as for v1.0\n
    - COMMENT:  the COMMENT command allows to enter comments in the logfile 
                Syntax:
                -------
                COMMENT|This is a comment: Will put 'This is a comment' in the
                                           Comments columns of the logfile
    - SAMPLING: the SAMPLING command allows to chaning the sampling time between
                two measures
                -------
                SAMPLING|value: Will change current sampling to value in seconds                                        
                                    
"""
        else:
            sys.exit('Instruction server failed to initialize')

    def handler(self, client):
        """handler for instruction send by the client to the IS
        The method parse the client.recv() string to use it for sending
        the correct instruction to the communication server
        """
        while True:
            self.save_file.write(str(client))            
            client.settimeout(5)
            # To avoid getting a timeout error when working in command line
            try:
                data = client.recv(4096)
            # When nothing is received, ignore timeout and continue reading
            except socket.timeout:
                continue

            if data != '':
                # client just typed Enter without anything, do nothing
                # int some string with basic commands?

                print ('Data received:', data)
                client_request = data.decode()
                if (client_request == 'INST|READ\r\n') & (self.MS._STARTED != True):
                    response = self.CS._read_setup()
#                    print ('> Data send:', json.dumps(response))
                    if json.dumps(response) == json.dumps({'Error':'Timeout'}):
                        self.CS._stop()
                        print ('Received timeout response, stopping CS and IS')
                        break
                    self.send_client(client, data, json.dumps(response))

                
                elif client_request == '\r\n':
                    time.sleep(2)
                
                elif client_request == 'DISCONNECT\r\n':
                    if self.MS._STARTED:
                        self.send_client(client, data, 'Monitoring is active, cannot disconnect from instruments')                        
                    else:
                        self.CS.stop()
                        self.send_client(client, data, 'Disconnecting instruments...')                    
                    
                elif client_request == 'CONNECT\r\n':
                    if self.MS._STARTED:
                        self.send_client(client, data, 'Monitoring is active, cannot re-connect to instruments')
                    else:                    
                        self.CS = CommunicationServer(self.MS.config_file, self.MS.df)
                        self.MS.comm = self.CS                        
                        self.send_client(client, data, 'Connecting to instruments...')                    

    				# Starting EXP|<SCRIPTNAME>
                elif client_request[:4] == 'EXP|':
                    exp = client_request.split('|')[1]
                    exp_file = glob.glob('./exps/'+self.MS.config_file['GLOBAL_CONFIG']['bench_name']+'*.json')
                    
                    link_file = open(exp_file[0],'r')
                    self.config_file = json.load(link_file)
                    link_file.close() 
                    
                    instructions = self.config_file[exp.replace('\r\n','')]
                    
                    for instruction in instructions:
                        self.send_command(client, instruction)
                elif client_request[:9] == 'SAMPLING|':
                    status = {0:'Inactive',1:'Active'}
                    monitoring_status = status[self.MS._STARTED]
                    if monitoring_status == 'Active':
                        self.send_client(client, data, 'Monitoring is active, change sampling while monitoring is stopped')
                    else:
                        sampling_rate = client_request.split('|')[1].strip()
                        self.MS._TIMER = int(sampling_rate)
                        self.MS.update_infos('sampling', self.MS._TIMER)
                        self.send_client(client, data, 'Changing sampling rate to: '+sampling_rate+' seconds')  
                        
                # Adding comment to logfile, comment is the string after the pipe
                elif client_request[:8] == 'COMMENT|':
                    comment = client_request.split('|')[1]
                    self.MS._add_comment(comment[:-2])
                    self.send_client(client, data, 'Adding comment to log file: '+comment)                    
                # Print the status of the monitoring
                elif client_request == 'STATUS\r\n':
                    infos = ''
                    status = {0:'Inactive',1:'Active'}
                    connection_status = status[self.CS._connected]
                    monitoring_status = status[self.MS._STARTED]
                    if monitoring_status == 'Active':
                        infos = '\n-'+'\n-'.join([i+'\t:'+str(self.MS.infos[i]) for i in self.MS.infos.keys()])+'\n'
                    print ('Monitoring status: ',infos)
                    self.send_client(client, data, 'Connection status: '+status[self.CS._connected]+'\nMonitoring status: '+status[self.MS._STARTED]+infos)
                # Print infos about the start time and save path
                elif client_request == 'INFOS\r\n':
                    infos = self.MS.infos
                    print ('Informations: ',infos)
                    self.send_client(client, data, json.dumps(infos))
                # Print help
                elif client_request == 'HELP\r\n':
                    self.send_client(client, data, self.helper)
                # Change savepath to the string after the pipe
                elif 'SAVEPATH|' in client_request:
                    savepath = client_request.split('|')[1].replace('\r\n','')
                    self.MS.DATAPATH = savepath
                    self.send_client(client, data, 'Changing saving path to: '+savepath)
                # Close monitoring, communication and instruction server
                # Closing python script at the same time
                elif client_request == 'CLOSE\r\n':
                    print ('Closing monitoring, instruction server closing',client)
                    self.MS._close()
                    self.send_client(client, data, 'Monitoring closed, Instruction server will now close.')
                    client.close()
                    self.socket.close()
                    break
                # Start the monitoring, savefile in ./ if no SAVEPATH changes
                elif client_request == 'START\r\n':
                    print ('Starting monitoring ',client)
                    self.MS.start()
                    self.send_client(client, data, 'Monitoring started.')
                # Stop the monitoring, communication still working
                elif client_request == 'STOP\r\n':
                    print ('Stoping monitoring, instruction server ON',client)
                    self.MS._stop()
                    self.send_client(client, data, 'Monitoring stopped, Instruction server awaiting instructions...')
                # Client exit from the connection to port 4500
                elif client_request == 'EXIT\r\n':
                    print ('Closing client ',client)
                    client.close()
                    break                
                # List all instruments
                elif client_request == 'INST|LIST\r\n':
                    response = dict()
                    for inst in self.CS.instruments_tag.keys():
                        response[inst] = str(type(self.CS.instruments_tag[inst]))
                    self.send_client(client, data, json.dumps(response))
                # Print the last read (if started) or the current value (if stopped)    
                elif (client_request == 'INST|READ\r\n') & (self.MS._STARTED == True):
                    self.send_client(client, data, json.dumps(self.CS.last_point))
                # Send commands to the instruments (by referring to them with their tags)    
                else:
                    if ('INST|' in client_request) & (self.CS._connected):
                        self.send_command(client, client_request)
                        
                    else:
                        print ('Request not valid: ', client_request)
                        self.send_client(client, data, client_request+': is not a valid instruction. Send HELP to the instruction to see the basic commands')

                time.sleep(2)
            else:
                time.sleep(2)

    def send_command(self, client, client_request):
        """send_command will format the command and send it to the client
        Send a command to the TAG instrument, saving it to the log file at
        the same time with a time stamp"""
        command = [i.split('|') for i in client_request.split(';')]
        for i in command:
            if i[1] not in self.CS.instruments_tag.keys():
                self.send_client(client, client_request.encode(), i[1]+': is not a valid instrument')
            else:
                response = None
                print (i[1],i[2])
                try:
                    response = self.CS.instruments_tag[i[1]].instrument.query(i[2].replace('\r\n',''))
                except visa.VisaIOError as err_string:
                    response = 'No response from instrument ['+str(err_string)+']'
                self.MS._add_comment('Instruction sent - '+client_request[:-2]+' Response - '+response)
#                                print ('> Data send:', response.encode())
                self.send_client(client, client_request.encode(), json.dumps(response))
        return None

    def send_client(self, client, str_recv, str_send):
        """Send the response to the client, printing it at the same time"""
        self.save_file.write(str_recv.decode()+'\n>'+str_send+'\n')
        self.save_file.flush()
        client.send((str_send+'\r\n').encode())
        return None

    def inst_server(self):
        """Initialization of the instruction server"""
        server_address = (self.ip_address[0], int(self.ip_address[1]))
        start_time = datetime.datetime.utcnow().strftime(self.CS.df)
        # Open the save file for every interaction with the IS
        self.save_file = open('logs/'+start_time+'.txt','w')
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(server_address)
        print ('%s:%s listening for client connection' % server_address)
        self.socket.listen(5)
        self._connected = True
        while True:
            # Wait for a connection
            client, client_adress = self.socket.accept()
            self.save_file.write('Connexion on '+'/'+str(client)+'/'+str(client_adress))
            # Starting the handler of this client on another thread
            client_handler = threading.Thread(target=self.handler,args=(client,))
            client_handler.start()
        return None

    def connect(self, host, port):
        """"""
        self.socket.connect((host, port))

    def _close(self):
        """Close the instruction server"""
        self.socket.close()
        self.CS._connected = False


class CommunicationServer(object):
    """Class for starting/stopping communication with the instruments
       Maybe add a separate communication log?
    """
    def __init__(self, config_file, time_fmt):
        """Initialization of the communication server"""
        # Time between measures
        self.dt = config_file["GLOBAL_CONFIG"]["sampling"]
        # Extract the instrument configuration from the config file
        dict_config = config_file["Instruments"]
        
        self.filename = time.ctime()
		# Starting pyvisa ResourceManager
        self.inst_rm = visa.ResourceManager()
        self.instruments = defaultdict(list)
        self.instruments_tag = dict()

        # Config file timeout in seconds, in pyvisa it is in ms
        timeout = int(config_file["GLOBAL_CONFIG"]["timeout"])*1000 
        
        # For each type of instrument defined in the json file
        for instrument_type in dict_config:
            # Get its tag 
            instrument_tag = dict_config[instrument_type]
            # For each instrument of this type, connect to it
            for idx,protocol in enumerate(instrument_tag['comm']):
                instrument = select_instrument(instrument_tag['ident'][idx])
                config = instrument_tag['config'][idx]
                models = instrument_tag['models']
                # gives ID_STR everytime: T001, T002 etc...
                id_str = instrument_type+str('{:03d}'.format(idx+1))

                conn = instrument(RESOURCE_STRING   = protocol, 
                                  RESOURCE_MANAGER  = self.inst_rm,
                                  RESOURCE_ID       = id_str,
                                  RESOURCE_TIMEOUT  = timeout,
                                  RESOURCE_CONFIG   = config,
                                  RESOURCE_MODEL   = models)

                if conn.connected == True:
                    print (id_str, conn, ' Connected')
                    self.instruments_tag[id_str] = conn
                    if dict_config[instrument_type]['type'] in self.instruments.keys():
                        self.instruments[dict_config[instrument_type]['type']].append(self.instruments_tag[id_str])
                    else:
                        self.instruments[dict_config[instrument_type]['type']] = [self.instruments_tag[id_str]]
                else:
                    print ('Instrument '+str(protocol)+ ' Failed to connect.')


        print (self.instruments_tag)
        self.df = time_fmt
        self._connected = True
        print ('Connexion initialization done.')


    def _read_UPSstat(self):
        """"""
#        battery_status = {**self.ups.dump_sensors()}
        return None

    def _read_setup(self):
        """Loop over the connected instrument and return the data:
        Input: None
        Output: dictionary with <tag>_<variable>:(<value>, <comment>)
        
        <tag>: created at the connection, identify the instrument (T001 for ex)
        <variable>: variable name as defined in the driver
        <value>: value formatted as defined in the driver
        <comment>: string to comment what is send as defined in the driver
        """
        results = dict()
        time = datetime.datetime.utcnow().strftime(self.df)
        results.update(Time=(time,'[str] Date with UTC time'))
        results.update(Comments=["","[str] Commments on the measure"])
        for key in self.instruments_tag.keys():
            try:
                results.update(self.instruments_tag[key].dump_sensors())

            except Exception as e:
    			# If an intrument takes to much time to respond, timeout
    			# Send a dictionnary with the error the tag
                results['Comments'][0]+='Error instrument - '+str(key)+\
                                     ' '+str(self.instruments_tag[key])+\
                                     ' '+str(e)

        return results        
        
    def _save(self):
        """"""
        self.save_file.flush()
        os.fsync(self.save_file)

    def start(self, path=''):
        try:
            start_time = datetime.datetime.utcnow().strftime(self.df)
            self.save_file = open(path+\
                                  start_time+'.txt','w')
            self.header = self._read_setup().keys()
            self.save_file.write('Reading #\t'+\
                                 '\t'.join(self.header)+'\tComments\n')
        except:
            self.cleanup()

    def stop(self):
        """"""
        self._connected = False
        for inst_tag in self.instruments_tag.keys():
            print ('Closing connection to ', inst_tag, self.instruments_tag[inst_tag])
            self.instruments_tag[inst_tag].instrument.close()
        self.inst_rm.close()


def dict_plot(input_name):
    '''Method to associate input name with a color'''
    colors_dict = dict(H1=(230,25,75),
                       H2=(0,130,200),
                       InputA=(60,180,75),
                       InputB=(255,225,25),
                       InputC=(245,130,48),
                       InputD=(128,0,0),
                       InputD2=(145,30,180),
                       InputD3=(70,240,240),
                       InputD4=(240,50,230),
                       InputD5=(210,245,60),
                       Gauge1=(230,25,75),
                       Gauge2=(0,130,200),
                       SETP1=(0,128,128),
                       SETP2=(170,110,40))

    # Return the full label, but for the color split it with the spaces and
    # take only last arg
    if 'T001' in input_name:
        style = QtCore.Qt.SolidLine
    else:
        style = QtCore.Qt.DashLine

    color = [colors_dict[i]\
             for i in colors_dict.keys()\
             if input_name.split('_')[-1].replace(' ','') in i]
    # Making the pyqtgraph pen
    pen = pg.mkPen(color=color[0], width=1.5, style=style)
    return dict(pen=pen, name=input_name)

#class TimeAxisItem(pg.AxisItem):
#    """Class used for formating x axis labels to dates"""
#    def tickStrings(self, values, scale, spacing):
#        return [datetime.datetime.fromtimestamp(value).replace(microsecond=0)\
#                for value in values]
#
class monitoring(object):
    """Monitoring class that will launch the communication server
    and can loop the _read_setup function of the CS to log the data
    into a file
    """
    def __init__ (self, time_fmt, config_file):
        """Initialization of the monitoring
        define the time format, the sampling of the data
        """
        self.df = time_fmt

		# Open the config file and load it into a dictionary
        link_file = open('config/'+config_file,'r')
        print (config_file)
        self.config_file = json.load(link_file)
        link_file.close()
        self._TIMER = int(self.config_file["GLOBAL_CONFIG"]["sampling"])
        
        # Start the communication server
        self.connect(self.df)
        self._STARTED = False
        self._STATUS = 'ACTIVE'
        # Start the Instruction Server
        self.InstructionServ = InstructionServer(self)
        # Extract the save path from the config file
        self.DATAPATH = self.config_file["GLOBAL_CONFIG"]["savepath"]
        # Connecting the SIGINT (ctrl+c) to the close method, so that
        # closing the program close the connection properly.
        # If it is not closing properly, some instruments might not
        # want another connection straight after closing!
        # (Yes, I am talking about you TPG262 controller).
        signal.signal(signal.SIGINT, self._close)

        self.infos = {'start':['Monitoring not started no timestamp available','[str] Starting date YYYY-MM-DD_hh-mm-ss'],
                      'spath':[self.DATAPATH,'[str] Path for save files'],
                      'sfile':['Monitoring not started no save file created','[str] Save file full name'],
                      'sampling':[self._TIMER,'[int] Sampling time in seconds']}

    def update_infos(self, keyword, updated_value):
        """"""
        current_value = self.infos[keyword]
        current_value[0] = updated_value
        self.infos[keyword] = current_value
    
    def update(self):
        """Update the data in the save file"""
        while self._STARTED == True:
			# Saving state ON, no closing allowed while reading
            self._SAVING = True
			# Reading index
            self.datacount += 1
            # Read the setup instruments
            read = self.comm._read_setup()
            # Request the current date [UTC]
            date_utc = datetime.datetime.utcnow()
            # Format it
            self.datatime = date_utc.strftime(self.comm.df)
			# If the day is not the same as the previous point, create another file
            if date_utc.day != self.save_startdate.day:
                self.save_file.close()
                self.header = read
                self._create_savefile(path = self.DATAPATH)                
                self.save_startdate = date_utc
            # If the keys of the read differ from the keys in the header, create another file
            if read.keys() != self.header.keys():
                self.save_file.close()
                self.header = read
                self._create_savefile(path = self.DATAPATH)
            # If a timeout occur, pass
            # I should crash here right?
            if 'Error' in read.keys():
                self.datapoint = str(self.datacount)+'\t'+\
                                 '\t'.join([val.replace('\n','') for val in read.values()])+'\t'+'\n'
                self.comm.last_point = read
                self.save_file.write(self.datapoint)
                # Every fifth read, flush the data in the file.
                # That way you don't miss more than 5*sampling worth of data if crash
                if self.datacount%1 == 0:
                    self._save()

            # Create the datapoint and write it to the save
            else:
    #            self.dates = np.append(self.dates, datetime.datetime.utcnow().timestamp())
                self.datapoint = str(self.datacount)+'\t'+\
                                 '\t'.join([read[keyw][0].replace('\n','') for keyw in read.keys() if keyw != 'Comments'])+\
                                 '\t'+read['Comments'][0].replace('\n','')+'\n'
                
                self.comm.last_point = read
                self.save_file.write(self.datapoint)
                # Every fifth read, flush the data in the file.
                # That way you don't miss more than 5*sampling worth of data if crash
                if self.datacount%1 == 0:
                    self._save()
            # Saving state OFF
            self._SAVING = False
            # Wait for _TIMER seconds
            time.sleep(self._TIMER)

    def connect(self, time_fmt):
        # Connect to the instruments
        self.comm = CommunicationServer(self.config_file, time_fmt)

    def start(self, path = ''):
        """"""
        # Get the header which will give the outputs to read
        try:
            print (path)
            self._create_savefile(path = self.DATAPATH)
        except:
            self._stop()
            self.comm.stop()
            sys.exit()

#        self.timer.start(self._TIMER)
        self._STARTED = True
        self.datacount = 0
        self.update_infos('start', datetime.datetime.utcnow().strftime(self.comm.df))
        self.update_infos('spath', self.DATAPATH)
        self.update_infos('sfile', self.save_file.name.replace(self.DATAPATH,''))
        self.update_infos('sampling', self._TIMER)
#        self.infos = {'start':(datetime.datetime.utcnow().strftime(self.comm.df),'[str] Starting date DD-MM-YYYY_hh-mm-ss'),
#                      'spath':(self.DATAPATH,'[str] Path for save files'),
#                      'sfile':(self.save_file.name.replace(self.DATAPATH,''),'[str] Save file full name'),
#                      'sampling':(self._TIMER,'[int] Sampling time in seconds')}
        
        thread1 = threading.Thread(target=self.update)
        thread1.start()
        
    def _create_savefile(self, path = ''):
        print (path)
        self.save_startdate = datetime.datetime.utcnow()

        start_time = self.save_startdate.strftime(self.comm.df)
        self.header = self.comm._read_setup()
        # Need to move 'Comments' keyword at the end of the data saved
        print (self.header)
        self.save_file = open(path+\
                              start_time+'.txt','w')
        self.save_file.write('# ___________________________________________\n')
        for i in self.header.keys():
            print (i, self.header[i])    
            self.save_file.write('# '+i+'\t'+self.header[i][1]+'\n')
        self.save_file.write('# ___________________________________________\n')
        self.save_file.write(('Reading\t'+\
                             '\t'.join(self.header)).replace('Comments\t','')+'\tComments\n')
    
    def _add_comment(self, string):
        if self._STARTED == True:
            string += '\r\n'
            timestamp = datetime.datetime.utcnow().strftime(self.comm.df)
            self.save_file.write('\t'+timestamp+'\t'*len(self.header.keys())-1+string)
        else:
            return None            
    def _save(self):
        """"""
        self.save_file.flush()
        os.fsync(self.save_file)

    def _stop(self):
        """"""
        self._STARTED = False
        while self._SAVING == True:
            # If monitoring is still saving, wait 1 second to check again
            # TIMEOUT to define?
            time.sleep(1)            
        try:
            self.save_file.close()
            print (self.save_file, ' Closed')
            self._SAVING = 'DONE'
        except:
            print ('No file to close')
            pass

    def _close(self, signal=None, frame=None):
        """"""
        try:
            self.save_file.close()
        except:
            print ('No file to close')
            pass
        self._STARTED = False

        # Closing all conections to instruments
        print ('Closing connections ...')
        self.comm.stop()
        self._STATUS = 'INACTIVE'

    def cleanup(self):
        """"""
        self._stop()
        sys.exit(1)
#
#
#
#class MonitoringWidget(pg.GraphicsWindow):
#
#    def __init__(self, time_fmt, parent=None, **kargs):
#        self.df = time_fmt
#        self.connect()
#        
#        self.header = self.comm._read_setup()
#        # Configure the layout of the plot
#        pg.setConfigOption('background', 'w')
#        pg.setConfigOption('foreground', 'k')
#        pg.GraphicsWindow.__init__(self, **kargs)
#        self.setParent(parent)
#        self.setWindowTitle('pyqtgraph example: Scrolling Plots')
#        # Change x_axis label format to dates
#        date_axis = TimeAxisItem(orientation='bottom')
#        date_axis2 = TimeAxisItem(orientation='bottom')
#        # Add a plot
#        self.p1 = self.addPlot(0,0,\
#                               labels =  {'left':'Temperature [K]',\
#                                          'bottom':'Date'},\
#                               axisItems = {'bottom': date_axis})
#        self.p1.setContentsMargins(170,5,150,5)
#        self.p2 = self.addPlot(1,0,\
#                               labels =  {'left':'Pressure [mbar]',\
#                                              'bottom':'Date'},\
#                               axisItems = {'bottom': date_axis2})
#        self.p2.setContentsMargins(150,5,150,5)
#        self.p2.setLogMode(y=True)
#
#        [p.showGrid(x=True) for p in [self.p1, self.p2]]
#        ## create a new ViewBox, link the right axis to its coordinate system
#        self.p3 = pg.ViewBox()
#        self.p1.showAxis('right')
#        self.p1.scene().addItem(self.p3)
#        self.p1.getAxis('right').linkToView(self.p3)
#        self.p3.setXLink(self.p1)
#        self.p1.getAxis('right').setLabel('Heaters %', color='#0000ff')
#
#        # Initialization of the data
#        self.Xm = np.array([0])
#        self.dates = np.array([datetime.datetime.utcnow().timestamp()])
#
#        self.monitor_curves = {}
#        self.monitor_data = {}
#
#        legend_heater = pg.LegendItem()
#        legend_temp = pg.LegendItem()
#        legend_vacuum = pg.LegendItem()
#
#        legends = [legend_heater,
#                   legend_temp,
#                   legend_vacuum]
#        [legend.setParentItem(self.p1.graphicsItem()) for legend in legends]
#        legends[2].setParentItem(self.p2.graphicsItem())
#
#        legend_temp.anchor((0,0), (0,0))
#        legend_heater.anchor((1,0), (1,0))
#        legend_vacuum.anchor((0,0), (0,0))
#
#        for keyw in self.header.keys():
#            if ('T00' in keyw[:3]) or ('P00' in keyw[:3]):
#
#                self.monitor_data[keyw] = np.array([float(self.header[keyw])])
#                if 'Gauge' in keyw:
#                    self.monitor_curves[keyw] = self.p2.plot(self.dates,\
#                                       self.monitor_data[keyw],\
#                                       **dict_plot(keyw))
#                    legends[2].addItem(self.monitor_curves[keyw],keyw)
#
#                elif ('Input' in keyw):
#                    self.monitor_curves[keyw] = self.p1.plot(self.dates,\
#                                       self.monitor_data[keyw],\
#                                       **dict_plot(keyw))
#                    legends[1].addItem(self.monitor_curves[keyw],keyw)
#
#                elif ('SETP' in keyw):
#                    self.monitor_curves[keyw] = self.p1.plot(self.dates,\
#                                       self.monitor_data[keyw],\
#                                       **dict_plot(keyw))
#                    legends[0].addItem(self.monitor_curves[keyw],keyw)
#
#                else:
#                    self.monitor_curves[keyw] = pg.PlotDataItem(self.dates,\
#                                       self.monitor_data[keyw],\
#                                       **dict_plot(keyw))
#                    self.p3.addItem(self.monitor_curves[keyw])
#                    legends[0].addItem(self.monitor_curves[keyw],keyw)
#
#        # CHANGE THE FONT SIZE AND COLOR OF ALL LEGENDS LABEL
#        legendLabelStyle = {'color': '#000',\
#                            'size': '6pt',\
#                            'bold': True,\
#                            'italic': False}
#
#        for legend in legends:
#            for item in legend.items:
#                for single_item in item:
#                    if isinstance(single_item,\
#                                  pg.graphicsItems.LabelItem.LabelItem):
#                        single_item.setText(single_item.text,\
#                                            **legendLabelStyle)
#
#        self.datacount = 0
#        self.ptr = 0
#        self._STARTED = False
#        self.timer = QtCore.QTimer(self)
#        self.timer.timeout.connect(self.update)
#
#    def update(self):
#        self.datacount += 1
#        self.datatime = datetime.datetime.utcnow().strftime(self.comm.df)
##        time_ref = time.time()
#        read = self.comm._read_setup()
##        time_read = time.time()
#        if read.keys() != self.header.keys():
#            self.save_file.close()
#            self.header = read
#            self._create_savefile(path = self.DATAPATH)
#            
#        if read == {'Error':'Timeout'}:
#            pass
#        else:
#            self.dates = np.append(self.dates, datetime.datetime.utcnow().timestamp())
#            for keyw in self.header:
#                if ('MM' not in keyw) and ('PSU' not in keyw) and ('OS' not in keyw) and ('Time' not in keyw):
#                    self.monitor_data[keyw] = np.append(self.monitor_data[keyw],\
#                                                        float(read[keyw]))
#                    self.monitor_curves[keyw].setData(self.dates,\
#                                                      self.monitor_data[keyw])
#            self.p3.setGeometry(self.p1.vb.sceneBoundingRect())
#    #        self.p3.linkedViewChanged(self.p1.vb, self.p3.XAxis)
#            QtGui.QApplication.processEvents()    # you MUST process the plot now
#            self.datapoint = str(self.datacount)+'\t'+\
#                             '\t'.join([val.replace('\n','') for val in read.values()])+'\t'+'\n'
#            
#            self.comm.last_point = read
#            self.save_file.write(self.datapoint)
#            if self.datacount%10 == 0:
#                self._save()
#
#    def connect(self):
#        # Connect to the instruments
#        self.comm = CommunicationServer(self.df)
#
#    def start(self, path = ''):
#        """"""
#        # Get the header which will give the outputs to read
#        try:
#            self._create_savefile(path)
#        except:
#            self._stop()
#            sys.exit()
#
#        self.timer.start(self._TIMER)
#
#        self._STARTED = True
#
#    def _create_savefile(self, path = ''):
#        self.DATAPATH = path
#        start_time = datetime.datetime.utcnow().strftime(self.comm.df)
#
#        self.save_file = open(path+\
#                              start_time+'.txt','w')
#        self.save_file.write('Reading #\t'+\
#                             '\t'.join(self.header)+'\tComments\n')
#
#
#    def _save(self):
#        """"""
#        self.save_file.flush()
#        os.fsync(self.save_file)
#
#    def _stop(self):
#        """"""
#        self.timer.stop()
#        try:
#            self.save_file.close()
#        except:
#            print ('No file to close')
#            pass
#        self._STARTED = False
#
#    def _close(self):
#        """"""
#        self.timer.stop()
#        try:
#            self.save_file.close()
#        except:
#            print ('No file to close')
#            pass
#        self._STARTED = False
#
#        # Closing all conections to instruments
#        self.comm.stop()
#
#    def cleanup(self):
#        """"""
#        self._stop()
#        sys.exit(1)
#
#class MyTableWidget(QWidget):
#
#    def __init__(self, parent, monitoring, main_widget):
#        super(QWidget, self).__init__(parent)
#        self.layout = QVBoxLayout(self)
#
#        # Initialize tab screen
#        self.tabs_widget = QTabWidget()
#        self.tab_log = QWidget()
#        self.tab_log.layout = QVBoxLayout(self.tabs_widget)
#
#        self.logAdd = QtWidgets.QLineEdit(main_widget)
#        self.logAdd.returnPressed.connect(self.AddToLog)        
#        self.logView = QtWidgets.QTextEdit(main_widget)
#        
#        self.tab_log.layout.addWidget(self.logAdd)
#        self.tab_log.layout.addWidget(self.logView)
#        self.tabs_widget.addTab(self.tab_log,"User log")
#
#        self.monitoring = monitoring
#        self.comm_serv = monitoring.comm
#        
#        self.tabs = []
#        self.cycle_instrument = dict()
#        self.selected_instrument = dict()
#        self.instrument_buttons = dict()
#        self.instrument_commands = dict()
#        
#        # Add tabs to widget       
#        for idx, inst_type in enumerate(self.comm_serv.instruments.keys()):
#            tab = QWidget()
#            tab.layout = QVBoxLayout()
#            self.tabs.append(tab)
#            self.tabs_widget.addTab(tab, inst_type)
#            
#            # Iterator with the different instrument for each category
#            self.cycle_instrument.update({inst_type:itertools.cycle(self.comm_serv.instruments[inst_type])})
#            self.selected_instrument.update({inst_type:next(self.cycle_instrument[inst_type])})
#            
#            # Buttons to swicth between selected instruments for comm
#            instrument_button = QtWidgets.QPushButton(inst_type)
#            instrument_button.clicked.connect(self.switchInstrument)
#            self.instrument_buttons.update({inst_type:instrument_button})
#         
#            # QLineEdits for sending commands for specific category
#            command_entry = QtWidgets.QLineEdit(main_widget)
#            command_log = QtWidgets.QTextEdit(main_widget) 
#            command_entry.returnPressed.connect(self.sendInstrument)
#            self.instrument_commands.update({inst_type:[command_entry,command_log]})
#            
#            tab.layout.addWidget(instrument_button)
#            tab.layout.addWidget(command_entry)
#            tab.layout.addWidget(command_log)
#            tab.setLayout(tab.layout)
#
#        self.tab_log.setLayout(self.tab_log.layout)
#        self.layout.addWidget(self.tabs_widget)
#
#    def switchInstrument(self):
#        '''Will switch to the next instrument in cycle_instrument'''        
#        for instrument, value in self.instrument_buttons.items():
#            if self.sender() == value:
#                self.selected_instrument[instrument] = next(self.cycle_instrument[instrument])        
#                
#    def sendInstrument(self):
#        '''Send command to selected instrument'''
#        for key, value in self.instrument_commands.items():
#            if self.sender() == value[0]:
#                instrument = key
#
#                resp = self.selected_instrument[instrument].instrument.query(self.sender().text())
#                self.logtime = datetime.datetime.utcnow().strftime(self.comm_serv.df)
#                self.logView.append(self.logtime+' - '+value[0].text()+'> '+resp)
#                value[1].append(self.logtime+' - '+value[0].text())
#                value[1].append('> '+resp)
#
#                save = '\t'+self.logtime+(len(self.monitoring.header.keys())+1)*'\t'+value[0].text()+'> '+resp
#                self.monitoring.save_file.write(save+'\n')
#
#    def AddToLog(self):
#        if (self.logAdd.text() != '') & (self.monitoring.comm._STARTED==True):
#            self.logtime = datetime.datetime.utcnow().strftime(self.comm_serv.df)
#            self.logView.append(self.logtime+' - '+self.logAdd.text())
#            self.datapoint = '\t'+self.logtime+(len(self.monitoring.header.keys())+1)*'\t'+self.logAdd.text()+'\n'
#            self.monitoring.save_file.write(self.datapoint)
#            self.logAdd.clear()
#        if (self.monitoring.comm._STARTED==False):
#            self.logView.append('Monitoring not running, cannot save comment')
#
#        
#    @pyqtSlot()
#    def on_click(self):
#        print("\n")
#        for currentQTableWidgetItem in self.tableWidget.selectedItems():
#            print(currentQTableWidgetItem.row(),\
#                  currentQTableWidgetItem.column(),\
#                  currentQTableWidgetItem.text())
#
#
#class ApplicationWindow(QtWidgets.QMainWindow):
#    def __init__(self):
#        QtWidgets.QMainWindow.__init__(self)
#        # Menu and close signal handling
#        self.DATETIME_FMT = '%d-%m-%Y_%H-%M-%S'
#        self.SAVE_PATH = 'C:\\Users\\irlab\\Desktop\\COOLDOWN_LOGS\\'
#
#        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
#        self.setWindowTitle("CRIMON")
#        self.file_menu = QtWidgets.QMenu('&File', self)
#        self.file_menu.addAction('&Quit', self.fileQuit,
#                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
#        self.file_menu.addAction('&New cooldown directory', self.fileNew,
#                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
#
#        self.menuBar().addMenu(self.file_menu)
#
#        self.help_menu = QtWidgets.QMenu('&Help', self)
#        self.menuBar().addSeparator()
#        self.menuBar().addMenu(self.help_menu)
#
#        self.help_menu.addAction('&About', self.about)
#
#        self.main_widget = QtWidgets.QWidget(self)
#        self.split_widget = QtWidgets.QSplitter(QtCore.Qt.Vertical,self.main_widget)
#        # QtWidgets.QVBoxLayout() and not QVBoxLayout() otherwise message
#        # main_widget already has a layout will appear
#        self.main_widget.layout = QtWidgets.QVBoxLayout()
#        self.main_widget.layout.addWidget(self.split_widget)
#        self.main_widget.setLayout(self.main_widget.layout)
#        self.setCentralWidget(self.main_widget)
#        self.main_widget.setFocus()
#        self.monitoring = MonitoringWidget(self.DATETIME_FMT)
#        self.split_widget.addWidget(self.monitoring)
#
#        #Reorganising layouts and widgets for v0.x
#        self.split_bottom = QtWidgets.QWidget()
#        self.split_bottom.layout = QtWidgets.QVBoxLayout()
#        self.test = QtWidgets.QWidget()
#        self.controls = QtWidgets.QWidget()
#        self.controls.layout = QtWidgets.QHBoxLayout()
#        self.label_time = QtWidgets.QLabel("Time sampling (ms)")
#        self.entry_time = QtWidgets.QLineEdit()
#        self.start_button = QtWidgets.QPushButton("Start")
#        self.stop_button = QtWidgets.QPushButton("Stop")
#        self.start_button.clicked.connect(self.start_monitoring)
#        self.stop_button.clicked.connect(self.stop_monitoring)
#        control_widgets = [self.label_time,
#                           self.entry_time,
#                           self.start_button,
#                           self.stop_button]
#        [self.controls.layout.addWidget(widg) for widg in control_widgets]
#        self.controls.setLayout(self.controls.layout)
#
#        self.table_widget = MyTableWidget(self, 
#                                          self.monitoring,
#                                          self.main_widget)
#    
#        self.split_bottom.layout.addWidget(self.controls)
#        self.split_bottom.layout.addWidget(self.table_widget)
#        self.split_bottom.setLayout(self.split_bottom.layout)
#        self.split_widget.addWidget(self.split_bottom)
##        self.split_widget.setFocus()
#
#        self.entry_time.setEnabled(True)
#        self.start_button.setEnabled(True)
#        self.stop_button.setEnabled(False)
#        [tab.setEnabled(False) for tab in self.table_widget.tabs]
#        
#        self.statusBar().showMessage(progname+' / Version '+str(progversion))
#        self.show()
#        self.InstructionServ = InstructionServer(self.monitoring.comm)
#
#    def start_monitoring(self):
#        try:
#            self.monitoring._TIMER = int(self.entry_time.text())
#            print (self.SAVE_PATH)
#            self.monitoring.start(path=self.SAVE_PATH)
#            self.entry_time.setEnabled(False)
#            self.start_button.setEnabled(False)
#            self.stop_button.setEnabled(True)
#            [tab.setEnabled(True) for tab in self.table_widget.tabs]
#
#            self.logtime = datetime.datetime.utcnow().strftime(self.DATETIME_FMT)+'\t'
#            self.statusBar().showMessage(self.logtime+' Monitoring started')
#
#        except Exception as inst:
#            print (inst)
#            self.logView.append(inst)
#
#    def stop_monitoring(self):
#        self.monitoring._stop()
#        self.entry_time.setEnabled(True)
#        self.start_button.setEnabled(True)
#        self.stop_button.setEnabled(False)
#        [tab.setEnabled(False) for tab in self.table_widget.tabs]
#
#    def fileQuit(self):
#        self.close()
#        self.monitoring._stop()
#        self.monitoring._close()
#        self.InstructionServ._close()
#
#    def fileNew(self):
#        import os, errno
#        date = datetime.datetime.utcnow().strftime(self.DATETIME_FMT)
#
#        try:
#            self.SAVE_PATH = 'C:\\Users\\irlab\\Desktop\\COOLDOWN_LOGS\\'+date+'\\'
#            os.makedirs(self.SAVE_PATH)
#        except OSError as e:
#            if e.errno != errno.EEXIST:
#                raise
#
#    def closeEvent(self, ce):
#        self.fileQuit()
#
#    def about(self):
#        QtWidgets.QMessageBox.about(self, "About",
#                                    progname+"""
#Version """+str(progversion)+""" / Copyright 2018 Benoit Serra (ESO)
#
#This program is a communication and monitoring interface for the MTF
#cryostat.
#
#It may be used and modified with no restriction; raw copies as well as
#modified versions may be distributed without limitation.
#
#This version is based on Python 3.6 pyqtgraph v0.10 and pyqt v5"""
#                                )
#

# MAIN
#########################
if __name__ == "__main__":
    if '--gui' in sys.argv:
        print ('GUI version not supported in 1.0. Exiting.')
#        qApp = QtWidgets.QApplication(sys.argv)
#        font = qApp.font()
#        font.setPointSize(9)
#        qApp.setFont(font)
#    
#        aw = ApplicationWindow()
#        aw.setWindowTitle("%s" % progname)
#        aw.show()
#        sys.exit(qApp.exec_())
    if '--conf' in sys.argv:
        idx = np.where(np.array(sys.argv)=='--conf')
        config_file = sys.argv[idx[0][0]+1]
    else:
        sys.exit('Error: no config file defined')
    if '--cli' in sys.argv:
        DATETIME_FMT = '%Y-%m-%d_%H-%M-%S'
        
        monit = monitoring(DATETIME_FMT,
                       config_file = config_file)
        
        print ('Monitoring can be started...')
        while monit._STATUS == 'ACTIVE':
            time.sleep(2)
        print ('Monitoring stopped.')
    else:
        print ('No gui or cli argument, leaving')

# GARBAGE
#########################  
