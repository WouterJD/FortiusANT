#!/bin/bash
# https://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/
sudo apt-get install samba samba-common-bin

echo workgroup = WORKGROUP
echo wins support = yes
sudo nano /etc/samba/smb.conf

cp /etc/samba/smb.conf .
cat << EOF >> ./smb.conf
[PiShare]
 comment=Raspberry Pi Share
 path=/home/pi
 browseable=Yes
 writeable=Yes
 only guest=no
 create mask=0777
 directory mask=0777
 public=no
EOF
sudo cp smb.conf /etc/samba/smb.conf
rm      smb.conf

sudo smbpasswd -a pi

echo pi home folder is shared as [PiShare], press Enter to continue
read reply
