'''
Created on 1 Dec 2012

@author: Jeremy
'''

import serial
import time
import sys

from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

import rt

# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
lcd = Adafruit_CharLCDPlate()

# Clear display and show greeting, pause 1 sec
lcd.clear()
lcd.message("Logger !!!")
lcd.backlight(lcd.ON)

s = None
s = file('../data/adaptronic-output.log','ab')
#s = serial.Serial("/dev/ttyUSB0",115200,timeout=5)
s = file('../data/dash-output.log','ab')
f = serial.Serial("/dev/ttyUSB0",115200,timeout=5)

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
        write_print_msg = '1k msgs in %.3f secs\n@ (%.3f mps)' % (d,c/d)
        print write_print_msg
        lcd.clear()
        lcd.message(write_print_msg)
        c = 0
        t = time.time()

def read_msg(header,length,msg,cs,variable_length):
    global c,t
    c += 1
    if c > 999:
        d = time.time() - t
        read_print_msg = '1k msgs in %.3f secs\n@ (%.3f mps)' % (d,c/d)
        print read_print_msg
        lcd.clear()
        lcd.message(read_print_msg)
        c = 0
        t = time.time()

#f = file('../data/F3.RUN','rb')
#rt.run(f, write_msg)
RT = rt.RaceTech(f)
#RT.run()
RT.run(write_msg)
lcd.backlight(lcd.OFF)
