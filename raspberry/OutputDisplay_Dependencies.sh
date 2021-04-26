#!/bin/bash
cd $HOME
# ----------------------------------------------------------
# https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-setup
# Install OutputDisplay dependencies
# ----------------------------------------------------------
pip3 install adafruit-circuitpython-rgb-display
pip3 install --upgrade --force-reinstall spidev

# ----------------------------------------------------------
# DejaVu TTF Font
# ---------------
# Raspberry Pi usually comes with the DejaVu font already
# installed.
# But in case it didn't, you can run the following to install it:
# ----------------------------------------------------------
sudo apt-get install ttf-dejavu

# ----------------------------------------------------------
# Pillow Library
# --------------
# We also need PIL, the Python Imaging Library, to allow
# graphics and using text with custom fonts.
# There are several system libraries that PIL relies on, so
# installing via a package manager is the easiest way to
# bring in everything:
# ----------------------------------------------------------
sudo apt-get install python3-pil

# ----------------------------------------------------------
# NumPy Library
# -------------
# A recent improvement of the RGB_Display library makes use
# of NumPy for some additional speed. This can be installed with the following command:
# ----------------------------------------------------------
sudo apt-get install python3-numpy

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} OutputDisplay dependencies installed, press Enter to continue: "
read reply
