#!/usr/bin/env python

# Upload CAN messages and Tags detected to Industrial PC via WiFi
# This script will be called every 5 second by the main script

import httplib
import datetime
import time
import os

# URL or IP and Port of Industrial PC
url = "127.0.0.1:80"
servlet = "/BananaProServer/index.php"

# Paths to the LOG files: only _canbus-messages and _rfid-tags data will be sent
today = datetime.datetime.now().strftime("%Y-%m-%d")
msgFilePath = '/root/slope-data/' + today + '_canbus-messages.txt'
tagsFilePath = '/root/slope-data/' + today + '_rfid-tags.txt'
logFilePath = '/root/slope-log/' + today + '_slope-upload.log'

#msgFilePath = 'umba-comments/examples/2016-05-25_canbus-messages.txt'
#tagsFilePath = 'umba-comments/examples/2016-05-25_rfid-tags.txt'

def write_log(text):
	logfile = open(logFilePath, 'a', 1)
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logfile.write('[' + now + '] ' + text + '\n')
	logfile.close()

def get_timestamp():
	return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")	

try:
	# Within this code we are trying to check if the industrial pc is reachable
	conn = httplib.HTTPConnection(url)
	conn.request("GET", servlet)

	if conn.getresponse().status == 200:
		write_log('Connection with the industrial pc established, send data')
		headers = {"Content-type": "text/plain"}

		# Send tags all together
		if os.path.isfile(tagsFilePath):
			tagsFile = open(tagsFilePath, 'r')
			tagsString = tagsFile.read()	
			conn = httplib.HTTPConnection(url)
			conn.request("POST", servlet, tagsString, headers)
			response = conn.getresponse()
			status = response.status
			text = response.read().strip();
			tagsFile.close()
			
			if status != 200:
				write_log('Error: ' + status + ' ' + response.reason)
			if status == 200:
				# Then, we will rename _rfid-tags.txt in order to avoid to send same data in the future
				write_log('Done: ' + tagsFilePath)
				os.rename(tagsFilePath, tagsFilePath + "." + get_timestamp() + ".done")

			# First, we will send TAGS data: one POST call for each Json stored in _rfid-tags.txt
			"""for tag in tagsFile:
				conn = httplib.HTTPConnection(url)
				conn.request("POST", servlet, tag, headers)
				response = conn.getresponse()
				status = response.status
				text = response.read()
				if status != 200:
					write_log('Error: ' + status + ' ' + response.reason)
				time.sleep(0.005)	

			tagsFile.close()"""

		# Send can all together
		if os.path.isfile(msgFilePath):
			msgFile = open(msgFilePath, 'r')
			msgString = msgFile.read()	
			conn = httplib.HTTPConnection(url)
			conn.request("POST", servlet, msgString, headers)
			response = conn.getresponse()
			status = response.status
			text = response.read().strip();
			msgFile.close()
			
			if status != 200:
				write_log('Error: ' + status + ' ' + response.reason)
			if status == 200:
				# Then, we will rename _rfid-tags.txt in order to avoid to send same data in the future
				write_log('Done: ' + msgFilePath)
				os.rename(msgFilePath, msgFilePath + "." + get_timestamp() + ".done")

		# Now, we will send CANBUS data: one POST call for each Json stored in _canbus-messages.txt
		"""if os.path.isfile(msgFilePath):
			msgFile = open(msgFilePath, 'r')
			for msg in msgFile:
				conn = httplib.HTTPConnection(url)
				conn.request("POST", servlet, msg, headers)
				response = conn.getresponse()
				status = response.status
				text = response.read()
				if status != 200:
					write_log('Error: ' + status + ' ' + response.reason)
				time.sleep(0.005)

			msgFile.close()
			# Then, we will rename _canbus-messages.txt in order to avoid to send same data in the future
			os.rename(msgFilePath, msgFilePath + "." + timestamp + ".done")"""

except IOError:
	write_log('Error: Industrial PC unreachable')

finally:
	conn.close()