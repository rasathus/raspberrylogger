#!/usr/bin/env python
# - * - Coding: utf-8 - * -

# sudo python race-logger.py --input /home/pi/rivetracing/car/trunk/data/F3.RUN --output /home/pi/race_logs/output.tmp --use_display

import sys
import os
import time
import datetime
import serial
import logging
import Queue
import json
import logging
import argparse

from logging.handlers import RotatingFileHandler
from threading import Thread

import rt

from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

logging_path = "/home/pi/race_logs"
app_logger_path = "/home/pi/race_logger_app.log"
log_state = False

class IntelliBlit(Adafruit_CharLCDPlate):
    def __init__(self):
        self.last_message = None
        Adafruit_CharLCDPlate.__init__(self)

    def output(self, message):
        if message != self.last_message:
            self.clear()
            self.last_message = message
            self.message(message)
            print "======= Screen Write ======"
            print message
            print "====== End of Screen ======"


class ThreadedLogger:

    def __init__(self, log_path):
        if not os.path.exists(log_path):
            print "Logging path '{0}' does not exist".format(log_path)
        self.log_file_path = os.path.join(log_path, "{0}".format(datetime.datetime.now().strftime("%d%m%y-%H%M%S")))
        logger.info("Logging to log file : {0}".format(self.log_file_path))
        self.output_file = open(self.log_file_path,'w')
        self.log_queue = Queue.Queue()
        # use a running flag for out while loop
        self.run = True
        logger.debug("ThreadedLogger starting write listner.")
        self.log_writer_instance = Thread(target=self.log_writer)
        self.log_writer_instance.start()

    def log_writer(self):
        logger.debug("log_writer - writing ...")
        while self.run :
            if not self.log_queue.empty():
                message = self.log_queue.get()
                #logger.debug("log_writer - writing message : {0}".format(message))
                self.output_file.write("{0}\n".format(message))
                self.output_file.flush()
                #logger.debug("log_writer - returned from message write.")

    def append_to_log(self, message):
        self.log_queue.put(message)

    def shutdown(self):
        logger.debug("shutdown - shutdown started ...")
        logger.debug("shutdown - sending empty message ...")
        self.append_to_log("")
        logger.debug("shutdown - stopping listener ...")
        self.run = False
        logger.debug("shutdown - flushing ...")
        self.output_file.flush()
        logger.debug("shutdown - closing ...")
        self.serial_connection.close()
        logger.debug("shutdown - returned from close.")

status_message = ""

class DisplayHandler:

    # LCD SCREENS

    def passthrough_status(self):
        global status_message
        self.lcd.output(status_message)

    def logging_status(self):
        global log_state

        if log_state:
            self.progress_pos += 1
            if self.progress_pos > self.progress_max:
                self.progress_pos = 0
            self.lcd.output("Logging Status:\n{0}      {1}".format(log_state, self.progress_icon[self.progress_pos]))
        else:
            self.lcd.output("Logging Status:\n{0}".format(log_state))

    def page2(self):
        self.lcd.output("Render\npage2")

    def log_toggle(self):
        global log_state

        if log_state:
            log_state = False
            # stop the file logger
        else:
            log_state = True
            # start the file logger

    # END OF LCD SCREENS

    def __init__(self):
        logger.debug("Initialising DisplayHandler")
        self.lcd = IntelliBlit()
        self.lcd.begin(16, 2)
        self.lcd.backlight(self.lcd.ON)
        self.lcd.clear()
        self.btn = [self.lcd.SELECT, self.lcd.UP, self.lcd.DOWN]

        self.current_page = 0
        # Map of pages to functions
        self.page_map = {0: self.passthrough_status,
                        1: self.logging_status,
                        2: self.page2}

        self.progress_icon = ['|','/','-','\\']
        self.progress_pos = 0
        self.progress_max = 3

        #self.render_int_counter = 0
        #self.render_int = 5

        # use a running flag for out while loop
        self.run = True
        logger.debug("DisplayHandler starting display thread.")
        self.display_instance = Thread(target=self.display_loop)
        self.display_instance.start()

    def display_loop(self):
        while self.run :
            for b in self.btn:
                if self.lcd.buttonPressed(b):
                    if b == self.lcd.SELECT:
                        self.log_toggle()
                    elif b == self.lcd.UP:
                        self.current_page += 1
                        if self.current_page > len(self.page_map)-1:
                            self.current_page = 0
                    elif b == self.lcd.DOWN:
                        self.current_page -= 1
                        if self.current_page < 0:
                            self.current_page = len(self.page_map)-1
                    else:
                        # unregistered button
                        pass

            self.page_map[self.current_page]()

            # render_int_counter += 1
            # # dont want to render on every tick, but want to respond to button input
            # if render_int <= render_int_counter:
            #     lcd.clear()
            #     # render the current page
            #     page_map[current_page]()
            #     render_int_counter = 0

            time.sleep(0.25)

    def shutdown(self):
        logger.debug("shutdown - shutdown started ...")
        logger.debug("shutdown - stopping display ...")
        self.run = False
        self.lcd.clear()
        self.lcd.backlight(lcd.OFF)


if __name__ == "__main__":
    logger = logging.getLogger('race-logger')
    hdlr = logging.FileHandler(app_logger_path)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--input", dest='input', help="path to the input file/device")
    parser.add_argument("--output", dest='output', help="path to the output file/device")
    parser.add_argument('--use_display', dest='use_display', action='store_true', default=False, help='use an attached Adafruit display')
    args = parser.parse_args()

    #try:

    logger.debug("main - instantiating ThreadedLogger.")
    threaded_logger = ThreadedLogger(logging_path)
    if args.use_display:
        logger.debug("main - instantiating DisplayHandler.")
        display_handler = DisplayHandler()

    #input_device = file('../data/F3.RUN','rb')
    #output_device = file(os.path.join(logging_path, 'output_log.tmp'),'w')
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

    t = time.time()
    c = 0

    def message_processor(header,length,msg,cs,variable_length):
        global log_state, c, t, status_message
    #    print header,length,msg,cs
        out_bytes = chr(header)
        if variable_length:
            out_bytes += chr(length)
        for b in msg:
            out_bytes += chr(b)
        out_bytes += chr(cs)
        if log_state:
            threaded_logger.append_to_log(out_bytes)
        output_device.write(out_bytes)

        c += 1
        if c > 999:
            d = time.time() - t
            status_message = '1k msgs in %.3f secs\n@ (%.3f mps)' % (d,c/d)
            c = 0
            t = time.time()


    RT = rt.RaceTech(input_device)
    RT.run(message_processor)

    logger.info("Shutting down ...")
    threaded_logger.shutdown()
    if args.use_display:
        display_handler.shutdown()


    # except KeyboardInterrupt:
    #     logger.info("Got signal KeyboardInterrupt")
    #     pass
    #
    # except:
    #     logger.exception()
    #
    # finally:
    #     logger.info("Shutting down ...")
    #     threaded_logger.shutdown()
    #     display_handler.shutdown()
