#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-06-11"
# 2020-06-11    First version, based upon antHRM.py
#-------------------------------------------------------------------------------
import time
import antDongle         as ant

def Initialize():
    global EventCount, AccumulatedPower
    EventCount          = 0
    AccumulatedPower    = 0

def BroadcastMessage (CurrentPower, Cadence):
    global EventCount, AccumulatedPower

    if   EventCount % 120 == 0:           # Transmit page 0x50 = 80
        info = ant.msgPage80_ManufacturerInfo(ant.channel_PWR, 0xff, 0xff, \
            ant.HWrevision_PWR, ant.Manufacturer_garmin, ant.ModelNumber_PWR)

    elif EventCount % 121 == 0:           # Transmit page 0x51 = 81
        info = ant.msgPage81_ProductInformation(ant.channel_PWR, 0xff, \
            ant.SWrevisionSupp_PWR, ant.SWrevisionMain_PWR, ant.SerialNumber_PWR)

    elif EventCount %  60 == 0:           # Transmit page 0x52 = 82
        info = ant.msgPage82_BatteryStatus(ant.channel_PWR)
    
    else:
        AccumulatedPower += CurrentPower
        info= ant.msgPage16_PowerOnly (ant.channel_PWR, EventCount, Cadence, AccumulatedPower, CurrentPower)

    pwrdata = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    #-------------------------------------------------------------------------
    # Prepare for next event
    #-------------------------------------------------------------------------
    EventCount += 1
    if EventCount > 0xff or AccumulatedPower > 0xffff:
        Initialize()

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