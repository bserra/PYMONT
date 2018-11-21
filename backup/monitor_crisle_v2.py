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

class RealtimePlot:
    
    
    
    
    
    def __init__(self, axes, nb_lines, max_entries = 100):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries
        
        self.l1, = axes.plot([], [], "r-",**dict_plot('H1'))
        self.l2, = axes.plot([], [], "r-",**dict_plot('H2'))
        self.l3, = axes.plot([], [], "r-",**dict_plot('A'))
        self.l4, = axes.plot([], [], "r-",**dict_plot('B'))
        self.l5, = axes.plot([], [], "r-",**dict_plot('C'))
        self.l6, = axes.plot([], [], "r-",**dict_plot('D'))
        self.l7, = axes.plot([], [], "r-",**dict_plot('D2'))
        self.l8, = axes.plot([], [], "r-",**dict_plot('D3'))
        self.l9, = axes.plot([], [], "r-",**dict_plot('D4'))
        self.l10, = axes.plot([], [], "r-",**dict_plot('D5'))
        self.l11, = axes.plot([], [], "r-",**dict_plot('G1'))
        self.l12, = axes.plot([], [], "r-",**dict_plot('G2'))
        self.axes.set_autoscaley_on(True)
        axes.legend()

    def add(self, x, y):
        self.axis_x.append(x)
#        self.axis_y.append(float(y))
        self.l1.set_data(self.axis_x, np.append(self.l1.get_ydata(), float(y['H1'])))
        self.l2.set_data(self.axis_x, np.append(self.l2.get_ydata(), float(y['H2'])))
        self.l3.set_data(self.axis_x, np.append(self.l3.get_ydata(), float(y['Input A'])))
        self.l4.set_data(self.axis_x, np.append(self.l4.get_ydata(), float(y['Input B'])))
        self.l5.set_data(self.axis_x, np.append(self.l5.get_ydata(), float(y['Input C'])))
        self.l6.set_data(self.axis_x, np.append(self.l6.get_ydata(), float(y['Input D'])))
        self.l7.set_data(self.axis_x, np.append(self.l7.get_ydata(), float(y['Input D2'])))
        self.l8.set_data(self.axis_x, np.append(self.l8.get_ydata(), float(y['Input D3'])))
        self.l9.set_data(self.axis_x, np.append(self.l9.get_ydata(), float(y['Input D4'])))
        self.l10.set_data(self.axis_x, np.append(self.l10.get_ydata(), float(y['Input D5'])))
        self.l11.set_data(self.axis_x, np.append(self.l11.get_ydata(), float(y['Gauge 1'])))
        self.l12.set_data(self.axis_x, np.append(self.l12.get_ydata(), float(y['Gauge 2'])))
#        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1])
        self.axes.set_ylim(-10,60)
        self.axes.relim()
        self.axes.autoscale_view() # rescale the y-axis
        print (x, y)
        print (self.axis_x, self.l1.get_xdata())

    def animate(self, figure, callback, interval = 1000):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
#            self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval,blit=True)


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

        display = RealtimePlot(axes, len(self.header))
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
                plt.pause(.1)
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
        
