'''
Created on 1 Dec 2012

@author: Jeremy
'''

TICKPERIOD = 1.66666666666667e-07
PI = 3.141592654


def decode(msg):
	print msg
	raise Exception('STOP')
	return msg	

def decode_raw(msg):
	return msg	

def decode_u16(msg):
	'''Decode the 2 input msg to an unsigned 16 bit integer'''
	return (msg[0] << 8) + msg[1] 

def decode_u24(msg):
	'''Decode the 3 input msg to an unsigned 24 bit integer'''
	return ( (msg[0] << 16) + (msg[1] << 8) + msg[2] )	

def decode_u32(msg):
	'''Decode the 4 input msg to an unsigned 32 bit integer'''
	return (msg[0] << 24) + (msg[1] << 16) + (msg[2] << 8) + msg[3]	

def decode_i32(msg):
	'''Decode the 4 input msg to a signed 32 bit integer'''
	i = ((msg[0] & 0x7F) << 24) + (msg[1] << 16) + (msg[2] << 8) + msg[3]	
	if msg[0] & 0x80 == 0x80:
		i = -(1<<31) +i
	return i

def decode_boolean(msg):
	'''Decode the first byte in the list as a boolean. 1 = True'''
	return msg[0] == 1

def decode_twos_comp(byte):
	if byte & 0x80 == 0x80:
		# negative so invert, add one and sign
		return -((byte^0xFF)+1)
	else:
		return byte

def decode_logger_storage(msg):
	'''(6) Decode logger storage. Return a tuple (Serial number, Software version, Bootload version).'''
	return (decode_u16(msg), msg[2], msg[3])

def decode_accelerations(msg):
	'''(8) Decode accelerations. Return a tuple (Lateral acceleration g, Longitudinal acceleration g).
	Longitudinal is positive for acceleration, negative for braking.
	Lateral is positive for cornering around a RH bend, negative for cornering around a LH bend.'''
	lat = (msg[0] & 0x7F) + (msg[1] / 256.0)
	if msg[0] & 0x80 != 0x80:
		lat = -lat

	lon = (msg[2] & 0x7F) + (msg[3] / 256.0)
	if msg[2] & 0x80 != 0x80:
		lon = -lon
	
	return (lat,lon)
		
def decode_timestamp(msg):
	'''(9) Decode timestamp. Return seconds'''
	return decode_u24(msg) / 100.0

def decode_gps_positional_data(msg):
	'''(10) Decode the GPS positional data. Return a tuple (Latitude dg, Longitude dg, Accuracy mm).'''
	#print '{:.8f},{:.8f},'.format(decode_i32(msg[4:8])*0.0000001, decode_i32(msg[0:4])*0.0000001)
	return (decode_i32(msg[4:8])*0.0000001, decode_i32(msg[0:4])*0.0000001, decode_u32(msg[8:12]))

def decode_gps_speed_data(msg):
	'''(11) Decode GPS speed data. Return a tuple (Speed m/s, Source, Speed Accuracy m/s).'''
	return (decode_u32(msg[0:4])*0.01, msg[4], decode_u24(msg[5:8])*0.01)

def decode_frequency(msg):
	'''(14-18) Decode frequency. Return frequency'''
	freq = decode_u24(msg) * TICKPERIOD
	if freq > 0:
		freq = 1 / freq
	return freq

def decode_analogue(msg):
	'''(20-51) Decode analogue. Return voltage'''
	return decode_u16(msg) / 1000.0

def decode_date_storage(msg):
	'''(55) Decode date storage. Return Current GMT time tuple (Seconds, Minutes, Hours, Date, Month, Year, Offset from GMT)
	Offset from GMT is given by 15 minutes increments or decrements
	For example (-22) = (- 5:30 GMT)'''
	return (msg[0], msg[1], msg[2], msg[3], msg[4], decode_u16(msg[5:7]), decode_twos_comp(msg[7]))

def decode_gps_course_data(msg):
	'''(56) Decode GPS Course data. Return tuple (Heading, Heading accuracy).'''
	heading = decode_i32(msg[0:4]) * 0.00001 / 180 * PI; # convert from ublox units to rads
	headacc = decode_u32(msg[4:8]) * 0.00001 / 180 * PI; # convert from ublox units to rads
	return (heading, headacc)

def decode_gps_altitude(msg):
	'''(57) Decode GPS Altitude and Altitude Accuracy. Return tuple (Altitude mm, Accuracy mm).'''
	return (decode_i32(msg[0:4]), decode_i32(msg[4:8]))

message_table = {
	1:(9,"Run Information",decode_raw), # race tech reserved
	2:(11,"Run start/stop info",decode),
	3:(255,"Raw GPS Data Input",decode), # the message has variable length --- length is given by second byte of the message
	4:(7,"New Sector Time",decode),
	5:(21,"New Lap Marker",decode),
	6:(6,"Logger Storage Channel",decode_logger_storage),
	7:(6,"GPS Time Storage Channel",decode_u32), #GPS ms time of week. Time of week is reset to zero at midnight between Saturday and Sunday
	8:(6,"Accelerations",decode_accelerations),
	9:(5,"Time Stamp",decode_timestamp),
	10:(14,"GPS Positional Data",decode_gps_positional_data),
	11:(10,"GPS Raw Speed Data",decode_gps_speed_data),
	12:(3,"Beacon Pulse Present",decode_boolean),
	13:(3,"GPS pulse present",decode_boolean),
	14:(5,"Frequency 1",decode_frequency),
	15:(5,"Frequency 2",decode_frequency),
	16:(5,"Frequency 3",decode_frequency),
	17:(5,"Frequency 4",decode_frequency),
	18:(5,"Frequency 5",decode_frequency),
	19:(255,"Serial Data Input",decode),
	20:(4,"Analogue 1",decode_analogue),
	21:(4,"Analogue 2",decode_analogue),
	22:(4,"Analogue 3",decode_analogue),
	23:(4,"Analogue 4",decode_analogue),
	24:(4,"Analogue 5",decode_analogue),
	25:(4,"Analogue 6",decode_analogue),
	26:(4,"Analogue 7",decode_analogue),
	27:(4,"Analogue 8",decode_analogue),
	28:(4,"Analogue 9",decode_analogue),
	29:(4,"Analogue 10",decode_analogue),
	30:(4,"Analogue 11",decode_analogue),
	31:(4,"Analogue 12",decode_analogue),
	32:(4,"Analogue 13",decode_analogue),
	33:(4,"Analogue 14",decode_analogue),
	34:(4,"Analogue 15",decode_analogue),
	35:(4,"Analogue 16",decode_analogue),
	36:(4,"Analogue 17",decode_analogue),
	37:(4,"Analogue 18",decode_analogue),
	38:(4,"Analogue 19",decode_analogue),
	39:(4,"Analogue 20",decode_analogue),
	40:(4,"Analogue 21",decode_analogue),
	41:(4,"Analogue 22",decode_analogue),
	42:(4,"Analogue 23",decode_analogue),
	43:(4,"Analogue 24",decode_analogue),
	44:(4,"Analogue 25",decode_analogue),
	45:(4,"Analogue 26",decode_analogue),
	46:(4,"Analogue 27",decode_analogue),
	47:(4,"Analogue 28",decode_analogue),
	48:(4,"Analogue 29",decode_analogue),
	49:(4,"Analogue 30",decode_analogue),
	50:(4,"Analogue 31",decode_analogue),
	51:(4,"Analogue 32",decode_analogue),
	52:(67,"Channel Data Channel",decode),
	53:(11,"Display Data Channel",decode),
	54:(6,"Reflash Channel",decode),
	55:(10,"Date Storage Channel",decode_date_storage),
	56:(10,"GPS Course Data",decode_gps_course_data),
	57:(10,"GPS Altitude and Altitude Accuracy",decode_gps_altitude),
	58:(11,"Extended Frequency 1",decode),
	59:(11,"Extended Frequency 2",decode),
	60:(11,"Extended Frequency 3",decode),
	61:(11,"Extended Frequency 4",decode),
	62:(11,"Extended RPM",decode),
	63:(3,"Start of Run Channel",decode),
	64:(5,"Processed Speed Data",decode),
	65:(30,"Gear Set Up Data",decode),
	66:(11,"Bargraph Set Up Data",decode),
	67:(4,"Dashboard Set Up Data",decode),
	68:(4,"Dashboard Set Up Data Two",decode),
	69:(42,"New Target Sector Time",decode),
	70:(42,"New Target Marker Time",decode),
	71:(3,"Auxiliary Input Module Number",decode),
	72:(5,"External Temperature Channel",decode),
	73:(5,"External Frequency Channel",decode),
	74:(5,"External Percentage Channel",decode),
	75:(6,"External Time Channel",decode),
	76:(24,"New LCD Data Channel",decode),
	77:(3,"New LED Data Channel",decode),
	78:(6,"Pre Calculated Distance Data Channel",decode),
	79:(4,"Yaw Rates Channel",decode),
	80:(4,"Calculated Yaw Channel",decode),
	81:(5,"Pitch Rate Channel",decode),
	82:(5,"Pitch Angle Channel",decode),
	83:(5,"Roll Rate Channel",decode),
	84:(5,"Roll Angle Channel",decode),
	85:(10,"Gradient Channel",decode),
	86:(5,"Pulse Count 1",decode),
	87:(5,"Pulse Count 2",decode),
	88:(5,"Pulse Count 3",decode),
	89:(5,"Pulse Count 4",decode),
	90:(6,"Baseline Channel",decode),
	91:(5,"Unit Control Channel",decode),
	92:(4,"Z Acceleration",decode),
	93:(5,"External Angle Channel",decode),
	94:(6,"External Pressure Channel",decode),
	95:(5,"External Miscellaneous Channel",decode),
	96:(10,"Time in to current lap and sector",decode),
	97:(8,"High resolution event timer",decode),
	101:(19,"Sector Definition Channel",decode),
	102:(255,"BRAKEBOX to PC Communication Channel",decode),
	103:(17,"DVR Communication Channel",decode),
	104:(9,"Video frame index",decode),
	105:(11,"Local NED velocities",decode),
	107:(255,"General Configuration Message",decode)}

class RaceTech:
	def __init__(self,f):
		self.buf = ''
		self.f = f

	def get_byte(self,p):
		if len(self.buf) <= p:
			b = self.f.read(16)
			if b == '':
				raise EOFError()
			self.buf += b
		return ord(self.buf[p])

	def run(self,alt_fn=None):
		pos = 0
		
		try:
			while True:
				header = self.get_byte(pos)
				pos += 1
				if not message_table.has_key(header):
					print 'INVALID HEADER',header
					self.buf = self.buf[pos:]
					pos = 0
					continue
				length, name, fn = message_table[header]
				cs = header
				variable_length = False
				if length == 255: #variable length
					pos += 1
					length = self.get_byte(pos)
					variable_length = True
					cs += length
				msg = []		
				for i in range(length-2):
					cs += self.get_byte(pos)
					msg.append(self.get_byte(pos))
					pos += 1
				cs = cs & 0xFF
				if cs == self.get_byte(pos):
					if alt_fn != None:
						alt_fn(header,length,msg,cs,variable_length)
					else:
						fn(msg)
					#fn(msg)
					#print header, name, fn(msg)
					self.buf = self.buf[pos+1:]
					pos = 0
				else:
					print 'CHECKSUM ERROR', header, name, msg, cs, ord(self.buf[pos])
					self.buf = self.buf[1:]
					pos = 0
		except EOFError:
			print "FINISHED"
