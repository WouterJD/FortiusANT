#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
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

import debug
import logfile
import structConstants   as sc
import FortiusAntGui     as gui
import FortiusAntCommand as cmd

#-------------------------------------------------------------------------------
# Globals
#-------------------------------------------------------------------------------
global trainer_type

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
# Convert Power (Watt) <--> Resistance (presumably Nm)
#
#            Power = Torque (Nm) * Speed (rad/s)
# <==>       Power = Resistance * WheelSpeed / factor 
# and   Resistance = Power / WheelSpeed * factor
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
PowerResistanceFactor = 128866 
def Resistance2Power(Resistance, WheelSpeed):
    return round(Resistance / PowerResistanceFactor * WheelSpeed, 1)

def Power2Resistance(PowerInWatt, WheelSpeed, Cadence):
    if WheelSpeed > 0:
        rtn = PowerInWatt * PowerResistanceFactor / WheelSpeed
        rtn = ResistanceAtLowSpeed(WheelSpeed, rtn)
    else:
        rtn = ResistanceAtLowSpeed(WheelSpeed, 6666)
    return rtn

# Limit Resistance
# (interface maximum = 0x7fff = 32767)
# at low speed, Fortius does not manage higher resistance
# at high speed, the rider does not
def ResistanceAtLowSpeed(WheelSpeed, Resistance):
    if Wheel2Speed(WheelSpeed) <= 15 and Resistance >= 6000:
        Resistance = int(max(1000, Wheel2Speed(WheelSpeed) / 15 * 6000))
    return Resistance

#-------------------------------------------------------------------------------
# Convert WheelSpeed --> Speed in km/hr
# WheelSpeed = 1 mm/sec <==> 1.000.000 / 3600 km/hr = 1/278 km/hr
# TotalReverse: Other implementations are using values between 1/277 and 1/360.
# A practical test shows that Cadence=92 gives 40km/hr at a given ratio 
#		factor 289.75 gives a slightly higher speed
#		factor 301 would be good (8-11-2019)
#-------------------------------------------------------------------------------
SpeedScale = 301							        # TotalReverse: 289.75
def Wheel2Speed(WheelSpeed):
    return round(WheelSpeed / SpeedScale, 1)

def Speed2Wheel(Speed):
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
def Grade2Resistance(TargetGrade, UserAndBikeWeight, WheelSpeed, Cadence):
    if TargetGrade < -20 or TargetGrade > 30:
        logfile.Write("SendToTrainer; TargetGrade (%s) out of bounds!" % (TargetGrade))

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

        if limit:
            MaxRes = Power2Resistance(clv.ftp * 1.25, WheelSpeed, Cadence)
            rtn = int(min(MaxRes, rtn))       # Limit resistance to my max
            rtn = int(max(     0, rtn))       # No negative target resistance

    elif option == 2:
        #-----------------------------------------------------------------------
        # TargetGrade ftp-based ergo mode
        # Resistance depends on the TargetGrade and the current WheelSpeed
        # Power is lineair between -10% and 10%, independant on speed
        #-----------------------------------------------------------------------
        P_max = clv.ftp * 1.50                                              # Power at grade =  10%
        P_min = clv.ftp * 0.00                                              # Power at grade = -10%
        P     = P_min + ( (P_max - P_min) / 20 * (TargetGrade + 10) )   # TargetPower

        if limit:
            P = max( 0.5  * clv.ftp, P)                                     # Minimum value
            P = min( 1.25 * clv.ftp, P)                                     # Maximum value
        P = int(P)
        rtn   = Power2Resistance(P, WheelSpeed, Cadence)
        
        if debug.on(debug.Application):
            logfile.Write ("2: Grade=%4.1f, max=%3s, min=%3s, power=%3s, resistance=%5s" % (TargetGrade, P_max, P_min, P, rtn) )

    elif option == 3:
        #-----------------------------------------------------------------------
        # TargetGrade ftp-based resistance mode; 
        #   I ride all in highest gear to get maximum WheelSpeed (best for Fortius)
        #   Adjusting cadence (wheelspeed) influences required power.
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
        w     = Speed2Wheel(d * rpm * 60 / 1000)# mm/sec   WheelSpeed
        P_max = clv.ftp * clv.ResistanceH / 100 # Watt     higher power
        R_max = Power2Resistance(P_max, w, rpm) # Resistance for this WheelSpeed at 50 rpm

        #------------------------------ Calculation for -20%, high cadence, 1 ftp
        down  = -20                             # %        slope gradient
        rpm   = 100                             # /min     high cadence
        d     = clv.tyre * clv.fL / clv.rS      # m        distance for one pedal-revolution
        w     = Speed2Wheel(d * rpm * 60 / 1000)# mm/sec   WheelSpeed
        P_min = clv.ftp * clv.ResistanceL / 100 # Watt     lower power
        R_min = Power2Resistance(P_min, w, rpm) # Resistance for this WheelSpeed at 100 rpm

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
        P       = PfietsNL(TargetGrade, UserAndBikeWeight, WheelSpeed)

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

        P_fiets = PfietsNL(10, UserAndBikeWeight, w)         # Power at 10%up at 50 rpm in highest gear
        factor  = min(1, P_max / P_fiets) # Reduction factor; <= 1
        if TargetGrade < 0: factor = 1

        #-----------------------------------------------------------------------
        # Reduce Target power with a constant factor to get to 1.5ftp at 10%
        # Resistance remains dependant on the TargetGrade (not the current speed)
        #-----------------------------------------------------------------------
        Px      = P * factor

        #-----------------------------------------------------------------------
        # Translate power to resistance at the current wheelspeed
        # Note that Power2Resistance() has its own limitations
        #-----------------------------------------------------------------------
        rtn     = Power2Resistance(Px, WheelSpeed, Cadence)
            
        if debug.on(debug.Application):
            logfile.Write ("%4.1f%%, P=%3.0fW(%3.0fW), R=%4.0f f=%4.2f" % \
                     (TargetGrade, P,     Px,        rtn,  factor) )

    rtn = ResistanceAtLowSpeed(WheelSpeed, rtn)

    return rtn

def PfietsNL(TargetGrade, UserAndBikeWeight, WheelSpeed):
        #-----------------------------------------------------------------------
        # Thanks to https://www.fiets.nl/2016/05/02/de-natuurkunde-van-het-fietsen/
        # Required power = roll + air + slope + mechanical
        #-----------------------------------------------------------------------
        c     = 0.004                           # roll-resistance constant
        m     = UserAndBikeWeight               # kg
        g     = 9.81                            # m/s2
        v     = Wheel2Speed(WheelSpeed) / 3.6   # m/s       km/hr * 1000 / 3600
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

  #---------------------------------------------------------------------------
  # Initialize
  #---------------------------------------------------------------------------
  if debug.on(debug.Function):logfile.Write ("GetTrainer()")
  trainer_type = 0
  idpl = [0x1932, 0x1942, 0xe6be]       # iflow, fortius, uninitialised fortius

  #---------------------------------------------------------------------------
  # Find supported trainer
  #---------------------------------------------------------------------------
  msg = "GetTrainer - No trainer found"
  for idp in idpl:
    try:
        if debug.on(debug.Function): logfile.Write ("GetTrainer - Check for trainer %s" % (hex(idp)))
        dev = usb.core.find(idVendor=0x3561, idProduct=idp)     # find trainer USB device
        if dev != None:
          msg = "GetTrainer - Trainer found: " + hex(idp)
          if debug.on(debug.Function):
            print (dev)
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
  else:                                                                         # found trainer
    #---------------------------------------------------------------------------
    # unintialised 1942 (not tested!!)
    #---------------------------------------------------------------------------
    if trainer_type == 0xe6be:                                                  
      if debug.on(debug.Function): logfile.Write ("GetTrainer - Found uninitialised 1942 head unit")
      try:
        os.system("fxload-libusb.exe -I FortiusSWPID1942Renum.hex -t fx -vv")   # load firmware
        if debug.on(debug.Function): logfile.Write ("GetTrainer - Initialising head unit, please wait 5 seconds")
        time.sleep(5)
        dev = usb.core.find(idVendor=0x3561, idProduct=0x1942)
        if dev != None:
          msg = "GetTrainer - 1942 head unit initialised"
          trainer_type = 0x1942
        else:
          msg = "GetTrainer - Unable to load firmware"
          dev = False
      except:                                                                   # not found
        msg = "GetTrainer - Unable to initialise trainer"
        dev = False
      
    #---------------------------------------------------------------------------
    # Set configuration
    #---------------------------------------------------------------------------
    dev.set_configuration()
  #---------------------------------------------------------------------------
  # Done
  #---------------------------------------------------------------------------
  logfile.Write(msg)
  if debug.on(debug.Function):logfile.Write ("GetTrainer() returns, trainertype=" + hex(trainer_type))
  return dev, msg
  
#-------------------------------------------------------------------------------
#  I n i t i a l i s e T r a i n e r
#-------------------------------------------------------------------------------
def InitialiseTrainer(dev):
    # will not read cadence until initialisation byte is sent
    data = struct.pack (sc.unsigned_int, 0x00000002)

    if debug.on(debug.Data2):
        logfile.Write ("InitialiseTrainer data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))

    dev.write(0x02,data)


#-------------------------------------------------------------------------------
# S e n d T o T r a i n e r
#-------------------------------------------------------------------------------
# input     devTrainer, Mode
#           if Mode=modeResistance:  TargetPower or TargetGrade/Weight
#                                    WheelSpeed and Cadence are reference for Power2Resistance
#           PedalEcho   - must be echoed
#           Calibrate   - Resistance during calibration is specified
#                         If =zero default is calculated
#
# function  Set trainer to calculated resistance (TargetPower) or Grade
#
# returns   None
#-------------------------------------------------------------------------------
def SendToTrainer(devTrainer, Mode, TargetMode, TargetPower, TargetGrade, UserAndBikeWeight, PedalEcho, WheelSpeed, Cadence, Calibrate, SimulateTrainer):
    if debug.on(debug.Function): logfile.Write ("SendToTrainer(%s, %s, %s, %s, %s, %s, %s)" % (TargetMode, TargetPower, TargetGrade, UserAndBikeWeight, PedalEcho, WheelSpeed, Cadence))
    
    fControlCommand     = sc.unsigned_int       # 0...3
    fTarget             = sc.short              # 4, 5      Resistance for Power=50...1000Watt
    fPedalecho          = sc.unsigned_char      # 6
    fFiller7            = sc.pad                # 7
    fMode               = sc.unsigned_char      # 8         Idle=0, Ergo/Slope=2, Calibrate/speed=3
    fWeight             = sc.unsigned_char      # 9         Ergo: 0x0a; Weight = ride + bike in kg
    fCalibrate          = sc.unsigned_short     # 10, 11    Depends on mode

    error = False
    if   Mode == modeStop:
        Calibrate   = 0
        PedalEcho   = 0
        Target      = 0
        Weight      = 0
        pass

    elif Mode == modeResistance:
        if Calibrate == 0:                              # Use old formula:
            Calibrate   = 0                             # may be -8...+8
            Calibrate   = ( Calibrate + 8 ) * 130       # 0x0410

        if TargetMode == gui.mode_Power:
            Target      = Power2Resistance(TargetPower, WheelSpeed, Cadence)
            if Target < Calibrate: Target = Calibrate   # Avoid motor-function for low TargetPower
            Weight      = 0x0a                          # weight=0x0a is a good fly-wheel value
                                                        # UserAndBikeWeight is not used!
        elif TargetMode == gui.mode_Grade:
            Target      = Grade2Resistance(TargetGrade, UserAndBikeWeight, WheelSpeed, Cadence)
########    if Target < Calibrate: Target = Calibrate   # Avoid motor-function for descends
            Weight      = 0x0a                          # weight=0x0a is a good fly-wheel value
                                                        # UserAndBikeWeight is not used!    
                                                        #       an 100kg flywheels gives undesired behaviour :-)
        else:
            error = "SendToTrainer; Unsupported TargetMode %s" % TargetMode

    elif Mode == modeCalibrate:
        Calibrate   = 0
        PedalEcho   = 0
        Target      = Speed2Wheel(20)
        Weight      = 0

    else:
        error = "SendToTrainer; incorrect Mode %s!" % Mode

    if error:
        logfile.Write(error)
    else:
        format = sc.no_alignment + fControlCommand + fTarget +    fPedalecho + fFiller7 + fMode + fWeight + fCalibrate
        data   = struct.pack (format, 0x00010801, int(Target),     PedalEcho,              Mode,   Weight,   Calibrate)

        if debug.on(debug.Data2):
            logfile.Write ("Trainer send data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
            logfile.Write ("                  target=%s pe=%s mode=%s weight=%s cal=%s" % \
                                         (int(Target), PedalEcho, Mode, Weight, Calibrate))

        if not SimulateTrainer:
            try:
                devTrainer.write(0x02, data, 30)                             # send data to device
            except Exception as e:
                logfile.Write ("SendToTrainer: USB WRITE ERROR " + str(e))
  
#-------------------------------------------------------------------------------
# R e c e i v e F r o m T r a i n e r
#-------------------------------------------------------------------------------
# input     devTrainer     
#
# function  Read status from trainer
#
# returns   Speed, WheelSpeed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, Buttons
#
# changes   2020-01-07 originally 'TargetResistance' was returned
#                      for calibration, now CurrentResistance is also returned
#               Caller must decide which one to use
#-------------------------------------------------------------------------------
def ReceiveFromTrainer(devTrainer):
  global trainer_type
  if debug.on(debug.Function):logfile.Write ("ReceiveFromTrainer()")

  Axis              = 0
  Buttons           = 0
  Cadence           = 0
  CurrentPower      = 0
  CurrentResistance = 0
  HeartRate         = 0
  PedalEcho         = 0
  Speed             = 0
  TargetResistance  = 0
  WheelSpeed        = 0

  #-----------------------------------------------------------------------------
  #  Read from trainer
  #-----------------------------------------------------------------------------
  try:
    data = devTrainer.read(0x82, 64, 30)
  except Exception as e:
    if "timeout error" in str(e):#trainer did not return any data
      pass
    else:
      logfile.Write ("ReceiveFromTrainer: USB READ ERROR: " + str(e))
    data = ""
  if debug.on(debug.Data2):logfile.Write ("Trainer recv data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))

  #-----------------------------------------------------------------------------
  #  Handle data when > 40 bytes                Will fail when less than struct.calcsize(format)
  #-----------------------------------------------------------------------------
  if len(data)>40:
    #---------------------------------------------------------------------------
    # Define buffer format
    #---------------------------------------------------------------------------
    nDeviceSerial       =  0                # 0...1
    fDeviceSerial       = sc.unsigned_short

    fFiller2_7          = sc.pad * ( 7 - 1) # 2...7

    nYearProduction     =  1                # 8
    fYearProduction     = sc.unsigned_char

    fFiller9_11         = sc.pad * (11 - 8) # 9...11

    nHeartRate          =  2                # 12
    fHeartRate          = sc.unsigned_char

    nButtons            =  3                # 13
    fButtons            = sc.unsigned_char

    nHeartDetect        =  4                # 14
    fHeartDetect        = sc.unsigned_char

    nErrorCount         =  5                # 15
    fErrorCount         = sc.unsigned_char

    nAxis0              =  6                # 16-17
    fAxis0              = sc.unsigned_short

    nAxis1              =  7                # 18-19
    fAxis1              = sc.unsigned_short

    nAxis2              =  8                # 20-21
    fAxis2              = sc.unsigned_short

    nAxis3              =  9                # 22-23
    fAxis3              = sc.unsigned_short

    nHeader             = 10                # 24-27
    fHeader             = sc.unsigned_int

    nDistance           = 11                # 28-31
    fDistance           = sc.unsigned_int

    nSpeed              = 12                # 32, 33            Wheel speed (Speed = WheelSpeed / SpeedScale in km/h)
    fSpeed              = sc.unsigned_short

    fFiller34_35        = sc.pad * 2        # 34...35           Increases if you accellerate?
    fFiller36_37        = sc.pad * 2        # 34...35           Average power?

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

    nModeEcho           = 17                # 46
    fModeEcho           = sc.unsigned_char

    nChecksumLSB        = 18                # 47
    fChecksumLSB        = sc.unsigned_char

    nChecksumMSB        = 19                # 48
    fChecksumMSB        = sc.unsigned_char

    fFiller49_63        = sc.pad * (63 - 48)# 49...63
        
    format = sc.no_alignment + fDeviceSerial + fFiller2_7 + fYearProduction + \
             fFiller9_11 + fHeartRate + fButtons + fHeartDetect + fErrorCount + \
             fAxis0 + fAxis1 + fAxis2 + fAxis3 + fHeader + fDistance + fSpeed + \
             fFiller34_35 + fFiller36_37 + fCurrentResistance + fTargetResistance + \
             fEvents + fFiller43 + fCadence + fFiller45 + fModeEcho + \
             fChecksumLSB + fChecksumMSB + fFiller49_63
    #---------------------------------------------------------------------------
    # Parse buffer
    #---------------------------------------------------------------------------
    tuple = struct.unpack (format, data)
    if debug.on(debug.Data2):
      logfile.Write ("ReceiveFromTrainer: TargetResistance=%s hr=%s sp=%s CurrentResistance=%s pe=%s cad=%s axis=%s %s %s %s" % \
                    (tuple[nTargetResistance], tuple[nHeartRate], tuple[nSpeed],      \
                    tuple[nCurrentResistance], hex(tuple[nEvents]), tuple[nCadence], \
                    tuple[nAxis0], tuple[nAxis1], tuple[nAxis2], tuple[nAxis3]  \
                    ))

    WheelSpeed          = tuple[nSpeed]

    Cadence             = tuple[nCadence]
    CurrentPower        = Resistance2Power(tuple[nCurrentResistance], WheelSpeed)
    HeartRate           = tuple[nHeartRate]
    PedalEcho           = tuple[nEvents]
    TargetResistance    = tuple[nTargetResistance]
    CurrentResistance   = tuple[nCurrentResistance]
    Speed               = Wheel2Speed(tuple[nSpeed])
    
    Buttons             = tuple[nButtons]
    Axis                = tuple[nAxis1]

  else:
    Speed = "Not Found"

  return Speed, WheelSpeed, PedalEcho, HeartRate, CurrentPower, Cadence, TargetResistance, CurrentResistance, Buttons, Axis