#!/bin/bash

echo For more information: refer the installation instruction on https://www.makersupplies.sg/blogs/tutorials/how-to-install-node-js-and-npm-on-the-raspberry-pi.
# ----------------------------------------------------------
# Raspberry Pi0: armv6l
#        others: armv7l
# ----------------------------------------------------------
NODEJS=node-v14.15.3-linux-`uname -m`

# ----------------------------------------------------------
# Go to Downloads
# ----------------------------------------------------------
cd ~/Downloads

# ----------------------------------------------------------
# Download node 14.15.3
# ----------------------------------------------------------
if [ -f "$NODEJS.tar.xz" ]; then
	rm $NODEJS.tar.xz
fi
if [ `uname -m` == 'armv6l' ]; then
    wget https://unofficial-builds.nodejs.org/download/release/v14.15.3/$NODEJS.tar.xz
else
    wget https://nodejs.org/dist/v14.15.3/$NODEJS.tar.xz
fi

# ----------------------------------------------------------
# Untar downloaded archive
# ----------------------------------------------------------
tar xf $NODEJS.tar.xz

# ----------------------------------------------------------
# Go into folder with unzipped files and install
# ----------------------------------------------------------
if [ -d "$NODEJS" ] ; then
	cd $NODEJS/
	# Copy folder content to 
	sudo cp -R * /usr/local/
	# Check if installed correctly
	echo Expected node version: v14.15.3
	node -v
	echo Expected npm  version: 6.14.9
	npm -v
fi

# ----------------------------------------------------------
# Cleanup
# ----------------------------------------------------------
cd ~/Downloads
rm $NODEJS.tar.xz
rm -rf $NODEJS

# ----------------------------------------------------------
# Next step is to grant the node binary cap_net_raw privileges,
# so it can start/stop BLE advertising without root access.
# ----------------------------------------------------------
sudo setcap cap_net_raw+eip $(eval readlink -f `which node`)

echo NodeJs is installed, press Enter to continue
read reply
