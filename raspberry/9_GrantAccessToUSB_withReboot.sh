#!/bin/bash
# three-step, immediate cat did not work
cat << EOF > 10-usbaccess.rules
# Allow users in group usbtacx to access usb
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="usbtacx"
EOF
sudo cp 10-usbaccess.rules /etc/udev/rules.d
rm 10-usbaccess.rules

echo Create group usbtacx
sudo addgroup usbtacx
echo add user pi to this group
sudo adduser pi usbtacx

echo pi user is granted access to usb after reboot, press Enter to continue
read reply

# Reboot to activate rule
sudo reboot now
