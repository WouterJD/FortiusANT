#!/bin/bash
cd $HOME
# ----------------------------------------------------------
# Install git
# ----------------------------------------------------------
sudo apt install git

# ----------------------------------------------------------
# Download (clone) FortuisAnt
# ----------------------------------------------------------
if [ -d "$HOME/FortiusANT" ] ; then
	echo "FortiusANT already present"
else
	git clone https://github.com/WouterJD/FortiusANT.git
fi

# ----------------------------------------------------------
# Install dependencies
# ----------------------------------------------------------
if [ `uname -m` == 'armv6l' ]; then
	# Requirements for Raspberry Pi0 will be installed
    pip3 install -r ~/FortiusANT/pythoncode/requirementsNoGUI.txt
else
	# Requirements will be installed (includes wxPython)
    pip3 install -r ~/FortiusANT/pythoncode/requirements.txt
fi

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} FortiusAnt and dependencies installed, press Enter to continue: "
read reply
