#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-02-18"
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

from  FortiusAnt        import SimulateReceiveFromTrainer 

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

                    else:
                        DeviceType = '?'

                    #-----------------------------------------------------------
                    # Store in device table, so we print at the end of loop
                    #-----------------------------------------------------------
                    deviceID = clsDeviceID(Channel, DeviceType, DeviceNumber, DeviceTypeID, TransmissionType)
                    if DeviceNumber == 0:       # The pairing device (?)
                        pass                    
                    else:
                        print('*', end=' ')
                        if not deviceID in deviceIDs:
                            deviceIDs.append(deviceID)
                            print(DeviceType, end=' ')
                            
                            #---------------------------------------------------
                            # Ask the found device for more info; page 70
                            #---------------------------------------------------
                            info = ant.msgPage70_RequestDataPage(Channel, ant.DeviceNumber_EA, 255, 255, 1, 70, 0)
                            d    = ant.ComposeMessage (ant.msgID_AcknowledgedData, info)
                            ant.SendToDongle([d], devAntDongle, '', False)
                    deviceID = None
                else:
                    logfile.Write ("Ignore message id=%s ch=%s page=%s" % (hex(id), Channel, DataPageNumber))
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
    for d in deviceIDs:
        logfile.Write ("%3s discovered on channel=%s, number=%5s typeID=%3s TrType=%3s" % \
            (d.DeviceType, d.Channel, d.DeviceNumber, d.DeviceTypeID, d.TransmissionType) )
    logfile.Write ("--------------------")
    
    #---------------------------------------------------------------------------
    # Free pairing channels
    #---------------------------------------------------------------------------
    messages = []
    for i in range(0, NrDevicesToPair):
        messages.append ( ant.msg41_UnassignChannel(i) )    # Does not have much effect
        pass
    ant.SendToDongle(messages, devAntDongle)
    ant.ResetDongle (devAntDongle)                          # This one does the job
    
    #---------------------------------------------------------------------------
    # If any channel specified and/or found: Open the device channels & listen.
    #---------------------------------------------------------------------------
    if True or clv.hrm > 0 or clv.fe > 0:
        # ----------------------------------------------------------------------
        # Calibrate ANT+ dongle (because reset was done!)
        # ----------------------------------------------------------------------
        ant.Calibrate(devAntDongle)
        
        # ----------------------------------------------------------------------
        # Open channels
        # ----------------------------------------------------------------------
        if clv.SimulateTrainer:
            hrm.Initialize()
            fe.Initialize()

            clv.hrm = -1 # When simulating master do not act as slave
            ant.HRM_ChannelConfig(devAntDongle)
            logfile.Write ('HRM master channel %s opened; device %s' % (ant.channel_HRM, ant.DeviceNumber_HRM))

            clv.fe = -1 # When simulating master do not act as slave
            ant.Trainer_ChannelConfig(devAntDongle)
            logfile.Write ('FE master channel %s opened; device %s' % (ant.channel_FE, ant.DeviceNumber_FE))

        if clv.hrm > 0:
            ant.SlaveHRM_ChannelConfig(devAntDongle, clv.hrm)
            logfile.Write ('HRM slave channel %s opened; listening to device %s' % (ant.channel_HRM_s, clv.hrm))

        if clv.fe > 0:
            ant.SlaveTrainer_ChannelConfig(devAntDongle, clv.fe)
            logfile.Write ('FE  slave channel %s opened; listening to device %s' % (ant.channel_FE_s,  clv.fe))

        # ----------------------------------------------------------------------
        # Get info from the devices
        # ----------------------------------------------------------------------
        logfile.Write ("Listening, press Ctrl-C to exit")
        try:
            RunningSwitch   = True
            
            HRM_s_count     = 0
            HRM_HeartRate   = -1
            HRM_page2_done  = False
            HRM_page3_done  = False

            FE_s_count      = 0
            FE_Power        = -1
            FE_Cadence      = -1
            FE_Speed        = -1
            FE_HeartRate    = -1
            FE_page80_done  = False
            FE_page81_done  = False
            
            listenCount     = 0

            dpBasicResistance     = 0       #  Requests received from Trainer Road or Zwift
            dpTargetPower         = 0
            dpTrackResistance     = 0
            dpUserConfiguration   = 0
            dpRequestDatapage     = 0

            TargetPower  	= 100           # For SimulateTrainer
            CurrentPower	= 100
            while RunningSwitch == True:
                StartTime = time.time()
                #---------------------------------------------------------------
                # Simulate HRM or Trainer (master device, broadcasting data)
                #---------------------------------------------------------------
                messages     = []

                if clv.SimulateTrainer:
                    if True:
                        SpeedKmh, WheelSpeed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, CurrentResistance, Buttons, Axis = \
                            SimulateReceiveFromTrainer (TargetPower, CurrentPower)
                    else:
                        Cadence, CurrentPower, SpeedKmh, HeartRate = 98, 234, 35.6, 123
                    messages.append(hrm.BroadcastHeartrateMessage (devAntDongle, HeartRate))
                    messages.append(fe.BroadcastTrainerDataMessage(devAntDongle, Cadence, CurrentPower, SpeedKmh, HeartRate))

                #---------------------------------------------------------------
                # Receive data
                #---------------------------------------------------------------
                if clv.SimulateTrainer and len(messages) > 0:
                    data = ant.SendToDongle(messages, devAntDongle, '', True, False)
                else:
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
                        # HRM_s = Heart rate Monitor Display
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
                                        logfile.Write ("HRM page=%s ManufacturerID=%s SerialNumber=%s" % \
                                                    (DataPageNumber, HRM_ManufacturerID, HRM_SerialNumber))

                                if DataPageNumber & 0x7f == 3:
                                    if HRM_page3_done == False:
                                        HRM_page3_done = True
                                        HRM_HWrevision = Spec1
                                        HRM_SWversion  = Spec2
                                        HRM_Model      = Spec3
                                        logfile.Write ("HRM page=%s HWrevision=%s, SWversion=%s Model=%s" % \
                                                (DataPageNumber, HRM_HWrevision, HRM_SWversion, HRM_Model))
                                    

                            #---------------------------------------------------
                            # Data page 89   ??????????????????????????????
                            #---------------------------------------------------
                            elif DataPageNumber == 89:    
                                Unknown = True

                        #-------------------------------------------------------
                        # FE_s = Cycle Training Program
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
                            if DataPageNumber == 25:    
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
                                    logfile.Write ("FE Page=%s HWrevision=%s ManufacturerID=%s Model=%s" % \
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
                                    logfile.Write ("FE Page=%s SWrevision=%s.%s Serial#=%s" % \
                                                   (DataPageNumber, FE_SWrevisionMain, FE_SWrevisionSupp, FE_SerialNumber))

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
                                    ant.SendToDongle(data, devAntDongle, comment, False)
                                
                            #-------------------------------------------------------
                            # Other data pages
                            #-------------------------------------------------------
                            else: error = "Unknown FE data page"
                    if Unknown:
                        logfile.Write ("IGNORED!! msg=%s ch=%s p=%s info=%s" % \
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
                        logfile.Write ( ("Cadence=%3s Power=%3s Speed=%4.1f hr=%3s " + \
                                    "B=%s P=%s T=%s U=%s R=%s") % \
                                    (Cadence, CurrentPower, SpeedKmh, HeartRate, \
                                     dpBasicResistance, dpTargetPower, dpTrackResistance, dpUserConfiguration, dpRequestDatapage))

                    else:
                        logfile.Write ("HRM#=%2s hr=%3s FE-C#=%2s Speed=%4s Cadence=%3s Power=%3s hr=%3s" % \
                                    (HRM_s_count, HRM_HeartRate, FE_s_count, FE_Speed, FE_Cadence, FE_Power, FE_HeartRate))
                    
        except KeyboardInterrupt:
            logfile.Write ("Listening stopped")
        #---------------------------------------------------------------
        # Free channel
        #---------------------------------------------------------------
        messages = []
        if clv.hrm > 0: messages.append ( ant.msg41_UnassignChannel(ant.channel_HRM_s) )
        if clv.fe  > 0: messages.append ( ant.msg41_UnassignChannel(ant.channel_FE_s ) )
        ant.SendToDongle(messages, devAntDongle)
        #---------------------------------------------------------------
        # Release dongle
        #---------------------------------------------------------------
        ant.ResetDongle (devAntDongle)
logfile.Write ("We're done")
logfile.Write ("--------------------")