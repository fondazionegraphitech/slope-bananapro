#!/usr/bin/env python

# upload CAN messages and Tags detected to Industrial PC via WiFi

import httplib
import datetime
import time
import os

# URL or IP and Port of Industrial PC
url = "127.0.0.1:80"
servlet = "/BananaProServer/index.php"

today = datetime.datetime.now().strftime("%Y-%m-%d")
msgFilePath = '/root/slope-data/' + today + '_canbus-messages.txt'
tagsFilePath = '/root/slope-data/' + today + '_rfid-tags.txt'
logFilePath = '/root/slope-log/' + today + '_slope-canbus.log'

# Files paths in local development
# msgFilePath = "../example_slope-canbus-messages.txt"
# tagsFilePath = "../example_slope-rfid-tags.txt"
# logFilePath = '../upload-data.log'


def write_log(text):
	logfile = open(logFilePath, 'a', 1)
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logfile.write('[' + now + '] ' + text + '\n')
	logfile.close()

#write_log('Slope-Upload Version 1.0')

try:
	conn = httplib.HTTPConnection(url)
	conn.request("GET", servlet)

	if conn.getresponse().status == 200:
		write_log('Connection with industrial pc established, send data')
		headers = {"Content-type": "text/plain"}

		if os.path.isfile(tagsFilePath):
			tagsFile = open(tagsFilePath, 'r')
			for tag in tagsFile:
				conn = httplib.HTTPConnection(url)
				conn.request("POST", servlet, tag, headers)
				response = conn.getresponse()
				status = response.status
				text = response.read()
				if status != 200:
					write_log('Error: ' + status + ' ' + response.reason)
				print text
				time.sleep(0.005)	

			tagsFile.close()
			os.rename(tagsFilePath, tagsFilePath + ".done")

		if os.path.isfile(msgFilePath):
			msgFile = open(msgFilePath, 'r')
			for msg in msgFile:
				conn = httplib.HTTPConnection(url)
				conn.request("POST", servlet, msg, headers)
				response = conn.getresponse()
				status = response.status
				text = response.read()
				if status != 200:
					write_log('Error: ' + status + ' ' + response.reason)
				print text	
				time.sleep(0.005)

			msgFile.close()
			os.rename(msgFilePath, msgFilePath + ".done")

except IOError:
	#write_log('Error: Industrial PC unreachable')

finally:
	conn.close()