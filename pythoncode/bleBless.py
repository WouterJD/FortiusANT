#-------------------------------------------------------------------------------
# Description
#-------------------------------------------------------------------------------
# The bless library enables python programs to access Bluetooth Low Energy
# as a server. This enables FortiusAnt to create a FTMS (FTMS FiTness Machine Server)
# and communicate with a CTP (which is the client, refer bleBleak.py).
#
# FortiusAnt uses class clsFTMS_bless, based upon clsBleServer
# This file can be executed and then a simulator is started for demo/test purpose.
#
#-------------------------------------------------------------------------------
# Author        https://github.com/WouterJD
#               wouter.dubbeldam@xs4all.nl
#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2022-08-10"
# 2022-08-10    Steering implemented according marcoveeneman and switchable's code
# 2022-04-12    TargetMode is initially None, so that FortiusAnt knowns that no
#               command is yet received.
#               Issue was that, when ANT and BLE both active and a CTP is active
#               on ANT then the BLE-interface should not overwrite the values!
# 2022-03-28    logfileTraceback() added
# 2022-03-21    Made available to kevincar/bless as example; small modifications
# 2022-03-08    Class to create a bless server split into bleBlessClass.py
# 2022-03-08    Tested:
#               - Windows 10 with Trainer Road and Rouvy
#               - Raspberry  with
# 2022-03-07    Major revision; make fit to share with bless as example
# 2022-03-01    Simulation tested on Windows 10 with Trainer Road and Rouvy
#
# 2020-12-18    First version, obtained from: " hbldh\bless"
#               examples\gattserver.py
#               Example for a BLE 4.0 Server using a GATT dictionary of
#               characteristics
#-------------------------------------------------------------------------------
import struct
import time

from typing import Any, Dict

from bless import (
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )

if True:
    BlessExample = False
    #---------------------------------------------------------------------------
    # Import in the FortiusAnt context
    #---------------------------------------------------------------------------
    import debug
    import logfile
    from   constants            import mode_Power, mode_Grade, UseBluetooth
    from   logfile              import HexSpace
    from   bleBlessClass        import clsBleServer
    import bleConstants         as bc

else:
    BlessExample = True
    #---------------------------------------------------------------------------
    # Import and Constants for bless example context
    #---------------------------------------------------------------------------
    from   FTMSserverClass      import clsBleServer
    import FTMSconstants        as bc
    from   FTMSconstants        import HexSpace
    import logging

    mode_Power          = 1     # Target Power
    mode_Grade          = 2     # Target Resistance
    UseBluetooth        = True

#-------------------------------------------------------------------------------
# Define the server structure with services and characteristics
# 2022-02-22 Note, see https://github.com/kevincar/bless/issues/67
#            Value should be with a capital, but currently bless uses "value".
#            Therefore both Value/value are present, to avoid future issues.
#-------------------------------------------------------------------------------

"""
    Is not allowed to be added in the GATT definition: failed to create entry in database
    This 'may be' because it's a standard service, but then: how to set the two characteristics?

    Definition as discovered from NodeJs:

    bc.sGenericAccessUUID: {
        bc.cDeviceNameUUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'FortiusAntTrainer',
            "value":        b'FortiusAntTrainer',
            "Description":  bc.cDeviceNameName
        },
        bc.cAppearanceUUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\x80\x00',
            "value":        b'\x80\x00',
            "Description":  bc.cAppearanceName
        },
    },

    Definition as suggested by Kevin: https://github.com/kevincar/bless/discussions/76#discussioncomment-2380163

    "<YOUR SERVICE UUID>": {
       bc.cDeviceNameUUID: {
           "Properties":   (GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate),
           "Permissions":  (GATTAttributePermissions.readable),
           "Value":        "My Device Name",
           "Description":  bc.cDeviceNameName
       },
       bc.cAppearanceUUID: {
           "Properties":   (GATTCharacteristicProperties.read | GATTCharacteristicProperties.indicate),
           "Permissions":  (GATTAttributePermissions.readable),
           "Value":        "My Appearance",
           "Description":  bc.cAppearanceName
       }
    },

    # On Windows 10:
    #     bc.sGenericAccessUUID: { ... containing the two characteristics ... }
    #       results in:
    #           clsBleServer._Server(); add_gatt() exception 'NoneType' object has no attribute 'add_advertisement_status_changed'
    #
    #     bc.sFitnessMachineUUID: { ... containing the two characteristics ... }
    #       results in that characteristic can be read by client, but Trainer Road does still provide TP-T430 as service name.
    #
    #     bc.sGenericAccessUUID_private: { ... containing the two characteristics ... }
    #       has the same effect.
    #       bleBleak considers the service to be "vendor specific"
    #
    # On Raspberry:
    #     bc.sGenericAccessUUID: { ... containing the two characteristics ... }
    #       results in:
    #            clsBleServer._Server(); start() exception org.bluez.Error.Failed: Failed to create entry in database
    #
    #     bc.sGenericAccessUUID_private: { ... containing the two characteristics ... }
    #       This confuses bleak at the Windows 10 side (duplicate keys, FTMS not found)

    "<YOUR SERVICE UUID>": {            # This line is modified as explained above
        bc.cDeviceNameUUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'FortiusAntTrainer',
            "value":        b'FortiusAntTrainer',
            "Description":  bc.cDeviceNameName
        },
        bc.cAppearanceUUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\x80\x00',
            "value":        b'\x80\x00',
            "Description":  bc.cAppearanceName
        },
    },
"""

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
        }
    },
    bc.sSteeringUUID: {
        bc.cSteeringUnknown1UUID: {
            "Properties":   (GATTCharacteristicProperties.write),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\x00\x00',
            "value":        b'\x00\x00',
            "Description":  bc.cSteeringUnknown1Name
        },
        bc.cSteeringUnknown2UUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\xff',
            "value":        b'\xff',
            "Description":  bc.cSteeringUnknown2Name
        },
        bc.cSteeringUnknown3UUID: {
            "Properties":   (GATTCharacteristicProperties.notify),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\x00',
            "value":        b'\x00',
            "Description":  bc.cSteeringUnknown3Name
        },
        bc.cSteeringUnknown4UUID: {
            "Properties":   (GATTCharacteristicProperties.read),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\xff',
            "value":        b'\xff',
            "Description":  bc.cSteeringUnknown4Name
        },
        bc.cSteeringAngleUUID: {
            "Properties":   (GATTCharacteristicProperties.notify),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        bc.angle_Info,
            "value":        bc.angle_Info,
            "Description":  bc.cSteeringAngleName
        },
        bc.cSteeringTxUUID: {
            "Properties":   (GATTCharacteristicProperties.indicate),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\x00',
            "value":        b'\x00',
            "Description":  bc.cSteeringTxName
        },
        bc.cSteeringRxUUID: {
            "Properties":   (GATTCharacteristicProperties.write),
            "Permissions":  (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
            "Value":        b'\x00',
            "value":        b'\x00',
            "Description":  bc.cSteeringRxName
        }
    }
}

#-------------------------------------------------------------------------------
# c l s F T M S _ b l e s s 
#-------------------------------------------------------------------------------
# Class to create an FiTnessMachineServer, based upon bless
#
# User methods:
#   See parent class AND
#
#   SetAthleteData  Pass Fitness Machine information to the class
#   SetTrainerData
#
#   Refresh()       Must be called before attributes are used
#
# User attributes:
#   See parent class AND
#   See below
#-------------------------------------------------------------------------------
class clsFTMS_bless(clsBleServer):
    #---------------------------------------------------------------------------
    # CTP data, received through WriteRequest() and sent by client
    #---------------------------------------------------------------------------
    TargetMode          = None          # No target received; and then:
                                        # either mode_Power or mode_Grade
    TargetGrade         = 0             # %
    TargetPower         = 100           # Watt

    WindResistance      = 0
    WindSpeed           = 0
    DraftingFactor      = 1             # Default since not supplied
    RollingResistance   = 0

    #---------------------------------------------------------------------------
    # data provided by SetAthleteData() as called by application
    #---------------------------------------------------------------------------
    HeartRate           = 0

    #---------------------------------------------------------------------------
    # data provided by SetTrainerData() as called by application
    #---------------------------------------------------------------------------
    CurrentSpeed        = 0             # km/hour
    Cadence             = 0             # /minute
    CurrentPower        = 0             # Watt
    SteeringAngle       = 0             # Steering is always present,
                                        # regardless the -S command-line setting
                                        # If no steering, value is zero.

    #---------------------------------------------------------------------------
    # Internal workflow control data
    #---------------------------------------------------------------------------
    HasControl          = False         # CTP is controlling the FTMS
    Started             = False         # A CTP training is started

    # --------------------------------------------------------------------------
    # _ _ i n i t _ _
    # --------------------------------------------------------------------------
    # Input     UseBluetooth; a 'compile-time' flag indicating to use BLE
    #           activate;     command-line flag, indicating to use BLE (-bb)
    #
    # Function  Create the instance, FTMS starting is done through Open().
    #
    # Output    .Message
    # --------------------------------------------------------------------------
    def __init__(self, activate):
        if UseBluetooth and activate:
            super().__init__("FortiusAntTrainer", FitnessMachineGatt)
        else:
            pass                        # Data structure is created, no actions

    # --------------------------------------------------------------------------
    # SetAthleteData, SetTrainerData, SetSteeringAngle
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
        self.logfileWrite("clsFTMS_bless.SetAthleteData(%s)" % HeartRate)

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
            info = struct.pack (bc.little_endian + bc.unsigned_char * 2, flags, h)
            self.BlessServer.get_characteristic(bc.cHeartRateMeasurementUUID).value = info
            self.BlessServer.update_value(bc.sHeartRateUUID, bc.cHeartRateMeasurementUUID)
        else:
            self.logfileConsole("clsFTMS_bless.SetAthleteData() error, interface not open")

    def SetTrainerData(self, CurrentSpeed, Cadence, CurrentPower):
        #-----------------------------------------------------------------------
        # Logging
        #-----------------------------------------------------------------------
        self.logfileWrite("clsFTMS_bless.SetTrainerData(%s, %s, %s)" % (CurrentSpeed, Cadence, CurrentPower))

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
            info  = struct.pack (bc.little_endian + bc.unsigned_short * 4, flags, s, c, p)

            self.BlessServer.get_characteristic(bc.cIndoorBikeDataUUID).value = info
            self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cIndoorBikeDataUUID)
        else:
            self.logfileConsole("clsFTMS_bless.SetTrainerData() error, interface not open")
            
    def SetSteeringAngle(self, SteeringAngle):
        #-----------------------------------------------------------------------
        # Logging
        #-----------------------------------------------------------------------
        self.logfileWrite("clsFTMS_bless.SetSteeringAngle(%s)" % SteeringAngle)

        #-----------------------------------------------------------------------
        # Remember provided data
        #-----------------------------------------------------------------------
        self.SteeringAngle  = SteeringAngle

        #-----------------------------------------------------------------------
        # Update angle in steering
        #-----------------------------------------------------------------------
        if self.OK:
            a    = SteeringAngle      # Avoid value anomalities here (if needed)
            info = struct.pack (bc.little_endian + bc.float, a)
            self.BlessServer.get_characteristic(bc.cSteeringAngleUUID).value = info
            self.BlessServer.update_value(bc.sSteeringUUID, bc.cSteeringAngleUUID)
        else:
            self.logfileConsole("clsFTMS_bless.SetSteeringAngle() error, interface not open")

    # --------------------------------------------------------------------------
    # C l i e n t D i s c o n n e c t e d
    # --------------------------------------------------------------------------
    # Input     None
    #
    # Function  Client is disconnected, reset workflow flags to prepare for next
    #           client-connect
    #
    # Output    HasControl and Started
    # --------------------------------------------------------------------------
    def ClientDisconnected(self):
        self.HasControl = False
        self.Started    = False

    # --------------------------------------------------------------------------
    # R e f r e s h
    # --------------------------------------------------------------------------
    # Input     None
    #
    # Function  Refresh data, so that attributes are accurate and can be used.
    #           Currently no implementation required, could be in future.
    #           Therefore just return OK
    #
    #           self.Refresh() must be called before accessing attributes
    #
    # Returns   self.OK
    # --------------------------------------------------------------------------
    def Refresh(self):
        return self.OK

    #---------------------------------------------------------------------------
    # l o g f i l e W r i t e / C o n s o l e / T r a c e b a c k
    #---------------------------------------------------------------------------
    # Input:    text to be written to logfile
    #
    # Function  Use our own standard logging functions
    #
    # Output:   none
    #---------------------------------------------------------------------------
    if not BlessExample:            # As used in the FortiusAnt context
        def logfileWrite(self, message):
            if debug.on(debug.Ble): logfile.Write(message)

        def logfileConsole(self, message):
            logfile.Console(message)

        def logfileTraceback(self, exception):
            if debug.on(debug.Ble): logfile.Traceback(exception)

    #---------------------------------------------------------------------------
    # R e a d R e q u e s t
    #---------------------------------------------------------------------------
    # Input:    characteristic for which the value is requested
    #
    # Function  Return the requested value, without further processing
    #           Replaces parent class because of enhanced logging
    #
    # Output:   characteristic.value
    #---------------------------------------------------------------------------
    def ReadRequest(self,
            characteristic: BlessGATTCharacteristic,
            **kwargs
            ) -> bytearray:

        uuid  = str(characteristic._uuid)
        if   uuid == bc.cFitnessMachineFeatureUUID:      char = bc.cFitnessMachineFeatureName
        elif uuid == bc.cIndoorBikeDataUUID:             char = bc.cIndoorBikeDataName
        elif uuid == bc.cFitnessMachineStatusUUID:       char = bc.cFitnessMachineStatusName
        elif uuid == bc.cFitnessMachineControlPointUUID: char = bc.cFitnessMachineControlPointName
        elif uuid == bc.cSupportedPowerRangeUUID:        char = bc.cSupportedPowerRangeName
        elif uuid == bc.cHeartRateMeasurementUUID:       char = bc.cHeartRateMeasurementName
        elif uuid == bc.cSteeringAngleUUID:              char = bc.cSteeringAngleName
        else:                                            char = "?"

        #---------------------------------------------------------------------------
        # Logging
        #---------------------------------------------------------------------------
        self.logfileWrite('clsFTMS_bless.ReadRequest(): characteristic "%s", value = %s' %
                            (char, HexSpace(characteristic._value)))

        return characteristic.value

    #-------------------------------------------------------------------------------
    # W r i t e R e q u e s t
    #-------------------------------------------------------------------------------
    # Input:    characteristic for which the value must be updated
    #
    # Function  Process the request
    #
    # Output:   characteristic values modified according request
    #           HasControl, Started
    #-------------------------------------------------------------------------------
    def WriteRequest(self,
            characteristic: BlessGATTCharacteristic,
            pvalue: Any,
            **kwargs
            ):

        value = bytes(pvalue)          # at least for struct.unpack()

        uuid  = str(characteristic._uuid)
        if   uuid == bc.cFitnessMachineFeatureUUID:      char = bc.cFitnessMachineFeatureName
        elif uuid == bc.cIndoorBikeDataUUID:             char = bc.cIndoorBikeDataName
        elif uuid == bc.cFitnessMachineStatusUUID:       char = bc.cFitnessMachineStatusName
        elif uuid == bc.cFitnessMachineControlPointUUID: char = bc.cFitnessMachineControlPointName
        elif uuid == bc.cSupportedPowerRangeUUID:        char = bc.cSupportedPowerRangeName
        elif uuid == bc.cHeartRateMeasurementUUID:       char = bc.cHeartRateMeasurementUUID
        elif uuid == bc.cSteeringAngleUUID:              char = bc.cSteeringAngleName
        else:                                            char = "?"
        
        #---------------------------------------------------------------------------
        # Logging
        #---------------------------------------------------------------------------
        self.logfileWrite('bleBless: Write request for characteristic "%s", actual value = %s, provided value = %s' %
                (char, HexSpace(characteristic.value), HexSpace(value)))

        #---------------------------------------------------------------------------
        # MachineControlPoint modifies behaviour; the only write we expect
        #---------------------------------------------------------------------------
        if not uuid == bc.cFitnessMachineControlPointUUID:
            self.logfileConsole('bleBless error: Write request on "%s" characteristic is not supported; ignored.' % char)

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
                    self.logfileWrite("bleBless: HasControl = True")
                    self.Message   = ", Bluetooth interface controlled"
                else:
                    ResultCode = bc.fmcp_ControlNotPermitted
                    self.logfileConsole("bleBless error: control requested by client, control already granted")

            elif UseWorkflow and not self.HasControl:
                ResultCode = bc.fmcp_ControlNotPermitted
                self.logfileConsole("bleBless error: request received, but client has no control")

            else:
                if OpCode == bc.fmcp_StartOrResume:
                    self.Started = True
                    self.logfileWrite("bleBless: Started = True")
                    self.notifyStartOrResume()              # Confirm receipt to client
                    self.Message   = ", Bluetooth interface training started"

                elif OpCode == bc.fmcp_SetTargetPower:
                    try:
                        tuple  = struct.unpack (bc.little_endian + bc.unsigned_char + bc.unsigned_short, value)
                    except Exception as e:
                        self.logfileConsole("bleBless error: unpack SetTargetPower %e" % e)
                    #opcode          = tuple[0]
                    self.TargetPower = tuple[1]
                    self.TargetGrade = 0
                    self.TargetMode  = mode_Power
                    self.logfileWrite("bleBless: TargetPower = %s" % self.TargetPower)
                    self.notifySetTargetPower()             # Confirm receipt to client
                    self.Message   = ", Bluetooth interface in power mode"

                elif OpCode == bc.fmcp_SetIndoorBikeSimulation:
                    try:
                        tuple  = struct.unpack (bc.little_endian + bc.unsigned_char + bc.short + bc.short + bc.unsigned_char + bc.unsigned_char, value)
                    except Exception as e:
                        self.logfileConsole("bleBless error: unpack SetIndoorBikeSimulation %s" % e)
                    #opcode                = tuple[0]
                    self.WindSpeed         = round(tuple[1] * 0.001,  3)
                    self.TargetGrade       = round(tuple[2] * 0.01,   2)
                    self.TargetPower       = 0
                    self.TargetMode        = mode_Grade
                    self.RollingResistance = round(tuple[3] * 0.0001, 4)
                    self.WindResistance    = round(tuple[4] * 0.01,   2)
                    self.logfileWrite(
                           "bleBless: windspeed=%s, TargetGrade=%s, RollingResistance=%s, WindResistance=%s" %
                           (self.WindSpeed, self.TargetGrade, self.RollingResistance, self.WindResistance))
                    self.notifySetIndoorBikeSimulation()    # Confirm receipt to client
                    self.Message   = ", Bluetooth interface in grade mode"

                elif OpCode == bc.fmcp_StopOrPause:
                    self.Started = False
                    self.logfileWrite("bleBless: Started = False")
                    self.notifyStopOrPause()                # Confirm receipt to client
                    self.Message   = ", Bluetooth interface training stopped"

                elif OpCode == bc.fmcp_Reset:
                    self.Started    = False
                    self.HasControl = False
                    self.logfileWrite("bleBless: HasControl = False")
                    self.notifyReset()                      # Confirm receipt to client
                    self.Message   = ", Bluetooth interface open"

                else:
                    self.logfileConsole("bleBless error: Unknown OpCode %s" % OpCode)
                    ResultCode = bc.fmcp_ControlNotPermitted

            #-----------------------------------------------------------------------
            # Response:
            #-----------------------------------------------------------------------
            ResponseCode = 0x80
            info = struct.pack(bc.little_endian + bc.unsigned_char * 3, ResponseCode, OpCode, ResultCode)
            characteristic.value = info
            self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineControlPointUUID)

            if False:
                self.logfileWrite("bleBless: New value for characteristic %s = %s" % (char, HexSpace(info)))

    # --------------------------------------------------------------------------
    # After that a characteristic is written, it must also be confirmed through
    # a notification in FitnessMachineStatus
    # --------------------------------------------------------------------------
    def notifyStartOrResume(self):
        self.logfileWrite("bleBless.notifyStartOrResume()")
        info = struct.pack(bc.little_endian + bc.unsigned_char, bc.fms_FitnessMachineStartedOrResumedByUser)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifySetTargetPower(self):
        self.logfileWrite("bleBless.notifySetTargetPower()")
        info = struct.pack(bc.little_endian + bc.unsigned_char + bc.unsigned_short, bc.fms_TargetPowerChanged, self.TargetPower)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifySetIndoorBikeSimulation(self):
        self.logfileWrite("bleBless.notifySetIndoorBikeSimulation()")

        windSpeed = int(self.WindSpeed         / 0.001 )
        grade     = int(self.TargetGrade       / 0.01  )
        crr       = int(self.RollingResistance / 0.0001)
        cw        = int(self.WindResistance    / 0.01  )

        info = struct.pack(bc.little_endian + bc.unsigned_char + bc.short * 2 + bc.unsigned_char * 2,
                            bc.fms_IndoorBikeSimulationParametersChanged, windSpeed, grade, crr, cw)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifyStopOrPause(self):
        self.logfileWrite("bleBless.notifyStopOrPause()")
        info = struct.pack(bc.little_endian + bc.unsigned_char, bc.fms_FitnessMachineStoppedOrPausedByUser)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    def notifyReset(self):
        self.logfileWrite("bleBless.notifyReset()")
        info = struct.pack(bc.little_endian + bc.unsigned_char, bc.fms_Reset)
        self.BlessServer.get_characteristic(bc.cFitnessMachineStatusUUID).value = info
        self.BlessServer.update_value(bc.sFitnessMachineUUID, bc.cFitnessMachineStatusUUID)

    # ------------------------------------------------------------------------------
    # S i m u l a t o r
    # ------------------------------------------------------------------------------
    # Input     None
    #
    # Function  For test-purpose, simulate a trainer with random data.
    #           A real application will have a similar structure:
    #           while True:
    #               time-control
    #               SetAthleteData() and/or SetTrainerData()
    #               Refresh()
    #               use class-attributes (TargetMode, TargetPower, ...)
    #               
    #
    # Output    The interface is used, no further output.
    # ------------------------------------------------------------------------------
    def Simulator(self):
        self.logfileConsole("---------------------------------------------------------------------------------------")
        self.logfileConsole("FortiusAnt simulated trainer is active")
        self.logfileConsole("Start a training in a CTP; 5 seconds after completing the training, simulation will end")
        self.logfileConsole("---------------------------------------------------------------------------------------")

        #---------------------------------------------------------------------------
        # FortiusAntServer is now active
        # read/write through read_Request() and write_Request() functions
        #---------------------------------------------------------------------------
        ClientWasConnected = False
        i = 5
        while i:
            #-----------------------------------------------------------------------
            # Stop 5 seconds after a client is disconnected
            # In the meantime, Start, Power/Grade, Stop is expected....
            #-----------------------------------------------------------------------
            if self.ClientConnected:
                ClientWasConnected = True

            if ClientWasConnected and not self.ClientConnected:
                i -= 1
                pass

            #-----------------------------------------------------------------------
            # Update trainer info every second
            #-----------------------------------------------------------------------
            time.sleep(1)

            #-----------------------------------------------------------------------
            # Create some fancy data
            #-----------------------------------------------------------------------
            s = int(time.time() % 60)           # Seconds
            HeartRate    =   int(000 + s)
            Cadence      =   int(100 + s )
            CurrentSpeed = round(200 + s,1)
            CurrentPower =   int(300 + s)
            SteeringAngle=   s - 30             # -30 ... 30

            #-----------------------------------------------------------------------
            # Update actual values of Athlete and Trainer and Steering
            #-----------------------------------------------------------------------
            self.SetAthleteData  (HeartRate)
            self.SetTrainerData  (CurrentSpeed, Cadence, CurrentPower)
            self.SetSteeringAngle(SteeringAngle)

            #-----------------------------------------------------------------------
            # Allow class to take care that attributes are accurate
            #-----------------------------------------------------------------------
            self.Refresh()

            #-----------------------------------------------------------------------
            # Here the real application can take action, usually adjust the
            # resistance of the bicycle and/or display the target Mode/Power/Grade.
            #-----------------------------------------------------------------------

            #-----------------------------------------------------------------------
            # All we do is show current status / target
            # --> Four variables are filled by ourselves, which in reality comes from
            #     the athlete's HeartRateMonitor and the fitness bike (see above).
            #
            # --> HasControl and Started are status fields from the class
            #
            # --> TargetMode, TargetPower, TargetGrade are provided by the Cycling
            #       Trining Program (CTP), the client to this fitness machine.
            #-----------------------------------------------------------------------
            print(
                "Client=%-5s HasControl=%-5s Started=%-5s TargetPower=%4s TargetGrade=%-6s Speed=%3s Cadence=%3s, Power=%3s, HeartRate=%3s Angle=%5s" %
                (self.ClientConnected, self.HasControl, self.Started, self.TargetPower, self.TargetGrade, self.CurrentSpeed, self.Cadence, self.CurrentPower, self.HeartRate, self.SteeringAngle))

        self.logfileConsole("FortiusAnt simulated trainer is stopped")
        self.logfileConsole("---------------------------------------")

# ==============================================================================
# Main program
# ==============================================================================
if __name__ == "__main__":
    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    if not BlessExample:
        debug.activate(debug.Ble | debug.logging_DEBUG)
        logfile.Open()
        print('FTMS server in FortiusAnt context')
    else:
        logging.basicConfig(level=logging.DEBUG)            # pylint:disable=invalid-name,used-before-assignment,undefined-variable
        logger = logging.getLogger(name=__name__)
        print('FTMS server in bless/example context')

    print("bleBless started")
    print("----------------")

    #---------------------------------------------------------------------------
    # This is what it's all about
    #---------------------------------------------------------------------------
    FortiusAntServer = clsFTMS_bless(True)              # clv.ble
    print("Message=%s" % FortiusAntServer.Message)

    b = FortiusAntServer.Open()
    print("Message=%s" % FortiusAntServer.Message)

    if b:
        FortiusAntServer.Simulator()
        FortiusAntServer.Close()
        print("Message=%s" % FortiusAntServer.Message)

    #---------------------------------------------------------------------------
    # Termination
    #---------------------------------------------------------------------------
    print("bleBless ended")

"""
SAMPLE OUTPUT:
==============

FTMS server in FortiusAnt context
bleBless started
----------------
Message=, Bluetooth interface available (bless)
Message=, Bluetooth interface open
15:17:00,381: ---------------------------------------------------------------------------------------
15:17:00,382: FortiusAnt simulated trainer is active
15:17:00,383: Start a training in a CTP; 5 seconds after completing the training, simulation will end
15:17:00,383: ---------------------------------------------------------------------------------------
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=201 Cadence=101, Power=301, HeartRate=  1 Angle=  -29
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=202 Cadence=102, Power=302, HeartRate=  2 Angle=  -28
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=203 Cadence=103, Power=303, HeartRate=  3 Angle=  -27
...
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=258 Cadence=158, Power=358, HeartRate= 58 Angle=   28
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=259 Cadence=159, Power=359, HeartRate= 59 Angle=   29
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=200 Cadence=100, Power=300, HeartRate=  0 Angle=  -30
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=201 Cadence=101, Power=301, HeartRate=  1 Angle=  -29
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=202 Cadence=102, Power=302, HeartRate=  2 Angle=  -28
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=203 Cadence=103, Power=303, HeartRate=  3 Angle=  -27
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=204 Cadence=104, Power=304, HeartRate=  4 Angle=  -26
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=205 Cadence=105, Power=305, HeartRate=  5 Angle=  -25
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=206 Cadence=106, Power=306, HeartRate=  6 Angle=  -24
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=207 Cadence=107, Power=307, HeartRate=  7 Angle=  -23
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=208 Cadence=108, Power=308, HeartRate=  8 Angle=  -22
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=209 Cadence=109, Power=309, HeartRate=  9 Angle=  -21
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=210 Cadence=110, Power=310, HeartRate= 10 Angle=  -20
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=211 Cadence=111, Power=311, HeartRate= 11 Angle=  -19
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=212 Cadence=112, Power=312, HeartRate= 12 Angle=  -18
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=213 Cadence=113, Power=313, HeartRate= 13 Angle=  -17
Client=True  HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=214 Cadence=114, Power=314, HeartRate= 14 Angle=  -16
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=215 Cadence=115, Power=315, HeartRate= 15 Angle=  -15
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=216 Cadence=116, Power=316, HeartRate= 16 Angle=  -14
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=217 Cadence=117, Power=317, HeartRate= 17 Angle=  -13
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=218 Cadence=118, Power=318, HeartRate= 18 Angle=  -12
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=219 Cadence=119, Power=319, HeartRate= 19 Angle=  -11
Client=False HasControl=False Started=False TargetPower= 100 TargetGrade=0      Speed=220 Cadence=120, Power=320, HeartRate= 20 Angle=  -10
15:18:20,624: FortiusAnt simulated trainer is stopped
15:18:20,627: ---------------------------------------
Message=, Bluetooth interface closed
bleBless ended


Information from LightBlue as BLE-sniffer
==========================================
LightBlue® app launched
App foregrounded
Connecting to 4F:69:66:13:7A:2A (LT-ENTERTAIN)
Connected to 4F:69:66:13:7A:2A (LT-ENTERTAIN)
Discovering services for 4F:69:66:13:7A:2A (LT-ENTERTAIN)
Discovered 6 services for 4F:69:66:13:7A:2A.

Service 00001800-0000-1000-8000-00805f9b34fb
Characteristics:
|--00002a00-0000-1000-8000-00805f9b34fb: Readable
|--00002a01-0000-1000-8000-00805f9b34fb: Readable
|--00002a04-0000-1000-8000-00805f9b34fb: Readable
|--00002aa6-0000-1000-8000-00805f9b34fb: Readable

Service 00001801-0000-1000-8000-00805f9b34fb
Characteristics:
|--00002a05-0000-1000-8000-00805f9b34fb: Indicate
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002b29-0000-1000-8000-00805f9b34fb: Readable, Writable
|--00002b2a-0000-1000-8000-00805f9b34fb: Readable

Service 0000180a-0000-1000-8000-00805f9b34fb
Characteristics:
|--00002a50-0000-1000-8000-00805f9b34fb: Readable

Service 00001826-0000-1000-8000-00805f9b34fb                    == sFitnessMachineUUID
Characteristics:
|--00002acc-0000-1000-8000-00805f9b34fb: Readable
|--00002ad2-0000-1000-8000-00805f9b34fb: Notify
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002ada-0000-1000-8000-00805f9b34fb: Notify
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002ad9-0000-1000-8000-00805f9b34fb: Writable, Indicate
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002ad8-0000-1000-8000-00805f9b34fb: Readable

Service 0000180d-0000-1000-8000-00805f9b34fb                    == sHeartRateUUID
Characteristics:
|--00002a37-0000-1000-8000-00805f9b34fb: Notify
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>

Service 347b0001-7635-408b-8918-8ff3949ce592                    == sSteeringUUID
Characteristics:
|--347b0012-7635-408b-8918-8ff3949ce592: Writable               == cSteeringUnknown1UUID
|--347b0013-7635-408b-8918-8ff3949ce592: Readable               == cSteeringUnknown2UUID
|--347b0014-7635-408b-8918-8ff3949ce592: Notify                 == cSteeringUnknown3UUID
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--347b0019-7635-408b-8918-8ff3949ce592: Readable               == cSteeringUnknown4UUID
|--347b0030-7635-408b-8918-8ff3949ce592: Notify                 == cSteeringAngleUUID
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--347b0032-7635-408b-8918-8ff3949ce592: Indicate               == cSteeringTxUUID
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--347b0031-7635-408b-8918-8ff3949ce592: Writable               == cSteeringRxName

Enabling notifications/indications on 347b0030-7635-408b-8918-8ff3949ce592
Notifications or indications ENABLED on 347b0030-7635-408b-8918-8ff3949ce592
Wrote to descriptor 00002902-0000-1000-8000-00805f9b34fb | value: 01 00
Characteristic 347b0030-7635-408b-8918-8ff3949ce592 changed | value: 00 00 E8 41
Characteristic 347b0030-7635-408b-8918-8ff3949ce592 changed | value: 00 00 F0 C1
Characteristic 347b0030-7635-408b-8918-8ff3949ce592 changed | value: 00 00 E8 C1
...
Disconnecting from 4F:69:66:13:7A:2A (LT-ENTERTAIN)
Disconnected from 4F:69:66:13:7A:2A (LT-ENTERTAIN)

===================================================================================
When the service is published through NodeJs, the services and characteristics are:
===================================================================================

Service 00001800-0000-1000-8000-00805f9b34fb
Characteristics:
|--00002a00-0000-1000-8000-00805f9b34fb: Readable
|--00002a01-0000-1000-8000-00805f9b34fb: Readable

Service 00001801-0000-1000-8000-00805f9b34fb
Characteristics:
|--00002a05-0000-1000-8000-00805f9b34fb: Indicate
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>

Service 00001826-0000-1000-8000-00805f9b34fb                    == sFitnessMachineUUID
Characteristics:
|--00002acc-0000-1000-8000-00805f9b34fb: Readable
|------00002901-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002ad2-0000-1000-8000-00805f9b34fb: Notify
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|------00002901-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002ada-0000-1000-8000-00805f9b34fb: Notify
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|------00002901-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002ad9-0000-1000-8000-00805f9b34fb: Writable, Indicate
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|------00002901-0000-1000-8000-00805f9b34fb: <EMPTY>
|--00002ad8-0000-1000-8000-00805f9b34fb: Readable
|------00002901-0000-1000-8000-00805f9b34fb: <EMPTY>

Service 0000180d-0000-1000-8000-00805f9b34fb                    == sHeartRateUUID
Characteristics:
|--00002a37-0000-1000-8000-00805f9b34fb: Notify
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|------00002901-0000-1000-8000-00805f9b34fb: <EMPTY>

Service 347b0001-7635-408b-8918-8ff3949ce592                    == sSteeringUUID
Characteristics:
|--347b0012-7635-408b-8918-8ff3949ce592: Writable               == cSteeringUnknown1UUID
|--347b0013-7635-408b-8918-8ff3949ce592: Readable               == cSteeringUnknown2UUID
|--347b0014-7635-408b-8918-8ff3949ce592: Notify                 == cSteeringUnknown3UUID
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--347b0019-7635-408b-8918-8ff3949ce592: Readable               == cSteeringUnknown4UUID
|--347b0030-7635-408b-8918-8ff3949ce592: Notify                 == cSteeringAngleUUID
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>
|--347b0031-7635-408b-8918-8ff3949ce592: Writable               == cSteeringRxName
|--347b0032-7635-408b-8918-8ff3949ce592: Indicate               == cSteeringTxUUID
|------00002902-0000-1000-8000-00805f9b34fb: <EMPTY>

"""