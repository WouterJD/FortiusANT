#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2022-03-03"
# 2022-03-03    #366 -bb added
#               -d can be defined as characters
# 2022-01-14    #363 st7789b added
# 2021-12-02    default command line value for HRM was False, changed to None
#                   HRM=0 has another meaning than "HRM not specified"
#                   same applied to all other integer command-line variables
# 2021-04-13    added: mph
# 2021-04-13    If AntRequired and self.antDeviceID == -1, a message is given
# 2021-03-24    changed: command line help + validation
# 2021-03-24    added: OutputDisplay
# 2021-03-22    changed: -l allowed for Raspberry or GUI
#               leds active by default
# 2021-03-02    added: -l Raspberry status Leds
#               -A -g -l dummy definition present to avoid command-line error
#                   when dependencies are not fulfilled, FortiusAnt will proceed
#                   silently to headless mode.
# 2021-02-25    settings required, even when UseGui = False
# 2021-02-11    added: -e homeTrainer (Exersize bike)
# 2021-02-12    Apply default settings only if no json file loaded
# 2021-02-01    Standard welcome message changed
# 2021-01-19    PowerFactor limit changed to 0.5 ... 1.5
# 2021-01-18    help texts defined as 'constants' to be used for commandline.
# 2021-01-10    -T transmission added, issue #120
#               added: trainer type: Magneticbrake, for consistency
# 2021-01-06    settings added and can be tested from __main__
#               Json-file overwrites command line
# 2021-01-05    added: trainer type: Motorbrake
# 2020-12-30    added: trainer types "Vortex", "Bushido" and "Genius" (-t option)
#               "i-Vortex" is deprecated
#               fix typo in power factor error message
# 2020-12-18    added: -b for Bluetooth support
#               used:  UseBluetooth and UseGui
# 2020-12-15    added: -R for Runoff procedure
#               Command line variables are all printed when debugging
#               Some command line handling code improvements
# 2020-12-14    added: -C for ANT+ Control device
# 2020-12-10    GradeAdjust defined as integer%
#               float (-p and -c); decimal-comma is replaced by decimal-point.
#               Removed: -u uphill
#               Added:   -D antDeviceID
# 2020-12-09    GradeAdjust is split into GradeFactor/GradeFactorDH/GradeShift
# 2020-12-08    GradeAdjust is split into GradeShift/GradeFactor
#               old code removed
# 2020-12-07    -c -G flags added
#               old code removed
# 2020-12-04    -H help-text extended (#157)
# 2020-11-11    Added: -r Resistance
# 2020-11-18    exportTCX implicit for manual mode (that's what is was asked for)
# 2020-11-11    Added: -x exportTCX
# 2020-10-09    Added: -u uphill
# 2020-05-12    Default flags when no command-line arguments specified
#               especially for the novice users.
# 2020-04-30    Added: PedalStrokeAnalysis
# 2020-04-28    Added: clv=self, cmd.Get() used in usbTrainer. TODO.
# 2020-04-20    Added: -t i-Vortex
# 2020-04-16    Write() replaced by Console()
# 2020-04-10    Added: -P PowerMode
# 2020-04-09    Improved: -p command line help
# 2020-03-25    Typo's corrected on command line help
# 2020-03-04    Command-line variables with values printed when debugging
# 2020-02-10    scs added for Alana, analoque to .hrm
#               disabled (#scs) on command-line since not implemented
# 2020-02-09    Added: -H hrm
# 2020-01-23    Added: -m manualGrade
#-------------------------------------------------------------------------------
import argparse
import sys
import time

import debug
import logfile

from   constants                    import UseBluetooth, UseGui, OnRaspberry
import constants
import settings

if UseGui:
    import wx

#-------------------------------------------------------------------------------
# Realize clv to be program-global, by accessing through this function.
#-------------------------------------------------------------------------------
def Get():
    global clv
    return clv

#-------------------------------------------------------------------------------
# F o r t i u s   A N T   -   C o m m a n d L i n e V a r i a b l e s
#-------------------------------------------------------------------------------
class CommandLineVariables(object):
    args            = None

    antDeviceID     = None       # introduced 2020-12-10; Use this usb antDongle type only
    autostart       = False
    ble             = False      # introduced 2020-12-18; Bluetooth support
    DeviceNumberBase= False      # introduced 2021-02-22; Issue #260
    calibrate       = True
    CTRL_SerialL    = 0          # introduced 2020-12-14; ANT+ Control command (Left/Right)
    CTRL_SerialR    = 0
    debug           = 0
    exportTCX       = False      # introduced 2020-11-11;
    GradeAdjust     = 0          # introduced 2020-12-07; The number of parameters specified
    GradeFactor     = 1          #                        The factor to be applied
    GradeFactorDH   = 1          #                        Extra factor to be applied downhill
    GradeShift      = 0          #                        The number of degrees to be added
    gui             = False
    hrm             = None       # introduced 2020-02-09; None=not specified, numeric=HRM device, -1=no HRM
    homeTrainer     = False
    imperial        = False      # introduced 2021-04-13; If True, speed is displayed in mph
    manual          = False
    manualGrade     = False
    PedalStrokeAnalysis = False
    PowerMode       = False      # introduced 2020-04-10; When specified Grade-commands are ignored xx seconds after Power-commands
    Resistance      = False      # introduced 2020-11-23; When specified, Target Resistance equals Target Power
    StatusLeds      = False      # modified   2020-03-22; When specified, Status Led displayed (GUI / raspberry)
    CalibrateRR     = False      # introduced 2020-12-07; To calibrate Magnetic Brake power RollingResistance
    scs             = None       # introduced 2020-02-10; None=not specified, numeric=SCS device
    OutputDisplay   = False      # introduced 2021-03-24; Raspberry small display
    OutputDisplayR  = 0          # introduced 2021-04-09; Rotation
    PowerFactor     = 1.00
    SimulateTrainer = False
    TacxType        = False
    Tacx_Vortex     = False
    Tacx_Genius     = False
    Tacx_Bushido    = False
    Tacx_MotorBrake = False
    Tacx_MagneticBrake = False
    Tacx_Cadence    = True      # Trainer has cadence sensor; only for USB-trainers

    Transmission    = ''        # introduced 2020-01-10

    Cranckset       = []
    CrancksetStart  = 0         # The initial value of index
    CrancksetMax    = 0         # Corresponds to full WH of the drawing area

    Cassette        = []
    CassetteStart   = 0         # The initial value of index
    CassetteMax     = 0         # Corresponds to full WH of the drawing area

    rpiButton       = 3         # Introduced 2021-03-22, for Raspberry
                                # See raspberry.py for button layout
                                # Position moves when -L specified
    rpiTacx         = 5
    rpiShutdown     = 6
    rpiCadence      = 13
    rpiBLE          = 19
    rpiANT          = 26

    #---------------------------------------------------------------------------
    # Runoff, as defined by @cyclingflow
    # Max Speed: I prefer a lower max speed. 40kph requires gearing up to largest
    #   blade on my triple (26inch wheel), which i like to avoid.
    #   30 is the original tacx maximum. Currently I use 36.
    #
    # Over the years i have regularly find myself wondering, did I cleanly stop
    # pedaling in time? I propose a change such that after reaching the max speed,
    # the program signals STOP PEDALLING, and then after a slight further dip
    # say 2kph (40-2=38kph), the programs starts measuring and tells you so.
    #
    # Minimum speed. I have noticed several times that the behavior of the wheel
    # just before stopping is inconsistent (may be smudge or something), which
    # made be start wondering if stopping measuring slightly above zero speed
    # would be better.
    #---------------------------------------------------------------------------
    RunoffMaxSpeed  =  40        # introduced 2020-12-15; #147 Improve runoff procedure
    RunoffDip       =   2
    RunoffMinSpeed  =   1
    RunoffTime      =   7
    RunoffPower     = 100

    #---------------------------------------------------------------------------
    # Define and process command line
    #---------------------------------------------------------------------------
    # Before 2021-03-24 The following specs were used:
    #   parser.add_argument   ('-a','--autostart',          ...
    #   parser.add_argument   ('-t','--TacxType',           ...
    #
    # resulting in the following help-text:
    # optional arguments:
    #   -h, --help            show this help message and exit
    #   -a, --autostart       Automatically start; “Locate HW” and “Start” if the required devices were found.
    #   -t {Bushido,Genius,Vortex,Magneticbrake,Motorbrake,i-Vortex}, --TacxType {Bushido,Genius,Vortex,Magneticbrake,Motorbrake,i-Vortex}
    #                         Specify Tacx Type; if not specified, USB-trainers will be detected automatically.
    #
    # 2021-03-24 '--VariableName' replaced by dest='VariableName' result in in:
    #       (which is a lot more readable)
    # optional arguments:
    #   -h, --help            show this help message and exit
    #   -a                    Automatically start; “Locate HW” and “Start” if the required devices were found.
    #   -t {Bushido,Genius,Vortex,Magneticbrake,Motorbrake,i-Vortex}
    #                         Specify Tacx Type; if not specified, USB-trainers will be detected automatically.
    #---------------------------------------------------------------------------
    def __init__(self):
        global clv
        clv = self
        #-----------------------------------------------------------------------
        # Define and process command line
        # Ref: https://docs.python.org/3/library/argparse.html
        #-----------------------------------------------------------------------
        parser = argparse.ArgumentParser(description='FortiusAnt exchanges data between USB or ANT+ Tacx trainer with an ANT+ or BLE Cycling Training Program')
        parser.add_argument   ('-a', dest='autostart',                                  help=constants.help_a,  required=False, action='store_true')
        if UseGui:
           parser.add_argument('-A', dest='PedalStrokeAnalysis',                        help=constants.help_A,  required=False, action='store_true')
        else:
           parser.add_argument('-A', dest='A_IgnoredIfDefined',                         help=argparse.SUPPRESS, required=False, action='store_true')
        if UseBluetooth:
           parser.add_argument('-b', dest='ble',                                        help=constants.help_b,  required=False, action='store_true')
           parser.add_argument('-bb', dest='bless',                                     help=constants.help_bb, required=False, action='store_true')
        else:
           pass # If -b is requested but not available, then an error is appropriate
        parser.add_argument   ('-B', dest='DeviceNumberBase',   metavar='0...65535',    help=constants.help_B,  required=False, default=None,  type=int)
        parser.add_argument   ('-c', dest='CalibrateRR',        metavar='0...100',      help=constants.help_c,  required=False, default=None,  type=int)
#       parser.add_argument   ('-C', dest='CtrlCommand',        metavar='ANT+DeviceID', help=constants.help_C,  required=False, default=False, type=int)
        parser.add_argument   ('-C', dest='CtrlCommand',        metavar='ANT+DeviceID', help=argparse.SUPPRESS, required=False, default=False, type=int)
        parser.add_argument   ('-d', dest='debug',              metavar='0...65535',    help=constants.help_d,  required=False, default=None)               #type=int
        parser.add_argument   ('-D', dest='antDeviceID',        metavar='USB-DeviceID', help=constants.help_D,  required=False, default=None,  type=int)
        parser.add_argument   ('-e', dest='homeTrainer',                                help=constants.help_e,  required=False, action='store_true')
        #                       -h     help!!
        if UseGui:
           parser.add_argument('-g', dest='gui',                                        help=constants.help_g,  required=False, action='store_true')
        else:
           parser.add_argument('-g', dest='g_IgnoredIfDefined',                         help=argparse.SUPPRESS, required=False, action='store_true')
        parser.add_argument   ('-G', dest='GradeAdjust',        metavar='% / % / %',    help=constants.help_G,  required=False, default=False)
        parser.add_argument   ('-H', dest='hrm',                metavar='ANT+DeviceID', help=constants.help_H,  required=False, default=None, type=int)
        parser.add_argument   ('-i', dest='imperial',                                   help=constants.help_i,  required=False, action='store_true')
        if UseGui or OnRaspberry:
           parser.add_argument('-l', dest='StatusLeds',                                 help=constants.help_l,  required=False, action='store_true')
        else:
           parser.add_argument('-l', dest='l_IgnoredIfDefined',                         help=argparse.SUPPRESS, required=False, action='store_true')
        if OnRaspberry:
           parser.add_argument('-L', dest='gpioLayout',         metavar='gpioLayout',   help=constants.help_L,  required=False, default=False)
        else:
           parser.add_argument('-L', dest='-L_IgnoredIfDefined',                        help=argparse.SUPPRESS, required=False, default=False)
        parser.add_argument   ('-m', dest='manual',                                     help=constants.help_m,  required=False, action='store_true')
        parser.add_argument   ('-M', dest='manualGrade',                                help=constants.help_M,  required=False, action='store_true')
        parser.add_argument   ('-n', dest='calibrate',                                  help=constants.help_n,  required=False, action='store_false')
        if OnRaspberry:
           parser.add_argument('-O', dest='OutputDisplay',      metavar='see text',     help=constants.help_O, required=False, default=False)
        else:
           parser.add_argument('-O', dest='O_IgnoredIfDefined',                         help=argparse.SUPPRESS, required=False, default=False)
        parser.add_argument   ('-p', dest='factor',             metavar='%',            help=constants.help_p,  required=False, default=None,  type=int)
        parser.add_argument   ('-P', dest='PowerMode',                                  help=constants.help_P,  required=False, action='store_true')
        parser.add_argument   ('-r', dest='Resistance',                                 help=constants.help_r,  required=False, action='store_true')
        parser.add_argument   ('-R', dest='Runoff',             metavar='see text',     help=constants.help_R,  required=False, default=False)
        parser.add_argument   ('-s', dest='simulate',                                   help=constants.help_s,  required=False, action='store_true')
#scs    parser.add_argument   ('-S', dest='scs',                metavar='ANT+ DeviceID',help=constants.help_S,  required=False, default=None,  type=int)
        parser.add_argument   ('-T', dest='Transmission',       metavar='see text',     help=constants.help_T,  required=False, default=False)
        self.ant_tacx_models = ['Bushido', 'Genius', 'Vortex', 'Magneticbrake', 'Motorbrake']
        parser.add_argument   ('-t', dest='TacxType',                                   help=constants.help_t, required=False, default=False, \
                    choices=self.ant_tacx_models + ['i-Vortex'])
                    # i-Vortex is still allowed for compatibility
        parser.add_argument   ('-x', dest='exportTCX',                                  help=constants.help_x,  required=False, action='store_true')

        #-----------------------------------------------------------------------
        # Parse command line
        # Overwrite from json file if present
        #-----------------------------------------------------------------------
        self.args  = parser.parse_args()
        jsonLoaded = settings.ReadJsonFile(self.args)

        #-----------------------------------------------------------------------
        # If nothing specified at all, use sensible defaults
        #-----------------------------------------------------------------------
        if len(sys.argv) == 1 and not jsonLoaded:
            pgm = max(sys.argv[0].rfind('/'), sys.argv[0].rfind('\\')) + 1
            pgm = sys.argv[0][pgm:]
            print('---------------------------------------------------------------')
            print('Hello!')
            print('You have started FortiusANT without command-line parameters.')
            print(' ')
            print('Therefore we start with a best-practice setting:')
            print('     %s -a -g -H0 -A -l' % pgm)
            print(' ')
            print('If you want to start without the graphical user interface:')
            print('     %s -a' % pgm)
            print(' ')
            print('For more info, please refer to the wiki on github.')
            print('Success!')
            self.args.autostart              = True
            self.args.gui                    = UseGui    # Show gui
            self.args.hrm                    = 0         # Pair with HRM
            self.args.PedalStrokeAnalysis    = UseGui    # Show it
            self.args.StatusLeds             = UseGui    # Show it

        #-----------------------------------------------------------------------
        # Display welcome message
        #-----------------------------------------------------------------------
        print('---------------------------------------------------------------')
        print('FortiusANT is open source and can be used freely.')
        print('')
        print('Just for the fun of knowing where you all are training,')
        print('put yourself on the FortiusANT map by making yourself known')
        print('by leaving a message with name/location/trainer on')
        print('https://github.com/WouterJD/FortiusANT/issues/14')
        print('')
        print('or visit the sponsoring page https://github.com/sponsors/WouterJD')
        print('---------------------------------------------------------------')

        #-----------------------------------------------------------------------
        # Booleans; either True or False
        #-----------------------------------------------------------------------
        self.autostart              = self.args.autostart
        if UseBluetooth:
            self.ble                = self.args.ble         # BLE using NodeJS
            self.bless              = self.args.bless       # BLE using bless
        if UseGui:
            self.gui                = self.args.gui
        self.homeTrainer            = self.args.homeTrainer # Exersize Bike
        self.StatusLeds             = self.args.StatusLeds
        self.imperial               = self.args.imperial
        self.manual                 = self.args.manual
        self.manualGrade            = self.args.manualGrade
        self.calibrate              = self.args.calibrate
        self.PowerMode              = self.args.PowerMode
        if UseGui:
            self.PedalStrokeAnalysis= self.args.PedalStrokeAnalysis
        self.Resistance             = self.args.Resistance
        self.SimulateTrainer        = self.args.simulate
        self.exportTCX              = self.args.exportTCX or self.homeTrainer or self.manual or self.manualGrade

        i = 0
        if self.homeTrainer:    i += 1
        if self.manual:         i += 1
        if self.manualGrade:    i += 1

        if i > 1:
            logfile.Console("Only one of -h, -m and -M may be specified; manual power selected")
            self.homeTrainer = False
            self.manual      = True
            self.manualGrade = False

        if (self.homeTrainer or self.manual or self.manualGrade) and self.SimulateTrainer:
            logfile.Console("-e/-m/-M and -s both specified, most likely for program test purpose")

        #-----------------------------------------------------------------------
        # Get DeviceNumberBase
        #-----------------------------------------------------------------------
        if self.args.DeviceNumberBase != None:
            try:
                self.DeviceNumberBase = int(self.args.DeviceNumberBase)
            except:
                logfile.Console('Command line error; -B incorrect DeviceNumber Base=%s' % self.args.DeviceNumberBase)

        #-----------------------------------------------------------------------
        # Get calibration of Rolling Resistance
        # Not limitted to a range here, because can be different for different
        #       types of brakes, although initially only used for Magnetic Brake
        #-----------------------------------------------------------------------
        if self.args.CalibrateRR != None:
            try:
                self.CalibrateRR = float(self.args.CalibrateRR.replace(',', '.'))
            except:
                logfile.Console('Command line error; -c incorrect calibration of Rolling Resistance=%s' % self.args.CalibrateRR)

        #-----------------------------------------------------------------------
        # Get CtrlCommand = Serial#1/Serial#2
        #-----------------------------------------------------------------------
        if self.args.CtrlCommand:
            s = self.args.CtrlCommand.split("/")
            try:
                assert(len(s) <= 2)

                if len(s) >= 1: self.CTRL_SerialL = int( s[0] )
                if len(s) >= 2: self.CTRL_SerialR = int( s[1] )

                assert(self.CTRL_SerialL >= 0)
                assert(self.CTRL_SerialR >= 0)
            except:
                logfile.Console('Command line error; -C incorrect SerialNumber in %s' % self.args.CtrlCommand)

        #-----------------------------------------------------------------------
        # Get OutputDisplay
        #-----------------------------------------------------------------------
        if OnRaspberry and self.args.OutputDisplay:
            s = self.args.OutputDisplay.split("/")
            try:
                assert(len(s) <= 2)

                if len(s) >= 1: self.OutputDisplay  = s[0]
                if len(s) >= 2: self.OutputDisplayR = int( s[1] )    # Rotation

                if self.OutputDisplay == 'display':
                    self.OutputDisplay = 'st7789'       # Default device driver
                    # As long as no more devices supported, no reason to bother user
                    # Like this we're ready for other devices in future 

                assert (self.OutputDisplay  in ('console', 'st7789', 'st7789b'))
                assert (self.OutputDisplayR in (0,90,180,270))

                assert(self.CTRL_SerialL >= 0)
                assert(self.CTRL_SerialR >= 0)
            except:
                logfile.Console('Command line error; -O incorrect OutputDisplay in %s' % self.args.CtrlCommand)

            #---------------------------------------------------------------
            # OutputDisplay uses first 24 pins, so our button moves
            # Refer to pinlayout in raspberry.py
            #---------------------------------------------------------------
            if self.OutputDisplay in ('st7789', 'st7789b'):
                self.rpiButton = 16

        #-----------------------------------------------------------------------
        # Get Raspberry GPIO Layout = Button/Tacx/Shutdown/Cadence/BLE/ANT
        #-----------------------------------------------------------------------
        if OnRaspberry and self.args.gpioLayout:
            s = self.args.gpioLayout.split("/")
            try:
                e = 'Too many GPIO pins defined'
                assert(len(s) <= 6)

                e = 'Pin number not numeric'
                if len(s) >= 1: self.rpiButton   = int( s[0] )
                if len(s) >= 2: self.rpiTacx     = int( s[1] )
                if len(s) >= 3: self.rpiShutdown = int( s[2] )
                if len(s) >= 4: self.rpiCadence  = int( s[3] )
                if len(s) >= 5: self.rpiBLE      = int( s[4] )
                if len(s) >= 6: self.rpiANT      = int( s[5] )

                # https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering
                e = 'Pin number not in range 2...27'
                assert(self.rpiButton   in range(2,28) )
                assert(self.rpiTacx     in range(2,28) )
                assert(self.rpiShutdown in range(2,28) )
                assert(self.rpiCadence  in range(2,28) )
                assert(self.rpiBLE      in range(2,28) )
                assert(self.rpiANT      in range(2,28) )

                e = 'Pin number used twice'
                assert(self.rpiButton   not in (                self.rpiTacx, self.rpiShutdown, self.rpiCadence, self.rpiBLE, self.rpiANT) )
                assert(self.rpiTacx     not in (self.rpiButton,               self.rpiShutdown, self.rpiCadence, self.rpiBLE, self.rpiANT) )
                assert(self.rpiShutdown not in (self.rpiButton, self.rpiTacx,                   self.rpiCadence, self.rpiBLE, self.rpiANT) )
                assert(self.rpiCadence  not in (self.rpiButton, self.rpiTacx, self.rpiShutdown,                  self.rpiBLE, self.rpiANT) )
                assert(self.rpiBLE      not in (self.rpiButton, self.rpiTacx, self.rpiShutdown, self.rpiCadence,              self.rpiANT) )
                assert(self.rpiANT      not in (self.rpiButton, self.rpiTacx, self.rpiShutdown, self.rpiCadence, self.rpiBLE             ) )
            except:
                logfile.Console('Command line error; -L incorrect pin-number in %s; %s' % (self.args.gpioLayout, e) )

        #-----------------------------------------------------------------------
        # Get debug-flags, used in debug module
        #-----------------------------------------------------------------------
        if self.args.debug != None:
            try:
                self.debug = int(self.args.debug)
            except:
                #logfile.Console('Command line error; -d incorrect debugging flags=%s' % self.args.debug)

                self.debug = 0
                if 'A' in self.args.debug: self.debug |= debug.Application
                if 'f' in self.args.debug: self.debug |= debug.Function
                if 'a' in self.args.debug: self.debug |= debug.Data1
                if 'u' in self.args.debug: self.debug |= debug.Data2
                if 'm' in self.args.debug: self.debug |= debug.MultiProcessing
                if 'j' in self.args.debug: self.debug |= debug.LogfileJson
                if 'b' in self.args.debug: self.debug |= debug.Ble
                if 'p' in self.args.debug: self.debug |= debug.Performance

                if 'D' in self.args.debug: self.debug |= debug.logging_DEBUG
                if 'I' in self.args.debug: self.debug |= debug.logging_INFO
                if 'W' in self.args.debug: self.debug |= debug.logging_WARNING
                if 'E' in self.args.debug: self.debug |= debug.logging_ERROR
                if 'C' in self.args.debug: self.debug |= debug.logging_CRITICAL

        #-----------------------------------------------------------------------
        # Get antDeviceID
        #-----------------------------------------------------------------------
        if self.args.antDeviceID != None:
            try:
                self.antDeviceID = int(self.args.antDeviceID)
            except:
                logfile.Console('Command line error; -D incorrect antDeviceID=%s' % self.args.antDeviceID)

        #-----------------------------------------------------------------------
        # Get HRM
        # - None: read HRM from Tacx Fortius and broadcast as HRM master device
        # - -1  : no master and no slave device
        # - 0   : pair with the first ANT+ HRM that is found
        # - next: pair with the defined ANT+ HRM monitor
        #             the number can be found with ExplorANT
        #-----------------------------------------------------------------------
        # 2021-12-02 False==0 and therefore False is a bad default if zero is
        #                     a valid value. Therefore default changed to None
        #-----------------------------------------------------------------------
        if self.args.hrm != None:
            try:
                self.hrm = int(self.args.hrm)
            except:
                logfile.Console('Command line error; -H incorrect HRM=%s' % self.args.hrm)

        #-----------------------------------------------------------------------
        # Get SCS
        # - None: No Speed Cadence Sensor
        # - 0   : pair with the first ANT+ SCS that is found
        # - next: pair with the defined ANT+ SCS
        #             the number can be found with ExplorANT
        #-----------------------------------------------------------------------
#scs    if self.args.scs != None:
#scs        try:
#scs            self.scs = int(self.args.scs)
#scs        except:
#scs            logfile.Console('Command line error; -S incorrect SCS=%s' % self.args.scs)

        #-----------------------------------------------------------------------
        # Get powerfactor
        #-----------------------------------------------------------------------
        if self.args.factor != None:
            try:
                self.PowerFactor = int(self.args.factor) / 100
                # I would expect +/- 15% would be enough for compensation, but
                # reactions from "the field" have reported 35% difference.
                # So the range became 50% ... 150%
                #
                # If the power is good and you specify 50% then you will report
                # 500 Watt when producing 250Watt and ... you're cheating...
                #
                # HomeTrainer users may want a low resistance but a reasonable
                # power on Zwift or Strava, otherwise the mountain becomes 
                # endless. So the lower range is set to 20%.
                # When producing 50 Watts, Rouvy will receive 250 Watt and you 
                # can cycle uphill.
                self.PowerFactor = max(0.2, min(1.5, self.PowerFactor) )
            except:
                logfile.Console('Command line error; -p incorrect power factor=%s' % self.args.factor)

        #-----------------------------------------------------------------------
        # Get GradeAdjust = shift/factor
        # Motor Brake default              = -G 100/100
        # Magnetic Brake suggested (Rouvy) = -G  50/100
        #-----------------------------------------------------------------------
        if self.args.GradeAdjust:
            s = self.args.GradeAdjust.split("/")
            self.GradeAdjust = len(s)
            #-------------------------------------------------------------------
            # parameter1: factor (default = 1, allowed = 0...100%)
            # The target slope is divided by this number.
            # Factor = 50 means: requested slope = 20% --> 10%
            #-------------------------------------------------------------------
            # parameter2: factor (default = 1, allowed = 0...100%)
            # The target slope is divided by this number (if negative).
            # Factor = 50 means: requested slope = -20% --> -10%
            #-------------------------------------------------------------------
            # parameter3: shift percentage (default = 0, allowed = 0...20)
            # The target slope is incremented by this number.
            # Shift = 10 means: requested slope = -10% --> 0%
            #-------------------------------------------------------------------
            try:
                assert( len(s) <= 3 )
                if len(s) >= 1 and s[0]: self.GradeFactor   = max(0, min( 1, int( s[0] ) / 100 ))
                if len(s) >= 2 and s[1]: self.GradeFactorDH = max(0, min( 1, int( s[1] ) / 100 ))
                if len(s) >= 3 and s[2]: self.GradeShift    = max(0, min(20, int( s[2] )       ))
            except:
                logfile.Console('Command line error; -G incorrect Grade Adjust=%s' % self.args.GradeAdjust)
                self.GradeAdjust = 0

        #-----------------------------------------------------------------------
        # Get RunOff definition
        # All defined as int (float seems not useful) with exception of Time
        #-----------------------------------------------------------------------
        if self.args.Runoff:
            s = self.args.Runoff.split("/")
            try:
                assert( len(s) <= 5 )
                if len(s) >= 1 and s[0]: self.RunoffMaxSpeed = max(20, min( 50, int  ( s[0] ) )) # km/hr
                if len(s) >= 2 and s[1]: self.RunoffDip      = max( 0, min(  5, int  ( s[1] ) )) # km/hr
                if len(s) >= 3 and s[2]: self.RunoffMinSpeed = max( 0, min( 10, int  ( s[2] ) )) # km/hr
                if len(s) >= 4 and s[3]: self.RunoffTime     = max( 0, min( 10, float( s[3] ) )) # seconds
                if len(s) >= 5 and s[4]: self.RunoffPower    = max( 0, min(500, int  ( s[4] ) )) # Watt
                assert(self.RunoffMinSpeed <= self.RunoffMaxSpeed - self.RunoffDip * 2 )
            except:
                logfile.Console('Command line error; -R incorrect Runoff definition %s' % self.args.Runoff)

        #-----------------------------------------------------------------------
        # Get TacxType
        #-----------------------------------------------------------------------
        AntRequired = False
        if self.args.TacxType:
            self.TacxType = self.args.TacxType
            if 'Vortex' in self.TacxType:
                self.Tacx_Vortex  = True
                self.Tacx_Cadence = False
                AntRequired = True
            elif 'Genius' in  self.TacxType:
                self.Tacx_Genius  = True
                self.Tacx_Cadence = False
                AntRequired = True
            elif 'Bushido' in self.TacxType:
                self.Tacx_Bushido = True
                self.Tacx_Cadence = False
                AntRequired = True
            elif 'Magneticbrake' in self.TacxType:
                self.Tacx_Magneticbrake = True
            elif 'Motorbrake' in self.TacxType:
                self.Tacx_MotorBrake = True
            else:
                logfile.Console('Command line error; -t incorrect value=%s' % self.args.TacxType)
                self.args.TacxType = False

        if AntRequired and self.antDeviceID == -1:
            logfile.Console('You have selected an ANT-trainer (-t %s) and de-selected ANT-dongle (-D-1); -D-1 ignored.' % self.TacxType)
            self.antDeviceID = None

        #-----------------------------------------------------------------------
        # Get Transmission
        # Default    = "34-50    x 34-30-27-25-23-21-19-17-15-13-11"
        # MTB single = "32       x 50-42-36-32-28-24-21-18-16-14-12-10"
        # MTB double = "24-36    x 36-32-28-24-21-19-17-15-13-11"
        # MTB triple = "22-34-44 x 36-32-28-24-21-19-17-15-13-11"
        # MTB 3 x 13 = "22-34-44 x 50-42-36-32-28-24-21-18-16-14-12-10"
        #-----------------------------------------------------------------------
        self.Transmission = self.args.Transmission
        while True:
            #-------------------------------------------------------------------
            # Use command-line value, if fails - use default
            #-------------------------------------------------------------------
            try:
                self.Cranckset      = []
                self.CrancksetStart = 0  # The initial value of index
                self.CrancksetMax   = 0  # Corresponds to full WH of the drawing area

                self.Cassette       = []
                self.CassetteStart  = 0  # The initial value of index
                self.CassetteMax    = 0  # Corresponds to full WH of the drawing area

                self.Transmission    = self.Transmission.replace(' ', '')
                #---------------------------------------------------------------
                # Split in crackset and cassette
                #---------------------------------------------------------------
                s1 = self.Transmission.split("x")
                assert( len(s1) == 2 )
                #---------------------------------------------------------------
                # Split cranckset into chainrings (max 3)
                #---------------------------------------------------------------
                s2 = s1[0].split("-")
                for i in range(0, len(s2)):
                    chainring = s2[i]
                    if (chainring.find('*') != -1): 
                        self.CrancksetStart = i
                        chainring = chainring.replace('*', '')
                    self.Cranckset.append(int(chainring))
                    if int(chainring) > self.CrancksetMax: self.CrancksetMax = int(chainring)
                    if i == 2: break
                #---------------------------------------------------------------
                # Split cassette into sprockets (max 13)
                #---------------------------------------------------------------
                s2 = s1[1].split("-")
                for i in range(0, len(s2)):
                    sprocket = s2[i]
                    if (sprocket.find('*') != -1): 
                        self.CassetteStart = i
                        sprocket = sprocket.replace('*', '')
                    self.Cassette.append(int(sprocket))
                    if int(sprocket) > self.CassetteMax: self.CassetteMax = int(sprocket)
                    if i == 12: break
            except:
                if self.Transmission:
                    logfile.Console('Command line error; -T incorrect Transmission=%s' % self.args.Transmission)
                self.Transmission = constants.Transmission
            else:
                break
        #-----------------------------------------------------------------------
        # If no start defined, take middle position
        #-----------------------------------------------------------------------
        if self.CrancksetStart == 0: self.CrancksetStart = int(round(len(self.Cranckset) / 2 - 0.5))
        if self.CassetteStart  == 0: self.CassetteStart  = int(round(len(self.Cassette)  / 2 - 0.5))

        #-----------------------------------------------------------------------
        # Check pedal stroke analysis
        #-----------------------------------------------------------------------
        if self.PedalStrokeAnalysis and (not self.args.gui or self.Tacx_Vortex or
                                         self.Tacx_Genius or self.Tacx_Bushido):
            logfile.Console("Pedal stroke analysis is not possible in console mode or this Tacx type")
            self.PedalStrokeAnalysis = False

    def print(self):
        try:
            v = self.debug                          # Verbose: print all command-line variables with values
            if      self.autostart:                     logfile.Console("-a")
            if      self.PedalStrokeAnalysis:           logfile.Console("-A")
            if      self.ble:                           logfile.Console("-b")
            if      self.bless:                         logfile.Console("-bb")
            if v or self.args.DeviceNumberBase != None: logfile.Console("-B %s" % self.DeviceNumberBase )
            if v or self.args.CalibrateRR != None:      logfile.Console("-c %s" % self.CalibrateRR )
            if v or self.CTRL_SerialL or self.CTRL_SerialR:
                logfile.Console("-C %s/%s" % (self.CTRL_SerialL, self.CTRL_SerialR ) )
            if v or self.args.debug != None:            logfile.Console("-d %s (%s, %s)" % (self.args.debug, self.debug, bin(self.debug) ) )
            if v or self.args.antDeviceID != None:      logfile.Console("-D %s" % self.antDeviceID )
            if v or self.args.GradeAdjust:
                if self.GradeAdjust == 1:               logfile.Console("-G defines Grade = antGrade * %s" \
                                                                            % (self.GradeFactor ) )
                if self.GradeAdjust == 2:               logfile.Console("-G defines Grade = antGrade * %s [* %s (downhill)]" \
                                                                            % (self.GradeFactor, self.GradeFactorDH) )
                if self.GradeAdjust == 3:               logfile.Console("-G defines Grade = (antGrade - %s) * %s [* %s (downhill)]" \
                                                                            % (self.GradeShift, self.GradeFactor, self.GradeFactorDH) )
            if      self.gui:                           logfile.Console("-g")
            if      self.homeTrainer:                   logfile.Console("-e")
            if v or self.args.hrm != None:              logfile.Console("-H %s" % self.hrm )
            if      self.StatusLeds:                    logfile.Console("-l")
            if OnRaspberry and (v or self.args.gpioLayout):
                logfile.Console("-L %s/%s/%s/%s/%s/%s" % (self.rpiButton, self.rpiTacx, self.rpiShutdown, self.rpiCadence, self.rpiBLE, self.rpiANT) )
            if      self.manual:                        logfile.Console("-m")
            if      self.manualGrade:                   logfile.Console("-M")
            if      self.imperial:                      logfile.Console("-i")
            if      not self.args.calibrate:            logfile.Console("-n")
            if v or self.args.factor != None:           logfile.Console("-p %s" % self.PowerFactor )
            if v or self.args.OutputDisplay:            logfile.Console("-O %s" % self.OutputDisplay)
            if      self.args.PowerMode:                logfile.Console("-P")
            if      self.args.Resistance:               logfile.Console("-r")
            if v or self.args.Runoff:                   logfile.Console("-R defines Runoff: maxSpeed=%s dip=%s minSpeed=%s targetTime=%s power=%s" % \
                        (self.RunoffMaxSpeed, self.RunoffDip, self.RunoffMinSpeed, self.RunoffTime, self.RunoffPower) )
            if      self.args.simulate:                 logfile.Console("-s")
#scs        if v or self.args.scs != None:              logfile.Console("-S %s" % self.scs )
            if v or self.args.TacxType:                 logfile.Console("-t %s" % self.TacxType)
            if v or self.args.Transmission:
                                                        logfile.Console('-T %s x %s (start=%sx%s)' % \
                                                                    (self.Cranckset, self.Cassette, \
                                                                     self.Cranckset[self.CrancksetStart], \
                                                                     self.Cassette [self.CassetteStart]) )
            if      self.exportTCX:                     logfile.Console("-x")

        except:
            pass # May occur when incorrect command line parameters, error already given before

#-------------------------------------------------------------------------------
# Main program to test the previous functions
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    clv=CommandLineVariables()
    clv.print()

    print ('......')

    print('HRM', clv.hrm)
    print('SCS', clv.scs)

    if clv.hrm == None:
        print("----hrm none")
    else:
        i = int(clv.hrm)
        print(i)

    if UseGui:
        app = wx.App(0)
        settings.OpenDialog(app, None, clv)