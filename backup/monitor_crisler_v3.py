# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 13:58:11 2018

@author: irlab
"""

import lakeshore as ls
import vacuumgauge as vg
from collections import deque

import time, random

import matplotlib.pyplot as plt
import numpy as np

import datetime
import os, sys

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg


class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(True)
        self.view.setRange(QtCore.QRectF(0,0, 100, 100))

        #  image plot
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)

        self.canvas.nextRow()
        #  line plot
        self.otherplot = self.canvas.addPlot()
        self.h2 = self.otherplot.plot(pen='y')


        #### Set Data  #####################

        self.x = np.linspace(0,50., num=100)
        self.X,self.Y = np.meshgrid(self.x,self.x)

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        self.data = np.sin(self.X/3.+self.counter/9.)*np.cos(self.Y/3.+self.counter/9.)
        self.ydata = np.sin(self.x/3.+ self.counter/9.)

        self.img.setImage(self.data)
        self.h2.setData(self.ydata)

        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        QtCore.QTimer.singleShot(1, self._update)
        self.counter += 1

class monitor(object):
    
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
            self.get_data()            
        except:
            self.cleanup()

    def get_data(self):
        """Start the monitoring"""    
            
        def display_data(self):
            """"""
 
        fig, axes = plt.subplots()
        display = RealtimePlot(axes,len(self.header))
        T = True
        datacount = 0
        try:
            while T is True:
                datacount += 1
                self.datatime = datetime.datetime.now().strftime(self.df)+'\t'
                read = self._read_setup()
                self.datapoint = self.datatime+'\t'+\
                                 str(datacount)+'\t'+\
                                 '\t'.join(read.values())+'\n'

                self.save_file.write(self.datapoint)
                if datacount%10 == 0:
                    self._save()
                display.add(datacount, read)
                plt.pause(1)
                time.sleep(.5)

            self.save_file.close()
                
        except KeyboardInterrupt:
            self.datatime = datetime.datetime.now().strftime(self.df)+'\t'
            self.save_file.write(self.datatime+'\tProgram interrupted by user\n')
            self._save()
            e = sys.exc_info()[0]
            self.stop()
            sys.exit(e)
        except:
            self.datatime = datetime.datetime.now().strftime(self.df)+'\t'
            self.save_file.write(self.datatime+'\tProgram crashed\n')
            self._save()
            e = sys.exc_info()[0]
            print (e)
            self.stop()
            sys.exit(e)            
            
    def stop(self):
        """"""
        self.save_file.close()
        self.vg.serial.close()
        self.ls.close()
        
    def cleanup(self):
        """"""
        self.stop()
        sys.exit(1)