#!/bin/bash
# https://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/
sudo apt-get install samba samba-common-bin

# grep: 0 = line is selected, 1 = no lines, 2 = error
grep -c 'PiShare' /etc/samba/smb.conf
if [ $? == 1 ] ; then
    # workgroup = WORKGROUP
    # wins support = yes
    # sudo nano /etc/samba/smb.conf (if edited manually)

    cat /etc/samba/smb.conf | sed 's/workgroup = WORKGROUP/workgroup = WORKGROUP\n    wins support = yes/' >./smb.conf
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

    echo specify new password for remote access by user pi
    sudo smbpasswd -a pi
else
    echo PiShare already created
fi

echo pi home folder is shared as [PiShare], press Enter to continue
read reply
