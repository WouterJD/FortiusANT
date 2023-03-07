#!/bin/bash

echo Install development branch of bless - required April-June and November 2022.
echo See https://github.com/WouterJD/FortiusANT/issues/402#issuecomment-1320887551
pip3 install --force-reinstall git+https://github.com/kevincar/bless.git@develop

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} NodeJs is installed, press Enter to continue: "
read reply
