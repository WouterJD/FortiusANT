#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-02-18"
# 2020-02-18    First version, split-off from FortiusAnt.py
#-------------------------------------------------------------------------------
import time
import antDongle         as ant

def Initialize():
    global EventCounter, AccumulatedPower, AccumulatedTimeCounter, DistanceTravelled, AccumulatedLastTime
    EventCounter            = 0
    AccumulatedPower        = 0
    AccumulatedTimeCounter  = 0
    DistanceTravelled       = 0
    AccumulatedLastTime     = time.time()

# ------------------------------------------------------------------------------
# B r o a d c a s t T r a i n e r D a t a M e s s a g e
# ------------------------------------------------------------------------------
# input:        Cadence, CurrentPower, SpeedKmh, HeartRate
#
# Description:  Create next message to be sent for FE-C device.
#               Refer to D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
#
# Output:       EventCounter, AccumulatedPower, AccumulatedTimeCounter, DistanceTravelled
#
# Returns:      fedata; next message to be broadcasted on ANT+ channel
# ------------------------------------------------------------------------------
def BroadcastTrainerDataMessage (devAntDongle, Cadence, CurrentPower, SpeedKmh, HeartRate):
    global EventCounter, AccumulatedPower, AccumulatedTimeCounter, DistanceTravelled, AccumulatedLastTime
    #---------------------------------------------------------------------------
    # Prepare data to be sent to ANT+
    #---------------------------------------------------------------------------
    CurrentPower = max(   0, CurrentPower)      # Not negative
    CurrentPower = min(4093, CurrentPower)      # Limit to 4093
    Cadence      = min( 253, Cadence)           # Limit to 253
    
    AccumulatedPower += CurrentPower
    if AccumulatedPower >= 65536: AccumulatedPower = 0

    if   EventCounter % 64 in (30, 31):     # After 10 blocks of three messages, then 2 = 32 messages
        #-----------------------------------------------------------------------
        # Send first and second manufacturer's info packet
        #      FitSDKRelease_20.50.00.zip
        #      profile.xlsx 
        #      D00001198_-_ANT+_Common_Data_Pages_Rev_3.1%20.pdf 
        #      page 28 byte 4,5,6,7- 15=dynastream, 89=tacx
        #-----------------------------------------------------------------------
        comment = "(Manufacturer's info packet)"
        info    = ant.msgPage80_ManufacturerInfo(ant.channel_FE, 0xff, 0xff, \
                    ant.HWrevision_FE, ant.Manufacturer_tacx, ant.ModelNumber_FE)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
        
    elif EventCounter % 64 in (62, 63):     # After 10 blocks of three messages, then 2 = 32 messages
        #-----------------------------------------------------------------------
        # Send first and second product info packet
        #-----------------------------------------------------------------------
        comment = "(Product info packet)"
        info    = ant.msgPage81_ProductInformation(ant.channel_FE, 0xff, \
                    ant.SWrevisionSupp_FE, ant.SWrevisionMain_FE, ant.SerialNumber_FE)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
    
    elif EventCounter % 3 == 0:                                                                             
        #-----------------------------------------------------------------------
        # Send general fe data every 3 packets
        #-----------------------------------------------------------------------
        AccumulatedTimeCounter += 1
        AccumulatedTime         = int(time.time() - AccumulatedLastTime)    # time since start
        Distance                = AccumulatedTime * SpeedKmh * 1000/3600    # SpeedKmh reported in kmh- convert to m/s
        DistanceTravelled      += Distance
        
        if AccumulatedTimeCounter >= 256 or  DistanceTravelled >= 256:      # rollover at 64 seconds (256 quarter secs)
            AccumulatedTimeCounter  = 0
            AccumulatedLastTime     = time.time()                           # Reset last loop time
            DistanceTravelled       = 0

        comment = "(General fe data)"
        # Note: AccumulatedTimeCounter as first parameter,
        #       To be checked whether it should be AccumulatedTime (in 0.25 s)
        info    = ant.msgPage16_GeneralFEdata (ant.channel_FE, AccumulatedTimeCounter, DistanceTravelled, SpeedKmh*1000*1000/3600, HeartRate)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    else:
        #-----------------------------------------------------------------------
        # Send specific trainer data
        #-----------------------------------------------------------------------
        comment = "(Specific trainer data)"
        info    = ant.msgPage25_TrainerData(ant.channel_FE, EventCounter, Cadence, AccumulatedPower, CurrentPower)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    #-------------------------------------------------------------------------
    # Prepare for next event
    #-------------------------------------------------------------------------
    EventCounter += 1           # Increment and ...
    EventCounter &= 0xff        # maximize to 255

    #-------------------------------------------------------------------------
    # Return message to be sent
    #-------------------------------------------------------------------------
    return fedata
    
#-------------------------------------------------------------------------------
# Main program for module test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    fedata = BroadcastTrainerDataMessage (-1, 98, 234, 35.6, 123)
    print (fedata)