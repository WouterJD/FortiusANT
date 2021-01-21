#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-12-27"
# 2020-12-27    Interleave like antPWR.py
# 2020-12-14    First version, obtained from switchable
#-------------------------------------------------------------------------------
import antDongle         as ant

#---------------------------------------------------------------------------
# ANT+ Control command codes
# D00001307_-_ANT+_Device_Profile_-_Controls_-_2.0.pdf
# Table 9-8.
#---------------------------------------------------------------------------
MenuUp      = 0
MenuDown    = 1
MenuSelect  = 2
MenuBack    = 3
Home        = 4
Start       = 32
Stop        = 33
Reset       = 34
Length      = 35
Lap         = 36
NoAction    = 65535            # None is reserved

CommandName = {
    MenuUp:     'MenuUp',
    MenuDown:   'MenuDown',
    MenuSelect: 'MenuSelect',
    MenuBack:   'MenuBack',
    Home:       'Home',
    Start:      'Start',
    Stop:       'Stop',
    Reset:      'Reset',
    Length:     'Length',
    Lap:        'Lap',
    NoAction:   'NoAction'
}

def Initialize():
    global Interleave
    Interleave = 0

def BroadcastControlMessage ():
    global Interleave

    if Interleave == 64:  # Transmit page 0x50 = 80
        info = ant.msgPage80_ManufacturerInfo(ant.channel_CTRL, 0xff, 0xff, \
                                              ant.HWrevision_CTRL, ant.Manufacturer_dev, ant.ModelNumber_CTRL)

    elif Interleave == 129:  # Transmit page 0x51 = 81
        info = ant.msgPage81_ProductInformation(ant.channel_CTRL, 0xff, \
                                                ant.SWrevisionSupp_CTRL, ant.SWrevisionMain_CTRL, ant.SerialNumber_CTRL)

        Interleave = 0              # Restart after the last interleave message

    else:
        # support generic control only
        info = ant.msgPage2_CTRL(ant.channel_CTRL, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10)

    ctrldata = ant.ComposeMessage (ant.msgID_BroadcastData, info)

    #-------------------------------------------------------------------------
    # Prepare for next event
    #-------------------------------------------------------------------------
    Interleave += 1

    #-------------------------------------------------------------------------
    # Return message to be sent
    #-------------------------------------------------------------------------
    return ctrldata
#-------------------------------------------------------------------------------
# Main program for module test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    ctrldata =  BroadcastControlMessage()
    print (ctrldata)