
# Headless Raspi
In these instructions the operating system is installed and configured for headless operation
Python software FortiusAnt downloaded (with LED support) and installed
Autostart set up
LEDs connected

Hardware Requirements:
1. PC
1. Software to write the operating system to the SD card. Download from this address https://www.raspberrypi.org/software/
1. Rasperry, preferably Raspi4, because it is much faster when compiling. (RP3 also works, Zero ???)
1. Fast SD card with at least 16GB. The install process is taking a long time
1. Network cable
1. ANT + dongle
1. TacxTrainer
1. Head Unit T1932
1. For Rouvy/Swift you need a tablet with an integrated ANT+ or a second ANT+ dongle for the mentioned PC

## Aim
Installation of the system without use of additional keyboard and screen.

With autostart and status LEDs.
With optional connection via VNC.
The graphical user interface still freezes. However, this does not matter because the headless operation still works perfectly.

## Preparation
Write the Raspberry PI OS (32-bit) image to SD card (1.1GB)
Remove the SD card and insert it again so that the PC reads the SD card partitions again.
The boot partition can be read normally by the PC.
To get access via SSH for the installation, the trick is a "dummy" file to activate SSH server.
Copy an empty file called "ssh" (without any extension) to the SD-card in the PC. You put it to the boot partition of the SD card.

Then put the card into the Raspi. Connect Power supply and network cable to the router.


Open the command window on the PC and enter the following command.
    ssh pi@raspberrypi   

password: `raspberry`

### Activate SSH Server
Since the dummy ssh file is automatically removed from the boot partition, the SSH server must be switched on permanently.
Start the raspi-config program and activate the SSH server

    sudo raspi-config

3 Interface Options    Configure connections to peripherals
P2 SSH         Enable/disable remote command line access using SSH 

### Install updates first

    sudo apt-get update
    sudo apt-get upgrade -y

### Diagnose the hardware Tacx and ANT+ Stick

    lsusb

…...
Bus 001 Device 006: ID 3561:1932  
Bus 001 Device 007: ID 0fcf:1009 Dynastream Innovations, Inc. ANTUSB-m Stick



In this example the first number is the Tacx Trainer, the second is the Antstick. The ID's can differ from model to model.
Create the file and adapt the ID's in the file (1932/1009) !!

    sudo nano /etc/udev/rules.d/ANT_USB.rules

Copy and paste the following text into nano editor.

    SUBSYSTEM=="usb", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1009", RUN+="/sbin/modprobe usbserial vendor=0x0fcf product= 0x1009",MODE="0666", OWNER="pi", GROUP="dialout"
    SUBSYSTEM=="usb", ATTRS{idVendor}=="3561", ATTRS{idProduct}=="1932",MODE="0666", OWNER="pi", GROUP="dialout"

Then exit with: Control X
Safe modified buffer? y
Complete with return

In the previous rules, the USB interfaces were assigned to the “dialout” user group. Therefore the user “pi” must be added to the Dialout group to be able to access this devices.

    sudo usermod -aG dialout pi 

Download and unzip the special "FortiusAnt" software

    wget https://github.com/decodeais/FortiusANT/archive/Raspi-Status-LED.zip -O tmp.zip
    unzip tmp.zip
    rm tmp.zip

### Yet another update for Python

    python3 -m pip install --upgrade pip


### Install the requirements for FortiusAnt
!!!!!!!! build wheel for wxPython takes hours (Raspi 4 2h, Raspi Zero is rumoret to take 23h).
If the Raspi hangs, "reboot" (command: sudo reboot) and repeat the step


Stop the unnecessary X-Server with the command "sudo pkill x". To save resources while compiling.

    sudo pkill x

It also helps to increase the size of the swapfile.
To do this, the following file must be edited.

    sudo nano /etc/dphys-swapfile 

`CONF_SWAPFILE=1000`  von 100auf 1000 ändern.

Call up the new setup to apply the change

    sudo dphys-swapfile setup 
    sudo /etc/init.d/dphys-swapfile stop 
    sudo /etc/init.d/dphys-swapfile start 


Since wxPython has to be recompiled for the Raspberry the required dev packages have to be installed. The FortiusAnt program could not be started with any older version of wxPython

    sudo apt-get update
    sudo apt-get install dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libwebkitgtk-dev libghc-gtk3-dev libwxgtk3.0-gtk3-dev -y
    sudo apt-get install python3.7-dev`
    pip3 install -r ~/FortiusANT-Raspi-Status-LED/pythoncode/requirements.txt 

## Configure autostart

Make the startupscript executable
    chmod +x /home/pi/FortiusANT-Raspi-Status-LED/FortiusAntHeadless.sh
    
Create a file with the editor and insert the code:

    sudo nano /etc/xdg/autostart/antifier_.desktop
 
Text einfügen
        
        [Desktop Entry]
        Type=Application
        Name=Antifier
        Comment=USB_Ant+
        NoDisplay=false
        Exec=/home/pi/FortiusANT-Raspi-Status-LED/FortiusAntHeadless.sh

# Connection of the LED's
Assignment of the IO's for the status LED's
   
           Raspberry Pi Pin  Pin Raspberry Pi
                     + 3,3 V           1  2   + 5 V
                   (SDA1) GPI_O2       3  4   + 5 V
    Button On/Off <----  (SCL1) GPI_O3 5  6   GND                    ---> GND Button On/Off
                   (GPIO_GCLK) GPI_O4  7  8   GPIO_14 (TXD0)
                     GND               9  10  GPIO_15 (RXD0)
                  (GPIO_GEN0) GPIO_17 11  12  GPIO_18 (GPIO_GEN1)
                  (GPIO_GEN2) GPIO_27 13  14  GND                    ---> GND
                  (GPIO_GEN3) GPIO_22 15  16  GPIO_23 (GPIO_GEN4)    ---> LED_Dongle
                     + 3,3 V          17  18  GPIO_24 (GPIO_GEN5)    ---> LED_Cadence
                  (SPI_MISO) GPIO_9   21  22  GPIO_25 (GPIO_GEN6)    ---> LED_Tacx
                  (SPI_SLCK) GPIO_11  23  24  GPIO_8 (SPI_CE0_N)
                     GND              25  26  GPIO_7 (SPI_CE1_N)
                  (für I2C) ID_SD     27  28  ID_SC (nur für I2C)
                     GPI_O5           29  30  GND
                     GPI_O6           31  32  GPIO_12
                     GPI_O13          33  34  GND
                     GPI_O19          35  36  GPIO_16
                     GPIO_26          37  38  GPIO 20
                     GND              39  40  GPIO 21
    
  
# Optional Addons

## VNC-Server enablen
Access to the graphical user interface via RealVNC.
Start the raspi-config program and activate the VNC server

    pi@raspberrypi:~ $ sudo raspi-config

3 Interface Options    Configure connections to peripherals
P3 VNC         Enable/disable graphical remote access using RealVNC  

Change monitor setting for VNC without monitor. Otherwise the VNC server will not work if no monitor is connected.


    Sudo nano /boot/config.txt
    
Remove the commet marks in the “/boot/config.txt” file for the following options.

    framebuffer_width=1280
    framebuffer_height=720
    hdmi_force_hotplug=1

## On/Off
The Raspi4 can be switched on and off optionally with a button.
The button must be switched between GPIO pin 3 and GND.
To do this, add this line to the Boot.txt file.

    dtoverlay=gpio-shutdown,gpio_pin=3, active_low=1,gpio_pull=up
