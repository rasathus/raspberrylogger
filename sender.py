'''
Created on 1 Dec 2012

@author: Jeremy
'''

import serial
import time
import sys
import rt

s = None
#s = serial.Serial(sys.argv[1],115200,timeout=5)
t = time.time()
c = 0

def write_msg(header,length,msg,cs,variable_length):
#    print header,length,msg,cs
    out_bytes = chr(header)
    if variable_length:
        out_bytes += chr(length)
    for b in msg:
        out_bytes += chr(b)
    out_bytes += chr(cs)
    s.write(out_bytes)
    global c,t
    c += 1
    if c > 999:
        d = time.time() - t
        print 'Sent %d messages in %.3f seconds (%.3f mps)' % (c,d,c/d)
        c = 0
        t = time.time()

def read_msg(header,length,msg,cs,variable_length):
    global c,t
    c += 1
    if c > 999:
        d = time.time() - t
        print 'Sent %d messages in %.3f seconds (%.3f mps)' % (c,d,c/d)
        c = 0
        t = time.time()

f = file('../data/F3.RUN','rb')
#rt.run(f, write_msg)
RT = rt.RaceTech(f)
RT.run()
