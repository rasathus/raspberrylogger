'''
Created on 3 Jun 2013

@author: Jeremy
'''

import serial
import sys
import argparse

import rt

parser = argparse.ArgumentParser(description='A simple sender for racetech')
parser.add_argument("--input", dest='input', help="path to the input file/device")
parser.add_argument("--output", dest='output', help="path to the output file/device")
args = parser.parse_args()

if args.input.startswith("/dev/"):
    # using a serial device
    input_device = serial.Serial(args.input, 57600, timeout=5)
else:
    # treat as file input
    input_device = file(args.input, 'rb')

if args.output.startswith("/dev/"):
    # using a serial device
    output_device = serial.Serial(args.output, 57600, timeout=5)
else:
    # treat as file output
    output_device = file(args.output, 'w')

def write_to_device(header,length,msg,cs,variable_length):
    out_bytes = chr(header)
    if variable_length:
        out_bytes += chr(length)
    for b in msg:
        out_bytes += chr(b)
    out_bytes += chr(cs)
    output_device.write(out_bytes)

RT = rt.RaceTech(input_device)
RT.run(write_to_device)
