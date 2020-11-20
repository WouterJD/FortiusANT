#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
WindowTitle = "Fortius Antifier v3.8"                # Double quotes, see below!
# 2020-11-18    Version 3.7
# 2020-11-12    Version 3.6
# 2020-11-05    Version 3.5
# 2020-11-04    First version
#-------------------------------------------------------------------------------
import debug
import logfile
import time
import urllib.request

#-------------------------------------------------------------------------------
# g i t h u b W i n d o w T i t l e
#-------------------------------------------------------------------------------
# input:        WindowTitle
#				The published version on github
#
# description:  Check whether github uploaded version is different from ourselves
#
# output:		none
#
# returns:      WindowTitle [version on github=WindowTitle]
#-------------------------------------------------------------------------------
def githubWindowTitle():
    rtn = WindowTitle
    url = 'https://raw.githubusercontent.com/WouterJD/FortiusANT/master/pythoncode/FortiusAntTitle.py'

    try:
        file = urllib.request.urlopen(url)
    except:
        if debug.on(debug.Function):
            logfile.Write ('No access to FortiusAntTitle.py on github')
        pass
    else:
        if debug.on(debug.Function):
            logfile.Write ('Check FortiusAntTitle.py on github')
        for line in file:
            DecodedLine = line.decode('utf-8')

            if DecodedLine[:len('WindowTitle')] == 'WindowTitle':
                #---------------------------------------------------------------
                # We read ourselves, so second token must be WindowTitle
                #---------------------------------------------------------------
                githubWindowTitle = DecodedLine.split('"')[1]
                #---------------------------------------------------------------
                # Check if equal; unequal is considered newer
                #---------------------------------------------------------------
                if debug.on(debug.Any):
                    logfile.Write ('Version='+ WindowTitle + ', on github=' + githubWindowTitle + '.')
                if githubWindowTitle == WindowTitle:
                    pass
                else:
                    rtn = rtn + ' [version on github=' + githubWindowTitle + ']'
                break
        file = None
    return rtn

#-------------------------------------------------------------------------------
# Main program to test the previous functions
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    t1 = time.time()
    print(githubWindowTitle())
    t2 = time.time()
    print('Executed in %5.3f seconds' % (t2 - t1))