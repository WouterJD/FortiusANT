#-------------------------------------------------------------------------------
# Description
#-------------------------------------------------------------------------------
# The bless library enables python programs to access Bluetooth Low Energy
# as a server. This enables FortiusAnt to create a FTMS (FTMS FiTness Machine Server)
# and communicate with a CTP (which is the client, refer bleBleak.py).
#
#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2022-03-01"
# 2022-03-01    Simulation tested on Windows 10 with Trainer Road and Rouvy
#
# 2020-12-18    First version, obtained from: " hbldh\bless"
#               examples\gattserver.py
#               Example for a BLE 4.0 Server using a GATT dictionary of
#               characteristics
#-------------------------------------------------------------------------------
# The ble-functions are not encapsulated in a class for the following reason:
# 1. async functions, I have no clue what the impact is to move to class methods
# 2. call back functions required, require translation into class-methods
#-------------------------------------------------------------------------------
import asyncio
import atexit
import logging
import random
from   socket               import timeout
import struct
import time
import threading

from typing import Any, Dict

from bless import (
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )

import bleConstants         as bc
from   constants            import mode_Power, mode_Grade, UseBluetooth
import debug
import FortiusAntCommand    as cmd
import logfile
import structConstants      as sc

#-------------------------------------------------------------------------------
# Define the server structure with services and characteristics
# 2022-02-22 Note, see https://github.com/kevincar/bless/issues/67
#            Value should be with a capital, but currently bless uses "value".
#            Therefore both Value/value are present, to avoid future issues.
#-------------------------------------------------------------------------------
FitnessMachineGatt: Dict = {
    bc.sFitnessMachineUUID: {
        bc.cFitnessMachineFeatureUUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        bc.fmf_Info,                        # b'\x02\x40\x00\x00\x08\x20\x00\x00',
            "value":        bc.fmf_Info,
            "Description":  bc.cFitnessMachineFeatureName
        },
        bc.cIndoorBikeDataUUID: {
            "Properties":   (GATTCharacteristicProperties.notify),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        bc.ibd_Info,                        # Instantaneous Cadence, Power, HeartRate
            "value":        bc.ibd_Info,
            "Description":  bc.cIndoorBikeDataName
        },
        bc.cFitnessMachineStatusUUID: {
            "Properties":   (GATTCharacteristicProperties.notify),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "value":        b'\x00\x00',                        # Status as "sent" to Cycling Training Program
            "Value":        b'\x00\x00',
            "Description":  bc.cFitnessMachineStatusName
        },
        bc.cFitnessMachineControlPointUUID: {
            "Properties":   (GATTCharacteristicProperties.write | GATTCharacteristicProperties.indicate),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\x00\x00',                        # Commands as received from Cycling Training Program
            "value":        b'\x00\x00',
            "Description":  bc.cFitnessMachineControlPointName
        },
        bc.cSupportedPowerRangeUUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        bc.spr_Info,                        # Static additional properties of the FTMS
                                                                # b'\x00\x00\xe8\x03\x01\x00'
                                                                # min=0, max=1000, incr=1 
                                                                # ==> 0x0000 0x03e8 0x0001 ==> 0x0000 0xe803 0x0100
            "value":        bc.spr_Info,
            "Description":  bc.cSupportedPowerRangeName
        }
    },
    bc.sHeartRateUUID: {
        bc.cHeartRateMeasurementUUID: {
            "Properties":   (GATTCharacteristicProperties.notify),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        bc.hrm_Info,
            "value":        bc.hrm_Info,
            "Description":  bc.cHeartRateMeasurementName
        },
    }
}

#-------------------------------------------------------------------------------
# c l s F T M S _ b l e s s 
#-------------------------------------------------------------------------------
# Class to create an FiTnessMachineServer, based upon bless
#-------------------------------------------------------------------------------
class clsFTMS_bless:
    #---------------------------------------------------------------------------
    # Athlete data
    #---------------------------------------------------------------------------
    HeartRate           = 0

    #---------------------------------------------------------------------------
    # Trainer data
    #---------------------------------------------------------------------------
    CurrentSpeed        = 0         # km/hour
    Cadence             = 0         # /minute
    CurrentPower        = 0         # Watt

    #---------------------------------------------------------------------------
    # CTP data
    #---------------------------------------------------------------------------
    TargetMode          = None      # No target received
    TargetGrade         = 0         # %
    TargetPower         = 0         # Watt

    WindResistance      = None
    WindSpeed           = None
    DraftingFactor      = 1         # Default since not supplied
    RollingResistance   = None

    #---------------------------------------------------------------------------
    # External attributes
    #---------------------------------------------------------------------------
    Message             = ''            # Shows status of interface

    #---------------------------------------------------------------------------
    # Internal processing data
    #---------------------------------------------------------------------------
    OK                  = False         # FTMS is operational
    BlessServer         = None          # The BlessServer instance
    loop                = None          # Loop instance to support BlessServer
    HasControl          = False         # CTP is controlling the FTMS
    Started             = False         # A CTP training is started

    # --------------------------------------------------------------------------
    # _ _ i n i t _ _
    # --------------------------------------------------------------------------
    # Input     FortiusAnt' command line variables
    #
    # Function  Create the instance, FTMS starting is done through Open().
    #
    # Output    .Message
    # --------------------------------------------------------------------------
    def __init__(self, clv):
        if UseBluetooth and clv.ble:
            self.Message   = ", Bluetooth interface available (bless)"
            #-------------------------------------------------------------------
            # register self.Close() to make sure the BLE server is stopped
            #   ON program termination
            # Note that __del__ is called too late to be able to close.
            #-------------------------------------------------------------------
            atexit.register(self.Close)

        else:
            self.Message   = "" # Bluetooth disabled or not used

    # --------------------------------------------------------------------------
    # O p e n
    # --------------------------------------------------------------------------
    # Input     None
    #
    # Function  In a separate thread;
    #               Create a loop and then activate FortiusAntServer
    #
    # Output    OK = True
    #           loop
    #
    # Returns   self.OK
    # --------------------------------------------------------------------------
    def Open(self):
        #-----------------------------------------------------------------------
        # Logging
        #-----------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless.Open()")

        #-----------------------------------------------------------------------
        # Create a thread and run the server in that thread
        #-----------------------------------------------------------------------
        thread = threading.Thread(target=self._OpenThread)
        thread.start()

        #-----------------------------------------------------------------------
        # Allow thread to start
        #-----------------------------------------------------------------------
        time.sleep(1)

        #-----------------------------------------------------------------------
        # After a second, it will be clear that we're OK
        # (For the time being, at least)
        #-----------------------------------------------------------------------
        return self.OK

    def _OpenThread(self):
        self.OK      = True
        self.Message = ", Bluetooth interface open" # Assume it will work OK

        #loop = asyncio.get_event_loop()            # Crashes: "There is no current event loop in thread"
        self.loop    = asyncio.new_event_loop()     # Because we're in a thread
        self.loop.run_until_complete(self._FortiusAntServer())

    # --------------------------------------------------------------------------
    # SetAthleteData, SetTrainerData
    # --------------------------------------------------------------------------
    # Input     function parameters
    #
    # Function  Provide trainer data to the FTMS, to be transmitted to CTP
    #
    # Output    OK = False
    # --------------------------------------------------------------------------
    def SetAthleteData(self, HeartRate):
        #-----------------------------------------------------------------------
        # Logging
        #-----------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless.SetAthleteData(%s)" % HeartRate)

        #-----------------------------------------------------------------------
        # Remember provided data
        #-----------------------------------------------------------------------
        self.HeartRate = HeartRate

        #-----------------------------------------------------------------------
        # Update heartrate in FTMS
        #-----------------------------------------------------------------------
        if self.OK:
            flags = 0
            h     = int(self.HeartRate) & 0xff      # Avoid value anomalities
            info = struct.pack (sc.little_endian + sc.unsigned_char * 2, flags, h)
            self.BlessServer.get_characteristic(bc.cHeartRateMeasurementUUID).value = info
            self.BlessServer.update_value(bc.sHeartRateUUID, bc.cHeartRateMeasurementUUID)
        else:
            logfile.Console("bleBless.SetAthleteData() error, interface not open")

    def SetTrainerData(self, CurrentSpeed, Cadence, CurrentPower):
        #-----------------------------------------------------------------------
        # Logging
        #-----------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless.SetTrainerData(%s, %s, %s)" % (CurrentSpeed, Cadence, CurrentPower))

        #-----------------------------------------------------------------------
        # Remember provided data
        #-----------------------------------------------------------------------
        self.CurrentSpeed = CurrentSpeed
        self.Cadence      = Cadence
        self.CurrentPower = CurrentPower

        #-----------------------------------------------------------------------
        # Update trainer status in FTMS
        # Note that: Speed always present UNLESS...)
        #            HeartRate not transmitted, is not used.
        #-----------------------------------------------------------------------
        if self.OK:
            flags = (bc.ibd_InstantaneousCadencePresent | bc.ibd_InstantaneousPowerPresent)
            s     = int(self.CurrentSpeed * 100) & 0xffff      # Avoid value anomalities
            c     = int(self.Cadence * 2)        & 0xffff      # Avoid value anomalities
            p     = int(self.CurrentPower)       & 0xffff      # Avoid value anomalities
            info  = struct.pack (sc.little_endian + sc.unsigned_short * 4, flags, s, c, p)

            self.BlessServer.get_characteristic(bc.cIndoorBikeDataUUID).value = info
            self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cIndoorBikeDataUUID)
        else:
            logfile.Console("bleBless.SetTrainerData() error, interface not open")

    # --------------------------------------------------------------------------
    # R e f r e s h
    # --------------------------------------------------------------------------
    # Input     None
    #
    # Function  This function could be used to implement send/receive
    #           but that is not required
    #           Therefore return True when bluetooth is enabled and Server OK
    #
    # Returns   True when data is available
    # --------------------------------------------------------------------------
    def Refresh(self):
        rtn                 = False

        if UseBluetooth:
            if self.OK:
                rtn         = True

        return rtn

    # --------------------------------------------------------------------------
    # C l o s e
    # --------------------------------------------------------------------------
    # Input     None
    #
    # Function  Indicate that FortiusAntServer() must stop
    #
    # Output    OK = False
    # --------------------------------------------------------------------------
    def Close(self):
        #-----------------------------------------------------------------------
        # Logging
        #-----------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless.Close()")

        #-----------------------------------------------------------------------
        # Signal FortiusAntServer to stop
        #-----------------------------------------------------------------------
        self.Message = ", Bluetooth interface closed"
        self.OK      = False

    #---------------------------------------------------------------------------
    # _ R e a d R e q u e s t
    #---------------------------------------------------------------------------
    # Input:    characteristic for which the value is requested
    #
    # Function  Return the requested value, without further processing
    #
    # Output:   characteristic.value
    #---------------------------------------------------------------------------
    def _ReadRequest(self,
            characteristic: BlessGATTCharacteristic,
            **kwargs
            ) -> bytearray:

        #print('characteristic -----------------------------')
        #print('\n'.join("%s: %s" % item for item in vars(characteristic).items()))
        #print('characteristic --------------------------end')

        uuid  = str(characteristic._uuid)
        if   uuid == bc.cFitnessMachineFeatureUUID:      char = bc.cFitnessMachineFeatureName
        elif uuid == bc.cIndoorBikeDataUUID:             char = bc.cIndoorBikeDataName
        elif uuid == bc.cFitnessMachineStatusUUID:       char = bc.cFitnessMachineStatusName
        elif uuid == bc.cFitnessMachineControlPointUUID: char = bc.cFitnessMachineControlPointName
        elif uuid == bc.cSupportedPowerRangeUUID:        char = bc.cSupportedPowerRangeName
        elif uuid == bc.cHeartRateMeasurementUUID:       char = bc.cHeartRateMeasurementUUID
        else:                                            char = "?"
        #---------------------------------------------------------------------------
        # Logging
        #---------------------------------------------------------------------------
        if debug.on(debug.Ble):
            logfile.Write('bleBless: Read request for characteristic "%s", value = %s' %
                            (char, logfile.HexSpace(characteristic._value)))

        return characteristic.value

    #-------------------------------------------------------------------------------
    # _ W r i t e R e q u e s t
    #-------------------------------------------------------------------------------
    # Input:    characteristic for which the value must be updated
    #
    # Function  Return...
    #
    # Output:   ...
    #-------------------------------------------------------------------------------
    def _WriteRequest(self,
            characteristic: BlessGATTCharacteristic,
            value: Any,
            **kwargs
            ):

        uuid  = str(characteristic._uuid)
        if   uuid == bc.cFitnessMachineFeatureUUID:      char = bc.cFitnessMachineFeatureName
        elif uuid == bc.cIndoorBikeDataUUID:             char = bc.cIndoorBikeDataName
        elif uuid == bc.cFitnessMachineStatusUUID:       char = bc.cFitnessMachineStatusName
        elif uuid == bc.cFitnessMachineControlPointUUID: char = bc.cFitnessMachineControlPointName
        elif uuid == bc.cSupportedPowerRangeUUID:        char = bc.cSupportedPowerRangeName
        elif uuid == bc.cHeartRateMeasurementUUID:       char = bc.cHeartRateMeasurementUUID
        else:                                            char = "?"
        
        #---------------------------------------------------------------------------
        # Logging
        #---------------------------------------------------------------------------
        if debug.on(debug.Ble):
            logfile.Write('bleBless: Write request for characteristic "%s", actual value = %s, provided value = %s' %
                (char, logfile.HexSpace(characteristic.value), logfile.HexSpace(value)))

        #---------------------------------------------------------------------------
        # MachineControlPoint modifies behaviour; the only write we expect
        #---------------------------------------------------------------------------
        if not uuid == bc.cFitnessMachineControlPointUUID:
            logfile.Console('bleBless error: Write request on "%s" characteristic is not supported; ignored.' % char)

        else:
            OpCode     = int(value[0])    # The operation to be performed
            ResultCode = bc.fmcp_Success  # Let's assume it will be OK

            UseWorkflow  = True           # A CTP must request control to be able to
                                          # send further requests and Start before
                                          # changing TargetPower/Grade
                                          # If UseWorkflow == False, these checks
                                          # are disabled.
                                          #
                                          # Funny things is, that HasControl suggests
                                          # a check, but if the CTP proceeds regard-
                                          # less, the Request would be accepted
                                          # Unless there we would know what CTP has
                                          # been granted access...
                                          #
                                          # Now that _FortiusAntServer() detects
                                          # a disconnect, the workflow can be enabled.
            #-----------------------------------------------------------------------
            # React on requested operation
            # - check workflow
            # - accept values and/or modify internal state (HasControl, Started)
            # - notify client that value is changed (FitnessMachineStatus)
            # - notify that operation is completed (ResultCode)
            #-----------------------------------------------------------------------
            if OpCode == bc.fmcp_RequestControl:
                if not UseWorkflow or not self.HasControl:
                    self.HasControl = True
                    self.Started    = False
                    if debug.on(debug.Ble): logfile.Write("bleBless: HasControl = True")
                    self.Message   = ", Bluetooth interface controlled"
                else:
                    ResultCode = bc.fmcp_ControlNotPermitted
                    logfile.Console("bleBless error: control requested by client, control already granted")

            elif UseWorkflow and not self.HasControl:
                ResultCode = bc.fmcp_ControlNotPermitted
                logfile.Console("bleBless error: request received, but client has no control")

            else:
                if OpCode == bc.fmcp_StartOrResume:
                    self.Started = True
                    if debug.on(debug.Ble): logfile.Write("bleBless: Started = True")
                    self.notifyStartOrResume()              # Confirm receipt to client
                    self.Message   = ", Bluetooth interface training started"

                elif OpCode == bc.fmcp_SetTargetPower:
                    tuple  = struct.unpack (sc.little_endian + sc.unsigned_char + sc.unsigned_short, value)
                    #opcode          = tuple[0]
                    self.TargetPower = tuple[1]
                    self.TargetGrade = None
                    self.TargetMode  = mode_Power
                    if debug.on(debug.Ble): logfile.Write("bleBless: TargetPower = %s" % self.TargetPower)
                    self.notifySetTargetPower()             # Confirm receipt to client
                    self.Message   = ", Bluetooth interface in power mode"

                elif OpCode == bc.fmcp_SetIndoorBikeSimulation:
                    tuple  = struct.unpack (sc.little_endian + sc.unsigned_char + sc.short + sc.short + sc.unsigned_char + sc.unsigned_char, value)
                    #opcode                = tuple[0]
                    self.WindSpeed         = tuple[1] * 0.001
                    self.TargetGrade       = tuple[2] * 0.01
                    self.TargetPower       = None
                    self.TargetMode        = mode_Grade
                    self.RollingResistance = tuple[3] * 0.0001
                    self.WindResistance    = tuple[4] * 0.01
                    if debug.on(debug.Ble): logfile.Write(
                           "bleBless: windspeed=%s, TargetGrade=%s, RollingResistance=%s, WindResistance=%s" %
                           (self.WindSpeed, self.TargetGrade, self.RollingResistance, self.WindResistance))
                    self.notifySetIndoorBikeSimulation()    # Confirm receipt to client
                    self.Message   = ", Bluetooth interface in grade mode"

                elif OpCode == bc.fmcp_StopOrPause:
                    self.Started = False
                    if debug.on(debug.Ble): logfile.Write("bleBless: Started = False")
                    self.notifyStopOrPause()                # Confirm receipt to client
                    self.Message   = ", Bluetooth interface training stopped"

                elif OpCode == bc.fmcp_Reset:
                    self.Started    = False
                    self.HasControl = False
                    if debug.on(debug.Ble): logfile.Write("bleBless: HasControl = False")
                    self.notifyReset()                      # Confirm receipt to client
                    self.Message   = ", Bluetooth interface open"

                else:
                    logfile.Console("bleBless error: Unknown OpCode %s" % OpCode)
                    ResultCode = bc.fmcp_ControlNotPermitted

            #-----------------------------------------------------------------------
            # Response:
            #-----------------------------------------------------------------------
            ResponseCode = 0x80
            info = struct.pack(sc.little_endian + sc.unsigned_char * 3, ResponseCode, OpCode, ResultCode)
            characteristic.value = info
            self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineControlPointUUID)

            if False and debug.on(debug.Ble):
                logfile.Write("bleBless: New value for characteristic %s = %s" % (char, logfile.HexSpace(info)))

    # --------------------------------------------------------------------------
    # After that a characteristic is written, it must also be confirmed through
    # a notification in FitnessMachineStatus
    # --------------------------------------------------------------------------
    def notifyStartOrResume(self):
        if debug.on(debug.Ble): logfile.Write("bleBless.notifyStartOrResume()")
        info = struct.pack(sc.little_endian + sc.unsigned_char, bc.fms_FitnessMachineStartedOrResumedByUser)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifySetTargetPower(self):
        if debug.on(debug.Ble): logfile.Write("bleBless.notifySetTargetPower()")
        info = struct.pack(sc.little_endian + sc.unsigned_char + sc.unsigned_short, bc.fms_TargetPowerChanged, self.TargetPower)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifySetIndoorBikeSimulation(self):
        if debug.on(debug.Ble): logfile.Write("bleBless.notifySetIndoorBikeSimulation()")

        windSpeed = int(self.WindSpeed         / 0.001 )
        grade     = int(self.TargetGrade       / 0.01  )
        crr       = int(self.RollingResistance / 0.0001)
        cw        = int(self.WindResistance    / 0.01  )

        info = struct.pack(sc.little_endian + sc.unsigned_char + sc.short * 2 + sc.unsigned_char * 2,
                            bc.fms_IndoorBikeSimulationParametersChanged, windSpeed, grade, crr, cw)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifyStopOrPause(self):
        if debug.on(debug.Ble): logfile.Write("bleBless.notifyStopOrPause()")
        info = struct.pack(sc.little_endian + sc.unsigned_char, bc.fms_FitnessMachineStoppedOrPausedByUser)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifyReset(self):
        if debug.on(debug.Ble): logfile.Write("bleBless.notifyReset()")
        info = struct.pack(sc.little_endian + sc.unsigned_char, bc.fms_Reset)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    # ------------------------------------------------------------------------------
    # _ F o r t i u s A n t S e r v e r
    # ------------------------------------------------------------------------------
    # Input     .OK
    #           .loop
    #
    # Function  A BLE-server is created with the required services and characteristics
    #           The server will remain active until stop_FortiusAntServer() is called
    #
    # Output    BLE Server/Service/Characteristics
    # ------------------------------------------------------------------------------
    async def _FortiusAntServer(self):
        myServiceName = "FortiusANT Trainer"
        #---------------------------------------------------------------------------
        # Create the server
        #---------------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless._FortiusAntServer(): BlessServer(%s)" % myServiceName)

        if self.OK:
            self.BlessServer = BlessServer(name=myServiceName, loop=self.loop)
            
            self.BlessServer.read_request_func  = self._ReadRequest
            self.BlessServer.write_request_func = self._WriteRequest

        #---------------------------------------------------------------------------
        # Add the services
        # Windows 10: BLE crashes on add_gatt() if there is no BLE-5 dongle
        #             BLE crashed on start()    if interface is not compatible
        #---------------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless._FortiusAntServer(): self.BlessServer.add_gatt()")
        if self.OK:
            try:
                await self.BlessServer.add_gatt(FitnessMachineGatt)
            except Exception as e:
                self.OK = False
                if debug.on(debug.Ble):
                    logfile.Console("bleBless; exception %s" % e)

        if debug.on(debug.Ble): logfile.Write("bleBless._FortiusAntServer(): self.BlessServer.start()")
        if self.OK:
            try:
                await self.BlessServer.start()
            except Exception as e:
                self.OK = False
                if debug.on(debug.Ble):
                    logfile.Console("bleBless; exception %s" % e)

        if not self.OK:
            self.Message = ", Bluetooth interface n/a; BLE-5 required!"
            logfile.Console(self.Message)

        #---------------------------------------------------------------------------
        # DEBUG: Check that all characteristics are actually accepted
        #        Issue resolved by defining Value and value, see above 
        #---------------------------------------------------------------------------
        if False and self.OK:
            for sUUID, sINFO in FitnessMachineGatt.items():
                logfile.Console("Service: %s" % sUUID)
                for cUUID, cINFO in sINFO.items():
                    v = self.BlessServer.get_characteristic(cUUID).value
                    logfile.Console("\t\t %s=%s" % (cINFO["Description"], logfile.HexSpace(v)))
                    if not v:
                        print("FitnessMachineGatt has a .value / .Value conflict; see https://github.com/kevincar/bless/issues/67!!")

        #---------------------------------------------------------------------------
        # FortiusAntServer is now active
        # read/write through _ReadRequest() and _WriteRequest() functions
        # FortiusAntServer will stop when OK = False.
        #---------------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless._FortiusAntServer(): go into loop")
        WeWereOK = self.OK
        while self.OK:
            await asyncio.sleep(1)
            #-----------------------------------------------------------------------
            # Check whether there are clients connected
            # If a CTP had control (and started) but disconnects, implicit reset.
            #-----------------------------------------------------------------------
            # await b = self.BlessServer.is_connected()  ... This is not allowed
            b = len(self.BlessServer._subscribed_clients) > 0

            if not b and (self.Started or self.HasControl):
                self.Started    = False
                self.HasControl = False
                if debug.on(debug.Ble): logfile.Write(
                    "bleBless: A CTP was active and is disconnected; reset executed.")

            #-----------------------------------------------------------------------
            # Show actual status
            #-----------------------------------------------------------------------
            if False and debug.on(debug.Ble): logfile.Write(
                "bleBless: FTMS alive; HasControl=%-5s Started=%-5s TargetPower=%4s TargetGrade=%4s Speed=%3s Cadence=%3s, Power=%3s, HeartRate=%3s" %
                (self.HasControl, self.Started, self.TargetPower, self.TargetGrade, self.CurrentSpeed, self.Cadence, self.CurrentPower, self.HeartRate))

        #---------------------------------------------------------------------------
        # Cleanup
        # self.OK is always False, since set by Close()!!
        #---------------------------------------------------------------------------
        if WeWereOK:
            if debug.on(debug.Ble): logfile.Write("bleBless._FortiusAntServer(): self.BlessServer.stop()")
            await self.BlessServer.stop()

        #-----------------------------------------------------------------------
        # Logging
        #-----------------------------------------------------------------------
        if debug.on(debug.Ble): logfile.Write("bleBless._FortiusAntServer() ended")

    # ------------------------------------------------------------------------------
    # S i m u l a t o r
    # ------------------------------------------------------------------------------
    # Input     None
    #
    # Function  For test-purpose, simulate a trainer for 10 cycles of a second,
    #           with random data.
    #
    # Output    The interface is used, no further output.
    # ------------------------------------------------------------------------------
    def Simulator(self):
        logfile.Console("---------------------------------------------------------------------------------------")
        logfile.Console("FortiusAnt simulated trainer is active")
        logfile.Console("Start a training in a CTP; 5 seconds after completing the training, simulation will end")
        logfile.Console("---------------------------------------------------------------------------------------")

        #---------------------------------------------------------------------------
        # FortiusAntServer is now active
        # read/write through read_Request() and write_Request() functions
        #---------------------------------------------------------------------------
        CurrentSpeed, Cadence, CurrentPower, HeartRate = (0, 0, 0, 0)
        TrainingStarted = False
        i = 5
        while i:
            #-----------------------------------------------------------------------
            # Stop 5 seconds after a training is stopped
            # - Should be, because CTP starts/stops (but TrainerRoad does not ??)
            # - TargetPower is back to 50 Watt after that it was different
            #-----------------------------------------------------------------------
            if self.TargetPower > 100:              # self.Started
                TrainingStarted = True

            if TrainingStarted:
                if self.TargetPower <= 50:          # not self.Started
                    i -= 1
                    pass

            #-----------------------------------------------------------------------
            # Update trainer info every second
            #-----------------------------------------------------------------------
            time.sleep(1)

            #-----------------------------------------------------------------------
            # Just make up some fancy data
            #-----------------------------------------------------------------------
            if False:
                CurrentSpeed= 34.5
                HeartRate   = 135
                CurrentPower= 246
                Cadence     = 113
            else:
                HRmax       = 180
                ftp         = 246   # at 80% HRmax

                if self.TargetMode == None:
                    self.TargetPower = 100 + self.TargetGrade * 20

                deltaPower    = (self.TargetPower - self.CurrentPower)
                    
                if deltaPower < 8:
                    CurrentPower = self.TargetPower
                    deltaPower   = 0
                else:
                    CurrentPower = self.CurrentPower + deltaPower / 8           # Step towards TargetPower
                CurrentPower *= (1 + random.randint(-3,3) / 100)                # Variation of 5%

                Cadence       = 100 - min(10, deltaPower) / 10                  # Cadence drops when Target increases
                Cadence      *= (1 + random.randint(-2,2) / 100)                # Variation of 2%

                CurrentSpeed  = 35 * Cadence / 100                              # Speed is 35 kmh at cadence 100 (My highest gear)

                HeartRate     = HRmax * (0.5 + ((CurrentPower - 100) / (ftp - 100) ) * 0.3)
                                                                                # As if power is linear with power
                                                                                # 100W is reached at 50%
                                                                                # ftp  is reached at 80%
                                                                                # Assume lineair between 100W and ftp
                if HeartRate < HRmax * 0.5: HeartRate = HRmax * 0.5             # minimize HR
                if HeartRate > HRmax:       HeartRate = HRmax                   # maximize HR
                HeartRate    += random.randint(-5,5)                            # Variation of heartrate by 5 beats

            # ----------------------------------------------------------------------
            # Round after all these calculations (and correct data type!) #361 
            # ----------------------------------------------------------------------
            Cadence             = int(Cadence)
            CurrentPower        = int(CurrentPower)
            HeartRate           = int(HeartRate)
            CurrentSpeed        = round(CurrentSpeed,1)

            #-----------------------------------------------------------------------
            # Update trainer data
            # The appropriate functions are used, like FortiusAnt will do
            #-----------------------------------------------------------------------
            self.SetAthleteData(HeartRate)
            self.SetTrainerData(CurrentSpeed, Cadence, CurrentPower)

            #-----------------------------------------------------------------------
            # Show current status
            #-----------------------------------------------------------------------
            print(
                "HasControl=%-5s Started=%-5s TargetPower=%4s TargetGrade=%4s Speed=%3s Cadence=%3s, Power=%3s, HeartRate=%3s" %
                (self.HasControl, self.Started, self.TargetPower, self.TargetGrade, self.CurrentSpeed, self.Cadence, self.CurrentPower, self.HeartRate))

        logfile.Console("FortiusAnt simulated trainer is stopped")
        logfile.Console("---------------------------------------")

# ==============================================================================
# Main program
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name=__name__)

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    clv       = cmd.CommandLineVariables()
    clv.ble   = True
    clv.debug = debug.Ble
    debug.activate(clv.debug)

    if debug.on(debug.Ble):
        logfile.Open()
        logfile.Console("bleBless started")
        clv.print()
        logfile.Console("------------------")

    #---------------------------------------------------------------------------
    # This is what it's all about
    #---------------------------------------------------------------------------
    FortiusAntServer = clsFTMS_bless(clv)
    logfile.Console("Message=%s" % FortiusAntServer.Message)
    b = FortiusAntServer.Open()
    logfile.Console("Message=%s" % FortiusAntServer.Message)
    if b:
        FortiusAntServer.Simulator()
        FortiusAntServer.Close()
        logfile.Console("Message=%s" % FortiusAntServer.Message)

    #---------------------------------------------------------------------------
    # Termination
    #---------------------------------------------------------------------------
    if debug.on(debug.Ble):
        logfile.Console("bleBless ended")