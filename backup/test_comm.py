# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 16:40:04 2018

@author: irlab
"""

import monitor_crisle_v2 as mc

if __name__ == '__main__':
    try:
        monitoring = mc.monitor()
        monitoring.start()
    except KeyboardInterrupt:
        monitoring.cleanup()