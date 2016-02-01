# simple pyCan Example for can4linux
import time
import signal
import sys
sys.path.insert(0, '/root/can4linux-code/can4linux-examples')
import pyCan

logFile = open("/var/log/slope/slope.log", "a")

logFile.write('Python wrapper loaded');

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
	logFile.write('Could not set the new bitrate');
	exit()
except IndexError:
	logFile.write('No proper entry for bitrate of can'+ str(device) + ' found.');
	exit()

#print 'open can'+ str(device) + ' none blocking'
can_fd = pyCan.open(device)

if (can_fd == -1):
	logFile.write('error opening CAN device /dev/can'+ str(device));
	exit()

count = 0
while (count < 1): # sent n-times the message
	# send 8 byte with messageID 385dec = 181hex
	pyCan.send(can_fd,8,'385:1,2,3,4,5,6,7,8')
	count = count + 1

# use hex
#pyCan.send(can_fd,0,'0x100:0xaa,16,0x55')
#print '... sent message'

def sigterm_handler(_signo, _stack_frame):
	# Raises SystemExit(0):
	sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

try:
	logFile.write('Wait for message...');
	count = 0
	while True:
		data = pyCan.read(can_fd)
		arr = data.split(':', 1)
		messId = arr[0]
		if (messId == '512'):
			logFile.write(data);
		count = count + 1
		if (count == 100):
			count = 0
			time.sleep(1)
finally:
    pyCan.close(can_fd)
    logFile.write('/dev/can' + str(device) + ' closed.');
    logFile.close()

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
logFile.write('/dev/can' + str(device) + ' closed.');
logFile.close()
exit()
