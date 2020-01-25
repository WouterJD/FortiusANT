#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-01-25"
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
#-------------------------------------------------------------------------------
channel_FE  = 0             # ANT+ channel for Fitness Equipment
channel_HRM = 1             # ANT+ channel for Heart Rate Monitor

#-------------------------------------------------------------------------------
# D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf
# 9.3 ANT Message summary
#-------------------------------------------------------------------------------
ChannelType_BidirectionalTransmit=0x10

msgID_ANTversion        = 0x3e
msgID_BroadcastData     = 0x4e
msgID_AcknowledgedData  = 0x4f
msgID_ChannelResponse   = 0x40
msgID_Capabilities      = 0x54

# profile.xlsx: antplus_device_type
DeviceTypeID_FE         = 0x11
DeviceTypeID_HRM        = 0x78

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
  if debug.on(debug.Function): logfile.Write ("Calibrate()")
  messages=[
    msg4D_RequestMessage        (channel_FE, msgID_Capabilities),   # request max channels
    msg4A_ResetSystem           (),
    msg4D_RequestMessage        (channel_FE, msgID_ANTversion),     # request ant version
    msg46_SetNetworkKey         ()
  ]
  SendToDongle(messages,devAntDongle, "(Calibrate)")
  
def Trainer_ChannelConfig(devAntDongle):
  if debug.on(debug.Function): logfile.Write ("Trainer_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_FE, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
    msg51_ChannelID             (channel_FE, 0x00cf, DeviceTypeID_FE, TransmissionType_IC_GDP),         # [cf] device number 207
    msg45_ChannelRfFrequency    (channel_FE, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_FE, ChannelPeriod=0x2000),                                     # 4 Hz
    msg60_ChannelTransmitPower  (channel_FE, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_FE)
  ]
  SendToDongle(messages, devAntDongle, "(Trainer channel config)")

def HRM_ChannelConfig(devAntDongle):
  if debug.on(debug.Function): logfile.Write ("HRM_ChannelConfig()")
  messages=[
    msg42_AssignChannel         (channel_HRM, ChannelType_BidirectionalTransmit, NetworkNumber=0x00),
    msg51_ChannelID             (channel_HRM, 0x0065, DeviceTypeID_HRM, TransmissionType_IC),           # [65] device number 101
    msg45_ChannelRfFrequency    (channel_HRM, RfFrequency_2457Mhz), 
    msg43_ChannelPeriod         (channel_HRM, ChannelPeriod=0x1f86),
    msg60_ChannelTransmitPower  (channel_HRM, TransmitPower_0dBm),
    msg4B_OpenChannel           (channel_HRM)
  ]
  SendToDongle(messages, devAntDongle, "(HRM channel config)")

def PowerDisplay_unused(devAntDongle):
  if debug.on(debug.Function): logfile.Write ("powerdisplay()")
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
  SendToDongle(stringl, devAntDongle, "(Power display)")

def ResetDongle(devAntDongle):
  if debug.on(debug.Function): logfile.Write ("ResetDongle()")
  messages=[
    msg4A_ResetSystem(),
  ]
  return SendToDongle(messages, devAntDongle, "(Reset dongle)")
  
#-------------------------------------------------------------------------------
# G e t D o n g l e
#-------------------------------------------------------------------------------
# input     none
#
# function  find antDongle (defined types only)
#
# returns   return devAntDongle and readable message
#-------------------------------------------------------------------------------
def GetDongle():
    if debug.on(debug.Function): logfile.Write ("GetDongle()")

    msg     = ""
    dongles = { (4104, "Suunto"), (4105, "Garmin"), (4100, "Older") }

    #---------------------------------------------------------------------------
    # Windows, Darwin
    #---------------------------------------------------------------------------
    # https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
    #---------------------------------------------------------------------------
    if platform.system() in [ 'Windows', 'Darwin', 'Linux' ]:
        found_available_ant_stick= False
        for dongle in dongles:                                          # iterate through ant pids
            ant_pid = dongle[0]
            if not found_available_ant_stick:                           # if haven't found a working ANT dongle yet
                if debug.on(debug.Function): logfile.Write ("GetDongle - Check for dongle %s %s" % (ant_pid, dongle[1]))
                try:
                    devAntDongle = usb.core.find(idVendor=0x0fcf, idProduct=ant_pid) #get ANT+ stick 
                    if devAntDongle:                                    # No Exception when no ANT+ stick
                        if debug.on(debug.Function): logfile.Write ("GetDongle - Dongle found")

                        devAntDongle.set_configuration()                # set active configuration

                        try:                                            # check if in use
                            reset_string=msg4A_ResetSystem()            # reset string probe
                                                                        # same as ResetDongle()
                                                                        # done here to have explicit error-handling.
                            if debug.on(debug.Function): logfile.Write ("GetDongle - Send reset string to dongle")
                            devAntDongle.write(0x01, reset_string)

                            if debug.on(debug.Function): logfile.Write ("GetDongle - Read answer")
                            reply = ReadFromDongle(devAntDongle, False)

                            if debug.on(debug.Function): logfile.Write ("GetDongle - Check for an ANT+ reply")

                            msg = "No expected reply from dongle"
                            for s in reply:
                                synch, length, id, info, checksum, rest = DongleData2Fields(s)
                                if synch==0xa4 and length==0x01 and id==0x6f:
                                    found_available_ant_stick = True
                                    msg = "Using %s dongle" % dongle[1]

                        except usb.core.USBError:                         # cannot write to ANT dongle
                            if debug.on(debug.Function): logfile.Write ("GetDongle - ANT dongle in use")
                            found_available_ant_stick = False
                    else:
                        msg = "Could not find ANT-dongle"
                except Exception as e:
                    if debug.on(debug.Function): logfile.Write ("GetDongle - " + str(e))

                    if "AttributeError" in str(e):
                        msg = "GetDongle - Could not find dongle: " + str(e)
                    elif "No backend" in str(e):
                        msg = "GetDongle - No backend, check libusb: " + str(e)
                    else:
                        msg = "GetDongle: " + str(e)
                    found_available_ant_stick = False

        if found_available_ant_stick == False:
            devAntDongle = False 
    #---------------------------------------------------------------------------
    # Linux, Posix     --    Find ANT+ USB stick on serial (Linux)
    #---------------------------------------------------------------------------
    elif False:
        print ('***** not tested; what platform needs this? *****')
        found_available_ant_stick = False
        for p in glob.glob('/dev/ttyUSB*'):
            devAntDongle = serial.Serial(p, 19200, rtscts=True, dsrdtr=True)

            # I would expect that devAntDongle is checked for success....

            reply = ResetDongle(devAntDongle)
            msg = "No expected reply from dongle"
            for s in reply:
                synch, length, id, info, checksum, rest = DongleData2Fields(s)
                if synch==0xa4 and length==0x01 and id==0x6f:
                    serial_port = p
                    found_available_ant_stick = True
                    msg = "Found ANT Stick"

            if not found_available_ant_stick:
                 devAntDongle.close()   #not correct reply to reset

            if found_available_ant_stick == True  : break

        if found_available_ant_stick == False:
            print ('Could not find ANT+ device. Check output of "lsusb | grep 0fcf" and "ls /dev/ttyUSB*"')
            #sys.exit()
            devAntDongle = False
        
    #---------------------------------------------------------------------------
    # Other OS
    #---------------------------------------------------------------------------
    else:
        msg = "OS not Supported"
        devAntDongle = False
  
    #---------------------------------------------------------------------------
    # Done
    #---------------------------------------------------------------------------
    if debug.on(debug.Function): logfile.Write ("GetDongle() returns: " + msg)
    return devAntDongle, msg


#-------------------------------------------------------------------------------
# S e n d T o D o n g l e
#-------------------------------------------------------------------------------
# input     devAntDongle
#			strings             an array of data-buffers
#			comment				for the logfile
#
#           receive             after sending the data, receive all responses
#           drop                the caller does not process the returned data
#
# function  send all strings to antDongle
#           read responses from antDongle
#
# returns   rtn                 the string-array as received from antDongle
#-------------------------------------------------------------------------------
def SendToDongle(messages, devAntDongle, comment, receive=True, drop=True):
    if debug.on(debug.Function): logfile.Write ("SendToDongle(" +  logfile.HexSpaceL(messages) + "," + comment + ")")
    rtn = []
    for message in messages:
        #-----------------------------------------------------------------------
        # Send the message
        #-----------------------------------------------------------------------
        if False:
            print ('***** not tested; what platform needs this? *****')
            devAntDongle.write(message)             # Note: devAntDongle is a serial here!
        else:
            try:
                devAntDongle.write(0x01,message)    # input:   endpoint address, buffer, timeout
                                                    # returns: 
            except Exception as e:
                logfile.Write ("SendToDongle write error: " + str(e))

        DongleDebugMessage("Dongle    send   :", message, comment)

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
    if debug.on(debug.Function): logfile.Write ("ReadFromDongle()")
    #---------------------------------------------------------------------------
    # Read from antDongle untill no more data (timeout), or error
    # Usually, dongle gives one buffer at the time, starting with 0xa4
    # Sometimes, multiple messages are received together on one .read
    #
    # https://www.thisisant.com/forum/view/viewthread/812
    #---------------------------------------------------------------------------
    data = []
    try:
        while True:                                     # ends on exception
            if False:
                print ('***** not tested; what platform needs this? *****')
                devAntDongle.timeout = 0.1
                try:
                    trv = devAntDongle.read(size=256)   # Note: devAntDongle is a serial here!
                except Exception as e:
                    trv = ""
                    logfile.Write ( str(e) )
            else:
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
                            DongleDebugMessage ("Dongle    drop   :", d, "")
                        else:
                            DongleDebugMessage ("Dongle    receive:", d, "")
                else:
                    error = "error: message exceeds buffer length"
                if error:
                    logfile.Write ("ReadFromDongle %s" % (error))
                #---------------------------------------------------------------
                # Next buffer in trv
                #---------------------------------------------------------------
                start += length
    except Exception as e:
        if "timeout error" in str(e):
            if debug.on(debug.Data1):
                logfile.Write ("Dongle    timeout")
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
        rest=d[4 + length:]             # Remainder
    else:
        rest= ""                        # No remainder
        
    if length >= 1: Channel         = d[3]
    if length >= 2: DataPageNumber  = d[4]

#   print(synch, length, "id=", id, info, checksum, "r=", rest, "ch=", Channel, "dp=", DataPageNumber)
    
    return synch, length, id, info, checksum, rest, Channel, DataPageNumber

#-------------------------------------------------------------------------------
# D e b u g M e s s a g e
#-------------------------------------------------------------------------------
# input     msg, d, comment
#
# function  Write structured dongle message to logfile if so requested
#
# returns   none
#-------------------------------------------------------------------------------
def DongleDebugMessage(text, d, comment):
    if debug.on(debug.Data1): 
        synch, length, id, info, checksum, rest = DongleData2Fields(d)
        logfile.Write ("%s synch=%s, len=%2s, id=%s, check=%s, info=%s +%s %s" % \
                    (text,   synch,  length,  id, checksum,  logfile.HexSpace(info),  rest,    comment))
                  
def DongleData2Fields(d):
    # d is a ANT message
    # e.g. 0xa40340000103e5
    #        s l i .1.2.3    synch=a4, len=03, id=40, info=000103, checksum=e5
    # ==> length of d = length + 4

    synch    = d[0]             # byte 0
    length   = d[1]             # byte 1; length of info
    id       = d[2]             # byte 2; id
    info     = d[3:3 + length]  # bytes 3...>>
    checksum = d[3 + length]    # byte after info

    if len(d) > 3 + length + 1: rest=d[3+length+1:len(d)]           # Remainder
    else:     rest= ""          # No remainder (as expected)
    
    return synch, length, id, info, checksum, rest

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   42   A s s i g n C h a n n e l
# ------------------------------------------------------------------------------
def msg42_AssignChannel(ChannelNumber, ChannelType, NetworkNumber):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     ChannelType,       NetworkNumber)
    msg     = ComposeMessage (0x42, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg42_AssignChannel(channel=%s, ChannelType=%s, NetworkNumber=%s)" % (ChannelNumber, ChannelType, NetworkNumber))

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   43   C h a n n e l P e r i o d
# ------------------------------------------------------------------------------
def msg43_ChannelPeriod(ChannelNumber, ChannelPeriod):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_short
    info    = struct.pack(format,  ChannelNumber,     ChannelPeriod)
    msg     = ComposeMessage (0x43, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg43_ChannelPeriod(channel=%s, ChannelPeriod=%s)" % (ChannelNumber, ChannelPeriod))

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   45   C h a n n e l R f F r e q u e n c y 
# ------------------------------------------------------------------------------
def msg45_ChannelRfFrequency(ChannelNumber, RfFrequency):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     RfFrequency)
    msg     = ComposeMessage (0x45, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg45_ChannelRfFrequency(channel=%s, RfFrequency=%s)" % (ChannelNumber, RfFrequency))

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   46   S e t N e t w o r k K e y
# ------------------------------------------------------------------------------
def msg46_SetNetworkKey(NetworkNumber = 0x00, NetworkKey=0x45c372bdfb21a5b9):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_long_long
    info    = struct.pack(format,  NetworkNumber,     NetworkKey)
    msg     = ComposeMessage (0x46, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg46_SetNetworkKey(NetworkNumber=%s, NetworkKey=%s)" % (NetworkNumber, hex(NetworkKey)))

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   4A   R e s e t   S y s t e m
# ------------------------------------------------------------------------------
def msg4A_ResetSystem():
    format  =    sc.no_alignment + sc.unsigned_char
    info    = struct.pack(format,  0x00)
    msg     = ComposeMessage (0x4a, info)

    if debug.on(debug.Data1): logfile.Write ("msg4A_ResetSystem()")

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   4B   O p e n C h a n n e l
# ------------------------------------------------------------------------------
def msg4B_OpenChannel(ChannelNumber):
    format  =    sc.no_alignment + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber)
    msg     = ComposeMessage (0x4b, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg4B_OpenChannel(channel=%s)" % (ChannelNumber))

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   4D   R e q u e s t   M e s s a g e
# ------------------------------------------------------------------------------
def msg4D_RequestMessage(ChannelNumber, RequestedMessageID):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     RequestedMessageID)
    msg     = ComposeMessage (0x4d, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg4D_RequestMessage(channel=%s, RequestedMessageID=%s)" % \
            (ChannelNumber, hex(RequestedMessageID)))

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   51   C h a n n e l I D
# ------------------------------------------------------------------------------
def msg51_ChannelID(ChannelNumber, DeviceNumber, DeviceTypeID, TransmissionType):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_short + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     DeviceNumber,       DeviceTypeID,      TransmissionType)
    msg     = ComposeMessage (0x51, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg51_ChannelID(channel=%s,DeviceNumber=%s, DeviceTypeID=%s, TransmissionType=%s)" % \
            (ChannelNumber, DeviceNumber, DeviceTypeID, TransmissionType))

    return msg

# ------------------------------------------------------------------------------
# A N T   M e s s a g e   60   C h a n n e l T r a n s m i t P o w e r
# ------------------------------------------------------------------------------
def msg60_ChannelTransmitPower(ChannelNumber, TransmitPower):
    format  =    sc.no_alignment + sc.unsigned_char + sc.unsigned_char
    info    = struct.pack(format,  ChannelNumber,     TransmitPower)
    msg     = ComposeMessage (0x60, info)

    if debug.on(debug.Data1):
        logfile.Write ("msg60_ChannelTransmitPower(channel=%s, TransmitPower=%s)" % \
            (ChannelNumber, TransmitPower))

    return msg

# ==============================================================================
# ANT+ message interface
# ==============================================================================

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
    EquipmentType       = 0x19
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

    if debug.on(debug.Data1):
        logfile.Write ("msgPage16_GeneralFEdata(channel=%s, elapsed=%s, distance=%s, speed=%s, hr=%s) returns %s" % \
            (Channel, ElapsedTime, DistanceTravelled, Speed, HeartRate, logfile.HexSpace(info)))

    return info

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

    if debug.on(debug.Data1):
        logfile.Write ("msgPage25_TrainerData(channel=%s, event=%s, cadence=%s, accPower=%s, power=%s) returns %s" % \
            (Channel, EventCounter, Cadence, AccumulatedPower, CurrentPower, logfile.HexSpace(info)))

    return info

# ------------------------------------------------------------------------------
# P a g e 8 0 _ M a n u f a c t u r e r I n f o
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common Data Page 80: (0x50) Manufacturers Information          
# ------------------------------------------------------------------------------
def msgPage80_ManufacturerInfo(Channel):
    DataPageNumber      = 80

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char
    fReserved2          = sc.unsigned_char
    fHWrevision         = sc.unsigned_char
    fManufacturerID     = sc.unsigned_short
    fModelNumber        = sc.unsigned_short

    format=    sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fReserved2 + fHWrevision + fManufacturerID + fModelNumber
    info  = struct.pack (format,  Channel,   DataPageNumber,   0xff,        0xff,        0x01,         0x0059,          0x8385)
    
    if debug.on(debug.Data1):
        logfile.Write ("msgPage80_ManufacturerInfo(channel=%s) returns %s" % (Channel, logfile.HexSpace(info)))

    return info

# ------------------------------------------------------------------------------
# P a g e 8 1   P r o d u c t I n f o r m a t i o n
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common Data Page 81: (0x51) Product Information          
# ------------------------------------------------------------------------------
def msgPage81_ProductInformation(Channel):
    DataPageNumber      = 81

    fChannel            = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber     = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1          = sc.unsigned_char
    fSWrevisionSupp     = sc.unsigned_char
    fSWrevisionMain     = sc.unsigned_char
    fSerialNumber       = sc.unsigned_int

    format=    sc.no_alignment + fChannel + fDataPageNumber + fReserved1 + fSWrevisionSupp + fSWrevisionMain + fSerialNumber
    info  = struct.pack (format,  Channel,   DataPageNumber,   0xff,        0xff,             0x01,             0x19590705)
    
    if debug.on(debug.Data1):
        logfile.Write ("msgPage81_ProductInformation(channel=%s) returns %s" % (Channel, logfile.HexSpace(info)))

    return info

# ------------------------------------------------------------------------------
# P a g e 8 2   B a t t e r y S t a t u s 
# ------------------------------------------------------------------------------
# Refer:    https://www.thisisant.com/developer/resources/downloads#documents_tab
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common Data Page 82: (0x52) Battery Status
# ------------------------------------------------------------------------------
def msgPage82_BatteryStatus(Channel):
    DataPageNumber      = 80

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
    
    if debug.on(debug.Data1):
        logfile.Write ("msgPage82_BatteryStatus(channel=%s) returns %s" % (Channel, logfile.HexSpace(info)))

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

# ------------------------------------------------------------------------------
# U n p a g e 4 8   B a s i c R e s i s t a n c e
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
    
    if debug.on(debug.Data1):
        logfile.Write ("msgUnpage48_BasicResistance(%s) returns power=%s" % (logfile.HexSpace(info), rtn))
    
    return rtn

# ------------------------------------------------------------------------------
# U n p a g e 4 9   T a r g e t P o w e r
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

    if debug.on(debug.Data1):
        logfile.Write ("msgUnpage49_TargetPower(%s) returns power=%s" % (logfile.HexSpace(info), rtn))
    
    return rtn

# ------------------------------------------------------------------------------
# U n p a g e 5 1   T r a c k R e s i s t a n c e
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
    
    rtn  *= 2.5                         # Empirically...
    rtn   = round(rtn,2)

    if debug.on(debug.Data1):
        logfile.Write ("msgUnpage51_TrackResistance(%s) [Raw grade=%s] returns Grade(slope)=%s" % (logfile.HexSpace(info), Grade, rtn))
    
    return rtn

# ------------------------------------------------------------------------------
# U n p a g e 5 5   U s e r   C o n f i g u r a t i o n
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

    if debug.on(debug.Data1):
        logfile.Write ("msgUnpage55_UserConfiguration(%s) returns UserWeigth=%s BicycleWeigth=%s" % \
                        (logfile.HexSpace(info), UserWeigth, BicycleWeigth))

    return UserWeigth, BicycleWeigth, BicyleWheelDiameter, GearRatio

# ------------------------------------------------------------------------------
# U n p a g e 7 0 _ R e q u e s t D a t a P a g e
# ------------------------------------------------------------------------------
# D00001198_-_ANT+_Common_Data_Pages_Rev_3.1.pdf
# Common page 70 (0x46) Request Data Page
# ------------------------------------------------------------------------------
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

    if debug.on(debug.Data1):
        logfile.Write ("msgUnpage70_RequestDataPage(%s) returns %s %s %s ack=%s nr=%s page=%s type=%s" % \
           (logfile.HexSpace(info), \
           tuple[nSlaveSerialNumber], tuple[nDescriptorByte1], tuple[nDescriptorByte2], \
           AckRequired, NrTimes, tuple[nRequestedPageNumber], tuple[nCommandType]))

    return tuple[nSlaveSerialNumber], tuple[nDescriptorByte1], tuple[nDescriptorByte2], \
           AckRequired, NrTimes, tuple[nRequestedPageNumber], tuple[nCommandType]

#-------------------------------------------------------------------------------
# Main program to compare strings with messages
#-------------------------------------------------------------------------------
if __name__ == "__main__":
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
    pass                                # We're included so do not take action!
