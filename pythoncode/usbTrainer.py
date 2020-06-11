#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-09-11"
# 2020-06-10    Changed: Speed and Cadence Sensor metrics (PedalEchoCount)
# 2020-06-09    Changed: VirtualSpeed in clsSimulatedTrainer corrected
# 2020-06-08    Changed: clsTacxAntVortexTrainer uses TargetResistance, even 
#                   when expressed in Watts, so that also PowerFactor applies.
#                   Previously TargetPower was used directly, short-cutting
#                   this mechanism, only because Watts were needed.
#                   Now also Resistance is displayed, which usually equals
#                   TargetPower.
# 2020-05-27    Changed: SetGrade() limits Grade to -30...+30
#                        clsSimulatedTrainer improved
# 2020-05-24    Changed: logfile typo's
# 2020-05-20    Added: PedalEcho also simulated, for PedalStrokeAnalysis during
#               simulation, so that screen shots can be made for documentation.
# 2020-05-19    Changed: exception handling when loading firmware (issue #89)
# 2020-05-18    Changed: Some clode cleanup in clsTacxAntVortexTrainer
# 2020-05-15    Changed: self.AntDevice initialized in clsTacxAntVortexTrainer
# 2020-05-15    Added: logging for SetPower() and SetGrade(), 
#                    TargetPower2Resistance()
# 2020-05-14    Changed: Refresh() QuarterSecond added, mandatory fields
#                        clsTacxTrainer with __init__
#               Added:   HandleANTmessage + iVortex ANT handling done here
#               Virtual gearbox: 0.1 ... 3.0. 0.1 should be light enough.
# 2020-05-13    Minor code changes
#               Added: AddGrade(), SetRollingResistance(), SetWind()
#               Implemented VirtualSpeedKmh to realize the virtual gearbox
#               Flywheel changed as suggested by mattipee, totalreverse.
#                   Weight = self.UserAndBikeWeight in GradeMode
#                   totalreverse wiki updated 2020-01-04
#               Grade2Power according Gribble
# 2020-05-11    usbTrainer refactored for the following reasons:
#               - attributes are now stored in one place and not passed to
#                   functions and returned to callers; in the end it was
#                   unclear what values were changed where and by whome
#               - separate Tacx-dependant code into their own classes
#               - Enable further improvement on the Grade2Power
#                   algorithm in one separated location.
#               - Grade2Power() replaces Grade2Resistance() and is therefore
#                   immediatly usable for i-Vortex
#                   Power2Resistance() is for USB-connected trainers only
#               - Grade2Power() is brought back to the very basic, with a 
#                   formula based on physics and no additions.
#                   Ready for testing and -perhaps- finetuning.
#               - Introduction VirtualSpeedKmh (not yet finalized)
# 2020-05-07    pylint error free
# 2020-04-28    FortiusAntGui; only two constants imported (I do not want a link here with GUI)
# 2020-04-16    Write() replaced by Console() where needed
# 2020-04-15    Message changed "Connected to Tacx Trainer"
# 2020-04-12    Timeout-handling improved; Macintosh returns "timed out".
# 2020-04-07    SendToTrainer() also logs Mode-parameters
# 2020-03-29    ReceiveFromTrainer() returns Error="Not found"
#                   I'm finally rid of text in Speed causing errors!
# 2020-03-29    PowercurveFactor implemented to increment/decrement resistance
# 2020-03-29    .hex files in same folder as .py or .exe and correct path used
# 2020-03-23    Short received buffer for tt_FortiusSB extended to 64 bytes
# 2020-03-06    Resistance2Power and Power2Resistance
#                   implemented for iMagic, based upon Yegorvin's work.
# 2020-03-02    Speed = km/hr and only where required WheelSpeed is used.
# 2020-03-02    InitialiseTrainer() code moved into GetTrainer(); new interface
#               only
# 2020-02-27    GoldenCheetah calculations for LegacyProtocol used
# 2020-02-26    CalibrateSupported() added
#               For LegacyProtocol (iMagic) only modeResistance supported
#               trainer_types corrected (ref TotalReverse)
# 2020-02-25    feedback from fritz-hh implemented
# 2020-02-25    added:   idVendor_Tacx (I do not like constants in code)
#               changed: firmware command to be executed to be confirmed (fxload...)
#                        struct-definition: 'sc.no_alignment + ' added
#
# 2020-02-24    added: trainer_types defined (tt_) and iMagic added
#                      LegacyProtocol added
#               todo:  firmware command to be executed to be provided
#                      ReceiveFromTrainer() and SendToTrainer() defined according TotalReverse
#                      BUT: note '# To be investigated' comments!
#                      This version will not work bu I expect can be used
#                      for interface testing and further development.
# 2020-01-22    Error handling in GetTrainer() added (similar to GetDongle())
# 2020-01-15    Grade2Resistance() option3 tested and OK
# 2020-01-10    Test done at 200W and dropping cadence (100, 90...30)
#               resulting in explanation at Power2Resistance()
# 2020-01-08    Grade2Resistance() modified; test-version to be removed
# 2019-12-25    Target grade implemented; modes defined
#-------------------------------------------------------------------------------
import usb.core
import os
import random
import struct
import sys
import time

import antDongle         as ant
import debug
import logfile
import structConstants   as sc
from   FortiusAntGui                import mode_Power, mode_Grade
import FortiusAntCommand as cmd
import fxload

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
hu1902          = 0x1902    # Old "solid green" iMagic headunit (with or without firmware)
hu1904          = 0x1904    # New "white green" iMagic headunit (firmware inside)
hu1932          = 0x1932    # New "white blue" Fortius headunit (firmware inside)
hu1942          = 0x1942    # Old "solid blue" Fortius (firmware inside)
hue6be_nfw      = 0xe6be    # Old "solid blue" Fortius (without firmware)

idVendor_Tacx   = 0x3561

EnterButton     =  1
DownButton      =  2
UpButton        =  4
CancelButton    =  8
OKButton        = 16        # Non-existant for USB-trainers, for i-Vortex only

modeStop        = 0         # USB Tacx modes
modeResistance  = 2
modeCalibrate   = 3

#-------------------------------------------------------------------------------
# path to firmware files; since 29-3-2020 in same folder as .py or .exe
#-------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    dirname = sys._MEIPASS                     # pylint: disable=maybe-no-member
else:
    dirname = os.path.dirname(__file__)

imagic_fw  = os.path.join(dirname, 'tacximagic_1902_firmware.hex')
fortius_fw = os.path.join(dirname, 'tacxfortius_1942_firmware.hex')

#-------------------------------------------------------------------------------
# Class inheritance
# -----------------
# clsTacxTrainer                            = Base class with attributes
#       -> clsSimulatedTrainer              = Simulated trainer
#       -> clsTacxAntVortexTrainer          = Tacx i-Vortex
#       -> clsTacxUsbTrainer
#             -> clsTacxLegacyUsbTrainer    = Tacx iMagic
#             -> clsTacxNewUsbTrainer       = Tacx Fortius
#-------------------------------------------------------------------------------
# Class functions (more info in the classes)
# ------------------------------------------
# class clsTacxTrainer()
#     def GetTrainer(clv, AntDevice=None)
#
#     def ResetPowercurveFactor()                             # Virtual Gearbox
#     def SetPowercurveFactorUp()
#     def SetPowercurveFactorDown()
#   
#     def SetPower(Power)                                     # Store Power
#     def AddPower(deltaPower)
#     def SetGrade(Grade)                                     # Store Grade
#     def AddGrade(deltaGrade)
#     def SetRollingResistance(RollingResistance)
#     def SetWind()
#     def SetUserConfiguration(UserWeight, ...)               # Store User
#
#     def Refresh(QuarterSecond, TacxMode)                    # Receive, Calculate, Send
#     def SendToTrainer(QuarterSecond, TacxMode)              # To be defined by child class
#     def _ReceiveFromTrainer()                               # To be defined by child class
#     def TargetPower2Resistance()                            # To be defined by child class
#
#     def CalibrateSupported()                                # Return whether calibration supported
#
#     def _Grade2Power()                                      # Calculate required Power from Grade
#                                                             # This is where the magic is done!
#
# class clsSimulatedTrainer(clsTacxTrainer)
#     def Refresh(QuarterSecond, Tacxmode)                    # Randomize data (does not receive/send!)
#                                                             # Completely replaces parent.Refresh()
#
# class clsTacxAntVortexTrainer(clsTacxTrainer)
#     def Refresh(QuarterSecond, TacxMode)
#     def SendToTrainer(QuarterSecond, TacxMode)
#     def _ReceiveFromTrainer()
#     def TargetPower2Resistance()                            # Conversion TargetPower -> TargetResistance
#     def HandleANTmessage(message)
#
# class clsTacxUsbTrainer(clsTacxTrainer)
#     def Wheel2Speed()                                       # Convert Wheelspeed -> Kmh
#     def Speed2Wheel(SpeedKmh)                               # Convert Kmh --> Wheelspeed
#     def Refresh(QuarterSecond, TacxMode)                    # Add USB-special(s) to parent.Refresh()
#     def USB_Read()                                          # Read buffer from USB connected Tacx
#     def SendToTrainer(tacxMode)                             # Send buffer to   USB connected Tacx
#
# class clsTacxLegacyUsbTrainer(clsTacxUsbTrainer)
#     def TargetPower2Resistance()                            # Legacy conversion TargetPower -> TargetResistance
#     def CurrentResistance2Power()                           # Legacy conversion CurrentResistance -> CurrentPower
#     def SendToTrainerUSBData(TacxMode, ...)                 # Compose legacy buffer to be sent
#     def _ReceiveFromTrainer ()                              # Read and parse legacy data from trainer
#
# class clsTacxNewUsbTrainer(clsTacxUsbTrainer)
#     def TargetPower2Resistance()                            # New conversion TargetPower -> TargetResistance
#     def CurrentResistance2Power()                           # New conversion CurrentResistance -> CurrentPower
#     def SendToTrainerUSBData(TacxMode, ...)                 # Compose new buffer to be sent
#     def _ReceiveFromTrainer ()                              # Read and parse new data from trainer
#
#-------------------------------------------------------------------------------
# c l s T a c x T r a i n e r           The parent for all trainers
#-------------------------------------------------------------------------------
class clsTacxTrainer():
    UsbDevice               = None          # clsHeadUnitLegacy and clsHeadUnitNew only!
    AntDevice               = None          # clsVortexTrainer only!
    OK                      = False
    Message                 = None

    # Target provided by CTP (Trainer Road, Zwift, Rouvy, ...)
    # See Refresh() for dependencies
    TargetMode              = mode_Power    # Start with power mode
    TargetGrade             = 0             # no grade
    TargetPower             = 100           # and 100Watts
    TargetResistance        = 0             # calculated and input to trainer

    # Information provided by CTP
    BicycleWeight           = 10
    BicycleWheelDiameter    = None
    GearRatio               = None
    UserWeight              = 75
    UserAndBikeWeight       = 75 + 10       # defined according the standard (data page 51)

    RollingResistance       = 0.004
    WindResistance          = 0.51          # 1.275 * 0.4 * 1.0
    WindSpeed               = 0
    DraftingFactor          = 1.0

    # Information provided by _ReceiveFromTrainer()
    Axis                    = 0             # int
    Buttons                 = 0             # int
    Cadence                 = 0             # int
    CurrentPower            = 0             # int
    CurrentResistance       = 0             # int
    HeartRate               = 0             # int
    PedalEcho               = 0
    PreviousPedalEcho       = 0             # detection for PedalEcho=1
    PedalEchoCount          = 0             # count of PedalEcho=1 events
    PedalEchoTime           = time.time()   # the time of the last PedalEcho event
    SpeedKmh                = 0             # round(,1)
    VirtualSpeedKmh         = 0             #           see Grade_mode
    TargetResistanceFT      = 0             # int       Returned from trainer
    WheelSpeed              = 0             # int

    # Other general variables
    clv                     = None          # Command line variables
    PowercurveFactor        = 1             # 1.1 causes higher load
                                            # 0.9 causes lower load
                                            # Is manually set in Grademode
    Teeth                   = 15            # See Refresh()

    # USB devices only:
    Headunit                = 0             # The connected headunit in GetTrainer()
    Calibrate               = 0             # The value as established during calibration
    SpeedScale              = None          # To be set in sub-class

    def __init__(self, clv, Message):
        if debug.on(debug.Function):logfile.Write ("clsTacxTrainer.__init__()")
        self.clv             = clv
        self.Message         = Message
        self.OK              = False

    #---------------------------------------------------------------------------
    # G e t T r a i n e r
    #---------------------------------------------------------------------------
    # Function      Create a TacxTrainer-child class, depending on the 
    #               circumstances.
    #
    # Output        object.OK and object.Message
    #
    # Returns       Object of a TacxTrainer sub-class
    #---------------------------------------------------------------------------
    @staticmethod                       # pretent to be c++ factory function
    def GetTrainer(clv, AntDevice=None):
        if debug.on(debug.Function):logfile.Write ("clsTacxTrainer.GetTrainer()")

        #-----------------------------------------------------------------------
        # Usually I do not like multiple exit points, but here it's too handy
        #-----------------------------------------------------------------------
        if clv.SimulateTrainer: return clsSimulatedTrainer(clv)
        if clv.Tacx_iVortex:    return clsTacxAntVortexTrainer(clv, AntDevice)
            
        #-----------------------------------------------------------------------
        # So we are going to initialize USB
        # This may be either 'Legacy interface' or 'New interface'
        #-----------------------------------------------------------------------
        msg             = "No Tacx trainer found"
        hu              = None                      # TrainerType
        dev             = False
        LegacyProtocol  = False

        #-----------------------------------------------------------------------
        # Find supported trainer (actually we talk to a headunit)
        #-----------------------------------------------------------------------
        for hu in [hu1902, hu1904, hu1932, hu1942, hue6be_nfw]:
            try:
                if debug.on(debug.Function):
                    logfile.Write ("GetTrainer - Check for trainer %s" % (hex(hu)))
                dev = usb.core.find(idVendor=idVendor_Tacx, idProduct=hu)      # find trainer USB device
                if dev:
                    msg = "Connected to Tacx Trainer T" + hex(hu)[2:]          # remove 0x from result
                    if debug.on(debug.Data2 | debug.Function):
                        logfile.Print (dev)
                    break
            except Exception as e:
                if debug.on(debug.Function):
                    logfile.Write ("GetTrainer - " + str(e))

                if "AttributeError" in str(e):
                    msg = "GetTrainer - Could not find USB trainer: " + str(e)
                elif "No backend" in str(e):
                    msg = "GetTrainer - No backend, check libusb: " + str(e)
                else:
                    msg = "GetTrainer: " + str(e)

        #-----------------------------------------------------------------------
        # Initialise trainer (if found)
        #-----------------------------------------------------------------------
        if not dev:
            hu  = 0
            dev = False
        else:                                                  # found trainer
            #-------------------------------------------------------------------
            # iMagic             As defined together with fritz-hh and jegorvin)
            #-------------------------------------------------------------------
            if hu == hu1902:
                LegacyProtocol = True
                logfile.Console ("Initialising head unit T1902 (iMagic), please wait 5 seconds")
                logfile.Console (imagic_fw)   # Hint what may be wrong if absent
                try:
                    fxload.loadHexFirmware(dev, imagic_fw)
                except Exception as e:                         # file not found?
                    msg = "GetTrainer: " + str(e)
                    dev = False
                else:
                    time.sleep(5)
                    msg = "T1902 head unit initialised (iMagic)"

            #-------------------------------------------------------------------
            # unintialised Fortius (as provided by antifier original code)
            #-------------------------------------------------------------------
            if hu == hue6be_nfw:
                logfile.Console ("Initialising head unit T1942 (Fortius), please wait 5 seconds")
                logfile.Console (fortius_fw)  # Hint what may be wrong if absent
                try:
                    fxload.loadHexFirmware(dev, fortius_fw)
                except Exception as e:                         # file not found?
                    msg = "GetTrainer: " + str(e)
                    dev = False
                else:
                    time.sleep(5)
                    dev = usb.core.find(idVendor=idVendor_Tacx, idProduct=hu1942)
                    if dev != None:
                        msg = "T1942 head unit initialised (Fortius)"
                        hu = hu1942
                    else:
                        msg = "GetTrainer - Unable to load firmware"
                        dev = False

            #-------------------------------------------------------------------
            # Set configuration
            #-------------------------------------------------------------------
            if dev != False:
                dev.set_configuration()
                if hu == hu1902:
                    dev.set_interface_altsetting(0, 1)

            #-------------------------------------------------------------------
            # InitialiseTrainer (will not read cadence until init str is sent)
            #-------------------------------------------------------------------
            if dev != False and LegacyProtocol == False:
                data = struct.pack (sc.unsigned_int, 0x00000002)
                if debug.on(debug.Data2):
                    logfile.Write ("InitialiseTrainer data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
                dev.write(0x02,data)

        #-----------------------------------------------------------------------
        # Done
        #-----------------------------------------------------------------------
        logfile.Console(msg)
        if debug.on(debug.Function):
            logfile.Write ("GetTrainer() returns, trainertype=" + hex(hu))

        #-----------------------------------------------------------------------
        # Return the correct Object
        #-----------------------------------------------------------------------
        if dev != False:
            if LegacyProtocol:
                return clsTacxLegacyUsbTrainer(clv, msg, hu, dev)
            else:
                return clsTacxNewUsbTrainer(clv, msg, hu, dev)
        else:
            return clsTacxTrainer (clv, msg)           # where .OK = False

    #---------------------------------------------------------------------------
    # Functions from external to provide data
    #
    # PowercurveFactor:
    # 10% steps insprired by 10-11-12...36-40-44 cassettes.
    # 0.1 ... 3 is arbitrary, where lowerbound 0 is definitely no good idea.
    #---------------------------------------------------------------------------
    def ResetPowercurveFactor(self):
        self.PowercurveFactor   = 1

    def SetPowercurveFactorUp(self):
        if self.PowercurveFactor < 3:
            self.PowercurveFactor   *= 1.1

    def SetPowercurveFactorDown(self):
        if self.PowercurveFactor > 0.1:
            self.PowercurveFactor   /= 1.1

    def SetPower(self, Power):
        if debug.on(debug.Function):logfile.Write ("SetPower(%s)" % Power)
        self.TargetMode         = mode_Power
        self.TargetGrade        = 0
        self.TargetPower        = Power
        self.TargetResistance   = 0             # .Refresh() must be called

    def AddPower(self, deltaPower):
        self.SetPower(self.TargetPower + deltaPower)

    def SetGrade(self, Grade):
        if debug.on(debug.Function):  logfile.Write   ("SetGrade(%s)" % Grade)
        if Grade < -30 or Grade > 30: logfile.Console ("Grade limitted to range -30 ... 30")
        if Grade >  30: Grade =  30
        if Grade < -30: Grade = -30

        self.TargetMode         = mode_Grade
        self.TargetGrade        = Grade
        self.TargetPower        = 0             # .Refresh() must be called
        self.TargetResistance   = 0             # .Refresh() must be called

    def AddGrade(self, deltaGrade):
        self.SetGrade(self.TargetGrade + deltaGrade)
    
    def SetRollingResistance(self, RollingResistance):
        if debug.on(debug.Function):
            logfile.Write ("SetRollingResistance(%s[def=0.004])" % RollingResistance)

        self.RollingResistance = RollingResistance

    def SetWind(self, WindResistance, WindSpeed, DraftingFactor):
        if debug.on(debug.Function):
            logfile.Write ("SetWind(%s[def=0.51], %s[def=0], %s[def=1])" % 
                (WindResistance, WindSpeed, DraftingFactor) )

        self.WindResistance = WindResistance
        self.WindSpeed      = WindSpeed
        self.DraftingFactor = DraftingFactor

    def SetUserConfiguration(self, UserWeight, BicycleWeight, BicycleWheelDiameter, GearRatio):
        self.BicycleWeight          = BicycleWeight
        self.BicycleWheelDiameter   = BicycleWheelDiameter
        self.GearRatio              = GearRatio
        self.UserWeight             = UserWeight
        self.UserAndBikeWeight      = UserWeight + BicycleWeight

    #---------------------------------------------------------------------------
    # SendToTrainer() and ReceivedFromTrainer() to be defined by sub-class
    #---------------------------------------------------------------------------
    def SendToTrainer(self, QuarterSecond, TacxMode):   # no return
        pass
    def _ReceiveFromTrainer(self):                      # No return
        pass
    def TargetPower2Resistance(self):
        self.TargetResistance = 0                    # child class must redefine

    #---------------------------------------------------------------------------
    # R e f r e s h
    #---------------------------------------------------------------------------
    # Input         Class variables Target***
    #               QuarterSecond, indicates that 1/4 second since previous
    #                              for ANTdevices only
    #               TacxMode, to pass to SendToTrainer()
    #
    # Function      Refresh updates the actual values from the trainer
    #               Then does required calculations
    #               And finally instructs the trainer what to do
    #
    #               It appears more logical to do calculations when inputs change
    #               but it's done here because some calculations depend on the
    #               wheelspeed, so must be redone after each _ReceiveFromTrainer()
    #
    # Output        Class variables match with Target***
    #---------------------------------------------------------------------------
    def Refresh(self, QuarterSecond, TacxMode):
        if debug.on(debug.Function):logfile.Write ( \
                    'clsTacxTrainer.Refresh(%s, %s)' % (QuarterSecond, TacxMode))
        #-----------------------------------------------------------------------
        # FIrst get data from the trainer
        #-----------------------------------------------------------------------
        self._ReceiveFromTrainer()

        #-----------------------------------------------------------------------
        # Make all variables consistent
        #-----------------------------------------------------------------------

        #-----------------------------------------------------------------------
        # PedalEcho for Speed and Cadence Sensor
        #-----------------------------------------------------------------------
        if self.PedalEcho == 1 and self.PreviousPedalEcho == 0:
            self.PedalEchoCount += 1
            self.PedalEchoTime   = time.time()
        self.PreviousPedalEcho = self.PedalEcho

        #-----------------------------------------------------------------------
        # Calculate Virtual speed applying the digital gearbox
        # if DOWN has been pressed, we pretend to be riding slower than the
        #       trainer wheel rotates
        # if UP has been pressed, we pretend to be faster than the trainer
        #
        # Note that Grade2Power() depends on the VirtualSpeed.
        #-----------------------------------------------------------------------
        self.VirtualSpeedKmh = self.SpeedKmh * self.PowercurveFactor

        # No negative value defined for ANT message Page25 (#)
        if self.CurrentPower < 0: self.CurrentPower = 0 

        assert (self.TargetMode in (mode_Power, mode_Grade))
        if self.TargetMode == mode_Power:
            pass

        elif self.TargetMode == mode_Grade:
            self._Grade2Power()

        #-----------------------------------------------------------------------
        # For all modes: To be implemented by USB-trainers; pass for others
        #-----------------------------------------------------------------------
        self.TargetPower2Resistance()

        #-----------------------------------------------------------------------
        # Antifier's calibration; valid for USB devices only
        #                         non-USB classes will set PowerFactor=1
        #
        # The idea is that Power2Resistance gives insufficient resistance
        # and that the formula can be corrected with the PowerFactor.
        # Therefore before Send:
        #       the TargetResistance is multiplied by factor
        # and after Receive:
        #       the CurrentResistance and CurrentPower are divided by factor
        # Just for antifier upwards compatibility; usage unknown.
        #-----------------------------------------------------------------------
        if self.clv.PowerFactor:
            self.TargetResistance  *= self.clv.PowerFactor  # Will be sent

            self.CurrentResistance /= self.clv.PowerFactor  # Was just received
            self.CurrentPower      /= self.clv.PowerFactor  # Was just received

        # ----------------------------------------------------------------------
        # Round after all these calculations
        # ----------------------------------------------------------------------
        self.TargetPower         = int(self.TargetPower)
        self.TargetResistance    = int(self.TargetResistance)
        self.CurrentResistance   = int(self.CurrentResistance)
        self.CurrentPower        = int(self.CurrentPower)
        self.SpeedKmh            = round(self.SpeedKmh,1)
        self.VirtualSpeedKmh     = round(self.VirtualSpeedKmh,1)

        # ----------------------------------------------------------------------
        # Show the virtual cassette, calculated from a 10 teeth sprocket
        # If PowercurveFactor = 1  : 15 teeth
        # If PowercurveFactor = 0.9: 14 teeth
        # Limit of PowercurveFactor is done at the up/down button
        # 15 is choosen so that when going heavier, first 14,12,11 teeth is
        #     shown. Numbers like 5,4,3 would be irrealistic in real world.
        #     Of course the number of teeth is a reference number.
        #
        # Set FortiusAntGui.py OnPaint() for details.
        #       PowercurveFactor = 0.1 = 150 teeth
        #       PowercurveFactor = 0.5 =  30 teeth
        #       PowercurveFactor = 1.0 =  15 teeth
        #       PowercurveFactor = 2.0 =   8 teeth
        #       PowercurveFactor = 3.0 =   5 teeth
        # ----------------------------------------------------------------------
        self.Teeth = int(15 / self.PowercurveFactor)
            
        #-----------------------------------------------------------------------
        # Then send the results to the trainer again
        #-----------------------------------------------------------------------
        self.SendToTrainer(QuarterSecond, TacxMode)

    #---------------------------------------------------------------------------
    # C a l i b r a t e S u p p o r t e d
    #---------------------------------------------------------------------------
    # input     self.tt
    #
    # function  Return whether this trainer support calibration
    #
    # returns   True/False
    #---------------------------------------------------------------------------
    def CalibrateSupported(self):
        if self.Headunit == hu1932:                 # And perhaps others as well
            return True
        else:
            return False

    #---------------------------------------------------------------------------
    # Convert G r a d e T o P o w e r           |  Grade = slope
    #---------------------------------------------------------------------------
    # TotalReverse:
    #   documents:      LOAD ~= (slope (in %) - 0.4) * 650
    #   ttyT1941.py:    SlopeScale =  2 * 5 * 130    = 1300
    #                   commented  = 13 * 5 * 10 * 5 = 3250
    #
    # TotalReverse, Issue #2:
    # ANT+ describes a simple physical model:
    #   Total resistance [N] = Gravitational Resistance + Rolling Resistance + Wind Resistance
    # Gravitational Resistance [N] = (Equipment Mass + User Mass) x Grade(%)/100 x 9.81
    # With the assumption of a total weight of about 80 kg and without rolling and wind
    # resistance together with the simple assumption
    # Load = Force [N] * 137 (the result of a fitting in ergo mode) one get:
    #
    # Load = 137 * 80 * 9.81 * slope_in_percent / 100
    #
    # SlopeScale = 137 * 80 * 9.81 / 100 = 1075
    #
    # Tests:
    # factor 650 causes Zwift to think we ride @ 20km/h where the wheel runs at 40km/hr
    # factor 1300 to be tested
    #
    #---------------------------------------------------------------------------
    # Refer to ANT msgUnpage51_TrackResistance()
    #          where zwift grade does not seem to match the definition
    #---------------------------------------------------------------------------
    # Input         TargetGrade, UserAndBikeWeight, SpeedKmh
    #
    # Function      Calculate what power must be produced, given the current
    #               grade, speed and weigth
    # 
    # Output        TargetPower
    #---------------------------------------------------------------------------
    def _Grade2Power(self):                                       #Grade2Power#
        if self.UserAndBikeWeight < 70:
            self.UserAndBikeWeight = 75 + 10

        self.__Grade2Power_Gribble()

        if debug.on(debug.Function):
            logfile.Write ("Grade2Power (TargetGrade=%4.1f%%, Speed=%4.1f, Weight=%3.0f, rR=%s, wR=%s, wS=%s, d=%s) = TargetPower=%3.0fW" % \
                (self.TargetGrade, self.VirtualSpeedKmh, self.UserAndBikeWeight, \
                self.RollingResistance, self.WindResistance, self.WindSpeed, self.DraftingFactor, \
                 self.TargetPower) )

    #---------------------------------------------------------------------------
    # www.gribble.org
    #---------------------------------------------------------------------------
    def __Grade2Power_Gribble(self):
        #-----------------------------------------------------------------------
        # Matthew updates according www.gribble.org
        # See: https://www.gribble.org/cycling/power_v_speed.html
        #-----------------------------------------------------------------------
        c     = self.RollingResistance              # default=0.004
        m     = self.UserAndBikeWeight              # default=75+10 kg
        g     = 9.81                                # m/s2
        v     = self.VirtualSpeedKmh / 3.6          # m/s   km/hr * 1000 / 3600
        Proll = c * m * g * v                       # Watt

        p_cdA = self.WindResistance                 # default=0.51
        w     = self.WindSpeed / 3.6                # default=0
        d     = self.DraftingFactor                 # default=1
        Pair  = 0.5 * p_cdA * (v+w) * (v+w) * d * v # Watt

        i     = self.TargetGrade                    # Percentage 0...100
        Pslope= i/100 * m * g * v                   # Watt

        self.TargetPower = int(Proll + Pair + Pslope)

    #---------------------------------------------------------------------------
    # www.fiets.nl
    #---------------------------------------------------------------------------
    def __Grade2Power_FietsNL(self):
        #-----------------------------------------------------------------------
        # Thanks to https://www.fiets.nl/2016/05/02/de-natuurkunde-van-het-fietsen/
        # Required power = roll + air + slope + mechanical
        #-----------------------------------------------------------------------
        c     = self.RollingResistance          # roll-resistance constant
        m     = self.UserAndBikeWeight          # kg
        g     = 9.81                            # m/s2
        v     = self.VirtualSpeedKmh / 3.6      # m/s       km/hr * 1000 / 3600
        Proll = c * m * g * v                   # Watt

        p     = 1.205                           # air-density
        cdA   = 0.3                             # resistance factor
                                                # p_cdA = 0.375
        w     =  0                              # wind-speed
        Pair  = 0.5 * p * cdA * (v+w)*(v+w)* v  # Watt

        i     = self.TargetGrade                # Percentage 0...100
        Pslope= i/100 * m * g * v               # Watt

        Pbike = 37

        self.TargetPower = int(Proll + Pair + Pslope + Pbike)

#-------------------------------------------------------------------------------
# c l s S i m u l a t e d T r a i n e r
#-------------------------------------------------------------------------------
# Simulate Tacx-trainer
#-------------------------------------------------------------------------------
class clsSimulatedTrainer(clsTacxTrainer):
    def __init__(self, clv):
        super().__init__(clv, "Simulated Tacx Trainer to test ANT-interface")
        if debug.on(debug.Function):logfile.Write ("clsSimulatedTrainer.__init__()")
        self.OK              = True
        self.clv.PowerFactor = 1            # Not applicable for simulation

    # --------------------------------------------------------------------------
    # R e f r e s h
    # --------------------------------------------------------------------------
    # input:        self.TargetPower
    #
    # Description:  Basically, values are set so that no trainer-interface is needed
    #               Especially, to be able to test without the trainer being active
    #
    #               Just for fun, generate values based upon what the trainer
    #               program wants so that a live simulation can be generated.
    #               For example to make a video without pedalling.
    #
    #               The CurrentPower smoothly adjust to TargetPower
    #               The HeartRate follows the CurrentPower produced
    #               The Cadence is floating around 100
    #               The Speed follows the Cadence
    #
    # Output:       self.* variables, see next 10 lines
    # --------------------------------------------------------------------------
    def Refresh (self, _QuarterSecond=None, _TacxMode=None):
        if debug.on(debug.Function):logfile.Write ("clsSimulatedTrainer.Refresh()")
        # ----------------------------------------------------------------------
        # Trigger for pedalstroke analysis (PedalEcho)
        # Data for Speed and Cadence Sensor (-Time and -Count)
        # ----------------------------------------------------------------------
        if self.Cadence and (time.time() - self.PedalEchoTime) > 60 / self.Cadence:
            self.PedalEchoTime   = time.time()
            self.PedalEcho       = 1
            self.PedalEchoCount += 1
        else:
            self.PedalEcho       = 0

        # ----------------------------------------------------------------------
        # Randomize figures
        # ----------------------------------------------------------------------
        self.Axis               = 0
        self.Buttons            = 0
        self.TargetResistance   = 2345

        if self.TargetMode == mode_Grade:
            self._Grade2Power()

        if False or self.TargetPower < 10:   # Return fixed value
            self.SpeedKmh    = 34.5
            self.HeartRate   = 135
            self.CurrentPower= 246
            self.Cadence     = 113
        else:                           # Return animated value
                                        # Using this setting, you let TrainerRoad and FortiusANT play together
                                        # and sip a beer yourself :-)
            HRmax       = 180
            ftp         = 246   # at 80% HRmax

            deltaPower    = (self.TargetPower - self.CurrentPower)
            if deltaPower < 8:
                self.CurrentPower = self.TargetPower
                deltaPower        = 0
            else:
                self.CurrentPower = self.CurrentPower + deltaPower / 8          # Step towards TargetPower
            self.CurrentPower *= (1 + random.randint(-3,3) / 100)               # Variation of 5%

            self.Cadence       = 100 - min(10, deltaPower) / 10                 # Cadence drops when Target increases
            self.Cadence      *= (1 + random.randint(-2,2) / 100)               # Variation of 2%

            self.SpeedKmh      = 35 * self.Cadence / 100                        # Speed is 35 kmh at cadence 100 (My highest gear)

            self.HeartRate     = HRmax * (0.5 + ((self.CurrentPower - 100) / (ftp - 100) ) * 0.3)
                                                                                # As if power is linear with power
                                                                                # 100W is reached at 50%
                                                                                # ftp  is reached at 80%
                                                                                # Assume lineair between 100W and ftp
            if self.HeartRate < HRmax * 0.5: self.HeartRate = HRmax * 0.5       # minimize HR
            if self.HeartRate > HRmax:       self.HeartRate = HRmax             # maximize HR
            self.HeartRate    += random.randint(-5,5)                           # Variation of heartrate by 5 beats

        self.VirtualSpeedKmh= self.SpeedKmh

#-------------------------------------------------------------------------------
# c l s T a c x A n t V o r t e x T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with ANT connection
# Actually, only the data-storage and Refresh() with Grade2Power() is used!
#-------------------------------------------------------------------------------
class clsTacxAntVortexTrainer(clsTacxTrainer):
    def __init__(self, clv, AntDevice):
        super().__init__(clv, "Pair with Tacx i-Vortex and Headunit")
        if debug.on(debug.Function):logfile.Write ("clsTacxAntVortexTrainer.__init__()")
        self.AntDevice         = AntDevice
        self.OK                = True           # The AntDevice is there,
                                                # the trainer not yet paired!

        self.__ResetTrainer()

    def __ResetTrainer(self):
        self.__AntVTXpaired    = False
        self.__AntVHUpaired    = False
        self.__DeviceNumberVTX = 0              # provided by CHANNEL_ID msg
        self.__DeviceNumberVHU = 0

        self.__Cadence         = 0              # provided by datapage 0
        self.__CurrentPower    = 0
        self.__WheelSpeed      = 0
        self.__SpeedKmh        = 0              #     (from WheelSpeed)

        self.__VortexID        = 0              # provided by datapage 3

        self.__iVortexButtons  = 0              # provided by datapage 221

        self.Message = 'Pair with Tacx i-Vortex and Headunit'

    #---------------------------------------------------------------------------
    # R e c e i v e F r o m T r a i n e r
    #---------------------------------------------------------------------------
    # input     __data as collected by HandleANTmessage
    #
    # function  Now provide data to TacxTrainer
    #
    # returns   Buttons, Cadence, CurrentPower, SpeedKmh, Message
    #
    #           NOT: HeartRate, TargetResistance, CurrentResistance, PedalEcho
    #                WheelSpeed
    #---------------------------------------------------------------------------
    def _ReceiveFromTrainer(self):
        # ----------------------------------------------------------------------
        # Data provided by data pages
        # ----------------------------------------------------------------------
        self.Cadence      = self.__Cadence
        self.CurrentPower = self.__CurrentPower
        self.WheelSpeed   = self.__WheelSpeed

#       self.SpeedKmh     = round( self.WheelSpeed / ( 100 * 1000 / 3600 ), 1)
        self.SpeedKmh     = self.WheelSpeed / 10    # Speed = in 0.1 km/hr

        # ----------------------------------------------------------------------
        # Translate i-Vortex buttons to TacxTrainer.Buttons.
        # Mapping according TotalReverse:
        # https://github.com/totalreverse/ttyT1941/issues/9#issuecomment-624360140
        # ----------------------------------------------------------------------
        if   self.__iVortexButtons == 0: self.Buttons = 0
        elif self.__iVortexButtons == 1: self.Buttons = CancelButton # Left 
        elif self.__iVortexButtons == 2: self.Buttons = UpButton
        elif self.__iVortexButtons == 3: self.Buttons = OKButton
        elif self.__iVortexButtons == 4: self.Buttons = DownButton
        elif self.__iVortexButtons == 5: self.Buttons = EnterButton  # Right
        self.__iVortexButtons = 0

        # ----------------------------------------------------------------------
        # Compose displayable message
        # ----------------------------------------------------------------------
        if self.__DeviceNumberVTX:
            self.Message = 'Tacx i-Vortex paired: %s' % self.__DeviceNumberVTX
        else:
            self.Message = "Pair with Tacx i-Vortex"

        if self.__DeviceNumberVHU:
            self.Message += ', Headunit: %s' % self.__DeviceNumberVHU
        else:
            self.Message += ', Headunit'

        if not (self.__DeviceNumberVTX and self.__DeviceNumberVHU):
            self.Message += ' (pairing can take a minute)'

    #---------------------------------------------------------------------------
    # SendToTrainer()
    #---------------------------------------------------------------------------
    def SendToTrainer(self, QuarterSecond, TacxMode):
        if TacxMode == modeStop:
            self.__ResetTrainer()                       # Must be paired again!

        if QuarterSecond:
            messages = []
            if TacxMode ==  modeResistance:
                #---------------------------------------------------------------
                # Set target power
                # TargetResistance is used, so that virtual gearbox works!
                #---------------------------------------------------------------
                if self.__AntVTXpaired and self.__VortexID:
                    info = ant.msgPage16_TacxVortexSetPower (ant.channel_VTX_s, \
                                self.__VortexID, self.TargetResistance)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                    messages.append ( msg )

                #---------------------------------------------------------------
                # Avoid power off on headunit
                #---------------------------------------------------------------
                if self.__AntVHUpaired:
                    info = ant.msgPage000_TacxVortexHU_StayAlive (ant.channel_VHU_s)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                    messages.append ( msg )

            elif TacxMode ==  modeStop:
                #---------------------------------------------------------------
                # Switch headunit to trainer control mode
                #---------------------------------------------------------------
                if self.__AntVHUpaired:
                    info = ant.msgPage172_TacxVortexHU_ChangeHeadunitMode (\
                                              ant.channel_VHU_s, ant.VHU_Normal)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                    messages.append ( msg )

            #-------------------------------------------------------------------
            # Send messages, leave receiving to the outer loop
            #-------------------------------------------------------------------
            if messages:
                self.AntDevice.Write(messages, False, False)

    #---------------------------------------------------------------------------
    # TargetPower2Resistance
    #
    # TargetResistance is used for the i-Vortex, even when expressed in Watt, so
    # that PowerFactor and PowercurveFactor apply; see clsUsbTrainer.Refresh().
    #---------------------------------------------------------------------------
    def TargetPower2Resistance(self):
        self.TargetResistance = self.TargetPower

    #---------------------------------------------------------------------------
    # Refresh()
    # No special actions required
    # Note that TargetResistance=0 for the i-Vortex; TargetPower is sent!
    #---------------------------------------------------------------------------
    # def Refresh(self, QuarterSecond, TacxMode):
    #     super().Refresh(QuarterSecond, TacxMode)
    #     if debug.on(debug.Function):logfile.Write ("clsTacxAntVortexTrainer.Refresh()")
    #     pass

    #---------------------------------------------------------------------------
    # HandleANTmessage()
    #---------------------------------------------------------------------------
    def HandleANTmessage(self, msg):
        _synch, _length, id, info, _checksum, _rest, Channel, DataPageNumber = \
                                                       ant.DecomposeMessage(msg)
        dataHandled = False
        messages    = []
        #-----------------------------------------------------------------------
        # VTX_s = Tacx i-Vortex trainer
        #-----------------------------------------------------------------------
        if Channel == ant.channel_VTX_s:
            if id == ant.msgID_AcknowledgedData:
                dataHandled = True

            #-------------------------------------------------------------------
            # BroadcastData - info received from the master device
            #-------------------------------------------------------------------
            elif id == ant.msgID_BroadcastData:
                #---------------------------------------------------------------
                # Ask what device is paired
                #---------------------------------------------------------------
                if not self.__AntVTXpaired:
                    msg = ant.msg4D_RequestMessage(ant.channel_VTX_s, ant.msgID_ChannelID)
                    messages.append ( msg )

                #---------------------------------------------------------------
                # Data page 00 msgUnpage00_TacxVortexDataSpeed
                #---------------------------------------------------------------
                if DataPageNumber == 0:
                    dataHandled = True
                    VTX_UsingVirtualSpeed, self.__CurrentPower, self.__WheelSpeed, \
                        VTX_CalibrationState, self.__Cadence = \
                        ant.msgUnpage00_TacxVortexDataSpeed(info)
                    if debug.on(debug.Function):
                        logfile.Write ('i-Vortex Page=%s UsingVirtualSpeed=%s Power=%s Speed=%s State=%s Cadence=%s' % \
                            (DataPageNumber, VTX_UsingVirtualSpeed, self.__CurrentPower, \
                                self.__SpeedKmh, VTX_CalibrationState, self.__Cadence) )

                #---------------------------------------------------------------
                # Data page 01 msgUnpage01_TacxVortexDataSerial
                #---------------------------------------------------------------
                elif DataPageNumber == 1:
                    dataHandled = True
                    VTX_S1, VTX_S2, VTX_Serial, VTX_Alarm = ant.msgUnpage01_TacxVortexDataSerial(info)
                    if debug.on(debug.Function):
                        logfile.Write ('i-Vortex Page=%s S1=%s S2=%s Serial=%s Alarm=%s' % \
                            (DataPageNumber, VTX_S1, VTX_S2, VTX_Serial, VTX_Alarm) )

                #---------------------------------------------------------------
                # Data page 02 msgUnpage02_TacxVortexDataVersion
                #---------------------------------------------------------------
                elif DataPageNumber == 2:
                    dataHandled = True
                    VTX_Major, VTX_Minor, VTX_Build = ant.msgUnpage02_TacxVortexDataVersion(info)
                    if debug.on(debug.Function):
                        logfile.Write ('i-Vortex Page=%s Major=%s Minor=%s Build=%s' % \
                            (DataPageNumber, VTX_Major, VTX_Minor, VTX_Build))

                #---------------------------------------------------------------
                # Data page 03 msgUnpage03_TacxVortexDataCalibration
                #---------------------------------------------------------------
                elif DataPageNumber == 3:
                    dataHandled = True
                    VTX_Calibration, self.__VortexID = ant.msgUnpage03_TacxVortexDataCalibration(info)
                    if debug.on(debug.Function):
                        logfile.Write ('i-Vortex Page=%s Calibration=%s VortexID=%s' % \
                            (DataPageNumber, VTX_Calibration, self.__VortexID))

            #-------------------------------------------------------------------
            # ChannelID - the info that a master on the network is paired
            #-------------------------------------------------------------------
            elif id == ant.msgID_ChannelID:
                Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                    ant.unmsg51_ChannelID(info)

                if DeviceTypeID == ant.DeviceTypeID_VTX:
                    dataHandled = True
                    self.__AntVTXpaired    = True
                    self.__DeviceNumberVTX = DeviceNumber

            #-------------------------------------------------------------------
            # Outer loop does not need to handle channel_VTX_s messages
            #-------------------------------------------------------------------
            dataHandled = True

        #-----------------------------------------------------------------------
        # VHU_s = Tacx i-Vortex headunit
        #-----------------------------------------------------------------------
        elif Channel == ant.channel_VHU_s:
            if id == ant.msgID_AcknowledgedData:
                #---------------------------------------------------------------
                # Data page 221 TacxVortexHU_ButtonPressed
                #---------------------------------------------------------------
                if DataPageNumber == 221:
                    dataHandled = True
                    self.__iVortexButtons = \
                              ant.msgUnpage221_TacxVortexHU_ButtonPressed (info)

            #-------------------------------------------------------------------
            # BroadcastData - info received from the master device
            #-------------------------------------------------------------------
            elif id == ant.msgID_BroadcastData:
                #---------------------------------------------------------------
                # Ask what device is paired
                #---------------------------------------------------------------
                if not self.__AntVHUpaired:
                    msg = ant.msg4D_RequestMessage(ant.channel_VHU_s, ant.msgID_ChannelID)
                    messages.append ( msg )

                #---------------------------------------------------------------
                # Data page 173 frames containing the serial number of the device
                #---------------------------------------------------------------
                if DataPageNumber == 173: # 0xad:
                    dataHandled = True

            #-------------------------------------------------------------------
            # ChannelID - the info that a master on the network is paired
            #-------------------------------------------------------------------
            elif id == ant.msgID_ChannelID:
                Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                    ant.unmsg51_ChannelID(info)

                if DeviceTypeID == ant.DeviceTypeID_VHU:
                    dataHandled = True
                    self.__AntVHUpaired    = True
                    self.__DeviceNumberVHU = DeviceNumber

                    #-----------------------------------------------------------
                    # And tell to switch to PC-mode
                    #-----------------------------------------------------------
                    info = ant.msgPage172_TacxVortexHU_ChangeHeadunitMode (\
                                             ant.channel_VHU_s, ant.VHU_PCmode)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                    messages.append ( msg )

            #-------------------------------------------------------------------
            # Outer loop does not need to handle channel_VHU_s messages
            #-------------------------------------------------------------------
            dataHandled = True

        #-----------------------------------------------------------------------
        # Send messages, leave receiving to the outer loop
        #-----------------------------------------------------------------------
        if messages:
            self.AntDevice.Write(messages, False, False)

        return dataHandled

#-------------------------------------------------------------------------------
# c l s T a c x U s b T r a i n e r
#-------------------------------------------------------------------------------
class clsTacxUsbTrainer(clsTacxTrainer):
    #---------------------------------------------------------------------------
    # Convert WheelSpeed --> Speed in km/hr
    # SpeedScale must be defined in sub-class
    #---------------------------------------------------------------------------
    # WheelSpeed = 1 mm/sec <==> 1.000.000 / 3600 km/hr = 1/278 km/hr
    # TotalReverse: Other implementations are using values between 1/277 and 1/360.
    # A practical test shows that Cadence=92 gives 40km/hr at a given ratio
    #		factor 289.75 gives a slightly higher speed
    #		factor 301 would be good (8-11-2019)
    #---------------------------------------------------------------------------
    def Wheel2Speed(self):
        self.SpeedKmh = round(self.WheelSpeed / self.SpeedScale, 1)

    def Speed2Wheel(self, SpeedKmh):
        return int(SpeedKmh * self.SpeedScale)
    
    #---------------------------------------------------------------------------
    # Refresh()
    #---------------------------------------------------------------------------
    def Refresh(self, QuarterSecond, TacxMode):
        super().Refresh(QuarterSecond, TacxMode)
        if debug.on(debug.Function):logfile.Write ("clsTacxUsbTrainer.Refresh()")

        # ----------------------------------------------------------------------
        # When a button is pressed, the button is returned a number of times,
        # depending on the polling-frequency. The caller would receive the same
        # button multiple times.
        # Therefore we poll the trainer untill "no button" received, only if
        # the last receive provided Buttons.
        # ----------------------------------------------------------------------
        Buttons = self.Buttons                  # Remember the buttons pressed

        while self.Buttons:                     # Loop untill no button pressed
            time.sleep(0.1)
            self._ReceiveFromTrainer()

        self.Buttons = Buttons                  # Restore buttons
    #---------------------------------------------------------------------------
    # U S B _ R e a d
    #---------------------------------------------------------------------------
    # input     UsbDevice
    #
    # function  Read data from Tacx USB trainer
    #
    # returns   data
    #---------------------------------------------------------------------------
    def USB_Read(self):
        data = ""
        try:
            data = self.UsbDevice.read(0x82, 64, 30)
        except TimeoutError:
            pass
        except Exception as e:
            if "timeout error" in str(e) or "timed out" in str(e): # trainer did not return any data
                pass
            else:
                logfile.Console("Read from USB trainer error: " + str(e))
        if debug.on(debug.Data2):
            logfile.Write ("Trainer recv data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
        
        return data

    #---------------------------------------------------------------------------
    # S e n d T o T r a i n e r
    #---------------------------------------------------------------------------
    # input     UsbDevice, TacxMode
    #           if Mode=modeResistance:  TargetResistance
    #
    #           PedalEcho   - must be echoed
    #           Calibrate   - Resistance during calibration is specified
    #                         If =zero default is calculated
    #
    # function  Set trainer to calculated resistance (TargetPower or TargetGrade)
    #
    # returns   None
    #---------------------------------------------------------------------------
    def SendToTrainerUSBData(self, TacxMode, Calibrate, PedalEcho, Target, Weight):
        raise NotImplementedError                   # To be defined in sub-class

    def SendToTrainer(self, _QuarterSecond, TacxMode):
        assert (TacxMode in (modeStop, modeResistance, modeCalibrate))

        Calibrate = self.Calibrate
        PedalEcho = self.PedalEcho
        Target    = self.TargetResistance
        Weight    = 0

        if debug.on(debug.Function):
            logfile.Write ("clsTacxUsbTrainer.SendToTrainer(T=%s, M=%s, P=%s, G=%s, R=%s, W=%s, PE=%s, S=%s, C=%s)" % \
            (TacxMode, self.TargetMode, self.TargetPower, self.TargetGrade, \
            self.TargetResistance, self.UserAndBikeWeight, self.PedalEcho, \
            self.SpeedKmh, self.Cadence))

        #-----------------------------------------------------------------------
        # Prepare parameters to be sent to trainer
        #-----------------------------------------------------------------------
        error = False
        if  TacxMode == modeStop:
            Calibrate   = 0
            PedalEcho   = 0
            Target      = 0
            Weight      = 0

        elif TacxMode == modeResistance:
            if Calibrate == 0:                                  # Use old formula:
                Calibrate   = 0                                 # may be -8...+8
                Calibrate   = ( Calibrate + 8 ) * 130           # 0x0410

            assert(self.UserAndBikeWeight >= 0x0a)              # Avoid surprises
            if self.TargetMode == mode_Power:
                Target = self.TargetResistance
                Weight = 0x0a                                   # Small flywheel in ERGmode
            elif self.TargetMode == mode_Grade:
                Target = self.TargetResistance
                Weight = self.UserAndBikeWeight
            else:
                error = "SendToTrainer; Unsupported TargetMode %s" % self.TargetMode

        elif TacxMode == modeCalibrate:
            Calibrate   = 0
            PedalEcho   = 0
            Target      = self.Speed2Wheel(20)                  # 20 km/h is our decision for calibration
            Weight      = 0

        if error:
            logfile.Console(error)
        else:
            Target = int(Target)
            data   = self.SendToTrainerUSBData(TacxMode, Calibrate, PedalEcho, Target, Weight)

            #-------------------------------------------------------------------
            # Send buffer to trainer
            #-------------------------------------------------------------------
            if data != False:
                if debug.on(debug.Data2):
                    logfile.Write ("Trainer send data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
                    logfile.Write ("                  tacx mode=%s target=%s pe=%s weight=%s cal=%s" % \
                                                (TacxMode, Target, PedalEcho, Weight, Calibrate))

                try:
                    self.UsbDevice.write(0x02, data, 30)                             # send data to device
                except Exception as e:
                    logfile.Console("Write to USB trainer error: " + str(e))

#-------------------------------------------------------------------------------
# c l s T a c x L e g a c y U s b T r a i n e r
#-------------------------------------------------------------------------------
# USB-trainer with Legacy interface and old formula's
# ==> headunit = 1902
# ==> iMagic
#-------------------------------------------------------------------------------
class clsTacxLegacyUsbTrainer(clsTacxUsbTrainer):
    def __init__(self, clv, Message, Headunit, UsbDevice):
        super().__init__(clv, Message)
        if debug.on(debug.Function):logfile.Write ("clsTacxLegacyUsbTrainer.__init__()")
        self.Headunit   = Headunit
        self.UsbDevice  = UsbDevice
        self.OK         = True
        self.SpeedScale = 11.9 # GoldenCheetah: curSpeed = curSpeedInternal / (1.19f * 10.0f);
        #PowerResistanceFactor = (1 / 0.0036)       # GoldenCheetah ~= 277.778

    #---------------------------------------------------------------------------
    # Basic physics: Power = Resistance * Speed  <==> Resistance = Power / Speed
    #
    # These two functions calculate as measured with @yegorvin
    #---------------------------------------------------------------------------
    def CurrentResistance2Power(self):
        if self.SpeedKmh == 0:
            rtn = 0
        else:
            # GoldenCheetah: curPower = ((curResistance * 0.0036f) + 0.2f) * curSpeedInternal;
            # return round(((Resistance / PowerResistanceFactor) + 0.2) * WheelSpeed, 1)

            # ref https://github.com/WouterJD/FortiusANT/wiki/Power-calibrated-with-power-meter-(iMagic)
            rtn = self.CurrentResistance * (self.SpeedKmh * self.SpeedKmh / 648 + \
                                                  self.SpeedKmh / 5411 + 0.1058) + \
                        2.2 * self.SpeedKmh
        self.CurrentPower = int(rtn)

    def TargetPower2Resistance(self):
        rtn = 0
        if self.SpeedKmh > 0:
            # instead of brakeCalibrationFactor use PowerFactor -p
            # GoldenCheetah: setResistance = (((load  / curSpeedInternal) - 0.2f) / 0.0036f)
            #                setResistance *= brakeCalibrationFactor
            # rtn = ((PowerInWatt / WheelSpeed) - 0.2) * PowerResistanceFactor

            # ref https://github.com/WouterJD/FortiusANT/wiki/Power-calibrated-with-power-meter-(iMagic)
            rtn = (self.TargetPower - 2.2 * self.SpeedKmh) / \
                    (self.SpeedKmh * self.SpeedKmh / 648 + \
                     self.SpeedKmh / 5411 + 0.1058)

        # Check bounds
        rtn = min(226, rtn) # Maximum value; as defined by Golden Cheetah
        rtn = max( 30, rtn) # Minimum value
        rtn = int(rtn)

        if debug.on(debug.Function):logfile.Write (\
                "clsTacxLegacyUsbTrainer.TargetPower2Resistance(%s, %s) = %s" % \
                    (self.TargetPower, self.SpeedKmh, rtn) )
        self.TargetResistance = rtn

    #---------------------------------------------------------------------------
    # S e n d T o T r a i n e r U S B D a t a
    #---------------------------------------------------------------------------
    # input     Mode, Target
    #
    # function  Called by SendToTrainer()
    #           Compose buffer to be sent to trainer
    #
    # returns   data
    #---------------------------------------------------------------------------
    def SendToTrainerUSBData(self, TacxMode, _Calibrate, _PedalEcho, Target, _Weight):
        #-----------------------------------------------------------------------
        # Data buffer depends on trainer_type
        # Refer to TotalReverse; "Legacy protocol"
        #-----------------------------------------------------------------------
        fDesiredForceValue  = sc.unsigned_char      # 0         0x00-0xff
                                                    #           0x80 = field switched off
                                                    #           < 0x80 reduce brake force
                                                    #           > 0x80 increase brake force
        fStartStop          = sc.unsigned_char      # 1         0x01 = pause/start manual control
                                                    #           0x02 = autopause if wheel < 20
                                                    #           0x04 = autostart if wheel >= 20
        fStopWatch          = sc.unsigned_int       # 2...5

        #-----------------------------------------------------------------------
        # Build data buffer to be sent to trainer (legacy)
        #-----------------------------------------------------------------------
        if TacxMode == modeResistance:
            DesiredForceValue = Target
            StartStop, StopWatch = 0,0  # GoldenCheetah sends 2-byte data
                                        #    in sendRunCommand() with
                                        #    StartStop always zero
                                        # so we should be good like this
            format = sc.no_alignment + fDesiredForceValue + fStartStop + fStopWatch
            data   = struct.pack (format, DesiredForceValue, StartStop, StopWatch)
        else:
            data   = False
        return data
    #---------------------------------------------------------------------------
    # R e c e i v e F r o m T r a i n e r
    #---------------------------------------------------------------------------
    # input     usbDevice
    #
    # function  Read status from trainer
    #
    # returns   Speed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, Buttons
    #---------------------------------------------------------------------------
    def _ReceiveFromTrainer(self):
        if debug.on(debug.Function):logfile.Write ("clsTacxLegacyUsbTrainer._ReceiveFromTrainer()")
        #-----------------------------------------------------------------------
        #  Read from trainer
        #-----------------------------------------------------------------------
        data = self.USB_Read()

        #-----------------------------------------------------------------------
        # Define buffer format
        #-----------------------------------------------------------------------
        nStatusAndCursors   = 0                 # 0
        fStatusAndCursors   = sc.unsigned_char

        nSpeed              = 1                 # 1, 2      Wheel speed (Speed = WheelSpeed / SpeedScale in km/h)
        fSpeed              = sc.unsigned_short

        nCadence            = 2                 # 3
        fCadence            = sc.unsigned_char

        nHeartRate          = 3                 # 4
        fHeartRate          = sc.unsigned_char

        #nStopWatch         = 4
        fStopWatch          = sc.unsigned_int   # 5,6,7,8

        nCurrentResistance  = 5                 # 9
        fCurrentResistance  = sc.unsigned_char

        nPedalSensor        = 6                 # 10
        fPedalSensor        = sc.unsigned_char

        #nAxis0             = 7                 # 11
        fAxis0              = sc.unsigned_char

        nAxis1              = 8                 # 12
        fAxis1              = sc.unsigned_char

        #nAxis2             = 9                 # 13
        fAxis2              = sc.unsigned_char

        #nAxis3             = 10                # 14
        fAxis3              = sc.unsigned_char

        #nCounter           = 11                # 15
        fCounter            = sc.unsigned_char

        #nWheelCount        = 12                # 16
        fWheelCount         = sc.unsigned_char

        #nYearProduction    = 13                # 17
        fYearProduction     = sc.unsigned_char

        #nDeviceSerial      = 14                # 18, 19
        fDeviceSerial       = sc.unsigned_short

        #nFirmwareVersion   = 15                # 20
        fFirmwareVersion    = sc.unsigned_char

        #-----------------------------------------------------------------------
        # Parse buffer
        # Note that the button-bits have an inversed logic:
        #   1=not pushed, 0=pushed. Hence the xor.
        #-----------------------------------------------------------------------
        format = sc.no_alignment + fStatusAndCursors + fSpeed + fCadence + fHeartRate + fStopWatch + fCurrentResistance + \
                fPedalSensor + fAxis0 + fAxis1 + fAxis2 + fAxis3 + fCounter + fWheelCount + \
                fYearProduction + fDeviceSerial + fFirmwareVersion
        tuple = struct.unpack (format, data)

        self.Axis                = tuple[nAxis1]
        self.Buttons             = ((tuple[nStatusAndCursors] & 0xf0) >> 4) ^ 0x0f
        self.Cadence             = tuple[nCadence]
        self.CurrentResistance   = tuple[nCurrentResistance]
        self.HeartRate           = tuple[nHeartRate]
        self.PedalEcho           = tuple[nPedalSensor]
        self.WheelSpeed          = tuple[nSpeed]

        self.Wheel2Speed()
        self.CurrentResistance2Power()

        if debug.on(debug.Function):
            logfile.Write ("ReceiveFromTrainer() = hr=%s Buttons=%s, Cadence=%s Speed=%s TargetRes=%s CurrentRes=%s CurrentPower=%s, pe=%s %s" % \
                (  self.HeartRate, self.Buttons, self.Cadence, self.SpeedKmh, self.TargetResistance, self.CurrentResistance, self.CurrentPower, self.PedalEcho, self.Message) \
                          )

#-------------------------------------------------------------------------------
# c l s T a c x N e w U s b T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with New interface & USB connection
#-------------------------------------------------------------------------------
class clsTacxNewUsbTrainer(clsTacxUsbTrainer):
    def __init__(self, clv, Message, Headunit, UsbDevice):
        super().__init__(clv, Message)
        if debug.on(debug.Function):logfile.Write ("clsTacxNewUsbTrainer.__init__()")
        self.SpeedScale = 301                        # TotalReverse: 289.75
        self.PowerResistanceFactor = 128866          # TotalReverse

        self.Headunit   = Headunit
        self.UsbDevice  = UsbDevice
        self.OK         = True

    #---------------------------------------------------------------------------
    # Basic physics: Power = Resistance * Speed  <==> Resistance = Power / Speed
    #---------------------------------------------------------------------------
    def CurrentResistance2Power(self):
        self.CurrentPower = int(self.CurrentResistance / self.PowerResistanceFactor * self.WheelSpeed)

    def TargetPower2Resistance(self):
        rtn        = 0
        if self.WheelSpeed > 0:
            rtn = self.TargetPower * self.PowerResistanceFactor / self.WheelSpeed
            rtn = self.__AvoidCycleOfDeath(rtn)
        rtn = int(rtn)

        if debug.on(debug.Function):logfile.Write (\
            "clsTacxNewUsbTrainer.TargetPower2Resistance(%s, %s) = %s" % \
            (self.TargetPower, self.WheelSpeed, rtn ))
        self.TargetResistance = rtn

    #---------------------------------------------------------------------------
    # Limit Resistance to avoid the Cycle of Death
    #
    # This a phenomenon occuring in ERGmode (constant power, resistance depends
    # on (wheel)speed): if you get tired at a certain power and cycle slower, 
    # the resistance keeps going up untill Power/0 = infinite and you "die".
    # Starting-up will be quite impossible as well: Power/0.1 is very high!
    # ==> 1: Resistance must be limitted to a maximum at low wheel-speeds
    #
    # Also, Fortius (I do not know for others) does not perform well for high
    # resistances at low wheelspeed. Practical tests have shown a maximum
    # of Resistance = 4500 at 10km/hr. Higher resistances cause stuttering.
    # ==> 2: Same rule, other reason.
    #
    # The protection is that when Speed droppes below 10km/hr, the resistance is
    # limitted. And, if you do not like this, avoid going into this protection,
    # by keeping the wheelspeed above 10km/hr in ERG-mode rides.
    #
    # Note that, the protection factor must be Speed (not Cadence), since that
    # is used in Power2Resistance. Note that, Speed may drop faster than Cadance!
    #
    # Note also that, the figures are empirically determined.
    # option 1. R=6000 at 15km/hr ==> 6000 / 128866 * (15 * 301) = 210Watt
    # option 2. R=4500 at 10km/hr ==> 4500 / 128866 * (10 * 301) = 100Watt
    #
    # The minium of 1500 is chosen above calibration level to avoid that the
    # brake is going to spinn (negative power mode).
    #
    # It means that the required power is maintained untill 10 km/hr, then drops
    # to 100Watt and gradually runs down to minimum at zero-speed.
    # Also, when required power would be 300Watt and you speed up from
    # 1...10km/hr, the power gradually increases to 100Watt untill above 10km/hr
    # the real power is set.
    #
    # With all this said, a similar function should be present in the LegacyUSB
    # class; or function generalized and constants 1500 and 4500 (6000) adjusted.
    #---------------------------------------------------------------------------
    def __AvoidCycleOfDeath(self, Resistance):

        if self.TargetMode == mode_Power and self.SpeedKmh <= 10 and Resistance >= 6000:
            Resistance = int(1500 + self.SpeedKmh * 300)
#           print('__AvoidCycleOfDeath', self.SpeedKmh, Resistance)

        return Resistance

    #---------------------------------------------------------------------------
    # S e n d T o T r a i n e r D a t a
    #---------------------------------------------------------------------------
    # input     Mode, Target, Pedecho, Weight, Calibrate
    #
    # function  Called by SendToTrainer()
    #           Compose buffer to be sent to trainer
    #
    # returns   data
    #---------------------------------------------------------------------------
    def SendToTrainerUSBData(self, TacxMode, Calibrate, PedalEcho, Target, Weight):
        Target = int(min(0x7fff, Target))
        #-----------------------------------------------------------------------
        # Data buffer depends on trainer_type
        # Refer to TotalReverse; "Newer protocol"
        #-----------------------------------------------------------------------
        fControlCommand     = sc.unsigned_int       # 0...3
        fTarget             = sc.short              # 4, 5      Resistance for Power=50...1000Watt
        fPedalecho          = sc.unsigned_char      # 6
        fFiller7            = sc.pad                # 7
        fMode               = sc.unsigned_char      # 8         Idle=0, Ergo/Slope=2, Calibrate/speed=3
        fWeight             = sc.unsigned_char      # 9         0x0a for 'almost no fly wheel' or
                                                            # weight of rider+bike in kg for 
                                                            # 'realistic' simulation of riders mass
                                                            # TotalReverse, updated 2020-01-04
        fCalibrate          = sc.unsigned_short     # 10, 11    Depends on mode

        if self.TargetMode == mode_Power and Target < Calibrate:
            Target = Calibrate        # Avoid motor-function for low TargetPower
        #-----------------------------------------------------------------------
        # Build data buffer to be sent to trainer (legacy or new)
        #-----------------------------------------------------------------------
        format = sc.no_alignment + fControlCommand + fTarget + fPedalecho + fFiller7 + fMode +    fWeight + fCalibrate
        data   = struct.pack (format, 0x00010801,     Target,   PedalEcho,          TacxMode,  int(Weight),  Calibrate)
        return data

    #---------------------------------------------------------------------------
    # R e c e i v e F r o m T r a i n e r
    #---------------------------------------------------------------------------
    # input     usbDevice
    #
    # function  Read status from trainer
    #
    # returns   Speed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, Buttons
    #
    #---------------------------------------------------------------------------
    def _ReceiveFromTrainer(self):
        if debug.on(debug.Function):logfile.Write ("clsTacxNewUsbTrainer._ReceiveFromTrainer()")
        #-----------------------------------------------------------------------
        #  Read from trainer
        #-----------------------------------------------------------------------
        data = self.USB_Read()

        #-----------------------------------------------------------------------
        # Define buffer format
        #-----------------------------------------------------------------------
        #nDeviceSerial      =  0                # 0...1
        fDeviceSerial       = sc.unsigned_short

        fFiller2_7          = sc.pad * ( 7 - 1) # 2...7

        #nYearProduction    =  1                # 8
        fYearProduction     = sc.unsigned_char

        fFiller9_11         = sc.pad * (11 - 8) # 9...11

        nHeartRate          =  2                # 12
        fHeartRate          = sc.unsigned_char

        nButtons            =  3                # 13
        fButtons            = sc.unsigned_char

        #nHeartDetect       =  4                # 14
        fHeartDetect        = sc.unsigned_char

        #nErrorCount        =  5                # 15
        fErrorCount         = sc.unsigned_char

        #nAxis0             =  6                # 16-17
        fAxis0              = sc.unsigned_short

        nAxis1              =  7                # 18-19
        fAxis1              = sc.unsigned_short

        #nAxis2             =  8                # 20-21
        fAxis2              = sc.unsigned_short

        #nAxis3             =  9                # 22-23
        fAxis3              = sc.unsigned_short

        #nHeader            = 10                # 24-27
        fHeader             = sc.unsigned_int

        #nDistance          = 11                # 28-31
        fDistance           = sc.unsigned_int

        nSpeed              = 12                # 32, 33            Wheel speed (Speed = WheelSpeed / SpeedScale in km/h)
        fSpeed              = sc.unsigned_short

        fFiller34_35        = sc.pad * 2        # 34...35           Increases if you accellerate?
        fFiller36_37        = sc.pad * 2        # 36...37           Average power?

        nCurrentResistance  = 13                # 38, 39
        fCurrentResistance  = sc.short

        nTargetResistance   = 14                # 40, 41
        fTargetResistance   = sc.short

        nEvents             = 15                # 42
        fEvents             = sc.unsigned_char

        fFiller43           = sc.pad            # 43

        nCadence            = 16                # 44
        fCadence            = sc.unsigned_char

        fFiller45           = sc.pad            # 45

        #nModeEcho          = 17                # 46
        fModeEcho           = sc.unsigned_char

        #nChecksumLSB       = 18                # 47
        fChecksumLSB        = sc.unsigned_char

        #nChecksumMSB       = 19                # 48
        fChecksumMSB        = sc.unsigned_char

        fFiller49_63        = sc.pad * (63 - 48)# 49...63

        format = sc.no_alignment + fDeviceSerial + fFiller2_7 + fYearProduction + \
                fFiller9_11 + fHeartRate + fButtons + fHeartDetect + fErrorCount + \
                fAxis0 + fAxis1 + fAxis2 + fAxis3 + fHeader + fDistance + fSpeed + \
                fFiller34_35 + fFiller36_37 + fCurrentResistance + fTargetResistance + \
                fEvents + fFiller43 + fCadence + fFiller45 + fModeEcho + \
                fChecksumLSB + fChecksumMSB + fFiller49_63

        #-----------------------------------------------------------------------
        # Buffer must be 64 characters (struct.calcsize(format)),
        # Note that tt_FortiusSB returns 48 bytes only; append with dummy
        #-----------------------------------------------------------------------
        for _v in range( 64 - len(data) ):
            data.append(0)

        #-----------------------------------------------------------------------
        # Parse buffer
        #-----------------------------------------------------------------------
        tuple = struct.unpack (format, data)
        self.Axis               = tuple[nAxis1]
        self.Buttons            = tuple[nButtons]
        self.Cadence            = tuple[nCadence]
        self.CurrentResistance  = tuple[nCurrentResistance]
        self.HeartRate          = tuple[nHeartRate]
        self.PedalEcho          = tuple[nEvents]
        self.TargetResistanceFT = tuple[nTargetResistance]
        self.WheelSpeed         = tuple[nSpeed]

        self.Wheel2Speed()
        self.CurrentResistance2Power()

        if debug.on(debug.Function):
            logfile.Write ("ReceiveFromTrainer() = hr=%s Buttons=%s Cadence=%s Speed=%s TargetRes=%s CurrentRes=%s CurrentPower=%s, pe=%s %s" % \
                        (  self.HeartRate, self.Buttons, self.Cadence, self.SpeedKmh, self.TargetResistance, self.CurrentResistance, self.CurrentPower, self.PedalEcho, self.Message) \
                          )
