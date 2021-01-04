#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-12-28"
# 2020-12-28    AccumulatedPower not negative
# 2020-12-27    Interleave and EventCount more according specification
#               see comment in antPWR.py for more info.
# 2020-05-07    devAntDongle not needed, not used
# 2020-05-07    pylint error free
# 2020-02-18    First version, split-off from FortiusAnt.py
#-------------------------------------------------------------------------------
import time
import antDongle         as ant

def Initialize():
    global Interleave, EventCount, AccumulatedPower, AccumulatedTime, DistanceTravelled, AccumulatedLastTime
    Interleave              = 0
    EventCount              = 0
    AccumulatedPower        = 0
    AccumulatedTime         = 0
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
# Output:       Interleave, AccumulatedPower, AccumulatedTime, DistanceTravelled
#
# Returns:      fedata; next message to be broadcasted on ANT+ channel
# ------------------------------------------------------------------------------
def BroadcastTrainerDataMessage (Cadence, CurrentPower, SpeedKmh, HeartRate):
    global Interleave, EventCount, AccumulatedPower, AccumulatedTime, DistanceTravelled, AccumulatedLastTime
    #---------------------------------------------------------------------------
    # Prepare data to be sent to ANT+
    #---------------------------------------------------------------------------
    CurrentPower = max(   0, CurrentPower)      # Not negative
    CurrentPower = min(4093, CurrentPower)      # Limit to 4093
    Cadence      = min( 253, Cadence)           # Limit to 253
    
    if   Interleave % 64 in (30, 31):     # After 10 blocks of three messages, then 2 = 32 messages
        #-----------------------------------------------------------------------
        # Send first and second manufacturer's info packet
        #      FitSDKRelease_20.50.00.zip
        #      profile.xlsx 
        #      D00001198_-_ANT+_Common_Data_Pages_Rev_3.1%20.pdf 
        #      page 28 byte 4,5,6,7- 15=dynastream, 89=tacx
        #-----------------------------------------------------------------------
        # comment = "(Manufacturer's info packet)"
        info    = ant.msgPage80_ManufacturerInfo(ant.channel_FE, 0xff, 0xff, \
                    ant.HWrevision_FE, ant.Manufacturer_tacx, ant.ModelNumber_FE)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
        
    elif Interleave % 64 in (62, 63):     # After 10 blocks of three messages, then 2 = 32 messages
        #-----------------------------------------------------------------------
        # Send first and second product info packet
        #-----------------------------------------------------------------------
        # comment = "(Product info packet)"
        info    = ant.msgPage81_ProductInformation(ant.channel_FE, 0xff, \
                    ant.SWrevisionSupp_FE, ant.SWrevisionMain_FE, ant.SerialNumber_FE)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)
    
    elif Interleave % 3 == 0:                                                                             
        #-----------------------------------------------------------------------
        # Send general fe data every 3 packets
        #-----------------------------------------------------------------------
        t                       = time.time()
        ElapsedTime             = t - AccumulatedLastTime # time since previous event
        AccumulatedLastTime     = t
        AccumulatedTime        += ElapsedTime * 4         # in 0.25s

        Speed                   = SpeedKmh * 1000/3600    # convert SpeedKmh to m/s
        Distance                = ElapsedTime * Speed     # meters
        DistanceTravelled      += Distance                # meters

        AccumulatedTime        = int(AccumulatedTime)   & 0xff # roll-over at 255 (64 seconds)
        DistanceTravelled      = int(DistanceTravelled) & 0xff # roll-over at 255

        # comment = "(General fe data)"
        info    = ant.msgPage16_GeneralFEdata (ant.channel_FE, AccumulatedTime, DistanceTravelled, Speed * 1000, HeartRate)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    else:
        EventCount       += 1
        AccumulatedPower += max(0, CurrentPower)            # No decrement allowed

        EventCount        = int(EventCount)       & 0xff    # roll-over at 255
        AccumulatedPower  = int(AccumulatedPower) & 0xffff  # roll-over at 65535

        #-----------------------------------------------------------------------
        # Send specific trainer data
        #-----------------------------------------------------------------------
        # comment = "(Specific trainer data)"
        info    = ant.msgPage25_TrainerData(ant.channel_FE, EventCount, Cadence, AccumulatedPower, CurrentPower)
        fedata  = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    #-------------------------------------------------------------------------
    # Prepare for next event
    #-------------------------------------------------------------------------
    Interleave += 1           # Increment and ...
    Interleave &= 0xff        # maximize to 255

    #-------------------------------------------------------------------------
    # Return message to be sent
    #-------------------------------------------------------------------------
    return fedata
    
#-------------------------------------------------------------------------------
# Main program for module test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    fedata = BroadcastTrainerDataMessage (98, 234, 35.6, 123)
    print (fedata)