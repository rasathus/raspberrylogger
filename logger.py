











#!/usr/bin/env python
# - * - Coding: utf-8 - * -

import time
import serial
import logging
import Queue
from threading import Thread
import json

import logging
from logging.handlers import FileHandler





input_device = None
output_devices = []











# Assign Arduino's serial comms path
comms_port = '/dev/ttyACM0'


# create console handler and set level to debug, with auto log rotate max size 10mb keeping 10 logs.
file_handler = FileHandler( 'logger.log')

# create formatter
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
# add formatter to our console handler
file_handler.setFormatter(log_formatter)

# example code for various logging levels
#app.logger.debug("debug message")
#app.logger.info("info message")
#app.logger.warn("warn message")
#app.logger.error("error message")
#app.logger.critical("critical message")
#app.logger.exception("exception message followed by trace")

file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)


class Serial_Communicator:

    def __init__(self):
        # Set up serial baud rate
        self.serial_connection = serial.Serial (comms_port, 57600 , timeout = 1 )
        self.send_queue = Queue.Queue()
        self.receive_queue = Queue.Queue()
        # use a running flag for out while loop
        self.run = True
        app.logger.debug("Serial_Communicator starting receive listner.")
        self.receive_listner_instance = Thread(target=self.receive_listner)
        self.receive_listner_instance.start()
        app.logger.debug("Serial_Communicator starting send listner.")
        self.send_listner_instance = Thread(target=self.send_listner)
        self.send_listner_instance.start()
        app.logger.debug("Serial_Communicator starting keepalive sentinel.")
        self.keepalive_sentinel_instance = Thread(target=self.keepalive_sentinel)
        self.keepalive_sentinel_instance.start()
        app.logger.debug("Serial_Communicator init complete.")

    def receive_listner(self):
        app.logger.debug("receive_listner - listening ...")
        while self.run :
            read_line = None
            read_line = self.serial_connection.readline()
            self.receive_queue.put(read_line)
            app.logger.debug("receive_listner - '%s'" % read_line)

    def send_listner(self):
        app.logger.debug("send_listner - listening ...")
        while self.run :
            if not self.send_queue.empty():
                message = self.send_queue.get()
                app.logger.debug("send_message - writing message : %s" % message)
                self.serial_connection.write("%s\n" % message)
                self.serial_connection.flush()
                app.logger.debug("send_message - returned from message write.")

    def keepalive_sentinel(self):
        while self.run :
            self.send_queue.put("KA0000")
            time.sleep(1)

    def send_message(self, message):
        self.send_queue.put(message)

    def shutdown(self):
        app.logger.debug("shutdown - shutdown started ...")
        app.logger.debug("shutdown - sending KI1100 message ...")
        self.send_message("KI1100")
        app.logger.debug("shutdown - stopping listener ...")
        self.run = False
        app.logger.debug("shutdown - flushing ...")
        self.serial_connection.flush()
        app.logger.debug("shutdown - closing ...")
        self.serial_connection.close()
        app.logger.debug("shutdown - returned from close.")


app.logger.debug("main - instantiating Serial_Communicator.")
serial_communicator = Serial_Communicator()

@app.route('/')
def index():
    #serial_communicator.send_message("LT0100")
    #serial_communicator.send_message("RT1100")
    #time.sleep(5)
    #serial_communicator.send_message("LT0000")
    #serial_communicator.send_message("RT0000")
    #time.sleep(1)
    #serial_communicator.send_message("LT1100")
    #serial_communicator.send_message("RT0100")
    #time.sleep(5)
    #serial_communicator.send_message("KI1100")
    return render_template('index.html')

@app.route('/send_command/<command>')
def send_command(command):
    app.logger.info("got command [%s]" % command)
    # Do some basic checks to ensure command string is valid.
    return_object = {'output' : None , 'error' : None, 'success' : False}
    app.logger.info("Is this the first two digits ? %s" % command[0:2])
    command_string = command[0:2]

    try:
        # Check we've been given a valid integer
        int(command[2])
        command_string = "%s%s" % (command_string,command[2])
    except ValueError:
        return_object['error'] = "Direction element of non integer value : %s" % command[2]

    try:
        # Check we've been given a valid integer
        if int(command[3:6]) <= 255 :
            command_string = "%s%s" % (command_string,command[3:6])
        else:
            return_object['error'] = "Power element value greater than 255 : %s" % command[3:6]
    except ValueError:
        return_object['error'] = "Power element of non integer value : %s" % command[3:6]

    if not return_object['error']:
        serial_communicator.send_message(command_string)
        return_object['output'] = command_string
        return_object['success'] = True
        app.logger.info('sending command [%s]' % command_string)
    else:
        app.logger.error(return_object['error'])

    return json.dumps(return_object)

if __name__ == '__main__':
    app.logger.debug("main - sending serial messages.")
    app.run(host='0.0.0.0', port=8082, use_reloader=False)
    app.logger.debug("main - sending shutdown.")
    serial_communicator.shutdown()










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
