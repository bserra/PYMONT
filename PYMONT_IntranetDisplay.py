# -*- coding: utf-8 -*-
"""
Created on Wed May  9 16:41:14 2018

@author: bserra
"""

# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from itertools import cycle
import os
import json

# bokeh basics
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.plotting import show, ColumnDataSource
from bokeh.models import LinearAxis, Range1d

#import bokeh as bk

import glob

#cooldown_folders =glob.glob('/home/pi/Softwares/Monitoring_v1.x/*.txt')
#print (cooldown_folders)
#list_folders = [i.split('/')[-2] for i in cooldown_folders]
#print (list_folders)
#list_dates = [datetime.strptime(i,'%d-%m-%Y_%H-%M-%S') for i in list_folders]
#print (list_dates)
#more_recent = [idx for idx,j in enumerate(list_dates) if j == max(list_dates)]
#files = glob.glob(cooldown_folders[more_recent[0]]+'/*.txt')

date_fmt = '%Y-%m-%d_%H-%M-%S'
files = glob.glob('./*.txt')
config_display = "./config/d-PYMONT.json"
config_display = json.load(open(config_display))

# Methods 
#############################

# Main 
#############################
for idx, file in enumerate(files):
    print (file)
    txt = pd.read_csv(file,sep='\t', dtype={'Time': object},header=0,comment='#')
    if idx == 0:
        df = txt
    else:
        df = pd.concat([df,txt],ignore_index=True)        

#df2 = df[df['Comments'].notna()]
#df2['Time'] = pd.to_datetime(df2.Time, format=date_fmt) 

df = df[df['Comments'].isna()]
df['Time'] = pd.to_datetime(df.Time, format=date_fmt)
df = df.sort_values(by=['Time'])

# Create a blank figure with labels
test = list()

count =0
## Plot all temperatures

num_data = 5*360 # max number of data point

instruments_log = np.unique([i.split('_')[0] for i in df.columns if i not in ['Comments','Reading','Time', 'OS001', 'PSU002']])
instruments_display = np.unique([i.split('_')[0] for i in config_display["fields"]])

print (instruments_log, instruments_display)
for idx, instrument in enumerate(instruments_log):
    fig = None
    if instrument in instruments_display:
        colors = cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])
        # If it is the pressure
        if 'P00' in instrument:
            scale = 'log'
        else:
            scale = 'linear'
        heater_ax_created = False

        fig = figure(plot_width = 1200, 
    			   plot_height = 300, 	
    			   title = instrument,
    			   x_axis_label = 'Time', 
    			   y_axis_label = 'Value',
    			   x_axis_type='datetime',
             y_axis_type = scale)		

        for idx, i in enumerate(df.columns):
            if (instrument in i) and (i in config_display["fields"]):
                if ('T001_H' in i) or ('T002_H' in i):
                    if heater_ax_created == False:
                        # Setting the second y axis range name and range
                        fig.extra_y_ranges = {"heaters": Range1d(start=0, end=100)}
                        # Adding the second axis to the plot.  
                        fig.add_layout(LinearAxis(y_range_name="heaters"), 'right')
                        heater_ax_created = True

                    fig.line(x=df['Time'][-num_data:],y=df[i][-num_data:],legend=i,line_color=next(colors), y_range_name="heaters")                    

                elif (instrument in i) and (i in config_display["fields"]):	
                    fig.line(x=df['Time'][-num_data:],y=df[i][-num_data:],legend=i,line_color=next(colors))

 
    if fig != None:					
        fig.legend.location = "center_left"
        test.append(fig)

curdoc().title = "PYMONT Intranet Display"
curdoc().add_root(column(test))
#curdoc().add_root(column(test[:6]))

