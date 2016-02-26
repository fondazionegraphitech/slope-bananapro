#!/bin/sh

mkdir -p /var/log/slope
mkdir -p /root/slope-data
cp /root/slope-bananapro/slope /etc/init.d/slope
update-rc.d slope defaults