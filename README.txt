OVERVIEW
FortiusANT enables a usb-connected Tacx trainer to communicate with TrainerRoad or Zwift through ANT.

FortiusANT is running on the computer where the trainer is connected and broadcasts the ANT+ signal, using a dongle, to another computer or tablet. You might also run TrainerRoad or Zwift on the same computer and then two ANT+ dongles on the same computer are required.

Fortius ANT is a python-program, developed on Windows 7-64, for Tacx Fortius.
Of course it may run on other environments, feed-back is highly appreciated.

THANKS
FortiusANT is based upon the methods and architecture from 'antifier' (https://github.com/john-38787364/antifier)
and uses the interface description from 'totalreverse' (https://github.com/totalreverse/ttyT1941)
and without their work, FortiusANT would not have existed.

DESCRIPTION
TrainerRoad or Zwift (CTP=Cycling Training Programs) send commands to the Tacx Fortius (FE=Fitness Equipment) through ANT.
There are two modes: Power- or Ergo-mode and Resistance- or Slope-mode.

Resistance
It is important to understand that an FE only knows 'resistance' which is the torque to turn the braking axle.
From physics we know that power (Watt) = torque (Nm) * speed (km/hr).
For a given resistance, the power required is lineair with the speed (=cadence), provided you do not change gears.
Also, for a given resistance and cadence, the power required is lineair with the gear-ratio.

Power- or Ergo-mode
In Powermode the CTP sends the required power to the FE and regardless gear or cadence, the requested power is constant.
FortiusANT calculates the resistance as power/speed (with some constants applied).
Note that, if you change gears and/or cadence, the required power will remain equal because the resistance is adjusted.

Resistance mode
In resistance mode, FortuisANT receives the required grade from CTP. Grade may vary from -20% (downhill) to +20% (uphill).
FortiusANT must calculate the resistance to be sent to the FE.

A starting point could be 'calculate the power required to ride up a hill with a given grade with a weight of 90 kg (rider + bike) at a given speed'.
Input parameters are grade (from CTP), weight and speed (as measured by FE).
Result is Power and conversion to resistance is described above.

It poses some challenges: if zwift sends +20%, even driving slowly would require a hughe force at a low speed.
It's either the rider who cannot produce the power at that angle (even at a low speed of 5 km/hr)
or the Fortius does not work well, because low wheelspeeds are not it's specialty.

So another approach is chosen and two reference points defined:
- If riding uphill at 20%, the cadence will be low (50) and the requested power high (150% ftp).
- If riding downhill at -20%, the cadence will be high (100) and the requested power low (100% ftp).
Using those two powers, the reference resistances are calculated. These are constant for a specific rider and bicycle.
The target resistance, sent to FE, is calculated lineairly between these two points (0% being the midpoint).

To be able to calculate the speed at the two reference points, it is required to know the gear-ratio that will be used when doing exercises on the FE.
(speed = tyre-circumference * gear-ratio * cadence * some constants)
If you have a single-speed bicycle, the gear-ratio may be 50x15, and all you can do is vary the cadence (from 50...100).
If you have a compact with a 15/25 cassette, the gear-ratio varies from 50x15 ... 34x25. During the exercise you can vary cadence and ratio.

Note that, since the resistance for a given grade is calculated, that resistance remains constant.
The required power is lineair with the speed of the wheel and is influenced by cadence and gear-ratio.

Just start with zwift and then customize the behaviour to your needs as described in next section.

CUSTOMIZATION
For power-mode, no customizations are required. The CTP requires a power and the trainer is set to the corresponding resistance.
If you experience a too high resistance on your trainer, compared to your experience, you may use the -f powerfactor to adjust. -f 0.90 reduces force with 10% and -f 1.1 adds 10%.

For resistance-mode, you can customize the behaviour to your needs.
- specify ftp, your weight is communicated by CTP.
- specify your bike parameters: tyre circumference, chainring (front) and cassette (rear)
- specify the power-level you like. Default is 150/100; you could chose for 200/75.

REQUIREMENTS
- Windows or Linux PC
- ANT+ dongle to broadcast data - standard Garmin and Suunto dongles tested. Any dongle with hardware ID 0fcf:1009 or 0fcf:1008 should work
- Tacx Fortius trainer. So far tested with 1932 and 1942 head unit

INSTALLATION
Linux (Root required)
** to be supplied, since I have no linux environment to test

Windows:
You will need to reinstall your trainer as a libusb-win32 device:
1. Open device manager, right click on the device and click "Uninstall". It may be listed as a "Jungo" device 
(see http://www.tacxdata.com/files/support/Windows10driverissues.pdf - DO NOT RUN TacxDriversSetup.exe!)
2. Unplug the trainer, wait 5 seconds, and plug it back in again
3. Find it again (usually under other devices>VR-interface)
4. Right click and select "update driver software"
5. Select "Browse my computer for driver software"
6. Select "Let me select from a list of device drivers on my computer"
7. Select libusb-win32 devices
8. Select ANT USB Stick 2, then OK in the warning, then close

Download the python code for the application from:
https://github.com/WouterJD/FortiusANT

To install the required python libraries:
	pip install -r requirements.txt
download libusb-win32-devel-filter:
	https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/ 
	(or easier, use Zadig to install libusb driver)


USAGE: FortiusAnt.py [-h] [-a] [-b BICYCLE] [-d DEBUG] [-f FTP] [-g]
                     [-m] [-n] [-p FACTOR] [-r RESISTANCE] [-s]

Program to broadcast data from USB Tacx Fortius trainer, and to receive
resistance data for the trainer

optional arguments:
  -h,                   Show this help message and exit
  -a,                   Automatically start
  -b BICYCLE,           Bicycle definition, default=2.096,50/34,15/25
  -d DEBUG,             Show debugging data
  -f FTP, 		FTP of the rider, default=200
  -g,                   Run with graphical user interface
  -m,                   Run manual (ignore target from usbDongle)
  -n,                   Do not calibrate before start
  -p FACTOR,            Adjust target Power by multiplying by this factor
  -r RESISTANCE,        FTP percentages for resistance mode, default=150/100
  -s,                   Simulated trainer to test ANT+ connectivity

Examples:
FortiusAnt.py           FortiusANT is started without user-interface, -a is assumed
FortiusAnt.py -g -a     FortiusANT is started with user-interface and starts automatically
FortiusAnt.py -g -m     FortiusANT is started with user-interface
                            No CTP is required, power can be set using the console
                            Although intended for interface testing, you could do a manual ride this way
FortiusAnt.py -g -s     FortiusANT is started with user-interface
                            No FE is required, automatic response to CTP is generated
                            This is intended for interface testing

values
    BICYLE              Is the tyre circumference, the chain-ring and cassette of your bike
    DEBUG               Is a binary flag list what to write to the logfile, 0=nothing, 127=everything
    FTP                 Your functional threshold power
    FACTOR              Correction factor 0.9 ... 1.10
    RESISTANCE          The upper and lower ftp for resistance mode.


USER INTERFACE
After starting FortiusANT, you will see a user-interface with three buttons:
- Locate HW
- Runoff
- Start
- Stop

Locate HW
Checks for the presence of USB-trainer and ANT-dongle.
If succesfull, results are displayed and the button is disabled.

Rundown test
To ensure comparable training sessions, the trainer should provide the same relative resistance each time
1. Aim for about 100psi in tyre when cold
2. Warm up for 2-3 minutes to warm rubberer
3. Perform test- try for about a 7 second rundown from 40kph

Start
Pressing this button starts FortiusANT to listen to the USB-trainer and ANT-dongle and exchange info between them.

FortiusANT starts to calibrate the trainer (unless -n is specified).
Calibration means that the brake rotates the wheel at 20 km/hr and returns the resistance found.
As soon as the resistance is constant, the calibration stops.
The calibration time is at least 30 seconds (warming up the tyre) and stops when the resistance value is constant.

Note that the Fortius starts calibration when you turn the pedal as if starting to cycle, that is the manual action to take.

After calibration, the Fortius is ready for training.

Stop
Pressing this button stops the currently running process (runoff, calibration or operational mode).

Buttons on the Fortius console
There are four buttons: Cancel, Enter, Up, Down.

Cancel is activated in all modes.
If not in an active mode, Up/Down navigate through the menu, Enter activates the selected button and cancel exits FortiusANT.
In manual mode, Up/Down increase/decrease the resistance of the Fortius.