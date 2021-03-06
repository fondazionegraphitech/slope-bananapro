#!/usr/bin/env python

# simple pyCan Example for can4linux
import time
import datetime
import signal
import sys
import subprocess
import struct
import json
import os
import threading

sys.path.insert(0, '/root/can4linux-code/can4linux-examples')
import pyCan

import upload

# the power expressed in (mW)
# default is around 660
# it must be an Integer greater then 45
# 45mW allows to detect tags at aroud 50cm distance
antennaPower = 2000

datafolder = '/root/slope-data/'
logFolder = '/root/slope-log/'

def get_incremental_number():
	maxcounter = 0
	listFiles = os.listdir(datafolder)
	for file in listFiles:
		if os.path.isfile(datafolder + file):
			name = file.split('_')
			if len(name) > 0:
				counter = name[0]
				if counter.isdigit():
					counter = int(counter)
					if counter > maxcounter:
				 		maxcounter = counter	 		
	return maxcounter + 1

incremental = get_incremental_number()
msgFilePath = datafolder + str(incremental) + '_canbus-messages.txt'
logFilePath = logFolder + 'slope-canbus.log'

def get_lifting_status(status):
	if status == 0:
		return "stop"
	elif status == 1:
		return "going up"
	elif status == 2:
		return "going down"
	elif status == 3:
		return "going up, antenna down"	
	elif status == 4:
		return "going down, antenna down"		
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
	logfile = open(logFilePath, 'a', 1)
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logfile.write('[' + now + '] ' + text + '\n')
	logfile.close()


def write_msg(text):
	msgfile = open(msgFilePath, 'a+', 1)
	# now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	msgfile.write(text + '\n')
	msgfile.close()

def get_timestamp():
	return str(int(round(time.time() * 1000)))	


def sigterm_handler(_signo, _stack_frame):
	# Raises SystemExit(0):
	sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

#print 'Python wrapper loaded'
#print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
write_log('Slope-Canbus Version 1.0')
write_log('Python wrapper loaded')
write_log('Incremental Log Number: ' + str(incremental))

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
	lastMsg30 = ""
	lastMsg31 = ""
	lastLifting = 0
	
	speedLimit = 1 # (m/s) meters at second 3.6 km/h
	lastSpeed = 0
	
	upload_th = threading.Thread(target=upload.upload, args=())
	
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
			if messBytes != lastMsg30:  # discard new message if is equal to last one
				lastMsg30 = messBytes
				arrBytes = messBytes.split()
				if bytesNum.isdigit():
					bytesNum = int(bytesNum)
				if bytesNum == len(arrBytes):
					weight = int(struct.unpack('<h', "".join(map(chr, [int(arrBytes[0]), int(arrBytes[1])])))[0])
					# (kg) kilogrammes
					position = int(struct.unpack('<h', "".join(map(chr, [int(arrBytes[2]), int(arrBytes[3])])))[0])
					# (m) meters
					speed = float(struct.unpack('<f', "".join(map(chr, [int(arrBytes[4]), int(arrBytes[5]), int(arrBytes[6]), int(arrBytes[7])])))[0])
					# (m/s) meters at second

					# decide what to do...
					# strOutput = str(weight) + "kg " + str(position) + "m " + str(speed) + "m/s "
					# write_msg("%d:%s" % (messId, strOutput))
					objOutput = {"id": incremental, "weight": weight, "position": position, "speed": speed, "timestamp": get_timestamp()}
					write_msg(json.dumps(objOutput))
					lastSpeed = speed

		if messId == 31:
			# print messId
			start = arrMess[1].find("(")
			end = arrMess[1].find(")")
			bytesNum = arrMess[1][start + 1:end]
			# print bytesNum
			messBytes = arrMess[2][1:]
			if messBytes != lastMsg31:  # discard new message if is equal to last one
				lastMsg31 = messBytes
				arrBytes = messBytes.split()
				if bytesNum.isdigit():
					bytesNum = int(bytesNum)
				if bytesNum == len(arrBytes):
					axleX = int(arrBytes[0])
					# (%) percentage of X axle grade (frontal)
					axleY = int(arrBytes[1])
					# (%) percentage of Y axle grade (lateral)
					consumption = int(struct.unpack('<h', "".join(map(chr, [int(arrBytes[2]), int(arrBytes[3])])))[0])
					# (l/h) liters at hour
					lifting = get_lifting_status(int(arrBytes[4]))
					# lifting status (0='stop', 1='going up', 2='going down', 3='antenna down')
					translation = get_translation_status(int(arrBytes[5]))
					# translation status (0='stop', 1='going to load', 2='going to release')

					# decide what to do...
					# strOutput = str(axleX) + "% " + str(axleY) + "% " + str(consumption) + "l/h " + lifting + " " + translation
					# write_msg("%d:%s" % (messId, strOutput))
					objOutput = {"id": incremental, "axleX": axleX, "axleY": axleY, "consumption": consumption, "lifting": lifting, "translation": translation, "timestamp": get_timestamp()}
					write_msg(json.dumps(objOutput))
					lastLifting = int(arrBytes[4]) 

		
		count += 1
		
		#every 0.5 sec see below (10 msg per second)
		if count % 5 == 0:
			try:
				if lastLifting == 3 and lastSpeed <= speedLimit: #if is going up AND it is not moving
					subprocess.check_call("java -jar /root/slope-bananapro/TagsReader.jar " + str(antennaPower) + " "  + str(incremental), shell=True)
					lastLifting = 0
			except subprocess.CalledProcessError, e:
				write_log('Error executing lib TagsReader.jar: ' + str(e))	
		
		#every 5 sec upload data and send watchdog
		if count == 50:
			count = 0
			pyCan.send(can_fd, 1, '60:' + flip)
			if flip == '0':
				flip = '1'
			if flip == '1':
				flip = '0'
				
			if not upload_th.isAlive():
				upload_th = threading.Thread(target=upload.upload, args=())
				upload_th.start()

		time.sleep(0.1)	

except KeyboardInterrupt:
	write_log('Program exits with ctrl+c')

finally:
	pyCan.close(can_fd)
	write_log('/dev/can' + str(device) + ' closed in finally')

# print 'Wait ' + str(timeout) + ' sec for an message.....'
# print pyCan.read1(can_fd, timeout * 1000000)
# print 'Wait default timeout for an message.....'
# print pyCan.read1(can_fd)

# pyCan.close(can_fd)
# write_log('/dev/can' + str(device) + ' closed at the end')
# logFile.close()
# msgFile.close()
# exit()
