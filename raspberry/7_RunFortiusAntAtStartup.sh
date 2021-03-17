#!/bin/bash 
# https://www.raspberrypi.org/forums/viewtopic.php?f=66&t=294014

mkdir $HOME/.config/lxsession
mkdir $HOME/.config/lxsession/LXDE-pi

# ----------------------------------------------------------
# Uncomment so that Raspberry will boot without HDMI monitor connected
# ----------------------------------------------------------
cat /boot/config.txt | sed -e "s/#hdmi_force_hotplug=1/hdmi_force_hotplug=1/" >./config.txt
sudo cp ./config.txt /boot/config.txt
rm ./config.txt

# ----------------------------------------------------------
# copy system-wide autostart (to Pi user)
# ----------------------------------------------------------
cp /etc/xdg/lxsession/LXDE-pi/autostart $HOME/.config/lxsession/LXDE-pi/

# ----------------------------------------------------------
# add startup of FortiusAnt to it
# ----------------------------------------------------------
echo "@lxterminal -e $HOME/FortiusANT/raspberry/FortiusAnt.sh" >>$HOME/.config/lxsession/LXDE-pi/autostart
#nano $HOME/.config/lxsession/LXDE-pi/autostart

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} FortiusAnt will be started after reboot, press Enter to continue: "
read reply