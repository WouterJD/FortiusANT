#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-12-27"
# 2020-12-27    Interleave and EventCount improved according
#               D00001086_ANT+Device_Profile-_Bicycle_Power_Rev_5.1.pdf
#               Implementation fitted to the definitions in the profile:
#               7.1 Power only sensors
#                   page 0x50 - Interleave every 121 messages
#                   page 0x51 - Interleave every 121 messages
#                   page 0x52 - Interleave every  61 messages
#               8.1 Update Event Count
#                   The update event count field is incremented each time the
#                   information in the message is updated.
#                   ...
#                   The Power-only page... must be sent each time the update
#                   event counter is incremented.
#               8.4 Accumulated power
#                   The accumulated power field rolls over at 65.535kW
#               Refer to (regarding roll over values):
#                   D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
#                   9.1.2 Receiving and Calculating Data from Accumulated Values
#               Most important change: Interleave counting is separate from 
#                   the AccumulatedPower related EventCount.
# 2020-06-11    First version, based upon antHRM.py
#-------------------------------------------------------------------------------
import time
import antDongle         as ant

def Initialize():
    global AccumulatedPower, EventCount, Interleave
    AccumulatedPower    = 0
    EventCount          = 0
    Interleave          = 0

def BroadcastMessage (CurrentPower, Cadence):
    global AccumulatedPower, EventCount, Interleave

    if   Interleave ==  61:         # Transmit page 0x52 = 82
        info = ant.msgPage82_BatteryStatus(ant.channel_PWR)
    
    elif Interleave == 120:         # Transmit page 0x50 = 80
        info = ant.msgPage80_ManufacturerInfo(ant.channel_PWR, 0xff, 0xff, \
            ant.HWrevision_PWR, ant.Manufacturer_garmin, ant.ModelNumber_PWR)

    elif Interleave == 121:         # Transmit page 0x51 = 81
        info = ant.msgPage81_ProductInformation(ant.channel_PWR, 0xff, \
            ant.SWrevisionSupp_PWR, ant.SWrevisionMain_PWR, ant.SerialNumber_PWR)

        Interleave = 0              # Restart after the last interleave message

    else:
        EventCount       += 1
        AccumulatedPower += CurrentPower

        EventCount        = int(EventCount)       & 0xff    # roll-over at 255
        AccumulatedPower  = int(AccumulatedPower) & 0xffff  # roll-over at 65535

        info= ant.msgPage16_PowerOnly (ant.channel_PWR, EventCount, Cadence, AccumulatedPower, CurrentPower)

    pwrdata = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    #-------------------------------------------------------------------------
    # Prepare for next event
    #-------------------------------------------------------------------------
    Interleave += 1

    #-------------------------------------------------------------------------
    # Return message to be sent
    #-------------------------------------------------------------------------
    return pwrdata

#-------------------------------------------------------------------------------
# Main program for module test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    pwrdata = BroadcastMessage (456.7, 123)
    print (pwrdata)