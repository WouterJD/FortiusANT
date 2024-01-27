#---------------------------------------------------------------------------
# Version info
#---------------------------------------------------------------------------
__version__ = "2024-01-22"
# 2024-01-23    #381/1 Weight should be positive and <= 255
#               #381/2 HRM is searched for infinitely
#                       This is implemented for all slaves, for consistency.
#                       I hope it improves quality, if not clearly marked to remove.
#               #381/3 HRM is transmitted through FE-C
# 2023-03-15    Even when there is no ANT-dongle, the message queue must be
#               created, so that MessageQueueSize() returns zero.
# 2022-08-22    Data from the ANT dongle is stored in a queue.
#               This class only adds messages to the queue, the user removes
#               the messages. Messages are never skipped anymore.
# 2022-08-10    Steering merged from marcoveeneman and switchable's code
# 2021-12-03    When pairing, TransmissionType must be zero (TransmissionType_Pairing)
#               this became apparent when using another make of HRM, returning
#               a TransmissionType=207, not being found using TransmissionType_IC.
#               When using Garmin HRM, there was not problem.
#               This is applied to SlaveHRM_ChannelConfig (and SCS, Trainer).
#               It's not applied to for VTX, GNS, VTU, since cannot be tested,
#               avoiding to cause side-effects.
#               Most likely, those devices always match the used TransmissionType.
# 2021-04-15    flush improved, #286
# 2021-04-01    DongleReconnected WAS initially True but should be False
#               (Although the field should only be used when AntDongle.OK = True)
# 2021-03-03    Message in ...Config() function only given if self.ConfigMsg:
#               so that it's given only once.
#               When -D -1 is specified, we don't even look for an ANTdongle
# 2021-02-22    devAntDongle.read() given variable timeout
#               devAntDongle.write() sends all messages and then does ONE read-loop
# 2021-02-19    msgPage16_PowerOnly, msgPage25_TrainerData: CurrentPower must be > 0
# 2021-02-11    Vortex HU serial/mode page added
#               Vortex brake search time-out disabled
# 2020-12-30    Tacx Genius/Bushido data pages, constants and channel
#               configuration implemented
#               Added: msg44_ChannelSearchTimeout
# 2020-12-28    msgPage16_GeneralFEdata commented
# 2020-12-14    ANT+ Control command implemented
# 2020-11-18    Retry added when intiating USB dongle as suggested by @martin-vi
# 2020-11-03    If there is no dongle, Write() and Read() become completely
#               dummy, so that we can run without ANTdongle.
# 2020-06-16    Added: When pairing with a master, the master-id is printed
# 2020-06-12    Added: BikePowerProfile and SpeedAndCadenceSensor final
# 2020-06-10    Changed: ChannelPeriods defined decimal, like ANT+ specification
# 2020-06-09    Added: SpeedAndCadenceSensor 
# 2020-05-26    Added: msgPage71_CommandStatus
# 2020-05-25    Changed: DongleDebugMessage() adjusted with some more info
# 2020-05-20    Changed: DecomposeMessage() made foolproof against wrong data
#                        msgPage172_TacxVortexHU_ChangeHeadunitMode wrong page
#                        DongleDebugMessage; VHU pages added
#               Added:  Headunit mode constants
# 2020-05-14    Added: msgPage000_TacxVortexHU_NoPowerOff
#                      msgPage172_TacxVortexHU_ChangeHeadunitMode
#                      msgUnpage221_TacxVortexHU_ButtonPressed
#               Changed: msgID_ChannelID issued in SlaveXXX_ChannelConfig
# 2020-05-13    Added:    msgUnpage50_WindResistance
#               Modified: msgUnpage51_TrackResistance
#               #55 Support for Data Page 50 - Wind Resistance
#               #56 Support for Data Page 51 - Coefficient of Rolling Resistance
# 2020-05-08    Linux: detach_kernel_driver added 
# 2020-05-07    clsAntDongle encapsulates all functions
# 2020-05-07    pylint error free
# 2020-05-01    Added: SlaveVHU_ChannelConfig()
#               Disabled: SCS because of lack of channel numbers
# 2020-04-29    msgUnpage00_TacxVortexDataSpeed, speed corrected (0x03ff)
# 2020-04-28    crash when checksum incorrect; conditions were in wrong sequence
#               causing   IndexError: array index out of range
#                   in    while trv[skip] != 0xa4 and skip < len(trv):
# 2020-04-22    channel numbers changed into 0...7
# 2020-04-22    unmsg51_ChannelID() returned incorrect TransmissionType
#               channel_VTX = 4 (was 5, not intended)
# 2020-04-20    Tacx i-Vortex data pages implemented, Command+Subcommand
# 2020-04-18    Changed: Vortex frequency=2466
#                        Calibrate() creates two networks, the default and
#                           an extra network for Tacx i-Vortex
# 2020-04-17    Added: i-Vortex (VTX)
# 2020-04-17    Added: Page54 FE_Capabilities to support Golden Cheetah
# 2020-04-17    Added: msgID_UnassignChannel
# 2020-04-16    Write() replaced by Console() where needed
# 2020-04-15    Exception handling on antDongle.read() improved
# 2020-04-15    Logfile extended for .write and .read
# 2020-04-14    Error handling on GetDongle() improved
#               OS-dependencies removed (since works for Windows, Linux and Mac)
# 2020-04-13    Some print() replaced by logfile.Write().
#               Dongle printed to logfile
# 2020-04-12    TimeoutError-handling improved; Macintosh returns "timed out".
#               Old code is removed, it appears obsolete for all platforms
# 2020-03-31    The grade as provided by Zwift or Rouvy was multiplied by 2.5
#               resulting in far too steep slopes. Removed.
# 2020-03-09    GetDongle() improved; multiple dongles of same type supported
# 2020-02-26    Implementation restriction:
#               When two same ANT dongles are in the system, always the first
#               is found and can be used (or is in use). Should be changed.
# 2020-02-26    msgID_BurstData added (restricted implementation)
# 2020-02-25    Tacx Neo constants used, trying to get Tacx Desktop App to pair
#               with ExplorAnt(simulating) or FortiusAnt. No luck yet.
# 2020-02-13    msgPage80_ManufacturerInfo and msgPage81_ProductInformation
#                   now expect parameters in stead of using fixed constants
#               todo: msgPage82_BatteryStatus
# 2020-02-12    Different channels used for HRM and HRM_s (SCS and SCS_s)
#               so that ExplorANT can use both simultaneously
#               ResetDongle() used for reset + 500ms wait after reset before
#                   next actions, seems to imrpove pairing behaviour
#               Calibrate() changed with respect to reset-dongle
# 2020-02-10    SCS added (example code, not tested)
# 2020-02-02    Function EnumerateAll() added, GetDongle() has optional input
#               Function SlaveTrainer_ChannelConfig(), SlaveHRM_ChannelConfig()
#                   for device pairing, with related constants
#               Improved logging, major overhaul
# 2020-01-23    OS-dependant code seems unnecessary; disabled
# 2020-01-22    Error handling in GetDongle made similar to GetTrainer()
# 2020-01-15    hexlify/unhexlify removed, buffers are all of type 'bytes' now
# 2019-12-30    strings[] replaced by messages[]
#---------------------------------------------------------------------------
import binascii
import glob
import os
import platform
from pyexpat.errors import messages
import re
if platform.system() == 'False':
    import serial                   # pylint: disable=import-error
import queue
import struct
import threading
import time
import usb.core

import debug
import logfile
import structConstants      as sc

import FortiusAntCommand    as cmd

#---------------------------------------------------------------------------
# Our own choice what channels are used
#
# Note that a running program cannot be slave AND master for same device
# since the channels are statically assigned!
#---------------------------------------------------------------------------
# M A X #   c h a n n e l s   m a y   b e   8   s o   b e w a r e   h e r e !
#---------------------------------------------------------------------------
channel_FE          = 0           # ANT+ channel for Fitness Equipment
channel_FE_s        = channel_FE  # slave=Cycle Training Program

channel_HRM         = 1           # ANT+ channel for Heart Rate Monitor
channel_HRM_s       = channel_HRM # slave=display or Cycle Training Program

channel_PWR         = 2           # ANT+ Channel for Power Profile

channel_SCS         = 3           # ANT+ Channel for Speed Cadence Sensor
channel_SCS_s       = channel_SCS # slave=display or Cycle Training Program

channel_VTX         = 4           # ANT+ Channel for Tacx Vortex
channel_VTX_s       = channel_VTX # slave=Cycle Training Program

channel_VHU_s       = 5           # ANT+ Channel for Tacx Vortex Headunit
                                  # slave=Cycle Training Program
channel_GNS_s       = channel_VHU_s # ANT+ Channel for Tacx Genius

channel_BHU_s       = channel_VHU_s # ANT+ Channel for Tacx Bushido Headunit

channel_CTRL        = 6           # ANT+ Channel for Remote Control

channel_BLTR_s      = 7           # ANT Channel for Tacx BlackTrack

#---------------------------------------------------------------------------
# Vortex Headunit modes
#---------------------------------------------------------------------------
VHU_Normal          = 0        # Headunit commands the Vortex trainer
VHU_ResetDistance   = 1        # Reset odometer on HU
VHU_Training        = 2        # Headunit controls the Vortex and
                               #        FortiusANT TargetPower seems ignored.
VHU_TrainingPause   = 3        # Displays "start cycling"
VHU_PCmode          = 4        # Headunit only sends buttons to slave (FortiusANT)

#---------------------------------------------------------------------------
# Vortex head unit buttons
#---------------------------------------------------------------------------
VHU_Button_None  = 0x0
VHU_Button_Left  = 0x1
VHU_Button_Up    = 0x2
VHU_Button_Enter = 0x3
VHU_Button_Down  = 0x4
VHU_Button_Right = 0x5

#---------------------------------------------------------------------------
# Vortex alarm bits
#---------------------------------------------------------------------------
VTX_Alarm_WrongMainsVoltage     = 0x0001
VTX_Alarm_TemperatureHigh       = 0x0002
VTX_Alarm_NoBrakeCoils          = 0x0004

#---------------------------------------------------------------------------
# Tacx Genius brake modes
#---------------------------------------------------------------------------
GNS_Mode_Slope      = 0x00
GNS_Mode_Power      = 0x01
GNS_Mode_Heartrate  = 0x02

#---------------------------------------------------------------------------
# Tacx Genius calibration actions
#---------------------------------------------------------------------------
GNS_Calibration_Action_Stop         = 0x00
GNS_Calibration_Action_Start        = 0x01
GNS_Calibration_Action_Request_Info = 0x02

#---------------------------------------------------------------------------
# Tacx Genius calibration status
#---------------------------------------------------------------------------
GNS_Calibration_State_Stopped       = 0x00
GNS_Calibration_State_Started       = 0x01
GNS_Calibration_State_Running       = 0x02
GNS_Calibration_State_Calibrated    = 0x03
GNS_Calibration_State_Uncalibrated  = 0x04
GNS_Calibration_State_Value_Error   = 0x81
GNS_Calibration_State_Cadence_Error = 0x82
GNS_Calibration_State_Speed_Error   = 0x83
GNS_Calibration_State_Timeout       = 0x83
GNS_Calibration_State_Torque_Error  = 0x83

#---------------------------------------------------------------------------
# Tacx Genius alarm bits
#---------------------------------------------------------------------------
GNS_Alarm_Overtemperature       = 0x0001
GNS_Alarm_Overvoltage           = 0x0004
GNS_Alarm_GenericError          = 0x0008
GNS_Alarm_Overcurrent           = 0x0020
GNS_Alarm_SpeedTooHigh          = 0x0080
GNS_Alarm_Undervoltage          = 0x0100
GNS_Alarm_DownhillLimited       = 0x4000
GNS_Alarm_CommunicationError    = 0x8000

#---------------------------------------------------------------------------
# Tacx Bushido head unit alarm bits
#---------------------------------------------------------------------------
BHU_Alarm_Temperature_1      = 0x0001
BHU_Alarm_Temperature_2      = 0x0002
BHU_Alarm_Temperature_3      = 0x0003
BHU_Alarm_Temperature_4      = 0x0004
BHU_Alarm_Temperature_5      = 0x0005
BHU_Alarm_Overvoltage        = 0x0008
BHU_Alarm_Overcurrent_1      = 0x0010
BHU_Alarm_Overcurrent_2      = 0x0020
BHU_Alarm_SpeedTooHigh       = 0x0080
BHU_Alarm_Undervoltage       = 0x0100
BHU_Alarm_CommunicationError = 0x8000

DeviceNumber_EA     = 57590    # short Slave device-number for ExplorANT
DeviceNumber_FE     = 57591    #       These are the device-numbers FortiusANT uses and
DeviceNumber_HRM    = 57592    #       slaves (TrainerRoad, Zwift, ExplorANT) will find.
DeviceNumber_VTX    = 57593    #
DeviceNumber_VHU    = 57594    #
DeviceNumber_SCS    = 57595    #
DeviceNumber_PWR    = 57596    #
DeviceNumber_CTRL   = 57597    #
def DeviceNumberBase(base):
    global DeviceNumber_EA,  DeviceNumber_FE,  DeviceNumber_HRM, DeviceNumber_VTX, \
           DeviceNumber_VHU, DeviceNumber_SCS, DeviceNumber_PWR, DeviceNumber_CTRL
    DeviceNumber_EA     = base + 0
    DeviceNumber_FE     = base + 1
    DeviceNumber_HRM    = base + 2
    DeviceNumber_VTX    = base + 3
    DeviceNumber_VHU    = base + 4
    DeviceNumber_SCS    = base + 5
    DeviceNumber_PWR    = base + 6
    DeviceNumber_CTRL   = base + 7

ModelNumber_FE      = 2875     # short antifier-value=0x8385, Tacx Neo=2875
SerialNumber_FE     = 19590705 # int   1959-7-5
HWrevision_FE       = 1        # char
SWrevisionMain_FE   = 1        # char
SWrevisionSupp_FE   = 1        # char

ModelNumber_HRM     = 0x33     # char  antifier-value
SerialNumber_HRM    = 5975     # short 1959-7-5
HWrevision_HRM      = 1        # char
SWversion_HRM       = 1        # char

ModelNumber_CTRL     = 1234     # short
SerialNumber_CTRL    = 19590709 # int   1959-7-9
HWrevision_CTRL      = 1        # char
SWrevisionMain_CTRL  = 1        # char
SWrevisionSupp_CTRL  = 1        # char

ModelNumber_PWR      = 2161     # Garmin Vector 2 (profile.xlsx, garmin_product)
SerialNumber_PWR     = 19570702 # int   1957-7-2
HWrevision_PWR       = 1        # char
SWrevisionMain_PWR   = 1        # char
SWrevisionSupp_PWR   = 1        # char

if False:                      # Tacx Neo Erik OT; perhaps relevant for Tacx Desktop App
                               # because TDA does not want to pair with FortiusAnt...
    DeviceNumber_FE = 48365
    SerialNumber_FE = 48365

#---------------------------------------------------------------------------
# D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
# 5.2.1 Channel Type
# 5.3   Establishing a channel (defines master/slave)
# 9.3   ANT Message summary
#---------------------------------------------------------------------------
ChannelType_BidirectionalReceive        = 0x00          # Slave
ChannelType_BidirectionalTransmit       = 0x10          # Master

ChannelType_UnidirectionalReceiveOnly   = 0x40          # Slave
ChannelType_UnidirectionalTransmitOnly  = 0x50          # Master

ChannelType_SharedBidirectionalReceive  = 0x20          # Slave
ChannelType_SharedBidirectionalTransmit = 0x30          # Master

msgID_RF_EVENT                          = 0x01

msgID_ANTversion                        = 0x3e
msgID_BroadcastData                     = 0x4e
msgID_AcknowledgedData                  = 0x4f
msgID_ChannelResponse                   = 0x40
msgID_Capabilities                      = 0x54

msgID_UnassignChannel                   = 0x41
msgID_AssignChannel                     = 0x42
msgID_ChannelPeriod                     = 0x43
msgID_ChannelSearchTimeout              = 0x44
msgID_ChannelRfFrequency                = 0x45
msgID_SetNetworkKey                     = 0x46
msgID_ResetSystem                       = 0x4a
msgID_OpenChannel                       = 0x4b
msgID_RequestMessage                    = 0x4d

msgID_ChannelID                         = 0x51          # Set, but also receive master channel - but how/when?
msgID_ChannelTransmitPower              = 0x60

msgID_StartUp                           = 0x6f

msgID_BurstData                         = 0x50

# profile.xlsx: antplus_device_type
DeviceTypeID_antfs                      =  1
DeviceTypeID_bike_power                 = 11
DeviceTypeID_environment_sensor_legacy  = 12
DeviceTypeID_multi_sport_speed_distance = 15
DeviceTypeID_control                    = 16
DeviceTypeID_fitness_equipment          = 17
DeviceTypeID_blood_pressure             = 18
DeviceTypeID_geocache_node              = 19
DeviceTypeID_light_electric_vehicle     = 20
DeviceTypeID_env_sensor                 = 25
DeviceTypeID_racquet                    = 26
DeviceTypeID_control_hub                = 27
DeviceTypeID_muscle_oxygen              = 31
DeviceTypeID_bike_light_main            = 35
DeviceTypeID_bike_light_shared          = 36
DeviceTypeID_exd                        = 38
DeviceTypeID_bike_radar                 = 40
DeviceTypeID_bike_aero                  = 46
DeviceTypeID_weight_scale               =119
DeviceTypeID_heart_rate                 =120
DeviceTypeID_bike_speed_cadence         =121
DeviceTypeID_bike_cadence               =122
DeviceTypeID_bike_speed                 =123
DeviceTypeID_stride_speed_distance      =124

# Manufacturer ID       see FitSDKRelease_21.20.00 profile.xlsx
Manufacturer_garmin                     =  1
Manufacturer_dynastream	                = 15
Manufacturer_tacx                       = 89
Manufacturer_trainer_road	            =281
Manufacturer_dev                        =255

DeviceTypeID_FE         = DeviceTypeID_fitness_equipment
DeviceTypeID_HRM        = DeviceTypeID_heart_rate
DeviceTypeID_PWR        = DeviceTypeID_bike_power
DeviceTypeID_SCS        = DeviceTypeID_bike_speed_cadence
DeviceTypeID_CTRL       = DeviceTypeID_control
DeviceTypeID_VTX        = 61            # Tacx Vortex
DeviceTypeID_GNS        = 83            # Tacx Genius
DeviceTypeID_BHU        = 82            # Tacx Bushido head unit
# 0x3d  according TotalReverse
DeviceTypeID_VHU        = 0x3e          # Thanks again to TotalReverse
# https://github.com/WouterJD/FortiusANT/issues/46#issuecomment-616838329
DeviceTypeID_BLTR       = 84            # Tacx BlackTrack steering unit

TransmissionType_Pairing=    0          # See ANT+ HRM  Device Profile D00000693 5.1
                                        # See ANT+ FE-C Device Profile D00001231 7.1
                                        # See ANT+ FE-C Device Profile D00001163 7.1.1
TransmissionType_IC     = 0x01          # 5.2.3.1   Transmission Type
TransmissionType_IC_GDP = 0x05          #           0x01 = Independant Channel
                                        #           0x04 = Global datapages used
TransmitPower_0dBm      = 0x03          # 9.4.3     Output Power Level Settings
RfFrequency_2457Mhz     =   57          # 9.5.2.6   Channel RF Frequency
RfFrequency_2460Mhz     =   60          # used for Tacx Genius/Bushido
RfFrequency_2466Mhz     =   66          # used for Tacx Vortex only
RfFrequency_2478Mhz     = 0x4e          # used for Tacx Vortex Headunit
#---------------------------------------------------------------------------
# c l s A n t D o n g l e
#---------------------------------------------------------------------------
# function  Encapsulate all operations required on the AntDongle
#
# attributes
#
# functions __init__
#
#---------------------------------------------------------------------------
class clsAntDongle():
    devAntDongle        = None      # There is no dongle connected yet
    ConfigMsg           = True
    OK                  = False
    DeviceID            = None
    Message             = ''
    Cycplus             = False
    DongleReconnected   = False     # So can be used even when OK=False

    # Messages are store in a queue since 22-8-2022
    _MessageQueue       = None
    _MessageLock        = None

    # Read messages in a separate thread
    UseThread           = True     # "Compile time" flag to use threading
    ThreadActive        = False     # "Run time" flag that threading active
    MessageThread       = None      # The thread handle

    #-----------------------------------------------------------------------
    # _ _ i n i t _ _
    #-----------------------------------------------------------------------
    # Function  Create the class and try to find a dongle
    #-----------------------------------------------------------------------
    def __init__(self, DeviceID = None):
        self.DeviceID      = DeviceID
        self._MessageQueue = queue.Queue()      # Here messages are stored
        self._MessageLock  = threading.Lock()   # This lock protects the queue
        self.OK            = True               # Otherwise we're disabled!!
        if self.DeviceID == -1:
            self.OK      = False                # No ANT dongle wanted
            self.Message = "No ANT"
        else:
            self.OK      = self.__GetDongle()

    #-----------------------------------------------------------------------
    # G e t D o n g l e
    #-----------------------------------------------------------------------
    # input     self.DeviceID               If a specific dongle is selected
    #
    # function  find antDongle (defined types only)
    #
    # output    self.devAntDongle           False if failed
    #           self.Message                Readable end-user message
    #
    # returns   True/False
    #-----------------------------------------------------------------------
    def __GetDongle(self):
        self.Message            = ''
        self.Cycplus            = False
        self.DongleReconnected  = False

        self.StopReadThread()           # Stop reading in a thread

        if self.DeviceID == None:
            dongles = { (4104, "Suunto"), (4105, "Garmin"), (4100, "Older") }
        else:
            dongles = { (self.DeviceID, "(provided)")                       }

        #-------------------------------------------------------------------
        # https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
        #-------------------------------------------------------------------
        found_available_ant_stick = False
        #-------------------------------------------------------------------
        # Check the known (and supported) dongle types
        # Removed: if platform.system() in [ 'Windows', 'Darwin', 'Linux' ]:
        #-------------------------------------------------------------------
        for dongle in dongles:
            ant_pid = dongle[0]
            if debug.on(debug.Function): logfile.Write (\
                "GetDongle - Check for dongle %s %s" % (ant_pid, dongle[1]))
            try:
                #-----------------------------------------------------------
                # Find the ANT-dongles of this type
                # Note: filter on idVendor=0x0fcf is removed
                #-----------------------------------------------------------
                self.Message = "No (free) ANT-dongle found"
                devAntDongles = usb.core.find(find_all=True, idProduct=ant_pid)
            except Exception as e:
                logfile.Console("GetDongle - Exception: %s" % e)
                if "AttributeError" in str(e):
                    self.Message = "GetDongle - Could not find dongle: " + str(e)
                elif "No backend" in str(e):
                    self.Message = "GetDongle - No backend, check libusb: " + str(e)
                else:
                    self.Message = "GetDongle: " + str(e)
            else:
                #-----------------------------------------------------------
                # Try all dongles of this type (as returned by usb.core.find)
                #-----------------------------------------------------------
                for self.devAntDongle in devAntDongles:
                    if debug.on(debug.Function):
                        s = "GetDongle - Try dongle: manufacturer=%7s, product=%15s, vendor=%6s, product=%6s(%s)" %\
                            (self.devAntDongle.manufacturer, self.devAntDongle.product, \
                            hex(self.devAntDongle.idVendor), hex(self.devAntDongle.idProduct), \
                            self.devAntDongle.idProduct)
                        logfile.Console(s.replace('\0',''))
                    if debug.on(debug.Data1 | debug.Function):
                        logfile.Print (self.devAntDongle)
                        # prints "DEVICE ID 0fcf:1009 on Bus 000 Address 001 ================="
                        # But .Bus and .Address not found for logging
                    #-------------------------------------------------------
                    # Initialize the dongle
                    #-------------------------------------------------------
                    try:                                   # check if in use
                        #-------------------------------------------------------
                        # As suggested by @ElDonad Elie Donadio
                        #-------------------------------------------------------
                        if os.name == 'posix':
                            if debug.on(debug.Function): logfile.Write("GetDongle - Detach kernel drivers")
                            for config in self.devAntDongle:
                                for i in range(config.bNumInterfaces):
                                    if self.devAntDongle.is_kernel_driver_active(i):
                                        self.devAntDongle.detach_kernel_driver(i)
                        #-------------------------------------------------------
                        if debug.on(debug.Function): logfile.Write ("GetDongle - Set configuration")
                        self.devAntDongle.set_configuration()

                        for _ in range(2):
                            #---------------------------------------------------
                            # If not succesfull immediatly, repeat this
                            # As suggested by @martin-vi
                            #---------------------------------------------------
                            reset_string = msg4A_ResetSystem()  # reset string probe
                                                                # same as ResetDongle()
                                                                # done here to have explicit error-handling.
                            if debug.on(debug.Function): logfile.Write ("GetDongle - Send reset string to dongle")
                            self.devAntDongle.write(0x01, reset_string)
                            time.sleep(0.500)                           # after reset, 500ms before next action


                            if debug.on(debug.Function): logfile.Write ("GetDongle - Read answer")
                            self.Read(False)


                            if debug.on(debug.Function): logfile.Write ("GetDongle - Check for an ANT+ reply")
                            self.Message = "No expected reply from dongle"
                            while self.MessageQueueSize() > 0:
                                s = self.MessageQueueGet()
                                synch, length, id, _info, _checksum, _rest, _c, _d = DecomposeMessage(s)
                                if synch==0xa4 and length==0x01 and id==0x6f:
                                    found_available_ant_stick = True
                                    self.Message = "Using %s dongle" %  self.devAntDongle.manufacturer # dongle[1]
                                    self.Message = self.Message.replace('\0','')          # .manufacturer is NULL-terminated
                                    if 'CYCPLUS' in self.Message:
                                        self.Cycplus = True

                            #---------------------------------------------------
                            # If found, then done - else retry to reset
                            #---------------------------------------------------
                            if found_available_ant_stick: break

                    except usb.core.USBError as e:                  # cannot write to ANT dongle
                        if debug.on(debug.Data1 | debug.Function):
                            logfile.Write ("GetDongle - Exception: %s" % e)
                        self.Message = "GetDongle - ANT dongle in use"

                    except Exception as e:
                        logfile.Console("GetDongle - Exception: %s" % e)
                        self.Message = "GetDongle: " + str(e)

                    #-------------------------------------------------------
                    # If found, don't try the next ANT-dongle of this type
                    #-------------------------------------------------------
                    if found_available_ant_stick: break

            #---------------------------------------------------------------
            # If found, don't try the next type
            #---------------------------------------------------------------
            if found_available_ant_stick: break

        #-------------------------------------------------------------------
        # Done
        # If no success, invalidate devAntDongle
        #-------------------------------------------------------------------
        if not found_available_ant_stick: self.devAntDongle = None
        if debug.on(debug.Function): logfile.Write ("GetDongle() returns: " + self.Message)
        return found_available_ant_stick

    #-----------------------------------------------------------------------
    # M e s s a g e Q u e u e   P u t   /   G e t   /   S i z e
    #-----------------------------------------------------------------------
    # input     self._MessageLock
    #           self._MessageQueue
    #
    # function  Put: add message to   queue, protected by lock
    #           Get: get message from queue, protected by lock
    #
    #           The lock is used, so that Put/Get can be called from 
    #           different threads.
    #
    # output    self._MessageQueue
    #
    # returns   Put: None
    #           Get: the next message from the queue (or None)
    #-----------------------------------------------------------------------
    def MessageQueuePut(self, message):
        if debug.on(debug.Function): logfile.Write ("MessageQueuePut(%s)" % logfile.HexSpace(message))
        self._MessageLock.acquire()
        self._MessageQueue.put(message)
        self._MessageLock.release()

    def MessageQueueGet(self):
        self._MessageLock.acquire()
        if self.MessageQueueSize():
            message = self._MessageQueue.get(block=False, timeout=1)	# No timeout in the lock!!
            self._MessageQueue.task_done()
        else:
            message = None
        self._MessageLock.release()
        if debug.on(debug.Function): logfile.Write ("MessageQueueGet() returns %s" % logfile.HexSpace(message))
        return message

    def MessageQueueSize(self):
        return self._MessageQueue.qsize()

    #-----------------------------------------------------------------------
    # W r i t e
    #-----------------------------------------------------------------------
    # input     messages    an array of data-buffers
    #
    #           receive     after sending the data, receive all responses
    #           drop        the caller does not process the returned data
    #
    #           flush       read all available messages
    #                       This flag is provided True on the first call in
    #                       a loop, so that write() does not run into a
    #                       filled ANT-dongle (device driver) because many
    #                       messages are waiting to be processed.
    #                       Default = True, which is safe behaviour
    #                       2021-04-15 initial flush only done when data is
    #                                  to be received, messages were lost!
    #
    # function  write all strings to antDongle
    #           read responses from antDongle
    #
    # returns   None; data is in the Queue. QueueSize() returns nr messages.
    #-----------------------------------------------------------------------
    def Write(self, messages, receive=True, drop=True, flush=True):
        if self.OK:                      # If no dongle ==> no action at all
            #---------------------------------------------------------------
            # Read all available messages first, it seems required to be
            # able to write (if too many messages pending: Write exception,
            # message lost)
            #---------------------------------------------------------------
            if receive and flush:
                self.Read(drop)   # Flush -> default timeout = proven!

            for message in messages:
                #-----------------------------------------------------------
                # Logging
                #-----------------------------------------------------------
                DongleDebugMessage("Dongle    send   :", message)
                if debug.on(debug.Performance):
                    logfile.Write('devAntDongle.write(0x01,%s) ...' \
                                                    % logfile.HexSpace(message))
                #-----------------------------------------------------------
                # Send the message
                # No error recovery here, will be done on the subsequent Read()
                #       that fails, which is done either here or by application.
                #-----------------------------------------------------------
                try:
                    self.devAntDongle.write(0x01,message)   # input:   endpoint address, buffer, timeout
                                                            # returns:
                except Exception as e:
                    logfile.Console("AntDongle.Write exception (message lost): " + str(e))

                if debug.on(debug.Performance): logfile.Write('... done')
                #-----------------------------------------------------------
                # Read all responses (after each write only when flushing!)
                #-----------------------------------------------------------
                if receive and flush:
                    self.Read(drop) # Flush -> default timeout = proven!

            #---------------------------------------------------------------
            # Read all responses after having sent all messages.
            # Not required when flushing, to avoid double timeout.
            #---------------------------------------------------------------
            if receive and not flush:
                self.Read(drop, 1)       # Shortest possible timeout

    #---------------------------------------------------------------------------
    # R e a d
    #---------------------------------------------------------------------------
    # input     drop    the caller does not process the returned data, this flag
    #                           impacts the logfile only!
    #                   2022-08-22 since messages are stored in a queue, they
    #                           are no longer dropped
    #
    # function  read response from antDongle
    #
    # returns   None; data is in the Queue. QueueSize() returns nr messages.
    #---------------------------------------------------------------------------
    # Dongle disconnect recovery
    # summary           This is introduced for the CYCPLUS dongles that appear
    #                   do disconnect during a session. Reason unknown.
    #                   Thanks to @mattipee and @ElDonad for persistent
    #                   investigations!
    #                   See https://github.com/WouterJD/FortiusANT/issues/65
    #
    # __ReadAndRetry    checks the succesfull read from the dongle.
    #                   If an error occurs, the dongle is reconnected and
    #                   the DongleReconnected flag is raised, signalling the
    #                   caller that the channels must be reinitiated.
    #                   This is usefull, so that the calling process does not
    #                   need to check this after every call, in the outer loop
    #                   is enough.
    #
    # ApplicationRestart must be called to reset the flag, a good place to do
    #                   this is before the channel-initiating routines
    #---------------------------------------------------------------------------
    def ApplicationRestart(self):
        self.DongleReconnected = False

    def __ReadAndRetry(self, timeout):
        failed  = False
        # ----------------------------------------------------------------------
        # 2021-02-22 timeout was 20 untill now; but that causes too much delay!
        #
        # Zero is not allowed, so take 1 milli-second
        #       Measurements however show, the delay still is 16 ms.
        # But with a too short delay, sometimes incomplete buffers are returned
        #       causing the message "characters skipped"
        #       
        # Now we have a default of 20ms, which can be overridden by the caller
        # tipically in the ANT-loop, a short timeout will be specified.
        # ----------------------------------------------------------------------
        if debug.on(debug.Performance): logfile.Write('devAntDongle.__ReadAndRetry(0x81,1000,%s) ...' % timeout)
        try:
            trv = []                                        # initialize because is processed even after exception
            trv = self.devAntDongle.read(0x81,1000,timeout) # input:  endpoint address, length, timeout
                                                            # returns: an array of bytes
        # ----------------------------------------------------------------------
        # https://docs.python.org/3/library/exceptions.html
        # ----------------------------------------------------------------------
        # TimeoutError not raised on all systems, inspect text-message as well.
        # "timeout error" on most systems, "timed out" on Macintosh.
        # ----------------------------------------------------------------------
        except TimeoutError:
            pass
        except Exception as e:
            if "timeout error" in str(e) or "timed out" in str(e):
                pass
            else:
                failed = True
                logfile.Console("devAntDongle.read exception: " + str(e))
        # ----------------------------------------------------------------------
        # Recover from Exception
        # If the dongle does not come back, it's an infinite loop. Bad luck.
        #
        # When an AntDongle is unplugged and put back in again, the reading from
        # the dongle continues. BUT: the channel definition is lost.
        # So we have to signal to the calling application to repair!
        #
        # Still, this recovery is not useless. The dongle is connected again.
        # the caller must redo the channels.
        # ----------------------------------------------------------------------
        while failed:
            logfile.Console('ANT Dongle not available; try to reconnect after 1 second')
            time.sleep(1)
            if self.__GetDongle():
                failed = False       # Exception resolved
                self.DongleReconnected = True
                logfile.Console('ANT Dongle reconnected, application restarts')

        if debug.on(debug.Performance): logfile.Write('... done')
        return trv

    def _Read(self, _drop, timeout = 20):
        #-------------------------------------------------------------------
        # Read from antDongle untill no more data (timeout), or error
        # Usually, dongle gives one buffer at the time, starting with 0xa4
        # Sometimes, multiple messages are received together on one .read
        #
        # https://www.thisisant.com/forum/view/viewthread/812
        #-------------------------------------------------------------------
        while self.OK:                   # If no dongle ==> no action at all
            trv = self.__ReadAndRetry(timeout)
            if len(trv) == 0:
                break
            # --------------------------------------------------------------------------
            # Handle content returned by .__ReadAndRetry()
            # --------------------------------------------------------------------------
            if debug.on(debug.Data1): logfile.Write('devAntDongle.__ReadAndRetry() returns %s ' \
                                                    % (logfile.HexSpaceL(trv)))

            if len(trv) > 900: logfile.Console("Dongle.Read() too much data from .read()" )
            start  = 0
            while start < len(trv):
                error = False
                #-------------------------------------------------------
                # Each message starts with a4; skip characters if not
                #-------------------------------------------------------
                skip = start
                while skip < len(trv) and trv[skip] != 0xa4:
                    skip += 1
                if skip != start:
                    logfile.Console("Dongle.Read: %s characters skipped " % (skip - start))
                    start = skip
                #-------------------------------------------------------
                # Second character in the buffer (element in trv) is length of
                # the info; add four for synch, len, id and checksum
                #-------------------------------------------------------
                if start + 1 < len(trv):
                    length = trv[start+1] + 4
                    if start + length <= len(trv):
                        #-------------------------------------------------------
                        # Check length and checksum
                        # Append to return array when correct
                        #-------------------------------------------------------
                        d = bytes(trv[start : start+length])
                        checksum = d[-1:]
                        expected = CalcChecksum(d)

                        if expected != checksum:
                            error = "error: checksum incorrect"
                            logfile.Console("%s checksum=%s expected=%s data=%s" % \
                                ( error, logfile.HexSpace(checksum), logfile.HexSpace(expected), logfile.HexSpace(d) ) )
                        else:
                            self.MessageQueuePut(d) # 2022-08-22
                            # Messages are always stored in the queue and hence never
                            # dropped because a caller does not handle them.
                            DongleDebugMessage ("Dongle    receive:", d)
                    else:
                        error = "error: message exceeds buffer length"
                        break
                else:
                    break
                if error:
                    logfile.Console("Dongle.Read: %s" % (error))
                #-------------------------------------------------------
                # Next buffer in trv
                #-------------------------------------------------------
                start += length
        if self.OK and debug.on(debug.Function):
            logfile.Write ("AntDongle.Read: Queue contains %s messages" % self.MessageQueueSize())

    #--------------------------------------------------------------------------
    # R e a d   /   R e a d T h r e a d
    #--------------------------------------------------------------------------
    # Read the ANT dongle directly
    #   - as is done in GetDongle()
    #   - or when no thread is created.
    # ... or just using the queue as is filled in the thread
    #--------------------------------------------------------------------------
    def StartReadThread(self):
        if self.UseThread and self.OK:
            if debug.on(debug.Function): logfile.Write ("StartReadThread(): Create thread to read messages from ANT dongle")
            self.MessageThread = threading.Thread(target=self.ReadThread, daemon=True)    # No args=(), 
            self.ThreadActive  = True
            self.MessageThread.start()
            if debug.on(debug.Function): logfile.Write ("StartReadThread(): Thread started")

    def Read(self, drop, timeout=20):
        if self.UseThread and self.ThreadActive:
            # Reading is done by ReadThread()
            pass
        else:
            self._Read(drop, timeout)

    def ReadThread(self):
        while self.ThreadActive:
            # print('*** Thread read message')
            self._Read(False)

    def StopReadThread(self):
        if self.MessageThread:
            if debug.on(debug.Function): logfile.Write ("StopReadThread(): Stop thread reading messages from ANT dongle")
            self.ThreadActive = False       # Signal thread to stop
            self.MessageThread.join()       # Wait that thread is stopped
            self.MessageThread = None
            if debug.on(debug.Function): logfile.Write ("StopReadThread(): Thread stopped")


    #-----------------------------------------------------------------------
    # Standard dongle commands
    # Observation: all commands have two bytes 00 00 for which purpose is unclear
    # ------------------------------------------------------------------------------
    # Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
    #   ANT:     D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
    #   trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
    #   hrm:     D00000693_-_ANT+_Device_Profile_-_Heart_Rate_Rev_2.1.pdf
    #---------------------------------------------------------------------------
    def Calibrate(self):
        if self.OK and debug.on(debug.Data1): logfile.Write ("Calibrate()")

        self.ResetDongle()

        messages=[
            msg4D_RequestMessage        (0, msgID_Capabilities),   # request max channels
            msg4D_RequestMessage        (0, msgID_ANTversion),     # request ant version
            msg46_SetNetworkKey         (),
            msg46_SetNetworkKey         (NetworkNumber = 0x01, NetworkKey=0x00),
                                                                # network for Tacx i-Vortex
        ]
        self.Write(messages)
        self.StartReadThread()          # Start reading in a thread from now on

    def ResetDongle(self):
        self.StopReadThread()           # Stop reading in a thread

        if self.Cycplus:
            # For CYCPLUS dongles this command may be given on initialization only
            # If done lateron, the dongle hangs
            # Note that __GetDongle() does not use this routine!
            pass
        else:
            if self.OK and debug.on(debug.Data1): logfile.Write ("ResetDongle()")
            messages=[
                msg4A_ResetSystem(),
            ]
            self.Write(messages, False)
        time.sleep(0.500)                           # After Reset, 500ms before next action

    def SlavePair_ChannelConfig(self, channel_pair, \
                                DeviceNumber=0, DeviceTypeID=0, TransmissionType=0):
                                # Slave, by default full wildcards ChannelID, see msg51 comment
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT tries to pair with an ANT+ device' + s)
            if debug.on(debug.Data1): logfile.Write ("SlavePair_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_pair, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
            msg51_ChannelID             (channel_pair, DeviceNumber, DeviceTypeID, TransmissionType),
            msg45_ChannelRfFrequency    (channel_pair, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_pair, ChannelPeriod=0x1f86),
            msg60_ChannelTransmitPower  (channel_pair, TransmitPower_0dBm),
            msg44_ChannelSearchTimeout  (channel_pair, 255),  #381/2 Analogously to other slaves; I hope it improves
            msg4B_OpenChannel           (channel_pair)
        ]
        self.Write(messages) # 2021-04-15 ", True, False"  removed because it's inconsistent

    def Trainer_ChannelConfig(self):
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT broadcasts data as an ANT+ Controlled Fitness Equipent device (FE-C), id=%s' % DeviceNumber_FE)
            if debug.on(debug.Data1): logfile.Write ("Trainer_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_FE, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
            msg51_ChannelID             (channel_FE, DeviceNumber_FE, DeviceTypeID_FE, TransmissionType_IC_GDP),
            msg45_ChannelRfFrequency    (channel_FE, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_FE, ChannelPeriod=8192),           # 4 Hz
            msg60_ChannelTransmitPower  (channel_FE, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_FE)
        ]
        self.Write(messages)

    def SlaveTrainer_ChannelConfig(self, DeviceNumber):
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives data from an ANT+ Controlled Fitness Equipent device (FE-C)' + s)
            if debug.on(debug.Data1): logfile.Write ("SlaveTrainer_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_FE_s, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
            msg51_ChannelID             (channel_FE_s, DeviceNumber, DeviceTypeID_FE, TransmissionType_Pairing),
            msg45_ChannelRfFrequency    (channel_FE_s, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_FE_s, ChannelPeriod=8192),         # 4 Hz
            msg60_ChannelTransmitPower  (channel_FE_s, TransmitPower_0dBm),
            msg44_ChannelSearchTimeout  (channel_FE_s, 255),  #381/2 Analogously to other slaves; I hope it improves
            msg4B_OpenChannel           (channel_FE_s),
            msg4D_RequestMessage        (channel_FE_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def HRM_ChannelConfig(self):
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT broadcasts data as an ANT+ Heart Rate Monitor (HRM), id=%s' % DeviceNumber_HRM)
            if debug.on(debug.Data1): logfile.Write ("HRM_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_HRM, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
            msg51_ChannelID             (channel_HRM, DeviceNumber_HRM, DeviceTypeID_HRM, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_HRM, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_HRM, ChannelPeriod=8070),          # 4,06 Hz
            msg60_ChannelTransmitPower  (channel_HRM, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_HRM)
        ]
        self.Write(messages)

    def SlaveHRM_ChannelConfig(self, DeviceNumber):
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives data from an ANT+ Heart Rate Monitor (HRM display)' + s)
            if debug.on(debug.Data1): logfile.Write ("SlaveHRM_ChannelConfig()")

        # 2021-12-03 Pairing must be done with TransmissionType=TransmissionType_Pairing (0)!! 
        messages=[
            msg42_AssignChannel         (channel_HRM_s, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
            msg51_ChannelID             (channel_HRM_s, DeviceNumber, DeviceTypeID_HRM, TransmissionType_Pairing),
            msg45_ChannelRfFrequency    (channel_HRM_s, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_HRM_s, ChannelPeriod=8070),        # 4,06 Hz
            msg44_ChannelSearchTimeout  (channel_HRM_s, 255),                       #381/2 Search infinitely for HRM
            msg60_ChannelTransmitPower  (channel_HRM_s, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_HRM_s),
            msg4D_RequestMessage        (channel_HRM_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def PWR_ChannelConfig(self, DeviceNumber):
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT broadcasts data as an ANT+ Bicycle Power Sensor (PWR), id=%s' % DeviceNumber_PWR)
            if debug.on(debug.Data1): logfile.Write ("PWR_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_PWR, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
            msg51_ChannelID             (channel_PWR, DeviceNumber_PWR, DeviceTypeID_PWR, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_PWR, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_PWR, ChannelPeriod=8182),          # 4,0059 Hz
            msg60_ChannelTransmitPower  (channel_PWR, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_PWR),
        ]
        self.Write(messages)

    def SCS_ChannelConfig(self, DeviceNumber):
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT broadcasts data as an ANT+ Speed and Cadence Sensor (SCS), id=%s' % DeviceNumber_SCS)
            if debug.on(debug.Data1): logfile.Write ("SCS_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_SCS, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
            msg51_ChannelID             (channel_SCS, DeviceNumber_SCS, DeviceTypeID_SCS, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_SCS, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_SCS, ChannelPeriod=8086),          # 4,05 Hz
            msg60_ChannelTransmitPower  (channel_SCS, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_SCS),
        ]
        self.Write(messages)

    def SlaveSCS_ChannelConfig(self, DeviceNumber):
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives data from an ANT+ Speed and Cadence Sensor (SCS Display)' + s)
            if debug.on(debug.Data1): logfile.Write ("SlaveSCS_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_SCS_s, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
            msg51_ChannelID             (channel_SCS_s, DeviceNumber, DeviceTypeID_SCS, TransmissionType_Pairing),
            msg45_ChannelRfFrequency    (channel_SCS_s, RfFrequency_2457Mhz),
            msg44_ChannelSearchTimeout  (channel_SCS_s, 255),                       #381/2 Analogously to other slaves; I hope it improves
            msg43_ChannelPeriod         (channel_SCS_s, ChannelPeriod=8086),        # 4,05 Hz
            msg60_ChannelTransmitPower  (channel_SCS_s, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_SCS_s),
            msg4D_RequestMessage        (channel_SCS_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def CTRL_ChannelConfig(self, DeviceNumber):
        if self.OK:
            # For consistency it should have been:
            #                'FortiusANT broadcasts that it accepts commands from an ANT+ Generic Remote Control')
            # because we are the master device and the Remote Control pairs to us
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives commands from an ANT+ Generic Remote Control')
            if debug.on(debug.Data1): logfile.Write ("CTRL_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_CTRL, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
            msg51_ChannelID             (channel_CTRL, DeviceNumber, DeviceTypeID_CTRL, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_CTRL, RfFrequency_2457Mhz),
            msg43_ChannelPeriod         (channel_CTRL, ChannelPeriod=8192),        # 4 Hz
            msg60_ChannelTransmitPower  (channel_CTRL, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_CTRL),
            msg4D_RequestMessage        (channel_CTRL, msgID_ChannelID)
        ]
        self.Write(messages)

    def VTX_ChannelConfig(self):                         # Pretend to be a Tacx Vortex
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT broadcasts data as an ANT Tacx Vortex (VTX), id=%s' % DeviceNumber_VTX)
            if debug.on(debug.Data1): logfile.Write ("VTX_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_VTX, ChannelType_BidirectionalTransmit, NetworkNumber=0x01),
            msg51_ChannelID             (channel_VTX, DeviceNumber_VTX, DeviceTypeID_VTX, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_VTX, RfFrequency_2466Mhz),
            msg43_ChannelPeriod         (channel_VTX, ChannelPeriod=0x2000),
            msg60_ChannelTransmitPower  (channel_VTX, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_VTX),
            msg4D_RequestMessage        (channel_VTX, msgID_ChannelID)
        ]
        self.Write(messages)

    def SlaveVTX_ChannelConfig(self, DeviceNumber):     # Listen to a Tacx Vortex
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives data from an ANT Tacx Vortex (VTX Controller)' + s)
            if debug.on(debug.Data1): logfile.Write ("SlaveVTX_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_VTX_s, ChannelType_BidirectionalReceive, NetworkNumber=0x01),
            msg51_ChannelID             (channel_VTX_s, DeviceNumber, DeviceTypeID_VTX, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_VTX_s, RfFrequency_2466Mhz),
            msg43_ChannelPeriod         (channel_VTX_s, ChannelPeriod=0x2000),
            msg44_ChannelSearchTimeout  (channel_VTX_s, 255),
            msg60_ChannelTransmitPower  (channel_VTX_s, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_VTX_s),
            msg4D_RequestMessage        (channel_VTX_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def SlaveGNS_ChannelConfig(self, DeviceNumber):     # Listen to a Tacx Genius
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives data from an ANT Tacx Genius (GNS Brake)' + s)
            if debug.on(debug.Data1): logfile.Write ("SlaveGNS_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_GNS_s, ChannelType_BidirectionalReceive, NetworkNumber=0x01),
            msg51_ChannelID             (channel_GNS_s, DeviceNumber, DeviceTypeID_GNS, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_GNS_s, RfFrequency_2460Mhz),
            msg43_ChannelPeriod         (channel_GNS_s, ChannelPeriod=0x1000), # keep searching indefinitely
            msg44_ChannelSearchTimeout  (channel_GNS_s, 255),
            msg60_ChannelTransmitPower  (channel_GNS_s, TransmitPower_0dBm),
            msg4B_OpenChannel           (channel_GNS_s),
            msg4D_RequestMessage        (channel_GNS_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def SlaveBHU_ChannelConfig(self, DeviceNumber):     # Listen to a Tacx Genius
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives data from an ANT Tacx Bushido head unit (BHU Controller)' + s)
            if debug.on(debug.Data1): logfile.Write ("SlaveBHU_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_GNS_s, ChannelType_BidirectionalReceive, NetworkNumber=0x01),
            msg51_ChannelID             (channel_GNS_s, DeviceNumber, DeviceTypeID_BHU, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_GNS_s, RfFrequency_2460Mhz),
            msg43_ChannelPeriod         (channel_GNS_s, ChannelPeriod=0x1000),
            msg60_ChannelTransmitPower  (channel_GNS_s, TransmitPower_0dBm),
            msg44_ChannelSearchTimeout  (channel_GNS_s, 255),  # keep searching indefinitely
            msg4B_OpenChannel           (channel_GNS_s),
            msg4D_RequestMessage        (channel_GNS_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def SlaveVHU_ChannelConfig(self, DeviceNumber):     # Listen to a Tacx Vortex Headunit
                                                        # See comment above msgPage000_TacxVortexHU_StayAlive
        
        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console ('FortiusANT receives data from an ANT Tacx Vortex Headunit (VHU Controller)' + s)
            if debug.on(debug.Data1): logfile.Write ("SlaveVHU_ChannelConfig()")
        messages=[
            msg42_AssignChannel         (channel_VHU_s, ChannelType_BidirectionalReceive, NetworkNumber=0x01),
            msg51_ChannelID             (channel_VHU_s, DeviceNumber, DeviceTypeID_VHU, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_VHU_s, RfFrequency_2478Mhz),
            msg43_ChannelPeriod         (channel_VHU_s, ChannelPeriod=0x0f00),
            msg60_ChannelTransmitPower  (channel_VHU_s, TransmitPower_0dBm),
            msg44_ChannelSearchTimeout  (channel_VHU_s, 255),  #381/2 Analogously to other slaves; I hope it improves
            msg4B_OpenChannel           (channel_VHU_s),
            msg4D_RequestMessage        (channel_VHU_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def SlaveBLTR_ChannelConfig(self, DeviceNumber):  # Listen to a Tacx Blacktrack steering unit

        if DeviceNumber > 0: s = ", id=%s only" % DeviceNumber
        else:                s = ", any device"
        if self.OK:
            if self.ConfigMsg:
                logfile.Console('FortiusANT receives data from an ANT Tacx BlackTrack steering unit (BLTR)' + s)
            if debug.on(debug.Data1): logfile.Write("SlaveBLTR_ChannelConfig()")
        messages = [
            msg42_AssignChannel         (channel_BLTR_s, ChannelType_BidirectionalReceive, NetworkNumber=0x01),
            msg51_ChannelID             (channel_BLTR_s, DeviceNumber, DeviceTypeID_BLTR, TransmissionType_IC),
            msg45_ChannelRfFrequency    (channel_BLTR_s, RfFrequency_2460Mhz),
            msg43_ChannelPeriod         (channel_BLTR_s, ChannelPeriod=0x2000),
            msg60_ChannelTransmitPower  (channel_BLTR_s, TransmitPower_0dBm),
            msg44_ChannelSearchTimeout  (channel_BLTR_s, 255),  #381/2 Analogously to other slaves; I hope it improves
            msg4B_OpenChannel           (channel_BLTR_s),
            msg4D_RequestMessage        (channel_BLTR_s, msgID_ChannelID)
        ]
        self.Write(messages)

    def PowerDisplay_unused(self):
        if self.OK and debug.on(debug.Data1): logfile.Write ("powerdisplay()")
                                                            # calibrate as power display
        messages=[
        "a4 03 42 00 00 00 e5",                     # 42 assign channel
        "a4 05 51 00 00 00 0b 00 fb",               # 51 set channel id, 0b device=power sensor
        "a4 02 45 00 39 da",                        # 45 channel freq
        "a4 03 43 00 f6 1f 0d",                     # 43 msg period
        "a4 02 71 00 00 d7",                        # 71 Set Proximity Search chann number 0 search threshold 0
        "a4 02 63 00 0a cf",                        # 63 low priority search channel number 0 timeout 0
        "a4 02 44 00 02 e0",                        # 44 Host Command/Response
        "a4 01 4b 00 ee"                            # 4b ANT_OpenChannel message ID channel = 0 D00001229_Fitness_Modules_ANT+_Application_Note_Rev_3.0.pdf
        ]
        self.Write(messages)

#-------------------------------------------------------------------------------
# E n u m e r a t e A l l
#-------------------------------------------------------------------------------
# input     none
#
# function  list all usb-devices
#
# returns   none
#-------------------------------------------------------------------------------
def EnumerateAll():
    logfile.Console("Dongles in the system:")
    devices = usb.core.find(find_all=True)
    for device in devices:
#       print (device)
        s = "manufacturer=%7s, product=%15s, vendor=%6s, product=%6s(%s)" %\
                (device.manufacturer, device.product, \
                hex(device.idVendor), hex(device.idProduct), device.idProduct)
        logfile.Console(s.replace('\0',''))

        i = 0
        for cfg in device:          # Do not understand this construction; see pyusb tutorial
            i += 1
            for intf in cfg:
                for _ep in intf:
                    pass
    logfile.Console("--------------------")
#-------------------------------------------------------------------------------
# C a l c C h e c k s u m
#-------------------------------------------------------------------------------
# input     ANT message,
#               e.g. "a40340000103e5" where last byte may be the checksum itself
#                     s l i .1.2.3    synch=a4, len=03, id=40, info=000103, checksum=e5
#
# function  Calculate the checksum over synch + length + id + info (3 + info)
#
# returns   checksum, which should match the last two characters
#-------------------------------------------------------------------------------
def calc_checksum(message):
    return CalcChecksum (message)           # alias for compatibility

def CalcChecksum (message):
    xor_value = 0
    length    = message[1]                  # byte 1; length of info
    length   += 3                           # Add synch, len, id
    for i in range (0, length):             # Process bytes as defined in length
        xor_value = xor_value ^ message[i]

#   print('checksum', logfile.HexSpace(message), xor_value, bytes([xor_value]))

    return bytes([xor_value])

#-------------------------------------------------------------------------------
# C o m p o s e   A N T   M e s s a g e
#-------------------------------------------------------------------------------
def ComposeMessage(id, info):
    fSynch      = sc.unsigned_char
    fLength     = sc.unsigned_char
    fId         = sc.unsigned_char
    fInfo       = str(len(info)) + sc.char_array  # 9 character string

    format  =    sc.no_alignment + fSynch + fLength + fId + fInfo
    data    = struct.pack (format, 0xa4,    len(info), id,  info)
    #-----------------------------------------------------------------------
    # Add the checksum
    # (antifier added \00\00 after each message for unknown reason)
    #-----------------------------------------------------------------------
    data += calc_checksum(data)

    return data

def DecomposeMessage(d):
    synch       = 0
    length      = 0
    id          = 0
    checksum    = 0
    info        = binascii.unhexlify('')                # NULL-string bytes
    rest        = ""                                    # No remainder (normal)

    if len(d) > 0:          synch    = d[0]             # Carefull approach
    if len(d) > 1:          length   = d[1]
    if len(d) > 2:          id       = d[2]
    if len(d) > 3 + length:
        if length:          info     = d[3:3+length]    # Info, if length > 0
        checksum                     = d[3 + length]    # Character after info
    if len(d) > 4 + length: rest     = d[4 + length:]   # Remainder (should not occur)

    Channel         = -1
    DataPageNumber  = -1
    if length >= 1: Channel         = d[3]
    if length >= 2: DataPageNumber  = d[4]

    #---------------------------------------------------------------------------
    # Special treatment for Burst data
    # Note that SequenceNumber is not returned and therefore lost, which is to
    #      be implemented as soon as we will use msgID_BurstData
    #---------------------------------------------------------------------------
    if id == msgID_BurstData:
        _SequenceNumber = (Channel & 0b11100000) >> 5 # Upper 3 bits
        Channel         =  Channel & 0b00011111       # Lower 5 bits

    return synch, length, id, info, checksum, rest, Channel, DataPageNumber

#-------------------------------------------------------------------------------
# D e b u g M e s s a g e
#-------------------------------------------------------------------------------
# input     msg, d
#
# function  Write structured dongle message to logfile if so requested
#           Message ID is translated to text
#           Also, channel and page are logged
#           - the first byte of info is not always channel, if not ignore!
#           - only some messages have a datapage, then page is printed
#           - and some messages, payload is not printed but specific data
#               e.g. ANTversion
#
# returns   none
#-------------------------------------------------------------------------------
def DongleDebugMessage(text, d):
    if debug.on(debug.Data1):
        synch, length, id, info, checksum, _rest, Channel, p = DecomposeMessage(d)

        #-----------------------------------------------------------------------
        # info_ is the payload of the message
        # Channel and p are filled, but only valid for some messages
        #-----------------------------------------------------------------------
        info_ = logfile.HexSpace(info)

        #-----------------------------------------------------------------------
        # First add readable name (id_) to id
        #-----------------------------------------------------------------------
        if   id == msgID_ANTversion             : id_ = 'ANT version'

        elif id == msgID_BroadcastData          : id_ = 'Broadcast Data'
        elif id == msgID_AcknowledgedData       : id_ = 'Acknowledged Data'

        elif id == msgID_ChannelResponse        : id_ = 'Channel Response'
        elif id == msgID_Capabilities           : id_ = 'Capabilities'
        elif id == msgID_UnassignChannel        : id_ = 'Unassign Channel'
        elif id == msgID_AssignChannel          : id_ = 'Assign Channel'
        elif id == msgID_ChannelPeriod          : id_ = 'Channel Period'
        elif id == msgID_ChannelSearchTimeout   : id_ = 'Channel Search Timeout'
        elif id == msgID_ChannelRfFrequency     : id_ = 'Channel RfFrequency'
        elif id == msgID_SetNetworkKey          : id_ = 'Set NetworkKey'
        elif id == msgID_ResetSystem            : id_ = 'Reset System'
        elif id == msgID_OpenChannel            : id_ = 'Open Channel'
        elif id == msgID_RequestMessage         : id_ = 'Request Message'
        elif id == msgID_ChannelID              : id_ = 'Channel ID'
        elif id == msgID_ChannelTransmitPower   : id_ = 'Channel TransmitPower'
        elif id == msgID_StartUp                : id_ = 'Start up'
        elif id == msgID_RF_EVENT               : id_ = 'RF event'  # D00000652..._Rev_5.1.pdf 9.5.6.1 Channel response
        else                                    : id_ = '??'

        #-------------------------------------------------------------------
        # extra is additional info for the message
        # p_ is readable pagenumber if there is a valid pagenumber
        #-------------------------------------------------------------------
        extra = ''                                              # Initially empty
        p_    = ''                                              # There is not always page-info, do not show

        if   id == msgID_ChannelResponse or id == msgID_RequestMessage:
                        extra = " (ch=%s, msg=%s)" % (Channel, hex(p))

        elif id == msgID_ANTversion:
                        Channel = -1                         # There is no channel number for this message
                        extra = info.decode("utf-8").replace('\0', '') # ANTversion in string format
                        info_ = ''

        elif id == msgID_ChannelID:
                        extra = " (ch=%s, nr=%s, ID=%s, tt=%s)" % (unmsg51_ChannelID(info))

        elif id == msgID_BroadcastData or id == msgID_AcknowledgedData:
                                                    # Pagenumber in Payload
            if   p        <   0: pass
            elif Channel  in (channel_SCS, channel_SCS_s):
                                 p_ = ' Speed and Cadence Sensor datapage'
                                 p  = None
            elif p & 0x7f ==  0: p_ = 'Default data page'           # D00000693_-_ANT+_Device_Profile_-_Heart_Rate_Rev_2.1
                                                                    # Also called "Unknown data page"
                                                                    # 'HRM' but other devices have other meanings
                                                                    #    Left for future improvements.
                                                                    #    e.g. dependant on Channel
            elif p & 0x7f ==  1: p_ = 'HRM Cumulative Operating Time'
            elif p & 0x7f ==  2: p_ = 'HRM Manufacturer info'
            elif p & 0x7f ==  3: p_ = 'HRM Product information'
            elif p & 0x7f ==  4: p_ = 'HRM Previous Heart beat'
            elif p & 0x7f ==  5: p_ = 'HRM Swim interval summary'
            elif p & 0x7f ==  6: p_ = 'HRM Capabilities'
            elif p        == 16: p_ = 'Main data page'
            elif p        == 25: p_ = 'Trainer Data'
            elif p        == 48: p_ = 'Basic Resistance'
            elif p        == 49: p_ = 'Target Power'
            elif p        == 50: p_ = 'Wind Resistance'
            elif p        == 51: p_ = 'Track Resistance'
            elif p        == 54: p_ = 'FE Capabilities'
            elif p        == 55: p_ = 'User Configuration'
            elif p        == 70: p_ = 'Request Datapage'
            elif p        == 76: p_ = 'Mode settings page'
            elif p        == 80: p_ = 'Manufacturer Info'
            elif p        == 81: p_ = 'Product Information'
            elif p        == 82: p_ = 'Battery Status'
#           elif p        == 89: p_ = 'Add channel ID to list ???'
            elif p        ==172: p_ = 'Tacx Request information/Set mode'
            elif p        ==173: p_ = 'Tacx Device information'
            elif p        ==220: p_ = 'Tacx Brake control'
            elif p        ==221: p_ = 'Tacx Data update'
            else               : p_ = '??'

            if p != None:        p_ = " p=%s(%s)" % (p, p_)     # Page, show number and name

        elif id == msgID_RF_EVENT:
            pass                                                # We could fill info with error code

        else:
            Channel = -1                                        # There is no channel number for this message

        #-----------------------------------------------------------------------
        # extra is the explanation of info
        # - if already filled, do not change
        # - for data-pages "ch=1 p, pagenumber"
        #-----------------------------------------------------------------------
        if extra != '':
            pass                                                        # Already filled
        else:
            if   Channel == -1:  extra = ""                             # No Channel, do not show
            else              :  extra = " (ch=%s%s)" % (Channel, p_)   # Channel, show it with optional pageinfo

        #-----------------------------------------------------------------------
        # Write to logfile
        #-----------------------------------------------------------------------
        logfile.Write ("%s synch=%s, len=%2s, id=%s %-21s, check=%4s, info=%s%s" % \
                (text,hex(synch), length, hex(id), id_, hex(checksum),  info_, extra))

# ==============================================================================
# ANT+ message interface
# ==============================================================================

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   42   A s s i g n C h a n n e l
# ------------------------------------------------------------------------------
def msg41_UnassignChannel(ChannelNumber):
    format  =    sc.no_alignment + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber)
    msg     = ComposeMessage (0x41, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   42   A s s i g n C h a n n e l
# ------------------------------------------------------------------------------
def msg42_AssignChannel(ChannelNumber, ChannelType, NetworkNumber):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     ChannelType,       NetworkNumber)
    msg     = ComposeMessage (0x42, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   43   C h a n n e l P e r i o d
# ------------------------------------------------------------------------------
def msg43_ChannelPeriod(ChannelNumber, ChannelPeriod):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_short
    info    = struct.pack(format,  ChannelNumber,     ChannelPeriod)
    msg     = ComposeMessage (0x43, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   44   C h a n n e l S e a r c h T i m e o u t
# ------------------------------------------------------------------------------
def msg44_ChannelSearchTimeout(ChannelNumber, SearchTimeout):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_short
    info    = struct.pack(format,  ChannelNumber,     SearchTimeout)
    msg     = ComposeMessage (0x44, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   45   C h a n n e l R f F r e q u e n c y
# ------------------------------------------------------------------------------
def msg45_ChannelRfFrequency(ChannelNumber, RfFrequency):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     RfFrequency)
    msg     = ComposeMessage (0x45, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   46   S e t N e t w o r k K e y
# ------------------------------------------------------------------------------
def msg46_SetNetworkKey(NetworkNumber = 0x00, NetworkKey=0x45c372bdfb21a5b9):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_long_long
    info    = struct.pack(format,  NetworkNumber,     NetworkKey)
    msg     = ComposeMessage (0x46, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   4A   R e s e t   S y s t e m
# ------------------------------------------------------------------------------
def msg4A_ResetSystem():
    format  =    sc.no_alignment + sc.unsigned_char
    info    = struct.pack(format,  0x00)
    msg     = ComposeMessage (0x4a, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   4B   O p e n C h a n n e l
# ------------------------------------------------------------------------------
def msg4B_OpenChannel(ChannelNumber):
    format  =    sc.no_alignment + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber)
    msg     = ComposeMessage (0x4b, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   4D   R e q u e s t   M e s s a g e
# ------------------------------------------------------------------------------
def msg4D_RequestMessage(ChannelNumber, RequestedMessageID):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     RequestedMessageID)
    msg     = ComposeMessage (0x4d, info)
    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   51   C h a n n e l I D
# ------------------------------------------------------------------------------
# D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
# Page  17.   5.2.3 Channel ID
# Page  66. 9.5.2.3 Set Channel ID (0x51)
# Page 121. 9.5.7.2 Channel ID (0x51)
# ------------------------------------------------------------------------------
def msg51_ChannelID(ChannelNumber, DeviceNumber, DeviceTypeID, TransmissionType):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_short + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     DeviceNumber,       DeviceTypeID,      TransmissionType)
    msg     = ComposeMessage (0x51, info)
    return msg

def unmsg51_ChannelID(info):
    #                              0                  1                   2                  3
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_short + sc.unsigned_char + sc.unsigned_char
    tuple  = struct.unpack (format, info)

    return                         tuple[0],          tuple[1],           tuple[2],          tuple[3]

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   60   C h a n n e l T r a n s m i t P o w e r
# ------------------------------------------------------------------------------
def msg60_ChannelTransmitPower(ChannelNumber, TransmitPower):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     TransmitPower)
    msg     = ComposeMessage (0x60, info)
    return msg

# ------------------------------------------------------------------------------
# U n m s g 6 4   C h a n n e l R e s p o n s e
# ------------------------------------------------------------------------------
# D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
# 9.5.6 Channel response / event messages
# ------------------------------------------------------------------------------
def unmsg64_ChannelResponse(info):
    nChannel            = 0
    fChannel            = sc.unsigned_char

    nInitiatingMessageID= 1
    fInitiatingMessageID= sc.unsigned_char

    nResponseCode       = 2
    fResponseCode       = sc.unsigned_char

    format = sc.no_alignment + fChannel + fInitiatingMessageID + fResponseCode
    tuple  = struct.unpack (format, info)

    return tuple[nChannel], tuple[nInitiatingMessageID], tuple[nResponseCode]

# ------------------------------------------------------------------------------
# P a g e 1 6   P o w e r   p r o f i l e
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
#  trainer: D00001086_ANT+_Device_Profile_-_Bicycle_Power_Rev_5.1.pdf
#           Data page 16 (0x10) Power-only Main Data Page
# ------------------------------------------------------------------------------
def msgPage16_PowerOnly (Channel, EventCount, Cadence, AccumulatedPower, CurrentPower):
    DataPageNumber      = 16

    EventCount            = int(       min(0xff,   EventCount      ))
    Cadence               = int(       min(0xff,   Cadence         ))
    AccumulatedPower      = int(       min(0xffff, AccumulatedPower))
    CurrentPower          = int(max(0, min(0x0fff, CurrentPower    )))  # 2021-02-19

    fChannel              = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber       = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fEventCount           = sc.unsigned_char
    fPedalPower           = sc.unsigned_char
    fInstantaneousCadence = sc.unsigned_char
    fAccumulatedPower     = sc.unsigned_short
    fInstantaneousPower   = sc.unsigned_short

    format = sc.no_alignment +  fChannel + fDataPageNumber + fEventCount + fPedalPower + fInstantaneousCadence + fAccumulatedPower + fInstantaneousPower
    info   = struct.pack(format, Channel,   DataPageNumber,   EventCount,   0xff,         Cadence,                AccumulatedPower,   CurrentPower)

    return info

# ------------------------------------------------------------------------------
# P a g e 0 0   T a c x V o r t e x D a t a S p e e d
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#               vortexPage = payload[0];
#               case TACX_VORTEX_DATA_SPEED:
#               {
#                   vortexUsingVirtualSpeed = (payload[1] >> 7) == 1;
#                   vortexPower = payload[2] | ((payload[1] & 7) << 8); // watts
#                   vortexSpeed = payload[4] | ((payload[3] & 3) << 8); // cm/s
#                   // 0, 1, 2, 3 = none, running, new, failed
#                   vortexCalibrationState = (payload[1] >> 5) & 3;
#                   // unclear if this is set to anything
#                   vortexCadence = payload[7];
#                   break;
#               }
# ------------------------------------------------------------------------------
#                                           payload[0][1][2][3][4][5][6][7]
#06:15:48,254: IGNORED!! msg=0x4e ch=7 p=0 info="07 00 80 17 00 4a 00 05 1d" TACX_VORTEX_DATA_SPEED
#                                                ch p  power speed rrrrr cd
# ------------------------------------------------------------------------------
def msgPage00_TacxVortexDataSpeed (Channel, Power, Speed, Cadence):
    DataPageNumber      = 0

    fChannel            = sc.unsigned_char  # 0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # payload[0]        First byte of the ANT+ datapage
    fPower              = sc.unsigned_short # payload[1 and 2]  Watts, big-endian
    fSpeed              = sc.unsigned_short # payload[3 and 4]  cm/s, big-endian
    fReserved           = sc.pad * 2        # payload[5 and 6]
    fCadence            = sc.unsigned_char  # payload[7]

    format = sc.big_endian +    fChannel + fDataPageNumber +    fPower +    fSpeed + fReserved + fCadence
    info   = struct.pack(format, Channel ,  DataPageNumber , int(Power), int(Speed),          int(Cadence))

    # print('msgPage00_TacxVortexDataSpeed', info, Channel, Power, Speed, Cadence)

    return info

def msgUnpage00_TacxVortexDataSpeed (info):
    nChannel            = 0
    fChannel            = sc.unsigned_char  # 0 First byte of the ANT+ message content

    nDataPageNumber     = 1
    fDataPageNumber     = sc.unsigned_char  # payload[0]        First byte of the ANT+ datapage

    nPower              = 2
    fPower              = sc.unsigned_short # payload[1 and 2]  Watts, big-endian

    nSpeed              = 3
    fSpeed              = sc.unsigned_short # payload[3 and 4]  cm/s, big-endian

    fReserved           = sc.pad * 2        # payload[5 and 6]

    nCadence            = 4
    fCadence            = sc.unsigned_char  # payload[7]

    format= sc.big_endian + fChannel + fDataPageNumber + fPower + fSpeed + fReserved + fCadence
    tuple = struct.unpack (format, info)

    _Channel            =  tuple[nChannel]
    _DataPageNumber     =  tuple[nDataPageNumber]
    UsingVirtualSpeed   = (tuple[nPower] & 0x8000) >> 15 # B 1000 0000 0000 0000
    CalibrationState    = (tuple[nPower] & 0x6000) >> 13 # B 0110 0000 0000 0000
    Power               =  tuple[nPower] & 0x07ff        # B 0000 0111 1111 1111
    Speed               =  tuple[nSpeed] & 0x03ff        # B 0000 0011 1111 1111
    Cadence             =  tuple[nCadence]

    return UsingVirtualSpeed, Power, Speed, CalibrationState, Cadence

# ------------------------------------------------------------------------------
# P a g e 0 1   T a c x V o r t e x D a t a S e r i a l
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#               vortexPage = payload[0];
#               case TACX_VORTEX_DATA_SERIAL:
#               {
#                   // unk0 .. unk2 make up the serial number of the trainer
#                   //uint8_t unk0 = payload[1];
#                   //uint8_t unk1 = payload[2];
#                   //uint32_t unk2 = payload[3] << 16 | payload[4] << 8 || payload[5];
#                   // various flags, only known one is for virtual speed used
#                   //uint8_t alarmStatus = payload[6] << 8 | payload[7];
#                   break;
#               }
# ------------------------------------------------------------------------------
#                                           payload[0][1][2][3][4][5][6][7]
#06:15:35,603: IGNORED!! msg=0x4e ch=7 p=1 info="07 01 3d 0d 00 29 42 00 00" TACX_VORTEX_DATA_SERIAL
#                                                ch p  s1 s2 serial-- alarm
# ------------------------------------------------------------------------------
def msgUnpage01_TacxVortexDataSerial (info):
    nChannel            = 0
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content

    nDataPageNumber     = 1
    fDataPageNumber     = sc.unsigned_char  # payload[0] First byte of the ANT+ datapage

    nS1                 = 2
    fS1                 = sc.unsigned_char  # payload[1]

    nS2                 = 3
    fS2                 = sc.unsigned_char  # payload[2]

    nS3                 = 4
    fS3                 = sc.unsigned_char  # payload[3]

    nSerial             = 5
    fSerial             = sc.unsigned_short # payload[4, 5]

    nAlarm              = 6
    fAlarm              = sc.unsigned_short # payload[6, 7]

    format= sc.big_endian + fChannel + fDataPageNumber + fS1 + fS2 + fS3 + fSerial + fAlarm
    tuple = struct.unpack (format, info)

    _Channel            =  tuple[nChannel]
    _DataPageNumber     =  tuple[nDataPageNumber]
    S1                  =  tuple[nS1]
    S2                  =  tuple[nS2]
    Serial              =  tuple[nS3] * 256 * 256 + tuple[nSerial]
    Alarm               =  tuple[nAlarm]

    return S1, S2, Serial, Alarm

# ------------------------------------------------------------------------------
# P a g e 0 2   T a c x V o r t e x D a t a V e r s i o n
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#               vortexPage = payload[0];
#               case TACX_VORTEX_DATA_VERSION:
#               {
#                   //uint8_t major = payload[4];
#                   //uint8_t minor = payload[5];
#                   //uint8_t build = payload[6] << 8 | payload[7];
#                   break;
#               }
# ------------------------------------------------------------------------------
#                                           payload[0][1][2][3][4][5][6][7]
#06:15:35,850: IGNORED!! msg=0x4e ch=7 p=2 info="07 02 00 61 83 00 02 00 07" TACX_VORTEX_DATA_VERSION
#                                                ch p  rrrrrrrr ma mi build
# ------------------------------------------------------------------------------
def msgUnpage02_TacxVortexDataVersion (info):
    nChannel            = 0
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content

    nDataPageNumber     = 1
    fDataPageNumber     = sc.unsigned_char  # payload[0] First byte of the ANT+ datapage

    fReserved           = sc.pad * 3        # payload[1, 2, 3]

    nMajor              = 2
    fMajor              = sc.unsigned_char  # payload[4]

    nMinor              = 3
    fMinor              = sc.unsigned_char  # payload[5]

    nBuild              = 4
    fBuild              = sc.unsigned_short # payload[6, 7]

    format= sc.big_endian + fChannel + fDataPageNumber + fReserved + fMajor + fMinor + fBuild
    tuple = struct.unpack (format, info)

    _Channel            =  tuple[nChannel]
    _DataPageNumber     =  tuple[nDataPageNumber]
    Major               =  tuple[nMajor]
    Minor               =  tuple[nMinor]
    Build               =  tuple[nBuild]

    return Major, Minor, Build

# ------------------------------------------------------------------------------
# P a g e 0 3   T a c x V o r t e x D a t a C a l i b r a t i o n
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#               vortexPage = payload[0];
#               case TACX_VORTEX_DATA_CALIBRATION:
#               {
#                   // one byte for calibration, tacx treats this as signed
#                   vortexCalibration = payload[5];
#                   // duplicate of ANT deviceId, I think, necessary for issuing commands
#                   vortexId = payload[6] << 8 | payload[7];
#                   break;
#               }
# ------------------------------------------------------------------------------
#                                           payload[0][1][2][3][4][5][6][7]
#06:15:36,118: IGNORED!! msg=0x4e ch=7 p=3 info="07 03 ff ff ff ff 0e 30 b0" TACX_VORTEX_DATA_CALIBRATION
#                                                      rrrrrrrrrrr cal
#                                                                     vtxid
# ------------------------------------------------------------------------------
def msgPage03_TacxVortexDataCalibration (Channel, Calibration, VortexID):
    DataPageNumber      = 3

    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # payload[0] First byte of the ANT+ datapage
    fReserved           = sc.pad * 4        # payload[1, 2, 3, 4]
    fCalibration        = sc.unsigned_char  # payload[5]
    fVortexID           = sc.unsigned_short # payload[6, 7]

    format= sc.big_endian +     fChannel + fDataPageNumber + fReserved + fCalibration + fVortexID
    info   = struct.pack(format, Channel,   DataPageNumber,               Calibration,   VortexID)

    # print('msgPage03_TacxVortexDataCalibration', info, Channel, Calibration, VortexID)

    return info

def msgUnpage03_TacxVortexDataCalibration (info):
    nChannel            = 0
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content

    nDataPageNumber     = 1
    fDataPageNumber     = sc.unsigned_char  # payload[0] First byte of the ANT+ datapage

    fReserved           = sc.pad * 4        # payload[1, 2, 3, 4]

    nCalibration        = 2
    fCalibration        = sc.unsigned_char  # payload[5]

    nVortexID           = 3
    fVortexID           = sc.unsigned_short # payload[6, 7]

    format= sc.big_endian + fChannel + fDataPageNumber + fReserved + fCalibration + fVortexID
    tuple = struct.unpack (format, info)

    _Channel            =  tuple[nChannel]
    _DataPageNumber     =  tuple[nDataPageNumber]
    Calibration         =  tuple[nCalibration]
    VortexID            =  tuple[nVortexID]

    return Calibration, VortexID

# ------------------------------------------------------------------------------
# P a g e 1 6   T a c x V o r t e x S e t F C S e r i a l
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#   ANTMessage ANTMessage::tacxVortexSetFCSerial(const uint8_t channel, const uint16_t setVortexId)
#   {
#       return ANTMessage(9, ANT_BROADCAST_DATA, channel, 0x10, setVortexId >> 8, setVortexId & 0xFF,
#                         0x55, // coupling request
#                         0x7F, 0, 0, 0);
#   }
# ------------------------------------------------------------------------------
def msgPage16_TacxVortexSetFCSerial (Channel, VortexID):
    DataPageNumber      = 16

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fVortexID           = sc.unsigned_short
    fCommand            = sc.unsigned_char  # 0x55 = coupling request
    fSubcommand         = sc.unsigned_char  # no explanation...
    fReserved           = sc.pad * 3

    format = sc.big_endian +    fChannel + fDataPageNumber + fVortexID + fCommand + fSubcommand + fReserved
    info   = struct.pack(format, Channel,   DataPageNumber,   VortexID,   0x55,      0x7F)

    return info

# ------------------------------------------------------------------------------
# P a g e 1 6   T a c x V o r t e x S t a r t C a l i b r a t i o n
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#   ANTMessage ANTMessage::tacxVortexStartCalibration(const uint8_t channel, const uint16_t vortexId)
#   {
#       return ANTMessage(9, ANT_BROADCAST_DATA, channel, 0x10, vortexId >> 8, vortexId & 0xFF,
#                         0, 0xFF /* signals calibration start */, 0, 0, 0);
#   }
# ------------------------------------------------------------------------------
def msgPage16_TacxVortexStartCalibration (Channel, VortexID):
    DataPageNumber      = 16

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fVortexID           = sc.unsigned_short
    fCommand            = sc.unsigned_char  # 0x00
    fSubcommand         = sc.unsigned_char  # 0xFF signals calibration start
    fReserved           = sc.pad * 3

    format = sc.big_endian +    fChannel + fDataPageNumber + fVortexID + fCommand + fSubcommand + fReserved
    info   = struct.pack(format, Channel,   DataPageNumber,   VortexID,   0x00,     0xFF)

    return info

# ------------------------------------------------------------------------------
# P a g e 1 6   T a c x V o r t e x S t o p C a l i b r a t i o n
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#   ANTMessage ANTMessage::tacxVortexStopCalibration(const uint8_t channel, const uint16_t vortexId)
#   {
#       return ANTMessage(9, ANT_BROADCAST_DATA, channel, 0x10, vortexId >> 8, vortexId & 0xFF,
#                         0, 0x7F /* signals calibration stop */, 0, 0, 0);
#   }
# ------------------------------------------------------------------------------
def msgPage16_tacxVortexStopCalibration (Channel, VortexID):
    return msgPage16_TacxVortexSetCalibrationValue (Channel, VortexID, 0)

# ------------------------------------------------------------------------------
# P a g e 1 6   T a c x V o r t e x S e t C a l i b r a t i o n V a l u e
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
#   ANTMessage ANTMessage::tacxVortexSetCalibrationValue(const uint8_t channel, const uint16_t vortexId, const uint8_t calibrationValue)
#   {
#       return ANTMessage(9, ANT_BROADCAST_DATA, channel, 0x10, vortexId >> 8, vortexId & 0xFF,
#                         0, 0x7F, calibrationValue, 0, 0);
#   }
# ------------------------------------------------------------------------------
def msgPage16_TacxVortexSetCalibrationValue (Channel, VortexID, CalibrationValue):
    DataPageNumber      = 16

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fVortexID           = sc.unsigned_short
    fCommand            = sc.unsigned_char  #
    fSubcommand         = sc.unsigned_char  # 0x7F signals calibration start
    fCalibrationValue   = sc.unsigned_char
    fReserved           = sc.pad * 2

    format = sc.big_endian +    fChannel + fDataPageNumber + fVortexID + fCommand + fSubcommand + fCalibrationValue + fReserved
    info   = struct.pack(format, Channel,   DataPageNumber,   VortexID,   0,        0x7F,         CalibrationValue  )

    return info

# ------------------------------------------------------------------------------
# P a g e 1 6   T a c x V o r t e x S e t P o w e r
# ------------------------------------------------------------------------------
# Refer:    GoldenCheetah\GoldenCheetah\src\ANT; ANTmessage.cpp
# ANTMessage ANTMessage::tacxVortexSetPower(const uint8_t channel, const uint16_t vortexId, const uint16_t power)
#   {
#    return ANTMessage(9, ANT_BROADCAST_DATA, channel, 0x10, vortexId >> 8, vortexId & 0xFF,
#                      0xAA, // power request
#                      0, 0, // no calibration related data
#                      power >> 8, power & 0xFF);
#   }
# ------------------------------------------------------------------------------
def msgPage16_TacxVortexSetPower (Channel, VortexID, Power):
    DataPageNumber      = 16

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fVortexID           = sc.unsigned_short
    fCommand            = sc.unsigned_char  # 0xAA power request
    fSubcommand         = sc.unsigned_char
    fNoCalibrationData  = sc.unsigned_char
    fPower              = sc.unsigned_short # https://tacx.com/nl/product/i-vortex/
    Power = max(0, Power)                   # --> No simulation descent ==> power > 0

    format = sc.big_endian +    fChannel + fDataPageNumber +   fVortexID + fCommand + fSubcommand + fNoCalibrationData + fPower
    info   = struct.pack(format, Channel,   DataPageNumber, int(VortexID),  0xAA,      0,            0,               int(Power))

    return info

def msgUnpage16_TacxVortexSetPower (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fVortexID           = sc.unsigned_short
    fCommand            = sc.unsigned_char  # 0xAA power request
    fSubcommand         = sc.unsigned_char
    fNoCalibrationData  = sc.unsigned_char
    fPower              = sc.unsigned_short

    format = sc.big_endian +    fChannel + fDataPageNumber + fVortexID + fCommand + fSubcommand + fNoCalibrationData + fPower
    tuple = struct.unpack (format, info)

          #Channel,  DataPageNumber, VortexID, Command,  Subcommand, NoCalibrationData, Power
    return tuple[0], tuple[1],       tuple[2], tuple[3], tuple[4],   tuple[5],          tuple[6]

# ------------------------------------------------------------------------------
#     P a g e 1 7 2   T a c x V o r t e x H U _ C h a n g e H e a d u n i t M o d e
# U n P a g e 2 2 1   T a c x V o r t e x H U _ B u t t o n P r e s s e d
# ------------------------------------------------------------------------------
# TotalReverse:
# You have to switch the head unit into -PC- mode. The head unit config is
#
# Frequency=0x4e (78), DeviceType=0x3e, Period = 0x0f00 and no network key
#
# When active, the units sends "ad 01 .." frames containing the serial number of the device.
#
# You can change the head unit mode with the command
# "ac 03 xx 00 00 00 00 00"
# with
# xx=0x4 switchs to "-PC-" mode
# xx=0x0 switchs back to "trainer control" mode
# xx=0x2 switchs to some kind of "special mode" (probably some kind of 'mixed'
#        mode where the head unit shows the trainer speed, cad and power and
#        maybe works like a repeater of the data)
# xx="anything else" is another "special mode" (?)
#
# In -PC- mode, pressing the buttons sends frames like
# "dd 10 xx 00 00 00 00 cc"
# where "xx" is a button number from 1 to 5 and
#       "cc" is a counter, which increments for every button press.
#
# To prevent the head unit to switch to "power off" you have to send zero frames
# "00 00 00 00 00 00 00 00" from time to time.
#
# The device also knows the standard commands "ac 01 .." , "ac 02 .." , "ac 04 .."
# to trigger the serial-number (the default frame), the version-number and the
# battery status.
# ------------------------------------------------------------------------------
def msgPage000_TacxVortexHU_StayAlive (Channel):        # No Power Off
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fReserved           = sc.pad * 8

    format = sc.big_endian +    fChannel + fReserved
    info   = struct.pack(format, Channel)

    return info

def msgPage172_TacxVortexHU_ChangeHeadunitMode (Channel, Mode):
    DataPageNumber      = 172

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fCommand            = sc.unsigned_char  # 0x03 Change headunit Mode
    fMode               = sc.unsigned_char  # 0x00=TrainerControl 0x02=SpecialMode 0x04=PCmode
    fReserved           = sc.pad * 5

    format = sc.big_endian +    fChannel + fDataPageNumber + fCommand + fMode + fReserved
    info   = struct.pack(format, Channel,   DataPageNumber,   0x03,      Mode)

    return info

def msgUnpage221_TacxVortexHU_ButtonPressed (info):
    fChannel            = sc.unsigned_char  # 0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # 1 First byte of the ANT+ datapage (payload)
    fCommand            = sc.unsigned_char  # 2 0x10 Button press

    nButton             = 3
    fButton             = sc.unsigned_char  # 3 Button 1...5

    fReserved           = sc.pad * 4        # -
    fCount              = sc.unsigned_char  # 4

    format = sc.big_endian +    fChannel + fDataPageNumber + fCommand + fButton + fReserved + fCount
    tuple = struct.unpack (format, info)

    return tuple[nButton]

# -------------------------------------------------------------------------------------
# P a g e 1 7 3  ( 0 x 0 1 )  T a c x V o r t e x S e r i a l M o d e
# -------------------------------------------------------------------------------------
def msgUnpage173_01_TacxVortexHU_SerialMode (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char  # == 0x01

    fMode               = sc.unsigned_char  # head-unit mode
    nMode               = 3
    fYear               = sc.unsigned_char  # production year
    nYear               = 4
    fDeviceType         = sc.unsigned_char  # device type id
    nDeviceType         = 5
    fDeviceNumber       = '3' + sc.char_array  # device number
    nDeviceNumber       = 6

    format = sc.big_endian + fChannel + fDataPageNumber + fSubPageNumber + \
             fMode + fYear + fDeviceType + fDeviceNumber
    tuple = struct.unpack(format, info)

    deviceNumber = int.from_bytes(tuple[nDeviceNumber], byteorder='big')

    return tuple[nMode], tuple[nYear], tuple[nDeviceType], deviceNumber

# ------------------------------------------------------------------------------
# T a c x  G e n i u s  p a g e s
# ------------------------------------------------------------------------------
# Refer:    https://gist.github.com/switchabl/75b2619e2e3381f49425479d59523ead
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# P a g e 2 2 0  ( 0 x 0 1 )  T a c x G e n i u s S e t T a r g e t
# ------------------------------------------------------------------------------
def msgPage220_01_TacxGeniusSetTarget (Channel, Mode, Target, Weight):
    DataPageNumber      = 220
    SubPageNumber       = 0x01
    Weight              = int(max(0,min(0xff, Weight)))    #381/1 Avoid negative weigth
    if Mode == GNS_Mode_Slope:
        Target = int(Target * 10)
    else:
        Target = int(Target)

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char
    fMode               = sc.unsigned_char  # brake mode (slope/power/heart rate)
    fTarget             = sc.short          # target slope (%) * 10/power (W)/HR (bpm)
    fWeight             = sc.unsigned_char  # user + bike weight (kg)
    fPadding            = sc.pad * 2

    format = sc.big_endian +     fChannel + fDataPageNumber + fSubPageNumber + fMode + fTarget + fWeight + fPadding
    info   = struct.pack (format, Channel,   DataPageNumber,   SubPageNumber,   Mode,   Target,   Weight)

    return info

# ------------------------------------------------------------------------------
# P a g e 2 2 0  ( 0 x 0 2 )  T a c x G e n i u s W i n d R e s i s t a n c e
# ------------------------------------------------------------------------------
def msgPage220_02_TacxGeniusWindResistance (Channel, WindResistance, WindSpeed):
    DataPageNumber      = 220
    SubPageNumber       = 0x02
    WindResistance      = int(WindResistance)
    WindSpeed           = int(WindSpeed)

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char
    fWindResistance     = sc.unsigned_short # 0.5 * wind resistance cofficient (kg/m) * 1000
    fWindSpeed          = sc.short          # wind speed (m/s) * 250 (head wind = negative)
    fPadding            = sc.pad * 2

    format = sc.big_endian +     fChannel + fDataPageNumber + fSubPageNumber + fWindResistance + fWindSpeed + fPadding
    info   = struct.pack (format, Channel,   DataPageNumber,   SubPageNumber,   WindResistance,   WindSpeed)

    return info

# ------------------------------------------------------------------------------
# P a g e 2 2 0  ( 0 x 0 4 )  T a c x G e n i u s C a l i b r a t i o n
# ------------------------------------------------------------------------------
def msgPage220_04_TacxGeniusCalibration (Channel, Action):
    DataPageNumber      = 220
    SubPageNumber       = 0x04

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char
    fAction             = sc.unsigned_char  # Calibration action
    fPadding            = sc.pad * 5

    format = sc.big_endian +     fChannel + fDataPageNumber + fSubPageNumber + fAction + fPadding
    info   = struct.pack (format, Channel,   DataPageNumber,   SubPageNumber,   Action)

    return info

# -------------------------------------------------------------------------------------
# P a g e 2 2 1  ( 0 x 0 1 )  T a c x G e n i u s S p e e d / P o w e r / C a d e n c e
# -------------------------------------------------------------------------------------
def msgUnpage221_01_TacxGeniusSpeedPowerCadence (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char  # == 0x01

    fSpeed              = sc.unsigned_short # speed (km/h) * 10
    nSpeed              = 3
    fPower              = sc.unsigned_short # power (W)
    nPower              = 4
    fCadence            = sc.unsigned_char  # cadence (rpm)
    nCadence            = 5
    fBalance            = sc.unsigned_char  # L/R power balance (%)
    nBalance            = 6

    format = sc.big_endian + fChannel + fDataPageNumber + fSubPageNumber + \
             fSpeed + fPower + fCadence + fBalance
    tuple = struct.unpack(format, info)

    return tuple[nPower], tuple[nSpeed], tuple[nCadence], tuple[nBalance]

# -------------------------------------------------------------------------------------
# P a g e 2 2 1  ( 0 x 0 2 )  T a c x G e n i u s D i s t a n c e H R
# -------------------------------------------------------------------------------------
def msgUnpage221_02_TacxGeniusDistanceHR (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char  # == 0x02

    fDistance           = sc.unsigned_int   # distance (m)
    nDistance           = 3
    fHeartrate          = sc.unsigned_char  # heartrate (bpm) (Vortex/Bushido only?)
    nHeartrate          = 4
    fPadding            = sc.pad

    format = sc.big_endian + fChannel + fDataPageNumber + fSubPageNumber + \
             fDistance + fHeartrate + fPadding
    tuple = struct.unpack(format, info)

    return tuple[nDistance], tuple[nHeartrate]

# -------------------------------------------------------------------------------------
# P a g e 2 2 1  ( 0 x 0 3 )  T a c x G e n i u s A l a r m T e m p e r a t u r e
# -------------------------------------------------------------------------------------
def msgUnpage221_03_TacxGeniusAlarmTemperature (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char  # == 0x03

    fAlarm              = sc.unsigned_short # alarm bitmask
    nAlarm              = 3
    fTemperature        = sc.unsigned_char  # brake temperature (°C ?)
    nTemperature        = 4
    fPowerback          = sc.unsigned_short # Powerback (W)
    nPowerback          = 5
    fPadding            = sc.pad

    format = sc.big_endian + fChannel + fDataPageNumber + fSubPageNumber + \
             fAlarm + fTemperature + fPowerback + fPadding
    tuple = struct.unpack(format, info)

    return tuple[nAlarm], tuple[nTemperature], tuple[nPowerback]

# -------------------------------------------------------------------------------------
# P a g e 2 2 1  ( 0 x 0 4 )  T a c x G e n i u s C a l i b r a t i o n I n f o
# -------------------------------------------------------------------------------------
def msgUnpage221_04_TacxGeniusCalibrationInfo (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char  # == 0x04

    fCalibrationState   = sc.unsigned_char  # calibration status
    nCalibrationState   = 3
    fCalibrationValue   = sc.unsigned_short  # brake temperature (°C ?)
    nCalibrationValue   = 4
    fPadding            = 3 * sc.pad

    format = sc.big_endian + fChannel + fDataPageNumber + fSubPageNumber + \
             fCalibrationState + fCalibrationValue + fPadding
    tuple = struct.unpack(format, info)

    return tuple[nCalibrationState], tuple[nCalibrationValue]

# -------------------------------------------------------------------------------------
# P a g e 1 7 3  ( 0 x 0 1 )  T a c x B u s h i d o S e r i a l M o d e
# -------------------------------------------------------------------------------------
def msgUnpage173_01_TacxBushidoSerialMode (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSubPageNumber      = sc.unsigned_char  # == 0x01

    fMode               = sc.unsigned_char  # head unit mode
    nMode               = 3
    fYear               = sc.unsigned_char  # production year
    nYear               = 4
    fDeviceNumber       = sc.int            # device number
    nDeviceNumber       = 5

    format = sc.big_endian + fChannel + fDataPageNumber + fSubPageNumber + \
             fMode + fYear + fDeviceNumber
    tuple = struct.unpack(format, info)

    return tuple[nMode], tuple[nYear], tuple[nDeviceNumber]

# ------------------------------------------------------------------------------
# P a g e 1 6   G e n e r a l   F E   i n f o
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
#  trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
#           Data page 16 (0x10) General FE Data
# Notes:    Even though HRM is defined, it appears not being picked up by
#           Trainer Road.
# ------------------------------------------------------------------------------
def msgPage16_GeneralFEdata (Channel, ElapsedTime, DistanceTravelled, Speed, HeartRate):
    DataPageNumber      = 16
    EquipmentType       = 0x19      # Trainer
    ElapsedTime         = int(min(  0xff, ElapsedTime       ))
    DistanceTravelled   = int(min(  0xff, DistanceTravelled ))
    Speed               = int(min(0xffff, Speed             ))
    HeartRate           = int(min(  0xff, HeartRate         ))

    # Old: Capabilities = 0x30 | 0x03 | 0x00 | 0x00 # IN_USE | HRM | Distance | Speed
    #               bit  7......0   #185 Rewritten as below for better documenting bit-pattern
    # HRM            = 0b00000011 # 0b____ __xx bits 0-1  3 = hand contact sensor    (2020-12-28: Unclear why this option chosen)
    HRM              = 0b00000001 # 0b____ __xx bits 0-1  1 = HRM                    (2024-01-22: #381/3 transmit HRM through FE-C)
    Distance         = 0b00000000 # 0b____ _x__ bit 2     0 = No distance in byte 3  (2020-12-28: Unclear why this option chosen)
    VirtualSpeedFlag = 0b00000000 # 0b____ x___ bit 3     0 = Real speed in byte 4/5 (2020-12-28: Could be virtual speed)
    FEstate          = 0b00110000 # 0b_xxx ____ bits 4-6  3 = IN USE
    LapToggleBit     = 0b00000000 # 0bx___ ____ bit 7     0 = No lap toggle

    Capabilities = HRM | Distance | VirtualSpeedFlag | FEstate | LapToggleBit

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fEquipmentType      = sc.unsigned_char
    fElapsedTime        = sc.unsigned_char
    fDistanceTravelled  = sc.unsigned_char
    fSpeed              = sc.unsigned_short
    fHeartRate          = sc.unsigned_char
    fCapabilities       = sc.unsigned_char

    format=   sc.no_alignment+fChannel+fDataPageNumber+fEquipmentType+fElapsedTime+fDistanceTravelled+fSpeed+fHeartRate+fCapabilities
    info  =struct.pack(format, Channel, DataPageNumber, EquipmentType, ElapsedTime, DistanceTravelled, Speed, HeartRate, Capabilities)

    return info

def msgUnpage16_GeneralFEdata (info):
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  #1 First byte of the ANT+ datapage (payload)
    fEquipmentType      = sc.unsigned_char  #2
    fElapsedTime        = sc.unsigned_char  #3
    fDistanceTravelled  = sc.unsigned_char  #4
    fSpeed              = sc.unsigned_short #5
    fHeartRate          = sc.unsigned_char  #6
    fCapabilities       = sc.unsigned_char  #7

    format=   sc.no_alignment+fChannel+fDataPageNumber+fEquipmentType+fElapsedTime+fDistanceTravelled+fSpeed+fHeartRate+fCapabilities
    tuple = struct.unpack (format, info)

    return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6], tuple[7]

# ------------------------------------------------------------------------------
# P a g e 2 5   T r a i n e r   i n f o
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
#  trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
#           Data page 25 (0x19) Specific Trainer/Stationary Bike Data
# ------------------------------------------------------------------------------
def msgPage25_TrainerData(Channel, EventCounter, Cadence, AccumulatedPower, CurrentPower):
    DataPageNumber      = 25
    EventCounter        = int(       min(  0xff, EventCounter      ))
    Cadence             = int(       min(  0xff, Cadence           ))
    AccumulatedPower    = int(       min(0xffff, AccumulatedPower  ))
    CurrentPower        = int(max(0, min(0x0fff, CurrentPower      )))  # 2021-02-19
    Flags               = 0x30          # Hmmm.... leave as is but do not understand the value

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fEvent              = sc.unsigned_char
    fCadence            = sc.unsigned_char
    fAccPower           = sc.unsigned_short
    fInstPower          = sc.unsigned_short # The first four bits have another meaning!!
    fFlags              = sc.unsigned_char

    format=    sc.no_alignment + fChannel + fDataPageNumber + fEvent +      fCadence + fAccPower +       fInstPower +  fFlags
    info  = struct.pack (format,  Channel,   DataPageNumber,   EventCounter, Cadence,   AccumulatedPower, CurrentPower, Flags)

    return info

def msgUnpage25_TrainerData(info):
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  #1 First byte of the ANT+ datapage (payload)
    fEvent              = sc.unsigned_char  #2
    fCadence            = sc.unsigned_char  #3
    fAccPower           = sc.unsigned_short #4
    fInstPower          = sc.unsigned_short #5 The first four bits have another meaning!!
    fFlags              = sc.unsigned_char  #6

    format= sc.no_alignment + fChannel + fDataPageNumber + fEvent + fCadence + fAccPower + fInstPower + fFlags
    tuple = struct.unpack (format, info)

    return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6]

# ------------------------------------------------------------------------------
# P a g e 4 8   B a s i c R e s i s t a n c e
# ------------------------------------------------------------------------------
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# Data page 48 (0x30) Basic Resistance
# ------------------------------------------------------------------------------
def msgUnpage48_BasicResistance(info):
    _nChannel           = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content

    _nDataPageNumber    = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)

    fReserved           = sc.pad * 6

    nTotalResistance    = 2
    fTotalResistance    = sc.unsigned_char

    format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fTotalResistance
    tuple  = struct.unpack (format, info)

    rtn = tuple[nTotalResistance] * 0.005    # 0 ... 100%

    return rtn

# ------------------------------------------------------------------------------
# P a g e 4 9   T a r g e t P o w e r
# ------------------------------------------------------------------------------
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# Data page 49 (0x31) Target Power
# ------------------------------------------------------------------------------
def msgUnpage49_TargetPower(info):
    _nChannel           = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content

    _nDataPageNumber    = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)

    fReserved           = sc.pad * 5

    nTargetPower        = 2
    fTargetPower        = sc.unsigned_short # units of 0.25Watt

    format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fTargetPower
    tuple  = struct.unpack (format, info)

    TargetPower = tuple[nTargetPower] / 4   # returns units of 1Watt

    return TargetPower

# ------------------------------------------------------------------------------
# P a g e 5 0   W i n d R e s i s t a n c e
# ------------------------------------------------------------------------------
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# Data page 50 (0x32) Wind Resistance
# ------------------------------------------------------------------------------
def msgUnpage50_WindResistance(info):
    _nChannel           = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content

    _nDataPageNumber    = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)

    fReserved           = sc.pad * 4

    nWindResistanceCoefficient = 2
    fWindResistanceCoefficient = sc.unsigned_char

    nWindSpeed          = 3
    fWindSpeed          = sc.unsigned_char

    nDraftingFactor     = 4
    fDraftingFactor     = sc.unsigned_char

    format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fWindResistanceCoefficient + fWindSpeed + fDraftingFactor
    tuple  = struct.unpack (format, info)

    WindResistance = tuple[nWindResistanceCoefficient]
    if WindResistance == 0xff:
        WindResistance = 0.51
    else:
        WindResistance = WindResistance * 0.01 # kg/m

    WindSpeed = tuple[nWindSpeed]
    if WindSpeed == 0xff:
        WindSpeed = 0.0
    else:
        WindSpeed = WindSpeed - 127 # km/h

    DraftingFactor = tuple[nDraftingFactor]
    if DraftingFactor == 0xff:
        DraftingFactor = 1.0
    else:
        DraftingFactor = DraftingFactor * 0.01

    return WindResistance, WindSpeed, DraftingFactor

# ------------------------------------------------------------------------------
# P a g e 5 1   T r a c k R e s i s t a n c e
# ------------------------------------------------------------------------------
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# Data page 51 (0x33) Target Resistance
# ------------------------------------------------------------------------------
def msgUnpage51_TrackResistance(info):
    _nChannel           = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content

    _nDataPageNumber    = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)

    fReserved           = sc.pad * 4

    nGrade              = 2
    fGrade              = sc.unsigned_short

    nRollingResistance  = 3
    fRollingResistance  = sc.unsigned_char

    format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fGrade + fRollingResistance
    tuple  = struct.unpack (format, info)

    Grade = tuple[nGrade]
    if Grade == 0xffff: Grade = 0
    Grade = Grade * 0.01 - 200          # -200% - 200%, units 0.01%
    Grade = round(Grade,2)

    RollingResistance = tuple[nRollingResistance]
    if RollingResistance == 0xff:
        RollingResistance = 0.004
    else:
        RollingResistance = RollingResistance * 0.00005

    return Grade, RollingResistance

# ------------------------------------------------------------------------------
# P a g e 5 5   U s e r   C o n f i g u r a t i o n
# ------------------------------------------------------------------------------
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# Data page 55 (0x37) User Configuration
# ------------------------------------------------------------------------------
def msgUnpage55_UserConfiguration(info):
    _nChannel           = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content

    _nDataPageNumber    = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)

    nUserWeight         = 2
    fUserWeight         = sc.unsigned_short

    fReserved           = sc.pad

    nBicycleInfo        = 3
    fBicycleInfo        = sc.unsigned_short

    nBicycleWheelDiameter= 4
    fBicycleWheelDiameter= sc.unsigned_char

    nGearRatio          = 5
    fGearRatio          = sc.unsigned_char

    format = sc.no_alignment + fChannel + fDataPageNumber + fUserWeight + fReserved + fBicycleInfo + fBicycleWheelDiameter + fGearRatio
    tuple  = struct.unpack (format, info)

    UserWeigth                = tuple[nUserWeight] * 0.01                # 0 ... 655.34 kg

    BicycleInfo               = tuple[nBicycleInfo]
    _BicyleWheelDiameterOffset= (BicycleInfo & 0x000f)                   # 0 - 10 mm
    BicycleWeigth             = (BicycleInfo & 0xfff0) / 16 * 0.05       # 0 - 50 kg

    BicyleWheelDiameter       = tuple[nBicycleWheelDiameter] * 0.01      # 0 - 2.54m

    GearRatio                 = tuple[nGearRatio] * 0.03                 # 0.03 - 7.65

    return UserWeigth, BicycleWeigth, BicyleWheelDiameter, GearRatio

# ------------------------------------------------------------------------------
# P a g e 7 0 _ R e q u e s t D a t a P a g e
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common Data Page 70: (0x46) RequestDataPage
# ------------------------------------------------------------------------------
def msgPage70_RequestDataPage(Channel, SlaveSerialNumber, DescriptorByte1, \
                DescriptorByte2, NrTimes, RequestedPageNumber, CommandType):
    DataPageNumber      = 70

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSlaveSerialNumber  = sc.unsigned_short
    fDescriptorByte1    = sc.unsigned_char
    fDescriptorByte2    = sc.unsigned_char
    fReqTransmissionResp= sc.unsigned_char
    fRequestedPageNumber= sc.unsigned_char
    fCommandType        = sc.unsigned_char

    format=    sc.no_alignment + fChannel + fDataPageNumber + fSlaveSerialNumber + fDescriptorByte1 + \
               fDescriptorByte2 + fReqTransmissionResp + fRequestedPageNumber + fCommandType

    info  = struct.pack (format,  Channel,   DataPageNumber,   SlaveSerialNumber,   DescriptorByte1,  \
                DescriptorByte2,   NrTimes,               RequestedPageNumber,   CommandType)

    return info

def msgUnpage70_RequestDataPage(info):
    _nChannel           = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content

    _nDataPageNumber    = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)

    nSlaveSerialNumber  = 2
    fSlaveSerialNumber  = sc.unsigned_short

    nDescriptorByte1    = 3
    fDescriptorByte1    = sc.unsigned_char

    nDescriptorByte2    = 4
    fDescriptorByte2    = sc.unsigned_char

    nReqTransmissionResp= 5
    fReqTransmissionResp= sc.unsigned_char

    nRequestedPageNumber= 6
    fRequestedPageNumber= sc.unsigned_char

    nCommandType        = 7
    fCommandType        = sc.unsigned_char

    format = sc.no_alignment + fChannel + fDataPageNumber + fSlaveSerialNumber + \
             fDescriptorByte1 + fDescriptorByte2 + fReqTransmissionResp + \
             fRequestedPageNumber + fCommandType
    tuple  = struct.unpack (format, info)

    ReqTranmissionResponse = tuple[nReqTransmissionResp]
    AckRequired         = ReqTranmissionResponse & 0x80
    NrTimes             = ReqTranmissionResponse & 0x7f

    return tuple[nSlaveSerialNumber], tuple[nDescriptorByte1], tuple[nDescriptorByte2], \
           AckRequired, NrTimes, tuple[nRequestedPageNumber], tuple[nCommandType]

# ------------------------------------------------------------------------------
# P a g e 5 4 _ F E   C a p a b i l i t i e s
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# ------------------------------------------------------------------------------
def msgPage54_FE_Capabilities(Channel, Reserved1, Reserved2, Reserved3, Reserved4, MaximumResistance, CapabilitiesBits):
    DataPageNumber      = 54

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char
    fReserved2          = sc.unsigned_char
    fReserved3          = sc.unsigned_char
    fReserved4          = sc.unsigned_char
    fMaximumResistance  = sc.unsigned_short
    fCapabilitiesBits   = sc.unsigned_char

    format=    sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fReserved2 + fReserved3 + fReserved4 + fMaximumResistance + fCapabilitiesBits
    info  = struct.pack (format,  Channel,   DataPageNumber,   Reserved1 ,  Reserved2 ,  Reserved3 ,  Reserved4 ,  MaximumResistance,   CapabilitiesBits)

    return info

# ------------------------------------------------------------------------------
# P a g e 7 1 _ C o m m a n d S t a t u s
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# ------------------------------------------------------------------------------
def msgPage71_CommandStatus(Channel, LastReceivedCommandID, SequenceNr, CommandStatus, Data1, Data2, Data3, Data4):
    DataPageNumber          = 71

    fChannel                = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber         = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fLastReceivedCommandID  = sc.unsigned_char
    fSequenceNr             = sc.unsigned_char
    fCommandStatus          = sc.unsigned_char
    fData1                  = sc.unsigned_char
    fData2                  = sc.unsigned_char
    fData3                  = sc.unsigned_char
    fData4                  = sc.unsigned_char

    format=    sc.no_alignment + fChannel + fDataPageNumber + fLastReceivedCommandID + fSequenceNr + fCommandStatus + fData1 + fData2 + fData3 + fData4
    info  = struct.pack (format,  Channel,   DataPageNumber,   LastReceivedCommandID,   SequenceNr,   CommandStatus,   Data1,   Data2,   Data3,   Data4)

    return info

# ------------------------------------------------------------------------------
# P a g e 7 3 _ G e n e r i c C o m m a n d
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# ------------------------------------------------------------------------------
def msgPage73_GenericCommand(Channel, SlaveSerialNumber, SlaveManufacturerID, SequencNr, CommandNr):
    DataPageNumber          = 73

    fChannel                = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber         = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSlaveSerialNumber      = sc.unsigned_short
    fSlaveManufacturerID    = sc.unsigned_short
    fSequenceNr             = sc.unsigned_char
    fCommandNr              = sc.unsigned_short

    format=    sc.no_alignment + fChannel + fDataPageNumber + fSlaveSerialNumber + fSlaveManufacturerID + fSequenceNr +\
               fCommandNr
    info  = struct.pack (format,  Channel,   DataPageNumber,   SlaveSerialNumber,   SlaveManufacturerID,   SequencNr,
                         CommandNr)

    return info

def msgUnpage73_GenericCommand (info):
    fChannel                = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber         = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSlaveSerialNumber      = sc.unsigned_short
    fSlaveManufacturerID    = sc.unsigned_short
    fSequenceNr             = sc.unsigned_char
    fCommandNr              = sc.unsigned_short

    format=    sc.no_alignment + fChannel + fDataPageNumber + fSlaveSerialNumber + fSlaveManufacturerID + fSequenceNr + \
               fCommandNr
    tuple = struct.unpack (format, info)

    return tuple[2], tuple[3], tuple[4], tuple[5]

# ------------------------------------------------------------------------------
# P a g e 8 0 _ M a n u f a c t u r e r I n f o
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common Data Page 80: (0x50) Manufacturers Information
# ------------------------------------------------------------------------------
def msgPage80_ManufacturerInfo(Channel, Reserved1, Reserved2, HWrevision, ManufacturerID, ModelNumber):
    DataPageNumber      = 80

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char
    fReserved2          = sc.unsigned_char
    fHWrevision         = sc.unsigned_char
    fManufacturerID     = sc.unsigned_short
    fModelNumber        = sc.unsigned_short

    # page 28 byte 4,5,6,7- 15=dynastream, 89=tacx
    # antifier used 15 : "a4 09 4e 00 50 ff ff 01 0f 00 85 83 bb"
    # we use 89 (tacx) with the same ModelNumber
    #
    # Should be variable and caller-supplied; perhaps it influences pairing
    # when trainer-software wants a specific device?
    #
    format=    sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fReserved2 + fHWrevision + fManufacturerID + fModelNumber
    info  = struct.pack (format,  Channel,   DataPageNumber,   Reserved1,   Reserved2,   HWrevision,   ManufacturerID,   ModelNumber)

    return info

def msgUnpage80_ManufacturerInfo(info):
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  #1 First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char  #2
    fReserved2          = sc.unsigned_char  #3
    fHWrevision         = sc.unsigned_char  #4
    fManufacturerID     = sc.unsigned_short #5
    fModelNumber        = sc.unsigned_short #6

    format= sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fReserved2 + fHWrevision + fManufacturerID + fModelNumber
    tuple = struct.unpack (format, info)

    return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6]

# ------------------------------------------------------------------------------
# P a g e 8 1   P r o d u c t I n f o r m a t i o n
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common Data Page 81: (0x51) Product Information
# ------------------------------------------------------------------------------
def msgPage81_ProductInformation(Channel, Reserved1, SWrevisionSupp, SWrevisionMain, SerialNumber):
    DataPageNumber      = 81

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char
    fSWrevisionSupp     = sc.unsigned_char
    fSWrevisionMain     = sc.unsigned_char
    fSerialNumber       = sc.unsigned_int

    format=    sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fSWrevisionSupp + fSWrevisionMain + fSerialNumber
    info  = struct.pack (format,  Channel,   DataPageNumber,   Reserved1,   SWrevisionSupp,   SWrevisionMain,   SerialNumber)

    return info

def msgUnpage81_ProductInformation(info):
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  #1 First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char  #2
    fSWrevisionSupp     = sc.unsigned_char  #3
    fSWrevisionMain     = sc.unsigned_char  #4
    fSerialNumber       = sc.unsigned_int   #5

    format= sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fSWrevisionSupp + fSWrevisionMain + fSerialNumber
    tuple = struct.unpack (format, info)

    return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5]

# ------------------------------------------------------------------------------
# P a g e 8 2   B a t t e r y S t a t u s
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common Data Page 82: (0x52) Battery Status
# ------------------------------------------------------------------------------
def msgPage82_BatteryStatus(Channel):
    DataPageNumber      = 82

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char
    fBatteryIdentifier  = sc.unsigned_char
    fCumulativeTime1    = sc.unsigned_char
    fCumulativeTime2    = sc.unsigned_char
    fCumulativeTime3    = sc.unsigned_char
    fBatteryVoltage     = sc.unsigned_char
    fDescriptiveBitField= sc.unsigned_char

    format=    sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fBatteryIdentifier + \
                fCumulativeTime1 + fCumulativeTime2 + fCumulativeTime3 + \
                fBatteryVoltage + fDescriptiveBitField
    info  = struct.pack (format, Channel, DataPageNumber, 0xff, 0x00, 0,0,0, 0, 0x0f | 0x10 | 0x00)

    return info

# ------------------------------------------------------------------------------
# P a g e 0, 1, 2   H e a r t R a t e I n f o
# ------------------------------------------------------------------------------
# https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00000693_-_ANT+_Device_Profile_-_Heart_Rate_Rev_2.1.pdf
# ------------------------------------------------------------------------------
def msgPage_Hrm (Channel, DataPageNumber, Spec1, Spec2, Spec3, HeartBeatEventTime, HeartBeatCount, HeartRate):
    DataPageNumber      = int(min(  0xff, DataPageNumber     ))
    Spec1               = int(min(  0xff, Spec1              ))
    Spec2               = int(min(  0xff, Spec2              ))
    Spec3               = int(min(  0xff, Spec3              ))
    HeartBeatEventTime  = int(min(0xffff, HeartBeatEventTime * 1000/1024))  # Convert seconds into 1024seconds (since ever)
    HeartBeatCount      = int(min(  0xff, HeartBeatCount     ))
    HeartRate           = int(min(  0xff, HeartRate          ))

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fSpec1              = sc.unsigned_char
    fSpec2              = sc.unsigned_char
    fSpec3              = sc.unsigned_char
    fHeartBeatEventTime = sc.unsigned_short
    fHeartBeatCount     = sc.unsigned_char
    fHeartRate          = sc.unsigned_char

    format      = sc.no_alignment + fChannel + fDataPageNumber + fSpec1 + fSpec2 + fSpec3 + fHeartBeatEventTime +  fHeartBeatCount + fHeartRate
    info        = struct.pack (format, Channel, DataPageNumber,   Spec1,   Spec2,   Spec3,   HeartBeatEventTime,    HeartBeatCount,   HeartRate)

    return info

def msgUnpage_Hrm (info):
    fChannel            = sc.unsigned_char  #0 First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  #1 First byte of the ANT+ datapage (payload)
    fSpec1              = sc.unsigned_char  #2
    fSpec2              = sc.unsigned_char  #3
    fSpec3              = sc.unsigned_char  #4
    fHeartBeatEventTime = sc.unsigned_short #5
    fHeartBeatCount     = sc.unsigned_char  #6
    fHeartRate          = sc.unsigned_char  #7

    format      = sc.no_alignment + fChannel + fDataPageNumber + fSpec1 + fSpec2 + fSpec3 + fHeartBeatEventTime +  fHeartBeatCount + fHeartRate
    tuple = struct.unpack (format, info)

    return tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6], tuple[7]

# ------------------------------------------------------------------------------
# P a g e 0   S p e e d C a d e n c e S e n s o r
# ------------------------------------------------------------------------------
# https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001163_-_ANT+_Device_Profile_-_Bicycle_Speed_and_Cadence_2.1.pdf
# ------------------------------------------------------------------------------
def msgPage_SCS (Channel, CadenceEventTime, CadenceRevolutionCount, SpeedEventTime, SpeedRevolutionCount):
    _DataPageNumber         = 0
    CadenceEventTime        = int(min(0xffff, CadenceEventTime      ))
    CadenceRevolutionCount  = int(min(0xffff, CadenceRevolutionCount))
    SpeedEventTime          = int(min(0xffff, SpeedEventTime        ))
    SpeedRevolutionCount    = int(min(0xffff, SpeedRevolutionCount  ))

    fChannel                = sc.unsigned_char  # First byte of the ANT+ message content
    _fDataPageNumber        = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fCadenceEventTime       = sc.unsigned_short
    fCadenceRevolutionCount = sc.unsigned_short
    fSpeedEventTime         = sc.unsigned_short
    fSpeedRevolutionCount   = sc.unsigned_short

    format      = sc.no_alignment + fChannel + fCadenceEventTime + \
                        fCadenceRevolutionCount + fSpeedEventTime + fSpeedRevolutionCount
    info        = struct.pack (format, Channel, CadenceEventTime,   \
                        CadenceRevolutionCount,    SpeedEventTime,   SpeedRevolutionCount)

    return info

def msgUnpage_SCS (info):
    fChannel                = sc.unsigned_char  # First byte of the ANT+ message content
    _fDataPageNumber        = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fCadenceEventTime       = sc.unsigned_short
    fCadenceRevolutionCount = sc.unsigned_short
    fSpeedEventTime         = sc.unsigned_short
    fSpeedRevolutionCount   = sc.unsigned_short

    format      = sc.no_alignment + fChannel + fCadenceEventTime + \
                        fCadenceRevolutionCount + fSpeedEventTime + fSpeedRevolutionCount
    tuple = struct.unpack (format, info)

    #      EventTime, CadenceRevolutionCount, EventTime, SpeedRevolutionCount
    return tuple[1],  tuple[2],               tuple[3],  tuple[4]

# ------------------------------------------------------------------------------
# P a g e 2   C o n t r o l
# ------------------------------------------------------------------------------
# https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001307_-_ANT+_Device_Profile_-_Controls_-_2.0.pdf
# ------------------------------------------------------------------------------
def msgPage2_CTRL (Channel, CurrentNotifcations, Reserved1, Reserved2, Reserved3, Reserved4, Reserved5,
                   DeviceCapabilities):
    DataPageNumber         = 2

    fChannel                = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber         = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fCurrentNotifications   = sc.unsigned_char
    fReserved1              = sc.unsigned_char
    fReserved2              = sc.unsigned_char
    fReserved3              = sc.unsigned_char
    fReserved4              = sc.unsigned_char
    fReserved5              = sc.unsigned_char
    fDeviceCapabilities     = sc.unsigned_char

    format      = sc.no_alignment + fChannel + fDataPageNumber + fCurrentNotifications + fReserved1 + fReserved2 + \
                  fReserved3 + fReserved4 + fReserved5 + fDeviceCapabilities
    info        = struct.pack (format, Channel, DataPageNumber, CurrentNotifcations, Reserved1, Reserved2, Reserved3,
                               Reserved4, Reserved5, DeviceCapabilities)

    return info

# ------------------------------------------------------------------------------
# T a c x  B l a c k T r a c k  p a g e s
# ------------------------------------------------------------------------------
# Refer:    https://gist.github.com/switchabl/75b2619e2e3381f49425479d59523ead
# ------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# P a g e 0 0  T a c x B l a c k T r a c k A n g l e
# -------------------------------------------------------------------------------------
def msgUnpage00_TacxBlackTrackAngle (info):
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)

    fAngle              = sc.short # raw angle
    nAngle              = 2
    fReserved           = sc.unsigned_char # always 0xff (?)
    nReserved           = 3
    fPadding            = 4 * sc.pad

    format = sc.big_endian + fChannel + fDataPageNumber + fAngle + fReserved + fPadding
    tuple = struct.unpack(format, info)

    return tuple[nAngle], tuple[nReserved]

# ------------------------------------------------------------------------------
# P a g e 0 1  T a c x B l a c k T r a c k K e e p A l i v e
# ------------------------------------------------------------------------------
def msgPage01_TacxBlackTrackKeepAlive (Channel):
    DataPageNumber      = 0x01

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fPadding            = sc.pad * 7

    format = sc.big_endian +     fChannel + fDataPageNumber + fPadding
    info   = struct.pack (format, Channel,   DataPageNumber)

    return info
