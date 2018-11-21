# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 09:07:37 2018

@author: bserra
"""
# IMPORTS
#########################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams
import datetime as dt
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Bitstream Vera Sans', 'Computer Modern Sans Serif', 'Lucida Grande', 'Verdana', 'Geneva', 'Lucid', 'Arial', 'Helvetica', 'Avant Garde', 'sans-serif']
rcParams['font.serif'] = ['DejaVu Serif', 'Bitstream Vera Serif', 'Computer Modern Roman', 'New Century Schoolbook', 'Century Schoolbook L', 'Utopia', 'ITC Bookman', 'Bookman', 'Nimbus Roman No9 L', 'Times New Roman', 'Times', 'Palatino', 'Charter', 'serif']
#rcParams["font.size"] = "40"
import glob

#rcParams['figure.figsize'] = 20,20
#rcParams['font.size'] = 16
files = glob.glob('*.txt')

print (files)

# METHODS
#########################
def dict_plot(input_name):
    ''''''
    colors_dict = dict(A='#00ff00',
                       B='black',
                       C='#ffc800',
                       D='magenta',
                       D2='cyan',
                       D3='grey',
                       D4='#ffafaf',
                       D5='purple',
                       H1='blue',
                       H2='red')

    return dict(label=input_name,color=colors_dict[input_name.split(' ')[-1]])

def onclick(event):
    dates_vector = event.inaxes.lines[0].get_data()[0]
    test = mdates.num2date(event.xdata).replace(tzinfo=None)
    closestdate_cursor = min(dates_vector, key=lambda d: abs(d - test))
    print('Closest data point:',closestdate_cursor)
    for line in event.inaxes.lines:
        if '_line' not in line.get_label():
            print(line.get_label(), np.array(line.get_ydata())[np.where(dates_vector==closestdate_cursor)][0])
#    print(event.inaxes.lines[0].get_data())
#    print('%s click: button=%d, x=%d, y=%d, xdata=%s, ydata=%f' %
#          ('double' if event.dblclick else 'single', event.button,
#           event.x, event.y, mdates.num2date(event.xdata), event.ydata))


# MAIN
#########################
if __name__ == "__main__":

    fig = plt.figure(figsize = (15,10))
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    
    ax1 = fig.add_subplot(1,2,1)
    #ax1b = ax1.twinx()
    ax2 = fig.add_subplot(1,2,2, sharex = ax1)
    axes = [ax1, ax2]
    color = ['blue', 'green']
    ls = ['-','--']
    label = ['2018-11-16: Problem heat exchanger',
             '2018-11-21: New pump and clean heat exchanger']
    for idx, file in enumerate(files[::-1]):
        print (file)
        txt = pd.read_csv(file,sep='\t', dtype={'Time': object},header=0,comment='#')
        data = txt[txt['Comments'].notna()]
        df = txt
 
        df = df.sort_values(by=['Time'])    
        df2 = df[df['Comments'].notna()]
        df = df[df['Comments'].isna()]
			
        df['Time'] = pd.to_datetime(df.Time, format='%Y-%m-%d_%H-%M-%S')
        df2['Time'] = pd.to_datetime(df2.Time, format='%Y-%m-%d_%H-%M-%S')
		

		
		# Plot
		#############################
		## Plot all temperatures
        for i in df.columns:
            if (i != 'Time') and ('Reading' not in i):
                if ('C001_temp2' in i): 
                    axes[idx].plot(np.arange(len(df[i]))*5/3600., df[i],color = 'blue', ls='-',label= 'Water outlet')                
                elif ('C001_temp3' in i):
                    axes[idx].plot(np.arange(len(df[i]))*5/3600., df[i],color = 'green', ls='-', label = 'Water inlet')

        axes[idx].set_title(label[idx],fontsize=14)       
        #ax1.set_ylim(0,300)            
        #ax2.set_ylim(1e-8,1e4)            
        ax1.set_ylabel('Temperature [Celsius]')
        #ax2.set_ylabel('Pressure [mbar]')
        ax1.set_xlabel('Time since compressor turned on [h]')
        ax2.set_xlabel('Time since compressor turned on [h]')
        ax1.set_ylim((10,65))
        ax2.set_ylim((10,65))
        #ax2.semilogy()
		
		# Add notes from the comments in the file
		#for idx, note in df2.iterrows():
		#    ax1.axvline(x=note['Time'],ls='--',color='grey')
		#    ax1.text(note['Time'],290,idx,rotation=45, horizontalalignment='right',verticalalignment='top')
		#    print (idx, note['Comments']) 
		
		# Add manual notes date format YYYY-MM-DD HH:MM:SS
        notes = np.array([['2018-06-26 13:56:29','A'],
						  ['2018-06-26 14:00:09','B'],
						  ['2018-06-26 14:02:39','C']])
		
		#for idx, note in enumerate(notes):
		#    ax2.axvline(x=note[0],ls='--',color='grey')
		#    ax2.text(note[0],1e3,idx,rotation=45, horizontalalignment='right',verticalalignment='top')
		#    print (idx, note[1]) 
		
		
		## Others
		# If heater data is displayed
		#[ax.grid(True) for ax in fig.get_axes() if ax is not ax1b]
    [ax.grid(True) for ax in fig.get_axes()]
    ax2.legend(fontsize=14)
    #[ax.legend(fontsize=16) for ax in fig.get_axes()]
	#plt.gcf().autofmt_xdate()
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95,hspace=0.05,bottom=0.1)
    plt.tight_layout()
    plt.show()

# GARBAGE
#########################
