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
USBCONF=FortiusAntUsb2.conf
if [ ANT != NoAntFound ]; then
    cat << EOF > $USBCONF
# Options for ANTdongle $ANTTYPE $VENDOR:$ANT
Options usbserial vendor=0x$VENDOR product=0x$ANT
EOF
    sudo cp $USBCONF /etc/modprobe.d/
    rm $USBCONF
fi

USBRULES=FortiusAntUsbAccess.rules
cat << EOF > $USBRULES
# Allow users in group usbtacx to access Tacx USB headunit
SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="usbtacx"
EOF

if [ ANT != NoAntFound ]; then
    cat << EOF >> $USBRULES
# Allow users in group usbtacx to access ANTdongle
SUBSYSTEM==”tty”, ACTION==”add”, ATTRS{idProduct}==”$ANT”, ATTRS{idVendor}==”$VENDOR”, MODE=”0666”, GROUP=”usbtacx”
EOF
fi

sudo cp $USBRULES /etc/udev/rules.d/
rm $USBRULES

# ----------------------------------------------------------
# Verify
# ----------------------------------------------------------
#nano /etc/modprobe.d/$USBCONF
#nano /etc/udev/rules.d/$USBRULES

# ----------------------------------------------------------
# Create group and add user
# ----------------------------------------------------------
echo Create group usbtacx
sudo addgroup usbtacx
echo add user pi to this group
sudo adduser pi usbtacx

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} pi user is granted access to usb after reboot, press Enter to continue: "
read reply

# Reboot to activate rule
sudo reboot now
