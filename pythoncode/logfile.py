#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-01-25"
#-------------------------------------------------------------------------------
import binascii
import os
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
def Open():
    global fLogfile
    
    if debug.on():
        filename = "FortiusANT." + datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S') + ".log"
        fLogfile = open(filename,"w+")

def IsOpen():
    try:
        a = fLogfile
        return True
    except:
        return False

#-------------------------------------------------------------------------------
# W r i t e
#
# Refer https://strftime.org/ for format codes
# hh:mm:ss,ddd is 12 characters (%f for microseconds provides 6 digits)
#-------------------------------------------------------------------------------
def Write (logText):
    logText = datetime.utcnow().strftime('%H:%M:%S,%f')[0:12] + ": " + logText
    print (logText)

    if debug.on():
        try:
            test = fLogfile
        except:
            Open()                  # if module not initiated, open implicitly
    
    try:
        if debug.on(): fLogfile.write(logText + "\n")         # \r\n
    except:
        print ("logfile.Write (" + logText + ") called, but logfile is not opened.")

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
    str = binascii.hexlify(info).decode("utf-8")
    rtn = '"'
    for i in range (0, len(str) ):
        if i > 0 and i % 2 == 0: rtn += " "
        rtn += str[i]
    rtn += '"'
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
else:
    pass                                # We're included so do not take action!
