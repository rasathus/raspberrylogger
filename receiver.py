'''
Created on 1 Dec 2012

@author: Jeremy
'''

import serial
import sys
import rt
import time

s = serial.Serial(sys.argv[1],115200,timeout=15)
t = time.time()
c = 0

def decode(header,length,msg,cs,variable_length):
#    print header,length,msg,cs
    global c,t
    c += 1
    if c > 999:
        d = time.time() - t
        print 'Received %d messages in %.3f seconds (%.3f mps)' % (c,d,c/d)
        c = 0
        t = time.time()

RT = rt.RaceTech(s)
RT.run(decode)
