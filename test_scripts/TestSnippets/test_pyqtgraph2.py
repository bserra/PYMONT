# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 08:53:40 2018

@author: irlab
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 14:47:33 2018

@author: bserra
"""

# Import libraries

from scipy import arange, pi, sin, cos, exp

import numpy as np
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import serial
from datetime import datetime
import sys
#from PyQt5.QtCore import QTimer


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value) for value in values]

#
class CustomWidget(pg.GraphicsWindow):
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    ptr1 = 0
    def __init__(self, parent=None, **kargs):
        pg.GraphicsWindow.__init__(self, **kargs)
        self.setParent(parent)
        self.setWindowTitle('pyqtgraph example: Scrolling Plots')
        p1 = self.addPlot(labels =  {'left':'Voltage', 'bottom':'Time'})
        self.data1 = np.random.normal(size=10)
        self.data2 = np.random.normal(size=10)
        self.curve1 = p1.plot(self.data1, pen=(3,3))
        self.curve2 = p1.plot(self.data2, pen=(2,3))

        timer = pg.QtCore.QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(2000) # number of seconds (every 1000) for next update

    def update(self):
        self.data1[:-1] = self.data1[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
        self.data1[-1] = np.random.normal()
        self.ptr1 += 1
        self.curve1.setData(self.data1)
        self.curve1.setPos(self.ptr1, 0)
        self.data2[:-1] = self.data2[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
        self.data2[-1] = np.random.normal()
        self.curve2.setData(self.data2)
        self.curve2.setPos(self.ptr1,0)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # Menu and close signal handling
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        
        self.main_widget = QtWidgets.QWidget(self)
        self.l = QtWidgets.QVBoxLayout(self.main_widget)
#        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.dc =  CustomWidget()
        self.l.addWidget(self.dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)



if __name__ == '__main__':
    qApp = QtWidgets.QApplication(sys.argv)
    progname ='testing'
    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())


"""

### MAIN PROGRAM #####    
# this is a brutal infinite loop calling your realtime data plot
        
app = QtGui.QApplication([])            # you MUST do this once (initialize things)
win = pg.GraphicsWindow(title="Signal from serial port") # creates a window

#timer = QTimer()
#timer.timeout.connect(update)
#timer.start(1000)
### END QtApp ####
pg.QtGui.QApplication.exec_() # you MUST put this at the end
##################

        
# Create object serial port
portName = "COM1"                      # replace this port name by yours!
baudrate = 9600
#ser = serial.Serial(portName,baudrate)

### START QtApp #####
app = QtGui.QApplication([])            # you MUST do this once (initialize things)
####################
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

date_axis = TimeAxisItem(orientation='bottom')


win = pg.GraphicsWindow(title="Signal from serial port") # creates a window
p = win.addPlot(title="Realtime plot",axisItems = {'bottom': date_axis})  # creates empty space for the plot in the window
                    # create an empty "plot" (a curve to plot)
print (p)

windowWidth = 500                       # width of the window displaying the curve
Xm = array([0])
dates = array([datetime.now().timestamp()])

curve1 = p.plot(dates, Xm, pen=(0,1))                        # create an empty "plot" (a curve to plot)
curve2 = p.plot(dates, Xm*2, pen=(1,2))    
#linspace(0,0,windowWidth)          # create array that will contain the relevant time series     
#ptr = -windowWidth                      # set first x position
ptr = 0

# Realtime data plot. Each time this function is called, the data display is updated
def update():
    global curve, ptr, Xm, dates   
#    Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    value = 1                # read line (single value) from the serial port
    Xm = append(Xm, float(value))                 # vector containing the instantaneous values      
    dates = append(dates, datetime.now().timestamp())

    print (datetime.fromtimestamp(datetime.now().timestamp()))
    ptr += 1                              # update x position for displaying the curve
    print (Xm, dates)
    curve1.setData(dates, Xm)                     # set the curve with this data
    curve2.setData(dates, 2*Xm)                     # set the curve with this data
#    curve1.setPos(datetime.now().timestamp(),0)                   # set x position in the graph to 0
#    curve2.setPos(datetime.now().timestamp(),0)                   # set x position in the graph to 0
    QtGui.QApplication.processEvents()    # you MUST process the plot now

### MAIN PROGRAM #####    
# this is a brutal infinite loop calling your realtime data plot
timer = QTimer()
timer.timeout.connect(update)
timer.start(1000)
### END QtApp ####
pg.QtGui.QApplication.exec_() # you MUST put this at the end
##################
"""