# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 09:30:53 2018

@author: bserra
"""
# IMPORTS
#########################



# METHODS
#########################




# MAIN
#########################
if __name__ == "__main__":
    print ('Processing...')
    
    status_f70 = {0:{
                     'pos':0,
                     'info':{True:'System On',
                             False:'System Off'}
                     },
                  1:{'pos':1,
                     'info':{True:'Motor Temperature alarm',
                       False:'no alarm'}},
                  2:{'pos':2,
                     'info':{True:'Phase Sequence/Fuse alarm',
                       False:'no alarm'}},
                  3:{'pos':3,
                    'info':{True:'Helium Temperature alarm',
                       False:'no alarm'}},                 
                  4:{'pos':4,
                     'info':{True:'Water Temperature alarm',
                       False:'no alarm'}},                 
                  5:{'pos':5,
                     'info':{True:'Water Flow alarm',
                       False:'no alarm'}},
                  6:{'pos':6,
                     'info':{True:'Oil Level alarm',
                       False:'no alarm'}},
                  7:{'pos':7,
                     'info':{True:'Pressure alarm',
                       False:'no alarm'}},
                  8:{'pos':8,
                     'info':{True:'Solenoid on',
                       False:'Solenoid off'}},
                  9:{'pos':slice(9,12),
                     'info':{0:'Local Off',
                     1:'Local On',
                     2:'Remote Off',
                     3:'Remote On',
                     4:'Cold Head Run',
                     5:'Cold Head Pause',
                     6:'Fault Off',
                     7:'Oil Fault Off'}},
                  10:{'pos':12,
                      'info':{True:'spare',
                              False:'spare'}},
                  11:{'pos':13,
                      'info':{True:'spare',
                              False:'spare'}},
                  12:{'pos':14,
                      'info':{True:'spare',
                              False:'spare'}},
                  13:{'pos':15,
                      'info':{True:'Configuration 1',
                        False:'Configuration 2'}}}
             
string_f70 = '0331'

test = ''.join(['{:4b}'.format(int(char)).replace(' ','0') for char in string_f70])
#test = '{:16b}'.format(int(string_f70)).replace(' ','0')[::-1]
print (test)              
test = ''.join(['{:4b}'.format(int(char)).replace(' ','0') for char in string_f70])[::-1]

for i in status_f70.keys():
#    print ('{:4b}'.format(binary(test[status_f70[i]['pos']])).replace(' ','0'))
#    print (int(test[status_f70[i]['pos']],2))
    print (status_f70[i]['info'][int(test[status_f70[i]['pos']],2)])  
    
# GARBAGE
#########################
