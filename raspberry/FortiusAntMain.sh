#!/bin/bash
#
# Goto startup directory, logfiles are created here
cd ~/FortiusANT/raspberry

echo Trashcan emptied - keep 1 month
find /home/pi/.local/share/Trash/ -name '*.log*'  -type f -mtime +30 -delete 2>/dev/null
find /home/pi/.local/share/Trash/ -name '*.json*' -type f -mtime +30 -delete 2>/dev/null
find /home/pi/.local/share/Trash/ -name '*.tcx*'  -type f -mtime +30 -delete 2>/dev/null

echo Log-files from previous session are deleted - keep two days
find ./ -name '*.log'  -type f -mtime +2 -delete 2>/dev/null
find ./ -name '*.json' -type f -mtime +2 -delete 2>/dev/null
find ./ -name '*.tcx'  -type f -mtime +2 -delete 2>/dev/null

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
