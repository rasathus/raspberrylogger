import sys
sys.path.append('/home/pi/py/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate')
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

import serial
import subprocess
import time

def checksum(cmd):
    calc_cksum = 0
    for s in cmd:
        calc_cksum ^= ord(s)
    return '$'+cmd+'*'+hex(calc_cksum)[2:]

def get_addr(interface):
    try:
        s = subprocess.check_output(["ip","addr","show",interface])
        return s.split('\n')[2].strip().split(' ')[1].split('/')[0]
    except:
        return '?.?.?.?'

def write_ip_addresses():
    lcd.clear()
    lcd.home()
    lcd.message('e'+get_addr('eth0').rjust(15)+'w'+get_addr('wlan0').rjust(15))

def send_and_get_ack(ser,cmdno,cmdstr):
    #Send the cmd and wait for the ack
    #$PMTK001,604,3*32
    #PMTK001,Cmd,Flag 
    #Cmd: The command / packet type the acknowledge responds. 
    #Flag: .0. = Invalid command / packet. 
    #.1. = Unsupported command / packet type 
    #.2. = Valid command / packet, but action failed 
    #.3. = Valid command / packet, and action succeeded 
    cmd = 'PMTK%s%s' % (cmdno,cmdstr)
    msg = checksum(cmd)+chr(13)+chr(10)
    print '>>>%s' % cmd
    ser.write(msg)
    ack = False
    timeout = 300
    while (not ack) and timeout > 0:
        line = str(ser.readline())
        if line.startswith('$PMTK001'):
            tokens = line.split(',')
            ack = tokens[2][0] == '3'
            print '<<<%s success=%s' % (line,ack)
        timeout -= 1
    return ack
    

lcd = Adafruit_CharLCDPlate()

# Connect to GPS at default 9600 baud
gps = serial.Serial('/dev/ttyAMA0',9600,timeout=0.01)
# Switch GPS to faster baud
send_and_get_ack(gps,'251',',38400')
# Assume success - close and re-open serial port at new speed
gps.close()
gps = serial.Serial('/dev/ttyAMA0',38400,timeout=0.01)

# Set GPS into RMC and GGA only mode
send_and_get_ack(gps,'314',',0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set GPS into 10Hz mode
send_and_get_ack(gps,'220',',100')

# Recording
recording = 's'
rec_file = None

# Throw away first few key presses after waiting for the screen to start up
#time.sleep(4)
#lcd.read(16)

LCD_UPDATE_DELAY = 5

height = '0'
old_time_stamp = 'old'
lcd_update = 0
page = 0

time_stamp = ''
active = False
lat = None
lat_dir = None
lon = None
lon_dir = None
speed = None
heading = None
date = ''

# Start main loop
while True:
    #Read the 3 axis accelerometer
    #x = mcp3008.readadc(0)
    #y = mcp3008.readadc(1)
    #z = mcp3008.readadc(2)
    x = 500
    y = 500
    z = 500
    accX = (x-504)/102.0
    accY = (y-507)/105.0
    accZ = (z-515)/102.0
    #print x,accX,y,accY,z,accZ
    #time.sleep(1)

    #Read the GPS
    line = str(gps.readline())
#    print line
    # $GPRMC,105215.000,A,5128.5775,N,00058.5070,W,0.12,103.43,211012,,,A*78
    # 1 = Time
    # 2 = (A)ctive or (V)oid
    # 3 = Latitude
    # 5 = Longitude
    # 7 = Speed in knots
    # 8 = Compass heading
    # 9 = Date
    #Divide minutes by 60 and add to degrees. West and South = negative
    #Multiply knots my 1.15078 to get mph.

    # $GPGGA,210612.300,5128.5791,N,00058.5165,W,1,8,1.18,41.9,M,47.3,M,,*79
    # 9 = Height in metres
    if line.startswith('$GPGGA'):
        tokens = line.split(',')
        if len(tokens) < 15:
            continue
        try:
            height = tokens[9]
        except ValueError as e:
            print e    
    elif line.startswith('$GPRMC'):
        tokens = line.split(',')
        if len(tokens) < 10:
            continue
        try:
            time_stamp = tokens[1]
            active = tokens[2] == 'A'
            lat = tokens[3]
            lat_dir = tokens[4]
            lon = tokens[5]
            lon_dir = tokens[6]
            speed = tokens[7]
            heading = tokens[8]
            date = tokens[9]
            if active:
                lat = float(lat[:2]) + float(lat[2:])/60.0
                if lat_dir == 'S':
                    lat = -lat
                lon = float(lon[:3]) + float(lon[3:])/60.0
                if lon_dir == 'W':
                    lon = -lon
                speed = float(speed) * 1.15078
        except ValueError as e:
            print e
            
    #Update LCD  
    if time_stamp != old_time_stamp:      
        lcd_update += 1
        if lcd_update > LCD_UPDATE_DELAY:
            lcd_update = 0
            lcd.clear()
            lcd.home()
            
            if not active and (page == 0 or page == 1):
                lcd.backlight(lcd.RED)
                lcd.message('NO FIX: '+date+' '+recording+"\n"+time_stamp.ljust(16))
            elif page == 0:
                lcd.backlight(lcd.GREEN)
                lcd.message(('%.8f' % lat).rjust(14)+" "+recording+"\n"+('%.8f' % lon).rjust(14)+"  ")
            elif page == 1:
                #0.069 223.03 48.9 -0.010 0.010 0.980
                lcd.message('{: .3f}{:>9} '.format(speed,height))
                lcd.message('{: .2f}{: .2f}{: .2f}'.format(accX,accY,accZ))
        
        #Record to file if time_stamp has changed
        if recording == 'r' and time_stamp != old_time_stamp:
            rec_file.write('%s %s %.8f %.8f %.3f %s %s %.3f %.3f %.3f\n' % (date,time_stamp,lat,lon,speed,heading,height,accX,accY,accZ))

        old_time_stamp = time_stamp

    #Read keypad        
#    key = str(lcd.read(1))
    key = ''
    if key != '' and key in 'abcd':
        lcd_update = LCD_UPDATE_DELAY
        if key == 'c':
            if recording == 's':
                recording = 'r'
                rec_file = open("/home/pi/gps-"+date+time_stamp+".log", "a")
            else:
                recording = 's'
                rec_file.close()
        elif key == 'a':
            page += 1
            if page > 2:
                page = 0
            elif page == 2:
                write_ip_addresses()
