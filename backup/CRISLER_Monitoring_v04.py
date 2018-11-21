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
    self.datatime = datetime.datetime.now().strftime(self.comm.df)+'\t'
    to
    self.datatime = datetime.datetime.now().strftime(self.comm.df)


"""

# CRISLER_Monitoring.py --- Simple Qt5 application embedding pyqtgraph canvases
#                           for monitoring CRISLER
#
# Copyright (C) 2018 Benoit Serra
#
# This file is a program plotting realtime data using pyqtgraph. It may be used
# and modified with no restriction; raw copies as well as modified versions may
# be distributed without limitation.

from __future__ import unicode_literals
import sys
import os
import time, datetime
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget,QVBoxLayout
from PyQt5.QtCore import pyqtSlot

import numpy as np
import pyqtgraph as pg

import lakeshore as ls
import vacuumgauge as vg

progname = os.path.basename(sys.argv[0])
progversion = "0.4"

# Methods 
#############################
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
    pen = pg.mkPen(color=color[0], width=3, style=style)
    return dict(pen=pen, name=input_name)

class TimeAxisItem(pg.AxisItem):
    """Class used for formating x axis labels to dates"""
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).replace(microsecond=0)\
                for value in values]

class CommunicationServer(object):
    """Class for starting/stopping communication with the instruments"""
    def __init__(self,time_fmt):
        """"""
        # Time between measures
        self.dt = 10
        self.filename = time.ctime()
        
        # Lakeshore top (8 outputs)
        self.ls = ls.LakeShore33x(TCP_IP='192.168.5.1',id='001',type='T')
        # Lakeshore bottom (4 output)
        self.ls2 = ls.LakeShore33x(TCP_IP='192.168.5.2',id='002',type='T')
        print ('Connexion to Lakeshore')

        # Pfeiffer controller
        self.vg = vg.TPG262(port='COM4',id='001',type='P')
        print ('Connexion to Pfeiffer Controller')

        # UPS
#        self.ups = ups.
        self.df = time_fmt
        
    def _read_UPSstat(self):
        """"""
        battery_status = {**self.ups.dump_sensors()}
#        if battery_status[] ==

    def _read_setup(self):
        """"""
        return {**self.ls.dump_sensors(),\
                **self.ls2.dump_sensors(),\
                **self.vg.pressure_gauges()}

    def _save(self):
        """"""
        self.save_file.flush()
        os.fsync(self.save_file) 
            
    def start(self):
        try:
            start_time = datetime.datetime.now().strftime(self.df)
            self.save_file = open('C:/Users/irlab/Desktop/COOLDOWN_LOGS/'+\
                                  start_time+'.txt','w')
            self.header = self._read_setup().keys()
            self.save_file.write('Time\tReading #\t'+\
                                 '\t'.join(self.header)+'\tComments\n')
            print ('pouet')
        except:
            self.cleanup()

    def stop(self):
        """"""
        self.save_file.close()
        self.vg.serial.close()
        self.ls.close()
        
#    def cleanup(self):
#        """"""
#        self.stop()
#        sys.exit(1)
#
#        try:
#            start_time = datetime.datetime.now().strftime(self.df)
#            self.save_file = open('C:/Users/irlab/Desktop/COOLDOWN_LOGS/'+\
#                                  start_time+'.txt','w')
#            self.header = self._read_setup().keys()
#            self.save_file.write('Time\tReading #\t'+\
#                                 '\t'.join(self.header)+'\n')
#            self.get_data()            
#        except:
#            self.cleanup()


class MonitoringWidget(pg.GraphicsWindow):

    def __init__(self, time_fmt, parent=None, **kargs):

        self.df = time_fmt
        self.connect()
        self.header = self.comm._read_setup()
        # Configure the layout of the plot
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.GraphicsWindow.__init__(self, **kargs)
        self.setParent(parent)
        self.setWindowTitle('pyqtgraph example: Scrolling Plots')
        # Change x_axis label format to dates
        date_axis = TimeAxisItem(orientation='bottom')
        date_axis2 = TimeAxisItem(orientation='bottom')
        # Add a plot
        self.p1 = self.addPlot(0,0,\
                               labels =  {'left':'Temperature [K]',\
                                          'bottom':'Date'},\
                               axisItems = {'bottom': date_axis})
        self.p1.setContentsMargins(170,5,150,5)
        self.p2 = self.addPlot(1,0,\
                               labels =  {'left':'Pressure [mbar]',\
                                              'bottom':'Date'},\
                               axisItems = {'bottom': date_axis2})
        self.p2.setContentsMargins(150,5,150,5)
        self.p2.setLogMode(y=True)

        [p.showGrid(x=True) for p in [self.p1, self.p2]]
        ## create a new ViewBox, link the right axis to its coordinate system
        self.p3 = pg.ViewBox()
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p3)
        self.p1.getAxis('right').linkToView(self.p3)
        self.p3.setXLink(self.p1)
        self.p1.getAxis('right').setLabel('Heaters %', color='#0000ff')

        # Initialization of the data
        self.Xm = np.array([0])
        self.dates = np.array([datetime.datetime.now().timestamp()])
        
        self.monitor_curves = {}
        self.monitor_data = {}
    
        legend_heater = pg.LegendItem()
        legend_temp = pg.LegendItem()
        legend_vacuum = pg.LegendItem()
        
        legends = [legend_heater,
                   legend_temp,
                   legend_vacuum]
        [legend.setParentItem(self.p1.graphicsItem()) for legend in legends]
        legends[2].setParentItem(self.p2.graphicsItem())
        
        legend_temp.anchor((0,0), (0,0))
        legend_heater.anchor((1,0), (1,0))
        legend_vacuum.anchor((0,0), (0,0))
        
        for keyw in self.header.keys():
            self.monitor_data[keyw] = np.array([float(self.header[keyw])])
            if 'Gauge' in keyw:
                self.monitor_curves[keyw] = self.p2.plot(self.dates,\
                                   self.monitor_data[keyw],\
                                   **dict_plot(keyw))
                legends[2].addItem(self.monitor_curves[keyw],keyw)
                
            elif ('Input' in keyw):
                self.monitor_curves[keyw] = self.p1.plot(self.dates,\
                                   self.monitor_data[keyw],\
                                   **dict_plot(keyw))
                legends[1].addItem(self.monitor_curves[keyw],keyw)
                
            elif ('SETP' in keyw):
                self.monitor_curves[keyw] = self.p1.plot(self.dates,\
                                   self.monitor_data[keyw],\
                                   **dict_plot(keyw))
                legends[0].addItem(self.monitor_curves[keyw],keyw)

            else:
                self.monitor_curves[keyw] = pg.PlotDataItem(self.dates,\
                                   self.monitor_data[keyw],\
                                   **dict_plot(keyw))
                self.p3.addItem(self.monitor_curves[keyw])
                legends[0].addItem(self.monitor_curves[keyw],keyw)

        # CHANGE THE FONT SIZE AND COLOR OF ALL LEGENDS LABEL
        legendLabelStyle = {'color': '#000',\
                            'size': '6pt',\
                            'bold': True,\
                            'italic': False}
        
        for legend in legends:
            for item in legend.items:
                for single_item in item:
                    if isinstance(single_item,\
                                  pg.graphicsItems.LabelItem.LabelItem):
                        single_item.setText(single_item.text,\
                                            **legendLabelStyle)

        self.datacount = 0
        self.ptr = 0
        self._STARTED = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        
    def update(self):
        self.datacount += 1
        self.datatime = datetime.datetime.now().strftime(self.comm.df)
        read = self.comm._read_setup()
        self.datapoint = self.datatime+'\t'+\
                         str(self.datacount)+'\t'+\
                         '\t'.join(read.values())+'\n'  

        self.save_file.write(self.datapoint)
        if self.datacount%10 == 0:
            self._save()

        self.dates = np.append(self.dates, datetime.datetime.now().timestamp())
        for keyw in self.header:
            self.monitor_data[keyw] = np.append(self.monitor_data[keyw],\
                                                float(read[keyw]))
            self.monitor_curves[keyw].setData(self.dates,\
                                              self.monitor_data[keyw])

        self.p3.setGeometry(self.p1.vb.sceneBoundingRect())
        self.p3.linkedViewChanged(self.p1.vb, self.p3.XAxis)
        QtGui.QApplication.processEvents()    # you MUST process the plot now

    def connect(self):
        # Connect to the instruments
        self.comm = CommunicationServer(self.df)

    def start(self):
        """"""
        # Get the header which will give the outputs to read
        try:
            start_time = datetime.datetime.now().strftime(self.comm.df)

            self.save_file = open('C:/Users/irlab/Desktop/COOLDOWN_LOGS/'+\
                                  start_time+'.txt','w')
            self.save_file.write('Time\tReading #\t'+\
                                 '\t'.join(self.header)+'\tComments\n')

        except:
            self._stop()
            sys.exit()
            
        self.timer.start(self._TIMER)
        self._STARTED = True

    def _save(self):
        """"""
        self.save_file.flush()
        os.fsync(self.save_file) 

    def _stop(self):
        """"""
        self.timer.stop()
        try:
            self.save_file.close()
        except:
            print ('No file to close')
            pass
        self._STARTED = False

        self.comm.vg.serial.close()
        self.comm.ls.close()

    def cleanup(self):
        """"""
        self.stop()
        sys.exit(1)

class MyTableWidget(QWidget):        
 
    def __init__(self, parent):   
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
 
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()	
        self.tab2 = QWidget()
        self.tab3 = QWidget()
 
        # Add tabs
        self.tabs.addTab(self.tab1,"User log")
        self.tabs.addTab(self.tab2,"Lakeshore commands")
        self.tabs.addTab(self.tab3,"Pfeiffer commands")
 
        # Create first tab
        self.tab1.layout = QVBoxLayout(self.tabs)
        self.tab1.setLayout(self.tab1.layout)
        # Create second tab
        self.tab2.layout = QVBoxLayout(self.tabs)
        self.tab2.setLayout(self.tab2.layout)
        # Create third tab
        self.tab3.layout = QVBoxLayout(self.tabs)
        self.tab3.setLayout(self.tab3.layout)
        
        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
 
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(),\
                  currentQTableWidgetItem.column(),\
                  currentQTableWidgetItem.text())
 

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # Menu and close signal handling
        self.DATETIME_FMT = '%d-%m-%Y_%H-%M-%S'
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)
        
        self.main_widget = QtWidgets.QWidget(self)
        self.l = QtWidgets.QSplitter(QtCore.Qt.Vertical,self.main_widget)
        # QtWidgets.QVBoxLayout() and not QVBoxLayout() otherwise message
        # main_widget already has a layout will appear
        self.main_widget.layout = QtWidgets.QVBoxLayout()
        self.main_widget.layout.addWidget(self.l)
        self.main_widget.setLayout(self.main_widget.layout)
        self.setCentralWidget(self.main_widget)        
        self.main_widget.setFocus()
        self.dc = MonitoringWidget(self.DATETIME_FMT)
        self.l.addWidget(self.dc)

        #Reorganising layouts and widgets for v0.x
        self.split_bottom = QtWidgets.QWidget()
        self.split_bottom.layout = QtWidgets.QVBoxLayout()
        self.test = QtWidgets.QWidget()
        self.controls = QtWidgets.QWidget()
        self.controls.layout = QtWidgets.QHBoxLayout()
        self.label_time = QtWidgets.QLabel("Period (ms)")
        self.entry_time = QtWidgets.QLineEdit()
        self.start_button = QtWidgets.QPushButton("Start")
        self.stop_button = QtWidgets.QPushButton("Stop")        
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        control_widgets = [self.label_time,
                           self.entry_time,
                           self.start_button,
                           self.stop_button]
        [self.controls.layout.addWidget(widg) for widg in control_widgets]
        self.controls.setLayout(self.controls.layout)
        self.split_bottom.layout.addWidget(self.controls)

        self.logAdd = QtWidgets.QLineEdit(self.main_widget)
        self.logAdd.returnPressed.connect(self.AddToLog)
        self.logView = QtWidgets.QTextEdit(self.main_widget) 

        self.LakeShoreSend = QtWidgets.QLineEdit(self.main_widget)
        self.LakeShoreSend.returnPressed.connect(self.sendLakeshore)
        self.LakeShoreResp = QtWidgets.QTextEdit(self.main_widget) 

        self.table_widget = MyTableWidget(self)
        self.table_widget.tab1.layout.addWidget(self.logAdd)
        self.table_widget.tab1.layout.addWidget(self.logView)
        self.table_widget.tab1.setLayout(self.table_widget.tab1.layout)
        self.table_widget.tab2.layout.addWidget(self.LakeShoreSend)
        self.table_widget.tab2.layout.addWidget(self.LakeShoreResp)
        self.table_widget.tab2.setLayout(self.table_widget.tab2.layout)
        self.split_bottom.layout.addWidget(self.table_widget)
        self.split_bottom.setLayout(self.split_bottom.layout)

        self.l.addWidget(self.split_bottom)
#        self.l.setFocus()

        self.entry_time.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.table_widget.tab1.setEnabled(False)
        self.table_widget.tab2.setEnabled(False)

        self.statusBar().showMessage(progname+' / Version '+str(progversion))
        self.show()
        
    def start_monitoring(self):
        try:
            self.dc._TIMER = int(self.entry_time.text())
            self.dc.start()        
            self.entry_time.setEnabled(False)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.table_widget.tab1.setEnabled(True)
            self.table_widget.tab2.setEnabled(True)

            self.logtime = datetime.datetime.now().strftime(self.DATETIME_FMT)+'\t'
            self.statusBar().showMessage(self.logtime+' Monitoring started')

        except:
            self.logView.append('Period (ms) must be an integer value') 
            


    def stop_monitoring(self):
        self.dc._stop()
        self.entry_time.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.table_widget.tab1.setEnabled(False)
        self.table_widget.tab2.setEnabled(False)
        
    def sendLakeshore(self):
        if (self.LakeShoreSend.text() != '') & (self.dc._STARTED==True):
            resp = self.dc.comm.ls._send_command(self.LakeShoreSend.text())
            self.logtime = datetime.datetime.now().strftime(self.DATETIME_FMT)
 
            query = self.logtime+' QUERY LS: '+self.LakeShoreSend.text() 
            save = self.logtime+'\t'+(len(self.dc.header.keys())+1)*'\t'+self.LakeShoreSend.text()+'> '+resp
            self.LakeShoreResp.append(query)
            self.LakeShoreResp.append('> '+resp)
            self.dc.save_file.write(save+'\n')
            
    def AddToLog(self):
        if (self.logAdd.text() != '') & (self.dc._STARTED==True):
            self.logtime = datetime.datetime.now().strftime(self.DATETIME_FMT)
            self.logView.append(self.logtime+' - '+self.logAdd.text()) 
            self.datapoint = self.logtime+'\t'+(len(self.dc.header.keys())+1)*'\t'+self.logAdd.text()+'\n' 
            self.dc.save_file.write(self.datapoint)
            self.logAdd.clear()
        if (self.dc._STARTED==False):
            self.logView.append('Monitoring not running, cannot save comment')       
            
    def fileQuit(self):
        self.close()
        self.dc._stop()
        
    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    progname+"""
Version """+str(progversion)+""" / Copyright 2018 Benoit Serra (ESO)

This program is a communication and monitoring interface for the CRISLER
cryostat.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation.

This version is based on Python 3.6 pyqtgraph v0.10 and pyqt v5"""
                                )
if __name__ == "__main__":
    qApp = QtWidgets.QApplication(sys.argv)
    font = qApp.font()
    font.setPointSize(9)
    qApp.setFont(font)
    
    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
#qApp.exec_()