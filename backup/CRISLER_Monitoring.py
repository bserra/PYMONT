# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 11:12:03 2018

@author: irlab
"""

# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#               2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

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
progversion = "0.1"

# Methods 
#############################
def dict_plot(input_name):
    '''Method to associate input name with a color'''
    colors_dict = dict(H1=(255,0,0),
                       H2=(0,0,255),
                       InputA=(0,255,0),
                       InputB=(64,64,64),
                       InputC=(255,200,0),
                       InputD=(255,0,255),
                       InputD2=(0,255,255),
                       InputD3=(200,200,200),
                       InputD4=(255,175,175),
                       InputD5=(168,64,194),
                       Gauge1=(255,0,0),
                       Gauge2=(0,0,255),
                       SETP1=(255,0,0),
                       SETP2=(0,255,0))

    # Return the full label, but for the color split it with the spaces and take only last arg
    return dict(name=input_name,pen=colors_dict[input_name.replace(' ','')])

class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value) for value in values]

class CommumicationServer(object):
    """"""
    def __init__(self):
        """"""
        # Time between measures
        self.dt = 10
        self.filename = time.ctime()
        self.ls = ls.LakeShore33x()
        print ('Connexion to Lakeshore')
        self.vg = vg.TPG262()
        print ('Connexion to Pfeiffer Controller')
        self.df = '%Y-%m-%d_%H-%M-%S.%f'

    def _read_setup(self):
        """"""
        return {**self.ls.dump_sensors(),\
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
                                 '\t'.join(self.header)+'\n')
        except:
            self.cleanup()

    def stop(self):
        """"""
        self.save_file.close()
        self.vg.serial.close()
        self.ls.close()
        
    def cleanup(self):
        """"""
        self.stop()
        sys.exit(1)

        try:
            start_time = datetime.datetime.now().strftime(self.df)
            self.save_file = open('C:/Users/irlab/Desktop/COOLDOWN_LOGS/'+\
                                  start_time+'.txt','w')
            self.header = self._read_setup().keys()
            self.save_file.write('Time\tReading #\t'+\
                                 '\t'.join(self.header)+'\n')
            self.get_data()            
        except:
            self.cleanup()


class MonitoringWidget(pg.GraphicsWindow):

    def __init__(self, parent=None, **kargs):

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
        p1 = self.addPlot(0,0,labels =  {'left':'Temperature [K]', 'bottom':'Date'},axisItems = {'bottom': date_axis})
        p1.addLegend()
        p2 = self.addPlot(1,0,labels =  {'left':'Pressure [mbar]', 'bottom':'Date'},axisItems = {'bottom': date_axis2})
        p2.addLegend()
        # Initialization of the data
        self.Xm = np.array([0])
        self.dates = np.array([datetime.datetime.now().timestamp()])
        
        self.monitor_curves = {}
        self.monitor_data = {}
        for keyw in self.header.keys():
            self.monitor_data[keyw] = np.array([float(self.header[keyw])])
            if 'Gauge' in keyw:
                self.monitor_curves[keyw] = p2.plot(self.dates, self.monitor_data[keyw], **dict_plot(keyw))
            else:
                self.monitor_curves[keyw] = p1.plot(self.dates, self.monitor_data[keyw], **dict_plot(keyw))
        self.datacount = 0
        self.ptr = 0
        self._STARTED = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        
    def update(self):
        self.datacount += 1
        self.datatime = datetime.datetime.now().strftime(self.comm.df)+'\t'
        read = self.comm._read_setup()
        self.datapoint = self.datatime+'\t'+\
                         str(self.datacount)+'\t'+\
                         '\t'.join(read.values())+'\n'  

        self.save_file.write(self.datapoint)
        if self.datacount%10 == 0:
            self._save()

        self.dates = np.append(self.dates, datetime.datetime.now().timestamp())
        for keyw in self.header:
            self.monitor_data[keyw] = np.append(self.monitor_data[keyw], float(read[keyw]))
            self.monitor_curves[keyw].setData(self.dates,self.monitor_data[keyw])


        QtGui.QApplication.processEvents()    # you MUST process the plot now

    def connect(self):
        # Connect to the instruments
        self.comm = CommumicationServer()
        self.comm.start()        

    def start(self):
        """"""
        # Get the header which will give the outputs to read
        try:
            start_time = datetime.datetime.now().strftime(self.comm.df)

            self.save_file = open('C:/Users/irlab/Desktop/COOLDOWN_LOGS/'+\
                                  start_time+'.txt','w')
            self.save_file.write('Time\tReading #\t'+\
                                 '\t'.join(self.header)+'\n')

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

#        self.comm.vg.serial.close()
#        self.comm.ls.close()

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
        self.tabs.resize(300,200) 
 
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
#        self.setLayout(self.layout)
 
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
 

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # Menu and close signal handling
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
        self.l = QtWidgets.QSplitter(QtCore.Qt.Vertical) #self.main_widget,
        
        self.dc = MonitoringWidget()
        self.l.addWidget(self.dc)

        self.split_top = QtWidgets.QWidget()
        self.split_bottom = QtWidgets.QWidget()
        
        self.test = QtWidgets.QWidget()
        self.controls = QtWidgets.QHBoxLayout()
        self.label_time = QtWidgets.QLabel("Period (ms)")
        self.entry_time = QtWidgets.QLineEdit()
        self.entry_time.setFixedWidth(200)
        self.start_button = QtWidgets.QPushButton("Start")
        self.stop_button = QtWidgets.QPushButton("Stop")        
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        control_widgets = [self.label_time,
                           self.entry_time,
                           self.start_button,
                           self.stop_button]
#        [widg.setAlignment(QtCore.Qt.AlignLeft) for widg in control_widgets]
        self.controls.setSpacing(5)
        self.controls.setAlignment(QtCore.Qt.AlignLeft)
        [self.controls.addWidget(widg) for widg in control_widgets]
        self.split_bottom.addLayout(self.controls)

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
        self.split_bottom.addWidget(self.table_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage('CRISLER Monitoring Tool v0.1')

        self.entry_time.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.table_widget.tab1.setEnabled(False)
        self.table_widget.tab2.setEnabled(False)

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

            self.logtime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'\t'
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
        if (self.LakeShoreSend.text()) != '' & (self.dc._STARTED==True):
            resp = self.dc.comm.ls._send_command(self.LakeShoreSend.text())
            self.logtime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')+'\t'
 
            query = self.logtime+' QUERY LS: '+self.LakeShoreSend.text() 
            save = self.logtime+14*'\t'+self.LakeShoreSend.text()+'> '+resp
            self.LakeShoreResp.append(query)
            self.LakeShoreResp.append('> '+resp)
            self.dc.save_file.write(save)
            
    def AddToLog(self):
        if (self.logAdd.text() != '') & (self.dc._STARTED==True):
            self.logView.append(str(datetime.datetime.now())+self.logAdd.text()) 
            self.logtime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')+'\t'
            self.datapoint = self.logtime+14*'\t'+self.logAdd.text()+'\n' 
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
                                    """embedding_in_qt5.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale, 2015 Jens H Nielsen

This program is a simple example of a Qt5 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation.

This is modified from the embedding in qt4 example to show the difference
between qt4 and qt5"""
                                )


qApp = QtWidgets.QApplication(sys.argv)
font = qApp.font()
font.setPointSize(9)
qApp.setFont(font)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()