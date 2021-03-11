#!/bin/bash
#
# Goto startup directory, logfiles are created here
cd ~/FortiusANT/raspberry

echo Log-files from previous session are deleted
rm *.log *.json *.tcx 2>/dev/null

echo Stop standard Bluetooth Service
sudo service bluetooth stop
echo Enable Bluetooth for FortiusAnt
sudo hciconfig hci0 up
if [ $? != 0 ] ; then
    Red='\033[0;31m'
    NC='\033[0m'
    printf "${Red} hciconfig failed, press enter to continue: ${NC}"; read x
fi

#    Start FortiusANT
python3 ../pythoncode/FortiusAnt.py $@

echo Start standard Bluetooth Service
sudo service bluetooth start

echo FortiusAnt finished
