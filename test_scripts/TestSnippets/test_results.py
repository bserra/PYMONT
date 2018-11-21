# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 09:58:25 2018

@author: irlab
"""

import numpy as np

import datetime

import matplotlib.pyplot as plt
filename = 'C:/Users/irlab/Desktop/COOLDOWN_LOGS/2018-04-09_17-13-21.167906_2.txt'
#filename = 'C:/Users/irlab/Desktop/COOLDOWN_LOGS/2018-04-05_14-47-22.567101_2.txt'
a = np.genfromtxt(filename,skip_header=1,dtype="|U40")
print (a)

b= a[:,0]

b = [datetime.datetime.strptime(i,'%Y-%m-%d_%H-%M-%S.%f') for i in b]

test = [i.total_seconds() for i in np.diff(b)]

x_test = np.arange(np.size(test))

plt.plot(x_test,test)
plt.ylabel('dt [s]')
plt.xlabel('Measurement #')
plt.grid(True)
plt.show()