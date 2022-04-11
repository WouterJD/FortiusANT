#!/bin/bash

echo Install development branch of bless; required April 2022.
pip install --force-reinstall git+https://github.com/kevincar/bless.git@develop

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} NodeJs is installed, press Enter to continue: "
read reply
