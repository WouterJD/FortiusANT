#!/bin/bash
# https://www.raspberrypi.org/forums/viewtopic.php?f=66&t=294014

mkdir $HOME/.config/lxsession
mkdir $HOME/.config/lxsession/LXDE-pi

# copy system-wide autostart
cp /etc/xdg/lxsession/LXDE-pi/autostart $HOME/.config/lxsession/LXDE-pi/

# add startup of FortiusAnt to it
echo "@lxterminal -e $HOME/FortiusANT/raspberry/FortiusAnt.sh" >>$HOME/.config/lxsession/LXDE-pi/autostart
#nano $HOME/.config/lxsession/LXDE-pi/autostart

echo FortiusAnt will be started after reboot, press Enter to continue
read reply