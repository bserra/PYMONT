# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 13:58:11 2018

@author: irlab
"""

import lakeshore as ls
import vacuumgauge as vg

import time, random

import matplotlib.pyplot as plt
import numpy as np

from collections import deque
from matplotlib.animation import FuncAnimation


class RealtimePlot:
    def __init__(self, axes, max_entries = 100):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries
        
        self.lineplot, = axes.plot([], [], "ro-")
        self.axes.set_autoscaley_on(True)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
#        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 50):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval)

class monitor(object):
    
    def __init__(self):
        """"""
        # Time between measures
        self.dt = 10
        self.filename = time.ctime()
        self.ls = ls.LakeShore33x()
        self.vg = vg.TPG262()
        
    def _read_setup(self):
        """"""
        return {**self.ls.dump_sensors(),\
    **self.vg.pressure_gauges()}
            
    def start(self):
        """Start the monitoring"""
#        def _display():
#            """"""
#            self.moni_fig, self.moni_ax = plt.subplots()
#            self.line, = self.moni_ax.plot([], [], 'k-')
#            self.moni_ax.set_xlim((1,100))
#            self.moni_ax.set_ylim((0,100))
#            self.x = np.array([])
#            self.y = np.array([])
#            plt.ion()
#            return None

#        def _save(self):
#            """"""
#            return None
        
        start = time.time()
        maxi_meas = 10
        meas = 0
#        _display()
#        self.moni_fig.canvas.draw_idle()
    
        fig, axes = plt.subplots()
        display = RealtimePlot(axes)
        while True:
            display.add(time.time() - start, self._read_setup()['Gauge 1'])
            plt.pause(.1)

#        while meas!=maxi_meas:
##            b = ('Measure ',meas)
#            a = (self._read_setup())
#            self.x = np.append(self.x,meas)
#            self.y = np.append(self.y,a['Gauge 1'])
#            print (a['Gauge 1'])
#            # Choose success based on exceed a threshold with a uniform pick
#            self.line.set_data(self.x,self.y)
#            plt.pause(0.02)
#            self.moni_fig.canvas.draw_idle()
#            try:
#                # make sure that the GUI framework has a chance to run its event loop
#                # and clear any GUI events.  This needs to be in a try/except block
#                # because the default implementation of this method is to raise
#                # NotImplementedError
#                self.moni_fig.canvas.flush_events()
#            except NotImplementedError:
#                pass
#            time.sleep(1)
#            meas += 1
            

            
    def stop(self):
        """"""
        self.vg.serial.close()
        self.ls.close()