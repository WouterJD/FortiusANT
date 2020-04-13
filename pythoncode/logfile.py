#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-04-13"
# 2020-04-13    Logfile() added
# 2020-03-24    Resolve crash when non-bytes input to HexSpace()
# 2020-02-12    Write() flushes stdout
#               No error when fLogfile not opened (sometimes raised w/o reason)
# 2020-02-02    Open() has optional parameter for logfile-prefix
#-------------------------------------------------------------------------------
import binascii
import os
import sys
import time
from datetime import datetime

import debug

#-------------------------------------------------------------------------------
# module l o g f i l e
#-------------------------------------------------------------------------------
# functions:    Open, Write(), Close
#
# description:  One central logfile to trace program-execution
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# O p e n
#-------------------------------------------------------------------------------
def Open(prefix='FortiusANT'):
    global fLogfile
    
    if debug.on():
        filename = prefix + '.' + datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S') + ".log"
        fLogfile = open(filename,"w+")

def IsOpen():
    try:
        a = fLogfile
        return True
    except:
        return False

#-------------------------------------------------------------------------------
# P r i n t   to   l o g f i l e
#-------------------------------------------------------------------------------
def Print(*objects, sep=' ', end='\n'):
    global fLogfile
    enc = fLogfile.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=fLogfile)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=fLogfile)

#-------------------------------------------------------------------------------
# W r i t e
#
# Refer https://strftime.org/ for format codes
# hh:mm:ss,ddd is 12 characters (%f for microseconds provides 6 digits)
#-------------------------------------------------------------------------------
def Write (logText):
    logText = datetime.utcnow().strftime('%H:%M:%S,%f')[0:12] + ": " + logText
    print (logText)
    sys.stdout.flush()
    
    if debug.on():
        try:
            test = fLogfile
        except:
            Open()                  # if module not initiated, open implicitly
    
    try:
        if debug.on(): fLogfile.write(logText + "\n")         # \r\n
    except:
#       print ("logfile.Write (" + logText + ") called, but logfile is not opened.")
        pass

#-------------------------------------------------------------------------------
# C l o s e
#-------------------------------------------------------------------------------
def Close():
    try:
        if debug.on(): fLogfile.close
    except:
        pass

#-------------------------------------------------------------------------------
# HexSpace
#-------------------------------------------------------------------------------
# input         buffer;         e.g. "\01\02\03\04"
# 
# description   convert buffer into readable string
#
# returns       string          e.g. "01 02 03 04"
#-------------------------------------------------------------------------------
def HexSpace(info):
    if type(info) is bytes:
        s = binascii.hexlify(info).decode("utf-8")
        rtn = '"'
        for i in range (0, len(s) ):
            if i > 0 and i % 2 == 0: rtn += " "
            rtn += s[i]
        rtn += '"'
    else:
        rtn = '"' + str(info) + '"'        # Safeguard against non-bytes input
    return rtn

def HexSpaceL(list):
    rtn   = '['
    comma = ''
    for l in list:
        rtn += comma + HexSpace(l)
        comma = ', '
    rtn += ']'
    return rtn
#-------------------------------------------------------------------------------
# Main program to test the previous functions
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    print ("Test of wdLogfile")
    Write("This logrecord cannot be written")                 # Not open yet
    Open()                                                    # This is normal
    Write("This is a logrecord")                              # ..
    Close()                                                   # ..
    print ("Test of wdLogfile done")
    print (HexSpace(binascii.unhexlify("203031")))
    print (HexSpace('False'))
    print (HexSpace(False))
else:
    pass                                # We're included so do not take action!
