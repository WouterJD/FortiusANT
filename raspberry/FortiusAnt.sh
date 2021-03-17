#!/bin/bash
# autostart, bluetooth, gui, led, no ANT
~/FortiusANT/raspberry/FortiusAntMain.sh -a -b -g -l -D-1
# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry}  Press Enter to continue: "
read reply
