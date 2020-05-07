#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-05-07"
# 2020-05-07    usbTrainer refactored for the following reasons:
#               - attributes are now stored in one place and not passed to
#                   functions and returned to callers; in the end it was
#                   unclear what values was changed where and by whome
#               - separate Tacx-dependant code into their own classes
#               - enable further improvement on the Grade2Resistance
#                   algorithm in one separated location
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
# Constants
#-------------------------------------------------------------------------------
hu1902          = 0x1902    # Old "solid green" iMagic headunit (with or without firmware)
hu1904          = 0x1904    # New "white green" iMagic headunit (firmware inside)
hu1932          = 0x1932    # New "white blue" Fortius headunit (firmware inside)
hu1942          = 0x1942    # Old "solid blue" Fortius (firmware inside)
hue6be_nfw      = 0xe6be    # Old "solid blue" Fortius (without firmware)

idVendor_Tacx   = 0x3561

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
# Class inheritance:
# ------------------
# clsTacxTrainer ->                     clsSimulatedTrainer
#                -> clsTacxUsbTrainer   clsHeadUnitLegacyUsb
#                                                               ...|-> clsUsbTrainer.headunit
#                -> clsHeadUnitNew -> clsHeadUnitNewUsb          .../
#                                 -> clsHeadUnitNewAntVortex
#-------------------------------------------------------------------------------
# c l s T a c x T r a i n e r           The parent for all trainers
#-------------------------------------------------------------------------------
class clsTacxTrainer():
    UsbDevice               = None          # clsHeadUnitLegacy and clsHeadUnitNew only!
    AntDevice               = None          # clsVortexTrainer only!
    TargetMode              = mode_Power    # Start with power mode
    TargetGrade             = None          # no grade
    TargetPower             = 100           # and 100Watts
    TargetResistance        = None          # calculated and input to trainer

    UserAndBikeWeight       = 75 + 10       # defined according the standard (data page 51)

    Cadence                 = None          # below variables provided by trainer
    CurrentPower            = None
    CurrentResistance       = None
    HeartRate               = None
    PedalEcho               = None
    SpeedKmh                = None
    TargetResistanceFT      = None          # Returned from trainer
    WheelSpeed              = None

    clv                     = None          # Command line variables
    PowercurveFactor        = 1             #

    # USB devices only:
    Headunit                = None
    Calibrate               = None
    SpeedScale              = None          # To be set in sub-class
    #---------------------------------------------------------------------------
    # G e t T r a i n e r
    #---------------------------------------------------------------------------
    # Function      Create a TacxTrainer-child class, depending on the 
    #               circumstances.
    #
    # Returns       Object of a TacxTrainer sub-class
    #---------------------------------------------------------------------------
    @staticmethod                       # pretent to be c++ factory function
    def GetTrainer(clv, AntDevice=None):
        if debug.on(debug.Function):logfile.Write ("GetTrainer()")

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
        dev             = None
        LegacyProtocol  = False

        #-----------------------------------------------------------------------
        # Find supported trainer (actually we talk to a headunit)
        #-----------------------------------------------------------------------
        for hu in [hu1902, hu1904, hu1932, hu1942, hue6be_nfw]:
            try:
                if debug.on(debug.Function):
                    logfile.Write ("GetTrainer - Check for trainer %s" % (hex(hu)))
                dev = usb.core.find(idVendor=idVendor_Tacx, idProduct=hu)      # find trainer USB device
                if dev != None:
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
        if hu == 0:
            dev = False
        else:                                                    # found trainer
            #-------------------------------------------------------------------
            # iMagic             As defined together with fritz-hh and jegorvin)
            #-------------------------------------------------------------------
            if hu == hu1902:
                LegacyProtocol = True
                if debug.on(debug.Function):
                    logfile.Write ("GetTrainer - Found 1902 head unit (iMagic)")
                try:
                    fxload.loadHexFirmware(dev, imagic_fw)
                    if debug.on(debug.Function):
                        logfile.Write ("GetTrainer - Initialising head unit, please wait 5 seconds")
                    time.sleep(5)
                    msg = "GetTrainer - 1902 head unit initialised (iMagic)"
                except:                                              # not found
                    msg = "GetTrainer - Unable to initialise trainer"
                    dev = False

            #-------------------------------------------------------------------
            # unintialised Fortius (as provided by antifier original code)
            #-------------------------------------------------------------------
            if hu == hue6be_nfw:
                if debug.on(debug.Function):
                    logfile.Write ("GetTrainer - Found uninitialised 1942 head unit (Fortius)")
                try:
                    fxload.loadHexFirmware(dev, fortius_fw)
                    if debug.on(debug.Function):
                        logfile.Write ("GetTrainer - Initialising head unit, please wait 5 seconds")
                    time.sleep(5)
                    dev = usb.core.find(idVendor=idVendor_Tacx, idProduct=hu1942)
                    if dev != None:
                        msg = "GetTrainer - 1942 head unit initialised (Fortius)"
                        hu = hu1942
                    else:
                        msg = "GetTrainer - Unable to load firmware"
                        dev = False
                except:                                              # not found
                    msg = "GetTrainer - Unable to initialise trainer"
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
        if LegacyProtocol:
            return clsTacxLegacyUsbTrainer(clv, hu, dev, msg)
        else:
            return clsTacxNewUsbTrainer(clv, hu, dev, msg)

    #---------------------------------------------------------------------------
    # Functions from external to provide data
    #---------------------------------------------------------------------------
    def SetPower(self, Power):
        self.TargetMode         = mode_power    # pylint: disable=undefined-variable
        self.TargetGrade        = None          # .Refresh() must be called
        self.TargetPower        = Power
        self.TargetResistance   = None          # .Refresh() must be called

    def SetGrade(self, Grade):
        self.TargetMode         = mode_grade    # pylint: disable=undefined-variable
        self.TargetGrade        = Grade
        self.TargetPower        = None          # .Refresh() must be called
        self.TargetResistance   = None          # .Refresh() must be called

    def SetUserAndBikeWeigth(self, UserAndBikeWeight):
        self.UserAndBikeWeight  = UserAndBikeWeight

    #---------------------------------------------------------------------------
    # R e f r e s h
    #---------------------------------------------------------------------------
    # Input         Class variables Target***
    #
    # Function      Refresh updates the actual values from the trainer
    #               Then does required calculations
    #               And finally instructs the trainer what to do
    #
    #               It appears more logical to do calculations when inputs change
    #               but it's done here for two reasons:
    #               - some calculations depend on the wheelspeed, so must be 
    #                 redone after each ReceiveFromTrainer()
    #               - ??? I had another one
    # 
    # Output        Class variables match with Target***
    #---------------------------------------------------------------------------
    def Refresh(self, TacxMode=modeResistance):
        self.ReceiveFromTrainer()

        assert (self.TargetMode in (mode_power, mode_grade))# pylint: disable=undefined-variable

        if self.TargetMode == mode_power:                   # pylint: disable=undefined-variable
            self.TargetResistance = self.Power2Resistance(self.TargetPower)

        elif self.TargetMode == mode_grade:                 # pylint: disable=undefined-variable
            self.Grade2Power()
            self.TargetResistance = self.Power2Resistance(self.TargetPower)

        self.SendToTrainer(TacxMode)

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
    # Functions to be defined in sub-class
    #---------------------------------------------------------------------------
    def ReceiveFromTrainer(self):
        raise NotImplementedError
    def Power2Resistance(self, P):
        raise NotImplementedError
    def Resistance2Power(self, R):             
        raise NotImplementedError

    #---------------------------------------------------------------------------
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
    #---------------------------------------------------------------------------
    # Refer to ANT msgUnpage51_TrackResistance()
    #          where zwift grade does not seem to match the definition
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    # Input         TargetGrade
    #
    # Function      Calculate what power must be produced, given the current
    #               grade, speed and weigth
    # 
    # Output        TargetPower
    #---------------------------------------------------------------------------
    def Grade2Power(self):
        if self.TargetGrade < -20 or self.TargetGrade > 30:
            logfile.Console("Grade2Resistance; TargetGrade (%s) out of bounds!" % (self.TargetGrade))

        if self.UserAndBikeWeight < 70:
            self.UserAndBikeWeight = 75 + 10

        self.TargetPower = self.__PfietsNL()

        if debug.on(debug.Application):
            logfile.Write ("%4.1f%%, P=%3.0fW, R=%4.0f" % \
                (self.TargetGrade, self.TargetPower, self.TargetResistance) )

    def __PfietsNL(self):
        #-----------------------------------------------------------------------
        # Thanks to https://www.fiets.nl/2016/05/02/de-natuurkunde-van-het-fietsen/
        # Required power = roll + air + slope + mechanical
        #-----------------------------------------------------------------------
        c     = 0.004                           # roll-resistance constant
        m     = self.UserAndBikeWeight          # kg
        g     = 9.81                            # m/s2
        v     = self.SpeedKmh / 3.6             # m/s       km/hr * 1000 / 3600
        Proll = c * m * g * v                   # Watt

        p     = 1.205                           # air-density
        cdA   = 0.3                             # resistance factor
        w     =  0                              # wind-speed
        Pair  = 0.5 * p * cdA * (v+w)*(v+w)* v  # Watt

        i     = self.TargetGrade
        Pslope= i/100 * m * g * v               # Watt

        Pbike = 37

        return Proll + Pair + Pslope + Pbike
        
    #-------------------------------------------------------------------------------
    # Convert WheelSpeed --> Speed in km/hr
    # SpeedScale must be defined in sub-class
    #-------------------------------------------------------------------------------
    # WheelSpeed = 1 mm/sec <==> 1.000.000 / 3600 km/hr = 1/278 km/hr
    # TotalReverse: Other implementations are using values between 1/277 and 1/360.
    # A practical test shows that Cadence=92 gives 40km/hr at a given ratio
    #		factor 289.75 gives a slightly higher speed
    #		factor 301 would be good (8-11-2019)
    #-------------------------------------------------------------------------------
    def Wheel2Speed(self):
        self.SpeedKmh = round(self.WheelSpeed / self.SpeedScale, 2)

    def Speed2Wheel(self, SpeedKmh):
        return round(SpeedKmh * self.SpeedScale, 0)
    
    #---------------------------------------------------------------------------
    # U S B _ R e a d                          Function for USB-sub-classes only
    #-------------------------------------------------------------------------------
    # input     UsbDevice
    #
    # function  Read data from Tacx USB trainer
    #
    # returns   data
    #-------------------------------------------------------------------------------
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
                logfile.Console("ReceiveFromTrainer: USB READ ERROR: " + str(e))
        if debug.on(debug.Data2):
            logfile.Write ("Trainer recv data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
        
        return data
    #-------------------------------------------------------------------------------
    # S e n d T o T r a i n e r                    Function for USB-sub-classes only
    #                                              Most be redefined for Vortex
    #-------------------------------------------------------------------------------
    # input     UsbDevice, TacxMode
    #           if Mode=modeResistance:  TargetPower or TargetGrade/Weight
    #                                    Speed and Cadence are reference for Power2Resistance
    #               in mode_Grade: PowercurveFactor increments/decrements resistance
    #           PedalEcho   - must be echoed
    #           Calibrate   - Resistance during calibration is specified
    #                         If =zero default is calculated
    #
    # function  Set trainer to calculated resistance (TargetPower or TargetGrade)
    #
    # returns   None
    #-------------------------------------------------------------------------------
    def SendToTrainerData(self, TacxMode, Calibrate, PedalEcho, Target, Weight):
        raise NotImplementedError                   # To be defined in sub-class

    def SendToTrainer(self, TacxMode):              # Ready for USB sub-classes
        Calibrate = self.Calibrate
        PedalEcho = self.PedalEcho
        Target    = self.TargetResistance
        Weight    = 0

        if debug.on(debug.Function):
            logfile.Write ("SendToTrainer(%s, %s, %s, %s, %s, %s, %s, %s)" % \
            (TacxMode, self.TargetMode, self.TargetPower, self.TargetGrade, self.UserAndBikeWeight, self.PedalEcho, self.SpeedKmh, self.Cadence))

        #---------------------------------------------------------------------------
        # Prepare parameters to be sent to trainer
        #---------------------------------------------------------------------------
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

            if self.TargetMode == mode_Power:
                # # Target = self.Power2Resistance(self.TargetPower)
                Target = self.TargetResistance
                # Target *= PowercurveFactor                    # manual adjustment of requested resistance
                                                                # IS NOT permitted: When trainer software
                                                                # asks for 100W, you will get 100Watt!
                Weight = 0x0a                                   # weight=0x0a is a good fly-wheel value
                                                                # UserAndBikeWeight is not used!
            elif self.TargetMode == mode_Grade:
                # # Target = self.Grade2Resistance(self.TargetGrade)
                Target = self.TargetResistance
                Target *= self.PowercurveFactor                 # manual adjustment of requested resistance
                Weight = 0x0a                                   # weight=0x0a is a good fly-wheel value
                                                                # UserAndBikeWeight is not used!
                                                                #       an 100kg flywheels gives undesired behaviour :-)
            else:
                error = "SendToTrainer; Unsupported TargetMode %s" % self.TargetMode

        elif TacxMode == modeCalibrate:
            Calibrate   = 0
            PedalEcho   = 0
            Target      = self.Speed2Wheel(20)                  # 20 km/h is our decision for calibration
            Weight      = 0

        else:
            error = "SendToTrainer; incorrect Mode %s!" % TacxMode

        if error:
            logfile.Console(error)
        else:
            Target = int(Target)
            data   = self.SendToTrainerData(TacxMode, Calibrate, PedalEcho, Target, Weight)

            #-----------------------------------------------------------------------
            # Send buffer to trainer
            #-----------------------------------------------------------------------
            if data != False:
                if debug.on(debug.Data2):
                    logfile.Write ("Trainer send data=%s (len=%s)" % (logfile.HexSpace(data), len(data)))
                    logfile.Write ("                  tacx mode=%s target=%s pe=%s weight=%s cal=%s" % \
                                                (TacxMode, Target, PedalEcho, Weight, Calibrate))

                try:
                    self.UsbDevice.write(0x02, data, 30)                             # send data to device
                except Exception as e:
                    logfile.Console("SendToTrainer: USB WRITE ERROR " + str(e))

#-------------------------------------------------------------------------------
# c l s T a c x L e g a c y U s b T r a i n e r
#-------------------------------------------------------------------------------
# USB-trainer with Legacy interface and old formula's
# ==> headunit = 1902
# ==> iMagic
#-------------------------------------------------------------------------------
class clsTacxLegacyUsbTrainer(clsTacxTrainer):
    def __init__(self, clv, Headunit, UsbDevice, Message):
        self.clv        = clv
        self.Headunit   = Headunit
        self.UsbDevice  = UsbDevice
        self.Message    = Message
        self.SpeedScale = 11.9 # GoldenCheetah: curSpeed = curSpeedInternal / (1.19f * 10.0f);
        #PowerResistanceFactor = (1 / 0.0036)       # GoldenCheetah ~= 277.778

    #---------------------------------------------------------------------------
    # Basic physics: Power = Resistance * Speed  <==> Resistance = Power / Speed
    #
    # These two functions calculate as measured with @yegorvin
    #---------------------------------------------------------------------------
    def Resistance2Power(self, Resistance):
        if self.SpeedKmh == 0:
            return 0
        else:
            # GoldenCheetah: curPower = ((curResistance * 0.0036f) + 0.2f) * curSpeedInternal;
            # return round(((Resistance / PowerResistanceFactor) + 0.2) * WheelSpeed, 1)

            # ref https://github.com/WouterJD/FortiusANT/wiki/Power-calibrated-with-power-meter-(iMagic)
            return round(Resistance * (self.SpeedKmh * self.SpeedKmh / 648 + self.SpeedKmh / 5411 + 0.1058) + 2.2 * self.SpeedKmh, 1)

    def Power2Resistance(self, Power):
        rtn = 0
        if self.SpeedKmh > 0:
            # instead of brakeCalibrationFactor use PowerFactor -p
            # GoldenCheetah: setResistance = (((load  / curSpeedInternal) - 0.2f) / 0.0036f)
            #                setResistance *= brakeCalibrationFactor
            # rtn = ((PowerInWatt / WheelSpeed) - 0.2) * PowerResistanceFactor

            # ref https://github.com/WouterJD/FortiusANT/wiki/Power-calibrated-with-power-meter-(iMagic)
            rtn = (Power - 2.2 * self.SpeedKmh) / (self.SpeedKmh * self.SpeedKmh / 648 + self.SpeedKmh / 5411 + 0.1058)

        # Check bounds
        rtn = int(min(226, rtn)) # Maximum value; as defined by Golden Cheetah
        rtn = int(max( 30, rtn)) # Minimum value

        return rtn

    #-------------------------------------------------------------------------------
    # S e n d T o T r a i n e r D a t a
    #-------------------------------------------------------------------------------
    # input     Mode, Target
    #
    # function  Called by SendToTrainer()
    #           Compose buffer to be sent to trainer
    #
    # returns   data
    #-------------------------------------------------------------------------------
    def SendToTrainerData(self, TacxMode, _Calibrate, _Pedecho, Target, _Weight):
        #---------------------------------------------------------------------------
        # Data buffer depends on trainer_type
        # Refer to TotalReverse; "Legacy protocol"
        #---------------------------------------------------------------------------
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
    #-------------------------------------------------------------------------------
    # R e c e i v e F r o m T r a i n e r
    #-------------------------------------------------------------------------------
    # input     usbDevice
    #
    # function  Read status from trainer
    #
    # returns   Speed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, Buttons
    #-------------------------------------------------------------------------------
    def ReceiveFromTrainer(self):
        #-----------------------------------------------------------------------------
        #  Read from trainer
        #-----------------------------------------------------------------------------
        data = self.USB_Read()

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

        self.Axis                = tuple[nAxis1]
        self.Buttons             = ((tuple[nStatusAndCursors] & 0xf0) >> 4) ^ 0x0f
        self.Cadence             = tuple[nCadence]
        self.CurrentResistance   = tuple[nCurrentResistance]
        self.HeartRate           = tuple[nHeartRate]
        self.PedalEcho           = tuple[nPedalSensor]
        self.WheelSpeed          = tuple[nSpeed]

        self.Wheel2Speed()
        self.CurrentPower        = self.Resistance2Power(self.CurrentResistance)

        if debug.on(debug.Function):
            logfile.Write ("ReceiveFromTrainer() = hr=%s Cadence=%s Speed=%s TargetRes=%s CurrentRes=%s CurrentPower=%s, pe=%s %s" % \
                (  self.HeartRate,   self.Cadence,   self.SpeedKmh, self.TargetResistance, self.CurrentResistance, self.CurrentPower, self.PedalEcho, self.Message) \
                          )

#-------------------------------------------------------------------------------
# c l s T a c x N e w I n t e r f a c e T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with New interface ==> the formula's are different
#-------------------------------------------------------------------------------
class clsTacxNewInterfaceTrainer(clsTacxTrainer):
    def __init__(self, clv):
        self.clv        = clv
        self.SpeedScale = 301                        # TotalReverse: 289.75
        self.PowerResistanceFactor = 128866          # TotalReverse

    #---------------------------------------------------------------------------
    # Basic physics: Power = Resistance * Speed  <==> Resistance = Power / Speed
    #---------------------------------------------------------------------------
    def Resistance2Power(self, Resistance):
        return round(Resistance / self.PowerResistanceFactor * self.WheelSpeed, 1)

    def Power2Resistance(self, PowerInWatt):
        rtn        = 0
        if self.WheelSpeed > 0:
            rtn = PowerInWatt * self.PowerResistanceFactor / self.WheelSpeed
            rtn = self.__ResistanceAtLowSpeed(rtn)
        return rtn

    # Limit Resistance
    # (interface maximum = 0x7fff = 32767)
    # at low speed, Fortius does not manage higher resistance
    # at high speed, the rider does not
    def __ResistanceAtLowSpeed(self, Resistance):
        if self.SpeedKmh <= 15 and Resistance >= 6000:
            Resistance = int(max(1000, self.SpeedKmh / 15 * 6000))
        return Resistance

#-------------------------------------------------------------------------------
# c l s T a c x N e w U s b T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with New interface & USB connection
#-------------------------------------------------------------------------------
class clsTacxNewUsbTrainer(clsTacxNewInterfaceTrainer):
    SpeedScale = 301                        # TotalReverse: 289.75
    PowerResistanceFactor = 128866          # TotalReverse

    def __init__(self, clv, Headunit, UsbDevice, Message):
        clsTacxNewInterfaceTrainer.__init__(self, clv)
        self.Headunit   = Headunit
        self.UsbDevice  = UsbDevice
        self.Message    = Message

    #-------------------------------------------------------------------------------
    # S e n d T o T r a i n e r D a t a
    #-------------------------------------------------------------------------------
    # input     Mode, Target, Pedecho, Weight, Calibrate
    #
    # function  Called by SendToTrainer()
    #           Compose buffer to be sent to trainer
    #
    # returns   data
    #-------------------------------------------------------------------------------
    def SendToTrainerData(self, TacxMode, Calibrate, Pedecho, Target, Weight):
        #---------------------------------------------------------------------------
        # Data buffer depends on trainer_type
        # Refer to TotalReverse; "Newer protocol"
        #---------------------------------------------------------------------------
        fControlCommand     = sc.unsigned_int       # 0...3
        fTarget             = sc.short              # 4, 5      Resistance for Power=50...1000Watt
        fPedalecho          = sc.unsigned_char      # 6
        fFiller7            = sc.pad                # 7
        fMode               = sc.unsigned_char      # 8         Idle=0, Ergo/Slope=2, Calibrate/speed=3
        fWeight             = sc.unsigned_char      # 9         Ergo: 0x0a; Weight = ride + bike in kg
        fCalibrate          = sc.unsigned_short     # 10, 11    Depends on mode

        if self.TargetMode == mode_Power and Target < Calibrate:
            Target = Calibrate        # Avoid motor-function for low TargetPower
        #-----------------------------------------------------------------------
        # Build data buffer to be sent to trainer (legacy or new)
        #-----------------------------------------------------------------------
        format = sc.no_alignment + fControlCommand + fTarget +    fPedalecho + fFiller7 + fMode + fWeight + fCalibrate
        data   = struct.pack (format, 0x00010801, int(Target), self.PedalEcho,         TacxMode,   Weight,   Calibrate)
        return data

    #-------------------------------------------------------------------------------
    # R e c e i v e F r o m T r a i n e r
    #-------------------------------------------------------------------------------
    # input     usbDevice
    #
    # function  Read status from trainer
    #
    # returns   Speed, PedalEcho, HeartRate, CurrentPower, Cadence, Resistance, Buttons
    #
    #-------------------------------------------------------------------------------
    def ReceiveFromTrainer(self):
        #-----------------------------------------------------------------------------
        #  Read from trainer
        #-----------------------------------------------------------------------------
        data = self.USB_Read()

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
        self.Axis               = tuple[nAxis1]
        self.Buttons            = tuple[nButtons]
        self.Cadence            = tuple[nCadence]
        self.CurrentResistance  = tuple[nCurrentResistance]
        self.HeartRate          = tuple[nHeartRate]
        self.PedalEcho          = tuple[nEvents]
        self.TargetResistance   = tuple[nTargetResistance]
        self.WheelSpeed         = tuple[nSpeed]

        self.Wheel2Speed()
        self.CurrentPower       = self.Resistance2Power(self.CurrentResistance)

        if debug.on(debug.Function):
            logfile.Write ("ReceiveFromTrainer() = hr=%s Cadence=%s Speed=%s TargetRes=%s CurrentRes=%s CurrentPower=%s, pe=%s %s" % \
                (  self.HeartRate,   self.Cadence,   self.SpeedKmh, self.TargetResistance, self.CurrentResistance, self.CurrentPower, self.PedalEcho, self.Message) \
                          )

#-------------------------------------------------------------------------------
# c l s T a c x A n t V o r t e x T r a i n e r
#-------------------------------------------------------------------------------
# Tacx-trainer with New interface & ANT connection
#-------------------------------------------------------------------------------
class clsTacxAntVortexTrainer(clsTacxNewInterfaceTrainer):

    def __init__(self, clv, AntDevice):
        clsTacxNewInterfaceTrainer.__init__(self, clv)
        self.AntDevice  = AntDevice
        self.Message    = "Pair with Tacx i-Vortex"

    def SendToTrainer(self):
        pass

    def ReceivedFromTrainer(self):
        pass

    def SetTrainerValues(self, Cadence, CurrentPower, SpeedKmh):
        self.Cadence        = Cadence
        self.CurrentPower   = CurrentPower
        self.SpeedKmh       = SpeedKmh

#-------------------------------------------------------------------------------
# c l s S i m u l a t e d T r a i n e r
#-------------------------------------------------------------------------------
# Simulate Tacx-trainer
#-------------------------------------------------------------------------------
class clsSimulatedTrainer(clsTacxTrainer):
    def __init__(self, clv):
        self.clv        = clv
        self.Message    = "Simulated Trainer"

    def SendToTrainer(self):
        pass

    def ReceivedFromTrainer(self):
        pass