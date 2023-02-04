#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2022-03-03"
# 2022-03-03    added: UsePythonLogging
#               added: help_bb, modified help_b
# 2021-04-13    added: help_i
# 2021-03-24    added: help_L, help_O
# 2021-03-22    added: OnRaspberry; status leds also for GUI
# 2021-03-02    added: -l Raspberry status Leds
# 2021-02-25    if wxPython not present, disable GUI (UseGui = False)
# 2021-02-22    added: -B DeviceNumbers base #260
# 2021-02-11    added: -e homeTrainer
# 2021-01-18    help texts defined as 'constants' to be used for commandline.
# 2021-01-07    UseMultiProcessing moved here
# 2020-12-20    Constants moved to constants.py
#-------------------------------------------------------------------------------
mode_Basic          = 0     # Basic Resistance
mode_Power          = 1     # Target Power
mode_Grade          = 2     # Target Resistance

#-------------------------------------------------------------------------------
# 'directives' to exclude parts from the code
# For example for small footprint implementations
#-------------------------------------------------------------------------------
UseBluetooth        = True
UseGui              = True	    # Can be modified to force no-GUI
UseMultiProcessing  = True      # Production version can be either False or True
OnRaspberry         = True      # We're running on Raspberry Pi
UsePythonLogging    = True

try:
    from wx import EVT_CLOSE    # Just checking presence
except:
    UseGui          = False  	# no wx, no GUI

try:
                    # this module is a preinstalled module on Raspbian
    import gpiozero # pylint: disable=import-error
except:
    OnRaspberry     = False

#-------------------------------------------------------------------------------
# FortiusAnt states; as defined by @MeanHat
#-------------------------------------------------------------------------------
                        # Logfile content ~ messages from FortiusAnt[Body].py
faStarted       = 1     # FortiusANT started
faTrainer       = 2     # Connected to Tacx Trainer
faWait2Calibrate= 3     # G I V E   A   P E D A L   K I C K
faCalibrating   = 4     # C A L I B R A T I N G
# Bluetooth     = 5     # FortiusANT exchanges data with a bluetooth
faActivate      = 6     # BLE-devices are activated
faOperational   = 7     # Target=100W
faStopped       = 8     # Stopped
faDeactivated   = 9     # BLE-devices are deactivated
faTerminated    = 10    # Shutting down

#-------------------------------------------------------------------------------
# Miscellaneous
#-------------------------------------------------------------------------------
mile            = 1.609344  # km

#-------------------------------------------------------------------------------
# Commandline / Settings constants
#-------------------------------------------------------------------------------
Transmission = "34-50*x34-30-27-25-23-21-19*-17-15-13-11"      # No spaces here!

help_A = "Pedal Stroke Analysis."
help_B = "ANT DeviceNumber range Base, making multiple FortiusAnt sessions unique."
help_C = "ANT+ Control Command (#1/#2)"
help_D = "Select one specific antDongle (perhaps with a non-standard deviceID)."
help_G = "Modify the requested grade with a factor/factorDownhill."
help_H = "Pair this Heart Rate Monitor (0: any, -1: none). Tacx HRM is used if not specified."
help_L = "Raspberry GPIO pin Layout button/Tacx/Shutdown/Cadence/BLE/ANT."
help_M = "Run manual grade (ignore target from ANT+ Dongle)."
help_O = "Output to Raspberry mini display: console or display / rotation."
help_P = "Power mode has preference over Resistance mode (for 30 seconds)."
help_S = "Pair this Speed Cadence Sensor (0: default device)"
help_R = "The runoff procedure can be customized: maxSpeed/dip/minSpeed/targetTime/power."
help_a = "Automatically start; “Locate HW” and “Start” if the required devices were found."
help_b = "Advertise FortiusAnt as “FortiusAnt Trainer” on a Bluetooth Low Energy dongle, using nodejs."
help_bb= "Advertise FortiusAnt as “FortiusAnt Trainer” on a Bluetooth Low Energy dongle, using bless."
help_c = "Calibrate the rolling resistance for magnetic brake."
help_d = "Create logfile with debugging data."
help_e = "Operate as homeTrainer (excersize bike); up/down increments/decrements power with 10%%."
help_g = "Run with graphical user interface."
help_h = "Reserved for help!!"
help_i = "Imperial, speed in mph."
help_l = "Display status leds."
help_m = "Run manual power (ignore target from ANT+ Dongle)."
help_n = "Do not calibrate before start."
help_p = "Adjust target Power by multiplying by this factor for static calibration."
help_r = "Target Resistance = Target Power (to create power curve)."
help_s = "Simulate trainer to test ANT+ connectivity."
help_t = "Specify Tacx Type; if not specified, USB-trainers will be detected automatically."
help_T = "Transmission, default value = " + Transmission
help_x = "Export TCX file to upload into Strava, Sporttracks, Training peaks."

#-------------------------------------------------------------------------------
# define colours to use, in raspberry but perhaps also elsewhere
#-------------------------------------------------------------------------------
WHITE   = "#FFFFFF"
BLUE    = "#0000FF"
GREY    = "#7A7A7A"
AMBER   = "#fc8106"
GREEN   = "#00EE00"
RED     = "#FF3030"
BLACK   = "#000000"
FORTIUS = "#7894E3"            # 120,148,227
