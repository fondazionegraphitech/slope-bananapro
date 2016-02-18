# simple pyCan Example for can4linux
import time
import datetime
import signal
import sys
import subprocess
import struct
sys.path.insert(0, '/root/can4linux-code/can4linux-examples')
import pyCan

logFile = open('/var/log/slope/slope.log', 'a', 1)
msgFile = open('/root/slope-canbus-messages.txt', 'a+', 1)


def get_lifting_status(status):
	if status == 0:
		return "stop"
	elif status == 1:
		return "going up"
	elif status == 2:
		return "going down"
	else:
		return "error"


def get_translation_status(status):
	if status == 0:
		return "stop"
	elif status == 1:
		return "going to load"
	elif status == 2:
		return "going to release"
	else:
		return "error"


def write_log(text):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logFile.write('[' + now + '] ' + text + '\n')


def write_msg(text):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	msgFile.write('[' + now + '] ' + text + '\n')


def sigterm_handler(_signo, _stack_frame):
	# Raises SystemExit(0):
	sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

write_log('Python wrapper loaded')

# setting the device number
device = 0
defaultBaudrate = '250'

# open the can interface /dev/can0
try:
	fileBaud = open('/proc/sys/dev/Can/Baud', 'r+')
	baudRates = fileBaud.read().split()
	baudRates[device] = defaultBaudrate
	fileBaud.write(' '.join(baudRates))
	fileBaud.close()

except IOError:
	write_log('Could not set the new bitrate')
	exit()

except IndexError:
	write_log('No proper entry for bitrate of can' + str(device) + ' found')
	exit()

# print 'open can'+ str(device) + ' none blocking'
can_fd = pyCan.open(device)

if can_fd == -1:
	write_log('Error opening CAN device /dev/can' + str(device))
	exit()

try:
	write_log('Wait for message...')
	count = 0
	flip = '0'
	while True:
		data = pyCan.read(can_fd)
		arrMess = data.split(':', 3)
		messId = arrMess[0][:len(arrMess[0]) - 1]
		if messId.isdigit():
			messId = int(messId)
		if messId == 30:
			# print messId
			start = arrMess[1].find("(")
			end = arrMess[1].find(")")
			bytesNum = arrMess[1][start + 1:end]
			# print bytesNum
			messBytes = arrMess[2][1:]
			arrBytes = messBytes.split()
			if bytesNum.isdigit():
				bytesNum = int(bytesNum)
			if bytesNum == len(arrBytes):
				weight = int(struct.unpack('>h', "".join(map(chr, [int(arrBytes[0]), int(arrBytes[1])])))[0])
				# (kg) kilogrammes
				position = int(struct.unpack('>h', "".join(map(chr, [int(arrBytes[2]), int(arrBytes[3])])))[0])
				# (m) meters
				speed = float(struct.unpack('>f', "".join(
					map(chr, [int(arrBytes[4]), int(arrBytes[5]), int(arrBytes[6]), int(arrBytes[7])])))[0])
				# (m/s) meters at second

				output = str(weight) + "kg " + str(position) + "m " + str(speed) + "m/s "
				# decide what to do...
				write_msg("%d:%s" % (messId, output))

		if messId == 31:
			# print messId
			start = arrMess[1].find("(")
			end = arrMess[1].find(")")
			bytesNum = arrMess[1][start + 1:end]
			# print bytesNum
			messBytes = arrMess[2][1:]
			arrBytes = messBytes.split()
			if bytesNum.isdigit():
				bytesNum = int(bytesNum)
			if bytesNum == len(arrBytes):
				axleX = int(arrBytes[0])
				# (%) percentage of X axle grade (frontal)
				axleY = int(arrBytes[1])
				# (%) percentage of Y axle grade (lateral)
				consumption = int(struct.unpack('>h', "".join(map(chr, [int(arrBytes[2]), int(arrBytes[3])])))[0])
				# (l/h) liters at hour
				lifting = get_lifting_status(int(arrBytes[4]))
				# lifting status (0='stop', 1='up', 2='down')
				translation = get_translation_status(int(arrBytes[5]))
				# translation status (0='stop', 1='to load', 2='to release')

				output = str(axleX) + "% " + str(axleY) + "% " + str(consumption) + "l/h " + lifting + " " + translation
				# decide what to do...
				write_msg("%d:%s" % (messId, output))

		count += 1
		if count == 100:
			count = 0
			pyCan.send(can_fd, 1, '60:' + flip)
			if flip == '0':
				flip = '1'
			if flip == '1':
				flip = '0'
			subprocess.call(['java -jar', '/root/slope-bananapro/TagsReader.jar'])
			time.sleep(0.5)

except KeyboardInterrupt:
	write_log('Program exits with ctrl+c')

finally:
	pyCan.close(can_fd)
	write_log('/dev/can' + str(device) + ' closed in finally')
	logFile.close()
	msgFile.close()

# print 'Wait ' + str(timeout) + ' sec for an message.....'
# print pyCan.read1(can_fd, timeout * 1000000)
# print 'Wait default timeout for an message.....'
# print pyCan.read1(can_fd)

# pyCan.close(can_fd)
# write_log('/dev/can' + str(device) + ' closed at the end')
# logFile.close()
# msgFile.close()
# exit()
