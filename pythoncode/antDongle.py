#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-04-14b"
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
#-------------------------------------------------------------------------------
import binascii
import glob
import os
import platform
import re
if platform.system() == 'False':
    import serial
import struct
import usb.core
import time

import debug
import logfile
import structConstants      as sc

import FortiusAntCommand    as cmd

#-------------------------------------------------------------------------------
# Our own choice what channels are used
#
# A different channel is used for HRM as HRM_d, even though usually a device 
# will be either one or the other. ExplorANT can be both.
#-------------------------------------------------------------------------------
channel_FE          = 1        # ANT+ channel for Fitness Equipment
channel_HRM         = 2        # ANT+ channel for Heart Rate Monitor
channel_SCS         = 3        # ANT+ Channel for Speed Cadence Sensor

channel_FE_s        = 4        # ANT+ channel for Fitness Equipment    (slave=Cycle Training Program)
channel_HRM_s       = 5        # ANT+ channel for Heart Rate Monitor   (slave=display)
channel_SCS_s       = 6        # ANT+ Channel for Speed Cadence Sensor (slave=display)

DeviceNumber_EA     = 57590    # short Slave device-number for ExplorANT
DeviceNumber_FE     = 57591    #       These are the device-numbers FortiusANT uses and
DeviceNumber_HRM    = 57592    #       slaves (TrainerRoad, Zwift, ExplorANT) will find.

ModelNumber_FE      = 2875     # short antifier-value=0x8385, Tacx Neo=2875
SerialNumber_FE     = 19590705 # int   1959-7-5
HWrevision_FE       = 1        # char
SWrevisionMain_FE   = 1        # char
SWrevisionSupp_FE   = 1        # char

ModelNumber_HRM     = 0x33     # char  antifier-value
SerialNumber_HRM    = 5975     # short 1959-7-5
HWrevision_HRM      = 1        # char
SWversion_HRM       = 1        # char

if False:                      # Tacx Neo Erik OT; perhaps relevant for Tacx Desktop App
                               # because TDA does not want to pair with FortiusAnt...
    DeviceNumber_FE = 48365
    SerialNumber_FE = 48365

#-------------------------------------------------------------------------------
# D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
# 5.2.1 Channel Type
# 5.3   Establishing a channel (defines master/slave)
# 9.3   ANT Message summary
#-------------------------------------------------------------------------------
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

msgID_AssignChannel                     = 0x42
msgID_ChannelPeriod                     = 0x43
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


DeviceTypeID_FE         = DeviceTypeID_fitness_equipment
DeviceTypeID_HRM        = DeviceTypeID_heart_rate
DeviceTypeID_SCS        = DeviceTypeID_bike_speed_cadence

TransmissionType_IC     = 0x01          # 5.2.3.1   Transmission Type
TransmissionType_IC_GDP = 0x05          #           0x01 = Independant Channel
                                        #           0x04 = Global datapages used
TransmitPower_0dBm      = 0x03          # 9.4.3     Output Power Level Settings
RfFrequency_2457Mhz     =   57          # 9.5.2.6   Channel RF Frequency
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
# Standard dongle commands
# Observation: all commands have two bytes 00 00 for which purpose is unclear
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
#   ANT:     D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
#   trainer: D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
#   hrm:     D00000693_-_ANT+_Device_Profile_-_Heart_Rate_Rev_2.1.pdf
#-------------------------------------------------------------------------------
def Calibrate(devAntDongle):
  if debug.on(debug.Data1): logfile.Write ("Calibrate()")
  
  ResetDongle(devAntDongle)
  
  messages=[
    msg4D_RequestMessage        (0, msgID_Capabilities),   # request max channels
#   msg4A_ResetSystem           (),
    msg4D_RequestMessage        (0, msgID_ANTversion),     # request ant version
    msg46_SetNetworkKey         ()
  ]
  SendToDongle(messages,devAntDongle)
  
def SlavePair_ChannelConfig(devAntDongle, channel_pair):
  if debug.on(debug.Data1): logfile.Write ("SlavePair_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_pair, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
    msg51_ChannelID             (channel_pair, 0, 0, 0), # Slave, full wildcards ChannelID, see msg51 comment
    msg45_ChannelRfFrequency    (channel_pair, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_pair, ChannelPeriod=0x1f86),
    msg60_ChannelTransmitPower  (channel_pair, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_pair)
  ]
  return SendToDongle(messages, devAntDongle, '', True, False)

def Trainer_ChannelConfig(devAntDongle):
  if debug.on(debug.Data1): logfile.Write ("Trainer_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_FE, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
    msg51_ChannelID             (channel_FE, DeviceNumber_FE, DeviceTypeID_FE, TransmissionType_IC_GDP),
    msg45_ChannelRfFrequency    (channel_FE, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_FE, ChannelPeriod=0x2000),                                     # 4 Hz
    msg60_ChannelTransmitPower  (channel_FE, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_FE)
  ]
  SendToDongle(messages, devAntDongle, '')

def SlaveTrainer_ChannelConfig(devAntDongle, DeviceNumber):
  if debug.on(debug.Data1): logfile.Write ("SlaveTrainer_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_FE_s, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
    msg51_ChannelID             (channel_FE_s, DeviceNumber, DeviceTypeID_FE, TransmissionType_IC_GDP),
    msg45_ChannelRfFrequency    (channel_FE_s, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_FE_s, ChannelPeriod=0x2000),                                     # 4 Hz
    msg60_ChannelTransmitPower  (channel_FE_s, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_FE_s),
#   msg4D_RequestMessage        (channel_FE_s, msgID_ChannelID) # Note that answer may be in logfile only
  ]
  SendToDongle(messages, devAntDongle, '')

def HRM_ChannelConfig(devAntDongle):
  if debug.on(debug.Data1): logfile.Write ("HRM_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_HRM, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
    msg51_ChannelID             (channel_HRM, DeviceNumber_HRM, DeviceTypeID_HRM, TransmissionType_IC),
    msg45_ChannelRfFrequency    (channel_HRM, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_HRM, ChannelPeriod=0x1f86),
    msg60_ChannelTransmitPower  (channel_HRM, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_HRM)
  ]
  SendToDongle(messages, devAntDongle, '')

def SlaveHRM_ChannelConfig(devAntDongle, DeviceNumber):
  if debug.on(debug.Data1): logfile.Write ("SlaveHRM_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_HRM_s, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
    msg51_ChannelID             (channel_HRM_s, DeviceNumber, DeviceTypeID_HRM, TransmissionType_IC),
    msg45_ChannelRfFrequency    (channel_HRM_s, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_HRM_s, ChannelPeriod=0x1f86),
    msg60_ChannelTransmitPower  (channel_HRM_s, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_HRM_s),
#   msg4D_RequestMessage        (channel_HRM_s, msgID_ChannelID) # Note that answer may be in logfile only
  ]
  SendToDongle(messages, devAntDongle, '')

def SlaveSCS_ChannelConfig(devAntDongle, DeviceNumber):                     # Note: not tested!!!
  if debug.on(debug.Data1): logfile.Write ("SlaveSCS_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_SCS_s, ChannelType_BidirectionalReceive, NetworkNumber=0x00),
    msg51_ChannelID             (channel_SCS_s, DeviceNumber, DeviceTypeID_SCS, TransmissionType_IC),
    msg45_ChannelRfFrequency    (channel_SCS_s, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_SCS_s, ChannelPeriod=0x1f86),
    msg60_ChannelTransmitPower  (channel_SCS_s, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_SCS_s),
#   msg4D_RequestMessage        (channel_SCS_s, msgID_ChannelID) # Note that answer may be in logfile only
  ]
  SendToDongle(messages, devAntDongle, '')

def PowerDisplay_unused(devAntDongle):
  if debug.on(debug.Data1): logfile.Write ("powerdisplay()")
                                                    # calibrate as power display
  stringl=[
  "a4 03 42 00 00 00 e5",                     # 42 assign channel
  "a4 05 51 00 00 00 0b 00 fb",               # 51 set channel id, 0b device=power sensor
  "a4 02 45 00 39 da",                        # 45 channel freq
  "a4 03 43 00 f6 1f 0d",                     # 43 msg period
  "a4 02 71 00 00 d7",                        # 71 Set Proximity Search chann number 0 search threshold 0
  "a4 02 63 00 0a cf",                        # 63 low priority search channel number 0 timeout 0
  "a4 02 44 00 02 e0",                        # 44 Host Command/Response 
  "a4 01 4b 00 ee"                            # 4b ANT_OpenChannel message ID channel = 0 D00001229_Fitness_Modules_ANT+_Application_Note_Rev_3.0.pdf
  ]
  SendToDongle(stringl, devAntDongle, '')

def ResetDongle(devAntDongle):
  if debug.on(debug.Data1): logfile.Write ("ResetDongle()")
  messages=[
    msg4A_ResetSystem(),
  ]
  rtn = SendToDongle(messages, devAntDongle, '', False)
  time.sleep(0.500)                           # After Reset, 500ms before next action
  return rtn

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
    logfile.Write("Dongles in the system:")
    devices = usb.core.find(find_all=True)
    for device in devices:
#       print (device)
        s = "manufacturer=%7s, product=%15s, vendor=%6s, product=%6s(%s)" %\
                (device.manufacturer, device.product, \
                 hex(device.idVendor), hex(device.idProduct), device.idProduct) 
        logfile.Write (s.replace('\0',''))

        i = 0
        for cfg in device:          # Do not understand this construction; see pyusb tutorial
            i += 1
            for intf in cfg:
                for ep in intf:
                    pass
    logfile.Write("--------------------")
  
#-------------------------------------------------------------------------------
# G e t D o n g l e
#-------------------------------------------------------------------------------
# input     none
#
# function  find antDongle (defined types only)
#
# returns   return devAntDongle and readable message
#-------------------------------------------------------------------------------
def GetDongle(p=None):
    msg     = ""
    if p==None:
        dongles = { (4104, "Suunto"), (4105, "Garmin"), (4100, "Older") }
    else:
        dongles = { (p, "(provided)")                                     }

    #---------------------------------------------------------------------------
    # https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
    #---------------------------------------------------------------------------
    found_available_ant_stick = False
    #---------------------------------------------------------------------------
    # Check the known (and supported) dongle types
    # Removed: if platform.system() in [ 'Windows', 'Darwin', 'Linux' ]:
    #---------------------------------------------------------------------------
    for dongle in dongles:
        ant_pid = dongle[0]
        if debug.on(debug.Function): logfile.Write ("GetDongle - Check for dongle %s %s" % (ant_pid, dongle[1]))
        try:
            #-------------------------------------------------------------------
            # Find the ANT-dongles of this type
            # Note: filter on idVendor=0x0fcf is removed
            #-------------------------------------------------------------------
            msg = "No (free) ANT-dongle found"         # was: "Could not find ANT-dongle"
            devAntDongles = usb.core.find(find_all=True, idProduct=ant_pid)
        except Exception as e:
            logfile.Write ("GetDongle - Exception: %s" % e)
            if "AttributeError" in str(e):
                msg = "GetDongle - Could not find dongle: " + str(e)
            elif "No backend" in str(e):
                msg = "GetDongle - No backend, check libusb: " + str(e)
            else:
                msg = "GetDongle: " + str(e)
        else:
            #-------------------------------------------------------------------
            # Try all dongles of this type
            #-------------------------------------------------------------------
            for devAntDongle in devAntDongles:
                if debug.on(debug.Function): 
                    s = "GetDongle - Try dongle: manufacturer=%7s, product=%15s, vendor=%6s, product=%6s(%s)" %\
                        (devAntDongle.manufacturer, devAntDongle.product, \
                        hex(devAntDongle.idVendor), hex(devAntDongle.idProduct), devAntDongle.idProduct) 
                    logfile.Write (s.replace('\0',''))
                if debug.on(debug.Data1 | debug.Function):
                    logfile.Print (devAntDongle)
                    # prints "DEVICE ID 0fcf:1009 on Bus 000 Address 001 ================="
                    # But .Bus and .Address not found for logging
                #---------------------------------------------------------------
                # Initialize the dongle
                #---------------------------------------------------------------
                try:                                            # check if in use
                    if debug.on(debug.Function): logfile.Write ("GetDongle - Set configuration")
                    devAntDongle.set_configuration()


                    reset_string=msg4A_ResetSystem()            # reset string probe
                                                                # same as ResetDongle()
                                                                # done here to have explicit error-handling.
                    if debug.on(debug.Function): logfile.Write ("GetDongle - Send reset string to dongle")
                    devAntDongle.write(0x01, reset_string)
                    time.sleep(0.500)                           # after reset, 500ms before next action


                    if debug.on(debug.Function): logfile.Write ("GetDongle - Read answer")
                    reply = ReadFromDongle(devAntDongle, False)


                    if debug.on(debug.Function): logfile.Write ("GetDongle - Check for an ANT+ reply")
                    msg = "No expected reply from dongle"
                    for s in reply:
                        synch, length, id, info, checksum, rest, c, d = DecomposeMessage(s)
                        if synch==0xa4 and length==0x01 and id==0x6f:
                            found_available_ant_stick = True
                            msg = "Using %s dongle" %  devAntDongle.manufacturer # dongle[1]
                            msg = msg.replace('\0','')          # .manufacturer is NULL-terminated

                except usb.core.USBError as e:                  # cannot write to ANT dongle
                    if debug.on(debug.Data1 | debug.Function):
                        logfile.Write ("GetDongle - Exception: %s" % e)
                    msg = "GetDongle - ANT dongle in use"

                except Exception as e:
                    logfile.Write ("GetDongle - Exception: %s" % e)
                    msg = "GetDongle: " + str(e)

                #---------------------------------------------------------------
                # If found, don't try the next ANT-dongle of this type
                #---------------------------------------------------------------
                if found_available_ant_stick: break

        #-----------------------------------------------------------------------
        # If found, don't try the next type
        #-----------------------------------------------------------------------
        if found_available_ant_stick: break
  
    #---------------------------------------------------------------------------
    # Done
    #---------------------------------------------------------------------------
    if found_available_ant_stick == False:
        devAntDongle = False 
    if debug.on(debug.Function): logfile.Write ("GetDongle() returns: " + msg)
    return devAntDongle, msg


#-------------------------------------------------------------------------------
# S e n d T o D o n g l e
#-------------------------------------------------------------------------------
# input     devAntDongle
#			strings             an array of data-buffers
#			comment				deprecated
#
#           receive             after sending the data, receive all responses
#           drop                the caller does not process the returned data
#
# function  send all strings to antDongle
#           read responses from antDongle
#
# returns   rtn                 the string-array as received from antDongle
#-------------------------------------------------------------------------------
def SendToDongle(messages, devAntDongle, comment='', receive=True, drop=True):
    rtn = []
    for message in messages:
        #-----------------------------------------------------------------------
        # Send the message
        #-----------------------------------------------------------------------
        try:
            devAntDongle.write(0x01,message)    # input:   endpoint address, buffer, timeout
                                                # returns: 
        except Exception as e:
            logfile.Write ("SendToDongle write error: " + str(e))

        DongleDebugMessage("Dongle    send   :", message)

        #-----------------------------------------------------------------------
        # Read all responses
        #-----------------------------------------------------------------------
        if receive:
            data = ReadFromDongle(devAntDongle, drop)
            for d in data: rtn.append(d)

    if debug.on(debug.Function): logfile.Write ("SendToDongle() returns: " +  logfile.HexSpaceL(rtn))
    return rtn

#-------------------------------------------------------------------------------
# R e a d F r o m D o n g l e
#-------------------------------------------------------------------------------
# input     devAntDongle
#           drop                the caller does not process the returned data
#                               this flag impacts the logfile only!
#
# function  read response from antDongle
#
# returns   return array of data-buffers
#-------------------------------------------------------------------------------
def ReadFromDongle(devAntDongle, drop):
    #---------------------------------------------------------------------------
    # Read from antDongle untill no more data (timeout), or error
    # Usually, dongle gives one buffer at the time, starting with 0xa4
    # Sometimes, multiple messages are received together on one .read
    #
    # https://www.thisisant.com/forum/view/viewthread/812
    #---------------------------------------------------------------------------
    data = []
    try:
        while True:                                 # ends on exception
            trv = devAntDongle.read(0x81,1000,20)   # input:   endpoint address, length, timeout
                                                    # returns: an array of bytes

            if len(trv) > 900: logfile.Write ("ReadFromDongle() too much data from .read()" )
            start  = 0
            while start < len(trv):
                error = False
                #---------------------------------------------------------------
                # Each message starts with a4; skip characters if not
                #---------------------------------------------------------------
                skip = start
                while trv[skip] != 0xa4 and skip < len(trv):
                    skip += 1
                if skip != start:
                    logfile.Write ("ReadFromDongle %s characters skipped " % (skip - start))
                    start = skip
                #---------------------------------------------------------------
                # Second character in the buffer (element in trv) is length of 
                # the info; add four for synch, len, id and checksum
                #---------------------------------------------------------------
                length = trv[start+1] + 4
                if start + length <= len(trv):
                    #---------------------------------------------------------------
                    # Check length and checksum
                    # Append to return array when correct
                    #---------------------------------------------------------------
                    d = bytes(trv[start : start+length])
                    checksum = d[-1:]
                    expected = CalcChecksum(d)

                    if expected != checksum:
                        error = "error: checksum incorrect"
                        logfile.Write ("%s checksum=%s expected=%s data=%s" % \
                            ( error, logfile.HexSpace(checksum), logfile.HexSpace(expected), logfile.HexSpace(d) ) )
                    else:
                        data.append(d)                         # add data to array
                        if drop == True:
                            DongleDebugMessage ("Dongle    drop   :", d)
                        else:
                            DongleDebugMessage ("Dongle    receive:", d)
                else:
                    error = "error: message exceeds buffer length"
                if error:
                    logfile.Write ("ReadFromDongle %s" % (error))
                #---------------------------------------------------------------
                # Next buffer in trv
                #---------------------------------------------------------------
                start += length
    # --------------------------------------------------------------------------
    # https://docs.python.org/3/library/exceptions.html
    # https://docs.python.org/3/library/exceptions.html
    # --------------------------------------------------------------------------
    # TimeoutError not raised on all systems, inspect text-message as well.
    # "timeout error" on most systems, "timed out" on Macintosh.
    # --------------------------------------------------------------------------
    except TimeoutError:
        pass
    except Exception as e:
        if "timeout error" in str(e) or "timed out" in str(e):
            pass
        else:
            logfile.Write ("ReadFromDongle read error: " + str(e))
       
    if debug.on(debug.Function): logfile.Write ("ReadFromDongle() returns: " + logfile.HexSpaceL(data))
    return data

# ------------------------------------------------------------------------------
# C o m p o s e   A N T   M e s s a g e
# ------------------------------------------------------------------------------
def ComposeMessage(id, info):
    fSynch      = sc.unsigned_char
    fLength     = sc.unsigned_char
    fId         = sc.unsigned_char
    fInfo       = str(len(info)) + sc.char_array  # 9 character string

    format  =    sc.no_alignment + fSynch + fLength + fId + fInfo
    data    = struct.pack (format, 0xa4,    len(info), id,  info)
    #---------------------------------------------------------------------------
    # Add the checksum
    # (antifier added \00\00 after each message for unknown reason)
    #---------------------------------------------------------------------------
    data += calc_checksum(data)    
    
    return data
    
def DecomposeMessage(d):
    synch    = d[0]
    length   = d[1]
    id       = d[2]
    if length > 0:
        info = d[3:3+length]            # Info, if length > 0
    else:
        info = binascii.unhexlify('')   # NULL-string bytes
    checksum = d[3+length]              # Character after info

    if len(d) > 4 + length:
        rest = d[4 + length:]           # Remainder (should not occur)
    else:
        rest = ""                       # No remainder (normal)

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
        SequenceNumber = (Channel & 0b11100000) >> 5 # Upper 3 bits
        Channel        =  Channel & 0b00011111       # Lower 5 bits

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
        synch, length, id, info, checksum, rest, Channel, p = DecomposeMessage(d)
        
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
        elif id == msgID_AssignChannel          : id_ = 'Assign Channel'
        elif id == msgID_ChannelPeriod          : id_ = 'Channel Period'
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

        #-----------------------------------------------------------------------
        # extra is additional info for the message
        # p_ is readable pagenumber if there is a valid pagenumber
        #-----------------------------------------------------------------------
        extra = ''                                              # Initially empty
        p_    = ''                                              # There is not always page-info, do not show

        if   id == msgID_ChannelResponse or id == msgID_RequestMessage:
                           Channel = -1                         # There is no channel number for this message
                           extra   = " msg=" + hex(p)           # No page but acknowledged/requested message

        elif id == msgID_ANTversion:
                           Channel = -1                         # There is no channel number for this message
                           extra = info.decode("utf-8").replace('\0', '') # ANTversion in string format
                           info_ = ''

        elif id == msgID_ChannelID:
                           extra = " (ch=%s, nr=%s, ID=%s, tt=%s)" % (unmsg51_ChannelID(info))
                           
        elif id == msgID_BroadcastData or id == msgID_AcknowledgedData:
                                                      # Pagenumber in Payload
            if   p        <   0: pass
            elif p & 0x7f ==  0: p_ = 'Default data page'             # D00000693_-_ANT+_Device_Profile_-_Heart_Rate_Rev_2.1
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
            elif p        == 16: p_ = 'General FE data'
            elif p        == 25: p_ = 'Trainer Data'
            elif p        == 48: p_ = 'Basic Resistance'
            elif p        == 49: p_ = 'Target Power'
            elif p        == 51: p_ = 'Track Resistance'
            elif p        == 55: p_ = 'User Configuration'
            elif p        == 70: p_ = 'Request Datapage'
            elif p        == 76: p_ = 'Mode settings page'
            elif p        == 80: p_ = 'Manufacturer Info'
            elif p        == 81: p_ = 'Product Information'
            elif p        == 82: p_ = 'Battery Status'
#           elif p        == 89: p_ = 'Add channel ID to list ???'
            else               : p_ = '??'

            p_ = " p=%s(%s)" % (p, p_)                          # Page, show number and name

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
            else              :  extra = " [ch=%s%s]" % (Channel, p_)   # Channel, show it with optional pageinfo

        #-----------------------------------------------------------------------
        # Write to logfile
        #-----------------------------------------------------------------------
        if debug.on(debug.Data1):
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

    return                         tuple[0],          tuple[1],           tuple[2],          tuple[2]

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
    Capabilities        = 0x30 | 0x03 | 0x00 | 0x00 # IN_USE | HRM | Distance | Speed

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
    EventCounter        = int(min(  0xff, EventCounter      ))
    Cadence             = int(min(  0xff, Cadence           ))
    AccumulatedPower    = int(min(0xffff, AccumulatedPower  ))
    CurrentPower        = int(min(0x0fff, CurrentPower      ))
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
    nChannel            = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    
    nDataPageNumber     = 1
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
    nChannel            = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    
    nDataPageNumber     = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    
    fReserved           = sc.pad * 5
    
    nTargetPower        = 2
    fTargetPower        = sc.unsigned_short # units of 0.25Watt

    format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fTargetPower
    tuple  = struct.unpack (format, info)
    
    rtn = tuple[nTargetPower] / 4      # returns units of 1Watt

    return rtn

# ------------------------------------------------------------------------------
# P a g e 5 1   T r a c k R e s i s t a n c e
# ------------------------------------------------------------------------------
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# Data page 51 (0x33) Target `Resistance
# ------------------------------------------------------------------------------
def msgUnpage51_TrackResistance(info):
    nChannel            = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    
    nDataPageNumber     = 1
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    
    fReserved           = sc.pad * 4
    
    nGrade              = 2
    fGrade              = sc.unsigned_short
    
    nRollingResistance  = 3
    fRollingResistance  = sc.unsigned_char
    
    format = sc.no_alignment + fChannel + fDataPageNumber + fReserved + fGrade + fRollingResistance
    tuple  = struct.unpack (format, info)
    
    Grade = tuple[nGrade]
    rtn   = Grade * 0.01 - 200          # -200% - 200%, units 0.01%
    
#   rtn  *= 2.5                         # Empirically...
                                        # This was entered when creating the file
                                        # but never tested / properly verified
                                        # 2020-03-31 Incorrect as comparing with Rouvy
    rtn   = round(rtn,2)

    return rtn

# ------------------------------------------------------------------------------
# P a g e 5 5   U s e r   C o n f i g u r a t i o n
# ------------------------------------------------------------------------------
# D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
# Data page 55 (0x37) User Configuration
# ------------------------------------------------------------------------------
def msgUnpage55_UserConfiguration(info):
    nChannel            = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    
    nDataPageNumber     = 1
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
    BicyleWheelDiameterOffset = (BicycleInfo & 0x000f)                   # 0 - 10 mm
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
    nChannel            = 0
    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    
    nDataPageNumber     = 1
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

#-------------------------------------------------------------------------------
# Main program to compare strings with messages
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    if False:
        print ("calibrate---------------------------------------------------------------")
        stringl=[
        "a4 02 4d 00 54 bf",                        # request max channels
        "a4 01 4a 00 ef",                           # reset system
        "a4 02 4d 00 3e d5",                        # request ant version
        "a4 09 46 00 b9 a5 21 fb bd 72 c3 45 64",   # set network key b9 a5 21 fb bd 72 c3 45
        ]
        messages=[
        msg4D_RequestMessage(channel_FE, msgID_Capabilities),   # request max channels
        msg4A_ResetSystem(),
        msg4D_RequestMessage(channel_FE, msgID_ANTversion),
        msg46_SetNetworkKey()
        ]

        for i in range(0,len(messages)):
            print(i, stringl[i])
            print(i, logfile.HexSpace(messages[i]))
            if messages[i] == binascii.unhexlify(stringl[i].replace(' ','')): print("equal")
            else:                                                             print("unequal ***********")
            

        print("Trainer_ChannelConfig---------------------------------------------------")
        stringl=[
        "a4 03 42 00 10 00 f5",                     # [42] assign channel, [00] 0, [10] type 10 bidirectional transmit, [00] network number 0, [f5] extended assignment
        "a4 05 51 00 cf 00 11 05 2b",               # [51] set channel ID, [00] number 0 (wildcard search) , [cf] device number 207, [00] pairing request (off), [11] device type fec, [05] transmission type  (page 18 and 66 Protocols) 00000101 - 01= independent channel, 1=global data pages used
        "a4 02 45 00 39 da",                        # [45] set channel freq, [00] transmit channel on network #0, [39] freq 2400 + 57 x 1 Mhz= 2457 Mhz
        "a4 03 43 00 00 20 c4",                     # [43] set messaging period, [00] channel #0, [f61f] = 32768/8182(f61f) = 4Hz (The channel messaging period in seconds * 32768. Maximum messaging period is ~2 seconds. )
        "a4 02 60 00 03 c5",                        # [60] set transmit power, [00] channel #0, [03] 0 dBm
        "a4 01 4b 00 ee"                            #      open channel #0
        ]
        messages=[
        msg42_AssignChannel         (channel_FE, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
        msg51_ChannelID             (channel_FE, 0x00cf, DeviceTypeID_FE, TransmissionType_IC_GDP),             # [cf] device number 207
        msg45_ChannelRfFrequency    (channel_FE, RfFrequency_2457Mhz), 
        msg43_ChannelPeriod         (channel_FE, ChannelPeriod=0x2000),
        msg60_ChannelTransmitPower  (channel_FE, TransmitPower_0dBm),
        msg4B_OpenChannel           (channel_FE)
        ]
        for i in range(0,len(messages)):
            print(i, stringl[i])
            print(i, logfile.HexSpace(messages[i]))
            if messages[i] == binascii.unhexlify(stringl[i].replace(' ','')): print("equal")
            else:                                                             print("unequal ***********")


        print("HRM_ChannelConfig-------------------------------------------------------")
        stringl=[
        "a4 03 42 01 10 00 f4",                   # [42] assign channel, [01] channel #1, [10] type 10 bidirectional transmit, [00] network number 0, [f4] normal assignment
        "a4 05 51 01 65 00 78 01 ed",             # [51] set channel ID, [01] channel 1 , [02] device number 2, [00] pairing request (off), [78] device type HR sensor, [01] transmission type  (page 18 and 66 Protocols) 00000101 - 01= independent channel, 1=global data pages used
        "a4 02 45 01 39 db",                      # [45] set channel freq, [01] set channel #1, [39] freq 2400 + 57 x 1 Mhz= 2457 Mhz
        "a4 03 43 01 86 1f 7c",                   # [43] set messaging period, [01] channel #1, [861f] = 32768/8070(861f) = 4Hz (The channel messaging period in seconds * 32768. Maximum messaging period is ~2 seconds. )
        "a4 02 60 01 03 c4",                      # [60] set transmit power, [01] channel #1, [03] 0 dBm
        "a4 01 4b 01 ef"                          #      open channel #1
        ]
        messages=[
        msg42_AssignChannel         (channel_HRM, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
        msg51_ChannelID             (channel_HRM, 0x0065, DeviceTypeID_HRM, TransmissionType_IC),           # [65] device number 101
        msg45_ChannelRfFrequency    (channel_HRM, RfFrequency_2457Mhz), 
        msg43_ChannelPeriod         (channel_HRM, ChannelPeriod=0x1f86),
        msg60_ChannelTransmitPower  (channel_HRM, TransmitPower_0dBm),
        msg4B_OpenChannel           (channel_HRM)
        ]

        for i in range(0,len(messages)):
            print(i, stringl[i])
            print(i, logfile.HexSpace(messages[i]))
            if messages[i] == binascii.unhexlify(stringl[i].replace(' ','')): print("equal")
            else:                                                             print("unequal ***********")
            

        print("ResetDongle-------------------------------------------------------------")
        stringl =[
        "a4 01 4a 00 ef"
        ]
        messages=[
        msg4A_ResetSystem(),
        ]
        for i in range(0,len(messages)):
            print(i, stringl[i])
            print(i, logfile.HexSpace(messages[i]))
            if messages[i] == binascii.unhexlify(stringl[i].replace(' ','')): print("equal")
            else:                                                             print("unequal ***********")
    else:
        debug.activate()
        EnumerateAll()
        
        print('----- # I have this one (sending ANT data)')
        d, msg = GetDongle(4104)        
        print(msg)
        
        print('----- # I have this one, used for Trainer Road and Zwift')
        d, msg = GetDongle(4105)        
        print(msg)
        
        print('----- # This is the USB-interface to the trainer')
        d, msg = GetDongle(0x1932)        
        print(msg)
        
else:
    pass                                # We're included so do not take action!
