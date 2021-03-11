#!/bin/bash
#
echo Stop standard Bluetooth Service
sudo service bluetooth stop
sudo service bluetooth status
#
echo Enable Bluetooth for FortiusAnt
sudo hciconfig hci0 up
if [ $? != 0 ] ; then
    Red='\033[0;31m'
    NC='\033[0m'
    printf "${Red} hciconfig failed, press enter to continue: ${NC}"; read x
else
    echo "hciconfig ok"
fi

echo Start standard Bluetooth Service
sudo service bluetooth start

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} Done, press Enter to continue: "
read x
