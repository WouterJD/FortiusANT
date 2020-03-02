#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-02-26"
WindowTitle = "Fortius Antifier v2.2"
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

from datetime import datetime

import antDongle         as ant
import antHRM            as hrm
import antFE             as fe
import debug
import FortiusAntCommand as cmd
import FortiusAntGui     as gui
import logfile
import structConstants   as sc
import usbTrainer

PrintWarnings = True                # Print warnings even when logging = off

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
class staticVariables:
    LastTime = 0
    
# ==============================================================================
# Subclass FortiusAnt GUI with our functions
# ==============================================================================
class frmFortiusAnt(gui.frmFortiusAntGui):
    def callIdleFunction(self):
        return IdleFunction(self)
    
    def callLocateHW(self):
        return LocateHW(self)
    
    def callRunoff(self):
        return Runoff(self)
        
    def callTacx2Dongle(self):
        return Tacx2Dongle(self)

class frmFortiusAntNoGui:
    pass
        
# ------------------------------------------------------------------------------
# Informatory messages on GUI or console
# Note that in non-GUI mode, "self" is not a frame; therefore not part of class!
# ------------------------------------------------------------------------------
def SetTacxMsg(self, msg):
    if clv.gui: self.SetMessages(Tacx  = msg)
    else: logfile.Write ("Tacx   - " + msg)

def SetDongleMsg(self, msg):
    if clv.gui: self.SetMessages(Dongle=msg)
    else: logfile.Write ("Dongle - " + msg)

def SetFactorMsg(self, msg):
    if clv.gui: self.SetMessages(Factor=msg)
#   else: logfile.Write ("Factor - " + str(msg))        # Already at start

def SetValues(self, fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, iTacx, iHeartRate):
    # --------------------------------------------------------------------------
    # Calculate delta time since previous call
    # --------------------------------------------------------------------------
    delta = time.time() - staticVariables.LastTime   # Delta time since previous
    
    # --------------------------------------------------------------------------
    # Update current readings
    # --------------------------------------------------------------------------
    if clv.gui:
        self.SetValues(fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, iTacx, iHeartRate)

    if delta >= 1 and (not clv.gui or debug.on(debug.Any)):
        staticVariables.LastTime = time.time()           # Time in seconds
        
        if   iTargetMode == gui.mode_Power:
            sTarget = "%3.0fW" % iTargetPower
        elif iTargetMode == gui.mode_Grade:
            sTarget = "%3.1f%%" % fTargetGrade
            if iTargetPower > 0:                         # 2020-01-22 
                sTarget += "(%iW)" % iTargetPower        # Target power added for reference
        else:
            sTarget = "None"
        msg = "Target=%s Speed=%4.1fkmh hr=%3.0f Current=%3.0fW Cad=%3.0f r=%4.0f %3.0f%%" % \
            (sTarget, fSpeed, iHeartRate, iPower, iRevs, iTacx, int(clv.PowerFactor * 100) )
        logfile.Write (msg)

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
# ------------------------------------------------------------------------------
def IdleFunction(self):
    global devTrainer, devAntDongle
    if devTrainer != False:
        TargetPower = 100
        SpeedKmh, WheelSpeed, PedalEcho, HeartRate, CurrentPower, Cadence, TargetResistance, CurrentResistance, Buttons, Axis = \
            usbTrainer.ReceiveFromTrainer(devTrainer)
        usbTrainer.SendToTrainer(devTrainer, usbTrainer.modeResistance, \
            gui.mode_Power, TargetPower, False, -1, PedalEcho, WheelSpeed, Cadence, 0, False)

        if   Buttons == usbTrainer.EnterButton: self.Navigate_Enter()
        elif Buttons == usbTrainer.DownButton:  self.Navigate_Down()
        elif Buttons == usbTrainer.UpButton:    self.Navigate_Up()
        elif Buttons == usbTrainer.CancelButton:self.Navigate_Back()
        else:                                   pass

# ------------------------------------------------------------------------------
# L o c a t e H W
# ------------------------------------------------------------------------------
# input:        devTrainer, devAntDongle
#
# Description:  If DONGLE  not already opened, Get the dongle
#               If TRAINER not already opened, Get the trainer
#                   unless trainer is simulated then ignore!
#               Show appropriate messages
#
# Output:       devTrainer, devAntDongle
#
# Returns:      True if TRAINER and DONGLE found
# ------------------------------------------------------------------------------
def LocateHW(self):
    global devTrainer, devAntDongle
    if debug.on(debug.Application): logfile.Write ("Scan for hardware")

    #---------------------------------------------------------------------------
    # Get ANT dongle
    #---------------------------------------------------------------------------
    if debug.on(debug.Application): logfile.Write ("Get Dongle")
    if not devAntDongle:
        if clv.manual or clv.manualGrade:
            SetDongleMsg(self, "Simulated Dongle (manual mode)")
        else:
            devAntDongle, msg = ant.GetDongle()
            SetDongleMsg(self, msg)

    #---------------------------------------------------------------------------
    # Get Trainer and find trainer model for Windows and Linux
    #---------------------------------------------------------------------------
    if debug.on(debug.Application): logfile.Write ("Get USB trainer")
    if not devTrainer:
        if clv.SimulateTrainer:
            SetTacxMsg(self, "Simulated Trainer")
        else:
            devTrainer, msg = usbTrainer.GetTrainer()
            SetTacxMsg(self, msg)

    #---------------------------------------------------------------------------
    # Done
    #---------------------------------------------------------------------------
    if debug.on(debug.Application): logfile.Write ("Scan for hardware - end")
    if (clv.manual or clv.manualGrade or devAntDongle) and (clv.SimulateTrainer or devTrainer): 
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
    global devTrainer
    TargetMode      = gui.mode_Power
    TargetPower     = 100       # Start with 100 Watt
    TargetGrade     = 0
    rolldown        = False
    rolldown_time   = 0
    SpeedKmh        = 0
    #self.InstructionsVariable.set('''
    #CALIBRATION TIPS: 
    #1. Tyre pressure 100psi (unloaded and cold) aim for 7.2s rolloff
    #2. Warm up for 2 mins, then cycle 30kph-40kph for 30s 
    #3. SpeedKmh up to above 40kph then stop pedalling and freewheel
    #4. Rolldown timer will start automatically when you hit 40kph, so stop pedalling quickly!
    #''')
    self.RunningSwitch = True
    while self.RunningSwitch == True:
        StartTime = time.time()
        #-----------------------------------------------------------------------
        # Get data from trainer
        #-----------------------------------------------------------------------
        SpeedKmh, WheelSpeed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, CurrentResistance, Buttons, Axis = \
            usbTrainer.ReceiveFromTrainer(devTrainer)
        if   Buttons == usbTrainer.EnterButton:     pass
        elif Buttons == usbTrainer.DownButton:      TargetPower -= 50          # Subtract 50 Watts for calibration test
        elif Buttons == usbTrainer.UpButton:        TargetPower += 50          # Add 50 Watts for calibration test
        elif Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False # Stop calibration
        else:                                       pass

        #-----------------------------------------------------------------------
        # Show what happens
        #-----------------------------------------------------------------------
        if debug.on(debug.Application): logfile.Write ("Trainer runoff: SpeedKmh=%s PedalEcho=%s hr=%s CurrentPower=%s cad=%s res=%s" % \
            (SpeedKmh, PedalEcho, HeartRate, CurrentPower, Cadence, TargetPower))
        
        if SpeedKmh == "Not Found":
            SetValues(self, 0, 0, 0, 0, 0, 0, 0, 0)
            SetTacxMsg(self, "Check if trainer is powered on")
        else:
            SetValues(self, SpeedKmh, Cadence, CurrentPower, TargetMode, TargetPower, TargetGrade, Resistance, HeartRate)
            if not rolldown:
                SetTacxMsg(self, "Cycle to above 40kph (then stop)")
            else:
                SetTacxMsg(self, "Rolldown timer started - STOP PEDALLING! %s " % ( round((time.time() - rolldown_time),1) ) )
          
            #---------------------------------------------------------------------
            # Send data to trainer
            #---------------------------------------------------------------------
            usbTrainer.SendToTrainer(devTrainer, usbTrainer.modeResistance, \
                            TargetMode, TargetPower, False, -1, PedalEcho, WheelSpeed, Cadence, Calibrate, False)

            #---------------------------------------------------------------------
            # SpeedKmh up to 40 km/h and then rolldown
            #---------------------------------------------------------------------
            SpeedKmh = int(SpeedKmh)
            if SpeedKmh > 40:                   # SpeedKmh above 40, start rolldown
                rolldown = True
        
            if rolldown and SpeedKmh <=40 and rolldown_time == 0: # rolldown timer starts when dips below 40
                rolldown_time = time.time()     # set initial rolldown time
          
            if rolldown and SpeedKmh < 0.1 :    # wheel stopped
                self.RunningSwitch = False      # break loop
                SetTacxMsg(self, "Rolldown time = %s seconds (aim 7s)" % round((time.time() - rolldown_time),1))

            #---------------------------------------------------------------------
            # WAIT    Add wait so we only send every 250ms
            #---------------------------------------------------------------------
            SleepTime = 0.25 - (time.time() - StartTime)
            if SleepTime > 0: time.sleep(SleepTime)
    return True
    
# ------------------------------------------------------------------------------
# T a c x 2 D o n g l e
# ------------------------------------------------------------------------------
# input:        devAntDongle, devTrainer
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
    global devAntDongle, devTrainer

    #---------------------------------------------------------------------------
    # Initialize antDongle
    # Open channels:
    #    one to transmit the trainer info (Fitness Equipment)
    #    one to transmit heartrate info   (HRM monitor)
    #
    # And if you want a dedicated Speed Cadence Sensor, implement like this...
    #---------------------------------------------------------------------------
    if not (clv.manual or clv.manualGrade):
        ant.ResetDongle(devAntDongle)             # reset dongle
        ant.Calibrate(devAntDongle)               # calibrate ANT+ dongle
        ant.Trainer_ChannelConfig(devAntDongle)   # Create ANT+ master channel for FE-C
        
        if clv.hrm == None:
            ant.HRM_ChannelConfig(devAntDongle)   # Create ANT+ master channel for HRM
        else:
            ant.SlaveHRM_ChannelConfig(devAntDongle, clv.hrm)   # Create ANT+ slave channel for HRM
                                                  # 0: auto pair, nnn: defined HRM

        if clv.scs != None:
            ant.SlaveSCS_ChannelConfig(devAntDongle, clv.scs)   # Create ANT+ slave channel for SCS
                                                  # 0: auto pair, nnn: defined SCS
            pass
    
    if not clv.gui: logfile.Write ("Ctrl-C to exit")

    #---------------------------------------------------------------------------
    # Loop control
    #---------------------------------------------------------------------------
    self.RunningSwitch = True
    EventCounter       = 0

    #---------------------------------------------------------------------------
    # Calibrate trainer
    #---------------------------------------------------------------------------
    Buttons         = 0
    CountDown       = 120 * 4 # 8 minutes; 120 is the max on the cadence meter
    ResistanceArray = numpy.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) # Array for running everage
    Calibrate       = 0
    if not clv.SimulateTrainer and usbTrainer.CalibrateSupported():
        SetTacxMsg(self, "* * * * * C A L I B R A T I N G * * * * *")
    try:
        while self.RunningSwitch == True and not clv.SimulateTrainer and clv.calibrate \
              and not Buttons == usbTrainer.CancelButton and Calibrate == 0 \
              and usbTrainer.CalibrateSupported():
            StartTime = time.time()
            #-------------------------------------------------------------------------
            # Receive / Send trainer
            #-------------------------------------------------------------------------
            usbTrainer.SendToTrainer(devTrainer, usbTrainer.modeCalibrate, \
                        False, False, False, False, False, False, False, False, False)
            SpeedKmh, WheelSpeed, PedalEcho, HeartRate, CurrentPower, Cadence, TargetResistance, Resistance, Buttons, Axis = \
                        usbTrainer.ReceiveFromTrainer(devTrainer)
            if SpeedKmh == "Not Found": SpeedKmh = 0
            #-------------------------------------------------------------------------
            # Show progress
            #-------------------------------------------------------------------------
            if clv.gui: SetTacxMsg(self, "* * * * * C A L I B R A T I N G * * * * *")
            SetValues(self, SpeedKmh, int(CountDown/4), round(CurrentPower * -1,0), gui.mode_Power, 0, 0, Resistance * -1, 0)

            # ----------------------------------------------------------------------
            # Average power over the last 20 readings
            # Stop if difference between min/max is below threshold (30)
            # At least 30 seconds but not longer than the countdown time (8 minutes)
            # Note that the limits are empiracally established.
            # ----------------------------------------------------------------------
            if Resistance < 0 and  WheelSpeed > 0:    # Calibration is started (with pedal kick)
                ResistanceArray = numpy.append(ResistanceArray, Resistance * -1) # Add new value to array
                ResistanceArray = numpy.delete(ResistanceArray, 0)               # Remove oldest from array
                
                if CountDown < (120 * 4 - 30) and numpy.min(ResistanceArray) > 0:
                    if (numpy.max(ResistanceArray) - numpy.min(ResistanceArray) ) < 30 or CountDown <= 0:
                        Calibrate = Resistance * -1

                CountDown -= 0.25                   # If not started, no count down!
                
            #-------------------------------------------------------------------------
            # WAIT        So we do not cycle faster than 4 x per second
            #-------------------------------------------------------------------------
            SleepTime = 0.25 - (time.time() - StartTime)
            if SleepTime > 0: time.sleep(SleepTime)
    except KeyboardInterrupt:
        logfile.Write ("Stopped")
    #---------------------------------------------------------------------------
    # Stop trainer
    #---------------------------------------------------------------------------
    usbTrainer.SendToTrainer(devTrainer, usbTrainer.modeStop, 0, False, False, 0, 0, 0, 0, 0, clv.SimulateTrainer)

    #---------------------------------------------------------------------------
    # Initialize variables
    #---------------------------------------------------------------------------
    TargetMode              = gui.mode_Power
    TargetGradeFromDongle   = 0
    TargetPowerFromDongle   = 100           # set initial Target Power

    TargetGrade             = 0             # different sets used to implement
    TargetPower             = 100           #   manual mode
    UserAndBikeWeight       = 75 + 10       # defined according the standard (data page 51)
#   testWeight              = 10            # used to test SendToTrainer()
    
    Cadence                 = 0
    CurrentPower            = 0
    HeartRate               = 0
    PedalEcho               = 0
    Resistance              = 0
    SpeedKmh                = 0
    WheelSpeed              = 0
    
    #---------------------------------------------------------------------------
    # Initialize antHRM and antFE module
    #---------------------------------------------------------------------------
    hrm.Initialize()
    fe.Initialize()
    
    try:
        while self.RunningSwitch == True:
            StartTime = time.time()
            #-------------------------------------------------------------------
            # Get data from trainer
            # TRAINER- SHOULD WRITE THEN READ 70MS LATER REALLY
            #-------------------------------------------------------------------
            if clv.SimulateTrainer:
                SpeedKmh, WheelSpeed, PedalEcho, HeartRateT, CurrentPower, Cadence, Resistance, CurrentResistance, Buttons, Axis = \
                    SimulateReceiveFromTrainer (TargetPower, CurrentPower)
            else:
                SpeedKmhT, WheelSpeedT, PedalEcho, HeartRateT, CurrentPower, CadenceT, Resistance, CurrentResistance, Buttons, Axis = \
                    usbTrainer.ReceiveFromTrainer(devTrainer)
                if CurrentPower < 0: CurrentPower = 0       # No negative value defined for ANT message Page25 (#)
                
                CurrentPower /= clv.PowerFactor
                #---------------------------------------------------------------
                # Show results
                #---------------------------------------------------------------
                if SpeedKmh == "Not Found":
                    SpeedKmh = 0 # resolve antifier legacy (error-message in numeric)
                    SpeedKmhT, WheelSpeedT, PedalEcho, HeartRateT, CurrentPower, CadenceT, Resistance, Buttons, Axis = 0, 0, 0, 0, 0, 0, 0, 0, 0
                    SetTacxMsg(self, 'Cannot read from trainer')
                else:
                    if clv.gui: SetTacxMsg(self, "Trainer detected")

                #---------------------------------------------------------------
                # If NO Speed Cadence Sensor defined, use Trainer-info
                #---------------------------------------------------------------
                if clv.scs == None:
                    SpeedKmh   = SpeedKmhT  
                    WheelSpeed = WheelSpeedT
                    Cadence    = CadenceT

            #-------------------------------------------------------------------
            # HeartRate from trainer is broadcasted
            #   if -H is NOT specified
            #   otherwise, HeartRate must be provided from other source
            #-------------------------------------------------------------------
            if clv.hrm == None:
                HeartRate = HeartRateT  

            #-------------------------------------------------------------------
            # In manual-mode, power can be incremented or decremented
            # In all modes, operation can be stopped.
            #-------------------------------------------------------------------
            if clv.manual:
                TargetMode = gui.mode_Power
                if   Buttons == usbTrainer.EnterButton:     pass
                elif Buttons == usbTrainer.DownButton:      TargetPower -= 50   # testWeight -= 10 to test effect of Weight
                elif Buttons == usbTrainer.UpButton:        TargetPower += 50   # testWeight += 10
                elif Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                       pass
            elif clv.manualGrade:                           # 2020-01-23 new option
                TargetMode = gui.mode_Grade
                if   Buttons == usbTrainer.EnterButton:     pass
                elif Buttons == usbTrainer.DownButton:      TargetGrade -= 1
                elif Buttons == usbTrainer.UpButton:        TargetGrade += 1
                elif Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                       pass
                #--------------------------------------------------------------
                # Translate "grade" to TargetPower for display purpose only
                # The trainer will only use Grade, because of TargetMode
                #--------------------------------------------------------------
                r = usbTrainer.Grade2Resistance(TargetGrade, UserAndBikeWeight, WheelSpeed, Cadence)
                TargetPower = usbTrainer.Resistance2Power(r, WheelSpeed)
            else:
                if   Buttons == usbTrainer.EnterButton:     pass
                elif Buttons == usbTrainer.DownButton:      pass
                elif Buttons == usbTrainer.UpButton:        pass
                elif Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                       pass

                if  TargetMode == gui.mode_Power:
                    TargetPower = TargetPowerFromDongle * clv.PowerFactor
                    TargetGrade = 0

                elif TargetMode == gui.mode_Grade:
                    TargetPower = TargetPowerFromDongle     # 2020-01-22 Now filled with Grade-based value
                    TargetGrade = TargetGradeFromDongle

                else:
                    logfile.Write("Unsupported TargetMode %s" % TargetMode)

            #-------------------------------------------------------------------
            # Send data to trainer (either power OR grade)
            #-------------------------------------------------------------------
            usbTrainer.SendToTrainer(devTrainer, usbTrainer.modeResistance, \
                    TargetMode, TargetPower, TargetGrade, UserAndBikeWeight, \
                    PedalEcho, WheelSpeed, Cadence, Calibrate, clv.SimulateTrainer)    # testWeight

            #-------------------------------------------------------------------
            # Broadcast Heartrate message
            #-------------------------------------------------------------------
            messages = []
            if clv.hrm == None and HeartRate > 0 and not (clv.manual or clv.manualGrade):
                messages.append(hrm.BroadcastHeartrateMessage(devAntDongle, HeartRate))

            #-------------------------------------------------------------------
            # Broadcast TrainerData message
            #-------------------------------------------------------------------
            if clv.manual or clv.manualGrade:
                data = []
            else:
                messages.append(fe.BroadcastTrainerDataMessage (devAntDongle, Cadence, CurrentPower, SpeedKmh, HeartRate))
                
            #-------------------------------------------------------------------
            # Broadcast and receive ANT+ responses
            #-------------------------------------------------------------------
            if len(messages) > 0:
                data = ant.SendToDongle(messages, devAntDongle, '', True, False)

            #-------------------------------------------------------------------
            # Here all response from the ANT dongle are processed (receive=True)
            #
            # Commands from dongle that are expected are:
            # - TargetGradeFromDongle or TargetPowerFromDongle
            #-------------------------------------------------------------------
            for d in data:
                synch, length, id, info, checksum, rest, Channel, DataPageNumber = ant.DecomposeMessage(d)
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
                            TargetMode            = gui.mode_Basic
                            TargetGradeFromDongle = 0
                            TargetPowerFromDongle = ant.msgUnpage48_BasicResistance(info) * 1000  # n % of maximum of 1000Watt
                            
                        #-------------------------------------------------------
                        # Data page 49 (0x31) Target Power
                        #-------------------------------------------------------
                        elif   DataPageNumber == 49:                  
                            TargetMode            = gui.mode_Power
                            TargetGradeFromDongle = 0
                            TargetPowerFromDongle = ant.msgUnpage49_TargetPower(info)

                        #-------------------------------------------------------
                        # Data page 51 (0x33) Track resistance
                        #-------------------------------------------------------
                        elif DataPageNumber == 51:
                            TargetMode            = gui.mode_Grade
                            TargetGradeFromDongle = ant.msgUnpage51_TrackResistance(info)
                            TargetPowerFromDongle = 0
                            
                            #-------------------------------------------------------
                            # 2020-01-22 Translate "grade" to TargetPower for
                            # display purpose on the console only
                            # The trainer will only use Grade, because of TargetMode
                            #-------------------------------------------------------
                            r = usbTrainer.Grade2Resistance(TargetGradeFromDongle, UserAndBikeWeight, WheelSpeed, Cadence)
                            TargetPowerFromDongle = usbTrainer.Resistance2Power(r, WheelSpeed)
                            
                        #-------------------------------------------------------
                        # Data page 55 User configuration
                        #-------------------------------------------------------
                        elif DataPageNumber == 55:
                            UserWeight, BicycleWeight, BicyleWheelDiameter, GearRatio = ant.msgUnpage55_UserConfiguration(info)
                            UserAndBikeWeight = UserWeight + BicycleWeight

                        #-------------------------------------------------------
                        # Data page 70 Request data page
                        #-------------------------------------------------------
                        elif DataPageNumber == 70:
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
                        # Data page 252 ????
                        #-------------------------------------------------------
                        elif DataPageNumber == 252 and (PrintWarnings or debug.on(debug.Data1)):
                            logfile.Write('FE data page 252 ignored. info=%' % logfile.HexSpace(info))
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
                        # Data page 0...4 HRM data
                        # Only expected when -H flag specified
                        #-------------------------------------------------------
                        if DataPageNumber & 0x7f in (0,1,2,3,4,5,6,7,89,95):
                            if clv.hrm >= 0:
                                Channel, DataPageNumber, Spec1, Spec2, Spec3, \
                                    HeartBeatEventTime, HeartBeatCount, HeartRate = \
                                    ant.msgUnpage_Hrm(info)
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
#scs                        WheelSpeed = ...
#scs                        Cadence    = ...

                        #-------------------------------------------------------
                        # Other data pages
                        #-------------------------------------------------------
                        else: error = "Unknown SCS data page"

                    #-----------------------------------------------------------
                    # Unknown channel
                    #-----------------------------------------------------------
                    else: error="Unknown channel"

                #---------------------------------------------------------------
                # ChannelID - the info from a Master device on the network
                #---------------------------------------------------------------
                elif id == ant.msgID_ChannelID:
                    Channel, DeviceNumber, DeviceTypeID, TransmissionType = \
                        ant.unmsg51_ChannelID(info)

                    if Channel == ant.channel_HRM_s and DeviceTypeID == ant.DeviceTypeID_HRM:
                        logfile.Write('Heart Rate Monitor paired: %s' % DeviceNumber)
                    else:
                        logfile.Write('Unexpected device %s on channel %s' % (DeviceNumber, Channel))
                        

                #---------------------------------------------------------------
                # Message ChannelResponse, acknowledges a message
                #---------------------------------------------------------------
                elif id == ant.msgID_ChannelResponse:
                    Channel, InitiatingMessageID, ResponseCode = ant.unmsg64_ChannelResponse(info)
                    pass
                    
                #---------------------------------------------------------------
                # Message BurstData, ignored
                #---------------------------------------------------------------
                elif id == ant.msgID_BurstData:
                    pass

                else: error = "Unknown message ID"

                #---------------------------------------------------------------
                # Unsupported channel, message or page can be silentedly ignored
                # Show WHAT we ignore, not to be blind for surprises!
                #---------------------------------------------------------------
                if error and (PrintWarnings or debug.on(debug.Data1)): logfile.Write(\
                    "ANT Dongle:%s: synch=%s, len=%2s, id=%s, check=%s, channel=%s, page=%s(%s) info=%s" % \
                    (error, synch, length, hex(id), checksum, Channel, DataPageNumber, hex(DataPageNumber), logfile.HexSpace(info)))

            #-------------------------------------------------------------------
            # Show progress
            #-------------------------------------------------------------------
            TargetPower = round(TargetPower,0)
            SetValues(self, SpeedKmh, Cadence, round(CurrentPower,0), TargetMode, TargetPower, TargetGrade, Resistance, HeartRate)
                
            #-------------------------------------------------------------------
            # WAIT        So we do not cycle faster than 4 x per second
            #-------------------------------------------------------------------
            SleepTime = 0.25 - (time.time() - StartTime)
            if SleepTime > 0:
                time.sleep(SleepTime)
                if debug.on(debug.Data2): logfile.Write ("Sleep(%4.2f) to fill 0.25 seconds done." % (SleepTime) )
            else:
                if SleepTime < -1:          # Avoid too many messages
                    logfile.Write ("Processing longer than 0.25 seconds: %4.2f" % (SleepTime * -1) )
                pass

            EventCounter += 1           # Increment and ...
            EventCounter &= 0xff        # maximize to 255
            
    except KeyboardInterrupt:
        logfile.Write ("Stopped")
        
    #---------------------------------------------------------------------------
    # Stop devices
    #---------------------------------------------------------------------------
    if not (clv.manual or clv.manualGrade):
        ant.ResetDongle(devAntDongle)
    usbTrainer.SendToTrainer(devTrainer, usbTrainer.modeStop, 0, False, False, \
                             0, 0, 0, 0, 0, clv.SimulateTrainer)

    return True

# ------------------------------------------------------------------------------
# S i m u l a t e R e c e i v e F r o m T r a i n e r 
# ------------------------------------------------------------------------------
# input:        None
#
# Description:  Basically, values are set so that no trainer-interface is needed
#               Especially, to be able to test without the trainer being active
#
#               Just for fun, generate so values based upon what the trainer
#               program wants so that a live simulation can be generated.
#               For example to make a video without pedalling.
#
#               The CurrentPower smoothly adjust to TargetPower
#               The HeartRate follows the CurrentPower produced
#               The Cadence is floating around 100
#               The Speed follows the Cadence
#
# Output:       None
# ------------------------------------------------------------------------------
def SimulateReceiveFromTrainer (TargetPower, CurrentPower):
    Axis        = 0
    Buttons     = 0
    PedalEcho   = 0
    Resistance  = 2345
    if False or TargetPower < 10:   # Return fixed value
        SpeedKmh    = 34.5
        HeartRate   = 135
        CurrentPower= 246
        Cadence     = 113
    else:                           # Return animated value
                                    # Using this setting, you let TrainerRoad and FortiusANT play together
                                    # and sip a beer yourself :-)
        HRmax       = 180
        ftp         = 246   # at 80% HRmax

        deltaPower    = (TargetPower - CurrentPower)
        if deltaPower < 8:
            CurrentPower = TargetPower
            deltaPower   = 0
        else:
            CurrentPower = CurrentPower + deltaPower / 8                    # Step towards TargetPower
        CurrentPower *= (1 + random.randint(-3,3) / 100)                    # Variation of 5%

        Cadence       = 100 - deltaPower / 10                               # Cadence drops when Target increases
        Cadence      *= (1 + random.randint(-2,2) / 100)                    # Variation of 2%

        SpeedKmh      = 35 * Cadence / 100                                  # Speed is 35 kmh at cadence 100 (My highest gear)

        HeartRate     = HRmax * (0.5 + ((CurrentPower - 100) / (ftp - 100) ) * 0.3)
                                                                            # As if power is linear with power
                                                                            # 100W is reached at 50%
                                                                            # ftp  is reached at 80%
                                                                            # Assume lineair between 100W and ftp
        if HeartRate < HRmax * 0.5: HeartRate = HRmax * 0.5 # minimize HR
        if HeartRate > HRmax:       HeartRate = HRmax       # maximize HR
        HeartRate    += random.randint(-5,5)                # Variation of heartrate by 5 beats

    WheelSpeed = usbTrainer.Speed2Wheel(SpeedKmh)
    Resistance = usbTrainer.Power2Resistance(CurrentPower, WheelSpeed, Cadence)

    return SpeedKmh, WheelSpeed, int(PedalEcho), int(HeartRate), int(CurrentPower), int(Cadence), int(Resistance), 0, int(Buttons), int(Axis)

# ==============================================================================
# Main program; Command line parameters
# ==============================================================================
if __name__ == "__main__":
    global clv

    debug.deactivate()
    clv = cmd.Create()
    debug.activate(clv.debug)

    if PrintWarnings or debug.on(debug.Any):
        logfile.Open()
        logfile.Write("FortiusANT started")
        clv.print()
        logfile.Write("------------------")

    #-------------------------------------------------------------------------------
    # Component info
    #-------------------------------------------------------------------------------
    if debug.on(debug.Any):
        logfile.Write('Version info for the components' )
        s = " %17s = %s"
        logfile.Write(s % ('FortiusAnt',                   __version__ ))
        logfile.Write(s % ('antDongle',                ant.__version__ ))
        logfile.Write(s % ('antHRM',                   hrm.__version__ ))
        logfile.Write(s % ('antFE',                     fe.__version__ ))
        logfile.Write(s % ('debug',                  debug.__version__ ))
        logfile.Write(s % ('FortiusAntCommand',        cmd.__version__ ))
        logfile.Write(s % ('FortiusAntGui',            gui.__version__ ))
        logfile.Write(s % ('logfile',              logfile.__version__ ))
        logfile.Write(s % ('structConstants',           sc.__version__ ))
        logfile.Write(s % ('usbTrainer',        usbTrainer.__version__ ))

        logfile.Write(s % ('argparse',            argparse.__version__ ))
    #   logfile.Write(s % ('binascii',            binascii.__version__ ))
    #   logfile.Write(s % ('math',                    math.__version__ ))
        logfile.Write(s % ('numpy',                  numpy.__version__ ))
    #   logfile.Write(s % ('os',                        os.__version__ ))
        logfile.Write(s % ('pickle',                pickle.format_version ))
        logfile.Write(s % ('platform',            platform.__version__ ))
    #   logfile.Write(s % ('glob',                    glob.__version__ ))
    #   logfile.Write(s % ('random',                random.__version__ ))
        logfile.Write(s % ('sys (python)',             sys.version ))
    #   logfile.Write(s % ('struct',                struct.__version__ ))
    #   logfile.Write(s % ('threading',          threading.__version__ ))
    #   logfile.Write(s % ('time',                    time.__version__ ))
        logfile.Write(s % ('usb',                      usb.__version__ ))
        logfile.Write(s % ('wx',                        wx.__version__ ))

    #-------------------------------------------------------------------------------
    # Main program; and go!
    #-------------------------------------------------------------------------------
    devTrainer = False
    devAntDongle = False
    if clv.gui:
        app = wx.App(0)
        frame = frmFortiusAnt(None)
        frame.SetTitle( WindowTitle )
        app.SetTopWindow(frame)
        SetFactorMsg(frame, clv.PowerFactor)
        frame.Show()
        if clv.autostart:
            frame.Autostart()
        app.MainLoop()
    else:
        x = frmFortiusAntNoGui()
        if LocateHW(x):
            Tacx2Dongle(x)
