# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 13:58:11 2018

@author: irlab
"""

from collections import deque

import time

import matplotlib.pyplot as plt
import numpy as np

import sys

# Methods 
#############################
def dict_plot(input_name):
    '''Method to associate input name with a color'''
    colors_dict = dict(O1='#00ff00',
                       O2='black',
                       O3='#ffc800')

    # Return the full label, but for the color split it with the spaces and take only last arg
    return dict(label=input_name,color=colors_dict[input_name.split(' ')[-1]])

# RealTime plot class
class MonitoringPlot:
    def __init__(self, axes):
        self.axes = axes
        self.axis_x = np.array([])
        self.l1, = axes.plot([], [], "r-",**dict_plot('O1'))
        self.l2, = axes.plot([], [], "r-",**dict_plot('O2'))
        self.l3, = axes.plot([], [], "r-",**dict_plot('O3'))

        self.axes.set_autoscaley_on(True)
        axes.legend()

    def add(self, x, y):
        self.axis_x = np.append(self.axis_x, x)
        self.l1.set_data(self.axis_x, np.append(self.l1.get_ydata(), float(y['O1'])))
        self.l2.set_data(self.axis_x, np.append(self.l2.get_ydata(), float(y['O2'])))
        self.l3.set_data(self.axis_x, np.append(self.l3.get_ydata(), float(y['O3'])))

        self.axes.set_ylim(0.5,3.5)
        self.axes.relim()
        self.axes.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 1000):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval,blit=True)


class monitor(object):
    
    def __init__(self):
        """"""
        # Time between measures
        self.dt = .1

    def _read_setup(self):
        """Should communicate with devices to obtain values"""
        return {'O1':'1',
                'O2':'2',
                'O3':'3'}
            
    def start(self):
        try:
            self.get_data()            
        except:
            self.cleanup()

    def get_data(self):
        """Start the monitoring"""    
        fig, axes = plt.subplots()
        display = MonitoringPlot(axes)
        T = True
        datacount = 0
        
        try:
            while T is True:
                datacount += 1
                read = self._read_setup()
                display.add(datacount, read)
                plt.pause(.1)
                time.sleep(self.dt)

            self.save_file.close()
                
        # If user break exec
        except KeyboardInterrupt:
            e = sys.exc_info()[0]
            self.stop()
            sys.exit(e)          
            
    def stop(self):
        """"""
        return None
        
    def cleanup(self):
        """"""
        return None
    
    
if __name__=='__main__':  
    monitoring = monitor()
    monitoring.start()