# -*- coding: utf-8 -*-
"""An example of how to use the lakeshore driver with python 3.6

"""

# Import the library
import lakeshore as ls

# Define the IP address as well as the port
# Address defined in the ethernet configuration of the Lakeshore
IPv4_address = '192.168.5.1'
# Default port for comm is 7777
port = 7777

# Connect to the lakeshore
ls_comm = ls.LakeShore33x(TCP_IP=IPv4_address, TCP_PORT=port)

# use _send_command to send whatever you want (no security, so be careful)
# reply contains the string send back by the lakeshore
reply = ls._send_command('KRDG? A')
print (reply)

# some commands can be used to have a more 'detailed' response

# temperature probes will get all temperatures from the inputs defined in the 
# instrumentation_config.json, will also have the names of the inputs.
# reply contains a dictionnary with everything
reply = ls.temperature_probes()
print (reply)

# Same with power_heaters and setpoints
reply = ls.power_heaters()
print (reply)

reply = ls.setpoints()
print (reply)

# And then you close the connection when finished
ls.close()

