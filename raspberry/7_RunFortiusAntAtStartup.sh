#!/bin/bash
# https://www.raspberrypi.org/forums/viewtopic.php?f=66&t=294014

mkdir /home/pi/.config/lxsession
mkdir /home/pi/.config/lxsession/LXDE-pi
cp /etc/xdg/lxsession/LXDE-pi/autostart /home/pi/.config/lxsession/LXDE-pi/

echo "@lxterminal -e /home/pi/FortiusANT/raspberry/FortiusAnt.sh" >>/home/pi/.config/lxsession/LXDE-pi/autostart
#nano /home/pi/.config/lxsession/LXDE-pi/autostart

echo FortiusAnt will be started after reboot, press Enter to continue
read reply
