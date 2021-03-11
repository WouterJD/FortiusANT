#!/bin/bash
# https://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/

# ----------------------------------------------------------
# Install samba
# ----------------------------------------------------------
sudo apt-get install samba samba-common-bin

# ----------------------------------------------------------
# Modify smb.conf:
#    workgroup = WORKGROUP
#    wins support = yes
# add [PiShare] section
# ----------------------------------------------------------
# grep: 0 = line is selected, 1 = no lines, 2 = error
grep -c 'PiShare' /etc/samba/smb.conf
if [ $? == 1 ] ; then
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

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} pi home folder is shared as [PiShare], press Enter to continue: "
read reply
