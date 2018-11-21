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
import random
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
import matplotlib.dates as md

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import lakeshore as ls
import vacuumgauge as vg

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

# Methods 
#############################
def dict_plot(input_name):
    '''Method to associate input name with a color'''
    colors_dict = dict(A='#00ff00',
                       B='black',
                       C='#ffc800',
                       D='magenta',
                       D2='cyan',
                       D3='grey',
                       D4='#ffafaf',
                       D5='purple',
                       H1='blue',
                       H2='red',
                       G1='red',
                       G2='blue')

    # Return the full label, but for the color split it with the spaces and take only last arg
    return dict(label=input_name,color=colors_dict[input_name.split(' ')[-1]])

class Monitor(object):
    """"""
    def __init__(self):
        """"""
        # Time between measures
        self.dt = 10
        self.filename = time.ctime()
        self.ls = ls.LakeShore33x()
        self.vg = vg.TPG262()
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


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
#        self.axes = self.fig.add_subplot(111)
        self.axes_temp = self.fig.add_subplot(211)
        self.axes_heat = self.axes_temp.twinx()
        self.axes_press = self.fig.add_subplot(212)
#        self.axes.set_ylim((0,10))
#        self.axes.set_xlim((0,10))
#        self.axes.xaxis_date()
        xfmt = md.DateFormatter('%y-%m-%d %H:%M:%S')
        self.axes_temp.xaxis.set_major_formatter(xfmt)
        self.axes_press.xaxis.set_major_formatter(xfmt)
        self.fig.autofmt_xdate() 
        self.axes_press.grid(True)
        self.axes_temp.grid(True)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(5000)
        self.autoscale = True
        self.axis_x = np.array([])
        self.datacount = 0

        self.monitor = Monitor()
        self.monitor.start()

        try:
            start_time = datetime.datetime.now().strftime(self.monitor.df)
            self.save_file = open('C:/Users/irlab/Desktop/COOLDOWN_LOGS/'+\
                                  start_time+'.txt','w')
            self.header = self.monitor._read_setup().keys()
            self.save_file.write('Time\tReading #\t'+\
                                 '\t'.join(self.header)+'\n')
            self.fig.suptitle(self.save_file.name)

        except:
            self._stop()
            sys.exit()


    def _save(self):
        """"""
        self.save_file.flush()
        os.fsync(self.save_file) 

    def _stop(self):
        """"""
        self.save_file.close()
        self.monitor.vg.serial.close()
        self.monitor.ls.close()

    def cleanup(self):
        """"""
        self.stop()
        sys.exit(1)
        
    def compute_initial_figure(self):
        self.l1, = self.axes_heat.plot([], [],**dict_plot('H1'))
        self.l2, = self.axes_heat.plot([], [],**dict_plot('H2'))
        self.l3, = self.axes_temp.plot([], [],**dict_plot('A'))
        self.l4, = self.axes_temp.plot([], [],**dict_plot('B'))
        self.l5, = self.axes_temp.plot([], [],**dict_plot('C'))
        self.l6, = self.axes_temp.plot([], [],**dict_plot('D'))
        self.l7, = self.axes_temp.plot([], [],**dict_plot('D2'))
        self.l8, = self.axes_temp.plot([], [],**dict_plot('D3'))
        self.l9, = self.axes_temp.plot([], [],**dict_plot('D4'))
        self.l10, = self.axes_temp.plot([], [],**dict_plot('D5'))
        self.l11, = self.axes_press.plot([], [],**dict_plot('G1'))
        self.l12, = self.axes_press.plot([], [],**dict_plot('G2'))
        self.axes_temp.legend()
        self.axes_heat.legend()
        self.axes_press.legend()
        
    def update_figure(self):
        self.datacount += 1
        self.datatime = datetime.datetime.now().strftime(self.monitor.df)+'\t'
        read = self.monitor._read_setup()
        self.datapoint = self.datatime+'\t'+\
                         str(self.datacount)+'\t'+\
                         '\t'.join(read.values())+'\n'  

        self.save_file.write(self.datapoint)
        if self.datacount%10 == 0:
            self._save()

        self.axis_x = np.append(self.axis_x, datetime.datetime.now())
        self.l1.set_data(self.axis_x, np.append(self.l1.get_ydata(), float(read['H1'])))
        self.l2.set_data(self.axis_x, np.append(self.l2.get_ydata(), float(read['H2'])))
        self.l3.set_data(self.axis_x, np.append(self.l3.get_ydata(), float(read['Input A'])))
        self.l4.set_data(self.axis_x, np.append(self.l4.get_ydata(), float(read['Input B'])))
        self.l5.set_data(self.axis_x, np.append(self.l5.get_ydata(), float(read['Input C'])))
        self.l6.set_data(self.axis_x, np.append(self.l6.get_ydata(), float(read['Input D'])))
        self.l7.set_data(self.axis_x, np.append(self.l7.get_ydata(), float(read['Input D2'])))
        self.l8.set_data(self.axis_x, np.append(self.l8.get_ydata(), float(read['Input D3'])))
        self.l9.set_data(self.axis_x, np.append(self.l9.get_ydata(), float(read['Input D4'])))
        self.l10.set_data(self.axis_x, np.append(self.l10.get_ydata(), float(read['Input D5'])))
        self.l11.set_data(self.axis_x, np.append(self.l11.get_ydata(), float(read['Gauge 1'])))
        self.l12.set_data(self.axis_x, np.append(self.l12.get_ydata(), float(read['Gauge 2']))) 
        if self.autoscale == True:
            [ax.relim() for ax in [self.axes_temp, self.axes_heat, self.axes_press]]
            [ax.autoscale() for ax in [self.axes_temp, self.axes_heat, self.axes_press]]
        self.draw()

class MyTableWidget(QWidget):        
 
    def __init__(self, parent):   
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
 
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()	
        self.tab2 = QWidget()
        self.tabs.resize(300,200) 
 
        # Add tabs
        self.tabs.addTab(self.tab1,"Tab 1")
        self.tabs.addTab(self.tab2,"Tab 2")
 
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("PyQt5 button")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)
 
        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
 
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
        self.l = QtWidgets.QVBoxLayout(self.main_widget)
#        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        nav = NavigationToolbar(self.dc, self.main_widget)    
#        test = QtWidgets.QPushButton('START',self.main_widget)
#        test.released.connect(self.startMonitoring)
        self.logAdd = QtWidgets.QLineEdit(self.main_widget)
        self.logAdd.returnPressed.connect(self.AddToLog)
        self.logView = QtWidgets.QTextEdit(self.main_widget) 
        radiobutton = QtWidgets.QRadioButton("Autoscale Plot")
        radiobutton.setChecked(True)
        radiobutton.country = "Brazil"
        radiobutton.toggled.connect(self.on_radio_button_toggled)


        self.table_widget = MyTableWidget(self)
        self.l.addWidget(self.dc)
        self.l.addWidget(radiobutton)
        self.l.addWidget(nav)
        self.l.addWidget(self.table_widget)
        self.l.addWidget(self.logAdd)
        self.l.addWidget(self.logView)
#        self.l.addWidget(test)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)
    
    def AddToLog(self):
        if self.logAdd.text() != '':
            self.logView.append(str(datetime.datetime.now())+self.logAdd.text()) 
            self.logtime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')+'\t'
            self.datapoint = self.logtime+14*'\t'+self.logAdd.text()+'\n' 
            self.dc.save_file.write(self.datapoint)
            self.logAdd.clear()
    
    def on_radio_button_toggled(self):
        radiobutton = self.sender()

        if radiobutton.isChecked():
            self.dc.autoscale=True
        else:
            self.dc.autoscale=False
         
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

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()