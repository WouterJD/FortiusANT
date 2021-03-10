#!/bin/bash
#
echo Stop standard Bluetooth Service
sudo service bluetooth stop
sudo service bluetooth status
#
echo Enable Bluetooth for FortiusAnt
sudo hciconfig hci0 up
if [ $? != 0 ] ; then
	echo "hciconfig failed"
else
	echo "hciconfig ok"
fi

echo Start standard Bluetooth Service
sudo service bluetooth start

echo Done, press Enter to continue
read x
