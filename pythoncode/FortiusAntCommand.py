import argparse
import debug
import logfile

#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
# 2020-01-23    manualGrade added
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Realize clv to be program-global, by accessing through these two functions
#-------------------------------------------------------------------------------
def Create():
    global clv
    clv = CommandLineVariables()
    return clv
    
def Get():
    global clv
    return clv

#-------------------------------------------------------------------------------
# F o r t i u s   A N T   -   C o m m a n d L i n e V a r i a b l e s
#-------------------------------------------------------------------------------
class CommandLineVariables(object):
    __tyre__        = 2.096
    __ftp__         = 200
    __fL__          = 50
    __fS__          = 34
    __rS__          = 15
    __rL__          = 25

    args            = None

    autostart       = False
    calibrate       = True
    tyre            = __tyre__   # m        tyre circumference
    fL              = __fL__     # teeth    chain wheel front / large
    fS              = __fS__     # teeth    chain wheel front / small
    rL              = __rL__     # teeth    cassette back / large
    rS              = __rS__     # teeth    cassette back / small
    debug           = 0
    ftp             = __ftp__
    gui             = False
    manual          = False
    manualGrade     = False
    PowerFactor     = 1.00
    ResistanceH     = 150        # % of ftp
    ResistanceL     = 100        # % of ftp
    SimulateTrainer = False

    #---------------------------------------------------------------------------
    # Define and process command line
    #---------------------------------------------------------------------------
    def __init__(self):
        #-----------------------------------------------------------------------
        # Define and process command line
        #-----------------------------------------------------------------------
        parser = argparse.ArgumentParser(description='Program to broadcast data from USB Tacx Fortius trainer, and to receive resistance data for the trainer')
        parser.add_argument('-a','--autostart', help='Automatically start',                                 required=False, action='store_true')
        s = '%s,%s/%s,%s/%s' % (self.__tyre__, self.__fL__, self.__fS__, self.__rS__, self.__rL__)
        parser.add_argument('-b','--bicycle',   help='Bicycle definition, default=' + s,                    required=False, default=False)
        parser.add_argument('-d','--debug',     help='Show debugging data',                                 required=False, default=False)
        parser.add_argument('-f','--ftp',       help='FTP of the rider, default=%s' % self.__ftp__,         required=False, default=False)
        parser.add_argument('-g','--gui',       help='Run with graphical user interface',                   required=False, action='store_true')
        parser.add_argument('-m','--manual',    help='Run manual power (ignore target from usbDongle)',     required=False, action='store_true')
        parser.add_argument('-M','--manualGrade',help='Run manual grade (ignore target from usbDongle)',    required=False, action='store_true')
        parser.add_argument('-n','--calibrate', help='Do not calibrate before start',                       required=False, action='store_false')
        parser.add_argument('-p','--factor',    help='Adjust target Power by multiplying by this factor',   required=False, default=False)
        parser.add_argument('-r','--resistance',help='FTP percentages for resistance mode, default=150/100',required=False, default=False)
        parser.add_argument('-s','--simulate',  help='Simulated trainer to test ANT+ connectivity',         required=False, action='store_true')
        args                 = parser.parse_args()
        self.args            = args

        #-----------------------------------------------------------------------
        # Booleans; either True or False
        #-----------------------------------------------------------------------
        self.autostart       = args.autostart
        self.gui             = args.gui
        self.manual          = args.manual
        self.manualGrade     = args.manualGrade
        self.calibrate       = args.calibrate
        self.SimulateTrainer = args.simulate
        
        if self.manual and self.manualGrade:
            logfile.Write("-m and -M are mutually exclusive; manual power selected")
            self.manualGrade = False        # Mutually exclusive
        
        if (self.manual or self.manualGrade) and self.SimulateTrainer:
            logfile.Write("-m/-M and -s both specified, most likely for program test purpose")
        
        #-----------------------------------------------------------------------
        # Bicycle definition to be parsed; three parameters
        # format=tyre,chainring,cassette, e.g. "2.096,50/34,15/25"
        #-----------------------------------------------------------------------
        if args.bicycle:
            b = args.bicycle.split(",")
            #-------------------------------------------------------------------
            # parameter1: Tyre defined?
            #-------------------------------------------------------------------
            if len(b) >= 1:
                try:
                    self.tyre = float(b[0])
                    if self.tyre < 1: self.tyre = self.__tyre__
                except:
                    logfile.Write('Command line error; -b incorrect tyre=%s' % b[0])
                    self.tyre = self.__tyre__
            
            #-------------------------------------------------------------------
            # parameter2: Chainring, large/small separated by /
            # format=large/small, e.g. 50/34
            # If one value is specified, e.g. "50" 50/50 is assumed
            #-------------------------------------------------------------------
            if len(b) >= 2:
                s = b[1].split('/')
                if len(s) >= 0:
                    try:
                        self.fL = int(s[0])
                    except:
                        logfile.Write('Command line error; -b incorrect large chainring=%s' % s[0])

                self.fS = self.fL                       # Default is single chainring
                if len(s) >= 1:
                    try:
                        self.fS = int(s[1])
                    except:
                        logfile.Write('Command line error; -b incorrect small chainring=%s' % s[1])

            #-------------------------------------------------------------------
            # parameter3: Cassette, small/large separated by /
            # If one value is specified, e.g. "15" 15/15 is assumed
            #-------------------------------------------------------------------
            if len(b) >= 3:
                s = b[2].split('/')
                if len(s) >= 0:
                    try:
                        self.rS = int(s[0])
                    except:
                        logfile.Write('Command line error; -b incorrect small cassette=%s' % s[0])

                self.rL = self.rS               # Default is single speed cassette
                if len(s) >= 1:
                    try:
                        self.rL = int(s[1])
                    except:
                        logfile.Write('Command line error; -b incorrect large cassette=%s' % s[1])

        #-----------------------------------------------------------------------
        # Get debug-flags, used in debug module
        #-----------------------------------------------------------------------
        if args.debug:
            try:
                self.debug = int(args.debug)
            except:
                logfile.Write('Command line error; -d incorrect debugging flags=%s' % args.debug)

        #-----------------------------------------------------------------------
        # Get riders FTP
        #-----------------------------------------------------------------------
        if args.ftp:
            try:
                self.ftp = int(args.ftp)
                if self.ftp < 50: self.ftp = self.__ftp__
            except:
                logfile.Write('Command line error; -f incorrect ftp=%s' % args.ftp)

        #-----------------------------------------------------------------------
        # Get powerfactor
        #-----------------------------------------------------------------------
        if args.factor:
            try:
                self.PowerFactor = float(args.factor)
            except:
                logfile.Write('Command line error; -f incorrect power factor=%s' % args.factor)

        #-----------------------------------------------------------------------
        # Parse Resistance
        #-----------------------------------------------------------------------
        if args.resistance:
            s = args.resistance.split('/')
            if len(s) >= 0:
                try:
                    self.ResistanceH = int(s[0])
                except:
                    logfile.Write('Command line error; -r incorrect high resistance=%s' % s[0])

            if len(s) >= 1:
                try:
                    self.ResistanceL = int(s[1])
                except:
                    logfile.Write('Command line error; -r incorrect low resistance=%s' % s[1])

    def print(self):
        try:
            if self.autostart:          logfile.Write ("-a")
            if self.args.bicycle:       logfile.Write ("-b %s,%s/%s,%s/%s" % (self.tyre, self.fL, self.fS, self.rS, self.rL))
            if self.args.debug:         logfile.Write ("-d %s (%s)" % (self.debug, bin(self.debug) ) )
            if self.args.ftp:           logfile.Write ("-f %s" % self.ftp )
            if self.gui:                logfile.Write ("-g")
            if self.manual:             logfile.Write ("-m")
            if self.manualGrade:        logfile.Write ("-M")
            if not self.args.calibrate: logfile.Write ("-n")
            if self.args.factor:        logfile.Write ("-p %s" % self.PowerFactor )
            if self.args.resistance:    logfile.Write ("-r %s/%s" % (self.ResistanceH, self.ResistanceL))
            if self.args.simulate:      logfile.Write ("-s")
        except:
            pass # May occur when incorrect command line parameters, error already given before

#-------------------------------------------------------------------------------
# Main program to test the previous functions
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    Create()
    Get().print()
