#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-05-07"
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
import struct
import sys
import time

import debug
import logfile
import structConstants   as sc
from   FortiusAntGui                import mode_Power, mode_Grade
import FortiusAntCommand as cmd
import fxload

#-------------------------------------------------------------------------------
# Globals
#-------------------------------------------------------------------------------
global trainer_type;    trainer_type     = 0
global LegacyProtocol;  LegacyProtocol   = False

tt_iMagic        = 0x1902    # Old "solid green" iMagic headunit (with or without firmware)
tt_iMagicWG      = 0x1904    # New "white green" iMagic headunit (firmware inside)
tt_Fortius       = 0x1932    # New "white blue" Fortius headunit (firmware inside)
tt_FortiusSB     = 0x1942    # Old "solid blue" Fortius (firmware inside)
tt_FortiusSB_nfw = 0xe6be    # Old "solid blue" Fortius (without firmware)

idVendor_Tacx    = 0x3561

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
EnterButton     = 1
DownButton      = 2
UpButton        = 4
CancelButton    = 8

modeStop        = 0
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
# Convert Power (Watt) <--> Resistance (presumably Nm)
#
#            Power = Torque (Nm) * Speed (rad/s)
# <==>       Power = Resistance * Speed / factor
# and   Resistance = Power / Speed * factor
#
# We assume resistance is something like Nm
#    know   WheelSpeed is mm/s
#    know   Power      is Watt
#-------------------------------------------------------------------------------
# The resistance is calculated above 10 km/hr and 30 rpm
# a. protect against divide-by-zero
# b. obviously rider does not meet up required power (so give him a brake)
# c. tacx fortius does not work well at (or above) 200W at 10km/h
#
# ad c. 200 W and 10 km/hr
#       R = 200 * 128866 / (10 * 301) = 8562
#
#       Tacx Fortius is said to have a range of 50...1000Watt,
#           let's calculate at 50km/hr:
#       R = 1000 * 128866 / (50 * 301) = 8562
#           I leave it to you to test whether you can go over this resistance at
#           high speeds :-)
#
#    My personal experience already showed that the Tacx Fortius works well
#       at higher speeds and here is the explanation!
#
#    Conclusion: for rider with ftp=250 (or more) who wants to do low-speed,
#       low-cadence (MTB) training, this is not the machine!
#-------------------------------------------------------------------------------
# legacyResistance2Power and vv for iMagic, using legacy protocol
# Thanks to GoldenCheetah / GoldenCheetah / master / src / Train / Imagic.cpp
#-------------------------------------------------------------------------------
PowerResistanceFactor = 128866                  # TotalReverse
legacyPowerResistanceFactor = (1 / 0.0036)      # GoldenCheetah ~= 277.778

def Resistance2Power(Resistance, SpeedKmh):
    global LegacyProtocol

    if LegacyProtocol:
        if SpeedKmh == 0:
            return 0
        else:
            # GoldenCheetah: curPower = ((curResistance * 0.0036f) + 0.2f) * curSpeedInternal;
            # return round(((Resistance / legacyPowerResistanceFactor) + 0.2) * WheelSpeed, 1)

            # ref https://github.com/WouterJD/FortiusANT/wiki/Power-calibrated-with-power-meter-(iMagic)
            return round(Resistance * (SpeedKmh* SpeedKmh / 648 + SpeedKmh / 5411 + 0.1058) + 2.2 * SpeedKmh, 1)
    else:
        WheelSpeed = Speed2Wheel(SpeedKmh)
        return round(Resistance / PowerResistanceFactor * WheelSpeed, 1)

def Power2Resistance(PowerInWatt, SpeedKmh, Cadence):
    global LegacyProtocol

    WheelSpeed = Speed2Wheel(SpeedKmh)

    if LegacyProtocol:
        rtn = 0
        if WheelSpeed > 0:
            # instead of brakeCalibrationFactor use PowerFactor -p
            # GoldenCheetah: setResistance = (((load  / curSpeedInternal) - 0.2f) / 0.0036f)
            #                setResistance *= brakeCalibrationFactor
            # rtn = ((PowerInWatt / WheelSpeed) - 0.2) * legacyPowerResistanceFactor

            # ref https://github.com/WouterJD/FortiusANT/wiki/Power-calibrated-with-power-meter-(iMagic)
            rtn = (PowerInWatt - 2.2 * SpeedKmh) / (SpeedKmh * SpeedKmh / 648 + SpeedKmh / 5411 + 0.1058)

        # Check bounds
        rtn = int(min(226, rtn)) # Maximum value; as defined by Golden Cheetah
        rtn = int(max( 30, rtn)) # Minimum value

    else:
        if WheelSpeed > 0:
            rtn = PowerInWatt * PowerResistanceFactor / WheelSpeed
            rtn = ResistanceAtLowSpeed(SpeedKmh, rtn)
        else:
            rtn = ResistanceAtLowSpeed(SpeedKmh, 6666)

    return rtn

# Limit Resistance
# (interface maximum = 0x7fff = 32767)
# at low speed, Fortius does not manage higher resistance
# at high speed, the rider does not
def ResistanceAtLowSpeed(SpeedKmh, Resistance):
    if SpeedKmh <= 15 and Resistance >= 6000:
        Resistance = int(max(1000, SpeedKmh / 15 * 6000))
    return Resistance

#-------------------------------------------------------------------------------
# Convert WheelSpeed --> Speed in km/hr
# WheelSpeed = 1 mm/sec <==> 1.000.000 / 3600 km/hr = 1/278 km/hr
# TotalReverse: Other implementations are using values between 1/277 and 1/360.
# A practical test shows that Cadence=92 gives 40km/hr at a given ratio
#		factor 289.75 gives a slightly higher speed
#		factor 301 would be good (8-11-2019)
#-------------------------------------------------------------------------------
SpeedScale = 301         # TotalReverse: 289.75
SpeedScale_Legacy = 11.9 # GoldenCheetah: curSpeed = curSpeedInternal / (1.19f * 10.0f);
def Wheel2Speed(WheelSpeed):
    global LegacyProtocol

    if LegacyProtocol:
        return round(WheelSpeed / SpeedScale_Legacy, 2)
    else:
        return round(WheelSpeed / SpeedScale, 2)

def Speed2Wheel(Speed):
    global LegacyProtocol

    if LegacyProtocol:
        return round(Speed * SpeedScale_Legacy, 0)
    else:
        return round(Speed * SpeedScale, 0)

#-------------------------------------------------------------------------------
# Convert Grade (slope) to resistance
#
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
#-------------------------------------------------------------------------------
# Refer to ANT msgUnpage51_TrackResistance()
#          where zwift grade does not seem to match the definition
#-------------------------------------------------------------------------------
def Grade2Resistance(TargetGrade, UserAndBikeWeight, SpeedKmh, Cadence):
    global LegacyProtocol

    if TargetGrade < -20 or TargetGrade > 30:
        logfile.Console("Grade2Resistance; TargetGrade (%s) out of bounds!" % (TargetGrade))

    if UserAndBikeWeight == 0: UserAndBikeWeight = 80

    clv = cmd.Get()     # clv = Command Line Variables
    option = 3          # 2020-01-15 after testing my preferred option is #3!
    limit  = True

    if option == 1:
        #-----------------------------------------------------------------------
        # Formula from TotalReverse
        # BUT: result is zero for TargetGrade=0
        #      result is negative for downhill; which is supported by Tacx Fortius
        #             but that's about the only one, ANT does not support it
        #             and it seems zwift does not understand it
        #             without produced power, zwift does not provide speed
        #             and at -5% the motorbrake starts pushing, so power=negative
        #
        # (grade=10 - 0.4) * 137 * g=9.81 / 100 * weight=90  results in r=11.611
        #             and that is a resistance I cannot handle
        # (grade=-5 - 0.4) * 137 * g=9.81 / 100 * weight=90  results in r=-6.531
        #           which makes the brake to drive the wheel,
        #           resulting that I cannot 'produce' power and Zwift says speed=0
        #-----------------------------------------------------------------------
        SlopeScale  = 137 * 9.81 / 100         # To be multiplied with UserAndBikeWeight
        SlopeOffset = -0.4
        rtn = int ( (TargetGrade - SlopeOffset) * SlopeScale * UserAndBikeWeight )

        if LegacyProtocol:
            # Resistance is calculated for new interface, convert to Legacy
            p   = Resistance2Power(rtn, SpeedKmh)
            rtn = Power2Resistance(p, SpeedKmh, Cadence)

        if limit:
            MaxRes = Power2Resistance(clv.ftp * 1.25, SpeedKmh, Cadence)
            rtn = int(min(MaxRes, rtn))       # Limit resistance to my max
            rtn = int(max(     0, rtn))       # No negative target resistance

    elif option == 2:
        #-----------------------------------------------------------------------
        # TargetGrade ftp-based ergo mode
        # Resistance depends on the TargetGrade and the current speed
        # Power is lineair between -10% and 10%, independant on speed
        #-----------------------------------------------------------------------
        P_max = clv.ftp * 1.50                                              # Power at grade =  10%
        P_min = clv.ftp * 0.00                                              # Power at grade = -10%
        P     = P_min + ( (P_max - P_min) / 20 * (TargetGrade + 10) )   # TargetPower

        if limit:
            P = max( 0.5  * clv.ftp, P)                                     # Minimum value
            P = min( 1.25 * clv.ftp, P)                                     # Maximum value
        P = int(P)
        rtn   = Power2Resistance(P, SpeedKmh, Cadence)

        if debug.on(debug.Application):
            logfile.Write ("2: Grade=%4.1f, max=%3s, min=%3s, power=%3s, resistance=%5s" % (TargetGrade, P_max, P_min, P, rtn) )

    elif option == 3:
        #-----------------------------------------------------------------------
        # TargetGrade ftp-based resistance mode;
        #   I ride all in highest gear to get maximum speed (best for Fortius)
        #   Adjusting cadence (speed) influences required power.
        #   No nead to change gears, although you are free to do so!
        #
        # Resistance depends on the TargetGrade (not the current speed)
        # Resistance is lineair between -20% and 20%, Power increases with speed
        #
        # To ride in highest gear only (no shifting) two checkpoints are used
        # - at  50rpm (higher power, lowest cadence)
        # - at 100rpm (lower  power, highest cadence)
        #
        # 2020-01-13 Test: this basically works well
        #            Even a tough track (-10% ... +20%) can be done (Zwift Muir)
        # 2020-01-15 Formula's made as clear as possible
        #            Ready for parameterization through command lineair
        #            with bike = (2.096,50/34,15/25) it will be easy to customize
        #            Effects can be visualized in related excel sheet
        #
        #            I use fS=fL and rS=rS so I do not need to change gears.
        # 2020-01-15 Tested with Zwift and it works well.
        #            Power is well distributed and gear-shifting has the
        #            expected effect.
        #            The ftp-based powercurve is realized and customizable!
        # 2020-01-16 Parameters moved to command-line
        #-----------------------------------------------------------------------
        #------------------------------ Bicycle constants (command line defined)
        # tyre  = 2.096                           # m        tyre circumference
        # fL    = 50                              # teeth    chain wheel front / large
        # fS    = 50  # 34                        # teeth    chain wheel front / small
        # rL    = 15  # 25                        # teeth    cassette back / large
        # rS    = 15                              # teeth    cassette back / small


        #------------------------------ Calculation for +20%, low cadence, 1.5 ftp
        up    = 20                              # %        slope gradient
        rpm   = 50                              # /min     low cadence
        d     = clv.tyre * clv.fS / clv.rL      # m        distance for one pedal-revolution
        s     = d * rpm * 60 / 1000             # km/hr    speed
        P_max = clv.ftp * clv.ResistanceH / 100 # Watt     higher power
        R_max = Power2Resistance(P_max, s, rpm) # Resistance for this speed at 50 rpm

        #------------------------------ Calculation for -20%, high cadence, 1 ftp
        down  = -20                             # %        slope gradient
        rpm   = 100                             # /min     high cadence
        d     = clv.tyre * clv.fL / clv.rS      # m        distance for one pedal-revolution
        s     = d * rpm * 60 / 1000             # km/hr    speed
        P_min = clv.ftp * clv.ResistanceL / 100 # Watt     lower power
        R_min = Power2Resistance(P_min, s, rpm) # Resistance for this speed at 100 rpm

        #--------------------------------------- Calculation for TargetGrade
        rtn   = int(R_min + ( (R_max - R_min) / (up - down) * (TargetGrade - down) ) )

        if debug.on(debug.Application):
            logfile.Write ("3: Grade=%4.1f, R_max=%4.0f, R_min=%4.0f, resistance=%4.0f" % (TargetGrade, R_max, R_min, rtn) )

    else:
        #-----------------------------------------------------------------------
        # Let's start with the basic formula.
        # Resistance depends on the TargetGrade (not the current speed)
        # But target resistance at steep slopes (8%...20%) cannot be done and
        #       you must gear down seriously.
        #-----------------------------------------------------------------------
        P       = PfietsNL(TargetGrade, UserAndBikeWeight, SpeedKmh)

        #-----------------------------------------------------------------------
        # Initial versions limitted P to 1.50ftp
        # But that means that the curve is maximized (e.g. at 5% and then remains
        #   flat until 20% which takes away the slope-effect)
        # Old formula: P = min (1.50 * ftp, P)
        #-----------------------------------------------------------------------

        #-----------------------------------------------------------------------
        # Let's learn from "ftp-based resistance mode" (read there)
        # Let's establish a factor so that 10%/50 rpm will require 1.50ftp
        #-----------------------------------------------------------------------
        rpm     = 50                      # /min     cadence
        d       = 2.096 * 50 / 17         # m        distance for one pedal-revolution
        w       = d * rpm / 60 * 1000     # mm/sec   WheelSpeed
        P_max   = clv.ftp * 1.50          # Watt     higher power

        P_fiets = PfietsNL(10, UserAndBikeWeight, Wheel2Speed(w))         # Power at 10%up at 50 rpm in highest gear
        factor  = min(1, P_max / P_fiets) # Reduction factor; <= 1
        if TargetGrade < 0: factor = 1

        #-----------------------------------------------------------------------
        # Reduce Target power with a constant factor to get to 1.5ftp at 10%
        # Resistance remains dependant on the TargetGrade (not the current speed)
        #-----------------------------------------------------------------------
        Px      = P * factor

        #-----------------------------------------------------------------------
        # Translate power to resistance at the current speed
        # Note that Power2Resistance() has its own limitations
        #-----------------------------------------------------------------------
        rtn     = Power2Resistance(Px, SpeedKmh, Cadence)

        if debug.on(debug.Application):
            logfile.Write ("%4.1f%%, P=%3.0fW(%3.0fW), R=%4.0f f=%4.2f" % \
                     (TargetGrade, P,     Px,        rtn,  factor) )

    rtn = ResistanceAtLowSpeed(SpeedKmh, rtn)

    return rtn

def PfietsNL(TargetGrade, UserAndBikeWeight, SpeedKmh):
        #-----------------------------------------------------------------------
        # Thanks to https://www.fiets.nl/2016/05/02/de-natuurkunde-van-het-fietsen/
        # Required power = roll + air + slope + mechanical
        #-----------------------------------------------------------------------
        c     = 0.004                           # roll-resistance constant
        m     = UserAndBikeWeight               # kg
        g     = 9.81                            # m/s2
        v     = SpeedKmh / 3.6                  # m/s       km/hr * 1000 / 3600
        Proll = c * m * g * v                   # Watt

        p     = 1.205                           # air-density
        cdA   = 0.3                             # resistance factor
        w     =  0                              # wind-speed
        Pair  = 0.5 * p * cdA * (v+w)*(v+w)* v  # Watt

        i     = TargetGrade
        Pslope= i/100 * m * g * v               # Watt

        Pbike = 37

        return Proll + Pair + Pslope + Pbike

#-------------------------------------------------------------------------------
# G e t T r a i n e r
#-------------------------------------------------------------------------------
# input     none
#
# function  find USB trainer
#
# returns   devTrainer, msg
#-------------------------------------------------------------------------------
def GetTrainer():
    global trainer_type
    global LegacyProtocol
    #---------------------------------------------------------------------------
    # Initialize
    #---------------------------------------------------------------------------
    if debug.on(debug.Function):logfile.Write ("GetTrainer()")
    trainer_type     = 0
    LegacyProtocol   = False

    #---------------------------------------------------------------------------
    # Find supported trainer
    #---------------------------------------------------------------------------
    msg = "No Tacx trainer found"
    for idp in [tt_iMagic, tt_iMagicWG, tt_Fortius, tt_FortiusSB, tt_FortiusSB_nfw]:
        try:
            if debug.on(debug.Function): logfile.Write ("GetTrainer - Check for trainer %s" % (hex(idp)))
            dev = usb.core.find(idVendor=idVendor_Tacx, idProduct=idp)      # find trainer USB device
            if dev != None:
                msg = "Connected to Tacx Trainer T" + hex(idp)[2:]          # remove 0x from result, was "Trainer found:"
                if debug.on(debug.Data2 | debug.Function):
                    logfile.Print (dev)
                trainer_type = idp
                break
        except Exception as e:
            if debug.on(debug.Function): logfile.Write ("GetTrainer - " + str(e))

            if "AttributeError" in str(e):
                msg = "GetTrainer - Could not find USB trainer: " + str(e)
            elif "No backend" in str(e):
                msg = "GetTrainer - No backend, check libusb: " + str(e)
            else:
                msg = "GetTrainer: " + str(e)

    #---------------------------------------------------------------------------
    # Initialise trainer (if found)
    #---------------------------------------------------------------------------
    if trainer_type == 0:
        dev = False
    else:                                                        # found trainer
        #-----------------------------------------------------------------------
        # iMagic            As defined together with fritz-hh and jegorvin)
        #-----------------------------------------------------------------------
        if trainer_type == tt_iMagic:
            LegacyProtocol = True
            if debug.on(debug.Function): logfile.Write ("GetTrainer - Found iMagic head unit")
            try:
                fxload.loadHexFirmware(dev, imagic_fw)
                if debug.on(debug.Function): logfile.Write ("GetTrainer - Initialising head unit, please wait 5 seconds")
                time.sleep(5)
                msg = "GetTrainer - iMagic head unit initialised"
            except:                                                  # not found
                msg = "GetTrainer - Unable to initialise trainer"
                dev = False

        #-----------------------------------------------------------------------
        # unintialised Fortius (as provided by antifier original code)
        #-----------------------------------------------------------------------
        if trainer_type == tt_FortiusSB_nfw:
            if debug.on(debug.Function): logfile.Write ("GetTrainer - Found uninitialised Fortius head unit")
            try:
                fxload.loadHexFirmware(dev, fortius_fw)
                if debug.on(debug.Function): logfile.Write ("GetTrainer - Initialising head unit, please wait 5 seconds")
                time.sleep(5)
                dev = usb.core.find(idVendor=idVendor_Tacx, idProduct=tt_FortiusSB)
                if dev != None:
                    msg = "GetTrainer - Fortius head unit initialised"
                    trainer_type = tt_FortiusSB
                else:
                    msg = "GetTrainer - Unable to load firmware"
                    dev = False
            except:                                                     # not found
                msg = "GetTrainer - Unable to initialise trainer"
                dev = False

        #-----------------------------------------------------------------------
        # Set configuration
        #-----------------------------------------------------------------------
        if dev != False:
            dev.set_configuration()
            if trainer_type == tt_iMagic:   dev.set_interface_altsetting(0, 1)

        #-----------------------------------------------------------------------
        # InitialiseTrainer (will not read cadence until initialisation byte is sent)
        #-----------------------------------------------------------------------
        if dev != False and LegacyProtocol == False:
            data = struct.pack (sc.unsigned_int, 0x00000002)
            if debug.on(debug.Data2):
                logfile.Write ("InitialiseTrainer data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
            dev.write(0x02,data)

    #---------------------------------------------------------------------------
    # Done
    #---------------------------------------------------------------------------
    logfile.Console(msg)
    if debug.on(debug.Function):logfile.Write ("GetTrainer() returns, trainertype=" + hex(trainer_type))
    return dev, msg


#-------------------------------------------------------------------------------
# S e n d T o T r a i n e r
#-------------------------------------------------------------------------------
# input     devTrainer, Mode
#           if Mode=modeResistance:  TargetPower or TargetGrade/Weight
#                                    Speed and Cadence are reference for Power2Resistance
#               in mode_Grade: PowercurveFactor increments/decrements resistance
#           PedalEcho   - must be echoed
#           Calibrate   - Resistance during calibration is specified
#                         If =zero default is calculated
#           LegacyProtocol (for iMagic)
#
# function  Set trainer to calculated resistance (TargetPower) or Grade
#
# returns   None
#-------------------------------------------------------------------------------
def SendToTrainer(devTrainer, Mode, TargetMode, TargetPower, TargetGrade,
                    PowercurveFactor, UserAndBikeWeight, \
                    PedalEcho, SpeedKmh, Cadence, Calibrate, SimulateTrainer):
    global LegacyProtocol # As filled in GetTrainer()

    if debug.on(debug.Function): logfile.Write ("SendToTrainer(%s, %s, %s, %s, %s, %s, %s, %s)" % (Mode, TargetMode, TargetPower, TargetGrade, UserAndBikeWeight, PedalEcho, SpeedKmh, Cadence))

    #---------------------------------------------------------------------------
    # Data buffer depends on trainer_type
    # Refer to TotalReverse; "Legacy protocol" or "Newer protocol"
    #---------------------------------------------------------------------------
    if LegacyProtocol == True:
        fDesiredForceValue  = sc.unsigned_char      # 0         0x00-0xff
                                                    #           0x80 = field switched off
                                                    #           < 0x80 reduce brake force
                                                    #           > 0x80 increase brake force
        fStartStop          = sc.unsigned_char      # 1         0x01 = pause/start manual control
                                                    #           0x02 = autopause if wheel < 20
                                                    #           0x04 = autostart if wheel >= 20
        fStopWatch          = sc.unsigned_int       # 2...5
    else:
        fControlCommand     = sc.unsigned_int       # 0...3
        fTarget             = sc.short              # 4, 5      Resistance for Power=50...1000Watt
        fPedalecho          = sc.unsigned_char      # 6
        fFiller7            = sc.pad                # 7
        fMode               = sc.unsigned_char      # 8         Idle=0, Ergo/Slope=2, Calibrate/speed=3
        fWeight             = sc.unsigned_char      # 9         Ergo: 0x0a; Weight = ride + bike in kg
        fCalibrate          = sc.unsigned_short     # 10, 11    Depends on mode

    #---------------------------------------------------------------------------
    # Prepare parameters to be sent to trainer
    #---------------------------------------------------------------------------
    error = False
    if   Mode == modeStop:
        Calibrate   = 0
        PedalEcho   = 0
        Target      = 0
        Weight      = 0
        pass

    elif Mode == modeResistance:
        if Calibrate == 0:                                  # Use old formula:
            Calibrate   = 0                                 # may be -8...+8
            Calibrate   = ( Calibrate + 8 ) * 130           # 0x0410

        if TargetMode == mode_Power:
            Target = Power2Resistance(TargetPower, SpeedKmh, Cadence)
            # Target *= PowercurveFactor                    # manual adjustment of requested resistance
                                                            # IS NOT permitted: When trainer software
                                                            # asks for 100W, you will get 100Watt!
            if LegacyProtocol == False and Target < Calibrate:
                Target = Calibrate                          # Avoid motor-function for low TargetPower
            Weight = 0x0a                                   # weight=0x0a is a good fly-wheel value
                                                            # UserAndBikeWeight is not used!
        elif TargetMode == mode_Grade:
            Target = Grade2Resistance(TargetGrade, UserAndBikeWeight, SpeedKmh, Cadence)
            Target *= PowercurveFactor                      # manual adjustment of requested resistance
            Weight = 0x0a                                   # weight=0x0a is a good fly-wheel value
                                                            # UserAndBikeWeight is not used!
                                                            #       an 100kg flywheels gives undesired behaviour :-)
        else:
            error = "SendToTrainer; Unsupported TargetMode %s" % TargetMode

    elif Mode == modeCalibrate:
        Calibrate   = 0
        PedalEcho   = 0
        Target      = Speed2Wheel(20)                       # 20 km/h is our decision for calibration
        Weight      = 0

    else:
        error = "SendToTrainer; incorrect Mode %s!" % Mode

    if error:
        logfile.Console(error)
    else:
        #-----------------------------------------------------------------------
        # Build data buffer to be sent to trainer (legacy or new)
        #-----------------------------------------------------------------------
        if LegacyProtocol == True:
            if Mode == modeResistance:
                DesiredForceValue = Target
                StartStop, StopWatch = 0,0  # GoldenCheetah sends 2-byte data
                                            #    in sendRunCommand() with
                                            #    StartStop always zero
                                            # so we should be good like this
                format = sc.no_alignment + fDesiredForceValue + fStartStop + fStopWatch
                data   = struct.pack (format, DesiredForceValue, StartStop, StopWatch)
            else:
                data   = False
        else:
            format = sc.no_alignment + fControlCommand + fTarget +    fPedalecho + fFiller7 + fMode + fWeight + fCalibrate
            data   = struct.pack (format, 0x00010801, int(Target),     PedalEcho,              Mode,   Weight,   Calibrate)

        #-----------------------------------------------------------------------
        # Send buffer to trainer
        #-----------------------------------------------------------------------
        if not SimulateTrainer and data != False:
            if debug.on(debug.Data2):
                logfile.Write ("Trainer send data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
                logfile.Write ("                  target=%s pe=%s mode=%s weight=%s cal=%s" % \
                                             (int(Target), PedalEcho, Mode, Weight, Calibrate))

            try:
                devTrainer.write(0x02, data, 30)                             # send data to device
            except Exception as e:
                logfile.Console("SendToTrainer: USB WRITE ERROR " + str(e))

#-------------------------------------------------------------------------------
# R e c e i v e F r o m T r a i n e r
#-------------------------------------------------------------------------------
# input     devTrainer
#
# function  Read status from trainer
#
# returns   Speed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, Buttons
#
# changes   2020-01-07 originally 'TargetResistance' was returned
#                      for calibration, now CurrentResistance is also returned
#               Caller must decide which one to use
#-------------------------------------------------------------------------------
def ReceiveFromTrainer(devTrainer):
    global trainer_type

    Axis              = 0
    Buttons           = 0
    Cadence           = 0
    CurrentPower      = 0
    CurrentResistance = 0
    Error             = ""
    HeartRate         = 0
    PedalEcho         = 0
    Speed             = 0
    TargetResistance  = 0

    #-----------------------------------------------------------------------------
    #  Read from trainer
    #-----------------------------------------------------------------------------
    data = ""
    try:
        data = devTrainer.read(0x82, 64, 30)
    except TimeoutError:
        pass
    except Exception as e:
        if "timeout error" in str(e) or "timed out" in str(e): # trainer did not return any data
            pass
        else:
            logfile.Console("ReceiveFromTrainer: USB READ ERROR: " + str(e))
    if debug.on(debug.Data2):logfile.Write ("Trainer recv data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))

    #-----------------------------------------------------------------------------
    # Handle data when > 40 bytes (boundary as derived from antifier)
    #-----------------------------------------------------------------------------
    if len(data) > 40 and LegacyProtocol == False:
        #---------------------------------------------------------------------------
        # Define buffer format
        #---------------------------------------------------------------------------
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

        #---------------------------------------------------------------------------
        # Buffer must be 64 characters (struct.calcsize(format)),
        # Note that tt_FortiusSB returns 48 bytes only; append with dummy
        #---------------------------------------------------------------------------
        for _v in range( 64 - len(data) ):
            data.append(0)

        #---------------------------------------------------------------------------
        # Parse buffer
        #---------------------------------------------------------------------------
        tuple = struct.unpack (format, data)
        Cadence             = tuple[nCadence]
        HeartRate           = tuple[nHeartRate]
        PedalEcho           = tuple[nEvents]
        TargetResistance    = tuple[nTargetResistance]
        CurrentResistance   = tuple[nCurrentResistance]
        Speed               = Wheel2Speed(tuple[nSpeed])
        CurrentPower        = Resistance2Power(tuple[nCurrentResistance], Speed)

        Buttons             = tuple[nButtons]
        Axis                = tuple[nAxis1]

    elif LegacyProtocol == True:
        #---------------------------------------------------------------------------
        # Define buffer format
        #---------------------------------------------------------------------------
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

        #---------------------------------------------------------------------------
        # Parse buffer
        # Note that the button-bits have an inversed logic:
        #   1=not pushed, 0=pushed. Hence the xor.
        #---------------------------------------------------------------------------
        format = sc.no_alignment + fStatusAndCursors + fSpeed + fCadence + fHeartRate + fStopWatch + fCurrentResistance + \
                 fPedalSensor + fAxis0 + fAxis1 + fAxis2 + fAxis3 + fCounter + fWheelCount + \
                 fYearProduction + fDeviceSerial + fFirmwareVersion
        tuple = struct.unpack (format, data)

        Cadence             = tuple[nCadence]
        HeartRate           = tuple[nHeartRate]
        PedalEcho           = tuple[nPedalSensor]
        CurrentResistance   = tuple[nCurrentResistance]
        TargetResistance    = CurrentResistance         # Is not separately returned
                                                        # is displayed by FortiusANT!
        Speed               = Wheel2Speed(tuple[nSpeed])
        Buttons             = ((tuple[nStatusAndCursors] & 0xf0) >> 4) ^ 0x0f
        Axis                = tuple[nAxis1]

        CurrentPower        = Resistance2Power(CurrentResistance, Speed)

    else:
        Error = "Not Found"

    if debug.on(debug.Function):
          logfile.Write ("ReceiveFromTrainer() = hr=%s Cadence=%s Speed=%s TargetRes=%s CurrentRes=%s CurrentPower=%s, pe=%s %s" % \
                                          (  HeartRate,   Cadence,   Speed, TargetResistance, CurrentResistance, CurrentPower, PedalEcho, Error) \
                        )

    return Error, Speed, PedalEcho, HeartRate, CurrentPower, Cadence, TargetResistance, CurrentResistance, Buttons, Axis

#-------------------------------------------------------------------------------
# C a l i b r a t e S u p p o r t e d
#-------------------------------------------------------------------------------
# input     trainer_type
#
# function  Return whether this trainer support calibration
#
# returns   True/False
#-------------------------------------------------------------------------------
def CalibrateSupported():
    global trainer_type
    if trainer_type == tt_Fortius:              # And perhaps others as well
        return True
    else:
        return False
