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
echo $?

#    Start FortiusANT
python3 ../pythoncode/FortiusAnt.py $@

echo Start standard Bluetooth Service
sudo service bluetooth start

echo FortiusAnt finished
