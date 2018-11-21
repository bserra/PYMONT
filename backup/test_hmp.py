# -*- coding: utf-8 -*-
"""
Created on Fri May  4 11:05:06 2018

@author: irlab
"""

import time
import roheandschwarze as rs

test = rs.HMP4040(port='COM6')


for i in range(1000):
    print (test.fetch())

test.close()
