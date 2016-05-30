#!/usr/bin/env python

# Upload CAN messages and Tags detected to Industrial PC via WiFi
# This script will be called every 5 second by the main script

import httplib
import datetime
import time
import os

logFilePath = ""

def write_log(text):
	logfile = open(logFilePath, 'a', 1)
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logfile.write('[' + now + '] ' + text + '\n')
	logfile.close()
	
def get_timestamp():
	return str(int(round(time.time() * 1000)))		

def upload(datafolder, logFolder):
	# URL or IP and Port of Industrial PC
	url = "127.0.0.1:80"
	servlet = "/BananaProServer/index.php"

	logFilePath = logFolder + 'slope-upload.log'

	# Timestamp here to have the same timestamp for all the loops
	timestamp = get_timestamp()

	try:
		# Within this code we are trying to check if the industrial pc is reachable
		conn = httplib.HTTPConnection(url)
		conn.request("GET", servlet)

		if conn.getresponse().status == 200:
			write_log('Connection with the industrial pc established, send data')
			headers = {"Content-type": "text/plain"}
		
			# Send all the files not delivered before
			listFiles = os.listdir(datafolder)
			for file in listFiles:
				msgFilePath = datafolder + file
				# Send files all together
				if os.path.isfile(msgFilePath):
					filename, extension = os.path.splitext(msgFilePath)
					if(extension != '.done'):
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
							os.rename(msgFilePath, msgFilePath + "." + timestamp + ".done")
	except IOError:
		write_log('Error: Industrial PC unreachable')
	finally:
		conn.close()