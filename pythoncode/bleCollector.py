#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2022-02-21"
# 2022-02-21    Version rebuilt to be able to validate the FortiusAnt/BLE 
#               implementation and I expect you could 'look' at an existing
#               Tacx-trainer as well, but did not try that.
#
#               FortiusAnt/BLE using NodeJS does not transmit:
#               - the trainer speed in the FTMS
#               - the heartrate in the HRS (in simulation mode)
#
#               Todo: implement writing the target speed/target grade to see
#                     whether those parameters are accepted by FortiusAnt.
#
# 2020-12-18    First version, obtained from: " hbldh\bleak"
#               Service Explorer
#               ----------------
#               An example showing how to access and print out the services,
#               characteristics anddescriptors of a connected GATT server.
#
#               Created on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>
#-------------------------------------------------------------------------------
import asyncio
import logging
import platform
from socket import timeout
import sys

from bleak import BleakClient
from bleak import discover

import bleConstants    as bc
import logfile
import struct
import structConstants as sc

#-------------------------------------------------------------------------------
# ADDRESSES: Returned by findBLEdevices()
#-------------------------------------------------------------------------------
global ADDRESSES
ADDRESSES = []        # The address appears appear to change continuously

#-------------------------------------------------------------------------------
# Status-fields of the Fitness Machine
#-------------------------------------------------------------------------------
global cadence, hrm, power, speed
cadence = 0
hrm     = 0
power   = 0
speed   = 0

#-------------------------------------------------------------------------------
# f i n d B L E D e v i c e s
#-------------------------------------------------------------------------------
# Input:    bleak devices
#
# Function  Discover existing devices and return list of addresses
#
# Output:   ADDRESSES
#-------------------------------------------------------------------------------
async def findBLEdevices():
    global ADDRESSES
    print('Discover existing BLE devices ----')
    devices = await discover()
    for d in devices:
        print(d)
        # print('d -----------------------------')
        # print('\n'.join("%s: %s" % item for item in vars(d).items()))
        # print('d --------------------------end')
        if bc.sFitnessMachineUUID in d.metadata['uuids']:
            ADDRESSES.append (d.address)                    # It's a candidate
    print('Done -----------------------------')

#-------------------------------------------------------------------------------
# s e r v e r I n s p e c t i o n
#-------------------------------------------------------------------------------
# Input:    address
#
# Function  Inspect structure of the provided server
#
# Output:   Console
#-------------------------------------------------------------------------------
async def serverInspection(address):
    print('Inspect BLE-device with address %s' % address)
    try:
        async with BleakClient(address) as client:          # , timeout=100
            await serverInspectionSub(client)
    except Exception as e:
        print(type(e), e)
    print('Inspection done --------------------------------------------------------------------------')
            
async def serverInspectionSub(client):

    print("Connected: ", client.is_connected)
    # print('client -----------------------------')
    # print('\n'.join("%s: %s" % item for item in vars(client).items()))
    # print('client --------------------------end')

    #---------------------------------------------------------------------------
    # Check whether this service is a Fitness Machine
    # For detailed comment, see loop below (same loop, more explanation)
    #---------------------------------------------------------------------------
    bFitnessMachine    = False
    sFitnessMachine    = 'NOT '
    sServiceDeviceName = '<Unknown>'

    for service in client.services:
        for char in service.characteristics:
            value = "n/a"
            if "read" in char.properties:
                value = bytes(await client.read_gatt_char(char.uuid))

                if char.uuid == bc.cDeviceNameUUID:
                    sServiceDeviceName = value.decode('ascii')

                if char.uuid == bc.cFitnessMachineFeatureUUID and len(value) == 8:
                    tuple  = struct.unpack (sc.little_endian + sc.unsigned_long * 2, value)
                    cFitnessMachineFeatureFlags1 = tuple[0]
                    cFitnessMachineFeatureFlags2 = tuple[1]

                    if (    cFitnessMachineFeatureFlags1 & bc.fmf_CadenceSupported
                        and cFitnessMachineFeatureFlags1 & bc.fmf_PowerMeasurementSupported
                        and cFitnessMachineFeatureFlags2 & bc.fmf_PowerTargetSettingSupported
                        and cFitnessMachineFeatureFlags2 & bc.fmf_IndoorBikeSimulationParametersSupported
                        ):
                        bFitnessMachine = True
                        sFitnessMachine = ''

    print ('%s: This is %sa matching Fitness Machine' % (sServiceDeviceName, sFitnessMachine) )

    #---------------------------------------------------------------------------
    # Inspect the Fitness Machine and print all details
    #---------------------------------------------------------------------------
    if bFitnessMachine:
        #-----------------------------------------------------------------------
        # Inspect all services of the server
        #-----------------------------------------------------------------------
        for service in client.services:
            s = "Service: %s" % service
            s = s.replace(bc.BluetoothBaseUUIDsuffix, '-...')  # Always the same
            print(s)
            #-------------------------------------------------------------------
            # Inspect all characteristics of the service
            #-------------------------------------------------------------------
            for char in service.characteristics:
                #---------------------------------------------------------------
                # Print characteristic, properties and value
                #---------------------------------------------------------------
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                    except Exception as e:
                        value = e
                elif "notify" in char.properties:
                    value = '(N/A: Wait for notification)'      # Initiated by server
                elif "indicate" in char.properties and "write" in char.properties:
                    value = '(N/A: Wait for indication)'        # Requested by client
                else:
                    value = '(N/A; not readable)'

                if char.uuid == bc.cDeviceNameUUID:
                    s = '"' + value.decode('ascii') + '"'       # Device name should be printable
                else:
                    s = logfile.HexSpace(value)

                s = '\tCharacteristic: %-80s, props=%s, value=%s' % (char, char.properties, s)
                s = s.replace(bc.BluetoothBaseUUIDsuffix, '-...') # Always the same
                print(s)

                #---------------------------------------------------------------
                # Inspect and print FitnessMachineFeature characteristic
                # (not used, but could be when implementing a real collector)
                #---------------------------------------------------------------
                if char.uuid == bc.cFitnessMachineFeatureUUID and len(value) == 8:
                    tuple  = struct.unpack (sc.little_endian + sc.unsigned_long * 2, value)
                    cFitnessMachineFeatureFlags1 = tuple[0]
                    cFitnessMachineFeatureFlags2 = tuple[1]

                    print('\t\tSupported: ', end='')
                    if cFitnessMachineFeatureFlags1 & bc.fmf_CadenceSupported:                        print('Cadence, '           , end='')
                    if cFitnessMachineFeatureFlags1 & bc.fmf_HeartRateMeasurementSupported:           print('HRM, '               , end='')
                    if cFitnessMachineFeatureFlags1 & bc.fmf_PowerMeasurementSupported:               print('PowerMeasurement, '  , end='')
                    if cFitnessMachineFeatureFlags2 & bc.fmf_PowerTargetSettingSupported:             print('PowerTargetSetting, ', end='')
                    if cFitnessMachineFeatureFlags2 & bc.fmf_IndoorBikeSimulationParametersSupported: print('IndoorBikeSimulation', end='')
                    print('.')

                #---------------------------------------------------------------
                # Inspect all descriptors of the characteristic
                #---------------------------------------------------------------
                for descriptor in char.descriptors:
                    if descriptor.uuid != bc.CharacteristicUserDescriptionUUID:
                        try:
                            value = bytes(
                                await client.read_gatt_descriptor(descriptor.handle)
                            )
                        except Exception as e:
                            value = e

                        # Does not seem to provide much additional information,
                        # So commented, perhaps for later use
                        # print("\t\tDescriptor: ", descriptor.uuid, 'value=', logfile.HexSpace(value))

        #-----------------------------------------------------------------------
        # Now receive notifications and indications
        #-----------------------------------------------------------------------
        print("Register notifications")
        await client.start_notify(bc.cFitnessMachineStatusUUID, notificationFitnessMachineStatus)
        await client.start_notify(bc.cHeartRateMeasurementUUID, notificationHeartRateMeasurement)
        await client.start_notify(bc.cIndoorBikeDataUUID,       notificationIndoorBikeData)

        # the server shall indicate...
        # BUT I have no clue how to receive an indication...

        print("Register indications")
        await client.start_notify(bc.cFitnessMachineControlPointUUID, indicationFitnessMachineControlPoint)

        #-----------------------------------------------------------------------
        # Now pretend to be a Cycling Training Program, cycling by all modes
        #-----------------------------------------------------------------------
        mode      = bc.fmcp_RequestControl  # ControlPoint opcodes are used
        PowerMode = 0x0100                  # Additional mode (no opcode)
        GradeMode = 0x0200
        waitmode  = 0x1000  # Range outside opcodes, to indicate waiting
        CountDown = 5       # Number of cycles between PowerMode / GradeMode
        timeout   = 10
        wait      = 0       # Waiting for comfirmation of response
        while True:
            if mode == bc.fmcp_RequestControl:
                #---------------------------------------------------------------
                print("Request control, so that commands can be sent")
                #---------------------------------------------------------------
                info = struct.pack(sc.little_endian + sc.unsigned_char, bc.fmcp_RequestControl)
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                # Wait for response
                wait = timeout
                mode += waitmode

            elif mode == bc.fmcp_RequestControl + waitmode:
                # EXPERIMENTAL, SINCE I DO NOT KNOW HOW THE RESPONSE COMES BACK
                # LET'S START WITH THIS
                #---------------------------------------------------------------
                print("Request control; waiting for response")
                #---------------------------------------------------------------
                if False:                        # If response received, proceed
                    mode = bc.fmcp_StartOrResume

                wait -= 1
                if not wait: break

            elif mode == bc.fmcp_StartOrResume:
                #---------------------------------------------------------------
                print("Start training session")
                #---------------------------------------------------------------
                info = struct.pack(sc.little_endian + sc.unsigned_char, bc.fmcp_StartOrResume)
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                mode = PowerMode

            elif mode == PowerMode:
                TargetPower = 320 + CountDown   # Watts
                #---------------------------------------------------------------
                print('Switch to PowerMode, %sW' % TargetPower)
                #---------------------------------------------------------------
                info = struct.pack(sc.little_endian + sc.unsigned_char +      sc.unsigned_short, 
                                                      bc.fmcp_SetTargetPower, TargetPower      )
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                mode == GradeMode

            elif mode == GradeMode:
                TargetGrade = 4 + CountDown/10  # % inclination
                windspeed   = 0
                crr         = 0.004             # rolling resistance coefficient
                cw          = 0.51              # wind resistance coefficient
                #---------------------------------------------------------------
                print('Switch to GradeMode, %s%%' % TargetGrade)
                #---------------------------------------------------------------
                TargetGrade = int(TargetGrade * 100)    # Resolution 0.01
                windspeed   = int(windspeed * 1000)     # Resolution 0.001
                crr         = int(crr * 10000)          # Resolution 0.0001
                cw          = int(cw  *   100)          # Resolution 0.01
                info = struct.pack(sc.little_endian + sc.unsigned_char + sc.short + sc.short   + sc.unsigned_char + sc.unsigned_char,
                                    bc.fmcp_SetIndoorBikeSimulation,  windspeed, TargetGrade, crr,               cw)
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                CountDown -= 1
                if CountDown:   mode = PowerMode
                else:           mode = bc.fmcp_StopOrPause

            elif mode == bc.fmcp_StopOrPause:
                #---------------------------------------------------------------
                print("Stop training session")
                #---------------------------------------------------------------
                info = struct.pack(sc.little_endian + sc.unsigned_char, bc.fmcp_StopOrPause)
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                mode = bc.fmcp_Reset

            elif mode == bc.fmcp_Reset:
                #---------------------------------------------------------------
                print("Release control / reset")
                #---------------------------------------------------------------
                info = struct.pack(sc.little_endian + sc.unsigned_char, bc.fmcp_Reset)
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                break
            #-------------------------------------------------------------------
            # Do an action every second
            #-------------------------------------------------------------------
            await asyncio.sleep(1)

        #-----------------------------------------------------------------------
        # Stop receiving notifications and indications
        #-----------------------------------------------------------------------
        print("Unregister notifications")
        await client.stop_notify(bc.cFitnessMachineStatusUUID)
        await client.stop_notify(bc.cHeartRateMeasurementUUID)
        await client.stop_notify(bc.cIndoorBikeDataUUID)

        print("Unregister indications")
        await client.stop_notify(bc.cFitnessMachineControlPointUUID)

#-------------------------------------------------------------------------------
# n o t i f i c a t i o n H a n d l e r
#-------------------------------------------------------------------------------
# Input:    handle, data
#
# Function  Notification handler to print the notified data
#
# Output:   Console
#           HeartRateMeasurement; hrm
#           IndoorBikeData;       cadence, hrm, speed, power
#-------------------------------------------------------------------------------
def indicationFitnessMachineControlPoint(handle, data):
    print('indicationFitnessMachineControlPoint() TO BE IMPLEMENTED <--------')
    notificationPrint(handle, bc.cFitnessMachineControlName, data)

def notificationFitnessMachineStatus(handle, data):
    print('notificationFitnessMachineStatus() TO BE IMPLEMENTED <--------')
    notificationPrint(handle, bc.cFitnessMachineStatusName, data)

def notificationHeartRateMeasurement(handle, data):
    global cadence, hrm, speed, power
    if len(data) == 2:
        tuple  = struct.unpack (sc.little_endian + sc.unsigned_short, data)
        hrm     = tuple[0]
    else:
        print('Error: incorrect length')

    notificationPrint(handle, bc.cHeartRateMeasurementName, data)

def notificationIndoorBikeData(handle, data):
    global cadence, hrm, speed, power

    if len(data) in (4,6,8,10): # All flags should be implemented; only this set done!!
        tuple  = struct.unpack (sc.little_endian + sc.unsigned_short * int(len(data)/2), data)
        flags   = tuple[0]
        speed   = tuple[1]               # always present
        n = 2
        if flags & bc.ibd_InstantaneousCadencePresent:
            cadence = int(tuple[n] / 2)  # Because transmitted in BLE in half rpm
            n += 1
        if flags & bc.ibd_InstantaneousPowerPresent:
            power   = tuple[n]
            n += 1
        if flags & bc.ibd_HeartRatePresent:
            hrm    = tuple[n]
            n += 1
    else:
        print('Error: incorrect length')

    notificationPrint(handle, bc.cIndoorBikeDataName, data)

def notificationPrint(handle, uuidName, data):
    global cadence, hrm, speed, power
    #---------------------------------------------------------------------------
    # Print what we got untill now
    #---------------------------------------------------------------------------
    print("%s %-22s %-25s speed=%s cadence=%3s power=%4s hrm=%3s" % (handle, uuidName, logfile.HexSpace(data), speed, cadence, power, hrm))


if __name__ == "__main__":
    #---------------------------------------------------------------------------
    # Introduction
    #---------------------------------------------------------------------------
    print('bleCollector; is used to show the characteristics of a running FTMS (Fitness Machine Service).')
    print('              FortiusAnt (BLE) provides such an FTMS and a Cycling Training Program is a client for that service.')
    print('              Note that, when a CTP is active, FortiusAnt will not be discovered because it is in use.')

    #---------------------------------------------------------------------------
    # Initialize logger, currently straight print() used
    # Logging for bleak can be activated here
    #---------------------------------------------------------------------------
    logger = logging.getLogger(__name__)
    #logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    #---------------------------------------------------------------------------
    # First discover ADDRESSES of all possible fitness machines (1 expected)
    #---------------------------------------------------------------------------
    asyncio.run(findBLEdevices())

    #---------------------------------------------------------------------------
    # Now show all details of the FTMS
    #---------------------------------------------------------------------------
    for a in ADDRESSES:
        asyncio.run(serverInspection(a))

"""

SAMPLE OUTPUT:
==============

bleDongleTest; a client to show the characteristics of a running FTMS (Fitness Machine Service)
               FortiusAnt (BLE) provides such an FTMS and a Cycling Training Program is a client for that service
Discover existing BLE devices ----
D4:46:F5:2C:85:86: Garmin International, Inc. (b'\t\xc7')
57:71:48:B7:EF:08: Google (b'\x02\x05\xca\x83\xa9\xc0')
B8:27:EB:28:D4:AA: FortiusANT Trainer
Done -----------------------------

Inspect BLE-device with address D4:46:F5:2C:85:86
<class 'bleak.exc.BleakError'> Could not get GATT services: Unreachable
Inspection done -------------------------------------------------------------------------

Inspect BLE-device with address 57:71:48:B7:EF:08
<class 'asyncio.exceptions.TimeoutError'>
Inspection done -------------------------------------------------------------------------

Inspect BLE-device with address B8:27:EB:28:D4:AA
INFO:bleak.backends.winrt.client:Services resolved for BleakClientWinRT (B8:27:EB:28:D4:AA)
Connected:  True
FortiusANT Trainer: This is a matching Fitness Machine
Service:  00001800-0000-1000-8000-00805f9b34fb (Handle: 1): Generic Access Profile
        Characteristic: 00002a00-... (Handle: 2):                               , props=['read'], value="FortiusANT Trainer"
        Characteristic: 00002a01-... (Handle: 4):                               , props=['read'], value="80 00"
Service:  00001801-0000-1000-8000-00805f9b34fb (Handle: 6): Generic Attribute Profile
        Characteristic: 00002a05-... (Handle: 7):                               , props=['indicate'], value="(N/A; not readable)"
Service:  00001826-0000-1000-8000-00805f9b34fb (Handle: 10): Fitness Machine
        Characteristic: 00002acc-... (Handle: 11): Fitness Machine Feature      , props=['read'], value="02 40 00 00 08 20 00 00"
                Supported: Cadence, PowerMeasurement, PowerTargetSetting, IndoorBikeSimulation.
        Characteristic: 00002ad2-... (Handle: 14): Indoor Bike Data             , props=['notify'], value="(N/A: Wait for notification)"
        Characteristic: 00002ada-... (Handle: 18): Fitness Machine Status       , props=['notify'], value="(N/A: Wait for notification)"
        Characteristic: 00002ad9-... (Handle: 22): Fitness Machine Control Point, props=['write', 'indicate'], value="(N/A; not readable)"
        Characteristic: 00002ad8-... (Handle: 26): Supported Power Range        , props=['read'], value="00 00 e8 03 01 00"
Service:  0000180d-0000-1000-8000-00805f9b34fb (Handle: 29): Heart Rate
        Characteristic: 00002a37-... (Handle: 30): Heart Rate Measurement       , props=['notify'], value="(N/A: Wait for notification)"
Wait for notifications on : ['00002ad2-0000-1000-8000-00805f9b34fb', '00002ada-0000-1000-8000-00805f9b34fb', '00002a37-0000-1000-8000-00805f9b34fb']
30 Heart Rate Measurement "00 00"                   speed=0 cadence=0 power=0 hrm=0
14 Indoor Bike Data       "44 00 00 00 e2 00 f6 00" speed=0 cadence=113.0 power=246 hrm=0
14 Indoor Bike Data       "44 00 00 00 e2 00 f6 00" speed=0 cadence=113.0 power=246 hrm=0
30 Heart Rate Measurement "00 00"                   speed=0 cadence=113.0 power=246 hrm=0
14 Indoor Bike Data       "44 00 00 00 e2 00 f6 00" speed=0 cadence=113.0 power=246 hrm=0
...
Inspection done -------------------------------------------------------------------------

"""