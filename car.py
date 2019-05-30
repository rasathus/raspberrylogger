'''
Created on 3 Jun 2013

@author: Jeremy
'''

import serial
import sys
import rt

def make_io(path,mode):
    if path.startswith('file:'):
        return file(path[5:],mode)
    else:
        return serial.Serial(path,115200,timeout=15)

ecu = make_io(sys.argv[1],'rb')
dash = make_io(sys.argv[2],'ab')

#ecu = serial.Serial(sys.argv[1],115200,timeout=15)
#dash = serial.Serial(sys.argv[2],115200,timeout=15)


#57600

#log = open(sys.argv[3], "a")

def write_to_dash(header,length,msg,cs,variable_length,decode_function,name):
#    print header,length,msg,cs
#    print name, decode_function(msg)
    out_bytes = chr(header)
    if variable_length:
        out_bytes += chr(length)
    for b in msg:
        out_bytes += chr(b)
    out_bytes += chr(cs)
    dash.write(out_bytes)

RT = rt.RaceTech(ecu)
RT.run(write_to_dash)
