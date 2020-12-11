#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-12-10"
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
    calibrate       = True
    debug           = 0
    exportTCX       = False      # introduced 2020-11-11;
    GradeAdjust     = 0          # introduced 2020-12-07; The number of parameters specified
    GradeFactor     = 1          #                        The factor to be applied
    GradeFactorDH   = 1          #                        Extra factor to be applied downhill
    GradeShift      = 0          #                        The number of degrees to be added
    gui             = False
    hrm             = None       # introduced 2020-02-09; None=not specified, numeric=HRM device, -1=no HRM
    manual          = False
    manualGrade     = False
    PedalStrokeAnalysis = False
    PowerMode       = False      # introduced 2020-04-10; When specified Grade-commands are ignored xx seconds after Power-commands
    Resistance      = False      # introduced 2020-11-23; When specified, Target Resistance equals Target Power
    CalibrateRR     = False      # introduced 2020-12-07; To calibrate Magnetic Brake power RollingResistance
    scs             = None       # introduced 2020-02-10; None=not specified, numeric=SCS device
    PowerFactor     = 1.00
    SimulateTrainer = False
    TacxType        = False
    Tacx_iVortex    = False

    #---------------------------------------------------------------------------
    # Deprecated
    #---------------------------------------------------------------------------
    # __tyre__        = 2.096
    # __ftp__         = 200
    # __fL__          = 50
    # __fS__          = 34
    # __rS__          = 15
    # __rL__          = 25

    # tyre            = __tyre__   # m        tyre circumference
    # fL              = __fL__     # teeth    chain wheel front / large
    # fS              = __fS__     # teeth    chain wheel front / small
    # rL              = __rL__     # teeth    cassette back / large
    # rS              = __rS__     # teeth    cassette back / small

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
        parser.add_argument('-c','--CalibrateRR',help='calibrate Rolling Resistance for Magnetic Brake',    required=False, default=False)
        parser.add_argument('-d','--debug',     help='Show debugging data',                                 required=False, default=False)
        parser.add_argument('-D','--antDeviceID',help='Use this antDongle type only',                       required=False, default=False)
        parser.add_argument('-g','--gui',       help='Run with graphical user interface',                   required=False, action='store_true')
        parser.add_argument('-G','--GradeAdjust',help='Adjust slope%% in GradeMode (factor/factorDownhill)',required=False, default=False)
        parser.add_argument('-H','--hrm',       help='Pair this ANT+ Heart Rate Monitor (0: any, -1: none); Tacx HRM is used if not specified',
                                                                                                            required=False, default=False)
        parser.add_argument('-m','--manual',    help='Run manual power (ignore target from ANT+ Dongle)',   required=False, action='store_true')
        parser.add_argument('-M','--manualGrade',help='Run manual grade (ignore target from ANT+ Dongle)',  required=False, action='store_true')
        parser.add_argument('-n','--calibrate', help='Do not calibrate before start',                       required=False, action='store_false')
        parser.add_argument('-p','--factor',    help='Adjust target Power by multiplying by this factor for static calibration',
                                                                                                            required=False, default=False)
        parser.add_argument('-P','--PowerMode', help='Power mode has preference over Resistance mode (for 30 seconds)',
                                                                                                            required=False, action='store_true')
        parser.add_argument('-r','--Resistance',help='Target Resistance = Target Power (to create power curve)',
                                                                                                            required=False, action='store_true')
        parser.add_argument('-s','--simulate',  help='Simulated trainer to test ANT+ connectivity',         required=False, action='store_true')
#scs    parser.add_argument('-S','--scs',       help='Pair this Speed Cadence Sensor (0: default device)',  required=False, default=False)
        parser.add_argument('-t','--TacxType',  help='Specify Tacx Type; e.g. i-Vortex, default=autodetect',required=False, default=False)
        parser.add_argument('-x','--exportTCX', help='Export TCX file',                                     required=False, action='store_true')

        #-----------------------------------------------------------------------
        # Parse
        #-----------------------------------------------------------------------
        args                        = parser.parse_args()
        self.args                   = args

        #-----------------------------------------------------------------------
        # Booleans; either True or False
        #-----------------------------------------------------------------------
        self.autostart              = args.autostart
        self.gui                    = args.gui
        self.manual                 = args.manual
        self.manualGrade            = args.manualGrade
        self.calibrate              = args.calibrate
        self.PowerMode              = args.PowerMode
        self.PedalStrokeAnalysis    = args.PedalStrokeAnalysis
        self.Resistance             = args.Resistance
        self.SimulateTrainer        = args.simulate
        self.exportTCX              = args.exportTCX or self.manual or self.manualGrade

        if self.manual and self.manualGrade:
            logfile.Console("-m and -M are mutually exclusive; manual power selected")
            self.manualGrade = False        # Mutually exclusive

        if (self.manual or self.manualGrade) and self.SimulateTrainer:
            logfile.Console("-m/-M and -s both specified, most likely for program test purpose")

        #-----------------------------------------------------------------------
        # Get calibration of Rolling Resistance
        #-----------------------------------------------------------------------
        if args.CalibrateRR:
            try:
                self.CalibrateRR = float(args.CalibrateRR.replace(',', '.'))
            except:
                logfile.Console('Command line error; -c incorrect calibration of Rolling Resistance=%s' % args.CalibrateRR)

        #-----------------------------------------------------------------------
        # Get debug-flags, used in debug module
        #-----------------------------------------------------------------------
        if args.debug:
            try:
                self.debug = int(args.debug)
            except:
                logfile.Console('Command line error; -d incorrect debugging flags=%s' % args.debug)

        #-----------------------------------------------------------------------
        # Get antDeviceID
        #-----------------------------------------------------------------------
        if args.antDeviceID:
            try:
                self.antDeviceID = int(args.antDeviceID)
            except:
                logfile.Console('Command line error; -D incorrect antDeviceID=%s' % args.antDeviceID)

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
                self.PowerFactor = int(args.factor)/100
            except:
                logfile.Console('Command line error; -f incorrect power factor=%s' % args.factor)

        #-----------------------------------------------------------------------
        # Get GradeAdjust = shift/factor
        # Motor Brake default              = -G 100/100
        # Magnetic Brake suggested (Rouvy) = -G  50/100
        #-----------------------------------------------------------------------
        if args.GradeAdjust:
            s = args.GradeAdjust.split("/")
            self.GradeAdjust = len(s)
            #-------------------------------------------------------------------
            # parameter1: factor (default = 1, allowed = 0...100%)
            # The target slope is divided by this number.
            # Factor = 5 means: requested slope = 20% --> 4%
            #-------------------------------------------------------------------
            if len(s) >= 1:
                try:
                    self.GradeFactor = int(s[0]) / 100
                    self.GradeFactor = max( 0, self.GradeFactor)
                    self.GradeFactor = min( 1, self.GradeFactor)
                except:
                    logfile.Console('Command line error; -G incorrect Grade Adjust=%s' % args.GradeAdjust)
                    self.GradeAdjust = 0

            #-------------------------------------------------------------------
            # parameter2: factor (default = 1, allowed = 0...100%)
            # The target slope is divided by this number.
            # Factor = 5 means: requested slope = 20% --> 4%
            #-------------------------------------------------------------------
            if len(s) >= 2:
                try:
                    self.GradeFactorDH = int(s[1]) / 100
                    self.GradeFactorDH = max( 0, self.GradeFactorDH)
                    self.GradeFactorDH = min( 1, self.GradeFactorDH)
                except:
                    logfile.Console('Command line error; -G incorrect Grade Adjust=%s' % args.GradeAdjust)
                    self.GradeAdjust = 0

            #-------------------------------------------------------------------
            # parameter3: shift percentage (default = 0, allowed = 0...20)
            # The target slope is incremented by this number.
            # Shift = 10 means: requested slope = -10% --> 0%
            #-------------------------------------------------------------------
            if len(s) >= 3:
                try:
                    self.GradeShift = int(s[2])
                    self.GradeShift = max( 0, self.GradeShift)
                    self.GradeShift = min(20, self.GradeShift)
                except:
                    logfile.Console('Command line error; -G incorrect Grade Adjust=%s' % args.GradeAdjust)
                    self.GradeAdjust = 0

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
            if      self.PedalStrokeAnalysis:logfile.Console("-A")
            if v or self.args.CalibrateRR:   logfile.Console("-c %s" % self.CalibrateRR )
            if v or self.args.debug:         logfile.Console("-d %s (%s)" % (self.debug, bin(self.debug) ) )
            if v or self.args.antDeviceID:   logfile.Console("-D %s" % self.antDeviceID )
            if v or self.args.GradeAdjust:
                if self.GradeAdjust == 1: logfile.Console("-G defines Grade = antGrade * %s" \
                                                    % (self.GradeFactor ) )
                if self.GradeAdjust == 2: logfile.Console("-G defines Grade = antGrade * %s [* %s (downhill)]" \
                                                    % (self.GradeFactor, self.GradeFactorDH) )
                if self.GradeAdjust == 3: logfile.Console("-G defines Grade = (antGrade - %s) * %s [* %s (downhill)]" \
                                                    % (self.GradeShift, self.GradeFactor, self.GradeFactorDH) )
            if      self.gui:                logfile.Console("-g")
            if v or self.args.hrm:           logfile.Console("-H %s" % self.hrm )
            if      self.manual:             logfile.Console("-m")
            if      self.manualGrade:        logfile.Console("-M")
            if      not self.args.calibrate: logfile.Console("-n")
            if v or self.args.factor:        logfile.Console("-p %s" % self.PowerFactor )
            if      self.args.PowerMode:     logfile.Console("-P")
            if      self.args.Resistance:    logfile.Console("-r")
            if      self.args.simulate:      logfile.Console("-s")
#scs        if v or self.args.scs:           logfile.Console("-S %s" % self.scs )
            if v or self.args.TacxType:      logfile.Console("-t %s" % self.TacxType)
            if      self.exportTCX:          logfile.Console("-x")

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