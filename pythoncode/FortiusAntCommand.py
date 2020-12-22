#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-11-18"
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

    autostart       = False
    ble             = False
    calibrate       = True
    debug           = 0

    exportTCX       = False      # introduced 2020-11-11;

    gui             = False
    hrm             = None       # introduced 2020-02-09; None=not specified, numeric=HRM device, -1=no HRM
    manual          = False
    manualGrade     = False
    PedalStrokeAnalysis = False
    PowerMode       = False      # introduced 2020-04-10; When specified Grade-commands are ignored xx seconds after Power-commands
    scs             = None       # introduced 2020-02-10; None=not specified, numeric=SCS device

    PowerFactor     = 1.00
    SimulateTrainer = False
    TacxType        = False
    Tacx_iVortex    = False

    uphill          = False      # introduced 2020-10-09; Negative grade is ignored

    #---------------------------------------------------------------------------
    # Deprecated
    #---------------------------------------------------------------------------
    # __tyre__        = 2.096
    # __ftp__         = 200
    # __fL__          = 50
    # __fS__          = 34
    # __rS__          = 15
    # __rL__          = 25

    # ftp             = __ftp__

    # tyre            = __tyre__   # m        tyre circumference
    # fL              = __fL__     # teeth    chain wheel front / large
    # fS              = __fS__     # teeth    chain wheel front / small
    # rL              = __rL__     # teeth    cassette back / large
    # rS              = __rS__     # teeth    cassette back / small

    # ResistanceH     = 150        # % of ftp
    # ResistanceL     = 100        # % of ftp

    #---------------------------------------------------------------------------
    # Define and process command line
    #---------------------------------------------------------------------------
    def __init__(self):
        global clv
        clv = self
        #-----------------------------------------------------------------------
        # Define and process command line
        #-----------------------------------------------------------------------
        parser = argparse.ArgumentParser(description='Program to broadcast data from USB Tacx Fortius trainer, and to receive resistance data for the trainer')
        parser.add_argument('-a','--autostart', help='Automatically start',                                 required=False, action='store_true')
        parser.add_argument('-A','--PedalStrokeAnalysis', help='Pedal Stroke Analysis',                     required=False, action='store_true')
        parser.add_argument('-b','--ble',       help='(EXPERIMENTAL) Use Bluetooth LE instead of ANT+',     required=False, action='store_true')
        parser.add_argument('-d','--debug',     help='Show debugging data',                                 required=False, default=False)
        parser.add_argument('-g','--gui',       help='Run with graphical user interface',                   required=False, action='store_true')
        parser.add_argument('-H','--hrm',       help='Pair this Heart Rate Monitor (0: any, -1: none)',     required=False, default=False)
        parser.add_argument('-m','--manual',    help='Run manual power (ignore target from ANT+ Dongle)',   required=False, action='store_true')
        parser.add_argument('-M','--manualGrade',help='Run manual grade (ignore target from ANT+ Dongle)',  required=False, action='store_true')
        parser.add_argument('-n','--calibrate', help='Do not calibrate before start',                       required=False, action='store_false')
        parser.add_argument('-p','--factor',    help='Adjust target Power by multiplying by this factor for static calibration',
                                                                                                            required=False, default=False)
        parser.add_argument('-P','--PowerMode', help='Power mode has preference over Resistance mode (for 30 seconds)',
                                                                                                            required=False, action='store_true')
        parser.add_argument('-s','--simulate',  help='Simulated trainer to test ANT+ connectivity',         required=False, action='store_true')
#scs    parser.add_argument('-S','--scs',       help='Pair this Speed Cadence Sensor (0: default device)',  required=False, default=False)
        parser.add_argument('-t','--TacxType',  help='Specify Tacx Type; e.g. i-Vortex, default=autodetect',required=False, default=False)
        parser.add_argument('-u','--uphill',    help='Uphill only; negative grade is ignored',              required=False, action='store_true')
        parser.add_argument('-x','--exportTCX', help='Export TCX file',                                     required=False, action='store_true')

        #-----------------------------------------------------------------------
        # Deprecated
        #-----------------------------------------------------------------------
        # s = '%s,%s/%s,%s/%s' % (self.__tyre__, self.__fL__, self.__fS__, self.__rS__, self.__rL__)
        # parser.add_argument('-b','--bicycle',   help='Bicycle definition, default=' + s,                    required=False, default=False)
        # parser.add_argument('-f','--ftp',       help='FTP of the rider, default=%s' % self.__ftp__,         required=False, default=False)
        # parser.add_argument('-r','--resistance',help='FTP percentages for resistance mode, default=150/100',required=False, default=False)

        #-----------------------------------------------------------------------
        # Parse
        #-----------------------------------------------------------------------
        args                        = parser.parse_args()
        self.args                   = args

        #-----------------------------------------------------------------------
        # Booleans; either True or False
        #-----------------------------------------------------------------------
        self.autostart              = args.autostart
        self.ble                    = args.ble
        self.gui                    = args.gui
        self.manual                 = args.manual
        self.manualGrade            = args.manualGrade
        self.calibrate              = args.calibrate
        self.PowerMode              = args.PowerMode
        self.PedalStrokeAnalysis    = args.PedalStrokeAnalysis
        self.SimulateTrainer        = args.simulate
        self.uphill                 = args.uphill
        self.exportTCX              = args.exportTCX or self.manual or self.manualGrade

        if self.manual and self.manualGrade:
            logfile.Console("-m and -M are mutually exclusive; manual power selected")
            self.manualGrade = False        # Mutually exclusive

        if (self.manual or self.manualGrade) and self.SimulateTrainer:
            logfile.Console("-m/-M and -s both specified, most likely for program test purpose")

        #-----------------------------------------------------------------------
        # Bicycle definition to be parsed; three parameters
        # format=tyre,chainring,cassette, e.g. "2.096,50/34,15/25"
        #-----------------------------------------------------------------------
        # if args.bicycle:
        #     b = args.bicycle.split(",")
        #     #-------------------------------------------------------------------
        #     # parameter1: Tyre defined?
        #     #-------------------------------------------------------------------
        #     if len(b) >= 1:
        #         try:
        #             self.tyre = float(b[0])
        #             if self.tyre < 1: self.tyre = self.__tyre__
        #         except:
        #             logfile.Console('Command line error; -b incorrect tyre=%s' % b[0])
        #             self.tyre = self.__tyre__

        #     #-------------------------------------------------------------------
        #     # parameter2: Chainring, large/small separated by /
        #     # format=large/small, e.g. 50/34
        #     # If one value is specified, e.g. "50" 50/50 is assumed
        #     #-------------------------------------------------------------------
        #     if len(b) >= 2:
        #         s = b[1].split('/')
        #         if len(s) >= 0:
        #             try:
        #                 self.fL = int(s[0])
        #             except:
        #                 logfile.Console('Command line error; -b incorrect large chainring=%s' % s[0])

        #         self.fS = self.fL                       # Default is single chainring
        #         if len(s) >= 1:
        #             try:
        #                 self.fS = int(s[1])
        #             except:
        #                 logfile.Console('Command line error; -b incorrect small chainring=%s' % s[1])

        #     #-------------------------------------------------------------------
        #     # parameter3: Cassette, small/large separated by /
        #     # If one value is specified, e.g. "15" 15/15 is assumed
        #     #-------------------------------------------------------------------
        #     if len(b) >= 3:
        #         s = b[2].split('/')
        #         if len(s) >= 0:
        #             try:
        #                 self.rS = int(s[0])
        #             except:
        #                 logfile.Console('Command line error; -b incorrect small cassette=%s' % s[0])

        #         self.rL = self.rS               # Default is single speed cassette
        #         if len(s) >= 1:
        #             try:
        #                 self.rL = int(s[1])
        #             except:
        #                 logfile.Console('Command line error; -b incorrect large cassette=%s' % s[1])

        #-----------------------------------------------------------------------
        # Get debug-flags, used in debug module
        #-----------------------------------------------------------------------
        if args.debug:
            try:
                self.debug = int(args.debug)
            except:
                logfile.Console('Command line error; -d incorrect debugging flags=%s' % args.debug)

        #-----------------------------------------------------------------------
        # Get riders FTP
        #-----------------------------------------------------------------------
        # if args.ftp:
        #     try:
        #         self.ftp = int(args.ftp)
        #         if self.ftp < 50: self.ftp = self.__ftp__
        #     except:
        #         logfile.Console('Command line error; -f incorrect ftp=%s' % args.ftp)

        #-----------------------------------------------------------------------
        # Get HRM
        # - None: read HRM from Tacx Fortius and broadcast as HRM master device
        # - -1  : no master and no slave device
        # - 0   : pair with the first ANT+ HRM that is found
        # - next: pair with the defined ANT+ HRM monitor
        #             the number can be found with ExplorANT
        #-----------------------------------------------------------------------
        if args.hrm:
            try:
                self.hrm = int(args.hrm)
            except:
                logfile.Console('Command line error; -H incorrect HRM=%s' % args.hrm)

        #-----------------------------------------------------------------------
        # Get SCS
        # - None: No Speed Cadence Sensor
        # - 0   : pair with the first ANT+ SCS that is found
        # - next: pair with the defined ANT+ SCS
        #             the number can be found with ExplorANT
        #-----------------------------------------------------------------------
#scs    if args.scs:
#scs        try:
#scs            self.scs = int(args.scs)
#scs        except:
#scs            logfile.Console('Command line error; -S incorrect SCS=%s' % args.scs)

        #-----------------------------------------------------------------------
        # Get powerfactor
        #-----------------------------------------------------------------------
        if args.factor:
            try:
                self.PowerFactor = float(args.factor)
            except:
                logfile.Console('Command line error; -f incorrect power factor=%s' % args.factor)

        #-----------------------------------------------------------------------
        # Parse Resistance
        #-----------------------------------------------------------------------
        # if args.resistance:
        #     s = args.resistance.split('/')
        #     if len(s) >= 0:
        #         try:
        #             self.ResistanceH = int(s[0])
        #         except:
        #             logfile.Console('Command line error; -r incorrect high resistance=%s' % s[0])

        #     if len(s) >= 1:
        #         try:
        #             self.ResistanceL = int(s[1])
        #         except:
        #             logfile.Console('Command line error; -r incorrect low resistance=%s' % s[1])

        #-----------------------------------------------------------------------
        # Get TacxType
        #-----------------------------------------------------------------------
        if args.TacxType:
            self.TacxType = args.TacxType
            if self.TacxType in ('i-Vortex'):
                self.Tacx_iVortex = True
            else:
                logfile.Console('Command line error; -t incorrect value=%s' % args.TacxType)
                args.TacxType = False

        #-----------------------------------------------------------------------
        # Check pedal stroke analysis
        #-----------------------------------------------------------------------
        if args.PedalStrokeAnalysis and (not args.gui or self.Tacx_iVortex):
            logfile.Console("Pedal stroke analysis is not possible in console mode or this Tacx type")
            self.PedalStrokeAnalysis = False

        #-----------------------------------------------------------------------
        # If nothing specified at all, help the poor windows-users
        #-----------------------------------------------------------------------
        if len(sys.argv) == 1:
            pgm = max(sys.argv[0].rfind('/'), sys.argv[0].rfind('\\')) + 1
            pgm = sys.argv[0][pgm:]
            print('---------------------------------------------------------------')
            print('Hello!')
            print('You have started FortiusANT without command-line parameters.')
            print(' ')
            print('Therefore we start with a best-practice setting:')
            print('     %s -a -g -H0 -A' % pgm)
            print(' ')
            print('If you want to start without the graphical user interface:')
            print('     %s -a' % pgm)
            print(' ')
            print('For more info, please refer to the wiki on github.')
            print('Succes!')
            print('---------------------------------------------------------------')
            print('FortiusANT is open source and can freely be used.')
            print('')
            print('A free gift would be appreciated:')
            print('Put yourself on the FortiusANT map by making yourself known')
            print('by leaving a message with name/location/trainer on')
            print('https://github.com/WouterJD/FortiusANT/issues/14')
            print('')
            print('Just for the fun of knowing where we are training.')
            print('---------------------------------------------------------------')
            self.autostart              = True
            self.gui                    = True      # Show gui
            self.hrm                    = 0         # Pair with HRM
            self.PedalStrokeAnalysis    = True      # Show it


    def print(self):
        try:
            v = debug.on(debug.Any)     # Verbose: print all command-line variables with values
            if      self.autostart:          logfile.Console("-a")
            if      self.ble:                logfile.Console("-b")
            if      self.PedalStrokeAnalysis:logfile.Console("-A")
            if v or self.args.debug:         logfile.Console("-d %s (%s)" % (self.debug, bin(self.debug) ) )
            if      self.gui:                logfile.Console("-g")
            if v or self.args.hrm:           logfile.Console("-H %s" % self.hrm )
            if      self.manual:             logfile.Console("-m")
            if      self.manualGrade:        logfile.Console("-M")
            if      not self.args.calibrate: logfile.Console("-n")
            if v or self.args.factor:        logfile.Console("-p %s" % self.PowerFactor )
            if      self.args.PowerMode:     logfile.Console("-P")
            if      self.args.simulate:      logfile.Console("-s")
#scs        if      self.args.scs:           logfile.Console("-S %s" % self.scs )
            if      self.args.TacxType:      logfile.Console("-t %s" % self.TacxType)
            if      self.uphill:             logfile.Console("-u")
            if      self.exportTCX:          logfile.Console("-x")

            #-------------------------------------------------------------------
            # Deprecated
            #-------------------------------------------------------------------
#           if v or self.args.bicycle:       logfile.Console("-b %s,%s/%s,%s/%s" % (self.tyre, self.fL, self.fS, self.rS, self.rL))
#           if v or self.args.ftp:           logfile.Console("-f %s" % self.ftp )
#           if v or self.args.resistance:    logfile.Console("-r %s/%s" % (self.ResistanceH, self.ResistanceL))
        except:
            pass # May occur when incorrect command line parameters, error already given before

#-------------------------------------------------------------------------------
# Main program to test the previous functions
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    clv=CommandLineVariables()
    clv.print()

    print('HRM', clv.hrm)
    print('SCS', clv.scs)

    if clv.hrm == None:
        print("----hrm none")
    else:
        i = int(clv.hrm)
        print(i)