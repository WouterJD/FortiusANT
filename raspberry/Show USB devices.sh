#!/bin/bash
# General info
lsusb
lsusb -t

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

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} Done, press Enter to continue: "
read x
