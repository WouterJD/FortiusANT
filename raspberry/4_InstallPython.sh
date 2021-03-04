#!/bin/bash
SRC=https://drive.google.com/drive/folders/1owWkRTsvcnvq7ZSRc6zHS5dip2AMvW79
PYTHON=wxPython-4.1.1-cp37-cp37m-linux_armv7l.whl
GDRIVE=https://drive.google.com/file/d/1Uk1TSc6iLArx14QH8q85c9ytrw0IKLIn/view?usp=sharing

# Go to Downloads
cd ~/Downloads

# Download pre-build wxPython package to home folder.
# wget $SRC/$PYTHON
pip install gdown
/home/pi/.local/bin/gdown --id 1Uk1TSc6iLArx14QH8q85c9ytrw0IKLIn --output $PYTHON

# This wheel package works for an ARM7l CPU.
# Install package with
sudo pip3 install $PYTHON

# If you can not use the prebuild package, you need follow the install instructions
# below to build your own wxPython by replacing the version with 4.1.1
# (This can take up to 18 hours depending on the RaspberryPi you are using):
#
# https://www.marcdobler.com/2020/05/17/how-to-compile-and-install-wxpython-on-raspberry-pi/

# Cleanup
cd ~/Downloads
rm $PYTHON

echo Pre-built Python is installed, press Enter to continue
read reply
