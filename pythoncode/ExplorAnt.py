#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-01-29"
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
import debug
import ExplorAntCommand  as cmd
import logfile

# ==============================================================================
# Main program; Command line parameters
# ==============================================================================
global clv

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
clv = cmd.Create()
debug.activate(clv.debug)

if True or debug.on(debug.Any):
    logfile.Open  ('ExplorANT')
    logfile.Write ("ExplorANT started")
    clv.print()
    logfile.Write ("--------------------")

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

devAntDongle, msg = ant.GetDongle(p)
logfile.Write (msg)

if devAntDongle:
    #---------------------------------------------------------------------------
    # Initialize dongle
    #---------------------------------------------------------------------------
    ant.Calibrate(devAntDongle)                          # calibrate ANT+ dongle

    #---------------------------------------------------------------------------
    # Create ANT+ slave channels for pairing to a master device (HRM, FE, ...)
    #
    # A channel with a wild-card is established when a master-device found.
    # After that moment, no other device will be seen on that channel.
    #
    # If ant.SlaveHRM_ChannelConfig(devAntDongle, 0) is used, the first HRM will
    # be found and not a list of HRM's.
    #
    # Therefore, open as many channels as devices you want to find.
    #---------------------------------------------------------------------------
    NrDevicesToPair = 10
    for i in range(0, NrDevicesToPair):
        ant.SlavePair_ChannelConfig(devAntDongle, i)
    deviceIDs = []

    # --------------------------------------------------------------------------
    # Do pairing loop
    # --------------------------------------------------------------------------
    logfile.Write ("Pairing, press Ctrl-C to exit")
    try:
        RunningSwitch  = True
        pairingCounter = 10             # Do pairing for n seconds
        #-------------------------------------------------------------------
        # Ask for ChannelID message
        # Refer to D0652.pdf, page 120. en section 9.5.4.4
        #-------------------------------------------------------------------
        messages = []
        for i in range(0, NrDevicesToPair):
            messages.append (ant.msg4D_RequestMessage(i, ant.msgID_ChannelID) )
        ant.SendToDongle(messages, devAntDongle, '', False, False)

        while RunningSwitch == True and pairingCounter > 0:
            StartTime = time.time()
            #-------------------------------------------------------------------
            # Receive response from channels
            #-------------------------------------------------------------------
            data = ant.ReadFromDongle(devAntDongle, False)

            #-------------------------------------------------------------------
            # Only handle ChannelID messages and ignore everyting else
            #
            # After msgID_ChannelID is received, the master-messages will be
            # received, but we ignore them here because we want to pair only.
            #-------------------------------------------------------------------
            Unknown = True
            for d in data:
                synch, length, id, info, checksum, rest, Channel, DataPageNumber = \
                    ant.DecomposeMessage(d)

                #---------------------------------------------------------------
                # ChannelID - the info from a Master device on the network
                #---------------------------------------------------------------
                if id == ant.msgID_ChannelID:
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

                    else:
                        DeviceType = '?'

                    #-----------------------------------------------------------
                    # Store in device table, so we print at the end of loop
                    #-----------------------------------------------------------
                    deviceID = (DeviceType, DeviceNumber, DeviceTypeID, TransmissionType)
                    if DeviceNumber == 0:       # The pairing device (?)
                        pass                    
                    else:
                        if not deviceID in deviceIDs:
                            deviceIDs.append(deviceID)
                            print(DeviceType, end=' ')
                else:
                    # logfile.Write ("Ignore message ch=%s id=%s page=%s" % (Channel, id, DataPageNumber))
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
    print('')
    logfile.Write ("Pairing stopped")

    #---------------------------------------------------------------------------
    # Show what devices discovered
    #---------------------------------------------------------------------------
    for deviceID in deviceIDs:
        logfile.Write ("Discovered %3s: number=%5s typeID=%3s TransmissionType=%3s" % deviceID)
    logfile.Write ("--------------------")
    
    #---------------------------------------------------------------------------
    # Free pairing channels
    #---------------------------------------------------------------------------
    messages = []
    for i in range(0, NrDevicesToPair):
        messages.append ( ant.msg41_UnassignChannel(i) )
    ant.SendToDongle(messages, devAntDongle)

    #---------------------------------------------------------------------------
    # If any channel specified and/or found: Open the device channels & listen.
    #---------------------------------------------------------------------------
    if clv.hrm > 0 or clv.fe > 0:
        if clv.hrm > 0:
            ant.SlaveHRM_ChannelConfig(devAntDongle, clv.hrm)
            logfile.Write ('HRM channel %s opened for device %s' % (ant.channel_HRM, clv.hrm))

        if clv.fe > 0:
            ant.SlaveTrainer_ChannelConfig(devAntDongle, clv.fe)
            logfile.Write ('FE  channel %s opened for device %s' % (ant.channel_FE,  clv.fe))

        # ----------------------------------------------------------------------
        # Get info from the master devices
        # ----------------------------------------------------------------------
        logfile.Write ("Listening, press Ctrl-C to exit")
        try:
            RunningSwitch  = True
            
            HRM_HeartRate = -1
            
            FE_Power      = -1
            FE_Cadence    = -1
            FE_Speed      = -1
            FE_HeartRate  = -1
            
            listenCount   = 0
            while RunningSwitch == True:
                StartTime = time.time()
                #---------------------------------------------------------------
                # Receive data
                #---------------------------------------------------------------
                data = ant.ReadFromDongle(devAntDongle, False)

                #---------------------------------------------------------------
                # Here all response from the ANT dongle are processed
                #
                # A message is the communication with the network (the dongle)
                # A datapage is the data that is exchanged with another device
                #       on the network
                #---------------------------------------------------------------
                Unknown = True
                for d in data:
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
                        # Data page 0...4 HRM data
                        #-------------------------------------------------------
                        if DataPageNumber & 0x7f in (0,1,2,3,4,5,6,7):
                            Unknown = False
                            Channel, DataPageNumber, Spec1, Spec2, Spec3, HeartBeatEventTime, HeartBeatCount, HRM_HeartRate = \
                                ant.msgUnpage_Hrm(info)

                        #-------------------------------------------------------
                        # Data page 16 (0x10) General FE Data
                        #-------------------------------------------------------
                        elif DataPageNumber == 16:
                            Unknown = False
                            Channel, DataPageNumber, EquipmentType, ElapsedTime, DistanceTravelled, FE_Speed, FE_HeartRate, Capabilities = \
                                ant.msgUnpage16_GeneralFEdata(info)

                        #-------------------------------------------------------
                        # Data page 25 (0x19) Manufacturers info
                        #-------------------------------------------------------
                        elif DataPageNumber == 25:    
                            Unknown = False
                            Channel, DataPageNumber, Event, FE_Cadence, AccPower, FE_Power, Flags = \
                                ant.msgUnpage25_TrainerData(info)

                        #-------------------------------------------------------
                        # Data page 89   ??????????????????????????????
                        #-------------------------------------------------------
                        elif DataPageNumber == 89:    
                            Unknown = True
                            
                        #-------------------------------------------------------
                        # Data page 80 (0x50) Manufacturers info
                        #-------------------------------------------------------
                        elif DataPageNumber == 80:    
                            Unknown = False
                            Channel, DataPageNumber, Reserved, Reserved, HWrevision, ManufacturerID, ModelNumber = \
                                ant.msgUnpage80_ManufacturerInfo(info)
                            logfile.Write ("ch=%s page=%s res1=%s res2=%s HWrev=%s manID=%s model=%s" % \
                                (Channel, DataPageNumber, Reserved, Reserved, HWrevision, ManufacturerID, ModelNumber))

                        #-------------------------------------------------------
                        # Data page 81 (0x51) Product Information
                        #-------------------------------------------------------
                        elif DataPageNumber == 81:
                            Unknown = False
                            Channel, DataPageNumber, Reserved1, SWrevisionSupp, SWrevisionMain, SerialNumber = \
                                ant.msgUnpage81_ProductInformation(info)
                            logfile.Write ("ch=%s page=%s res1=%s SWrevS=%s SWrevM=%s model=%s" % \
                                (Channel, DataPageNumber, Reserved1, SWrevisionSupp, SWrevisionMain, SerialNumber))

                    if Unknown:
                        logfile.Write ("IGNORED!! synch=%s len=%s id=%s info=%s, channel=%s pagenumber=%s" % \
                            (hex(synch),length,hex(id), logfile.HexSpace(info), Channel, DataPageNumber))
            
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
                    logfile.Write ("HRM hr=%3s TRAINER Speed=%4s Cadence=%3s Power=%3s hr=%3s" % \
                                    (HRM_HeartRate, FE_Speed, FE_Cadence, FE_Power, FE_HeartRate))
                    
        except KeyboardInterrupt:
            logfile.Write ("Listening stopped")
        #---------------------------------------------------------------
        # Free channel
        #---------------------------------------------------------------
        messages = []
        if clv.hrm > 0: messages.append ( ant.msg41_UnassignChannel(ant.channel_HRM) )
        if clv.fe  > 0: messages.append ( ant.msg41_UnassignChannel(ant.channel_FE ) )
        ant.SendToDongle(messages, devAntDongle)
logfile.Write ("We're done")
logfile.Write ("--------------------")