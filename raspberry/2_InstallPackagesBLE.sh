#!/bin/bash
sudo apt install -y build-essential bluetooth bluez libbluetooth-dev libudev-dev
sudo apt-get install -y libatlas-base-dev # for numpy, https://github.com/numpy/numpy/issues/11110

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} Packages are installed, press Enter to continue: "
read reply
