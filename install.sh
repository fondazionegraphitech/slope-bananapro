#!/bin/sh

mkdir -p /var/log/slope
cp /root/slope-bananapro/slope /etc/init.d/slope
update-rc.d slope defaults