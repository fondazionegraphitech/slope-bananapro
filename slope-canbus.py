# simple pyCan Example for can4linux
import pyCan
print '....... swig-python wrapper loaded'


# setting the device number
#device = 1
#defaultBaudrate = '125'
device = 0
defaultBaudrate = '250'

# open the can interface /dev/can1
# but before, set the baud rate if other than default
try:
    fileBaud = open('/proc/sys/dev/Can/Baud','r+')
    baudRates = fileBaud.read().split()
    baudRates[device] = defaultBaudrate
    fileBaud.write(' '.join(baudRates))
    fileBaud.close()
except IOError:
    print 'Could not set the new bitrate '
    exit()
except IndexError:
    print 'No proper entry for bitrate of can'+ str(device) + ' found.'
    exit()
    


print '....... bit rate changed'

print 'open can'+ str(device) + ' none blocking'
can_fd = pyCan.open(device)

if can_fd == -1:
     print 'error opening CAN device /dev/can'+ str(device)
     exit()

count = 0
while (count < 1):
    # send 8 byte, message id 385dec = 181hex
    pyCan.send(can_fd,8,'385:1,2,3,4,5,6,7,8')
    print '... sent message'
    count = count + 1

# don't specify message length
#pyCan.send(can_fd,0,'100:8,7,6,5,4,3,2,1')
#print '... sent message'

# use hex
#pyCan.send(can_fd,0,'0x100:0xaa,16,0x55')
#print '... sent message'

# send RTR messages
#pyCan.send(can_fd,0,'r200')
#print '... sent message'

#pyCan.send(can_fd,4,'r101')
#print '... sent message'


timeout = 30 #seconds
# try to receive something from can_fd, timeout in us
# wait forever if timeout == 0

print 'Wait ' + str(timeout) + ' sec for an message.....'
count = 0
#while (count < 30):
while 1:
    data = pyCan.read(can_fd)
    arr = data.split(':', 1)
    messId = arr[0]
    if (messId == '512'):
        print data
        count = count + 1
#    data = pyCan.read2(can_fd, timeout * 1000000)
#    arr = data.split(':', 3)
#    messByte = arr[2][1:]
#    
#    data2 = arr[0].split('  ', 2)
#    messId = data2[2]
#    messLen = len(messId)
#    messId = int(messId[:messLen-1], 0)
#
#    if (messId == 512):
#        print messId
#        print messByte
#        count = count + 1

#print 'Wait ' + str(timeout) + ' sec for an message.....'
#print pyCan.read1(can_fd, timeout * 1000000)
#print 'Wait default timeout for an message.....'
#print pyCan.read1(can_fd)

pyCan.close(can_fd)
print '....... /dev/can' + str(device) + ' closed'

#print 'open can'+ str(device) + ' blocking'
#can_fd = pyCan.open(device, 'b')

#print 'Wait for an message, forever if blocking opend.....'
#print pyCan.read(can_fd)
#pyCan.close(can_fd)
#print '....... /dev/can' + str(device) + ' closed'

exit()

