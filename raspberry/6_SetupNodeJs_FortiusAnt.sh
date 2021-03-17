#!/bin/bash
cd ~/FortiusANT/node/
npm install

echo ""
echo The npm install command has given several warnings which can be ignored.

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} FortiusAnt Bluetooth is installed, press Enter to continue: "
read reply
