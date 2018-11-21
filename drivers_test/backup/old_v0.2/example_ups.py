# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 10:42:57 2018

@author: bserra
"""
import time
UPS = UPSVSD3xxx()
#UPS.status()

#UPS.shutdown()
#a = UPS.serial.write(b'\x0201CS040000021B\x03')
UPS.identify()
UPS.status()
UPS.restart()
time.sleep(20)
UPS.shutdown()
UPS.close()

