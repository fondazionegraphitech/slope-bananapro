# SLOPE: BananaPro + CAN bus
[SLOPE Project](http://www.slopeproject.eu) by [Fondazione GraphiTech](http://www.graphitech.it).

## System Requirements

In order to use this project you need a [Banana PI Pro](https://en.wikipedia.org/wiki/Banana_Pi#Banana_Pi_Pro) with [Bananian OS](https://www.bananian.org/download) and the CAN bus device driver [can4linux](http://sourceforge.net/projects/can4linux).
If you want to connect the BananaPro to a real CAN bus you also need a CAN transceiver like [Texas Instruments TI SN65HVD230](http://www.ti.com/product/SN65HVD230), which allows to connect the CAN_TX and CAN_RX pins provided by the Banana GPIO port to CAN_H and CAN_L used by CAN bus networks. We used the [WaveShare CAN board](http://www.waveshare.com/sn65hvd230-can-board.htm), which provides the "TI SN65HVD230" already mounted on board.

These scripts have been tested with:

- Linux bananapro 3.4.108-bananian ##2 SMP PREEMPT Thu Aug 13 06:08:25 UTC 2015 armv7l GNU/Linux

- CAN Driver 4.5_BANANAPI SVN version 517 (c) Nov 24 2015 16:38:52

## Installation

1. Login via `ssh root@<DEVICE-IP>`

2. Perform the following steps:

	* cd /root/
	* git clone https://github.com/fondazionegraphitech/slope-bananapro.git
	* cd /root/slope-bananapro/
	* sh install.sh

3. Reboot the BananaPro.

4. You should have the Python script starting at boot check with command `service slope status`.

## Dependencies

1. Download & Install Bananian OS from "https://www.bananian.org/download", the default username/password is `root/pi`

2. Login to BananaPro using a USB keyboard and an HDMI monitor, then perform the following steps:
	
	* apt-get update & upgrade
	* reboot
	* apt-get install build-essential
	* apt-get install subversion
	* svn co https://svn.code.sf.net/p/can4linux/code/trunk@517 can4linux-code
	* uname -r
	* apt-get install linux-headers-3.4.108-bananian
	* cd /root/can4linux-code/can4linux/
	* make TARGET=BANANAPI
	* insmod can4linux.ko
	* cp can4linux.ko /lib/modules/3.4.108-bananian/kernel/net/can/
	* depmod -A -v
	* modprobe -v can4linux
	* echo "" >> /etc/modules ; echo "can4linux" >> /etc/modules
	* reboot
	* dmesg | grep can4linux
	* cat /proc/devices | grep can4linux

3. Set up SSH for future use `ssh root@<DEVICE-IP>`

4. Test using examples

	* apt-get install swig
	* apt-get install python-dev
	* cd /root/can4linux-code/can4linux-examples/
	* make
	* make pyCan

5. Update CAN speed and device in file `/root/can4linux-code/can4linux-examples/pyCan-example.py` with:

	* device = 0
	* defaultBaudrate = '250'

6. Execute `python /root/can4linux-code/can4linux-examples/pyCan-example.py`
