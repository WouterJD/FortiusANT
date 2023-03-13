#!/bin/bash

# Install packages for bless - they seem to be missing.
# See https://github.com/WouterJD/FortiusANT/issues/415
#
pip3 install lib_detect_testenv
pip3 install dbus_next
#
# Install packages for bleno - they seem to be missing.
# See https://github.com/WouterJD/FortiusANT/issues/412
#
pip3 install git+https://github.com/gwangyi/pysetupdi
# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} NodeJs is installed, press Enter to continue: "
read reply
