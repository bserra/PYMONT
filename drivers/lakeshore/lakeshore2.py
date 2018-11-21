"""This module contains drivers for the following equipment from LakeShore cryotonics

* LakeShore Model 336 Temperature Controller

Use of ethernet connection
"""

import visa
import json
import sys
import drivers.lakeshore.pyvisa_connect as pyvisa

# Code translations constants
INPUT_NAMES = {
    0: 'A',
    1: 'B',
    2: 'C',
    3: 'D',
    4: 'D2',
    5: 'D3',
    6: 'D4',
    7: 'D5'
}

# METHODS 
#########################

#### LAKESHORE 34x ############################################################

class LakeShore34x(object):
    r"""Abstract class that implements the common driver for the model 3xx 
    temperature controllers. The driver implement the following 7 commands out 
    the 97 in the specification:

    * *IDN?: Identification query (model identification)
    * KRDG?: Kelvin reading query
    * INCRV?: Input curve query
    * INNAME?: Sensor input name query
    * HTR?: Heater output query
    * HTRSET?: Heater setup query
    * SETP?: Control setpoint query

    """

    def __init__(self, 
                 RESOURCE_STRING, 
                 RESOURCE_MANAGER = None,
                 RESOURCE_ID = '',
                 RESOURCE_TIMEOUT = 1000,
                 TERMINATION_STRING = '\r\n',
                 **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the Lakeshore
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\r\n' by default for Lakeshore
        :type TERMINATION_STRING: str
        """

        self.instrument, 
        self.inst_id, 
        self.connected = pyvisa.connect(RESOURCE_STRING, 
                                         RESOURCE_MANAGER = None,
                                         RESOURCE_ID = '',
                                         TERMINATION_STRING = '\n',
                                         RESOURCE_TIMEOUT = 5,
                                         **kwargs)

    def identify(self):
        """"""
        return self.query('*IDN?')
        
    def temperature_probes(self):
        """"""
        results = dict()
        for idx, i in enumerate(self.inputs):
            results[self.inst_id+'Input '+i]= (self.instrument.query('KRDG? '+str(idx)), '[K] Temperature '+str(idx))
        return results

    def power_heaters(self):
        """"""
#        results = dict()
        results = {self.inst_id+'H1':(self.instrument.query('HTR? 1'), '[%] Heater output 1'),
                   self.inst_id+'H2':(self.instrument.query('HTR? 2'), '[%] Heater output 2')}
        return results

    def setpoints(self):
        """"""
        results = {self.inst_id+'SETP1':(self.instrument.query('SETP? 1'), '[K] Setpoint loop 1'),
                   self.inst_id+'SETP2':(self.instrument.query('SETP? 2'), '[K] Setpoint loop 2')}
        return results     
    
    def dump_sensors(self):
        """"""
        results = {**self.power_heaters(), 
                **self.temperature_probes(),
                **self.setpoints()}

        return results
        
    def curves(self):
        """"""
        reply = self.instrument.query('INCRV? D')
        return reply

#### LAKESHORE 33x ############################################################

class LakeShore33x(object):
    r"""Abstract class that implements the common driver for the model 3xx 
    temperature controllers. The driver implement the following 7 commands out 
    the 97 in the specification:

    * *IDN?: Identification query (model identification)
    * KRDG?: Kelvin reading query
    * INCRV?: Input curve query
    * INNAME?: Sensor input name query
    * HTR?: Heater output query
    * HTRSET?: Heater setup query
    * SETP?: Control setpoint query

    """

    def __init__(self, **kwargs):
        
        """Initialize internal variables and ethernet connection

        :param RESOURCE_STRING: The adress of the Lakeshore
        :type RESOURCE_STRING: str
        :param TERMINATION_STRING: '\r\n' by default for Lakeshore
        :type TERMINATION_STRING: str
        """
        
        dict_conn = kwargs.update({'TERMINATION_STRING':'\r\n'})
        print (kwargs)
        test = pyvisa.connector(kwargs)
        self.instrument, self.inst_id, self.connected = test.connect()
        
    def identify(self):
        """"""
        return self.query('*IDN?')
        
    def temperature_probes(self):
        """"""
        results = dict()
        T_K = [self.instrument.query('KRDG? '+i) for i in self.inputs]
        for idx, i in enumerate(self.inputs):
            results[self.inst_id+self.instrument.query('INNAME? '+i).strip()]=(T_K[idx], '[K] Temperature '+self.instrument.query('INNAME? '+i).strip())
        return results

    def power_heaters(self):
        """"""
#        results = dict()
        results = {self.inst_id+'H1':(self.instrument.query('HTR? 1'), '[%] Heater output 1'),
                   self.inst_id+'H2':(self.instrument.query('HTR? 2'), '[%] Heater output 2')}
        return results

    def setpoints(self):
        """"""
        results = {self.inst_id+'SETP1':(self.instrument.query('SETP? 1'), '[K] Setpoint loop 1'),
                   self.inst_id+'SETP2':(self.instrument.query('SETP? 2'), '[K] Setpoint loop 2')}
        return results        
    
    def dump_sensors(self):
        """"""
        results = {**self.power_heaters(), 
                **self.temperature_probes(),
                **self.setpoints()}

        return results
        
    def curves(self):
        """"""
        reply = self.instrument.query('INCRV? D')
        return reply