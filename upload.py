#!/usr/bin/env python

# Upload CAN messages and Tags detected to Industrial PC via WiFi
# This script will be called every 5 second by the main script

import httplib
import datetime
import time
import os

datafolder = '/root/slope-data/'
logFolder = '/root/slope-log/'

#datafolder = './umba-comments/examples/'
#logFolder = './umba-comments/slope-log/'

logFilePath = logFolder + 'slope-upload.log'

def write_log(text):
	logfile = open(logFilePath, 'a', 1)
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logfile.write('[' + now + '] ' + text + '\n')
	logfile.close()
	
def get_timestamp():
	return str(int(round(time.time() * 1000)))		

def upload():
	# URL or IP and Port of Industrial PC
	#url = "127.0.0.1:80"
	url = "192.168.43.78:8001"
	servlet_GET = "/SLOPE/HTTPMethod_SLOPE"
	servlet_POST = "/SLOPE/HTTPMethod_SLOPE_2"

	# Timestamp here to have the same timestamp for all the loops
	timestamp = get_timestamp()

	try:
		# Within this code we are trying to check if the industrial pc is reachable
		conn = httplib.HTTPConnection(url)
		conn.request("GET", servlet_GET)
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
						conn.request("POST", servlet_POST, msgString, headers)
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
			
#upload() #Used by tests made from executing this script from the PC		