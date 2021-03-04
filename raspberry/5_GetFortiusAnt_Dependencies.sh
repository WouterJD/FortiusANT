#!/bin/bash
cd $HOME
sudo apt install git
if [ -d "$HOME/FortiusANT" ] ; then
	echo "FortiusANT already present"
else
	git clone https://github.com/WouterJD/FortiusANT.git
fi
pip3 install -r ~/FortiusANT/pythoncode/requirements.txt

echo FortiusAnt dependencies installed, press Enter to continue
read reply
