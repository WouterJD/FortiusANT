#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2022-08-22"
# 2022-08-22    AntDongle stores received messages in a queue.
# 2020-05-07    clsAntDongle encapsulates all functions
#               and implements dongle recovery
# 2020-05-01    Added: Vortex Headunit
# 2020-04-22    Miscellaneous improvements for Tacx i-Vortex
#               Versions displayed on console
# 2020-04-20    Tacx i-Vortex speed in km/h, TargetPower *20
# 2020-04-19    Tacx i-Vortex data pages interpreted
#               If Tacx i-Vortex is detected, Power is set to 100+seconds.
# 2020-04-16    Write() replaced by Console() where needed
# 2020-02-18    SimulateTrainer added, so the behaviour of a training program
#                   can be checked.
# 2020-02-12    Different channels used for HRM and HRM_s
# 2020-02-11    Reset/Calibrate improved; UnassignChannel seems limitted effect
# 2020-01-29    First version
#-------------------------------------------------------------------------------
import argparse
import binascii
import math
import numpy
import os
import pickle
import platform, glob
import random
import sys
import struct
import threading
import time
import usb.core
import wx

from datetime import datetime

import antDongle         as ant
import antHRM            as hrm
import antFE             as fe
import debug
import ExplorAntCommand  as cmd
import logfile
import usbTrainer
class clsDeviceID(object):
    def __init__(self, Channel, DeviceType, DeviceNumber, DeviceTypeID, TransmissionType):
        self.Channel             = Channel
        self.DeviceType          = DeviceType
        self.DeviceNumber        = DeviceNumber
        self.DeviceTypeID        = DeviceTypeID
        self.TransmissionType    = TransmissionType


# ==============================================================================
# Main program; Command line parameters
# ==============================================================================

#-------------------------------------------------------------------------------
# And go!
# ------------------------------------------------------------------------------
# input:        command line
#
# Description:  Show all dongles available
#               Open defined dongle
#               Start listening what's going on in the air
#
# Output:       Console/logfile
#
# Returns:      None
# ------------------------------------------------------------------------------

debug.deactivate()
clv = cmd.CommandLineVariables()
debug.activate(clv.debug)

if True or debug.on(debug.Any):
    logfile.Open  ('ExplorANT')
    logfile.Console ("ExplorANT started")

    s = " %17s = %s"
    logfile.Console(s % ('ExplorANT',     __version__ ))
    logfile.Console(s % ('antDongle', ant.__version__ ))

    clv.print()
    logfile.Console ("--------------------")

# ------------------------------------------------------------------------------
# First enumerate all dongles
# ------------------------------------------------------------------------------
ant.EnumerateAll()

# ------------------------------------------------------------------------------
# Open dongle; either the defined one or default
#
# Note, it does not matter which dongle you open.
# The dongle itself means a connection to the ANT+ network
# Each application starting can use any ANT+ dongle
# ------------------------------------------------------------------------------
if clv.dongle > 0:
    p = clv.dongle      # Specified on command line
else:
    p = None            # Take the default

AntDongle = ant.clsAntDongle(p)
logfile.Console (AntDongle.Message)

if AntDongle.OK and not clv.SimulateTrainer:
    #---------------------------------------------------------------------------
    # We are going to look what MASTER devices there are
    #---------------------------------------------------------------------------
    logfile.Console ("ExplorANT: We're in slave mode, listening to master ANT+ devices")

    #---------------------------------------------------------------------------
    # Initialize dongle
    #---------------------------------------------------------------------------
    AntDongle.Calibrate()                          # calibrate ANT+ dongle

    #---------------------------------------------------------------------------
    # Create ANT+ slave channels for pairing to a master device (HRM, FE, ...)
    #
    # A channel with a wild-card is established when a master-device found.
    # After that moment, no other device will be seen on that channel.
    #
    # If ant.SlaveHRM_ChannelConfig(0) is used, the first HRM will
    # be found and not a list of HRM's.
    #
    # Therefore, open as many channels as devices you want to find.
    #
    # There may be masters around with the pairing bit set and they will be
    # found only when the slave has the pairing bit set as well
    #
    # Therefore set the pairing bit on every odd channel...
    #
    # Ref: D00000652_ANT_Message_Protocol_and_Usage_Rev_5.1.pdf, page 29.
    # ref: AN02_Device_Pairing_Rev2.3.pdf
    #---------------------------------------------------------------------------
    NrDevicesToPair = 8 # Must be > channel_VTX_s !! AND LESS THAN CHANNEL_MAX
    print ('Open channels: ', end='')
    for i in range(0, NrDevicesToPair):
        print (i, end=' ')
        if i == ant.channel_VTX_s:
            AntDongle.SlaveVTX_ChannelConfig(0)
        elif i == ant.channel_VHU_s:
            AntDongle.SlaveVHU_ChannelConfig(0)
        else:
            DeviceNumber    =0
            DeviceTypeID    =0
            TransmissionType=0
            if i % 1 == 1: DeviceTypeID &= 0x80
            AntDongle.SlavePair_ChannelConfig(i, DeviceNumber, DeviceTypeID, TransmissionType)
    print ('')

    deviceIDs = []

    # --------------------------------------------------------------------------
    # Do pairing loop
    # --------------------------------------------------------------------------
    logfile.Console ("Pairing, press Ctrl-C to exit")
    try:
        RunningSwitch  = True
        pairingCounter = 30     # Do pairing for n seconds
        #-------------------------------------------------------------------
        # Ask for ChannelID message
        # Refer to D0652.pdf, page 120. en section 9.5.4.4
        #-------------------------------------------------------------------
        messages = []
        for i in range(0, NrDevicesToPair):
            messages.append (ant.msg4D_RequestMessage(i, ant.msgID_ChannelID) )
        AntDongle.Write(messages, False, False)

        print ('Wait for responses from channel what device is paired: ', end='')
        while RunningSwitch == True and pairingCounter > 0:
            StartTime = time.time()
            #-------------------------------------------------------------------
            # Receive response from channels
            #-------------------------------------------------------------------
            AntDongle.Read(False)

            #-------------------------------------------------------------------
            # Only handle ChannelID messages and ignore everyting else
            #
            # After msgID_ChannelID is received, the master-messages will be
            # received, but we ignore them here because we want to pair only.
            #-------------------------------------------------------------------
            Unknown = True
            while AntDongle.MessageQueueSize() > 0:
                d = AntDongle.MessageQueueGet()
                synch, length, id, info, checksum, rest, Channel, DataPageNumber = \
                    ant.DecomposeMessage(d)

                #---------------------------------------------------------------
                # ChannelResponse: acknowledge message
                #---------------------------------------------------------------
                if id == ant.msgID_ChannelResponse:
                    Unknown = False

                #---------------------------------------------------------------
                # Message BroadcastData, provides a datapage from master
                #---------------------------------------------------------------
                elif id == ant.msgID_BroadcastData:
                    Unknown = False

                #---------------------------------------------------------------
                # ChannelID - the info from a Master device on the network
                #---------------------------------------------------------------
                elif id == ant.msgID_ChannelID:
                    Unknown = False
                    Channel, DeviceNumber, DeviceTypeID, TransmissionType = \
                        ant.unmsg51_ChannelID(info)

                    #-----------------------------------------------------------
                    # Check what DeviceType is discovered
                    #-----------------------------------------------------------
                    if   DeviceTypeID == ant.DeviceTypeID_HRM:
                        DeviceType = 'HRM'
                        if clv.hrm <= 0: clv.hrm = DeviceNumber

                    elif DeviceTypeID == ant.DeviceTypeID_FE:
                        DeviceType = 'FE'
                        if clv.fe <= 0: clv.fe = DeviceNumber

                    elif DeviceTypeID == ant.DeviceTypeID_SCS:
                        if clv.scs <= 0: clv.scs = DeviceNumber
                        DeviceType = 'SCS'

                    elif DeviceTypeID == ant.DeviceTypeID_VTX:
                        if clv.vtx <= 0: clv.vtx = DeviceNumber
                        DeviceType = 'VTX'

                    elif DeviceTypeID == ant.DeviceTypeID_VHU:
                        if clv.vhu <= 0: clv.vhu = DeviceNumber
                        DeviceType = 'VHU'

                    else:
                        DeviceType = '?'

                    #-----------------------------------------------------------
                    # Store in device table, so we print at the end of loop
                    #-----------------------------------------------------------
                    deviceID = clsDeviceID(Channel, DeviceType, DeviceNumber, DeviceTypeID, TransmissionType)
                    # print (Channel, end=' ')
                    if DeviceNumber == 0:      # No device paired, request again
                        AntDongle.Write([ant.msg4D_RequestMessage(Channel, ant.msgID_ChannelID)], \
                                        False, False)
                        pass
                    else:
                        d = deviceID
                        logfile.Write ("ExplorANT: %3s discovered on channel=%s, number=%5s typeID=%3s TrType=%3s" % \
                            (d.DeviceType, d.Channel, d.DeviceNumber, d.DeviceTypeID, d.TransmissionType) )
                        if not deviceID in deviceIDs:
                            print('%s=%s' % (d.Channel, DeviceType), end=' ')
                            logfile.Write('ExplorANT: added to list')

                            deviceIDs.append(deviceID)

                            #---------------------------------------------------
                            # Ask the found device for more info; page 70
                            #---------------------------------------------------
                            info = ant.msgPage70_RequestDataPage(Channel, ant.DeviceNumber_EA, 255, 255, 1, 70, 0)
                            d    = ant.ComposeMessage (ant.msgID_AcknowledgedData, info)
                            AntDongle.Write([d], False)
                        else:
                            print('*', end=' ')
                            logfile.Write('ExplorANT: already in list')

                    deviceID = None
                else:
                    logfile.Console ("Ignore message id=%s ch=%s page=%s" % (hex(id), Channel, DataPageNumber))
                    pass

            #-------------------------------------------------------------------
            # Show some movement on screen during pairing
            #-------------------------------------------------------------------
            print('.', end=' ')
            sys.stdout.flush()

            #-------------------------------------------------------------------
            # WAIT        So we do not cycle faster than 4 x per second
            #-------------------------------------------------------------------
            SleepTime = 0.25 - (time.time() - StartTime)
            if SleepTime > 0: time.sleep(SleepTime)

            pairingCounter -= 0.25              # Subtract quarter second

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logfile.Console ("Pairing loop stopped due to exception: " + str(e))
    print('')
    logfile.Console ("Pairing stopped")

    #---------------------------------------------------------------------------
    # Show what devices discovered
    #---------------------------------------------------------------------------
    for d in deviceIDs:
        logfile.Console (" %3s discovered on channel=%s, number=%5s typeID=%3s TrType=%3s" % \
            (d.DeviceType, d.Channel, d.DeviceNumber, d.DeviceTypeID, d.TransmissionType) )
    logfile.Console ("--------------------")

    #---------------------------------------------------------------------------
    # Free pairing channels
    #---------------------------------------------------------------------------
    messages = []
    for i in range(0, NrDevicesToPair):
        messages.append ( ant.msg41_UnassignChannel(i) )    # Does not have much effect
        pass
    AntDongle.Write(messages)
    AntDongle.ResetDongle ()                          # This one does the job

while AntDongle.OK:
    #---------------------------------------------------------------------------
    # If any channel specified and/or found: Open the device channels & listen.
    #---------------------------------------------------------------------------
    if clv.vtx < 0: clv.vtx = ant.DeviceNumber_VTX # Not found during pair, try anyway
    if clv.vhu < 0: clv.vhu = ant.DeviceNumber_VHU # Not found during pair, try anyway
    if clv.SimulateTrainer or clv.hrm >= 0 or clv.fe >= 0 or clv.scs >= 0 or clv.vtx >= 0 or clv.vhu >= 0:
        # ----------------------------------------------------------------------
        # Calibrate ANT+ dongle (because reset was done!)
        # ----------------------------------------------------------------------
        AntDongle.Calibrate()

        # ----------------------------------------------------------------------
        # Open channels
        # ----------------------------------------------------------------------
        if clv.SimulateTrainer:
            #-----------------------------------------------------------------------
            # We are going to simulate MASTER devices
            #-----------------------------------------------------------------------
            logfile.Console ("ExplorANT: We're simulating master ANT+ devices")

            if clv.hrm >= 0:
                hrm.Initialize()
                AntDongle.HRM_ChannelConfig()
                logfile.Console ('HRM master channel %s opened; device %s (act as an HRM)' % (ant.channel_HRM, ant.DeviceNumber_HRM))

            if clv.fe  >= 0:
                fe.Initialize()
                AntDongle.Trainer_ChannelConfig()
                logfile.Console ('FE  master channel %s opened; device %s (act as a Tacx Trainer)' % (ant.channel_FE, ant.DeviceNumber_FE))

            if clv.vtx >= 0:
                AntDongle.VTX_ChannelConfig()
                logfile.Console ('VTX master channel %s opened; device %s (act as a Tacx -Vortex)' % (ant.channel_VTX, ant.DeviceNumber_VTX))

        else:
            if clv.hrm > 0:
                AntDongle.SlaveHRM_ChannelConfig(clv.hrm)
                logfile.Console ('HRM slave channel %s opened; listening to master device %s' % (ant.channel_HRM_s, clv.hrm))

            if clv.fe  > 0:
                AntDongle.SlaveTrainer_ChannelConfig(clv.fe)
                logfile.Console ('FE  slave channel %s opened; listening to master device %s' % (ant.channel_FE_s,  clv.fe))

            if clv.scs > 0:
                AntDongle.SlaveSCS_ChannelConfig(clv.scs)
                logfile.Console ('SCS slave channel %s opened; listening to master device %s' % (ant.channel_SCS_s,  clv.scs))

            if clv.vtx > 0:
                AntDongle.SlaveVTX_ChannelConfig(clv.vtx)
                logfile.Console ('VTX slave channel %s opened; listening to master device %s' % (ant.channel_VTX_s, 0))

            if clv.vhu > 0:
                AntDongle.SlaveVHU_ChannelConfig(clv.vhu)
                logfile.Console ('VHU slave channel %s opened; listening to master device %s' % (ant.channel_VHU_s, 0))

        # ----------------------------------------------------------------------
        # Get info from the devices
        # ----------------------------------------------------------------------
        logfile.Console ("Listening, press Ctrl-C to exit")
        try:
        # if True:
            RunningSwitch       = True

            HRM_s_count         = 0
            HRM_HeartRate       = -1
            HRM_page2_done      = False
            HRM_page3_done      = False

            FE_s_count          = 0
            FE_Power            = -1
            FE_Cadence          = -1
            FE_Speed            = -1
            FE_HeartRate        = -1
            FE_page80_done      = False
            FE_page81_done      = False

            SCS_s_count         = 0

            VTX_UsingVirtualSpeed, VTX_Power, VTX_Speed, VTX_CalibrationState, VTX_Cadence = 0,0,0,0,0
            VTX_S1, VTX_S2, VTX_Serial, VTX_Alarm = 0,0,0,0
            VTX_Major, VTX_Minor, VTX_Build = 0,0,0
            VTX_Calibration, VTX_VortexID = 0,0
            VortexData          = False # Can be used to test the Tacx Vortex Unpage functions
            VortexPower         = True  # Can be used to test the Tacx Vortex setPower function
            Power               = -1

            listenCount         = 0

            dpBasicResistance   = 0     # Requests received from Trainer Road or Zwift
            dpTargetPower       = 0
            dpTrackResistance   = 0
            dpUserConfiguration = 0
            dpRequestDatapage   = 0

            TargetPower  	    = 100   # For SimulateTrainer
            CurrentPower	    = 100

            EventCounter        = 0

            while RunningSwitch == True and not AntDongle.DongleReconnected:
                StartTime = time.time()
                #---------------------------------------------------------------
                # Simulate HRM, FE-S, VTX (master device, broadcasting data)
                #---------------------------------------------------------------
                messages     = []

                if clv.SimulateTrainer:
                    if False:
                        raise NotImplementedError
                        # SpeedKmh, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, CurrentResistance, Buttons, Axis = \
                        #     SimulateReceiveFromTrainer (TargetPower, CurrentPower)
                    else:
                        Cadence, CurrentPower, SpeedKmh, HeartRate = 98, 234, 35.6, 123     # Always the same, ennoying but predictable

                    if clv.hrm >= 0:
                        messages.append(hrm.BroadcastHeartrateMessage (HeartRate))

                    if clv.fe >= 0:
                        messages.append(fe.BroadcastTrainerDataMessage(Cadence, CurrentPower, SpeedKmh, HeartRate))

                    if clv.vtx >= 0:
                        EventCounter += 1
                        if EventCounter == 64: EventCounter = 0

                        if EventCounter % 64 < 4:  # Transmit 4 times (0, 1, 2, 3) Page 3
                            messages.append ( ant.ComposeMessage (ant.msgID_BroadcastData, \
                                                ant.msgPage03_TacxVortexDataCalibration (ant.channel_VTX, 0, ant.DeviceNumber_VTX)))
                        else:                       # Transmit 60 times (4...63)    Page 0
                            messages.append ( ant.ComposeMessage (ant.msgID_BroadcastData, \
                                                ant.msgPage00_TacxVortexDataSpeed (ant.channel_VTX, CurrentPower, SpeedKmh, Cadence)))

                #---------------------------------------------------------------
                # Receive data
                #---------------------------------------------------------------
                if clv.SimulateTrainer and len(messages) > 0:
                    AntDongle.Write(messages, True, False)
                else:
                    AntDongle.Read( False)

                #---------------------------------------------------------------
                # Simulate vortex data, just to test the loop
                #---------------------------------------------------------------
                if AntDongle.MessageQueueSize() == 0 and VortexData:
                    VortexData = False
                    messages = [    'a4 09 4e 07 00 00 03 60 08 00 8a 00 05', \
                                    'a4 09 4e 07 00 00 00 cc 00 00 18 00 30', \
                                    'a4 09 4e 07 01 3d 0d 00 29 42 00 00 be', \
                                    'a4 09 4e 07 02 00 61 83 00 02 00 07 01', \
                                    'a4 09 4e 07 03 ff ff ff ff 0e 30 b0 69'  \
                                ]
                    for m in messages:
                        d = binascii.unhexlify(m.replace(' ',''))
                        AntDongle.MessageQueuePut(d)

                #---------------------------------------------------------------
                # Here all response from the ANT dongle are processed
                #
                # A message is the communication with the network (the dongle)
                # A datapage is the data that is exchanged with another device
                #       on the network
                #---------------------------------------------------------------
                Unknown = True
                while AntDongle.MessageQueueSize() > 0:
                    d = AntDongle.MessageQueueGet()
                    synch, length, id, info, checksum, rest, Channel, DataPageNumber = ant.DecomposeMessage(d)

                    #-----------------------------------------------------------
                    # Message ChannelResponse, acknowledges a message
                    #-----------------------------------------------------------
                    if id == ant.msgID_ChannelResponse:
                        # Ignore
                        Unknown = False

                    #-----------------------------------------------------------
                    # Message BroadcastData, provides a datapage from master
                    #-----------------------------------------------------------
                    elif id == ant.msgID_BroadcastData:
                        #-------------------------------------------------------
                        # HRM_s = Heart rate Monitor Display
                        # We are slave, listening to a master (Heartrate belt)
                        #-------------------------------------------------------
                        if Channel == ant.channel_HRM_s:
                            HRM_s_count += 1
                            if HRM_s_count > 99: HRM_s_count= 0
                            #---------------------------------------------------
                            # Data page 0...4 HRM data
                            #---------------------------------------------------
                            if DataPageNumber & 0x7f in (0,1,2,3,4,5,6,7,89):
                                Unknown = False
                                Channel, DataPageNumber, Spec1, Spec2, Spec3, HeartBeatEventTime, HeartBeatCount, HRM_HeartRate = \
                                    ant.msgUnpage_Hrm(info)
                                if DataPageNumber & 0x7f == 2:
                                    if HRM_page2_done == False:
                                        HRM_page2_done = True
                                        HRM_ManufacturerID = Spec1
                                        HRM_SerialNumber   = (Spec3 << 8) + Spec2
                                        logfile.Console ("HRM page=%s ManufacturerID=%s SerialNumber=%s" % \
                                                    (DataPageNumber, HRM_ManufacturerID, HRM_SerialNumber))

                                if DataPageNumber & 0x7f == 3:
                                    if HRM_page3_done == False:
                                        HRM_page3_done = True
                                        HRM_HWrevision = Spec1
                                        HRM_SWversion  = Spec2
                                        HRM_Model      = Spec3
                                        logfile.Console ("HRM page=%s HWrevision=%s, SWversion=%s Model=%s" % \
                                                (DataPageNumber, HRM_HWrevision, HRM_SWversion, HRM_Model))


                            #---------------------------------------------------
                            # Data page 89   ??????????????????????????????
                            #---------------------------------------------------
                            elif DataPageNumber == 89:
                                Unknown = True

                        #-------------------------------------------------------
                        # FE_s = Cycle Training Program (e.g. Zwift, Trainer Road)
                        # We are slave, listening to a master Tacx Trainer
                        #-------------------------------------------------------
                        elif Channel == ant.channel_FE_s:
                            FE_s_count += 1
                            if FE_s_count > 99: FE_s_count= 0
                            #---------------------------------------------------
                            # Data page 16 (0x10) General FE data
                            #---------------------------------------------------
                            if DataPageNumber == 16:
                                Unknown = False
                                Channel, DataPageNumber, EquipmentType, ElapsedTime, DistanceTravelled, \
                                    FE_Speed, FE_HeartRate, Capabilities = \
                                    ant.msgUnpage16_GeneralFEdata(info)

                                FE_Speed = round( FE_Speed / ( 1000*1000/3600 ), 1)

                            #---------------------------------------------------
                            # Data page 25 (0x19) Trainer info
                            #---------------------------------------------------
                            elif DataPageNumber == 25:
                                Unknown = False
                                Channel, DataPageNumber, xx_Event, FE_Cadence, xx_AccPower, FE_Power, xx_Flags = \
                                    ant.msgUnpage25_TrainerData(info)

                            #---------------------------------------------------
                            # Data page 80 (0x50) Manufacturers info
                            #---------------------------------------------------
                            elif DataPageNumber == 80:
                                Unknown = False
                                if FE_page80_done == False:
                                    FE_page80_done = True
                                    Channel, DataPageNumber, Reserved, Reserved, FE_HWrevision, FE_ManufacturerID, FE_ModelNumber = \
                                        ant.msgUnpage80_ManufacturerInfo(info)
                                    logfile.Console ("FE Page=%s HWrevision=%s ManufacturerID=%s Model=%s" % \
                                                   (DataPageNumber, FE_HWrevision, FE_ManufacturerID, FE_ModelNumber))

                            #---------------------------------------------------
                            # Data page 81 (0x51) Product Information
                            #---------------------------------------------------
                            elif DataPageNumber == 81:
                                Unknown = False
                                if FE_page81_done == False:
                                    FE_page81_done = True
                                    Channel, DataPageNumber, Reserved1, FE_SWrevisionSupp, FE_SWrevisionMain, FE_SerialNumber = \
                                        ant.msgUnpage81_ProductInformation(info)
                                    logfile.Console ("FE Page=%s SWrevision=%s.%s Serial#=%s" % \
                                                   (DataPageNumber, FE_SWrevisionMain, FE_SWrevisionSupp, FE_SerialNumber))

                        #-------------------------------------------------------
                        # SCS_s = Heart rate Monitor Display
                        # We are slave, listening to a master (Speed Cadence Sensor)
                        #-------------------------------------------------------
                        if Channel == ant.channel_SCS_s:
                            SCS_s_count += 1
                            if SCS_s_count > 99: SCS_s_count= 0

                            #---------------------------------------------------
                            # Only one Data page for SCS! msgUnpage_SCS
                            #---------------------------------------------------
                            Unknown = False
                            EventTime, CadenceRevolutionCount, _EventTime, \
                                SpeedRevolutionCount = ant.msgUnpage_SCS(info)

                            try:
                                _ = pEventTime
                            except:
                                pass
                            else:
                                if EventTime != pEventTime:
                                    cadence = 60 * (CadenceRevolutionCount - pCadenceRevolutionCount) * 1024 / \
                                                (EventTime - pEventTime)
                                    cadence = int(cadence)

                                    speed   = (SpeedRevolutionCount - pSpeedRevolutionCount) * 2.096 * 3.600 /  \
                                                (EventTime - pEventTime)
                                    print ('EventTime=%5s (%5s) CadenceRevolutionCount=%5s (%5s) Cadence=%3s EventTime=%5s SpeedRevolutionCount=%5s Speed=%4.1f' % \
                                        (EventTime, EventTime - pEventTime, \
                                         CadenceRevolutionCount, CadenceRevolutionCount - pCadenceRevolutionCount, \
                                         cadence, _EventTime, SpeedRevolutionCount, speed))
                            pCadenceRevolutionCount = CadenceRevolutionCount
                            pSpeedRevolutionCount   = SpeedRevolutionCount
                            pEventTime              = EventTime

                        #-------------------------------------------------------
                        # VTX_s = Tacx i-Vortex trainer
                        # We are slave, listening to a master (the real trainer)
                        #-------------------------------------------------------
                        elif Channel == ant.channel_VTX_s:
                            #---------------------------------------------------
                            # Data page 00 msgUnpage00_TacxVortexDataSpeed
                            #---------------------------------------------------
                            if DataPageNumber == 0:
                                Unknown = False
                                VTX_UsingVirtualSpeed, VTX_Power, VTX_Speed, VTX_CalibrationState, VTX_Cadence = \
                                    ant.msgUnpage00_TacxVortexDataSpeed(info)
                                VTX_Speed = round( VTX_Speed / ( 100 * 1000 / 3600 ), 1)
                                # logfile.Console ('i-Vortex Page=%s UsingVirtualSpeed=%s Power=%s Speed=%s State=%s Cadence=%s' % \
                                #   (DataPageNumber, VTX_UsingVirtualSpeed, VTX_Power, VTX_Speed, VTX_CalibrationState, VTX_Cadence) )

                            #---------------------------------------------------
                            # Data page 01 msgUnpage01_TacxVortexDataSerial
                            #---------------------------------------------------
                            elif DataPageNumber == 1:
                                Unknown = False
                                VTX_S1, VTX_S2, VTX_Serial, VTX_Alarm = ant.msgUnpage01_TacxVortexDataSerial(info)
                                logfile.Console ('i-Vortex Page=%s S1=%s S2=%s Serial=%s Alarm=%s' % \
                                    (DataPageNumber, VTX_S1, VTX_S2, VTX_Serial, VTX_Alarm) )

                            #---------------------------------------------------
                            # Data page 02 msgUnpage02_TacxVortexDataVersion
                            #---------------------------------------------------
                            elif DataPageNumber == 2:
                                Unknown = False
                                VTX_Major, VTX_Minor, VTX_Build = ant.msgUnpage02_TacxVortexDataVersion(info)
                                logfile.Console ('i-Vortex Page=%s Major=%s Minor=%s Build=%s' % \
                                    (DataPageNumber, VTX_Major, VTX_Minor, VTX_Build))

                            #---------------------------------------------------
                            # Data page 03 msgUnpage03_TacxVortexDataCalibration
                            #---------------------------------------------------
                            elif DataPageNumber == 3:
                                Unknown = False
                                VTX_Calibration, VTX_VortexID = ant.msgUnpage03_TacxVortexDataCalibration(info)
                                # logfile.Console ('i-Vortex Page=%s Calibration=%s VortexID=%s' % \
                                #    (DataPageNumber, VTX_Calibration, VTX_VortexID))

                        #-------------------------------------------------------
                        # VTX = Cycle Training Program (e.g. Zwift, Trainer Road)
                        # We are slave, listening to a master Fortius ANT or TTS
                        #
                        #-------------------------------------------------------
                        elif Channel == ant.channel_VTX:
                            VTX_Channel, VTX_DataPageNumber, VTX_VortexID, VTX_Command, VTX_Subcommand, VTX_NoCalibrationData, VTX_Power = \
                                ant.msgUnpage16_TacxVortexSetPower(info)
                            Unknown = False

                    elif id == ant.msgID_AcknowledgedData:
                        #-----------------------------------------------------------
                        # Fitness Equipment Channel inputs (Trainer Road, Zwift)
                        #-----------------------------------------------------------
                        if Channel == ant.channel_FE:
                            #-------------------------------------------------------
                            # Data page 48 (0x30) Basic resistance
                            #-------------------------------------------------------
                            if   DataPageNumber == 48:
                                dpBasicResistance += 1

                            #-------------------------------------------------------
                            # Data page 49 (0x31) Target Power
                            #-------------------------------------------------------
                            elif   DataPageNumber == 49:
                                dpTargetPower += 1

                            #-------------------------------------------------------
                            # Data page 51 (0x33) Track resistance
                            #-------------------------------------------------------
                            elif DataPageNumber == 51:
                                dpTrackResistance += 1

                            #-------------------------------------------------------
                            # Data page 55 User configuration
                            #-------------------------------------------------------
                            elif DataPageNumber == 55:
                                dpUserConfiguration += 1

                            #-------------------------------------------------------
                            # Data page 70 Request data page
                            #-------------------------------------------------------
                            elif DataPageNumber == 70:
                                dpRequestDatapage += 1
                                SlaveSerialNumber, DescriptorByte1, DescriptorByte2, AckRequired, NrTimes, \
                                    RequestedPageNumber, CommandType = ant.msgUnpage70_RequestDataPage(info)

                                info = False
                                if   RequestedPageNumber == 80:
                                    info = ant.msgPage80_ManufacturerInfo(ant.channel_FE, 0xff, 0xff, \
                                        ant.HWrevision_FE, ant.Manufacturer_tacx, ant.ModelNumber_FE)
                                    comment = "(Manufactorer info)"
                                elif RequestedPageNumber == 81:
                                    info = ant.msgPage81_ProductInformation(ant.channel_FE, 0xff, \
                                        ant.SWrevisionSupp_FE, ant.SWrevisionMain_FE, ant.SerialNumber_FE)
                                    comment = "(Product info)"
                                elif RequestedPageNumber == 82:
                                    info = ant.msgPage82_BatteryStatus(ant.channel_FE)
                                    comment = "(Battery status)"
                                else:
                                    error = "Requested page not suported"
                                if info != False:
                                    data = []
                                    d    = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                                    while (NrTimes):
                                        data.append(d)
                                        NrTimes -= 1
                                    AntDongle.Write(data, False)

                            #-------------------------------------------------------
                            # Other data pages
                            #-------------------------------------------------------
                            else: error = "Unknown FE data page"
                    if Unknown:
                        logfile.Console ("IGNORED!! msg=%s ch=%s p=%s info=%s" % \
                                        (hex(id), Channel, DataPageNumber, logfile.HexSpace(info)))

                #-------------------------------------------------------
                # WAIT So we do not cycle faster than 4 x per second
                #-------------------------------------------------------
                SleepTime = 0.25 - (time.time() - StartTime)
                if SleepTime > 0: time.sleep(SleepTime)

                #-------------------------------------------------------
                # Inform once per second
                #-------------------------------------------------------
                listenCount += 1
                if listenCount == 4:
                    listenCount = 0
                    if clv.SimulateTrainer:
                        logfile.Console ( ("Simulate Cadence=%3s Power=%3s Speed=%4.1f hr=%3s " + \
                                           "FE-C bRes=%s tPower=%s tRes=%s " + \
                                           "VTX  %s tPower=%s") % \
                                          (Cadence, CurrentPower, SpeedKmh, HeartRate, \
                                           dpBasicResistance, dpTargetPower, dpTrackResistance, \
                                           VTX_VortexID, VTX_Power \
                                          ) \
                                        )

                    else:
                        logfile.Console ("HRM#=%2s hr=%3s FE-C#=%2s Speed=%4s Cadence=%3s Power=%3s hr=%3s SCS#=%2s VTX ID=%s Speed=%4s Cadence=%3s Target=%s" % \
                                         (HRM_s_count, HRM_HeartRate, \
                                          FE_s_count, FE_Speed, FE_Cadence, FE_Power, FE_HeartRate, \
                                          SCS_s_count, \
                                          VTX_VortexID, VTX_Speed, VTX_Cadence, Power
                                         )\
                                        )

                #-------------------------------------------------------
                # Set Tacx Vortex power, once per second
                #-------------------------------------------------------
                if not clv.SimulateTrainer and listenCount == 0 and VortexPower and VTX_VortexID:
                    Power = 100 + time.localtime().tm_sec
                    logfile.Console('ExplorANT: Set Tacx Vortex power %s' % Power)
                    info = ant.msgPage16_TacxVortexSetPower (ant.channel_VTX_s, VTX_VortexID, Power)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                    AntDongle.Write([msg], False)

        except KeyboardInterrupt:
            logfile.Console ("Listening stopped")
        except Exception as e:
            logfile.Console ("Listening stopped due to exception: " + str(e))
        #---------------------------------------------------------------
        # Free channel
        #---------------------------------------------------------------
        messages = []
        if clv.hrm > 0: messages.append ( ant.msg41_UnassignChannel(ant.channel_HRM_s) )
        if clv.fe  > 0: messages.append ( ant.msg41_UnassignChannel(ant.channel_FE_s ) )
        AntDongle.Write(messages)
        #---------------------------------------------------------------
        # Release dongle
        #-----------------------------------------------------------------------
        AntDongle.ResetDongle ()
    #---------------------------------------------------------------------------
    # Quit "while AntDongle.OK"
    #---------------------------------------------------------------------------
    if AntDongle.DongleReconnected:
        AntDongle.ApplicationRestart()
    else:
        break
logfile.Console ("We're done")
logfile.Console ("--------------------")
