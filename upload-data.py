#!/usr/bin/env python

# upload CAN messages and Tags detected to Industrial PC via WiFi

import httplib
import datetime
import time
import os

# URL or IP and Port of Industrial PC
url = "192.168.253.100:8080"
servlet = "/SlopeIndustrialPC"

today = datetime.datetime.now().strftime("%Y-%m-%d")
# Files paths in production
msgFilePath = '/root/slope-data/' + today + '_canbus-messages.txt'
tagsFilePath = '/root/slope-data/' + today + '_rfid-tags.txt'
logFilePath = '/var/log/slope/' + today + '_upload-data.log'

# Files paths in local development
# msgFilePath = "../example_slope-canbus-messages.txt"
# tagsFilePath = "../example_slope-rfid-tags.txt"
# logFilePath = '../upload-data.log'


def write_log(text):
	logfile = open(logFilePath, 'a', 1)
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logfile.write('[' + now + '] ' + text + '\n')
	logfile.close()


begin = int(round(time.time() * 1000))

try:
	conn = httplib.HTTPConnection(url)
	conn.request("GET", servlet)

	if conn.getresponse().status == 200:
		headers = {"Content-type": "text/plain"}

		if os.path.isfile(tagsFilePath):
			tagsFile = open(tagsFilePath, 'r')
			for tag in tagsFile:
				conn = httplib.HTTPConnection(url)
				conn.request("POST", servlet + "/tags/upload", tag, headers)
				if conn.getresponse().status != 200:
					write_log('Error: ' + conn.getresponse().status + ' ' + conn.getresponse().reason)
				time.sleep(0.005)

			tagsFile.close()
			os.rename(tagsFilePath, tagsFilePath + ".done")

		if os.path.isfile(msgFilePath):
			msgFile = open(msgFilePath, 'r')
			for msg in msgFile:
				conn = httplib.HTTPConnection(url)
				conn.request("POST", servlet + "/canmsg/upload", msg, headers)
				if conn.getresponse().status != 200:
					write_log('Error: ' + conn.getresponse().status + ' ' + conn.getresponse().reason)
				time.sleep(0.001)

			msgFile.close()
			os.rename(msgFilePath, msgFilePath + ".done")

except IOError:
	write_log('Error: Industrial PC unreachable')

finally:
	conn.close()

end = int(round(time.time() * 1000))

print end - begin
