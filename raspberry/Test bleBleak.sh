#!/bin/bash
#

#sudo service bluetooth stop
#sudo hciconfig hci0 up

echo FortiusAnt module bleBleak
python3 ../pythoncode/bleBleak.py

#sudo service bluetooth start

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} Done, press Enter to continue: "
read x
