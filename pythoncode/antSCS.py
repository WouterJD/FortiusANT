#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-06-09"
# 2020-06-09    First version, based upon antHRM.py
#-------------------------------------------------------------------------------
import time
import antDongle         as ant
import logfile

def Initialize():
    global PedalEchoPreviousCount, CadenceEventTime, CadenceEventCount, SpeedEventTime, SpeedEventCount
    PedalEchoPreviousCount = 0               # There is no previous
    CadenceEventTime       = 0               # Initiate the even variables
    CadenceEventCount      = 0
    SpeedEventTime         = 0
    SpeedEventCount        = 0

def BroadcastMessage (_PedalEchoTime, PedalEchoCount, SpeedKmh, Cadence):
    global PedalEchoPreviousCount, CadenceEventTime, CadenceEventCount, SpeedEventTime, SpeedEventCount

    #-------------------------------------------------------------------------
    # If pedal passed the magnet, calculate new values
    # Otherwise repeat previous message
    #-------------------------------------------------------------------------
    if PedalEchoCount != PedalEchoPreviousCount:
        #---------------------------------------------------------------------
        # Cadence variables
        # Based upon the number of pedal-cycles that are done and the given
        # cadence, calculate the elapsed time.
        # _PedalEchoTime is not used, because that give rounding errors and
        # an instable reading.
        #---------------------------------------------------------------------
        PedalCycles        = PedalEchoCount - PedalEchoPreviousCount
        ElapsedTime        = PedalCycles / Cadence * 60 # count / count/min * seconds/min = seconds
        CadenceEventTime  += ElapsedTime * 1024         # 1/1024 seconds
        CadenceEventCount += PedalCycles

        #---------------------------------------------------------------------
        # Speed variables
        # First calculate how many wheel-cycles can be done
        # Then (based upon rounded #of cycles) calculate the elapsed time
        #---------------------------------------------------------------------
        Circumference    = 2.096         # Note: SimulANT has 2.070 as default
        WheelCadence     = SpeedKmh / 3.6 / Circumference           # km/hr / kseconds/hr / meters  = cycles/s
        WheelCycles      = round(ElapsedTime * WheelCadence, 0)     # seconds * /s                  = cycles

        ElapsedTime      = WheelCycles / SpeedKmh * 3.6 * Circumference
        SpeedEventTime  += ElapsedTime * 1024
        SpeedEventCount += WheelCycles

    #-------------------------------------------------------------------------
    # Rollover after 0xffff
    #-------------------------------------------------------------------------
    if CadenceEventTime > 0xffff or CadenceEventCount > 0xffff or \
         SpeedEventTime > 0xffff or   SpeedEventCount > 0xffff:
        Initialize()

    #-------------------------------------------------------------------------
    # Prepare for next event
    #-------------------------------------------------------------------------
    PedalEchoPreviousCount = PedalEchoCount

    #-------------------------------------------------------------------------
    # Compose message
    #-------------------------------------------------------------------------
    info    = ant.msgPage_SCS (ant.channel_SCS, CadenceEventTime, CadenceEventCount, SpeedEventTime, SpeedEventCount)
    scsdata = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    #-------------------------------------------------------------------------
    # Return message to be sent
    #-------------------------------------------------------------------------
    return scsdata

#-------------------------------------------------------------------------------
# Main program for module test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    time.sleep(1)
    scsdata = BroadcastMessage (0, 1, 45.6, 123)
    print (logfile.HexSpace(scsdata))