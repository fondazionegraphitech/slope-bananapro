# simple pyCan Example for can4linux
import time
import datetime
import signal
import sys
sys.path.insert(0, '/root/can4linux-code/can4linux-examples')
import pyCan

logFile = open('/var/log/slope/slope.log', 'a', 1)
msgFile = open('/root/slope-canbus-messages.txt', 'a+', 1)

def writeLog(text):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	logFile.write('[' + now + '] ' + text + '\n')

def writeMsg(text):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	msgFile.write('[' + now + '] ' + text + '\n')

def sigterm_handler(_signo, _stack_frame):
	# Raises SystemExit(0):
	sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

writeLog('Python wrapper loaded')

# setting the device number
device = 0
defaultBaudrate = '250'

# open the can interface /dev/can0
try:
	fileBaud = open('/proc/sys/dev/Can/Baud','r+')
	baudRates = fileBaud.read().split()
	baudRates[device] = defaultBaudrate
	fileBaud.write(' '.join(baudRates))
	fileBaud.close()
except IOError:
	writeLog('Could not set the new bitrate')
	exit()
except IndexError:
	writeLog('No proper entry for bitrate of can'+ str(device) + ' found')
	exit()

#print 'open can'+ str(device) + ' none blocking'
can_fd = pyCan.open(device)

if (can_fd == -1):
	writeLog('Error opening CAN device /dev/can'+ str(device))
	exit()

count = 0
while (count < 1): # sent n-times the message
	# send 8 byte with messageID 385dec = 181hex
	pyCan.send(can_fd,8,'385:1,2,3,4,5,6,7,8')
	count = count + 1

# use hex
#pyCan.send(can_fd,0,'0x100:0xaa,16,0x55')
#print '... sent message'

try:
	writeLog('Wait for message...')
	count = 0
	while True:
		data = pyCan.read(can_fd)
		arr = data.split(':', 1)
		messId = arr[0]
		if (messId == '512'):
			writeMsg(data)
		count = count + 1
		if (count == 100):
			count = 0
			time.sleep(0.5)
except KeyboardInterrupt:
	writeLog('Program exits with ctrl+c')
finally:
    pyCan.close(can_fd)
    writeLog('/dev/can' + str(device) + ' closed in finally')
    logFile.close()
    msgFile.close()
#data = pyCan.read2(can_fd, timeout * 1000000)
#arr = data.split(':', 3)
#messByte = arr[2][1:]
#data2 = arr[0].split('  ', 2)
#messId = data2[2]
#messLen = len(messId)
#messId = int(messId[:messLen-1], 0)
#if (messId == 512):
#	print messId
#	print messByte
#	count = count + 1

#print 'Wait ' + str(timeout) + ' sec for an message.....'
#print pyCan.read1(can_fd, timeout * 1000000)
#print 'Wait default timeout for an message.....'
#print pyCan.read1(can_fd)

pyCan.close(can_fd)
writeLog('/dev/can' + str(device) + ' closed at the end')
logFile.close()
msgFile.close()
exit()
