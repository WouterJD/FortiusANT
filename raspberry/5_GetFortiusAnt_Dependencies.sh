#!/bin/bash
cd $HOME
sudo apt install git
if [ -d "$HOME/FortiusANT" ] ; then
	echo "FortiusANT already present"
else
	git clone https://github.com/WouterJD/FortiusANT.git
fi

if [ `uname -m` == 'armv6l' ]; then
	# Requirements for Raspberry Pi0 will be installed
    pip3 install -r ~/FortiusANT/pythoncode/requirementsNoGUI.txt
else
	# Requirements will be installed (includes wxPython)
    pip3 install -r ~/FortiusANT/pythoncode/requirements.txt
fi

echo FortiusAnt dependencies installed, press Enter to continue
read reply
