#!/bin/bash
# ----------------------------------------------------------
# Modify bluetooth.conf:
# ----------------------------------------------------------
# grep: 0 = line is selected, 1 = no lines, 2 = error
grep -c 'FortiusAntTrainer' /etc/dbus-1/system.d/bluetooth.conf
if [ $? == 1 ] ; then
    #cp /etc/dbus-1/system.d/bluetooth.conf                            ./bluetooth.conf.org
    cat /etc/dbus-1/system.d/bluetooth.conf | sed 's/<\/busconfig>//' >./bluetooth.conf
    cat << EOF >> ./bluetooth.conf
  <policy user="pi">
    <allow own="org.bluez.FortiusAntTrainer"/>
    <allow send_destination="org.bluez.FortiusAntTrainer"/>
  </policy>
</busconfig>
EOF
    sudo cp bluetooth.conf /etc/dbus-1/system.d/bluetooth.conf
    rm      bluetooth.conf

else
    echo Bluetooth access already granted
fi

# ----------------------------------------------------- Done
Raspberry='\033[0;35m'
printf "${Raspberry} pi is now allowed to use Bluetooth Low Energy, press Enter to continue: "
read reply
