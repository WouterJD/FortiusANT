#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2021-02-03"
# 2021-02-04    Fix ANT command status response (page 71) #222 by @switchabl
# 2021-01-28    We're bravely calibrating BUT since in the split of 2020-04-23
#               'Calibrate' was not replaced by TacxTrainer.Calibrate
#               it was never used!!
#               Note that initiating the calibration value (-c) is not usefull;
#                    calibration not only measures but also warms the tire.
# 2021-01-14    Magnetic brake Version message handling modified
#               #202 Fortius calibration skipped in ANTdongle restart
# 2021-01-12    Small bu very relevant corrections :-(
# 2021-01-10    Digital gearbox changed to front/rear index
# 2021-01-06    settings added (+ missing other files for version check)
# 2020-12-30    Tacx Genius and Bushido implemented
# 2020-12-27    Inform user of (de)activation of ANT/BLE devices
# 2020-12-24    usage of UseGui implemented
#               If -b is expected, antDongle is optional.
# 2020-12-20    Constants used from constants.py
#               bleCTP device implemented
# 2020-12-14    ANT+ Control command implemented
#               Runoff procedure improved
# 2020-12-10    GradeShift/GradeFactor are multipliers
#               antDeviceID specified on command-line
# 2020-12-08    GradeAdjust is split into GradeShift/GradeFactor
# 2020-12-07    Slope grade as received from CTP is reduced with self.clv.GradeAdjust
# 2020-11-19    QuarterSecond calculation code modified (functionally unchanged)
# 2020-11-18    Same as 2020-09-30 In idle mode, modeCalibrate was used instead
#                   of modeStop.
# 2020-11-13    QuarterSecond calculation improved
# 2020-11-12    tcxExport class definitions changed
# 2020-11-10    Calibration employs moving average as requested by #132
# 2020-11-04    Basic Resistance implemented as a grade as requested by #119
# 2020-11-03    If there is no dongle, AntDongle becomes completely dummy, 
#               so that we can run without ANTdongle.
#               As extension to 2020-09-29, which was not complete.
# 2020-10-20    Pedalling replaced by pedaling.
# 2020-09-30    During Runoff, modeCalibrate was used instead of modeResistance
#                   an error introduced with release 3.0 and now resolved.
# 2020-09-29    If NO ANTdongle present; users want to be able to test
#               FortiusANT to evaluate the software before bying dongles.
#               Therefore in manual mode, no ANTdongle required.
#               Of course for USB-trainers only (==> not clv.Tacx_iVortex)
#               Typo's corrected (thanks RogerPleijers)
# 2020-06-12    Added: BikePowerProfile and SpeedAndCadenceSensor final
# 2020-06-11    Added: BikePowerProfile (master)
# 2020-06-09    Added: SpeedAndCadenceSensor (master)
# 2020-05-27    Added: msgPage71_CommandStatus handled -- and tested
# 2020-05-24    i-Vortex adjustments
#               - in manual mode, ANTdongle must be present as well, so that
#                 manual mode works for i-Vortex as well. 
#                 For USB-trainers perhaps not needed, but FortiusANT needs a
#                   dongle - I would say by name and hence definition!
# 2020-05-15    Window title removed here
# 2020-05-14    pylint error free
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
# 2020-04-07    Before Calibrating, "Start pedaling" is displayed
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
from   constants                    import mode_Power, mode_Grade, UseBluetooth, UseGui

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
if UseGui:
    import wx

from   datetime                     import datetime

import antDongle         as ant
import antFE             as fe
import antHRM            as hrm
import antPWR            as pwr
import antSCS            as scs
import antCTRL           as ctrl
import debug
import logfile
import TCXexport
import usbTrainer

import bleDongle

PrintWarnings = False   # Print warnings even when logging = off
CycleTimeFast = 0.02    # TRAINER- SHOULD WRITE THEN READ 70MS LATER REALLY
CycleTimeANT  = 0.25
# ------------------------------------------------------------------------------
# Initialize globals
# ------------------------------------------------------------------------------
def Initialize(pclv):
    global clv, AntDongle, TacxTrainer, tcx, bleCTP
    clv         = pclv
    AntDongle   = None
    TacxTrainer = None
    tcx         = None
    if clv.exportTCX: tcx = TCXexport.clsTcxExport()
    bleCTP = bleDongle.clsBleCTP(clv)
    
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
        TacxTrainer.Refresh(True, usbTrainer.modeStop)
        rtn = TacxTrainer.Buttons
    return rtn

# ------------------------------------------------------------------------------
# S e t t i n g s
# ------------------------------------------------------------------------------
# input:        pRestartApplication, pclv
#
# Description:  data provided by the GUI/Settings interface
#               NOTE: only dynamic parameters of clv may be changed, otherwise
#                     the application must be restarted.
#                     If important parameters are changed (without restart)
#                     this may cause unchecked inconsistencies!
#
# Output:       new clv adopted
#
# Returns:      True
# ------------------------------------------------------------------------------
def Settings(self, pRestartApplication, pclv):
    global clv
    clv = pclv
    if debug.on(debug.Function):
        logfile.Write ("FortiusAntBody.Settings(%s, %s)" % (pRestartApplication, pclv.debug))
    return True

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
    global clv, AntDongle, TacxTrainer, bleCTP
    if debug.on(debug.Application): logfile.Write ("Scan for hardware")

    #---------------------------------------------------------------------------
    # No actions needed for Bluetooth dongle
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # Get ANT dongle
    #---------------------------------------------------------------------------
    if debug.on(debug.Application): logfile.Write ("Get Dongle")
    if AntDongle and AntDongle.OK:
        pass
    else:
        AntDongle = ant.clsAntDongle(clv.antDeviceID)
        if AntDongle.OK or not (clv.Tacx_Vortex or clv.Tacx_Genius or clv.Tacx_Bushido):       # 2020-09-29
             if clv.manual:      AntDongle.Message += ' (manual power)'
             if clv.manualGrade: AntDongle.Message += ' (manual grade)'
        self.SetMessages(Dongle=AntDongle.Message + bleCTP.Message)

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
                                                                    # 2020-09-29
    return ((AntDongle.OK or (not (clv.Tacx_Vortex or clv.Tacx_Genius or clv.Tacx_Bushido)
                              and (clv.manual or clv.manualGrade or clv.ble))) \
            and TacxTrainer.OK)
    
# ------------------------------------------------------------------------------
# R u n o f f
# ------------------------------------------------------------------------------
# input:        devTrainer
#
#               clv.RunoffMaxSpeed  = 30  km/hr
#               clv.RunoffDip       = 2   km/hr
#               clv.RunoffMinSpeed  = 1   km/hr
#               clv.RunoffTime      = 7   seconds
#               clv.RunoffPower     = 100 Watt
#
# Description:  run trainer untill 40km/h reached then untill stopped.
#               Initially, target power is 100Watt, which may be influenced
#               with the up/down buttons on the headunit of the trainer.
#
#               Note, that there is no ANT+ loop active here!
#               - ANT+ Controller cannot be used here
#
#               The runoff process is:
#               - Warm-up for two minutes
#               - Increase speed until 30 km/hr is met
#               - Stop pedalling and let wheel rundown
#               - The time from stop pedalling -> wheel stopped is measured
#                   That time is aimed to be 7.2 seconds
#
# Thanks:       antifier, cycleflow
#
# Output:       none
#
# Returns:      True
# ------------------------------------------------------------------------------
def Runoff(self):
    global clv, AntDongle, TacxTrainer
    if clv.SimulateTrainer or clv.Tacx_Vortex or clv.Tacx_Genius or clv.Tacx_Bushido:
        logfile.Console('Runoff not implemented for Simulated trainer or Tacx Vortex/Genius/Bushido')
        return False

    #---------------------------------------------------------------------------
    # Initialize
    #---------------------------------------------------------------------------
    TacxTrainer.SetPower(clv.RunoffPower)
    rolldown        = False
    rolldown_time   = 0
    #ShortMessage   = TacxTrainer.Message + " | Runoff - "
    ShortMessage    = "Tacx Trainer Runoff - "

    #---------------------------------------------------------------------------
    # Pedal stroke Analysis
    #---------------------------------------------------------------------------
    pdaInfo         = []        # Collection of (time, power)
    LastPedalEcho   = 0         # Flag that cadence sensor was seen

    LastPower       = 0         # statistics
    PowerCount      = 0
    PowerEqual      = 0

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
        TacxTrainer.Refresh(True, usbTrainer.modeResistance) # This cannot be an ANT trainer

        #-----------------------------------------------------------------------
        # Show what happens
        #-----------------------------------------------------------------------
        if TacxTrainer.Message == "Not Found":
            self.SetValues(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            self.SetMessages(Tacx="Check if trainer is powered on")
        else:
            self.SetValues( TacxTrainer.SpeedKmh,         TacxTrainer.Cadence, \
                            TacxTrainer.CurrentPower,     TacxTrainer.TargetMode, \
                            TacxTrainer.TargetPower,      TacxTrainer.TargetGrade, \
                            TacxTrainer.TargetResistance, TacxTrainer.HeartRate, \
                            0, 0, 0)
            #---------------------------------------------------------------------
            # SpeedKmh up to 40 km/h and then let wheel rolldown
            #---------------------------------------------------------------------
            if not rolldown:
                self.SetMessages(Tacx=ShortMessage + "Warm-up for some minutes, then cycle to above {}km/hr" \
                                                    .format(clv.RunoffMaxSpeed))

                if TacxTrainer.SpeedKmh > clv.RunoffMaxSpeed:      # SpeedKmh above 40, start rolldown
                    self.SetMessages(Tacx=ShortMessage + "STOP PEDALLING")
                    rolldown = True

            #---------------------------------------------------------------------
            # Measure time from MaxSpeed-Dip --> MinSpeed
            #---------------------------------------------------------------------
            else:
                if TacxTrainer.SpeedKmh <= clv.RunoffMaxSpeed - clv.RunoffDip:
                    # rolldown timer starts when dips below 38
                    if rolldown_time == 0:
                        rolldown_time = time.time()
                    self.SetMessages(Tacx=ShortMessage + \
                                        "KEEP STILL, Rolldown timer %s seconds" % \
                                        ( round((time.time() - rolldown_time),1) ) \
                                    )
          
                if TacxTrainer.SpeedKmh < clv.RunoffMinSpeed :  # wheel almost stopped
                    self.SetMessages(Tacx=ShortMessage + \
                                        "Rolldown time = %s seconds (aim %s s)" % \
                                        (round((time.time() - rolldown_time),1), clv.RunoffTime) \
                                    )

                if TacxTrainer.SpeedKmh < 0.1 :                 # wheel stopped
                    self.RunningSwitch = False                  # break loop

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
        # case 3. Cadence = 120 and Cycle time (in seconds) = 0.02
        #       angle = .02 * 6 * 120 = 14.40 degrees
        #                             = 25 samples per circle
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
                # Gather some statistics while really pedaling
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
    self.SetValues( 0, 0, 0, TacxTrainer.TargetMode, 0, 0, 0, 0, 0, 0, 0 )
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
    global clv, AntDongle, TacxTrainer, bleCTP
    Restart = False
    while True:
        rtn = Tacx2DongleSub(self, Restart)
        if AntDongle.DongleReconnected:
            self.SetMessages(Dongle=AntDongle.Message + bleCTP.Message)
            AntDongle.ApplicationRestart()
            Restart = True
        else:
            break
    return rtn

def Tacx2DongleSub(self, Restart):
    global clv, AntDongle, TacxTrainer, tcx, bleCTP

    assert(AntDongle)                       # The class must be created
    assert(TacxTrainer)                     # The class must be created
    assert(bleCTP)                          # The class must be created

    AntHRMpaired = False

    #---------------------------------------------------------------------------
    # Front/rear shifting
    #---------------------------------------------------------------------------
    ReductionCranckset = 1                  # ratio between selected/start (front)
    ReductionCassette  = 1                  # same, rear
    ReductionCassetteX = 1                  # same, beyond cassette range
    CrancksetIndex = clv.CrancksetStart
    CassetteIndex  = clv.CassetteStart

    #---------------------------------------------------------------------------
    # Command status data
    #---------------------------------------------------------------------------
    p71_LastReceivedCommandID   = 255
    p71_SequenceNr              = 255
    p71_CommandStatus           = 255
    p71_Data1                   = 0xff
    p71_Data2                   = 0xff
    p71_Data3                   = 0xff
    p71_Data4                   = 0xff

    #---------------------------------------------------------------------------
    # Command status data for ANT Control
    #---------------------------------------------------------------------------
    ctrl_p71_LastReceivedCommandID   = 255
    ctrl_p71_SequenceNr              = 255
    ctrl_p71_CommandStatus           = 255
    ctrl_p71_Data1                   = 0xff
    ctrl_p71_Data2                   = 0xff
    ctrl_p71_Data3                   = 0xff
    ctrl_p71_Data4                   = 0xff

    ctrl_Commands = []  # Containing tuples (manufacturer, serial, CommandNr)

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
    #    one to interface with Tacx i-Vortex headunit (VHU)
    #
    # And if you want a dedicated Speed Cadence Sensor, implement like this...
    #---------------------------------------------------------------------------
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
        # msg = ant.msg4D_RequestMessage(ant.channel_HRM_s, ant.msgID_ChannelID)
        # AntDongle.Write([msg], False, False)

    if clv.Tacx_Vortex:
        #-------------------------------------------------------------------
        # Create ANT slave channel for VTX
        # No pairing-loop: VTX perhaps not yet active and avoid delay
        #-------------------------------------------------------------------
        AntDongle.SlaveVTX_ChannelConfig(0)

        # msg = ant.msg4D_RequestMessage(ant.channel_VTX_s, ant.msgID_ChannelID)
        # AntDongle.Write([msg], False, False)

        #-------------------------------------------------------------------
        # Create ANT slave channel for VHU
        #
        # We create this channel right away. At some stage the VTX-channel
        # sends the Page03_TacxVortexDataCalibration which provides the
        # VortexID. This VortexID is the DeviceID that could be provided
        # to SlaveVHU_ChannelConfig() to restrict pairing to that headunit
        # only. Not relevant in private environments, so left as is here.
        #-------------------------------------------------------------------
        AntDongle.SlaveVHU_ChannelConfig(0)

    if clv.Tacx_Genius:
        #-------------------------------------------------------------------
        # Create ANT slave channel for GNS
        # No pairing-loop: GNS perhaps not yet active and avoid delay
        #-------------------------------------------------------------------
        AntDongle.SlaveGNS_ChannelConfig(0)

    if clv.Tacx_Bushido:
        #-------------------------------------------------------------------
        # Create ANT slave channel for BHU
        # No pairing-loop: GNS perhaps not yet active and avoid delay
        #-------------------------------------------------------------------
        AntDongle.SlaveBHU_ChannelConfig(0)

    if True:
        #-------------------------------------------------------------------
        # Create ANT+ master channel for PWR
        #-------------------------------------------------------------------
        AntDongle.PWR_ChannelConfig(ant.channel_PWR)

    if clv.scs == None:
        #-------------------------------------------------------------------
        # Create ANT+ master channel for SCS
        #-------------------------------------------------------------------
        AntDongle.SCS_ChannelConfig(ant.channel_SCS)
    else:
        #-------------------------------------------------------------------
        # Create ANT+ slave channel for SCS
        # 0: auto pair, nnn: defined SCS
        #-------------------------------------------------------------------
        AntDongle.SlaveSCS_ChannelConfig(clv.scs)
        pass

    if True:
        #-------------------------------------------------------------------
        # Create ANT+ master channel for ANT Control
        #-------------------------------------------------------------------
        AntDongle.CTRL_ChannelConfig(ant.DeviceNumber_CTRL)

    if not clv.gui: logfile.Console ("Ctrl-C to exit")

    #---------------------------------------------------------------------------
    # Loop control
    #---------------------------------------------------------------------------
    EventCounter       = 0

    #---------------------------------------------------------------------------
    # Calibrate trainer
    #
    # Note, that there is no ANT+ loop active here!
    # - Calibration is currently implemented for Tacx Fortius (motorbrake) only.
    # - ANT+ Controller cannot be used here
    #---------------------------------------------------------------------------
    CountDownX      = 1 # If calibration takes more than two minutes
                        # Extend countdown: 2 ==> 4 minutes, 4 ==> 8 minutes
                        # This will not cause the countdown to take longer,
                        # it only extends the maximum time untill a stable reading.
    CountDown       = 120 * CountDownX # 2 minutes; 120 is the max on the cadence meter
    ResistanceArray = numpy.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) # Array for calculating running average
    AvgResistanceArray = numpy.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) # Array for collating running averages
    TacxTrainer.Calibrate  = 0
    StartPedaling   = True
    Counter         = 0

    if TacxTrainer.CalibrateSupported():
        self.SetMessages(Tacx="* * * * G I V E   A   P E D A L   K I C K   T O   S T A R T   C A L I B R A T I O N * * * *")
        if debug.on(debug.Function):
            logfile.Write('Tacx2Dongle; start pedaling for calibration')
    try:
    # if True:
        while         self.RunningSwitch \
              and     clv.calibrate \
              and not TacxTrainer.Buttons == usbTrainer.CancelButton \
              and     TacxTrainer.Calibrate == 0 \
              and     TacxTrainer.CalibrateSupported() \
              and not Restart:
            StartTime = time.time()
            #-------------------------------------------------------------------
            # Receive / Send trainer
            #-------------------------------------------------------------------
            TacxTrainer.Refresh(True, usbTrainer.modeCalibrate)

            #-------------------------------------------------------------------
            # When calibration IS supported, the following condition will NOT occur.
            # iFlow 1932 is expected to support calibration but does not.
            # This check is to stop calibration-loop because it will never end.
            #
            # First reading on 'my' Fortius shows a positive number, then goes negative
            # so ignore the first x readings before deciding it will not work.
            #-------------------------------------------------------------------
            # print(StartPedaling, SpeedKmh, CurrentResistance)
            if TacxTrainer.CurrentResistance > 0:
                Counter += 1
                if Counter == 10:
                    logfile.Console('Calibration stopped because of unexpected resistance value')
                    break

            if TacxTrainer.CurrentResistance < 0 and TacxTrainer.SpeedKmh > 0:
                # Calibration is started (with pedal kick)
                #---------------------------------------------------------------
                # Show progress (when calibrating is started)
                # This changes the message from "Start Pedaling" to "Calibrating"
                # The message must be given once for the console-mode (no GUI)
                #---------------------------------------------------------------
                if StartPedaling:
                    self.SetMessages(Tacx="* * * * C A L I B R A T I N G   (Do not pedal) * * * *")
                    if debug.on(debug.Function):
                        logfile.Write('Tacx2Dongle; start calibration')
                    StartPedaling = False

                self.SetValues(TacxTrainer.SpeedKmh, int(CountDown / CountDownX), \
                        round(TacxTrainer.CurrentPower * -1,0), \
                        mode_Power, 0, 0, TacxTrainer.CurrentResistance * -1, 0, 0, 0, 0)

                # --------------------------------------------------------------
                # Average power over the last 20 readings
                # Stop if difference between min/max running average is below threshold (2)
                # At least 30 seconds but not longer than the countdown time (8 minutes)
                # Note that the limits are empiracally established.
                # --------------------------------------------------------------
                ResistanceArray = numpy.append(ResistanceArray, TacxTrainer.CurrentResistance * -1) # Add new instantaneous value to array
                ResistanceArray = numpy.delete(ResistanceArray, 0)                      # Remove oldest from array

                AvgResistanceArray = numpy.append(AvgResistanceArray, numpy.average(ResistanceArray)) # Add new running average value to array
                AvgResistanceArray = numpy.delete(AvgResistanceArray, 0) # Remove oldest from array
                
                if CountDown < (120 * CountDownX - 30) and numpy.min(ResistanceArray) > 0:
                    if (numpy.max(AvgResistanceArray) - numpy.min(AvgResistanceArray) ) < 2 or CountDown <= 0:
                        TacxTrainer.Calibrate = int(numpy.average(AvgResistanceArray))
                        if debug.on(debug.Function):
                            logfile.Write( "Calibration stopped with resistance=%s after %s seconds" % \
                                           (TacxTrainer.Calibrate, int(120 * CountDownX - CountDown) ) )

                CountDown -= 0.25                   # If not started, no count down!
                
            #-------------------------------------------------------------------
            # WAIT        So we do not cycle faster than 4 x per second
            #-------------------------------------------------------------------
            SleepTime = 0.25 - (time.time() - StartTime)
            if SleepTime > 0: time.sleep(SleepTime)
    except KeyboardInterrupt:
        logfile.Console ("Stopped")
    except Exception as e:
        logfile.Console ("Calibration stopped with exception: %s" % e)
    #---------------------------------------------------------------------------
    # Stop trainer
    #---------------------------------------------------------------------------
    if TacxTrainer.OK:
        if debug.on(debug.Function): logfile.Write('Tacx2Dongle; stop trainer')
        TacxTrainer.SendToTrainer(True, usbTrainer.modeStop)
    self.SetMessages(Tacx=TacxTrainer.Message)

    #---------------------------------------------------------------------------
    # Initialize variables
    #---------------------------------------------------------------------------
    if not Restart:
        if clv.exportTCX:
            tcx.Start()                     # Start TCX export
        if clv.ble:
            bleCTP.Open()                   # Open connection with Bluetooth CTP
            self.SetMessages(Dongle=AntDongle.Message + bleCTP.Message)
        if clv.manualGrade:
            TacxTrainer.SetGrade(0)
        else:
            TacxTrainer.SetPower(100)
        TacxTrainer.SetGearboxReduction(1)

    TargetPowerTime         = 0             # Time that last TargetPower received
    PowerModeActive         = ''            # Text showing in userinterface
    
    LastANTtime             = 0             # ANT+ interface is sent/received only
                                            # every 250ms

    #---------------------------------------------------------------------------
    # Initialize antHRM and antFE module
    #---------------------------------------------------------------------------
    if debug.on(debug.Function): logfile.Write('Tacx2Dongle; initialize ANT')
    fe.Initialize()
    hrm.Initialize()
    pwr.Initialize()
    scs.Initialize()
    ctrl.Initialize()

    #---------------------------------------------------------------------------
    # Initialize CycleTime: fast for PedalStrokeAnalysis
    #---------------------------------------------------------------------------
    if clv.PedalStrokeAnalysis:
        CycleTime = CycleTimeFast   # Quick poll to get more info
        if debug.on(debug.Any): logfile.Console("Tacx2Dongle; Pedal Stroke Analysis active")
    else:
        CycleTime = CycleTimeANT    # Seconds, default = 0.25 (inspired by 4Hz ANT+)

    #---------------------------------------------------------------------------
    # ANT-, BLE- devices are active from here (after calibration!)
    #---------------------------------------------------------------------------
    s = ''
    if AntDongle.OK: s = 'ANT-'
    if clv.ble:
        if s: s += ' and '
        s += 'BLE-'
    ActivationMsg = '---------- %sdevices are activated ----------' % s
    if not Restart:
        logfile.Console (ActivationMsg)

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
        while self.RunningSwitch == True and not AntDongle.DongleReconnected:
            StartTime = time.time()
            #-------------------------------------------------------------------
            # ANT process is done once every 250ms
            # In case of PedalStrokeAnalysis, check whether it's time for ANT
            #-------------------------------------------------------------------
            if CycleTime == CycleTimeANT or (time.time() - LastANTtime) > 0.25:
                LastANTtime = time.time()
                QuarterSecond = True
            else:
                QuarterSecond = False 

            #-------------------------------------------------------------------
            # Get data from trainer (Receive + Calc + Send)
            #-------------------------------------------------------------------
            TacxTrainer.Refresh(QuarterSecond, usbTrainer.modeResistance)
            if clv.gui: self.SetMessages(Tacx=TacxTrainer.Message + PowerModeActive)

            #-------------------------------------------------------------------
            # If NO Speed Cadence Sensor defined, use Trainer-info
            # Hook for future development
            #-------------------------------------------------------------------
            # if clv.scs == None:
            #     SpeedKmh   = SpeedKmhSCS
            #     Cadence    = CadenceSCS

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
                            CrancksetIndex, \
                            CassetteIndex, ReductionCassetteX)

            #-------------------------------------------------------------------
            # Add trackpoint
            #-------------------------------------------------------------------
            if QuarterSecond and clv.exportTCX:
                tcx.TrackpointX(TacxTrainer, HeartRate)

            #-------------------------------------------------------------------
            # Store in JSON format
            #-------------------------------------------------------------------
            logfile.WriteJson(QuarterSecond, TacxTrainer, tcx, HeartRate)

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
            # Handle Control command
            #-------------------------------------------------------------------
            if len(ctrl_Commands):
                ctrl_SlaveManufacturerID, ctrl_SlaveSerialNumber, ctrl_CommandNr = ctrl_Commands[0]

                #-------------------------------------------------------------------
                # The ANT+controller gives head-unit commands.
                #       This is the default behaviour when no serial numbers defined
                #-------------------------------------------------------------------
                if clv.CTRL_SerialL == 0:
                    if   ctrl_CommandNr == ctrl.MenuUp:     TacxTrainer.Buttons = usbTrainer.UpButton
                    elif ctrl_CommandNr == ctrl.MenuDown:   TacxTrainer.Buttons = usbTrainer.DownButton
                    elif ctrl_CommandNr == ctrl.MenuSelect: TacxTrainer.Buttons = usbTrainer.OKButton
                    ctrl_CommandNr = ctrl.NoAction

                #-------------------------------------------------------------------
                # A left ANT+controller may be defined, with it's own behaviour
                #-------------------------------------------------------------------
                elif ctrl_SlaveSerialNumber == clv.CTRL_SerialL:
                    pass

                #-------------------------------------------------------------------
                # A right ANT+controller may be defined, with it's own behaviour
                #-------------------------------------------------------------------
                elif ctrl_SlaveSerialNumber == clv.CTRL_SerialR:
                    pass

                #-------------------------------------------------------------------
                # Remove command
                #-------------------------------------------------------------------
                ctrl_Commands.pop(0)

            #-------------------------------------------------------------------
            # In manual-mode, power can be incremented or decremented
            # In all modes, operation can be stopped.
            #
            # TargetMode  is set here (manual mode) or received from ANT+ (Zwift)
            # TargetPower and TargetGrade are set in this section only!
            #-------------------------------------------------------------------
            ReductionChanged = False
            if clv.manual:
                if   TacxTrainer.Buttons == usbTrainer.EnterButton:     pass
                elif TacxTrainer.Buttons == usbTrainer.DownButton:      TacxTrainer.AddPower(-50)
                elif TacxTrainer.Buttons == usbTrainer.OKButton:        TacxTrainer.SetPower(100)
                elif TacxTrainer.Buttons == usbTrainer.UpButton:        TacxTrainer.AddPower( 50)
                elif TacxTrainer.Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                                   pass
            elif clv.manualGrade:
                if   TacxTrainer.Buttons == usbTrainer.EnterButton:     pass
                elif TacxTrainer.Buttons == usbTrainer.DownButton:      TacxTrainer.AddGrade(-1)
                elif TacxTrainer.Buttons == usbTrainer.OKButton:        TacxTrainer.SetGrade(0)
                elif TacxTrainer.Buttons == usbTrainer.UpButton:        TacxTrainer.AddGrade( 1)
                elif TacxTrainer.Buttons == usbTrainer.CancelButton:    self.RunningSwitch = False
                else:                                                   pass
            else:
                if   TacxTrainer.Buttons == usbTrainer.EnterButton \
                or   TacxTrainer.Buttons == usbTrainer.OKButton:
                            ReductionChanged = True
                            CrancksetIndex = clv.CrancksetStart         # Reset both front
                            CassetteIndex  = clv.CassetteStart          # and rear

                elif TacxTrainer.Buttons == usbTrainer.UpButton:        # Switch rear right (smaller) = higher index
                            ReductionChanged = True
                            if CassetteIndex < 0:
                                CassetteIndex += 1
                                ReductionCassetteX *= 1.1
                            elif CassetteIndex < len(clv.Cassette) - 1:
                                CassetteIndex += 1
                            elif ReductionCassetteX < 2:
                                # Plus 7 extra steps beyond the end of the cassette
                                CassetteIndex += 1
                                ReductionCassetteX *= 1.1

                elif TacxTrainer.Buttons == usbTrainer.DownButton:      # Switch rear left (bigger) = lower index       
                            ReductionChanged = True
                            if CassetteIndex >= len(clv.Cassette):
                                CassetteIndex -= 1
                                ReductionCassetteX /= 1.1
                            elif CassetteIndex > 0:
                                CassetteIndex -= 1
                            elif ReductionCassetteX > 0.6:
                                # Plus 8 extra steps beyond the end of the cassette
                                CassetteIndex -= 1
                                ReductionCassetteX /= 1.1

                elif TacxTrainer.Buttons == usbTrainer.CancelButton:    # Switch front up (round robin)
                            ReductionChanged = True
                            #self.RunningSwitch = False
                            CrancksetIndex += 1
                            if CrancksetIndex == len(clv.Cranckset):
                                CrancksetIndex = 0

                else:                                                   pass

            #-------------------------------------------------------------------
            # Calculate Reduction
            #
            # Note that, the VIRTUAL gearbox has Reduction = 1 when the indexes
            #      are in the initial position (not when front = rear!).
            #
            # ReductionCranckset: >1 when chainring > start-value
            # ReductionCassette:  >1 when sprocket  < start-value
            # ReductionCassetteX: is a factor when index outside the cassette!
            #-------------------------------------------------------------------
            if ReductionChanged:
                if 0 <= CrancksetIndex < len(clv.Cranckset):
                    ReductionCranckset = clv.Cranckset[CrancksetIndex] / \
                                         clv.Cranckset[clv.CrancksetStart]

                if 0 <= CassetteIndex < len(clv.Cassette):
                    ReductionCassetteX = 1
                    ReductionCassette  = clv.Cassette[clv.CassetteStart] / \
                                         clv.Cassette[CassetteIndex]

                if debug.on(debug.Function):
                    if CassetteIndex >= len(clv.Cassette):
                        i = len(clv.Cassette) - 1
                    else:
                        i = CassetteIndex
                    logfile.Print('gearbox changed: index=%ix%2i ratio=%ix%i R=%3.1f*%3.1f*%3.1f=%3.1f' % \
                    (   CrancksetIndex, CassetteIndex, \
                        clv.Cranckset[CrancksetIndex], clv.Cassette[i], \
                        ReductionCranckset, ReductionCassette, ReductionCassetteX,\
                        ReductionCranckset * ReductionCassette * ReductionCassetteX))

                TacxTrainer.SetGearboxReduction(ReductionCranckset * ReductionCassette * ReductionCassetteX)

            #-------------------------------------------------------------------
            # Do ANT/BLE work every 1/4 second
            #-------------------------------------------------------------------
            messages = []       # messages to be sent to ANT
            data = []           # responses received from ANT
            if QuarterSecond:
                # LastANTtime = time.time()         # 2020-11-13 removed since duplicate
                #---------------------------------------------------------------
                # Sending i-Vortex messages is done by Refesh() not here
                #---------------------------------------------------------------

                #---------------------------------------------------------------
                # Broadcast Heartrate message
                #---------------------------------------------------------------
                if clv.hrm == None and TacxTrainer.HeartRate > 0:
                    messages.append(hrm.BroadcastHeartrateMessage(HeartRate))

                #---------------------------------------------------------------
                # Broadcast Bike Power message
                #---------------------------------------------------------------
                if True:
                    messages.append(pwr.BroadcastMessage( \
                        TacxTrainer.CurrentPower, TacxTrainer.Cadence))

                #---------------------------------------------------------------
                # Broadcast Speed and Cadence Sensor message
                #---------------------------------------------------------------
                if clv.scs == None:
                    messages.append(scs.BroadcastMessage( \
                        TacxTrainer.PedalEchoTime, TacxTrainer.PedalEchoCount, \
                        TacxTrainer.VirtualSpeedKmh, TacxTrainer.Cadence))

                #---------------------------------------------------------------
                # Broadcast Controllable message
                #---------------------------------------------------------------
                if True:
                    messages.append(ctrl.BroadcastControlMessage())

                #---------------------------------------------------------------
                # Broadcast TrainerData message to the CTP (Trainer Road, ...)
                #---------------------------------------------------------------
                # print('fe.BroadcastTrainerDataMessage', Cadence, CurrentPower, SpeedKmh, HeartRate)
                messages.append(fe.BroadcastTrainerDataMessage (TacxTrainer.Cadence, \
                    TacxTrainer.CurrentPower, TacxTrainer.SpeedKmh, TacxTrainer.HeartRate))

                #---------------------------------------------------------------
                # Send/receive to Bluetooth interface
                #
                # When data is received, TacxTrainer parameters are copied from
                # the bleCTP object.
                #---------------------------------------------------------------
                if clv.ble:
                    bleCTP.SetAthleteData(HeartRate)
                    bleCTP.SetTrainerData(TacxTrainer.SpeedKmh, \
                                    TacxTrainer.Cadence, TacxTrainer.CurrentPower)
                    if bleCTP.Refresh():
                        if bleCTP.TargetMode == mode_Power:
                            TargetPowerTime = time.time()
                            TacxTrainer.SetPower(bleCTP.TargetPower)

                        if bleCTP.TargetMode == mode_Grade:
                            if clv.PowerMode and (time.time() - TargetPowerTime) < 30:
                                pass
                            else:
                                Grade  = bleCTP.TargetGrade
                                Grade += clv.GradeShift
                                Grade *= clv.GradeFactor
                                if Grade < 0: Grade *= clv.GradeFactorDH

                                TacxTrainer.SetGrade(bleCTP.TargetGrade)

                        if bleCTP.WindResistance and bleCTP.WindSpeed and bleCTP.DraftingFactor:
                            TacxTrainer.SetWind(bleCTP.WindResistance, bleCTP.WindSpeed, bleCTP.DraftingFactor)

                        if bleCTP.RollingResistance:
                            TacxTrainer.SetRollingResistance(bleCTP.RollingResistance)

            #-------------------------------------------------------------------
            # Broadcast and receive ANT+ responses
            #-------------------------------------------------------------------
            if len(messages) > 0:
                data = AntDongle.Write(messages, True, False)

            #-------------------------------------------------------------------
            # Here all response from the ANT dongle are processed (receive=True)
            #
            # Commands from dongle that are expected are:
            # - TargetGradeFromDongle or TargetPowerFromDongle
            # - Information from HRM (if paired)
            # - Information from i-Vortex (if paired)
            #
            # Input is grouped by messageID, then channel. This has little
            # practical impact; grouping by Channel would enable to handle all
            # ANT in a channel (device) module. No advantage today.
            #-------------------------------------------------------------------
            for d in data:
                synch, length, id, info, checksum, _rest, Channel, DataPageNumber = ant.DecomposeMessage(d)
                error = False

                if clv.Tacx_Vortex or clv.Tacx_Genius or clv.Tacx_Bushido:
                    if TacxTrainer.HandleANTmessage(d):
                        continue                    # Message is handled or ignored

                #---------------------------------------------------------------
                # AcknowledgedData = Slave -> Master
                #       channel_FE = From CTP (Trainer Road, Zwift) --> Tacx 
                #---------------------------------------------------------------
                if id == ant.msgID_AcknowledgedData:
                    #-----------------------------------------------------------
                    # Fitness Equipment Channel inputs
                    #-----------------------------------------------------------
                    if Channel == ant.channel_FE:
                        #-------------------------------------------------------
                        # Data page 48 (0x30) Basic resistance
                        #-------------------------------------------------------
                        if   DataPageNumber == 48:
                            # logfile.Console('Data page 48 Basic mode not implemented')
                            # I never saw this appear anywhere (2020-05-08)
                            # TargetMode            = mode_Basic
                            # TargetGradeFromDongle = 0
                            # TargetPowerFromDongle = ant.msgUnpage48_BasicResistance(info) * 1000  # n % of maximum of 1000Watt

                            # 2020-11-04 as requested in issue 119
                            # The percentage is used to calculate grade 0...20%
                            Grade = ant.msgUnpage48_BasicResistance(info) * 20

                            # Implemented for Magnetic Brake:
                            # - grade is NOT shifted with GradeShift (here never negative)
                            # - but is reduced with factor
                            # - and is NOT reduced with factorDH since never negative
                            Grade *= clv.GradeFactor

                            TacxTrainer.SetGrade(Grade)
                            TacxTrainer.SetRollingResistance(0.004)
                            TacxTrainer.SetWind(0.51, 0.0, 1.0)

                            # Update "last command" data in case page 71 is requested later
                            p71_LastReceivedCommandID   = DataPageNumber
                            # wrap around after 254 (255 = no command received)
                            p71_SequenceNr              = (p71_SequenceNr + 1) % 255
                            p71_CommandStatus           = 0     # successfully processed
                            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
                            p71_Data2                   = 0xff
                            p71_Data3                   = 0xff
                            p71_Data4                   = info[8]      # target resistance
                            
                        #-------------------------------------------------------
                        # Data page 49 (0x31) Target Power
                        #-------------------------------------------------------
                        elif   DataPageNumber == 49:
                            TacxTrainer.SetPower(ant.msgUnpage49_TargetPower(info))
                            TargetPowerTime = time.time()
                            if False and clv.PowerMode and debug.on(debug.Application):
                                logfile.Write('PowerMode: TargetPower info received - timestamp set')

                            # Update "last command" data in case page 71 is requested later
                            p71_LastReceivedCommandID   = DataPageNumber
                            # wrap around after 254 (255 = no command received)
                            p71_SequenceNr              = (p71_SequenceNr + 1) % 255
                            p71_CommandStatus           = 0     # successfully processed
                            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
                            p71_Data2                   = 0xff
                            p71_Data3                   = info[7]       # target power (LSB)
                            p71_Data4                   = info[8]       # target power (MSB)

                        #-------------------------------------------------------
                        # Data page 50 (0x32) Wind Resistance
                        #-------------------------------------------------------
                        elif   DataPageNumber == 50:
                            WindResistance, WindSpeed, DraftingFactor = \
                                ant.msgUnpage50_WindResistance(info)
                            TacxTrainer.SetWind(WindResistance, WindSpeed, DraftingFactor)

                            # Update "last command" data in case page 71 is requested later
                            p71_LastReceivedCommandID   = DataPageNumber
                            # wrap around after 254 (255 = no command received)
                            p71_SequenceNr              = (p71_SequenceNr + 1) % 255
                            p71_CommandStatus           = 0     # successfully processed
                            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
                            p71_Data2                   = info[6]       # wind resistance coefficient
                            p71_Data3                   = info[7]       # wind speed
                            p71_Data4                   = info[8]       # drafting factor

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

                                #-----------------------------------------------
                                # Implemented when implementing Magnetic Brake:
                                # [-] grade is shifted with GradeShift (-10% --> 0) ]
                                # - then reduced with factor (can be re-adjusted with Virtual Gearbox)
                                # - and reduced with factorDH (for downhill only)
                                #
                                # GradeAdjust is valid for all configurations!
                                #
                                # GradeShift is not expected to be used anymore,
                                # and only left from earliest implementations
                                # to avoid it has to be re-introduced in future again.
                                #-----------------------------------------------
                                Grade += clv.GradeShift
                                Grade *= clv.GradeFactor
                                if Grade < 0: Grade *= clv.GradeFactorDH

                                TacxTrainer.SetGrade(Grade)
                                TacxTrainer.SetRollingResistance(RollingResistance)
                                PowerModeActive       = ''

                            # Update "last command" data in case page 71 is requested later
                            p71_LastReceivedCommandID   = DataPageNumber
                            # wrap around after 254 (255 = no command received)
                            p71_SequenceNr              = (p71_SequenceNr + 1) % 255
                            p71_CommandStatus           = 0     # successfully processed
                            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
                            p71_Data2                   = info[6]       # target grade (LSB)
                            p71_Data3                   = info[7]       # target grade (MSB)
                            p71_Data4                   = info[8]       # rolling resistance coefficient

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

                            elif RequestedPageNumber == 71:
                                info = ant.msgPage71_CommandStatus(ant.channel_FE, p71_LastReceivedCommandID, \
                                    p71_SequenceNr, p71_CommandStatus, p71_Data1, p71_Data2, p71_Data3, p71_Data4)

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
                    # Control Channel inputs
                    #-----------------------------------------------------------
                    if Channel == ant.channel_CTRL:
                        #-------------------------------------------------------
                        # Data page 73 (0x53) Generic Command
                        #-------------------------------------------------------
                        if   DataPageNumber == 73:
                            ctrl_SlaveSerialNumber, ctrl_SlaveManufacturerID, SequenceNr, ctrl_CommandNr =\
                                ant.msgUnpage73_GenericCommand(info)

                            # Update "last command" data in case page 71 is requested later
                            ctrl_p71_LastReceivedCommandID = DataPageNumber
                            ctrl_p71_SequenceNr = SequenceNr
                            ctrl_p71_CommandStatus = 0      # successfully processed
                            ctrl_p71_Data1 =  ctrl_CommandNr & 0x00ff
                            ctrl_p71_Data2 = (ctrl_CommandNr & 0xff00) >> 8
                            ctrl_p71_Data3 = 0xFF
                            ctrl_p71_Data4 = 0xFF

                            #---------------------------------------------------
                            # Commands should not overwrite, therefore stored
                            # in a table as tuples.
                            #---------------------------------------------------
                            ctrl_Commands.append((ctrl_SlaveManufacturerID, ctrl_SlaveSerialNumber, ctrl_CommandNr))
                            CommandName = ctrl.CommandName.get(ctrl_CommandNr, 'Unknown')
                            if debug.on(debug.Application):
                                logfile.Print(f"ANT+ Control {ctrl_SlaveManufacturerID} {ctrl_SlaveSerialNumber}: Received command {ctrl_CommandNr} = {CommandName} ")

                        # -------------------------------------------------------
                        # Data page 70 Request data page
                        # -------------------------------------------------------
                        elif DataPageNumber == 70:
                            _SlaveSerialNumber, _DescriptorByte1, _DescriptorByte2, \
                            _AckRequired, NrTimes, RequestedPageNumber, \
                            _CommandType = ant.msgUnpage70_RequestDataPage(info)

                            info = False
                            if RequestedPageNumber == 71:
                                info = ant.msgPage71_CommandStatus(ant.channel_CTRL, ctrl_p71_LastReceivedCommandID,
                                                                   ctrl_p71_SequenceNr, ctrl_p71_CommandStatus,
                                                                   ctrl_p71_Data1, ctrl_p71_Data2, ctrl_p71_Data3,
                                                                   ctrl_p71_Data4)
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
                        else: error = "Unknown Control data page"

                    #-----------------------------------------------------------
                    # Unknown channel
                    #-----------------------------------------------------------
                    else: error="Unknown channel"

                #---------------------------------------------------------------
                # BroadcastData = Master -> Slave
                #       channel_HRM_s = Heartbeat received from HRM
                #       channel_SCS_s = Speed/Cadence received from SCS
                #---------------------------------------------------------------
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
                # ChannelID - the info that a master on the network is paired
                #---------------------------------------------------------------
                elif id == ant.msgID_ChannelID:
                    Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                        ant.unmsg51_ChannelID(info)

                    if DeviceNumber == 0:   # No device paired, ignore
                        pass

                    elif Channel == ant.channel_HRM_s and DeviceTypeID == ant.DeviceTypeID_HRM:
                        AntHRMpaired = True
                        self.SetMessages(HRM='Heart Rate Monitor paired: %s' % DeviceNumber)

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
                    logfile.Write ("Tacx2Dongle; Processing time %5.3f is %5.3f longer than planned %5.3f (seconds)" % (ElapsedTime, SleepTime * -1, CycleTime) )
                pass

            EventCounter += 1           # Increment and ...
            EventCounter &= 0xff        # maximize to 255
            
    except KeyboardInterrupt:
        logfile.Console ("Stopped")
    #---------------------------------------------------------------------------
    # Stop devices, if not reconnecting ANT
    # - Create TCXexport
    # - Close  connection with bluetooth CTP
    # - Stop the Tacx trainer
    # - Inform user that ANT/BLE is deactivated
    #---------------------------------------------------------------------------
    if not AntDongle.DongleReconnected:
        if clv.exportTCX: tcx.Stop()
        if clv.ble:       bleCTP.Close()
        self.SetMessages(Dongle=AntDongle.Message + bleCTP.Message)
        TacxTrainer.SendToTrainer(True, usbTrainer.modeStop)
        logfile.Console (ActivationMsg.replace('activated', 'deactivated'))

    #---------------------------------------------------------------------------
    # Stop devices
    #---------------------------------------------------------------------------
    AntDongle.ResetDongle()

    return True
