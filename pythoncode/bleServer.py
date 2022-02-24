#---------------------------------------------------------------------------
# Example for a BLE 4.0 Server using a GATT dictionary of services and
# characteristics
#---------------------------------------------------------------------------
import asyncio
import logging
import struct
import threading

from typing import Any, Dict

from bless import (
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )

import bleConstants     as bc
import structConstants  as sc
import logfile

global server

global HasControl, Started, TargetPower, TargetGrade
HasControl  = False
Started     = False
TargetPower = 0
TargetGrade = 0

#-------------------------------------------------------------------------------
# Read/write functions for the characteristics
#-------------------------------------------------------------------------------
def read_request(
        characteristic: BlessGATTCharacteristic,
        **kwargs
        ) -> bytearray:

    #print('characteristic -----------------------------')
    #print('\n'.join("%s: %s" % item for item in vars(characteristic).items()))
    #print('characteristic --------------------------end')

    uuid  = str(characteristic._uuid)
    value = logfile.HexSpace(characteristic._value) # or: _initial_value

    if   uuid == bc.cFitnessMachineFeatureUUID:      char = bc.cFitnessMachineFeatureName
    elif uuid == bc.cIndoorBikeDataUUID:             char = bc.cIndoorBikeDataName
    elif uuid == bc.cFitnessMachineStatusUUID:       char = bc.cFitnessMachineStatusName
    elif uuid == bc.cFitnessMachineControlPointUUID: char = bc.cFitnessMachineControlPointName
    elif uuid == bc.cSupportedPowerRangeUUID:        char = bc.cSupportedPowerRangeName
    elif uuid == bc.cHeartRateMeasurementUUID:       char = bc.cHeartRateMeasurementUUID
    else:                                            char = '?'
    
    print("Read request for characteristic %s, value = %s" % (char, value))

    return characteristic.value

def write_request(
        characteristic: BlessGATTCharacteristic,
        value: Any,
        **kwargs
        ):
    global HasControl, Started, TargetPower, TargetGrade

    uuid  = str(characteristic._uuid)
    if   uuid == bc.cFitnessMachineFeatureUUID:      char = bc.cFitnessMachineFeatureName
    elif uuid == bc.cIndoorBikeDataUUID:             char = bc.cIndoorBikeDataName
    elif uuid == bc.cFitnessMachineStatusUUID:       char = bc.cFitnessMachineStatusName
    elif uuid == bc.cFitnessMachineControlPointUUID: char = bc.cFitnessMachineControlPointName
    elif uuid == bc.cSupportedPowerRangeUUID:        char = bc.cSupportedPowerRangeName
    elif uuid == bc.cHeartRateMeasurementUUID:       char = bc.cHeartRateMeasurementUUID
    else:                                            char = '?'
    
    print("Write request for characteristic %s, actual value = %s, provided value = %s" %
        (char, logfile.HexSpace(characteristic.value), logfile.HexSpace(value)))

    #---------------------------------------------------------------------------
    # MachineControlPoint modifies behaviour
    #---------------------------------------------------------------------------
    if not uuid == bc.cFitnessMachineControlPointUUID:
        print('Error: Write request on this characteristic is not supported; ignored.')

    else:
        OpCode   = int(value[0])        # The operation to be performed
        response = bc.fmcp_Success      # Let's assume it will be OK

        #-----------------------------------------------------------------------
        # Check what we need to do
        #-----------------------------------------------------------------------
        if OpCode == bc.fmcp_RequestControl:
            if HasControl:
                response = bc.fmcp_ControlNotPermitted
                print('\tError: already has control')
            else:
                HasControl = True
                print('\tHasControl = %s' % HasControl)

        elif not HasControl:
            response = bc.fmcp_ControlNotPermitted
            print('\tError: no control')

        else:
            if OpCode == bc.fmcp_SetTargetPower:
                tuple  = struct.unpack (sc.little_endian + sc.unsigned_char + sc.unsigned_short, value)
                #opcode     = tuple[0]
                TargetPower = tuple[1]
                print('\tTargetPower = %s' % TargetPower)

            elif OpCode == bc.fmcp_StartOrResume:
                Started = True
                print('\tStarted = %s' % Started)

            elif OpCode == bc.fmcp_StopOrPause:
                Started = False
                print('\tStarted = %s' % Started)

            elif OpCode == bc.fmcp_SetIndoorBikeSimulation:
                tuple  = struct.unpack (sc.little_endian + sc.unsigned_char + sc.short + sc.short + sc.unsigned_char + sc.unsigned_char, value)
                #opcode     = tuple[0]
                windspeed   = tuple[1] * 0.001
                TargetGrade = tuple[2] * 0.01
                crr         = tuple[3] * 0.0001
                cw          = tuple[4] * 0.01
                print('\twindspeed=%s, TargetGrade=%s, crr=%s, cw=%s' % (windspeed, TargetGrade, crr, cw))

            elif OpCode == bc.fmcp_Reset:
                HasControl = False
                print('\tHasControl = %s' % HasControl)

            else:
                print('\tUnknown OpCode %s' % OpCode)
                response = bc.fmcp_ControlNotPermitted

        #-----------------------------------------------------------------------
        # Response:
        #-----------------------------------------------------------------------
        info = struct.pack(sc.little_endian + sc.unsigned_char + sc.unsigned_char, response, OpCode)
        characteristic.value = info
        server.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineControlPointUUID)
        print("New value for characteristic %s = %s" % (char, logfile.HexSpace(info)))

    if characteristic.value == b'\x0f':
        logfile.Console("Nice")
        stop_FortiusAntServer()

# ------------------------------------------------------------------------------
# F o r t i u s A n t S e r v e r
# ------------------------------------------------------------------------------
# Input     None
#
# Function  A BLE-server is created with the required services and characteristics
#           The server will remain active until stop_FortiusAntServer() is called
#
# Output    BLE Server/Service/Characteristics
# ------------------------------------------------------------------------------
def stop_FortiusAntServer():
    trigger.set()

async def FortiusAntServer(loop):
    trigger.clear()

    #-----------------------------------------------------------------------
    # Define the server structure with services and characteristics
    #-----------------------------------------------------------------------
    FitnessMachineGatt: Dict = {
        bc.sFitnessMachineUUID: {
            bc.cFitnessMachineFeatureUUID: {
                "Properties":   (GATTCharacteristicProperties.read),
                "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
                "Value":        bc.fmf_Info,                           # b'\x02\x40\x00\x00\x08\x20\x00\x00',
                "Description":  bc.cFitnessMachineFeatureName
            },
            bc.cIndoorBikeDataUUID: {
                "Properties":   (GATTCharacteristicProperties.notify),
                "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
                "Value":        bc.ibd_Info,                           # Instantaneous Cadence, Power, HeartRate
                "Description":  bc.cIndoorBikeDataName
            },
            bc.cFitnessMachineStatusUUID: {
                "Properties":   (GATTCharacteristicProperties.notify),
                "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
                "Value":        b'\x00\x00',                        # Response as sent to Cycling Training Program
                "Description":  bc.cFitnessMachineStatusName
            },
            bc.cFitnessMachineControlPointUUID: {
                "Properties":   (GATTCharacteristicProperties.write | GATTCharacteristicProperties.indicate),
                "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
                "Value":        b'\x00\x00',                        # Commands as sent by Cycling Training Program
                "Description":  bc.cFitnessMachineControlPointName
            },
            bc.cSupportedPowerRangeUUID: {
                "Properties":   (GATTCharacteristicProperties.read),
                "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
                "Value":        bc.spr_Info,                           # b'\x00\x00\xe8\x03\x01\x00'
                                                                    # min=0, max=1000, incr=1 
                                                                    # ==> 0x0000 0x03e8 0x0001 ==> 0x0000 0xe803 0x0100
                "Description":  bc.cSupportedPowerRangeName
            }
        },
        bc.sHeartRateUUID: {
            bc.cHeartRateMeasurementUUID: {
                "Properties":   (GATTCharacteristicProperties.notify),
                "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
                "Value":        bc.hrm_Info,
                "Description":  bc.cHeartRateMeasurementName
            },
        }
    }

    #-----------------------------------------------------------------------
    # Create the server
    #-----------------------------------------------------------------------
    global server
    server = BlessServer(name=bc.sFitnessMachineName, loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    #-----------------------------------------------------------------------
    # Add the services
    #-----------------------------------------------------------------------
    await server.add_gatt(FitnessMachineGatt)
    await server.start()

    #-----------------------------------------------------------------------
    # DEBUG: check that all characteristics are actually accessible
    #-----------------------------------------------------------------------
    for sUUID, sINFO in FitnessMachineGatt.items():
        logfile.Console('Service: %s' % sUUID)
        for cUUID, cINFO in sINFO.items():
            logfile.Console('\t\t %s=%s' % (cINFO['Description'], logfile.HexSpace(server.get_characteristic(cUUID).value)))

    logfile.Console("---")
    logfile.Console("Advertising")
    logfile.Console("Write '0xF' to the advertised characteristic: " + bc.cFitnessMachineControlPointUUID)

    #-----------------------------------------------------------------------
    # FortiusAntServer is now active
    # read/write through read_Request() and write_Request() functions
    # FortiusAntServer will stop when trigger is activated.
    #-----------------------------------------------------------------------
    trigger.wait()
    await asyncio.sleep(2)
    logfile.Console("Updating")
    server.get_characteristic(bc.FitnessMachineControlPointUUID).value = bytearray(b"i")
    server.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineControlPointUUID)
    await asyncio.sleep(5)
    await server.stop()

#---------------------------------------------------------------------------
# Main program
#---------------------------------------------------------------------------
if True:
    logfile.Open()
    logfile.Console("bleDongleBless started")
    logfile.Console("----------------------")

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)
trigger: threading.Event = threading.Event()

loop = asyncio.get_event_loop()
loop.run_until_complete(FortiusAntServer(loop))