#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2023-04-06"
# 2023-04-06    If UserAndBikeWeight is set below the minimum, a sensible value is set.
# 2022-08-22    Steering only active when -S wired specified.
# 2022-08-10    Steering merged from marcoveeneman and switchable's code
# 2022-03-01    #361 clsSimulatedTrainer.Refresh() must correct data type of
#               variables otherwise CurrentPower = iPower is not integer.
# 2021-11-15    "Steering axis = " commented code added for investigation
# 2021-05-18    TargetResistanceFT used in logfile (instead of TargetResistance)
# 2021-04-29    Short message warning message comment added for Raspberry
# 2021-04-20    DisplayStateTable() added, for raspberry status display
#               Operational attribute added
# 2021-04-12    self.tacxEvent = set to True when valid data is received
#                   which can be used as trigger to blink the corresponding led
# 2021-03-16    @Meanhat's odd T1902 supported: 0547:2131
# 2021-02-11    added: -e homeTrainer --> MultiplyPower()
#               removed: self.DynamicAdjust code (which was experimental code)
# 2021-02-11    Vortex HU: request mode switch whenever wrong mode detected
#                          increase keep-alive interval to 10s
#               Vortex brake: handle alarm status (errors/warnings)
# 2021-01-12    @TotalReverse comment added on 128866
#               Power calculation incorrect due to GearboxReduction
# 2021-01-11    Error-recovery improved on USB_Read
#                   --> USB_Read(), USB_Read_retry4x40() and _ReceiveFromTrainer_MotorBrake
# 2021-01-10    Digital gearbox changed to front/rear index
#                   GearboxReduction provided by caller
#                   Also applies in power mode, modifying TargetPower
#                       theoretically against ERG-mode idea, but (see #195) if
#                       you're done, then it's nice to be able to modify.
#                       The returned power remains the produced power.
# 2021-01-10    Motorbrake version message decomposition improved #201
#               Informative messages on brake type
# 2021-01-05    Tacxtype Motorbrake added
# 2021-01-04    lib_programname used to get correct dirname
# 2020-12-30    Added: clsTacxAntTrainer, clsTacxAntBushidoTrainer,
#               clsTacxAntGeniusTrainer, GeniusState, BushidoState
#               (support for Tacx Genius and Tacx Bushido trainers)
#               Fix formula for wind resistance (with tail wind)
# 2020-12-29    message < 40; error message extended (signal AND power)
# 2020-12-27    #173 message < 40 received; retry implemented
# 2020-12-21    #173 T1946 was not detected as motor brake.
# 2020-12-20    Constants used from constants.py
# 2020-12-10    Removed: -u uphill
# 2020-12-03    For Magnetic brake -r uses the resistance table [0...13]
#               introduced: Resistance2PowerMB(), under investigation!!
# 2020-12-01    Speedscale set to 289.75
# 2020-12-01    -G option and Magnetic Brake formula's removed
#               and marked "TO BE IMPLEMENTED"
# 2020-11-23    Motor Brake command implemented for NewUSB interface
#               CalibrateSupported depends on motorbrake, not head unit
#               -r TargetResistance = TargetPower implemented
# 2020-11-18    Calibration also supported for 1942 headunit
# 2020-11-10    Issue 135: React on button press only once corrected
#               Function Power2Speed() added
# 2020-11-03    Issue 118: Adjust virtual flywheel according to virtual gearbox
# 2020-10-22    Removed: superfluous logging in _ReceiveFromTrainer()
# 2020-10-20    Changed: minimum resistance was limitted to the calibrate value
#                   which complicated life for low-FTP athletes.
#                   Therefore this lower limit is removed.
# 2020-10-20    Added: self.DynamicAdjust
# 2020-10-09    Added: -u uphill
# 2020-09-29    Short buffer <40 error recovery improved
#               Typo's corrected (thanks RogerPleijers)
# 2020-06-16    Corrected: USB_read() must always return array of bytes
# 2020-06-12    Added: BikePowerProfile and SpeedAndCadenceSensor final
# 2020-06-11    Changed: if clsTacxNewUsbTrainer less than 40 bytes received, retry
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
import array
import lib_programname
from enum import Enum
import usb.core
import os
import random
import struct
import sys
import time

import antDongle         as ant
from   constants                    import mode_Power, mode_Grade
import constants
import debug
import logfile
import steering
import structConstants   as sc
import FortiusAntCommand as cmd
import fxload

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
hu1902          = 0x1902    # Old "solid green" iMagic headunit (with or without firmware)
hu1902_nfw      = 0x2131    # @Meanhats headunit, without fw
hu1904          = 0x1904    # New "white green" iMagic headunit (firmware inside)
hu1932          = 0x1932    # New "white blue" Fortius headunit (firmware inside)
hu1942          = 0x1942    # Old "solid blue" Fortius (firmware inside)
hue6be_nfw      = 0xe6be    # Old "solid blue" Fortius (without firmware)

idVendor_Tacx   = 0x3561

EnterButton     =  1
DownButton      =  2
UpButton        =  4
CancelButton    =  8
OKButton        = 16        # Non-existant for USB-trainers, for Vortex only

modeStop        = 0         # USB Tacx modes
modeResistance  = 2
modeCalibrate   = 3
modeMotorBrake  = 10        # To distinguish from the previous real modes

#-------------------------------------------------------------------------------
# See https://github.com/totalreverse/ttyT1941/issues/20
#-------------------------------------------------------------------------------
USB_ControlCommand  = 0x00010801
USB_ControlResponse = 0x00021303
USB_VersionRequest  = 0x00000002
USB_VersionResponse = 0x00000c03

#-------------------------------------------------------------------------------
# path to firmware files; since 29-3-2020 in same folder as .py or .exe
#-------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    dirname = sys._MEIPASS                     # pylint: disable=maybe-no-member
else:
    # dirname = os.path.dirname(__file__)      # not always desired result!!
    dirname = str(lib_programname.get_path_executed_script())  # type: pathlib.Path
    dirname = os.path.dirname(dirname)

imagic_fw  = os.path.join(dirname, 'tacximagic_1902_firmware.hex')
fortius_fw = os.path.join(dirname, 'tacxfortius_1942_firmware.hex')

#-------------------------------------------------------------------------------
# Class inheritance
# -----------------
# clsTacxTrainer                            = Base class with attributes
#       -> clsSimulatedTrainer              = Simulated trainer
#       -> clsTacxAntVortexTrainer          = Tacx Vortex
#       -> clsTacxUsbTrainer
#             -> clsTacxLegacyUsbTrainer    = Tacx iMagic
#             -> clsTacxNewUsbTrainer       = Tacx Fortius
#-------------------------------------------------------------------------------
# Class functions (more info in the classes)
# ------------------------------------------
# class clsTacxTrainer()
#     def GetTrainer(clv, AntDevice=None)
#
#     def SetGearboxReduction()                               # Virtual Gearbox
#   
#     def SetPower(Power)                                     # Store Power
#     def AddPower(deltaPower)
#     def MultiplyPower(factor)
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
#     def DisplayStateTable()                                 # return FortiusAnt state
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
    MotorBrake              = False         # Fortius motorbrake, supports calibration

    # Target provided by CTP (Trainer Road, Zwift, Rouvy, ...)
    # See Refresh() for dependencies
    TargetMode              = mode_Power    # Start with power mode
    TargetGrade             = 0             # no grade
    TargetPowerProvided     = 100           # and 100Watts
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
    PreviousButtons         = 0             # int       Issue 135
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
    CalculatedSpeedKmh      = 0             # see #Power2Speed#
    TargetResistanceFT      = 0             # int       Returned from trainer
    WheelSpeed              = 0             # int
    tacxEvent               = False         # is set to True after received from USB or ANT
                                            # is set to False after unsuccesful USB-receive
                                            # must be set to False by caller setting leds
    # set by HandleANTmessage(), __SetState()
    Operational             = False         # Is set true when trainer connected
                                            # USB: after connection
                                            # ANT: after pairing [and calibration]

    # Other general variables
    clv                     = None          # Command line variables
    GearboxReduction        = 1             # 1.1 causes higher load
                                            # 0.9 causes lower load
                                            # Is manually set in Grademode

    # USB devices only:
    Headunit                = 0             # The connected headunit in GetTrainer()
    Calibrate               = 0             # The value as established during calibration
    SpeedScale              = None          # To be set in sub-class

    ControlCommand          = 0xffffffff    # Last command sent
    Header                  = 0xffffffff    # Last command received

    def __init__(self, clv, Message):
        if debug.on(debug.Function):logfile.Write ("clsTacxTrainer.__init__()")
        self.clv             = clv
        self.Message         = Message
        self.OK              = False

        self.SteeringFrame   = None         # a clsSteeringUnit instance, if available

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

        if clv.Tacx_Vortex:     return clsTacxAntVortexTrainer(clv, AntDevice)
        if clv.Tacx_Genius:     return clsTacxAntGeniusTrainer(clv, AntDevice)
        if clv.Tacx_Bushido:    return clsTacxAntBushidoTrainer(clv, AntDevice)

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
        for hu in [hu1902, hu1902_nfw, hu1904, hu1932, hu1942, hue6be_nfw]:
            try:
                if debug.on(debug.Function):
                    logfile.Write ("GetTrainer - Check for trainer %s" % (hex(hu)))
                if hu == hu1902_nfw:
                    vendor = 0x0547             # Unknown special vendor
                else:
                    vendor = idVendor_Tacx      # For all others

                dev = usb.core.find(idVendor=vendor, idProduct=hu)      # find trainer USB device
                if dev:
                    msg = "Connected to Tacx Trainer T" + hex(hu)[2:]   # remove 0x from result
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
            if hu in (hu1902, hu1902_nfw):
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
                    hu = hu1902 # so we do not need to think of hu1902_nfw elsewhere

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
                data = struct.pack (sc.unsigned_int, USB_VersionRequest)
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
    #---------------------------------------------------------------------------
    def SetGearboxReduction(self, Reduction):
        self.GearboxReduction   = Reduction

    def SetPower(self, Power):
        if debug.on(debug.Function):logfile.Write ("SetPower(%s)" % Power)
        self.TargetMode         = mode_Power
        self.TargetGrade        = 0
        self.TargetPowerProvided= Power
        self.TargetPower        = self.TargetPowerProvided * self.GearboxReduction
        self.TargetResistance   = 0             # .Refresh() must be called

    def MultiplyPower(self, factor):
        if factor < 1 and self.TargetPowerProvided <= 10:
            pass    # 10Watt is Minimum
        else:
            self.SetPower(self.TargetPowerProvided * factor)

    def AddPower(self, deltaPower):
        self.SetPower(self.TargetPowerProvided + deltaPower)

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
        if self.UserAndBikeWeight < 70:
            logfile.Console("UserAndBikeWeight is set to %d, which is below the expected minimum of 70kg; corrected to 85kg." % self.UserAndBikeWeight)
            self.UserAndBikeWeight = 75 + 10

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
        # Issue 135
        # Avoid multiple button press when polling faster than button released
        #-----------------------------------------------------------------------
        if self.PreviousButtons == 0:
            # if self.Buttons: print('Button press %s' % self.Buttons)
            # The button was NOT pressed the previous cycle
            # Therefore the button is accepted (rising edge)
            self.PreviousButtons = self.Buttons
        else:
            # if self.Buttons: print('Button press %s ignored' % self.Buttons)
            # Remember the current state of Buttons, must become zero before
            # a button press is accepted
            self.PreviousButtons = self.Buttons
            # Button was pressed previous cycle, so ignore now
            self.Buttons = 0

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

        # No negative value defined for ANT message Page25 (#)
        # if self.CurrentPower < 0: self.CurrentPower = 0     # --> msgPage25_TrainerData
        assert (self.TargetMode in (mode_Power, mode_Grade))

        if  self.TargetMode == mode_Grade:
            self.VirtualSpeedKmh = self.SpeedKmh * self.GearboxReduction
            self._Grade2Power()         # Resulting in self.TargetPower

        #-----------------------------------------------------------------------
        # Apply GearboxReduction to provided TargetPower
        # Then calculate resistance
        #
        # Modifying the VirtualSpeed would not affect the resistance, which is
        # based upon TargetPower and WheelSpeed.
        #-----------------------------------------------------------------------
        if self.TargetMode == mode_Power:
            self.VirtualSpeedKmh = self.SpeedKmh
            self.TargetPower = self.TargetPowerProvided * self.GearboxReduction

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
        # Round after all these calculations (and correct data type!) #361 
        # ----------------------------------------------------------------------
        self.Cadence             = int(self.Cadence)
        self.TargetPower         = int(self.TargetPower)
        self.TargetResistance    = int(self.TargetResistance)
        self.CurrentResistance   = int(self.CurrentResistance)
        self.CurrentPower        = int(self.CurrentPower)
        self.SpeedKmh            = round(self.SpeedKmh,1)
        self.VirtualSpeedKmh     = round(self.VirtualSpeedKmh,1)

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
        # if self.Headunit in (hu1932, hu1942):       # And perhaps others as well
        #     return True
        # else:
        #     return False
        return self.MotorBrake

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
    # Input         TargetGrade, UserAndBikeWeight, VirtualSpeedKmh
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
        # without abs a strong tailwind would result in a higher power
        Pair  = 0.5 * p_cdA * (v+w) * abs(v+w) * d * v # Watt

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

    #---------------------------------------------------------------------------
    # Convert Power to Speed
    #---------------------------------------------------------------------------
    # When Power is known, Zwift shows the speed - based upon the known slope
    # This function should be similar
    #---------------------------------------------------------------------------
    # input:        self.CurrentPower, self.UserAndBikeWeight, self.TargetGrade
    #
    # description   Based upon inputs, estimate Speed
    #
    #               Note: the Grade2Power() functions operate on self, and 
    #                     therefore do not require input/return variables.
    #
    #               The reason we do NOT modify self.VirtualSpeedKmh here is
    #               that that speed is directly related to the physical wheel-
    #               speed. So CalculatedSpeed is added and the consumer of the
    #               data can choose which of the two to use. 
    #
    #               _Grade2Power() uses self.VirtualSpeedKmh as input to
    #               calculate power. Therefore the value is saved and restored.
    #               The field is used here to find the correct speed resulting
    #               in the searched power.
    #               *** appologies for this construction ***
    #
    # output:       self.CalculatedSpeed
    #
    # returns:      None
    #---------------------------------------------------------------------------
    def Power2Speed(self, Grade=0):                             #Power2Speed#
        SpeedLo     = 1         # The low  speed in the range where we estimate
        SpeedHi     = 100       # The high ...
        Speed       = 0         # The estimated speed
        PrevPower   = 0         # The previous power

        # ----------------------------------------------------------------------
        # We are going to SEARCH a VirtualSpeedKmh, resulting in TargetPower
        # that equals CurrentPower. Save these two fields and restore afterwards
        # ----------------------------------------------------------------------
        SaveVirtualSpeedKmh = self.VirtualSpeedKmh
        SaveTargetPower     = self.TargetPower
        SaveTargetGrade     = self.TargetGrade

        # ----------------------------------------------------------------------
        # In powermode, by default we use TargetGrade=0 to calculate the speed
        # if we ride a virtual route, the TargetGrade is taken from the GPX and
        # provided as a parameter.
        # We COULD leave TargetGrade modified, but restore it just to be neat.
        #
        # In GradeMode, the TargetGrade is already set.
        # ----------------------------------------------------------------------
        if self.TargetMode == mode_Power:
            self.TargetGrade = Grade

        if self.CurrentPower == 0:
            Speed = 0           # No power, no speed
        else:
            SpeedLo = 1         # We do not cycle backwards
            SpeedHi = 100       # Smart guy going faster :-)
            
            # ------------------------------------------------------------------
            # If power is negative, find point where curve goes up
            # The powercurve with a big negative slope has two solutions for the
            # speed when the (negative) power is given; herewith we chose to get
            # the highest speed of the two.
            # ------------------------------------------------------------------
            if self.CurrentPower < 0:
                self.VirtualSpeedKmh = SpeedLo
                self._Grade2Power()
                PrevPower = 10000
                while self.TargetPower < PrevPower:
                    SpeedLo = SpeedLo + 5
                    PrevPower = self.TargetPower
                    self.VirtualSpeedKmh = SpeedLo
                    self._Grade2Power()
            
            # ------------------------------------------------------------------
            # Find the power that matches the searched speed
            #
            #    +----------+----------+
            # SpeedLo ... Speed ... SpeedHi
            #          TargetPower
            # Move SpeedLo/SpeedHi based upon power, untill close enough.
            # ------------------------------------------------------------------
            while (SpeedHi / SpeedLo) > 1.05:
            
                Speed = (SpeedLo + SpeedHi) / 2         # The estimated speed
                self.VirtualSpeedKmh = Speed            # results in
                self._Grade2Power()                     # TargetPower
                
                if self.TargetPower < self.CurrentPower:
                    SpeedLo = Speed                     # New boundary
                else:
                    SpeedHi = Speed                     # New boundary

        # ----------------------------------------------------------------------
        # Restore fields
        # ----------------------------------------------------------------------
        self.VirtualSpeedKmh = SaveVirtualSpeedKmh
        self.TargetPower     = SaveTargetPower
        self.TargetGrade     = SaveTargetGrade

        # ----------------------------------------------------------------------
        # Our output
        # ----------------------------------------------------------------------
        self.CalculatedSpeedKmh = Speed

    # --------------------------------------------------------------------------
    # D i s p l a y S t a t e T a b l e
    # --------------------------------------------------------------------------
    # input:        FortiusAntState, self.CalibrateSupported and self.clv.calibrate
    #
    # Description:  This function returns a table with texts, showing the state
    #               of FortiusAntBody, enhanced with knowledge of the trainer.
    #
    #               The function is defined here, so that the USB-trainers are
    #               covered; the function can be overwritten in (ANT)classes
    #               where that is applicable.
    #
    # Output:       None
    #
    # Returns:      table with texts and colour
    # --------------------------------------------------------------------------
    def DisplayStateTable(self, FortiusAntState):
        c0 = constants.WHITE if FortiusAntState == constants.faStarted        else constants.GREY
        c1 = constants.WHITE if FortiusAntState == constants.faTrainer        else constants.GREY
        c2 = constants.WHITE if FortiusAntState == constants.faWait2Calibrate else constants.GREY
        c3 = constants.WHITE if FortiusAntState == constants.faCalibrating    else constants.GREY
        c4 = constants.WHITE if FortiusAntState == constants.faActivate       else constants.GREY
        c5 = constants.WHITE if FortiusAntState == constants.faOperational    else constants.GREY
        c6 = constants.WHITE if FortiusAntState == constants.faStopped        else constants.GREY
        c7 = constants.WHITE if FortiusAntState == constants.faDeactivated    else constants.GREY
        c8 = constants.WHITE if FortiusAntState == constants.faTerminated     else constants.GREY

        # ----------------------------------------------------------------------
        # Show devices that are in-scope; not sure whethere they are present.
        # ----------------------------------------------------------------------
        device = 'ANT+' if self.clv.antDeviceID != -1 else ''
        if self.clv.ble:
            if device: device += ', '       # ' and ' is too long
            device += 'BLE'

        # ----------------------------------------------------------------------
        # Show status of FortiusAnt, assuminig that calibration is supported
        # ----------------------------------------------------------------------
        rtn = [ [ 'FortiusAnt started',    c0 ],\
                [ 'Tacx T%s trainer' % hex(self.Headunit)[2:], c1 ],\
                [ 'Give pedal kick',       c2 ],\
                [ 'Calibrating...',        c3 ],\
                [ 'Activate ' + device,    c4 ],\
                [ 'Ready for training',    c5 ],\
                [ 'Trainer stopped',       c6 ],\
                [ device + ' stopped',     c7 ],\
                [ 'FortiusAnt stopped',    c8 ]]

        # ----------------------------------------------------------------------
        # Remove calibration if not
        # ----------------------------------------------------------------------
        if not (self.CalibrateSupported and self.clv.calibrate):
            del rtn[3]	# Give pedal kick
            del rtn[2]	# Calibrating...

        return rtn

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
        self.Operational     = True         # Always true

        # ----------------------------------------------------------------------
        # Steering
        # ----------------------------------------------------------------------
        if self.clv.Steering == 'wired':
            self.Steering1st     = True
            self.SteeringFrame   = steering.clsSteering(InitialCalLeft=-100,
                                                        InitialCalRight=100,
                                                        DeadZone=7.0)

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
    #               For example to make a video without pedaling.
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
        self.Axis               = 75        # I have no sensible random axis
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

        # ----------------------------------------------------------------------
        # Round after all these calculations (and correct data type!) #361 
        # ----------------------------------------------------------------------
        self.Cadence             = int(self.Cadence)
        self.HeartRate           = int(self.HeartRate)
        self.TargetPower         = int(self.TargetPower)
        self.TargetResistance    = int(self.TargetResistance)
        self.CurrentResistance   = int(self.CurrentResistance)
        self.CurrentPower        = int(self.CurrentPower)
        self.SpeedKmh            = round(self.SpeedKmh,1)
        self.VirtualSpeedKmh     = round(self.VirtualSpeedKmh,1)

        # ----------------------------------------------------------------------
        # Steering
        # ----------------------------------------------------------------------
        if self.clv.Steering == 'wired':
            if self.Steering1st:
                # First time, send the stable center position. For us zero is fine.
                for _i in range(10): self.SteeringFrame.Update(   0) # Calibrate center
                for _i in range(10): self.SteeringFrame.Update( 110) # Calibrate right
                for _i in range(10): self.SteeringFrame.Update(-110) # Calibrate left
                self.Steering1st = False

            # Invert axis value so lower value -> left (not right)
            for _i in range(10): self.SteeringFrame.Update(-self.Axis)

#-------------------------------------------------------------------------------
# c l s T a c x A n t V o r t e x T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with ANT connection
# Actually, only the data-storage and Refresh() with Grade2Power() is used!
#-------------------------------------------------------------------------------
class clsTacxAntVortexTrainer(clsTacxTrainer):
    def __init__(self, clv, AntDevice):
        super().__init__(clv, "Pair with Tacx Vortex and Headunit")
        if debug.on(debug.Function):logfile.Write ("clsTacxAntVortexTrainer.__init__()")
        self.AntDevice         = AntDevice
        self.OK                = True           # The AntDevice is there,
                                                # the trainer not yet paired!
        self.__VHUmode = ant.VHU_Normal         # current HU mode

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

        self.__VortexButtons  = 0               # provided by datapage 221

        self.__VTX_AlarmStatus = 0              # brake errors/warnings (page 1)

        # time of last keep-alive message
        self.__KeepAliveTime   = time.time()

        self.Message = 'Pair with Tacx Vortex and Headunit'

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
        # Translate Vortex buttons to TacxTrainer.Buttons.
        # Mapping according TotalReverse:
        # https://github.com/totalreverse/ttyT1941/issues/9#issuecomment-624360140
        # ----------------------------------------------------------------------
        if   self.__VortexButtons == ant.VHU_Button_None:  self.Buttons = 0
        elif self.__VortexButtons == ant.VHU_Button_Left:  self.Buttons = CancelButton
        elif self.__VortexButtons == ant.VHU_Button_Up:    self.Buttons = UpButton
        elif self.__VortexButtons == ant.VHU_Button_Enter: self.Buttons = OKButton
        elif self.__VortexButtons == ant.VHU_Button_Down:  self.Buttons = DownButton
        elif self.__VortexButtons == ant.VHU_Button_Right: self.Buttons = EnterButton
        self.__VortexButtons = ant.VHU_Button_None

        # ----------------------------------------------------------------------
        # Compose displayable message
        # ----------------------------------------------------------------------
        if self.__DeviceNumberVTX:
            msg = 'Tacx Vortex paired: %d' % self.__DeviceNumberVTX
            if self.__VTX_AlarmStatus == ant.VTX_Alarm_WrongMainsVoltage:
                msg += " WRONG MAINS VOLTAGE!"
            if self.__VTX_AlarmStatus == ant.VTX_Alarm_TemperatureHigh:
                msg += " TEMPERATURE HIGH!"
            if self.__VTX_AlarmStatus == ant.VTX_Alarm_NoBrakeCoils:
                msg += " NO BRAKE COILS!"
            self.Message = msg
        else:
            self.Message = "Pair with Tacx Vortex"

        if self.__DeviceNumberVHU:
            self.Message += ', Headunit: %d' % self.__DeviceNumberVHU
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
                    info = ant.msgPage16_TacxVortexSetPower (ant.channel_VTX_s,
                                self.__VortexID, self.TargetResistance)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                    messages.append ( msg )

                #---------------------------------------------------------------
                # Avoid power off on headunit
                #---------------------------------------------------------------
                if self.__AntVHUpaired:
                    # Head-unit powers off after 3 minutes
                    KeepAliveInterval = 10  # in s
                    TimeElapsed = time.time() - self.__KeepAliveTime

                    if TimeElapsed > KeepAliveInterval:
                        info = ant.msgPage000_TacxVortexHU_StayAlive (ant.channel_VHU_s)
                        msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                        messages.append ( msg )

                        if debug.on(debug.Function):
                            logfile.Write("Vortex HU page 0 (OUT) Keep-alive")

                        # reset keep-alive timer
                        self.__KeepAliveTime = time.time()

                    # ---------------------------------------------------------------
                    #  Request PC-mode (repeat until confirmation)
                    # ---------------------------------------------------------------
                    elif self.__VHUmode != ant.VHU_PCmode:
                        info = ant.msgPage172_TacxVortexHU_ChangeHeadunitMode (
                            ant.channel_VHU_s, ant.VHU_PCmode)
                        msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                        messages.append ( msg )

                        if debug.on(debug.Function):
                            logfile.Write(
                                "Vortex HU page 172/0x03 (OUT)  Mode=%d" % \
                                ant.VHU_PCmode)

            elif TacxMode ==  modeStop:
                #---------------------------------------------------------------
                # Switch headunit to trainer control mode
                #---------------------------------------------------------------
                # TODO: ANT is turned off when training is stopped, so this does not work
                if self.__AntVHUpaired:
                    info = ant.msgPage172_TacxVortexHU_ChangeHeadunitMode (
                                              ant.channel_VHU_s, ant.VHU_Normal)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
                    messages.append ( msg )

                    if debug.on(debug.Function):
                        logfile.Write(
                            "Vortex HU page 172/0x03 (OUT)  Mode=%d" % \
                            ant.VHU_Normal)

            #-------------------------------------------------------------------
            # Send messages, leave receiving to the outer loop
            #-------------------------------------------------------------------
            if messages:
                self.AntDevice.Write(messages, False, False)

    #---------------------------------------------------------------------------
    # TargetPower2Resistance
    #
    # TargetResistance is used for the Vortex, even when expressed in Watt, so
    # that PowerFactor and GearboxReduction apply; see clsUsbTrainer.Refresh().
    #---------------------------------------------------------------------------
    def TargetPower2Resistance(self):
        self.TargetResistance = self.TargetPower

    #---------------------------------------------------------------------------
    # Refresh()
    # No special actions required
    # Note that TargetResistance=0 for the Vortex; TargetPower is sent!
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
        SubPageNumber = info[2] if len(info) > 2 else None
        dataHandled = False
        messages    = []

        #-----------------------------------------------------------------------
        # VTX_s = Tacx Vortex trainer
        #-----------------------------------------------------------------------
        if Channel == ant.channel_VTX_s:
            #-------------------------------------------------------------------
            # BroadcastData - info received from the master device
            #-------------------------------------------------------------------
            if id == ant.msgID_BroadcastData:
                self.tacxEvent = True
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
                    UsingVirtualSpeed, self.__CurrentPower, self.__WheelSpeed, \
                        CalibrationState, self.__Cadence = \
                        ant.msgUnpage00_TacxVortexDataSpeed(info)
                    if debug.on(debug.Function):
                        logfile.Write ('Vortex Page=%d (IN) UsingVirtualSpeed=%d Power=%d Speed=%d CalState=%d Cadence=%d' % \
                            (DataPageNumber, UsingVirtualSpeed, self.__CurrentPower,
                                self.__WheelSpeed, CalibrationState, self.__Cadence) )

                #---------------------------------------------------------------
                # Data page 01 msgUnpage01_TacxVortexDataSerial
                #---------------------------------------------------------------
                elif DataPageNumber == 1:
                    DeviceType, Year, DeviceNumber, self.__VTX_AlarmStatus = ant.msgUnpage01_TacxVortexDataSerial(info)
                    if debug.on(debug.Function):
                        logfile.Write ('Vortex Page=%d (IN) DeviceType=%d Year=%d DeviceNumber=%d Alarm=%d' % \
                                       (DataPageNumber, DeviceType, Year, DeviceNumber, self.__VTX_AlarmStatus))

                #---------------------------------------------------------------
                # Data page 02 msgUnpage02_TacxVortexDataVersion
                #---------------------------------------------------------------
                elif DataPageNumber == 2:
                    MajorVersion, MinorVersion, Build = ant.msgUnpage02_TacxVortexDataVersion(info)
                    if debug.on(debug.Function):
                        logfile.Write ('Vortex Page=%d (IN) MajorVersion=%d MinorVersion=%d Build=%d' % \
                            (DataPageNumber, MajorVersion, MinorVersion, Build))

                #---------------------------------------------------------------
                # Data page 03 msgUnpage03_TacxVortexDataCalibration
                #---------------------------------------------------------------
                elif DataPageNumber == 3:
                    CalValue, self.__VortexID = ant.msgUnpage03_TacxVortexDataCalibration(info)
                    if debug.on(debug.Function):
                        logfile.Write ('Vortex Page=%d (IN) CalValue=%d VortexID=%d' % \
                            (DataPageNumber, CalValue, self.__VortexID))

            #-------------------------------------------------------------------
            # ChannelID - the info that a master on the network is paired
            #-------------------------------------------------------------------
            elif id == ant.msgID_ChannelID:
                Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                    ant.unmsg51_ChannelID(info)

                if DeviceTypeID == ant.DeviceTypeID_VTX:
                    self.__AntVTXpaired    = True
                    self.__DeviceNumberVTX = DeviceNumber
                    self.Operational       = True # FortiusAnt can send/receive to brake

            #-------------------------------------------------------------------
            # Outer loop does not need to handle channel_VTX_s messages
            #-------------------------------------------------------------------
            dataHandled = True

        #-----------------------------------------------------------------------
        # VHU_s = Tacx Vortex headunit
        #-----------------------------------------------------------------------
        elif Channel == ant.channel_VHU_s:
            if id == ant.msgID_AcknowledgedData:
                #---------------------------------------------------------------
                # Data page 221 TacxVortexHU_ButtonPressed
                #---------------------------------------------------------------
                if DataPageNumber == 221:
                    self.__VortexButtons = \
                              ant.msgUnpage221_TacxVortexHU_ButtonPressed (info)
                    if debug.on(debug.Function):
                        logfile.Write ('Vortex HU Page=%d (IN) Buttons=%d' % \
                                       (DataPageNumber, self.__VortexButtons))

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
                # Data page 173 containing the serial number/mode of the device
                #---------------------------------------------------------------
                if DataPageNumber == 173 and SubPageNumber == 0x01: # 0xad:
                    self.__VHUmode, Year, DeviceType, DeviceNumber = \
                        ant.msgUnpage173_01_TacxVortexHU_SerialMode (info)
                    if debug.on(debug.Function):
                        logfile.Write ('Vortex HU Page=%d/%#x (IN) Mode=%d Year=%d DeviceType=%d DeviceNumber=%d' % \
                                       (DataPageNumber, SubPageNumber, self.__VHUmode, Year,
                                        DeviceType, DeviceNumber))

            #-------------------------------------------------------------------
            # ChannelID - the info that a master on the network is paired
            #-------------------------------------------------------------------
            elif id == ant.msgID_ChannelID:
                Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                    ant.unmsg51_ChannelID(info)

                if DeviceTypeID == ant.DeviceTypeID_VHU:
                    self.__AntVHUpaired    = True
                    self.__DeviceNumberVHU = DeviceNumber

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

    # --------------------------------------------------------------------------
    # D i s p l a y S t a t e T a b l e
    # --------------------------------------------------------------------------
    # input:        FortiusAntState, self.__AntVHUpaired
    #
    # Description:  This function returns a table with texts, showing the state
    #               of FortiusAntBody, enhanced with knowledge of the trainer.
    #
    # Output:       None
    #
    # Returns:      table with texts and colour
    # --------------------------------------------------------------------------
    def DisplayStateTable(self, FortiusAntState):
        c0 = constants.WHITE if FortiusAntState == constants.faStarted        else constants.GREY
        c1 = constants.WHITE if FortiusAntState == constants.faTrainer        else constants.GREY
       #c2 = constants.WHITE if FortiusAntState == constants.faWait2Calibrate else constants.GREY
       #c3 = constants.WHITE if FortiusAntState == constants.faCalibrating    else constants.GREY
        c4 = constants.WHITE if FortiusAntState == constants.faActivate       else constants.GREY
       #c5 = constants.WHITE if FortiusAntState == constants.faOperational    else constants.GREY
        c6 = constants.WHITE if FortiusAntState == constants.faStopped        else constants.GREY
        c7 = constants.WHITE if FortiusAntState == constants.faDeactivated    else constants.GREY
        c8 = constants.WHITE if FortiusAntState == constants.faTerminated     else constants.GREY

        c5 = constants.GREY
        c5w= constants.GREY
        if FortiusAntState == constants.faOperational:
            #if self.__AntVHUpaired:    Not used, because does not influence operation
            if not self.__AntVTXpaired:
                c5w= constants.WHITE       # Waiting for Vortex
            else:
                c5 = constants.WHITE       # Operational

        # ----------------------------------------------------------------------
        # Show devices that are in-scope; not sure whethere they are present.
        # ----------------------------------------------------------------------
        device = 'ANT+'                # Of course, otherwise no vortex possible
        if self.clv.ble:
            device += ', BLE'

        # ----------------------------------------------------------------------
        # Show status of FortiusAnt and Vortex
        # ----------------------------------------------------------------------
        rtn = [ [ 'FortiusAnt started',    c0 ],\
                [ 'Tacx Vortex trainer',   c1 ],\
                [ 'Activate ' + device,    c4 ],\
                [ 'Waiting for Vortex',    c5w],\
                [ 'Ready for training',    c5 ],\
                [ 'Trainer stopped',       c6 ],\
                [ device + ' stopped',     c7 ],\
                [ 'FortiusAnt stopped',    c8 ]]

        return rtn

#-------------------------------------------------------------------------------
# c l s T a c x A n t T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with ANT connection (base class)
#-------------------------------------------------------------------------------
class clsTacxAntTrainer(clsTacxTrainer):
    def __init__(self, clv, msg, AntDevice, channel):
        super().__init__(clv, msg)
        if debug.on(debug.Function):
            logfile.Write ("clsTacxAntTrainer.__init__()")
        self.AntDevice         = AntDevice
        self.OK                = True
        self.Channel           = channel
        # The AntDevice is there, the trainer is not yet paired!

        self._ResetTrainer()

    def _ResetTrainer(self):
        self._DeviceNumber     = 0              # provided by CHANNEL_ID msg
        self._CommandCounter   = 0

        self._Cadence          = 0              # provided by datapage 0
        self._CurrentPower     = 0
        self._WheelSpeed       = 0
        self._SpeedKmh         = 0              #     (from WheelSpeed)
        self._AlarmStatus      = 0

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
        self.Cadence      = self._Cadence
        self.CurrentPower = self._CurrentPower
        self.WheelSpeed   = self._WheelSpeed

        self.SpeedKmh     = self.WheelSpeed / 10    # Speed = in 0.1 km/hr

    #---------------------------------------------------------------------------
    # __ConvertWind()
    #---------------------------------------------------------------------------
    # Different Tacx trainers use different units for wind resistance/speed
    # Subclass needs to provide the correct formula
    def _ConvertWind(self, WindResistance, WindSpeed, DraftingFactor):
        raise NotImplementedError()

    #---------------------------------------------------------------------------
    # SendToTrainer()
    #---------------------------------------------------------------------------
    def SendToTrainer(self, QuarterSecond, TacxMode):
        if TacxMode == modeStop:
            self._ResetTrainer()                       # Must be paired again!

        if QuarterSecond:
            messages = []
            if TacxMode == modeResistance:
                if self.TargetMode == mode_Grade:
                    # insert a wind resistance page at regular intervals
                    WindResistanceInterval = 4

                    self._CommandCounter += 1
                    if self._CommandCounter < WindResistanceInterval:
                        #---------------------------------------------------------------
                        # Set target slope
                        #---------------------------------------------------------------

                        # the brake does not support changing the rolling resistance
                        # directly; higher than default rolling resistance is simulated
                        # by increasing the grade (result is the same)
                        effectiveGrade = self.TargetGrade + self.__RollingResistance2Grade()

                        info = ant.msgPage220_01_TacxGeniusSetTarget(self.Channel, ant.GNS_Mode_Slope,
                                                                     effectiveGrade, self.UserAndBikeWeight)

                        if debug.on(debug.Function):
                            logfile.Write(
                                "Tacx page 220/0x01 (OUT)  Mode=%d Target=%.1f Weight=%.1f" % \
                                (ant.GNS_Mode_Slope, effectiveGrade, self.UserAndBikeWeight))
                    else:
                        #---------------------------------------------------------------
                        # Set wind resistance and speed
                        #---------------------------------------------------------------
                        WindResistance, WindSpeed = self._ConvertWind(self.WindResistance,
                                                                      self.WindSpeed, self.DraftingFactor)
                        info = ant.msgPage220_02_TacxGeniusWindResistance(self.Channel,
                                                                          WindResistance, WindSpeed)
                        if debug.on(debug.Function):
                            logfile.Write(
                                "Tacx page 220/0x02 (OUT)  WindResistance=%.2f WindSpeed=%.1f" % \
                                (self.WindResistance, self.WindSpeed))
                        self._CommandCounter = 0

                    msg = ant.ComposeMessage(ant.msgID_BroadcastData, info)
                    messages.append(msg)
                else:
                    #---------------------------------------------------------------
                    # Set target power
                    #---------------------------------------------------------------
                    # lower flywheel mass in ERG mode to make the trainer more responsive
                    # 10kg is what is used on the Fortius
                    flywheelMass = 10
                    info = ant.msgPage220_01_TacxGeniusSetTarget(self.Channel, ant.GNS_Mode_Power,
                                                                  self.TargetResistance, flywheelMass)
                    msg = ant.ComposeMessage(ant.msgID_BroadcastData, info)
                    messages.append(msg)

                    if debug.on(debug.Function):
                        logfile.Write(
                            "Tacx page 220/0x01 (OUT)  Mode=%d Target=%.1f Weight=%.1f" % \
                            (ant.GNS_Mode_Power, self.TargetResistance, flywheelMass))

            #-------------------------------------------------------------------
            # Send messages, leave receiving to the outer loop
            #-------------------------------------------------------------------
            if messages:
                self.AntDevice.Write(messages, False, False)


    # ---------------------------------------------------------------------------
    # TargetPower2Resistance
    #
    # TargetResistance is used for the Genius/Bushido, even when expressed in Watt, so
    # that PowerFactor apply; see clsUsbTrainer.Refresh().
    # ---------------------------------------------------------------------------
    def TargetPower2Resistance(self):
        self.TargetResistance = self.TargetPower


    # ---------------------------------------------------------------------------
    # __RollingResistance2Grade
    #
    # Some trainers (Genius, Bushido) do not support setting a rolling
    # resistance coefficient, but it is possible to calculate an additional
    # slope that realizes the same effect
    # ---------------------------------------------------------------------------
    def __RollingResistance2Grade(self):
        # assume the default rolling resistance applied internally is 0.004
        # and calculate a slope that accounts for the difference
        defaultRR = 0.004
        deltaRR = self.RollingResistance - defaultRR
        return deltaRR * 100

    #---------------------------------------------------------------------------
    # HandleANTmessage()
    #---------------------------------------------------------------------------
    def HandleANTmessage(self, msg):
        _synch, _length, id, info, _checksum, _rest, \
        Channel, DataPageNumber = ant.DecomposeMessage(msg)
        SubPageNumber = info[2] if len(info) > 2 else None
        dataHandled = False
        messages = []

        if Channel == self.Channel:

            #-------------------------------------------------------------------
            # BroadcastData - info received from the master device
            #-------------------------------------------------------------------
            if id == ant.msgID_BroadcastData:
                self.tacxEvent = True
                #-----------------------------------------------------------------
                # Data page 221 (0x01) msgUnpage221_01_TacxGeniusSpeedPowerCadence
                #-----------------------------------------------------------------
                if DataPageNumber == 221 and SubPageNumber == 0x01:
                    self._CurrentPower, self._WheelSpeed, self._Cadence, Balance = \
                        ant.msgUnpage221_01_TacxGeniusSpeedPowerCadence(info)

                    if debug.on(debug.Function):
                        logfile.Write('Tacx Page=%d/%#x (IN)  Power=%d Speed=%d Cadence=%d Balance=%d' %
                                      (DataPageNumber, SubPageNumber, self._CurrentPower,
                                       self._WheelSpeed, self._Cadence, Balance))

                # -----------------------------------------------------------------
                # Data page 221 (0x02) msgUnpage221_02_TacxGeniusDistanceHR
                # -----------------------------------------------------------------
                elif DataPageNumber == 221 and SubPageNumber == 0x02:
                    Distance, Heartrate = \
                        ant.msgUnpage221_02_TacxGeniusDistanceHR(info)

                    if debug.on(debug.Function):
                        logfile.Write('Tacx Page=%d/%#x (IN)  Distance=%d Heartrate=%d' %
                                      (DataPageNumber, SubPageNumber, Distance, Heartrate))

                # -----------------------------------------------------------------
                # Data page 221 (0x03) msgUnpage221_03_TacxGeniusAlarmTemperature
                # -----------------------------------------------------------------
                elif DataPageNumber == 221 and SubPageNumber == 0x03:
                    self._AlarmStatus, Temperature, Powerback = \
                        ant.msgUnpage221_03_TacxGeniusAlarmTemperature(info)

                    if debug.on(debug.Function):
                        logfile.Write('Tacx Page=%d/%#x (IN)  Alarm=%d Temperature=%d Powerback=%d' %
                                      (DataPageNumber, SubPageNumber, self._AlarmStatus, Temperature, Powerback))

            #-------------------------------------------------------------------
            # Outer loop does not need to handle trainer channel messages
            #-------------------------------------------------------------------
            dataHandled = True

        #-----------------------------------------------------------------------
        # Send messages, leave receiving to the outer loop
        #-----------------------------------------------------------------------
        if messages:
            self.AntDevice.Write(messages, False, False)

        return dataHandled

#-------------------------------------------------------------------------------
# c l s T a c x A n t G e n i u s T r a i n e r
#-------------------------------------------------------------------------------
# Tacx Genius trainer
#-------------------------------------------------------------------------------

# Genius state machine
class GeniusState(Enum):
    Pairing = 0,
    RequestCalibrationInfo = 1,
    RequestCalibration = 2,
    CalibrationStarted = 3,
    CalibrationRunning = 4,
    CalibrationDone = 5,
    CalibrationFailed = 6,
    Running = 7

class clsTacxAntGeniusTrainer(clsTacxAntTrainer):
    def __init__(self, clv, AntDevice):
        msg = "Pair with Tacx Genius"
        super().__init__(clv, msg, AntDevice, ant.channel_GNS_s)

    def _ResetTrainer(self):
        super()._ResetTrainer()
        self.__Calibrated       = False
        self.__WatchdogTime     = time.time()
        self.__CalibrationValue = 0
        self.__State            = GeniusState.Pairing

    def __SetState(self, state):
        if debug.on(debug.Function):
            logfile.Write("Genius state %s -> %s" % (self.__State, state))
        self.__State = state
        self.__CommandCounter = 0

        if self.__State == GeniusState.Running:
            self.Operational = True       # FortiusAnt can send/receive to brake

    def __ResetTimeout(self):
        self.__WatchdogTime = time.time()

    def __CheckCalibrationTimeout(self):
        # cancel calibration if no progress in last 60s
        timeout = 60
        if time.time() > self.__WatchdogTime + timeout:
            self.__SetState(GeniusState.CalibrationFailed)
            self.__Calibrated = False

            if debug.on(debug.Function):
                logfile.Write("Genius calibration timed out")

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
        super()._ReceiveFromTrainer()

        # ----------------------------------------------------------------------
        # Compose displayable message
        # ----------------------------------------------------------------------
        if self.__State == GeniusState.CalibrationStarted:
            self.Message = "* * * * N U D G E  W H E E L  F O R W A R D * * * *"
        elif self.__State == GeniusState.CalibrationRunning:
            self.Message = "* * * * C A L I B R A T I N G  ( D O  N O T  P E D A L ! ) * * * *"
        elif self.__State == GeniusState.CalibrationDone:
            nominalCalValue = 75
            calMargin = 15
            msg = "Calibration complete (%+d)" % \
                           (self.__CalibrationValue - nominalCalValue)
            if self.__CalibrationValue > nominalCalValue + calMargin:
                msg += " - Decrease roller pressure!"
            elif self.__CalibrationValue < nominalCalValue - calMargin:
                msg += " - Increase roller pressure!"
            self.Message = msg
        elif self.__State == GeniusState.CalibrationFailed:
            self.Message = "Calibration failed"
        elif self._DeviceNumber:
            msg = "Tacx Genius paired: %d" % self._DeviceNumber
            if not self.__Calibrated:
                msg += " UNCALIBRATED"
            if self._AlarmStatus & ant.GNS_Alarm_Overtemperature:
                msg += " TEMPERATURE TOO HIGH!"
            if self._AlarmStatus & ant.GNS_Alarm_Overvoltage:
                msg += " OVERVOLTAGE!"
            if self._AlarmStatus & ant.GNS_Alarm_GenericError:
                msg += " BRAKE ERROR"
            if self._AlarmStatus & ant.GNS_Alarm_Overcurrent:
                msg += " OVERCURRENT!"
            if self._AlarmStatus & ant.GNS_Alarm_SpeedTooHigh:
                msg += " SPEED TOO HIGH!"
            if self._AlarmStatus & ant.GNS_Alarm_Undervoltage:
                msg += " UNDERVOLTAGE!"
            if self._AlarmStatus & ant.GNS_Alarm_CommunicationError:
                msg += " COMMUNICATION ERROR"
            self.Message = msg
        else:
            self.Message = "Pair with Tacx Genius (can take a minute)"

    #---------------------------------------------------------------------------
    # __ConvertWind()
    #---------------------------------------------------------------------------
    # Genius-specific wind resistance/speed units
    def _ConvertWind(self, WindResistance, WindSpeed, DraftingFactor):
        return 0.5 * WindResistance * DraftingFactor * 1000, \
               -250 * WindSpeed / 3.6

    #---------------------------------------------------------------------------
    # SendToTrainer()
    #---------------------------------------------------------------------------
    def SendToTrainer(self, QuarterSecond, TacxMode):
        messages = []
        if self.__State == GeniusState.Running:
            # ---------------------------------------------------------------
            # Normal operation (non-calibration) handled by base class
            # ---------------------------------------------------------------
            super().SendToTrainer(QuarterSecond, TacxMode)
        elif self.__State == GeniusState.RequestCalibrationInfo and QuarterSecond:
            # ---------------------------------------------------------------
            # Request calibration info (repeat until response received)
            # ---------------------------------------------------------------
            info = ant.msgPage220_04_TacxGeniusCalibration(self.Channel,
                        ant.GNS_Calibration_Action_Request_Info)
            msg = ant.ComposeMessage(ant.msgID_BroadcastData, info)
            messages.append(msg)

            if debug.on(debug.Function):
                logfile.Write(
                    "Genius page 220/0x04 (OUT)  CalibrationAction=%d" % \
                    ant.GNS_Calibration_Action_Request_Info)
        elif self.__State == GeniusState.RequestCalibration and QuarterSecond:
            # ---------------------------------------------------------------
            # Request calibration (repeat until response received)
            # ---------------------------------------------------------------
            info = ant.msgPage220_04_TacxGeniusCalibration(self.Channel,
                                                           ant.GNS_Calibration_Action_Start)
            msg = ant.ComposeMessage(ant.msgID_BroadcastData, info)
            messages.append(msg)

            if debug.on(debug.Function):
                logfile.Write(
                    "Genius page 220/0x04 (OUT)  CalibrationAction=%d" % \
                    ant.GNS_Calibration_Action_Start)

            self.__CheckCalibrationTimeout()
        elif self.__State in [GeniusState.CalibrationStarted, GeniusState.CalibrationRunning] \
                and QuarterSecond:
            RequestInterval = 4
            self._CommandCounter += 1

            if self._CommandCounter >= RequestInterval:
                # ---------------------------------------------------------------
                # Request calibration info (at regular intervals)
                # ---------------------------------------------------------------
                info = ant.msgPage220_04_TacxGeniusCalibration(self.Channel,
                                                               ant.GNS_Calibration_Action_Request_Info)
                msg = ant.ComposeMessage(ant.msgID_BroadcastData, info)
                messages.append(msg)

                if debug.on(debug.Function):
                    logfile.Write(
                        "Genius page 220/0x04 (OUT)  CalibrationAction=%d" % \
                        ant.GNS_Calibration_Action_Request_Info)

                self._CommandCounter = 0

            self.__CheckCalibrationTimeout()
        elif self.__State == GeniusState.CalibrationDone or \
                self.__State == GeniusState.CalibrationFailed:
            if self.WheelSpeed > 30:
                self.__SetState(GeniusState.Running)

        #-------------------------------------------------------------------
        # Send messages, leave receiving to the outer loop
        #-------------------------------------------------------------------
        if messages:
            self.AntDevice.Write(messages, False, False)

    #---------------------------------------------------------------------------
    # HandleANTmessage()
    #---------------------------------------------------------------------------
    def HandleANTmessage(self, msg):
        _synch, _length, id, info, _checksum, _rest,\
                Channel, DataPageNumber = ant.DecomposeMessage(msg)
        SubPageNumber = info[2] if len(info) > 2 else None
        dataHandled = False
        messages = []

        if Channel == self.Channel:

            #-------------------------------------------------------------------
            # BroadcastData - info received from the master device
            #-------------------------------------------------------------------
            if id == ant.msgID_BroadcastData:
                self.tacxEvent = True
                #---------------------------------------------------------------
                # Ask what device is paired
                #---------------------------------------------------------------
                if self.__State == GeniusState.Pairing:
                    msg = ant.msg4D_RequestMessage(self.Channel, ant.msgID_ChannelID)
                    messages.append(msg)

                # -------------------------------------------------------------------
                # Data page 221 (0x04) msgUnpage221_04_TacxGeniusCalibrationInfo
                # -------------------------------------------------------------------
                if DataPageNumber == 221 and SubPageNumber == 0x04:
                    calibrationState, calibrationValue = \
                        ant.msgUnpage221_04_TacxGeniusCalibrationInfo(info)

                    if self.__State == GeniusState.Running:
                        # ignore if no calibration pending
                        pass
                    elif self.__State == GeniusState.RequestCalibrationInfo:
                        if calibrationState == ant.GNS_Calibration_State_Calibrated:
                            # already calibrated, start training
                            self.__Calibrated = True
                            self.__SetState(GeniusState.Running)
                        elif self.clv.calibrate:
                            # uncalibrated, initiate calibration
                            self.__ResetTimeout()
                            self.__SetState(GeniusState.RequestCalibration)
                        else:
                            # start training without calibration
                            self.__Calibrated = False
                            self.__SetState(GeniusState.Running)
                    elif self.__State == GeniusState.RequestCalibration:
                        if calibrationState == ant.GNS_Calibration_State_Started:
                            # calibration initiated
                            self.__SetState(GeniusState.CalibrationStarted)
                            self.__ResetTimeout()
                    else: # calibration started or running
                        if calibrationState >= ant.GNS_Calibration_State_Value_Error:
                            # error, calibration failed
                            self.__SetState(GeniusState.CalibrationFailed)
                            self.__Calibrated = False

                        elif calibrationState == ant.GNS_Calibration_State_Running:
                            # calibration is running
                            self.__SetState(GeniusState.CalibrationRunning)
                            self.__ResetTimeout()
                        elif calibrationState == ant.GNS_Calibration_State_Calibrated:
                            # calibration completed
                            self.__SetState(GeniusState.CalibrationDone)
                            self.__Calibrated = True
                            self.__CalibrationValue = calibrationValue

                    if debug.on(debug.Function):
                        logfile.Write('Genius Page=%d/%#x (IN)  CalibrationState=%d CalibrationValue=%d' %
                                      (DataPageNumber, SubPageNumber, calibrationState, calibrationValue))

                    dataHandled = True

            #-------------------------------------------------------------------
            # ChannelID - the info that a master on the network is paired
            #-------------------------------------------------------------------
            elif id == ant.msgID_ChannelID:
                Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                    ant.unmsg51_ChannelID(info)

                if DeviceTypeID == ant.DeviceTypeID_GNS:
                    self._DeviceNumber = DeviceNumber

                    # check calibration state after pairing
                    self.__SetState(GeniusState.RequestCalibrationInfo)

                dataHandled = True

        #-----------------------------------------------------------------------
        # Messages that are not Genius specific are handled by the base class
        #-----------------------------------------------------------------------
        if not dataHandled:
            dataHandled = super().HandleANTmessage(msg)

        #-----------------------------------------------------------------------
        # Send messages, leave receiving to the outer loop
        #-----------------------------------------------------------------------
        if messages:
            self.AntDevice.Write(messages, False, False)

        return dataHandled

    # --------------------------------------------------------------------------
    # D i s p l a y S t a t e T a b l e
    # --------------------------------------------------------------------------
    # input:        FortiusAntState, self.__State
    #
    # Description:  This function returns a table with texts, showing the state
    #               of FortiusAntBody, enhanced with knowledge of the trainer.
    #
    # Output:       None
    #
    # Returns:      table with texts and colour
    # --------------------------------------------------------------------------
    def DisplayStateTable(self, FortiusAntState):
       #c0 = constants.WHITE if FortiusAntState == constants.faStarted        else constants.GREY
        c1 = constants.WHITE if FortiusAntState == constants.faTrainer        else constants.GREY
       #c2 = constants.WHITE if FortiusAntState == constants.faWait2Calibrate else constants.GREY
       #c3 = constants.WHITE if FortiusAntState == constants.faCalibrating    else constants.GREY
        c4 = constants.WHITE if FortiusAntState == constants.faActivate       else constants.GREY
       #c5 = constants.WHITE if FortiusAntState == constants.faOperational    else constants.GREY
        c6 = constants.WHITE if FortiusAntState == constants.faStopped        else constants.GREY
        c7 = constants.WHITE if FortiusAntState == constants.faDeactivated    else constants.GREY
        c8 = constants.WHITE if FortiusAntState == constants.faTerminated     else constants.GREY

        c5w= constants.GREY # pairing
        c2 = constants.GREY # nudge
        c3 = constants.GREY # calibrating
        c5 = constants.GREY # operational
        if FortiusAntState == constants.faOperational:
            if self.__State == GeniusState.Pairing:
                c5w = constants.WHITE
            elif self.__State == GeniusState.CalibrationStarted:
                c2 = constants.WHITE
            elif self.__State == GeniusState.Running:
                c5 = constants.WHITE
            else:                               # All calibration states
                c3 = constants.WHITE

        # ----------------------------------------------------------------------
        # Show devices that are in-scope; not sure whethere they are present.
        # ----------------------------------------------------------------------
        device = 'ANT+'                # Of course, otherwise no genius possible
        if self.clv.ble:
            device += ', BLE'

        # ----------------------------------------------------------------------
        # Show status of FortiusAnt and Genius
        # ----------------------------------------------------------------------
       #rtn = [ [ 'FortiusAnt started',    c0 ],\       That's a line too many
        rtn = [ [ 'Tacx Genius trainer',   c1 ],\
                [ 'Activate ' + device,    c4 ],\
                [ 'Waiting for Genius',    c5w],\
                [ 'Nudge wheel forward',   c2 ],\
                [ 'Calibrating...',        c3 ],\
                [ 'Ready for training',    c5 ],\
                [ 'Trainer stopped',       c6 ],\
                [ device + ' stopped',     c7 ],\
                [ 'FortiusAnt stopped',    c8 ]]

        return rtn

#-------------------------------------------------------------------------------
# c l s T a c x A n t B u s h i d o T r a i n e r
#-------------------------------------------------------------------------------
# Tacx Bushido trainer
#-------------------------------------------------------------------------------

# Bushido state machine
class BushidoState(Enum):
    Pairing = 0,
    RequestMode = 1,
    Running = 2


class clsTacxAntBushidoTrainer(clsTacxAntTrainer):
    def __init__(self, clv, AntDevice):
        msg = "Pair with Tacx Bushido controller"
        super().__init__(clv, msg, AntDevice, ant.channel_BHU_s)

    def _ResetTrainer(self):
        super()._ResetTrainer()
        self.__State            = BushidoState.Pairing
        self.__ModeRequested    = ant.VHU_PCmode
        self.__KeepAliveTime    = time.time()
        self.__Buttons          = ant.VHU_Button_None

    def __SetState(self, state):
        if debug.on(debug.Function):
            logfile.Write("Bushido state %s -> %s" % (self.__State, state))
        self.__State = state
        self._CommandCounter = 0

        if self.__State == BushidoState.Running:
            self.Operational = True       # FortiusAnt can send/receive to brake

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
        super()._ReceiveFromTrainer()

        # ----------------------------------------------------------------------
        # Compose displayable message
        # ----------------------------------------------------------------------
        if self._DeviceNumber:
            msg = "Tacx Bushido paired: %d" % self._DeviceNumber
            if self.__State == BushidoState.RequestMode:
                msg += " - Configuring head unit"
            if self._AlarmStatus & ant.BHU_Alarm_Temperature_5 \
                    == ant.BHU_Alarm_Temperature_5:
                msg += " TEMPERATURE TOO HIGH!"
            if self._AlarmStatus & ant.BHU_Alarm_Overvoltage:
                msg += " OVERVOLTAGE!"
            if self._AlarmStatus & ant.BHU_Alarm_Overcurrent_1 or \
               self._AlarmStatus & ant.BHU_Alarm_Overcurrent_2:
                msg += " OVERCURRENT!"
            if self._AlarmStatus & ant.BHU_Alarm_SpeedTooHigh:
                msg += " SPEED TOO HIGH!"
            if self._AlarmStatus & ant.BHU_Alarm_Undervoltage:
                msg += " UNDERVOLTAGE!"
            if self._AlarmStatus & ant.BHU_Alarm_CommunicationError:
                msg += " COMMUNICATION ERROR"
            self.Message = msg
        else:
            self.Message = "Pair with Tacx Bushido controller (can take a minute)"

        # ----------------------------------------------------------------------
        # Map head unit buttons
        # ----------------------------------------------------------------------
        Keycode = self.__Buttons & 0x0F     # ignore key press duration
        if   Keycode == ant.VHU_Button_None:  self.Buttons = 0
        elif Keycode == ant.VHU_Button_Left:  self.Buttons = CancelButton
        elif Keycode == ant.VHU_Button_Up:    self.Buttons = UpButton
        elif Keycode == ant.VHU_Button_Enter: self.Buttons = OKButton
        elif Keycode == ant.VHU_Button_Down:  self.Buttons = DownButton
        elif Keycode == ant.VHU_Button_Right: self.Buttons = EnterButton
        self.__Buttons = ant.VHU_Button_None

    #---------------------------------------------------------------------------
    # __ConvertWind()
    #---------------------------------------------------------------------------
    # Bushido-specific wind resistance/speed units
    def _ConvertWind(self, WindResistance, WindSpeed, DraftingFactor):
        return 0.5 * WindResistance * DraftingFactor * 1000, \
               WindSpeed / 3.6

    # ---------------------------------------------------------------------------
    # SendToTrainer()
    # ---------------------------------------------------------------------------
    def SendToTrainer(self, QuarterSecond, TacxMode):
        messages = []

        # -------------------------------------------------------------------
        # Send keep-alive pages at regular interval to keep HU awake
        # -------------------------------------------------------------------
        KeepAliveInterval = 10  # in s
        TimeElapsed = time.time() - self.__KeepAliveTime
        if TimeElapsed > KeepAliveInterval and QuarterSecond:
            info = ant.msgPage000_TacxVortexHU_StayAlive(self.Channel)
            msg = ant.ComposeMessage(ant.msgID_BroadcastData, info)
            messages.append(msg)

            if debug.on(debug.Function):
                logfile.Write("Bushido page 0 (OUT) Keep-alive")

            # reset keep-alive timer
            self.__KeepAliveTime = time.time()

        # ---------------------------------------------------------------
        # Request mode switch (repeat until response received)
        # ---------------------------------------------------------------
        elif self.__State == BushidoState.RequestMode and QuarterSecond:
            info = ant.msgPage172_TacxVortexHU_ChangeHeadunitMode(self.Channel, self.__ModeRequested)
            msg = ant.ComposeMessage(ant.msgID_BroadcastData, info)
            messages.append(msg)

            if debug.on(debug.Function):
                logfile.Write(
                    "Bushido page 172/0x03 (OUT)  Mode=%d" % \
                    self.__ModeRequested)

        # ---------------------------------------------------------------
        # Handle normal training commands in base class
        # ---------------------------------------------------------------
        elif self.__State == BushidoState.Running:
            super().SendToTrainer(QuarterSecond, TacxMode)

        # -------------------------------------------------------------------
        # Send messages, leave receiving to the outer loop
        # -------------------------------------------------------------------
        if messages:
            self.AntDevice.Write(messages, False, False)

    # ---------------------------------------------------------------------------
    # HandleANTmessage()
    # ---------------------------------------------------------------------------
    def HandleANTmessage(self, msg):
        _synch, _length, id, info, _checksum, _rest, \
        Channel, DataPageNumber = ant.DecomposeMessage(msg)
        SubPageNumber = info[2] if len(info) > 2 else None
        dataHandled = False
        messages = []

        if Channel == self.Channel:

            if id == ant.msgID_AcknowledgedData:
                # -------------------------------------------------------------------
                # Data page 221 (0x10) msgUnpage221_TacxVortexHU_ButtonPressed
                # -------------------------------------------------------------------
                if DataPageNumber == 221 and SubPageNumber == 0x10:
                    self.__Buttons = ant.msgUnpage221_TacxVortexHU_ButtonPressed(info)

                    if debug.on(debug.Function):
                        logfile.Write('Bushido Page=%d/%#x (IN)  Keycode=%d' %
                                      (DataPageNumber, SubPageNumber, self.__Buttons))

                    dataHandled = True

            # -------------------------------------------------------------------
            # BroadcastData - info received from the master device
            # -------------------------------------------------------------------
            elif id == ant.msgID_BroadcastData:
                self.tacxEvent = True
                # ---------------------------------------------------------------
                # Ask what device is paired
                # ---------------------------------------------------------------
                if self.__State == BushidoState.Pairing:
                    msg = ant.msg4D_RequestMessage(self.Channel, ant.msgID_ChannelID)
                    messages.append(msg)
                # ---------------------------------------------------------------
                # Check head unit mode
                # ---------------------------------------------------------------
                elif self.__State == BushidoState.RequestMode:
                    # -------------------------------------------------------------------
                    # Data page 173 (0x01) msgUnpage173_01_TacxBushidoSerialMode
                    # -------------------------------------------------------------------
                    if DataPageNumber == 173 and SubPageNumber == 0x01:
                        Mode, Year, DeviceNumber = ant.msgUnpage173_01_TacxBushidoSerialMode(info)

                        if debug.on(debug.Function):
                            logfile.Write('Bushido Page=%d/%#x (IN)  Mode=%d Year=%d DeviceNumber=%d' %
                                          (DataPageNumber, SubPageNumber, Mode,
                                           Year, DeviceNumber))

                        if Mode == self.__ModeRequested:
                            if Mode == ant.VHU_PCmode:
                                # PC connection active, go to training mode
                                self.__ModeRequested = ant.VHU_TrainingPause
                            elif Mode == ant.VHU_TrainingPause:
                                # entered training mode, start training
                                self.__ModeRequested = ant.VHU_Training
                            elif Mode == ant.VHU_Training:
                                self.__SetState(BushidoState.Running)

                        dataHandled = True

                elif self.__State == BushidoState.Running:
                    # -------------------------------------------------------------------
                    # Data page 173 (0x01) msgUnpage173_01_TacxBushidoSerialMode
                    # -------------------------------------------------------------------
                    if DataPageNumber == 173 and SubPageNumber == 0x01:
                        Mode, Year, DeviceNumber = ant.msgUnpage173_01_TacxBushidoSerialMode(info)

                        if debug.on(debug.Function):
                            logfile.Write('Bushido Page=%d/%#x (IN)  Mode=%d Year=%d DeviceNumber=%d' %
                                          (DataPageNumber, SubPageNumber, Mode,
                                           Year, DeviceNumber))

                        if Mode == ant.VHU_TrainingPause:
                            # unpause the training
                            self.__ModeRequested = ant.VHU_Training
                            self.__SetState(BushidoState.RequestMode)

            # -------------------------------------------------------------------
            # ChannelID - the info that a master on the network is paired
            # -------------------------------------------------------------------
            elif id == ant.msgID_ChannelID:
                Channel, DeviceNumber, DeviceTypeID, _TransmissionType = \
                    ant.unmsg51_ChannelID(info)

                if DeviceTypeID == ant.DeviceTypeID_BHU:
                    self._DeviceNumber = DeviceNumber

                    # switch to PC mode after pairing
                    self.__SetState(BushidoState.RequestMode)

                dataHandled = True

        # -----------------------------------------------------------------------
        # Messages that are not Bushido specific are handled by the base class
        # -----------------------------------------------------------------------
        if not dataHandled:
            dataHandled = super().HandleANTmessage(msg)

        # -----------------------------------------------------------------------
        # Send messages, leave receiving to the outer loop
        # -----------------------------------------------------------------------
        if messages:
            self.AntDevice.Write(messages, False, False)

        return dataHandled

    # --------------------------------------------------------------------------
    # D i s p l a y S t a t e T a b l e
    # --------------------------------------------------------------------------
    # input:        FortiusAntState, self.__AntVHUpaired
    #
    # Description:  This function returns a table with texts, showing the state
    #               of FortiusAntBody, enhanced with knowledge of the trainer.
    #
    # Output:       None
    #
    # Returns:      table with texts and colour
    # --------------------------------------------------------------------------
    def DisplayStateTable(self, FortiusAntState):
        c0 = constants.WHITE if FortiusAntState == constants.faStarted        else constants.GREY
        c1 = constants.WHITE if FortiusAntState == constants.faTrainer        else constants.GREY
       #c2 = constants.WHITE if FortiusAntState == constants.faWait2Calibrate else constants.GREY
       #c3 = constants.WHITE if FortiusAntState == constants.faCalibrating    else constants.GREY
        c4 = constants.WHITE if FortiusAntState == constants.faActivate       else constants.GREY
       #c5 = constants.WHITE if FortiusAntState == constants.faOperational    else constants.GREY
        c6 = constants.WHITE if FortiusAntState == constants.faStopped        else constants.GREY
        c7 = constants.WHITE if FortiusAntState == constants.faDeactivated    else constants.GREY
        c8 = constants.WHITE if FortiusAntState == constants.faTerminated     else constants.GREY

        c5 = constants.GREY
        c5w= constants.GREY
        if FortiusAntState == constants.faOperational:
            if not self._DeviceNumber:
                c5w= constants.WHITE       # Waiting for Bushido
            else:
                c5 = constants.WHITE       # Operational

        # ----------------------------------------------------------------------
        # Show devices that are in-scope; not sure whethere they are present.
        # ----------------------------------------------------------------------
        device = 'ANT+'               # Of course, otherwise no bushido possible
        if self.clv.ble:
            device += ', BLE'

        # ----------------------------------------------------------------------
        # Show status of FortiusAnt and Bushido
        # ----------------------------------------------------------------------
        rtn = [ [ 'FortiusAnt started',    c0 ],\
                [ 'Tacx Bushido trainer',  c1 ],\
                [ 'Activate ' + device,    c4 ],\
                [ 'Waiting for Bushido',   c5w],\
                [ 'Ready for training',    c5 ],\
                [ 'Trainer stopped',       c6 ],\
                [ device + ' stopped',     c7 ],\
                [ 'FortiusAnt stopped',    c8 ]]

        return rtn

#-------------------------------------------------------------------------------
# c l s T a c x U s b T r a i n e r
#-------------------------------------------------------------------------------
class clsTacxUsbTrainer(clsTacxTrainer):
    #---------------------------------------------------------------------------
    # Convert WheelSpeed --> Speed in km/hr
    # SpeedScale must be defined in sub-class
    #---------------------------------------------------------------------------
    # TotalReverse wiki:
    # - 'Load' is the target speed. load_speed = 'kph * 289.75'
    # - TTS4 calibrates with value '0x16a3' and says that this is 20 kph.
    #       0x16a3 / 20 (kph) = 289.75.
    #---------------------------------------------------------------------------
    # WheelSpeed = 1 mm/sec <==> 1.000.000 / 3600 km/hr = 1/278 km/hr
    # TotalReverse: Other implementations are using values between 1/277 and 1/360.
    # WouterJD: A practical test shows that Cadence=92 gives 40km/hr at a given ratio
    #		factor 289.75 gives a slightly higher speed
    #		factor 301 would be good (8-11-2019)
    #---------------------------------------------------------------------------
    # @switchable 2020-12-02:
    # If you mean: is there some simple explanation why the factor 289.75 is? 
    # Unfortunately I did not find one. Maybe it is just related to the way the
    # speed was orignally measured on the Fortius and there isn't one.
    # What I did to calculate the factor was this: with a roll diameter of 29mm,
    # if the speed is v then it will rotate at a rate v / (29mm * pi).
    # The sensor in the brake will output 4 pulses per turn, so I set my function
    # generator to a frequency of 4 * v / (29mm * pi) to simulate riding at speed
    # v and compared the value sent over USB.
    # I also compared the value calculated by TTS and it agreed well with the
    # theoretical one. This was repeated 60 times for different speeds, the factor
    # calculated using linear regression. It may in fact be closer to 289.76, 
    # but that ist irrelevant in practice.
    # It definitely isn't 280 or 300, at least on my unit.
    #---------------------------------------------------------------------------
    def Wheel2Speed(self):
        self.SpeedKmh = round(self.WheelSpeed / self.SpeedScale, 1)

    def Speed2Wheel(self, SpeedKmh):
        return int(SpeedKmh * self.SpeedScale)
    
    # #---------------------------------------------------------------------------
    # # Refresh(); removed due to Issue 135
    # #---------------------------------------------------------------------------
    # def Refresh(self, QuarterSecond, TacxMode):
    #     super().Refresh(QuarterSecond, TacxMode)
    #     if debug.on(debug.Function):logfile.Write ("clsTacxUsbTrainer.Refresh()")

    #     # ----------------------------------------------------------------------
    #     # When a button is pressed, the button is returned a number of times,
    #     # depending on the polling-frequency. The caller would receive the same
    #     # button multiple times.
    #     # Therefore we poll the trainer untill "no button" received, only if
    #     # the last receive provided Buttons.
    #     # ----------------------------------------------------------------------
    #     Buttons = self.Buttons                  # Remember the buttons pressed

    #     while self.Buttons:                     # Loop untill no button pressed
    #         time.sleep(0.1)
    #         self._ReceiveFromTrainer()

    #     self.Buttons = Buttons                  # Restore buttons
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
        self.tacxEvent = True                   # Assume we receive correct buffer
        data = array.array('B', [])             # Empty array of bytes
        try:
            data = self.UsbDevice.read(0x82, 64, 30)
        except TimeoutError:
            self.tacxEvent = False              # No data received
            pass
        except Exception as e:
            self.tacxEvent = False              # No data received
            if "timeout error" in str(e) or "timed out" in str(e): # trainer did not return any data
                pass
            else:
                logfile.Console("Read from USB trainer error: " + str(e))

        #-----------------------------------------------------------------------
        # 24...27 is the message response header
        #-----------------------------------------------------------------------
        if len(data) > 27:
            self.Header = int(data[27]<<24 | data[26]<<16 | data[25]<<8 | data[24] )
        else:
            self.Header = -1

        if debug.on(debug.Data2):
            logfile.Write   ("Trainer recv hdr=%s data=%s (len=%s)" % \
                        (hex(self.Header), logfile.HexSpace(data), len(data)))
        
        return data

    #---------------------------------------------------------------------------
    # U S B _ R e a d _ r e t r y 4 x 4 0
    #---------------------------------------------------------------------------
    # input     UsbDevice
    #           expectedHeader: the received message must contain this header
    #               Especially at start-of-program, sometimes rubbish is received
    #               which influences the content of the MotorBrake version message
    #               causing incorrect conclusion Motor/Magnetic brake
    #
    # function  Same plus:
    #           At least 40 bytes must be returned, retry 4 times
    #---------------------------------------------------------------------------
    def USB_Read_retry4x40(self, expectedHeader = USB_ControlResponse):
        retry = 4

        while True:
            data  = self.USB_Read()

            #-------------------------------------------------------------------
            # Retry if no correct buffer received
            #-------------------------------------------------------------------
            if retry and (len(data) < 40 or self.Header != expectedHeader):
                if debug.on(debug.Any):
                    logfile.Write ( \
'Retry because short buffer (len=%s) or incorrect header received (expected: %s received: %s)' % \
                                    (len(data), hex(expectedHeader), hex(self.Header)))
                time.sleep(0.1)             # 2020-09-29 short delay @RogerPleijers
                retry -= 1
            else:
                break

        #-----------------------------------------------------------------------
        # Inform when there's something unexpected
        #-----------------------------------------------------------------------
        if len(data) < 40:
            self.tacxEvent = False
            # 2020-09-29 the buffer is ignored when too short (was processed before)
            logfile.Console('Tacx head unit returns insufficient data, len=%s' % len(data))
            if self.clv.PedalStrokeAnalysis:
                logfile.Console('To resolve, try to run without Pedal Stroke Analysis.')
            else:
                logfile.Console('To resolve, check all (signal AND power) cabling for loose contacts.')
                # 2021-04-29 On Raspberry Pi Zero W this also occurs when the
                #            system is too busy. 
                #            When the system is less busy (FortiusAnt only active
                #            process) then the message disappears automatically.
                #            A longer timeout does not help (tried: 100ms).

        elif self.Header != expectedHeader:
            self.tacxEvent = False
            logfile.Console('Tacx head unit returns incorrect header %s (expected: %s)' % \
                                        (hex(expectedHeader), hex(self.Header)))

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

    def SendToTrainerUSBData_MotorBrake(self):
        return False                                # Can be overwritten in sub-class

    def SendToTrainer(self, _QuarterSecond, TacxMode):
        assert (TacxMode in (modeStop, modeResistance, modeCalibrate, modeMotorBrake))

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
                # Weight = self.UserAndBikeWeight               # Original
                # Issue 118: Adjust virtual flywheel according to virtual gearbox
                Weight = max(0x0a, int(self.GearboxReduction * self.UserAndBikeWeight))
            else:
                error = "SendToTrainer; Unsupported TargetMode %s" % self.TargetMode

        elif TacxMode == modeCalibrate:
            Calibrate   = 0
            PedalEcho   = 0
            Target      = self.Speed2Wheel(20)                  # 20 km/h is our decision for calibration
            Weight      = 0

        elif TacxMode == modeMotorBrake:
            pass                                                # No actions required

        if error:
            logfile.Console(error)
        else:
            if TacxMode == modeMotorBrake:
                data   = self.SendToTrainerUSBData_MotorBrake()
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
        self.Operational= True                    # Always true for USB-trainers
        self.SpeedScale = 11.9 # GoldenCheetah: curSpeed = curSpeedInternal / (1.19f * 10.0f);
        #PowerResistanceFactor = (1 / 0.0036)     # GoldenCheetah ~= 277.778

        # ----------------------------------------------------------------------
        # Steering
        # ----------------------------------------------------------------------
        if self.clv.Steering == 'wired':
            self.SteeringFrame = steering.clsSteering(InitialCalLeft=-25,
                                                    InitialCalRight=25,
                                                    DeadZone=7.0)

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

        if self.clv.Resistance:
            rtn = self.TargetPower  # e.g. in manual mode you can directly set Resistance
        else:
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

        # ----------------------------------------------------------------------
        # Steering
        # ----------------------------------------------------------------------
        if self.clv.Steering == 'wired':
            axisNotConnected = 0
            if self.Axis != axisNotConnected:
                self.SteeringFrame.Update(self.Axis)
            else:
                self.SteeringFrame.Update(None)

        if debug.on(debug.Function):
            logfile.Write ("ReceiveFromTrainer() = hr=%s Buttons=%s, Cadence=%s Speed=%s TargetRes=%s CurrentRes=%s CurrentPower=%s, pe=%s %s" % \
                (  self.HeartRate, self.Buttons, self.Cadence, self.SpeedKmh, self.TargetResistance, self.CurrentResistance, self.CurrentPower, self.PedalEcho, self.Message) \
                          )

#-------------------------------------------------------------------------------
# c l s T a c x N e w U s b T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with New interface & USB connection
#
# This class implements the MotorBrake AND the MagneticBrake.
# For the time being; Creating a derived class duplicates more common code than
# simplifying it.
#-------------------------------------------------------------------------------
class clsTacxNewUsbTrainer(clsTacxUsbTrainer):
    def __init__(self, clv, Message, Headunit, UsbDevice):
        super().__init__(clv, Message)
        if debug.on(debug.Function):logfile.Write ("clsTacxNewUsbTrainer.__init__()")
        self.SpeedScale = 289.75                    # See comment above
        self.PowerResistanceFactor = 128866         # TotalReverse
        #---------------------------------------------------------------------------
        # @totalreverse Do you know how 128866 was derived?
        # TotalReverse - 11-1-2021 - https://github.com/WouterJD/FortiusANT/issues/171#issuecomment-758277058
        # The 128866 was the result of my first "fittings" a long time ago without having a power meter.
        # I do not know which program and version I used for the test, but I tried to fit the power readings and speed showed by the software with recorded values from the data frames.
        # At least for the T1941 brakes, the "1/137N" formula fits better.
        #---------------------------------------------------------------------------
        self.Headunit   = Headunit
        self.UsbDevice  = UsbDevice
        self.OK         = True
        self.Operational= True                      # Always true for USB-trainers

        self.MotorBrakeUnitFirmware = 0             # Introduced 2020-11-23
        self.MotorBrakeUnitSerial   = 0
        self.MotorBrakeUnitYear     = 0
        self.MotorBrakeUnitType     = 0             # 41 = T1941 (Fortius motorbrake)
                                                    # 01 = T1901 (Magnetic brake)
        self.Version2               = 0

        # ----------------------------------------------------------------------
        # Steering
        # ----------------------------------------------------------------------
        if self.clv.Steering == 'wired':
            self.SteeringFrame = steering.clsSteering(InitialCalLeft=-100,
                                                    InitialCalRight=100,
                                                    DeadZone=7.0)

        #---------------------------------------------------------------------------
        # Resistance values for MagneticBrake
        # - possible force values to be recv from device
        # - possible resistance value to be transmitted to device
        #
        # The head-unit only returns the values 1039...4677 in CurrentResistance.
        # the head-unit only accepts the TargetResistances 1900...3750; other values
        # are rounded down to the nearest value..
        # Sending 1000 is the same as 1900
        # Sending 2029 is the same as 1900
        # Sending 5000 is the same as 3750
        #
        # The idea behind this, why there are 14 entries, why these values and why
        # the steps between these values are not equal is the secret of the new USB
        # interface with the Magnetic brake attached.
        #---------------------------------------------------------------------------
        self.currentR = [1039, 1299, 1559, 1819, 2078, 2338, 2598, 2858, 3118, 3378, 3767, 4027, 4287, 4677]
        self.targetR  = [1900, 2030, 2150, 2300, 2400, 2550, 2700, 2900, 3070, 3200, 3350, 3460, 3600, 3750]

        #---------------------------------------------------------------------------
        # Initial state = stop
        # Do not refresh() before sending a command
        #---------------------------------------------------------------------------
        self.SendToTrainer(True, modeStop)
        time.sleep(0.1)                            # Allow head unit time to process
        self.Refresh(True, modeStop)
        time.sleep(0.1)                            # Allow head unit time to process

        #---------------------------------------------------------------------------
        # Only headunit T1932 supports Magnetic brake; all others Motor Brake only
        #---------------------------------------------------------------------------
        if self.Headunit != hu1932:
            self.MotorBrake = True

        #---------------------------------------------------------------------------
        # Check motor brake version
        #---------------------------------------------------------------------------
        retry = 4
        while True:
            self.SendToTrainer(True, modeMotorBrake)
            time.sleep(0.1)                        # Allow head unit time to process
            msgReceived = self._ReceiveFromTrainer_MotorBrake()
            time.sleep(0.1)                        # Allow head unit time to process

            if not msgReceived and retry:
                if debug.on(debug.Any):
                    logfile.Write ('Retry because no motor brake version message received')
                retry -= 1
            else:
                break
        if not msgReceived:
            logfile.Write ('No motorbrake version message received from head unit')

        #---------------------------------------------------------------------------
        # Show how we behave
        #---------------------------------------------------------------------------
        if self.MotorBrake:
            logfile.Console ("FortiusAnt applies the MotorBrake power curve")
        else:
            logfile.Console ("FortiusAnt applies the MagneticBrake power curve")

        #---------------------------------------------------------------------------
        # Refresh with stop-command
        #---------------------------------------------------------------------------
        self.SendToTrainer(True, modeStop)
        time.sleep(0.1)                        # Allow head unit time to process
        self.Refresh(True, modeStop)

        #---------------------------------------------------------------------------
        if debug.on(debug.Function):logfile.Write ("clsTacxNewUsbTrainer.__init__() done")

    #---------------------------------------------------------------------------
    # Basic physics: Power = Resistance * Speed  <==> Resistance = Power / Speed
    #---------------------------------------------------------------------------
    def CurrentResistance2Power(self):
        if self.MotorBrake:
            #-------------------------------------------------------------------
            # e.g. Tacx Fortius: Motor Brake T1941 connected to head unit T1932
            #-------------------------------------------------------------------
            self.CurrentPower = int(self.CurrentResistance / self.PowerResistanceFactor * self.WheelSpeed)

        else:
            #-------------------------------------------------------------------
            # e.g. Tacx Flow: Magnetic Brake T1901 connected to head unit T1932
            #-------------------------------------------------------------------
            self.CurrentPower = int(self.Resistance2PowerMB(self.CurrentResistance, self.SpeedKmh))

    #---------------------------------------------------------------------------
    # Power formula for Magnetic brake; thanks to @swichabl and @cyclingflow
    #---------------------------------------------------------------------------
    # The formula used is this:
    # power = speed * (scale factor * resistance * 
    #                     speed / (speed + critical speed) + rolling resistance)
    # So there are just two parameters (scale factor and critical speed) that
    # would be the same for everyone + rolling resistance which should
    # eventually be determined individually using the "runoff"/spin-down test.
    #---------------------------------------------------------------------------
    def Resistance2PowerMB(self, Resistance, SpeedKmh):
        ScaleFactor             = 0.0149   # N
        CriticalSpeed           = 4.85     # m/s

        if self.clv.CalibrateRR:
            RollingResistance = self.clv.CalibrateRR    # Value 0...100 allowed
            RollingResistance = min(100, RollingResistance)
            RollingResistance = max(  0, RollingResistance)
        else:
            RollingResistance   = 15      # N

        Speed = SpeedKmh / 3.6
        return Speed * (ScaleFactor * Resistance * Speed / (Speed + CriticalSpeed) + RollingResistance)

    def TargetPower2Resistance(self):
        rtn        = 0

        if self.clv.Resistance:
            #-------------------------------------------------------------------
            # e.g. in manual mode you can directly set Resistance
            # For the magnetic brake, there are 13 individual values
            #       knowing that we UP/DOWN by 50 Watt, divide TargetPower by 50
            #       So 0...650 Watt results in passing the targetR[] table
            #-------------------------------------------------------------------
            if self.MotorBrake:
                rtn = self.TargetPower
            else:
                i = int(self.TargetPower / 50)
                i = max(                    0, i)        # Not less than 0
                i = min(len(self.targetR) - 1, i)        # Not more than 13
                rtn = self.targetR[i]

        elif self.MotorBrake:
            #-------------------------------------------------------------------
            # e.g. Tacx Fortius: Motor Brake T1941 connected to head unit T1932
            #-------------------------------------------------------------------
            if self.WheelSpeed > 0:
                rtn = self.TargetPower * self.PowerResistanceFactor / self.WheelSpeed
                rtn = self.__AvoidCycleOfDeath(rtn)

        else:
            #-------------------------------------------------------------------
            # e.g. Tacx Flow: Magnetic Brake T1901 connected to head unit T1932
            #-------------------------------------------------------------------
            if self.WheelSpeed > 0:
                for i in range(0, len(self.currentR)):
                    if self.Resistance2PowerMB(self.currentR[i], self.SpeedKmh) >= self.TargetPower:
                        break
                rtn = self.targetR[i]

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
        Weight = int(min(0xff,   Weight))
        #-----------------------------------------------------------------------
        # Data buffer depends on trainer_type
        # Refer to TotalReverse; "Newer protocol"
        #-----------------------------------------------------------------------
        # 2021-01-14 Description appears to be extended as follows:
        # 0	0x01	command number (1 = control command)
        # 1	0x08	payload message size (0 = no payload)
        # 2	0x01	payload type (0x01 = control data?)
        # 3	0x00	never seen anything else than 0x00 - maybe high byte of little endian 16 bit?
        #
        # Therefore USB_ControlCommand  = 0x00010801 ==> CommandNumber = 1
        #       and USB_VersionRequest  = 0x00000002 ==> CommandNumber = 2
        # I do not change the code accordingly (just for sake of beauty?)
        #       in favor of stability
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

        #-----------------------------------------------------------------------
        # Avoid motor-function for low TargetPower
        # The motor-function seemed odd when this piece of code was created.
        # BUT: for people with a very low FTP (50 Watt), the resistance of the
        #      bike without brake is already more than the required power and
        #      hence motor-operation is usefull
        #
        # Is disabled with "if False"
        #
        # 2021-02-19 Test done: -m with delta power = 10Watt
        #       Calibration = approximately 37 Watt
        #       Requested power 90..80..70..60..50..40 Watt: normal behaviour
        #                       30..20..10..0 Watt: motor starts to help
        #                       There still is a slight feeling to cycle.
        #       Conclusion: also in PowerMode, Target may drop below Calibrate.
        #-----------------------------------------------------------------------
        if False and self.TargetMode == mode_Power and Target < Calibrate:
            Target = Calibrate        

        #-----------------------------------------------------------------------
        # Build data buffer to be sent to trainer (legacy or new)
        #-----------------------------------------------------------------------
        self.ControlCommand = USB_ControlCommand
        format = sc.no_alignment + fControlCommand + fTarget + fPedalecho + fFiller7 + fMode +    fWeight + fCalibrate
        data   = struct.pack (format, self.ControlCommand,Target, PedalEcho,        TacxMode,  int(Weight),  Calibrate)
        return data

    #---------------------------------------------------------------------------
    # S e n d T o T r a i n e r D a t a _ M o t o r B r a k e
    #---------------------------------------------------------------------------
    # input     None
    #
    # function  Called by SendToTrainer()
    #           Compose buffer to ask for Motor Brake Version
    #
    # returns   data
    #---------------------------------------------------------------------------
    def SendToTrainerUSBData_MotorBrake(self):
        #-----------------------------------------------------------------------
        # Data buffer "T1941 Motor Brake Version Message", refer to TotalReverse
        # https://github.com/totalreverse/ttyT1941/wiki#t1941-motor-brake-commands-and-answers
        #-----------------------------------------------------------------------
        fControlCommand     = sc.unsigned_int       # 0...3

        #-----------------------------------------------------------------------
        # Build data buffer to be sent to trainer
        #-----------------------------------------------------------------------
        self.ControlCommand = USB_VersionRequest
        format = sc.no_alignment + fControlCommand
        data   = struct.pack (format, self.ControlCommand)
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
        # Read from trainer
        # 64 bytes are expected
        # 48 bytes are returned by some trainers
        # 24 bytes are sometimes returned (T1932, Gui Leite 2020-06-11) and
        #           seem to be incomplete buffers and are ignored.
        # Also my own tacx returns empty buffers, very seldomly though
        #-----
        # TotalReverse, 2020-09-27:
        # One more Information: the brake only sends an answer after receiving a
        # command from the head unit. And the 1942 head unit only sends a command
        # to the brake after receiving a frame from the host.
        # You first have to increase the send rate to receive more frames
        # (answers) from the brake.
        #
        # 2020-09-29 Practice shows that retry works; if not a message is given.
        # Then the buffer is ignored to avoid returning wrong data. The outer
        # loop will send a command and then receive again.
        # Perhaps just ignoring the short buffer would be enough as well, but
        # this has been tested and found working so I leave it.
        #
        # 2020-11-18 sleep() only done when too short buffer received
        #   As said this SHOULD occur seldomly; if frequently it's bad behaviour
        #   at this location. It is logged so that we don't mis it.
        #-----------------------------------------------------------------------
        # 2021-01-14 Description appears to be extended as follows:
        # Header			Size: 4 bytes
        # 24	0	0x03	command number (answer command)
        # 25	1	0x13	payload data size 19
        # 26	2	0x02	payload type number (0x02 = control answer)
        # 27	3	0x00	never seen anything else than 0x00 - maybe high byte of little endian 16 bit?
        #
        # Therefore USB_ControlResponse = 0x00021303 ==> CommandResponse = 3
        #       and USB_VersionResponse = 0x00000c03 ==> CommandResponse = 3
        # As in SendToTrainerUSBData() I do not change the code accordingly.
        #-----------------------------------------------------------------------
        data  = self.USB_Read_retry4x40()

        if len(data) < 40:
            pass
        else:
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

            _nHeader            = 10                # 24-27
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
            #self.Header            = tuple[nHeader]   filled in USB_Read already
            self.HeartRate          = tuple[nHeartRate]
            self.PedalEcho          = tuple[nEvents]
            self.TargetResistanceFT = tuple[nTargetResistance]
            self.WheelSpeed         = tuple[nSpeed]

            self.Wheel2Speed()
            self.CurrentResistance2Power()

            # ----------------------------------------------------------------------
            # Steering
            # ----------------------------------------------------------------------
            if self.clv.Steering == 'wired':
                axisNotConnected = 0x0a0d
                if self.Axis != axisNotConnected:
                    # Invert axis value so lower value -> left (not right)
                    self.SteeringFrame.Update(-self.Axis)
                else:
                    self.SteeringFrame.Update(None)

            if debug.on(debug.Function):
                logfile.Write ("ReceiveFromTrainer() = hr=%s Buttons=%s Cadence=%s Speed=%s TargetRes=%s CurrentRes=%s CurrentPower=%s, pe=%s hdr=%s %s" % \
                            (  self.HeartRate, self.Buttons, self.Cadence, self.SpeedKmh, self.TargetResistanceFT, self.CurrentResistance, self.CurrentPower, self.PedalEcho, hex(self.Header), self.Message) \
                            )
    #---------------------------------------------------------------------------
    # R e c e i v e F r o m T r a i n e r
    #---------------------------------------------------------------------------
    # input     usbDevice
    #
    # function  Read status from trainer
    #
    # output    self.MotorBrake and MotorBrake values
    #
    # returns   True/False for correct message received
    #---------------------------------------------------------------------------
    def _ReceiveFromTrainer_MotorBrake(self):
        if debug.on(debug.Function):logfile.Write ("clsTacxNewUsbTrainer._ReceiveFromTrainer_MotorBrake()...")
        #-----------------------------------------------------------------------
        # Define default
        # From 2020-01-11: MotorBrake is the default
        #                  When a correct message is received with Serial=0
        #                  then it is a MagneticBrake
        # And when explicitly specified (-t) then that value overrules.
        #-----------------------------------------------------------------------
        self.MotorBrake = True
        rtn             = False

        #-----------------------------------------------------------------------
        # Read from trainer
        #-----------------------------------------------------------------------
        data  = self.USB_Read_retry4x40(USB_VersionResponse)

        if len(data) < 40:
            pass
        else:
            #-------------------------------------------------------------------
            # Define buffer format
            #-------------------------------------------------------------------
            fFiller0_23             = sc.pad * 24       #  0...23

            _nHeader                = 0
            fHeader                 = sc.unsigned_int   # 24...27

            nMotorBrakeUnitFirmware = 1
            fMotorBrakeUnitFirmware = sc.unsigned_int   # 28...31   0.x.y.z

            nMotorBrakeUnitSerial   = 2                 # 32...35   tt-YY-##### (tt=41 (T1941), YY=year,
            fMotorBrakeUnitSerial   = sc.unsigned_int   #                 ##### brake individual serial)

            nVersion2               = 3                 # 36, 37
            fVersion2               = sc.unsigned_short

            fFiller38_63            = sc.pad * (63-37)  # 38...63

            format = sc.no_alignment + fFiller0_23 + fHeader + fMotorBrakeUnitFirmware + \
                        fMotorBrakeUnitSerial + \
                        fVersion2 + fFiller38_63

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
            #self.Header                = tuple[nHeader]   filled in USB_Read already
            self.MotorBrakeUnitFirmware = tuple[nMotorBrakeUnitFirmware]
            self.MotorBrakeUnitSerial   = tuple[nMotorBrakeUnitSerial]
            self.Version2               = tuple[nVersion2]

            #-----------------------------------------------------------------------
            # Split serial; all decimal digits = tt-yy-#####
            # Note that ##### may be any length; e.g. 1903!
            #-----------------------------------------------------------------------
            s = str(self.MotorBrakeUnitSerial)
            self.MotorBrakeUnitType     = 0
            self.MotorBrakeUnitYear     = 0
            Serial                      = 0
            try:
                self.MotorBrakeUnitType = int(s[0:2])
                self.MotorBrakeUnitYear = int(s[2:4])
                Serial                  = int(s[4:])
            except:
                pass

            #-----------------------------------------------------------------------
            # If T1941 or T1946 motorbrake, then calibration is supported AND
            #       a different PowerCurve is used.
            #
            # Note that Headunit T1932 does not return a value for T1901
            #       Note that, only the T1932 controls a magnetic brake.
            #
            # #173 The possible motor brakes are T1941 (230V) and T1946 (110V)
            #       Controlled by T1932 and T1942 headunits.
            #-----------------------------------------------------------------------
            if self.MotorBrakeUnitType in (41, 46, 49):
                self.MotorBrake = True

            if self.MotorBrakeUnitSerial == 0:
                self.MotorBrake = False

            #-----------------------------------------------------------------------
            # Important enough; always display
            #-----------------------------------------------------------------------
            if self.MotorBrakeUnitSerial == 0:
                logfile.Console ("Motor Brake Unit Firmware=%s Serial=%s MotorBrake=%s" % \
                                (   hex(self.MotorBrakeUnitFirmware), Serial, self.MotorBrake) \
                                )
            else:
                logfile.Console ("Motor Brake Unit Firmware=%s Serial=%5s year=%s type=T19%s Version2=%s MotorBrake=%s" % \
                                (   hex(self.MotorBrakeUnitFirmware), Serial, \
                                    self.MotorBrakeUnitYear + 2000, self.MotorBrakeUnitType, \
                                    self.Version2, self.MotorBrake) \
                                )

            #-----------------------------------------------------------------------
            # Correct message received
            #-----------------------------------------------------------------------
            rtn = True

        #---------------------------------------------------------------------------
        # If specified, take that value (regardless what happend before!!)
        #---------------------------------------------------------------------------
        if self.clv.Tacx_MotorBrake:    self.MotorBrake = True
        if self.clv.Tacx_MagneticBrake: self.MotorBrake = False

        #---------------------------------------------------------------------------
        # Return that a correct message is received
        # This does NOT reflect whether is a Motor- of Magnetic brake!
        #---------------------------------------------------------------------------
        if debug.on(debug.Function):logfile.Write ("... returns %s" % rtn)
        return rtn