#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-03-04"
# 2020-03-04    Command-line variables with values printed when debugging
# 2020-02-18    -s added
# 2020-01-29    first version
#-------------------------------------------------------------------------------
import argparse
import debug
import logfile

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
# E x p l o r   A N T   -   C o m m a n d L i n e V a r i a b l e s
#-------------------------------------------------------------------------------
class CommandLineVariables(object):

    args            = None

    autostart       = False
    debug           = 0
    dongle          = -1
    hrm             = -1
    fe              = -1
    SimulateTrainer = False

    #---------------------------------------------------------------------------
    # Define and process command line
    #---------------------------------------------------------------------------
    def __init__(self):
        #-----------------------------------------------------------------------
        # Define and process command line
        #-----------------------------------------------------------------------
        parser = argparse.ArgumentParser(description='Program to explore ANT devices in the system')
        parser.add_argument('-a','--autostart', help='Automatically start',                 required=False, action='store_true')
        parser.add_argument('-d','--debug',     help='Show debugging data',                 required=False, default=False)
        parser.add_argument('-s','--simulate',  help='Simulate master HRM and FE-C',        required=False, action='store_true')
        parser.add_argument('-D','--dongle',    help='Use this ANT dongle',                 required=False, default=False)
        parser.add_argument('-H','--hrm',       help='Listen to this Heart Rate Monitor',   required=False, default=False)
        parser.add_argument('-F','--fe',        help='Listen to this Fitness Equipment',    required=False, default=False)
        args                 = parser.parse_args()
        self.args            = args

        #-----------------------------------------------------------------------
        # Booleans; either True or False
        #-----------------------------------------------------------------------
        self.autostart         = args.autostart
        self.SimulateTrainer   = args.simulate

        #-----------------------------------------------------------------------
        # Get debug-flags, used in debug module
        #-----------------------------------------------------------------------
        if args.debug:
            try:
                self.debug = int(args.debug)
            except:
                logfile.Write('Command line error; -d incorrect debugging flags=%s' % args.debug)

        #-----------------------------------------------------------------------
        # Get ANTdongle
        #-----------------------------------------------------------------------
        if args.dongle:
            try:
                self.dongle = int(args.dongle)
            except:
                logfile.Write('Command line error; -D incorrect dongle=%s' % args.dongle)
        #-----------------------------------------------------------------------
        # Get HRM
        #-----------------------------------------------------------------------
        if args.hrm:
            try:
                self.hrm = int(args.hrm)
            except:
                logfile.Write('Command line error; -H incorrect HRM=%s' % args.hrm)
        #-----------------------------------------------------------------------
        # Get ANTdongle
        #-----------------------------------------------------------------------
        if args.fe:
            try:
                self.fe = int(args.fe)
            except:
                logfile.Write('Command line error; -F incorrect Fitness Equipment=%s' % args.fe)

    def print(self):
        try:
            v = debug.on(debug.Any)     # Verbose: print all command-line variables with values
            if      self.autostart:          logfile.Write ("-a")
            if      self.SimulateTrainer:    logfile.Write ("-s")
            if v or self.args.debug:         logfile.Write ("-d %s (%s)" % (self.debug,  bin(self.debug  ) ) )
            if v or self.args.dongle:        logfile.Write ("-D %s (%s)" % (self.dongle, hex(self.dongle ) ) )
            if v or self.args.hrm:           logfile.Write ("-H %s (%s)" % (self.hrm,    hex(self.hrm    ) ) )
            if v or self.args.fe:            logfile.Write ("-F %s (%s)" % (self.fe,     hex(self.fe     ) ) )
        except:
            pass # May occur when incorrect command line parameters, error already given before

#-------------------------------------------------------------------------------
# Main program to test the previous functions
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    Create()
    Get().print()