#!/bin/bash

# ----------------------------------------------------------
# Tacx USB-interface info
# Remove everything untill : (including)
# Remove spaces (Note: 's/ *//' does not work
# ----------------------------------------------------------
HEADUNIT=`lsusb | grep 3561 | sed -e 's/^.*://' -e 's/ //g'` 
if [ T$HEADUNIT = T ]; then
    echo No Tacx USB-interface connected
else
    echo Tacx with T$HEADUNIT connected
fi

# ----------------------------------------------------------
# ANT USB-interface info
# ----------------------------------------------------------
ANT=NoAntFound
ANTTYPE=
if [ `lsusb | grep -c ':1004'` == 1 ] ; then
    ANT=1004
    ANTTYPE=Older
fi
if [ `lsusb | grep -c ':1008'` == 1 ] ; then
    ANT=1008
    ANTTYPE=Suunto
fi
if [ `lsusb | grep -c ':1009'` == 1 ] ; then
    ANT=1009
    ANTTYPE=Garmin
fi
if [ ANT == NoAntFound ]; then
    echo No ANTdongle found
else
    VENDOR=`lsusb | grep $ANT | sed -e 's/^.*ID //' -e 's/:.*$//'`
    echo ANT dongle $VENDOR:$ANT $ANTTYPE found

    lsusb | grep ":$ANT"
fi

# ----------------------------------------------------------
# First create files, then cp to target
# ----------------------------------------------------------
if [ ANT != NoAntFound ]; then
    cat << EOF > ant-usb2.conf
# Options for ANTdonle $ANTTYPE $VENDOR:$ANT
Options usbserial vendor=0x$VENDOR product=0x$ANT
EOF
    sudo cp ant-usb2.conf /etc/modprobe.d/
    rm ant-usb2.conf
fi

cat << EOF > 10-usbaccess.rules
# Allow users in group usbtacx to access Tacx USB headunit
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="usbtacx"
EOF

if [ ANT != NoAntFound ]; then
    cat << EOF >> 10-usbaccess.rules
# Allow users in group usbtacx to access ANTdongle
SUBSYSTEM==”tty”, ACTION==”add”, ATTRS{idProduct}==”$ANT”, ATTRS{idVendor}==”$VENDOR”, MODE=”0666”, GROUP=”usbtacx”
EOF
fi

sudo cp 10-usbaccess.rules /etc/udev/rules.d/
rm 10-usbaccess.rules

# ----------------------------------------------------------
# Verify
# ----------------------------------------------------------
#nano /etc/modprobe.d/ant-usb2.conf
#nano /etc/udev/rules.d/10-usbaccess.rules

# ----------------------------------------------------------
# Create group and add user
# ----------------------------------------------------------
echo Create group usbtacx
sudo addgroup usbtacx
echo add user pi to this group
sudo adduser pi usbtacx

# ----------------------------------------------------------
echo pi user is granted access to usb after reboot, press Enter to continue
read reply

# Reboot to activate rule
sudo reboot now
