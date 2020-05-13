#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
WindowTitle = "Fortius Antifier v3.0 beta"
__version__ = "2020-05-13"
# 2020-05-13    Used: msgUnpage50_WindResistance, msgUnpage51_TrackResistance
# 2020-05-12    Minor code improvements
# 2020-05-08    Usage of clsTacxTrainer
# 2020-05-07    Target*** variables global to survive Restart
# 2020-05-07    clsAntDongle encapsulates all functions
#               and implements dongle recovery
# 2020-04-28    Created from FortiusAnt.py
#               Now only contains the Tacx2Dongle() basics.
#               Startup, GUI and Multiprocessing are in FortiusAnt.py
# 2020-04-28    HeartRateT not defined when using i-Vortex
# 2020-04-24    Recheck & document of TargetMode/Power/Grade/Resistance
#               Some calculations relocated
# 2020-04-22    Page16_TacxVortexSetPower sent every 0.25 second
# 2020-04-22    Crash because frame used instead of self
# 2020-04-22    Page16_TacxVortexSetPower only sent when data changed
#               HeartRateT was not initialized
# 2020-04-20    txtAntHRM used, i-Vortex paired
# 2020-04-17    Added: Page54 FE_Capabilities
# 2020-04-16    Write() replaced by Console() where needed
# 2020-04-15    Calibration is aborted when iFlow 1932 returns positive values
#               Fortius returns one positive reading and then goes negative...
# 2020-04-10    PowerMode added (PowerMode prevails over ResistanceMode)
# 2020-04-09    The PowercurveFactor is displayed as Digital Gearbox in number of
#                   teeth. factor = 1 = 15 teeth.
#               Not a bitmap but (new experience in Python) drawing rectangles.
# 2020-04-07    Before Calibrating, "Start pedalling" is displayed
#               PowercurveFactor is limitted to 0.3 ... 3
#               Runoff gives error "Calibrate not defined", resolved
#                   Messaging improved, method is still as inherited from antifier
# 2020-03-29    ReceiveFromTrainer() returns Error as extra parameter
# 2020-03-29    PowercurveFactor implemented to increment/decrement resistance
#               Also displayed on console
# 2020-03-04    Console message is displayed when debug.Application is set
#                   (was debug.Any)
#               Conversion error in SpeedKmh when trainer USB returns an error
#                   ReceiveFromTrainer() returns "Not found" in that case
#                   Correction of earlier solution.
# 2020-03-03    Format error resolved
# 2020-03-02    iMagic supported, thanks to Julian Pfefferkorn
# 2020-02-27    FE data page 252 ignored
#               PrintWarnings added for documentation
# 2020-02-26    msgID_BurstData ignored
#               usbTrainer.CalibrateSupported() used to skip calibration on iMagic
# 2020-02-18    Calibrate can be stopped with Ctrl-C
# 2020-02-18    Module antHRM.py and antFE.py created
# 2020-02-12    HRM display data pages 89, 95 implemented...
# 2020-02-12    if SpeedKmh == "Not Found"; required not to crash...
#               something to be changed in usbTrainer some day...
# 2020-02-12    Different channel used for HRM and HRM_d
#               msgPage80_ManufacturerInfo() was never sent
# 2020-02-10    clv.scs added (example code, not tested)
# 2020-02-09    id / channel handling improved
#                   (channel was checked before checking id)
# 2020-02-09    clv.hrm implemented
# 2020-01-23    manualGrade added
#               in manual mode, dongle entirely ignored
#
# 2020-01-21    Calibration improved
#               - Will run 8 minutes to allow tyre to warmup
#               - Will end when calibration-value is stable
#
# 2020-01-07    Calibration implemented
#
# 2020-01-06    Calibration tested: calibrate=the initial resistance of the trainer
#                                   which is subtracted from the TargetResistance
#               Weight tested: it appears to be "flywheel weight", not user weight
#               Mode: trainer has Resistance mode, no Ergo/Slope mode!
#
# 2019-12-24    Target grade implemented
#               All received ANT+ messages handled
#               Zwift interface works
#
# 2019-12-20    Navigation buttons implemented
#               - During Runoff:    up/down=add/reduce power, back=stop
#               - Normal operation: back=stop
#               - Manual operation: up/down=add/reduce power, back=stop
#               - Menu mode:        up/down=previous/next button,
#                                   enter  =press button
#                                   back   =stop program
#
# 2019-12-19    Powertest done
#               FortiusAnt.py -g -a -p1 -d0 -m
#                   So using the GUI, clv.autostart, no debugging, manual control
#                   Powerfactor = 1, which is the standard
#
#               Method: bike on the Fortius, power meter on bicycle.
#               1.  Select gear so you can run 10km/hr at a reasonable cadence.
#                   Manually select power 50Watt (up/down button on headunit)
#                   Ride untill reading from FortiusAnt and PowerMeter is stable.
#                   Write down power from PowerMeter (46 in table).
#                -- Increase power on headunit 100, 150, 200, 250, 300 Watt.
#                   Repeat test.
#               2.  Select gears for 20, 30, 40, 50 km/hr.
#                    Repeat test.
#
#               Test Results (Target power in column header, result in table)
#                           50W     100W    150W    200W    250W    300W
#               10 km/hr    46      97      145     194     245     285
#               20 km/hr    50      100     145     197     245     290
#               30 km/hr    63      102     154     196     245     295
#               40 km/hr    105     120     160     210     260     305
#               50 km/hr    123     130     165     210     250     310
#
#               Conclusions:
#               a. 50Watt at 50km/hr gives odd readings but that's not too strange.
#               b. Overall measured power correponds with TargetPower.
#               c. Multiple measurements give different results within 5%.
#                       Tests are done intermittently and hence have different
#                       brake and tyre temperatures.
#               d. PowerFactor not needed as a calibration option.
#
#               Assumption
#               Attempts to improve the algorithm may be useless, since it
#               should not be more exact than the Tacx Fortius (was designed for)
#               After all, changing the algorythm remains empirical
#
# 2019-12-17    The program works and is tested:
#               - Windows 64, python 3
#               - Tacx Fortius
#               - Trainer Road in ERG mode
#
#               The trainer is transmitted as a tacx. If the heartrate is
#               detected on the trainer, the HRM is transmitted as a garmin.
#
#               Todo:
#               - why is HeartRate not sent to Trainer Road directly but is a
#                   separate HRM channel needed?
#                   (see function ComposeGeneralFeInfo)
#                   done - 2020-02-09: Because TrainerRoad and/or Zwift expect an
#                       independant ANT+ HRM
#               - read buttons from trainer and navigate through menu
#                   (see function IdleFunction)
#                   done - 2019-12-20
#
#               Tests (and extensions) to be done:
#               - test with Trainer Road, resistance mode; done 2019-12-19
#               - test with Zwift; done 2019-12-24
#               - calibration test; done 2020-01-07
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

from   datetime                     import datetime

import antDongle         as ant
import antHRM            as hrm
import antFE             as fe
import debug
from   FortiusAntGui                import mode_Power, mode_Grade
import logfile
import usbTrainer

PrintWarnings = False                # Print warnings even when logging = off
CycleTimeFast = 0.02
CycleTimeANT  = 0.25
# ------------------------------------------------------------------------------
# Initialize globals
# ------------------------------------------------------------------------------
def Initialize(pclv):
    global clv, AntDongle, TacxTrainer
    clv         = pclv
    AntDongle   = None
    TacxTrainer = None
    
# ==============================================================================
# Here we go, this is the real work what's all about!
# ==============================================================================

# ------------------------------------------------------------------------------
# I d l e F u n c t i o n
# ------------------------------------------------------------------------------
# input:        None
#
# Description:  In idle-mode, read trainer and show what button pressed
#               So, when the trainer is not yet detected, the trainer cannot
#                   read for the headunit.
#
# Output:       None
#
# Returns:      The actual status of the headunit buttons
# ------------------------------------------------------------------------------
def IdleFunction(self):
    global TacxTrainer
    rtn = 0
    if TacxTrainer and TacxTrainer.OK:
        TacxTrainer.Refresh()
        rtn = TacxTrainer.Buttons
    return rtn

# ------------------------------------------------------------------------------
# L o c a t e H W
# ------------------------------------------------------------------------------
# input:        TacxTrainer, AntDongle
#
# Description:  If DONGLE  not already opened, Get the dongle
#               If TRAINER not already opened, Get the trainer
#                   unless trainer is simulated then ignore!
#               Show appropriate messages
#
# Output:       TacxTrainer, AntDongle
#
# Returns:      True if TRAINER and DONGLE found
# ------------------------------------------------------------------------------
def LocateHW(self):
    global clv, AntDongle, TacxTrainer
    if debug.on(debug.Application): logfile.Write ("Scan for hardware")

    #---------------------------------------------------------------------------
    # Get ANT dongle
    #---------------------------------------------------------------------------
    if debug.on(debug.Application): logfile.Write ("Get Dongle")
    if AntDongle and AntDongle.OK:
        pass
    else:
        if clv.manual or clv.manualGrade:
            self.SetMessages(Dongle="Simulated Dongle (manual mode)")
        else:
            AntDongle = ant.clsAntDongle()
            self.SetMessages(Dongle=AntDongle.Message)

    #---------------------------------------------------------------------------
    # Get Trainer and find trainer model for Windows and Linux
    #---------------------------------------------------------------------------
    if debug.on(debug.Application): logfile.Write ("Get Tacx Trainer")
    if TacxTrainer and TacxTrainer.OK:
        pass
    else:
        TacxTrainer = usbTrainer.clsTacxTrainer.GetTrainer(clv, AntDongle)
        self.SetMessages(Tacx=TacxTrainer.Message)

    #---------------------------------------------------------------------------
    # Show where the heartrate comes from 
    #---------------------------------------------------------------------------
    if clv.hrm == None:
        self.SetMessages(HRM="Heartrate expected from Tacx Trainer")
    else:
        self.SetMessages(HRM="Heartrate expected from ANT+ HRM")

    #---------------------------------------------------------------------------
    # Done
    #---------------------------------------------------------------------------
    if debug.on(debug.Application): logfile.Write ("Scan for hardware - end")
    if (clv.manual or clv.manualGrade or AntDongle.OK) and TacxTrainer.OK:
        return True
    else:
        return False
    
# ------------------------------------------------------------------------------
# R u n o f f
# ------------------------------------------------------------------------------
# input:        devTrainer
#
# Description:  run trainer untill 40km/h reached then untill stopped.
#               Initially, target power is 100Watt, which may be influenced
#               with the up/down buttons on the headunit of the trainer.
#
# Output:       none
#
# Returns:      True
# ------------------------------------------------------------------------------
def Runoff(self):
    global clv, AntDongle, TacxTrainer
    if clv.SimulateTrainer or clv.Tacx_iVortex:
        logfile.Console('Runoff not implemented for Simulated trainer or Tacx i-Vortex')
        return False

    TacxTrainer.SetPower(100)
    rolldown        = False
    rolldown_time   = 0

    #---------------------------------------------------------------------------
    # Pedal stroke Analysis
    #---------------------------------------------------------------------------
    pdaInfo         = []        # Collection of (time, power)
    LastPedalEcho   = 0         # Flag that cadence sensor was seen

    LastPower       = 0         # statistics
    PowerCount      = 0
    PowerEqual      = 0

    #self.InstructionsVariable.set('''
    #CALIBRATION TIPS: 
    #1. Tyre pressure 100psi (unloaded and cold) aim for 7.2s rolloff
    #2. Warm up for 2 mins, then cycle 30kph-40kph for 30s 
    #3. SpeedKmh up to above 40kph then stop pedalling and freewheel
    #4. Rolldown timer will start automatically when you hit 40kph, so stop pedalling quickly!
    #''')
    if clv.PedalStrokeAnalysis:
        CycleTime = CycleTimeFast   # Quick poll to get more info
        if debug.on(debug.Any):
            logfile.Console("Runoff; Pedal Stroke Analysis active")
    else:
        CycleTime = CycleTimeANT    # 0.25 Seconds, inspired by 4Hz ANT+

    while self.RunningSwitch == True:
        StartTime     = time.time()
        #-----------------------------------------------------------------------
        # Get data from trainer
        #-----------------------------------------------------------------------
        TacxTrainer.Refresh()

        #-----------------------------------------------------------------------
        # Show what happens
        #-----------------------------------------------------------------------
        if TacxTrainer.Message == "Not Found":
            self.SetValues(0, 0, 0, 0, 0, 0, 0, 0, 0)
            self.SetMessages(Tacx="Check if trainer is powered on")
        else:
            self.SetValues( TacxTrainer.SpeedKmh,         TacxTrainer.Cadence, \
                            TacxTrainer.CurrentPower,     TacxTrainer.TargetMode, \
                            TacxTrainer.TargetPower,      TacxTrainer.TargetGrade, \
                            TacxTrainer.TargetResistance, TacxTrainer.HeartRate, \
                            0)
            if not rolldown or rolldown_time == 0:
                self.SetMessages(Tacx=TacxTrainer.Message + " - Cycle to above 40kph (then stop)")
            else:
                self.SetMessages(Tacx=TacxTrainer.Message + \
                                    " - Rolldown timer %s - STOP pedalling!" % \
                                    ( round((time.time() - rolldown_time),1) ) \
                                )
          
            #---------------------------------------------------------------------
            # SpeedKmh up to 40 km/h and then rolldown
            #---------------------------------------------------------------------
            if TacxTrainer.SpeedKmh > 40:      # SpeedKmh above 40, start rolldown
                rolldown = True
        
            if rolldown and TacxTrainer.SpeedKmh <=40 and rolldown_time == 0:
                # rolldown timer starts when dips below 40
                rolldown_time = time.time()
          
            if rolldown and TacxTrainer.SpeedKmh < 0.1 :    # wheel stopped
                self.RunningSwitch = False                  # break loop
                self.SetMessages(Tacx=TacxTrainer.Message + \
                                    " - Rolldown time = %s seconds (aim 7s)" % \
                                    round((time.time() - rolldown_time),1) \
                                )

        #-------------------------------------------------------------------------
        # #48 Frequency of data capture - sufficient for pedal stroke analysis?
        #
        # If we want to do pedal stroke analysis, we should measure every
        # pedal-cycle multiple times per rotation.
        # 
        # Number of measurements/sec = (cadence * 360/angle) / 60 = 6 * cadence / angle
        # ==> Cycle time (in seconds) = angle / (6 * cadence)
        # ==> Angle = Cycle time (in seconds) * 6 * cadence
        #
        # case 1. Cadence = 120 and Angle = 1 degree
        #       Cycle time (in seconds) = 1 / (6 * 120) = 1.3889 ms
        #
        # case 2. Cadence = 120 and Cycle time (in seconds) = 0.25
        #       angle = .25 * 6 * 120 = 180 degrees
        #
        # case 2. Cadence = 120 and Cycle time (in seconds) = 0.01
        #       angle = .01 * 6 * 120 = 1.80 degrees
        #-------------------------------------------------------------------------
        if clv.PedalStrokeAnalysis:
            if LastPedalEcho == 0   and TacxTrainer.PedalEcho == 1 \
                                    and len(pdaInfo) \
                                    and TacxTrainer.Cadence:
                # Pedal triggers cadence sensor
                self.PedalStrokeAnalysis(pdaInfo, TacxTrainer.Cadence)
                pdaInfo = []

            # Store data for analysis until next signal
            pdaInfo.append((time.time(), TacxTrainer.CurrentPower)) 
            LastPedalEcho = TacxTrainer.PedalEcho
            
            if TacxTrainer.CurrentPower > 50 and TacxTrainer.Cadence > 30:
                # Gather some statistics while really pedalling
                PowerCount += 1
                if TacxTrainer.CurrentPower == LastPower: PowerEqual += 1
                LastPower = TacxTrainer.CurrentPower

        #-----------------------------------------------------------------------
        # Respond to button press
        #-----------------------------------------------------------------------
        if   TacxTrainer.Buttons == usbTrainer.EnterButton:     pass
        elif TacxTrainer.Buttons == usbTrainer.DownButton:      TacxTrainer.AddPower (-50) # Subtract 50 Watts for calibration test
        elif TacxTrainer.Buttons == usbTrainer.UpButton:        TacxTrainer.AddPower ( 50) # Add 50 Watts for calibration test
        elif TacxTrainer.Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False # Stop calibration
        else:                                                   pass

        #-----------------------------------------------------------------------
        # WAIT untill CycleTime is done
        #-----------------------------------------------------------------------
        ElapsedTime = time.time() - StartTime
        SleepTime = CycleTime - ElapsedTime
        if SleepTime > 0:
            time.sleep(SleepTime)
            if debug.on(debug.Data2):
                logfile.Write ("Sleep(%4.2f) to fill %s seconds done." % (SleepTime, CycleTime) )
        else:
            if ElapsedTime > CycleTime * 2 and debug.on(debug.Any):
                logfile.Write ("Runoff; Processing time %5.3f is %5.3f longer than planned %5.3f (seconds)" % (ElapsedTime, SleepTime * -1, CycleTime) )
            pass
        
    #---------------------------------------------------------------------------
    # Finalize
    #---------------------------------------------------------------------------
    self.SetValues( 0, 0, 0,TacxTrainer.TargetMode, 0, 0, 0, 0, 0)
    if not rolldown:
        self.SetMessages(Tacx=TacxTrainer.Message)
    if debug.on(debug.Any) and PowerCount > 0:
        logfile.Console("Pedal Stroke Analysis: #samples = %s, #equal = %s (%3.0f%%)" % \
                    (PowerCount, PowerEqual, PowerEqual * 100 /PowerCount))
    return True
    
# ------------------------------------------------------------------------------
# T a c x 2 D o n g l e
# ------------------------------------------------------------------------------
# input:        AntDongle, TacxTrainer
#
# Description:  Exchange data between TRAINER and DONGLE.
#               TRAINER tells DONGLE  speed, power, cadence, heartrate
#               DONGLE  tells TRAINER target power (or grade not tested)
#
#               In manual mode, the target power from DONGLE is ignored and
#               power is set using the headunit, like in runoff()
#
#               Target and Actual data are shown on the interface
#
# Output:       none
#
# Returns:      True
# ------------------------------------------------------------------------------
def Tacx2Dongle(self):
    global clv, AntDongle, TacxTrainer
    Restart = False
    while True:
        rtn = Tacx2DongleSub(self, Restart)
        if not (clv.manual or clv.manualGrade) and AntDongle.DongleReconnected:
            self.SetMessages(Dongle=AntDongle.Message)
            AntDongle.ApplicationRestart()
            Restart = True
        else:
            break
    return rtn

def Tacx2DongleSub(self, Restart):
    global clv, AntDongle, TacxTrainer

    AntHRMpaired = False
    AntVTXpaired = False
    VTX_VortexID = 0

    #---------------------------------------------------------------------------
    # Info from ANT slave channels
    #---------------------------------------------------------------------------
    HeartRate       = 0         # This field is displayed
                                # We have two sources: the trainer or
                                # our own HRM slave channel.
    #Cadence        = 0         # Analogously for Speed Cadence Sensor
                                # But is not yet implemented
    #---------------------------------------------------------------------------
    # Pedal stroke Analysis
    #---------------------------------------------------------------------------
    pdaInfo       = []          # Collection of (time, power)
    LastPedalEcho = 0           # Flag that cadence sensor was seen

    #---------------------------------------------------------------------------
    # Initialize Dongle
    # Open channels:
    #    one to transmit the trainer info (Fitness Equipment)
    #    one to transmit heartrate info   (HRM monitor)
    #    one to interface with Tacx i-Vortex (VTX)
    #
    # And if you want a dedicated Speed Cadence Sensor, implement like this...
    #---------------------------------------------------------------------------
    if not (clv.manual or clv.manualGrade):
        AntDongle.ResetDongle()             # reset dongle
        AntDongle.Calibrate()               # calibrate ANT+ dongle
        AntDongle.Trainer_ChannelConfig()   # Create ANT+ master channel for FE-C
        
        if clv.hrm == None:
            AntDongle.HRM_ChannelConfig()   # Create ANT+ master channel for HRM
        elif clv.hrm < 0:
            pass                            # No Heartrate at all
        else:
            #-------------------------------------------------------------------
            # Create ANT+ slave channel for HRM;   0: auto pair, nnn: defined HRM
            #-------------------------------------------------------------------
            AntDongle.SlaveHRM_ChannelConfig(clv.hrm)

            #-------------------------------------------------------------------
            # Request what DeviceID is paired to the HRM-channel
            # No pairing-loop: HRM perhaps not yet active and avoid delay
            #-------------------------------------------------------------------
            msg = ant.msg4D_RequestMessage(ant.channel_HRM_s, ant.msgID_ChannelID)
            AntDongle.Write([msg], False, False)
    
        if clv.Tacx_iVortex:
            #-------------------------------------------------------------------
            # Create ANT+ slave channel for VTX
            #-------------------------------------------------------------------
            AntDongle.SlaveVTX_ChannelConfig(0)

            #-------------------------------------------------------------------
            # Request what DeviceID is paired to the VTX-channel
            # No pairing-loop: VTX perhaps not yet active and avoid delay
            #-------------------------------------------------------------------
            msg = ant.msg4D_RequestMessage(ant.channel_VTX_s, ant.msgID_ChannelID)
            AntDongle.Write([msg], False, False)

        if clv.scs != None:
            AntDongle.SlaveSCS_ChannelConfig(clv.scs)   # Create ANT+ slave channel for SCS
                                                        # 0: auto pair, nnn: defined SCS
            pass
    
    if not clv.gui: logfile.Console ("Ctrl-C to exit")

    #---------------------------------------------------------------------------
    # Loop control
    #---------------------------------------------------------------------------
    # self.RunningSwitch = True             # Is set by caller!
    EventCounter       = 0

    #---------------------------------------------------------------------------
    # Calibrate trainer
    #---------------------------------------------------------------------------
    CountDown       = 120 * 4 # 8 minutes; 120 is the max on the cadence meter
    ResistanceArray = numpy.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) # Array for running everage
    Calibrate       = 0
    StartPedalling  = True
    Counter         = 0

    if TacxTrainer.CalibrateSupported():
        self.SetMessages(Tacx="* * * * S T A R T   P E D A L L I N G * * * *")
        if debug.on(debug.Function):
            logfile.Write('Tacx2Dongle; start pedalling for calibration')
    # try:
    if True:
        while         self.RunningSwitch \
              and     clv.calibrate \
              and not TacxTrainer.Buttons == usbTrainer.CancelButton \
              and     Calibrate == 0 \
              and     TacxTrainer.CalibrateSupported():
            StartTime = time.time()
            #-------------------------------------------------------------------
            # Receive / Send trainer
            #-------------------------------------------------------------------
            TacxTrainer.Refresh(usbTrainer.modeCalibrate)

            #-------------------------------------------------------------------
            # When calibration IS supported, the following condition will NOT occur.
            # iFlow 1932 is expected to support calibration but does not.
            # This check is to stop calibration-loop because it will never end.
            #
            # First reading on 'my' Fortius shows a positive number, then goes negative
            # so ignore the first x readings before deciding it will not work.
            #-------------------------------------------------------------------
            # print(StartPedalling, SpeedKmh, CurrentResistance)
            if TacxTrainer.CurrentResistance > 0:
                Counter += 1
                if Counter == 10:
                    logfile.Console('Calibration stopped because of unexpected resistance value')
                    break

            if TacxTrainer.CurrentResistance < 0 and TacxTrainer.SpeedKmh > 0:
                # Calibration is started (with pedal kick)
                #---------------------------------------------------------------
                # Show progress (when calibrating is started)
                # This changes the message from "Start Pedalling" to "Calibrating"
                # The message must be given once for the console-mode (no GUI)
                #---------------------------------------------------------------
                if StartPedalling:
                    self.SetMessages(Tacx="* * * * C A L I B R A T I N G * * * *")
                    if debug.on(debug.Function):
                        logfile.Write('Tacx2Dongle; start calibration')
                    StartPedalling = False

                self.SetValues(TacxTrainer.SpeedKmh, int(CountDown/4), \
                        round(TacxTrainer.CurrentPower * -1,0), \
                        mode_Power, 0, 0, TacxTrainer.CurrentResistance * -1, 0, 0)

                # --------------------------------------------------------------
                # Average power over the last 20 readings
                # Stop if difference between min/max is below threshold (30)
                # At least 30 seconds but not longer than the countdown time (8 minutes)
                # Note that the limits are empiracally established.
                # --------------------------------------------------------------
                ResistanceArray = numpy.append(ResistanceArray, TacxTrainer.CurrentResistance * -1) # Add new value to array
                ResistanceArray = numpy.delete(ResistanceArray, 0)                      # Remove oldest from array
                
                if CountDown < (120 * 4 - 30) and numpy.min(ResistanceArray) > 0:
                    if (numpy.max(ResistanceArray) - numpy.min(ResistanceArray) ) < 30 or CountDown <= 0:
                        Calibrate = TacxTrainer.CurrentResistance * -1
                        if debug.on(debug.Function):
                            logfile.Write('Tacx2Dongle; calibration ended %s' % Calibrate)

                CountDown -= 0.25                   # If not started, no count down!
                
            #-------------------------------------------------------------------
            # WAIT        So we do not cycle faster than 4 x per second
            #-------------------------------------------------------------------
            SleepTime = 0.25 - (time.time() - StartTime)
            if SleepTime > 0: time.sleep(SleepTime)
    # except KeyboardInterrupt:
    #     logfile.Console ("Stopped")
    # except Exception as e:
    #     logfile.Console ("Calibration stopped with exception: %s" % e)
    #---------------------------------------------------------------------------
    # Stop trainer
    #---------------------------------------------------------------------------
    if TacxTrainer.OK:
        if debug.on(debug.Function): logfile.Write('Tacx2Dongle; stop trainer')
        TacxTrainer.SendToTrainer(usbTrainer.modeStop)
    self.SetMessages(Tacx=TacxTrainer.Message)

    #---------------------------------------------------------------------------
    # Initialize variables
    #---------------------------------------------------------------------------
    if not Restart:
        if clv.manualGrade:
            TacxTrainer.SetGrade(0)
        else:
            TacxTrainer.SetPower(100)
        TacxTrainer.ResetPowercurveFactor()

    TargetPowerTime         = 0             # Time that last TargetPower received
    PowerModeActive         = ''            # Text showing in userinterface
    
    LastANTtime             = 0             # ANT+ interface is sent/received only
                                            # every 250ms
    
    #---------------------------------------------------------------------------
    # Initialize antHRM and antFE module
    #---------------------------------------------------------------------------
    if debug.on(debug.Function): logfile.Write('Tacx2Dongle; initialize ANT')
    hrm.Initialize()
    fe.Initialize()
    
    #---------------------------------------------------------------------------
    # Initialize CycleTime: fast for PedalStrokeAnalysis
    #---------------------------------------------------------------------------
    if clv.PedalStrokeAnalysis:
        CycleTime = CycleTimeFast   # Quick poll to get more info
        if debug.on(debug.Any): logfile.Console("Tacx2Dongle; Pedal Stroke Analysis active")
    else:
        CycleTime = CycleTimeANT    # Seconds, default = 0.25 (inspired by 4Hz ANT+)

    #---------------------------------------------------------------------------
    # Our main loop!
    # The loop has the following phases
    # -- Get data from trainer
    # -- Local adjustments (heartrate monitor, cadence sensor)
    # -- Display actual values
    # -- Pedal stroke analysis
    # -- Modify data, due to Buttons or ANT
    #---------------------------------------------------------------------------
    if debug.on(debug.Function): logfile.Write('Tacx2Dongle; start main loop')
    try:
        while self.RunningSwitch == True and \
            ((clv.manual or clv.manualGrade) or not AntDongle.DongleReconnected):
            StartTime = time.time()
            #-------------------------------------------------------------------
            # ANT process is done once every 250ms
            #-------------------------------------------------------------------
            if (time.time() - LastANTtime) > 0.25:
                LastANTtime = time.time()
                QuarterSecond = True
            else:
                QuarterSecond = False 

            #-------------------------------------------------------------------
            # Get data from trainer
            # TRAINER- SHOULD WRITE THEN READ 70MS LATER REALLY
            #-------------------------------------------------------------------
            TacxTrainer.Refresh()               # = Receive + Calc + Send
            if clv.gui: self.SetMessages(Tacx=TacxTrainer.Message + PowerModeActive)

            #-------------------------------------------------------------------
            # If NO Speed Cadence Sensor defined, use Trainer-info
            # Hook for future development
            #-------------------------------------------------------------------
            # if clv.scs == None:
            #     SpeedKmh   = SpeedKmhT  
            #     Cadence    = CadenceT

            #-------------------------------------------------------------------
            # If NO HRM defined, use the HeartRate from the trainer
            #-------------------------------------------------------------------
            if clv.hrm == None:
                HeartRate = TacxTrainer.HeartRate
                # print('Use heartrate from trainer', HeartRate)
            
            #-------------------------------------------------------------------
            # Show actual status
            #-------------------------------------------------------------------
            self.SetValues(TacxTrainer.VirtualSpeedKmh, 
                            TacxTrainer.Cadence, \
                            TacxTrainer.CurrentPower, \
                            TacxTrainer.TargetMode, \
                            TacxTrainer.TargetPower, \
                            TacxTrainer.TargetGrade, \
                            TacxTrainer.TargetResistance, \
                            HeartRate, \
                            TacxTrainer.Teeth)

            #-------------------------------------------------------------------
            # Pedal Stroke Analysis
            #-------------------------------------------------------------------
            if clv.PedalStrokeAnalysis:
                if LastPedalEcho == 0 and TacxTrainer.PedalEcho == 1 and \
                    len(pdaInfo) and TacxTrainer.Cadence:
                    # Pedal triggers cadence sensor
                    self.PedalStrokeAnalysis(pdaInfo, TacxTrainer.Cadence)
                    pdaInfo = []
                pdaInfo.append((time.time(), TacxTrainer.CurrentPower)) # Store data for analysis
                LastPedalEcho = TacxTrainer.PedalEcho                   # until next signal

            #-------------------------------------------------------------------
            # In manual-mode, power can be incremented or decremented
            # In all modes, operation can be stopped.
            #
            # TargetMode  is set here (manual mode) or received from ANT+ (Zwift)
            # TargetPower and TargetGrade are set in this section only!
            #-------------------------------------------------------------------
            if clv.manual:
                if   TacxTrainer.Buttons == usbTrainer.EnterButton:     pass
                elif TacxTrainer.Buttons == usbTrainer.DownButton:      TacxTrainer.AddPower(-50)
                elif TacxTrainer.Buttons == usbTrainer.UpButton:        TacxTrainer.AddPower( 50)
                elif TacxTrainer.Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                       pass
            elif clv.manualGrade:
                if   TacxTrainer.Buttons == usbTrainer.EnterButton:     pass
                elif TacxTrainer.Buttons == usbTrainer.DownButton:      TacxTrainer.AddGrade(-1)
                elif TacxTrainer.Buttons == usbTrainer.UpButton:        TacxTrainer.AddGrade( 1)
                elif TacxTrainer.Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                       pass
            else:
                if   TacxTrainer.Buttons == usbTrainer.EnterButton:     pass
                elif TacxTrainer.Buttons == usbTrainer.DownButton:      TacxTrainer.SetPowercurveFactorDown()
                elif TacxTrainer.Buttons == usbTrainer.UpButton:        TacxTrainer.SetPowercurveFactorUp()
                elif TacxTrainer.Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                       pass

            #-------------------------------------------------------------------
            # Do ANT work every 1/4 second
            #-------------------------------------------------------------------
            messages = []       # messages to be sent to ANT
            data = []           # responses received from ANT
            if QuarterSecond:
                LastANTtime = time.time()
                #---------------------------------------------------------------
                # Send power to iVortex
                # Yes, we could have put this into the clsTacxTrainer
                #      now all the ANT traffic is here.
                #---------------------------------------------------------------
                if clv.Tacx_iVortex and VTX_VortexID:
                    info = ant.msgPage16_TacxVortexSetPower (ant.channel_VTX_s, VTX_VortexID, TacxTrainer.TargetPower)
                    messages.append ( ant.ComposeMessage (ant.msgID_BroadcastData, info) )

                #---------------------------------------------------------------
                # Broadcast Heartrate message
                #---------------------------------------------------------------
                if clv.hrm == None and TacxTrainer.HeartRate > 0 and not (clv.manual or clv.manualGrade):
                    messages.append(hrm.BroadcastHeartrateMessage(HeartRate))

                #---------------------------------------------------------------
                # Broadcast TrainerData message to the CTP (Trainer Road, ...)
                #---------------------------------------------------------------
                if not (clv.manual or clv.manualGrade):
                    # print('fe.BroadcastTrainerDataMessage', Cadence, CurrentPower, SpeedKmh, HeartRate)
                    messages.append(fe.BroadcastTrainerDataMessage (TacxTrainer.Cadence, \
                        TacxTrainer.CurrentPower, TacxTrainer.SpeedKmh, TacxTrainer.HeartRate))
                    
                #---------------------------------------------------------------
                # Broadcast and receive ANT+ responses
                #---------------------------------------------------------------
                # Note that, if there are no messages to be sent, we do not 
                #       receive anything either.... This sounds weard but:
                # It occurs if we are in manual mode and NOT using Vortex...
                #---------------------------------------------------------------
                if len(messages) > 0:
                    data = AntDongle.Write(messages, True, False)

            #-------------------------------------------------------------------
            # Here all response from the ANT dongle are processed (receive=True)
            #
            # Commands from dongle that are expected are:
            # - TargetGradeFromDongle or TargetPowerFromDongle
            # - Information from HRM (if paired)
            # - Information from i-Vortex (if paired)
            #-------------------------------------------------------------------
            for d in data:
                synch, length, id, info, checksum, _rest, Channel, DataPageNumber = ant.DecomposeMessage(d)
                error = False

                if id == ant.msgID_AcknowledgedData:
                    #-----------------------------------------------------------
                    # Fitness Equipment Channel inputs
                    #-----------------------------------------------------------
                    if Channel == ant.channel_FE:
                        #-------------------------------------------------------
                        # Data page 48 (0x30) Basic resistance
                        #-------------------------------------------------------
                        if   DataPageNumber == 48:
                            logfile.Write('Data page 48 Basic mode not implemented')
                            # I never saw this appear anywhere (2020-05-08)
                            # TargetMode            = mode_Basic
                            # TargetGradeFromDongle = 0
                            # TargetPowerFromDongle = ant.msgUnpage48_BasicResistance(info) * 1000  # n % of maximum of 1000Watt
                            
                        #-------------------------------------------------------
                        # Data page 49 (0x31) Target Power
                        #-------------------------------------------------------
                        elif   DataPageNumber == 49:
                            TacxTrainer.SetPower(ant.msgUnpage49_TargetPower(info))
                            TargetPowerTime = time.time()
                            if False and clv.PowerMode and debug.on(debug.Application):
                                logfile.Write('PowerMode: TargetPower info received - timestamp set')

                        #-------------------------------------------------------
                        # Data page 50 (0x32) Wind Resistance
                        #-------------------------------------------------------
                        elif   DataPageNumber == 50:
                            TacxTrainer.SetWind(\
                                        ant.msgUnpage50_WindResistance(info) )

                        #-------------------------------------------------------
                        # Data page 51 (0x33) Track resistance
                        #-------------------------------------------------------
                        elif DataPageNumber == 51:
                            if clv.PowerMode and (time.time() - TargetPowerTime) < 30:
                                #-----------------------------------------------
                                # In PowerMode, TrackResistance is ignored
                                #       (for xx seconds after the last power-command)
                                # So if TrainerRoad is used simultaneously with
                                #       Zwift/Rouvythe power commands from TR 
                                #       take precedence over Zwift/Rouvy and a 
                                #       power-training can be done while riding
                                #       a Zwift/Rouvy simulation/video!
                                # When TrainerRoad is finished, the Track
                                #       resistance is active again
                                #-----------------------------------------------
                                PowerModeActive = ' [P]'
                                if False and clv.PowerMode and debug.on(debug.Application):
                                    logfile.Write('PowerMode: Grade info ignored')
                                pass
                            else:
                                Grade, RollingResistance = ant.msgUnpage51_TrackResistance(info)
                                TacxTrainer.SetGrade(Grade)
                                TacxTrainer.SetRollingResistance(RollingResistance)
                                PowerModeActive       = ''
                            
                        #-------------------------------------------------------
                        # Data page 55 User configuration
                        #-------------------------------------------------------
                        elif DataPageNumber == 55:
                            UserWeight, BicycleWeight, BicycleWheelDiameter, GearRatio = \
                                ant.msgUnpage55_UserConfiguration(info)
                            TacxTrainer.SetUserConfiguration(UserWeight, \
                                BicycleWeight, BicycleWheelDiameter, GearRatio)

                        #-------------------------------------------------------
                        # Data page 70 Request data page
                        #-------------------------------------------------------
                        elif DataPageNumber == 70:
                            _SlaveSerialNumber, _DescriptorByte1, _DescriptorByte2, \
                                _AckRequired, NrTimes, RequestedPageNumber, \
                                _CommandType = ant.msgUnpage70_RequestDataPage(info)
                            
                            info = False
                            if   RequestedPageNumber == 54:
                                # Capabilities;
                                # bit 0 = Basic mode
                                # bit 1 = Target/Power/Ergo mode
                                # bit 2 = Simulation/Restance/Slope mode
                                info = ant.msgPage54_FE_Capabilities(ant.channel_FE, 0xff, 0xff, 0xff, 0xff, 1000, 0x07)

                            elif RequestedPageNumber == 80:
                                info = ant.msgPage80_ManufacturerInfo(ant.channel_FE, 0xff, 0xff, \
                                    ant.HWrevision_FE, ant.Manufacturer_tacx, ant.ModelNumber_FE)

                            elif RequestedPageNumber == 81:
                                info = ant.msgPage81_ProductInformation(ant.channel_FE, 0xff, \
                                    ant.SWrevisionSupp_FE, ant.SWrevisionMain_FE, ant.SerialNumber_FE)

                            elif RequestedPageNumber == 82:
                                info = ant.msgPage82_BatteryStatus(ant.channel_FE)

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
                        # Data page 252 ????
                        #-------------------------------------------------------
                        elif DataPageNumber == 252 and (PrintWarnings or debug.on(debug.Data1)):
                            logfile.Write('FE data page 252 ignored. info=%s' % logfile.HexSpace(info))
                            pass
                            
                        #-------------------------------------------------------
                        # Other data pages
                        #-------------------------------------------------------
                        else: error = "Unknown FE data page"

                    #-----------------------------------------------------------
                    # Unknown channel
                    #-----------------------------------------------------------
                    else: error="Unknown channel"

                elif id == ant.msgID_BroadcastData:
                    #-----------------------------------------------------------
                    # Heart Rate Monitor inputs
                    #-----------------------------------------------------------
                    if Channel == ant.channel_HRM_s:
                        #-------------------------------------------------------
                        # Ask what device is paired
                        #-------------------------------------------------------
                        if not AntHRMpaired:
                            msg = ant.msg4D_RequestMessage(ant.channel_HRM_s, ant.msgID_ChannelID)
                            AntDongle.Write([msg], False, False)

                        #-------------------------------------------------------
                        # Data page 0...4 HRM data
                        # Only expected when -H flag specified
                        #-------------------------------------------------------
                        if DataPageNumber & 0x7f in (0,1,2,3,4,5,6,7,89,95):
                            if clv.hrm >= 0:
                                _Channel, _DataPageNumber, _Spec1, _Spec2, _Spec3, \
                                    _HeartBeatEventTime, _HeartBeatCount, HeartRate = \
                                    ant.msgUnpage_Hrm(info)
                                # print('Set heartrate from HRM', HeartRate)

                            else:
                                pass                            # Ignore it
                                
                        #-------------------------------------------------------
                        # Data page 89 (HRM strap Garmin#3), 95(HRM strap Garmin#4)
                        # Added to previous set, provides HR info
                        #-------------------------------------------------------
                        elif DataPageNumber in (89, 95):
                            pass                                # Ignore it

                        #-------------------------------------------------------
                        # Other data pages
                        #-------------------------------------------------------
                        else: error = "Unknown HRM data page"

                    #-----------------------------------------------------------
                    # VTX_s = Tacx i-Vortex trainer
                    #-----------------------------------------------------------
                    elif Channel == ant.channel_VTX_s:
                        # logfile.Console ('i-Vortex Page=%s %s' % (DataPageNumber, info))
                        #-------------------------------------------------------
                        # Ask what device is paired
                        #-------------------------------------------------------
                        if not AntVTXpaired:
                            msg = ant.msg4D_RequestMessage(ant.channel_VTX_s, ant.msgID_ChannelID)
                            AntDongle.Write([msg], False, False)

                        #-------------------------------------------------------
                        # Data page 00 msgUnpage00_TacxVortexDataSpeed
                        #-------------------------------------------------------
                        if DataPageNumber == 0:
                            VTX_UsingVirtualSpeed, CurrentPower, VTX_Speed, VTX_CalibrationState, Cadence = \
                                ant.msgUnpage00_TacxVortexDataSpeed(info)
                            SpeedKmh = round( VTX_Speed / ( 100 * 1000 / 3600 ), 1)
                            TacxTrainer.SetAntVortexValues(Cadence, CurrentPower, SpeedKmh)
                            if debug.on(debug.Function):
                                logfile.Write ('i-Vortex Page=%s UsingVirtualSpeed=%s Power=%s Speed=%s State=%s Cadence=%s' % \
                                    (DataPageNumber, VTX_UsingVirtualSpeed, CurrentPower, SpeedKmh, VTX_CalibrationState, Cadence) )

                        #-------------------------------------------------------
                        # Data page 01 msgUnpage01_TacxVortexDataSerial
                        #-------------------------------------------------------
                        elif DataPageNumber == 1:
                            VTX_S1, VTX_S2, VTX_Serial, VTX_Alarm = ant.msgUnpage01_TacxVortexDataSerial(info)
                            if debug.on(debug.Function):
                                logfile.Write ('i-Vortex Page=%s S1=%s S2=%s Serial=%s Alarm=%s' % \
                                    (DataPageNumber, VTX_S1, VTX_S2, VTX_Serial, VTX_Alarm) )

                        #-------------------------------------------------------
                        # Data page 02 msgUnpage02_TacxVortexDataVersion
                        #-------------------------------------------------------
                        elif DataPageNumber == 2:
                            VTX_Major, VTX_Minor, VTX_Build = ant.msgUnpage02_TacxVortexDataVersion(info)
                            if debug.on(debug.Function):
                                logfile.Write ('i-Vortex Page=%s Major=%s Minor=%s Build=%s' % \
                                    (DataPageNumber, VTX_Major, VTX_Minor, VTX_Build))

                        #-------------------------------------------------------
                        # Data page 03 msgUnpage03_TacxVortexDataCalibration
                        #-------------------------------------------------------
                        elif DataPageNumber == 3:
                            VTX_Calibration, VTX_VortexID = ant.msgUnpage03_TacxVortexDataCalibration(info)
                            if debug.on(debug.Function):
                                logfile.Write ('i-Vortex Page=%s Calibration=%s VortexID=%s' % \
                                    (DataPageNumber, VTX_Calibration, VTX_VortexID))

                        #-------------------------------------------------------
                        # Other data pages
                        #-------------------------------------------------------
                        else: error = "Unknown VTX data page"

                    #-----------------------------------------------------------
                    # Speed Cadence Sensor inputs
                    #-----------------------------------------------------------
                    elif Channel == ant.channel_SCS:
                        #-------------------------------------------------------
                        # Data page 0 CSC data
                        # Only expected when -S flag specified
                        #-------------------------------------------------------
                        if False:
                            pass
#scs                    elif clv.scs >= 0 and DataPageNumber & 0x7f == 0:
#scs                        Channel, DataPageNumber, BikeCadenceEventTime, \
#scs                            CumulativeCadenceRevolutionCount, BikeSpeedEventTime, \
#scs                            CumulativeSpeedRevolutionCount = \
#scs                            ant.msgUnpage0_CombinedSpeedCadence(info) 
#scs                        SpeedKmh   = ...
#scs                        Cadence    = ...

                        #-------------------------------------------------------
                        # Other data pages
                        #-------------------------------------------------------
                        else: error = "Unknown SCS data page"

                    #-----------------------------------------------------------
                    # Unknown channel
                    #-----------------------------------------------------------
                    else: error = "Unknown channel"

                #---------------------------------------------------------------
                # ChannelID - the info from a Master device on the network
                #---------------------------------------------------------------
                elif id == ant.msgID_ChannelID:
                    Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                        ant.unmsg51_ChannelID(info)

                    if DeviceNumber == 0:   # No device paired, ignore
                        pass

                    elif Channel == ant.channel_HRM_s and DeviceTypeID == ant.DeviceTypeID_HRM:
                        AntHRMpaired = True
                        self.SetMessages(HRM='Heart Rate Monitor paired: %s' % DeviceNumber)

                    elif Channel == ant.channel_VTX_s and DeviceTypeID == ant.DeviceTypeID_VTX:
                        AntVTXpaired = True
                        TacxTrainer.Message = 'Tacx i-Vortex paired: %s' % DeviceNumber
                        self.SetMessages(Tacx=TacxTrainer.Message)

                    else:
                        logfile.Console('Unexpected device %s on channel %s' % (DeviceNumber, Channel))
                        

                #---------------------------------------------------------------
                # Message ChannelResponse, acknowledges a message
                #---------------------------------------------------------------
                elif id == ant.msgID_ChannelResponse:
                    Channel, _InitiatingMessageID, _ResponseCode = ant.unmsg64_ChannelResponse(info)
                    pass
                    
                #---------------------------------------------------------------
                # Message BurstData, ignored
                #---------------------------------------------------------------
                elif id == ant.msgID_BurstData:
                    pass

                else: error = "Unknown message ID"

                #---------------------------------------------------------------
                # Unsupported channel, message or page can be silently ignored
                # Show WHAT we ignore, not to be blind for surprises!
                #---------------------------------------------------------------
                if error and (PrintWarnings or debug.on(debug.Data1)): logfile.Write(\
                    "ANT Dongle:%s: synch=%s, len=%2s, id=%s, check=%s, channel=%s, page=%s(%s) info=%s" % \
                    (error, synch, length, hex(id), checksum, Channel, DataPageNumber, hex(DataPageNumber), logfile.HexSpace(info)))

            #-------------------------------------------------------------------
            # WAIT untill CycleTime is done
            #-------------------------------------------------------------------
            ElapsedTime = time.time() - StartTime
            SleepTime = CycleTime - ElapsedTime
            if SleepTime > 0:
                time.sleep(SleepTime)
                if debug.on(debug.Data2): logfile.Write ("Sleep(%4.2f) to fill %s seconds done." % (SleepTime, CycleTime) )
            else:
                if ElapsedTime > CycleTime * 2 and debug.on(debug.Any):
                    logfile.Console ("Tacx2Dongle; Processing time %5.3f is %5.3f longer than planned %5.3f (seconds)" % (ElapsedTime, SleepTime * -1, CycleTime) )
                pass

            EventCounter += 1           # Increment and ...
            EventCounter &= 0xff        # maximize to 255
            
    except KeyboardInterrupt:
        logfile.Console ("Stopped")
        
    #---------------------------------------------------------------------------
    # Stop devices
    #---------------------------------------------------------------------------
    if not (clv.manual or clv.manualGrade):
        AntDongle.ResetDongle()
    if TacxTrainer and TacxTrainer.OK:
        TacxTrainer.SendToTrainer(usbTrainer.modeStop)

    return True