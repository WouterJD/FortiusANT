#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2022-08-10"
# 2022-08-10    Steering merged from marcoveeneman and switchable's code
# 2021-11-14    Initial version, switchable
#-------------------------------------------------------------------------------

from abc import ABC
import antDongle as ant
import debug
import logfile
import statistics
import time


#-------------------------------------------------------------------------------
# clsSteering
#-------------------------------------------------------------------------------
# Steering interface
#
# Applies dynamic calibration to raw steering data
#-------------------------------------------------------------------------------
class clsSteering:
    _CalLength = 5

    _MinAngle = -45.0
    _MaxAngle = 45.0

    def __init__(self, InitialCalLeft, InitialCalRight, CalStabilityLimit=15, DeadZone=0.0):
        self._InitialCalLeft    = InitialCalLeft
        self._InitialCalRight   = InitialCalRight
        self._CalStabilityLimit = CalStabilityLimit
        self._DeadZone          = DeadZone

        self._RawAngle          = None      # The value as provided by the device
        self._CalWindow         = FilterWindow(self._CalLength)

        self.CalMid             = None      # The filtered value for the   mid-position
        self.CalLeft            = None      # The filtered value for the  left-position = 45 degrees
        self.CalRight           = None      # The filtered value for the right-position = 45 degrees

    #---------------------------------------------------------------------------
    # Angle
    #---------------------------------------------------------------------------
    # returns   Calibrated angle in degrees (-45.0 - 45.0)
    #           When angle is < deadzone, then zero is returned
    #---------------------------------------------------------------------------
    @property
    def Angle(self):
        # default to 0.0 if no raw data available
        if self.RawAngle is None:
            return 0.0

        # default to 0 degrees while calibration is not ready
        if self.CalMid is None or self.CalLeft is None or self.CalRight is None:
            return 0.0

        # apply piece-wise linear calibration
        if self.RawAngle < self.CalMid:
            angle = (self.RawAngle - self.CalMid) / (self.CalMid - self.CalLeft) * 45.0
        else:
            angle = (self.RawAngle - self.CalMid) / (self.CalRight - self.CalMid) * 45.0

        # clamp to valid range
        angle = max(self._MinAngle, min(angle, self._MaxAngle))

        if abs(angle) < self._DeadZone:
            angle = 0.0

        if debug.on(debug.Function):
            logfile.Write("Steering: Angle=%f" % angle)

        return angle

    #---------------------------------------------------------------------------
    # RawAngle
    #---------------------------------------------------------------------------
    # returns   Uncalibrated angle (arbitrary units, device dependent)
    #---------------------------------------------------------------------------
    @property
    def RawAngle(self):
        return self._RawAngle

    #---------------------------------------------------------------------------
    # Update
    #---------------------------------------------------------------------------
    # function  Update the angle, calibration state from raw steering data
    #
    # inputs    Raw angle (int) or None
    #           higher values -> steer right
    #---------------------------------------------------------------------------
    def Update(self, RawAngle):
        if self._RawAngle == None:
            logfile.Console("Steering is calibrating...")

        self._RawAngle = RawAngle

        if RawAngle is None:
            logfile.Console("clsSteering.Update(); None value is ignored.")
            return

        # Enough data available for calibration?
        self._CalWindow.update(RawAngle)
        if not self._CalWindow.ready:
            # Calibrating
            return

        # Remove spikes that could mess up calibration (with median filter)
        filtered = self._CalWindow.median

        # Calibration value stable?
        if self._CalWindow.stdev > self._CalStabilityLimit:
            # Calibrating
            return

        # Use first (valid) angle for center calibration
        if self.CalMid is None:
            self.CalMid   = filtered
            self.CalLeft  = self.CalMid + self._InitialCalLeft
            self.CalRight = self.CalMid + self._InitialCalRight
            logfile.Console("Zeroed steering angle. Steer full left and right once to calibrate limits.")

        # The highest/lowest raw values seen become the new calibration values
        if filtered < self.CalLeft:
            logfile.Console("Left steering limit updated.")
            self.CalLeft = filtered
        elif filtered > self.CalRight:
            logfile.Console("Right steering limit updated.")
            self.CalRight = filtered

        if debug.on(debug.Function):
            logfile.Write("Steering: CalLeft=%d, CalMid=%d, CalRight=%d" % (self.CalLeft, self.CalMid, self.CalRight))

#-------------------------------------------------------------------------------
# FilterWindow
#-------------------------------------------------------------------------------
# Moving median filter
#-------------------------------------------------------------------------------
class FilterWindow:
    def __init__(self, length):
        self._window_len = length
        self._data = []

    def update(self, value):
        self._data.append(value)
        self._data = self._data[-self._window_len:]

    @property
    def ready(self):
        return len(self._data) == self._window_len

    @property
    def median(self):
        return statistics.median(self._data)

    @property
    def stdev(self):
        return statistics.pstdev(self._data)


#-------------------------------------------------------------------------------
# clsBlackTrack
#-------------------------------------------------------------------------------
# Tacx BlackTrack steering device (ANT)
#-------------------------------------------------------------------------------
class clsBlackTrack:
    def __init__(self, AntDevice):
        super().__init__()

        self.Steering = clsSteering(InitialCalLeft=-300, InitialCalRight=300, DeadZone=2.0)

        self._AntDevice = AntDevice
        self._Channel = ant.channel_BLTR_s
        self._DeviceNumber = None

        # time of last keep-alive message
        self._KeepAliveTime = time.time()

    #---------------------------------------------------------------------------
    # HandleAntMessage
    #---------------------------------------------------------------------------
    # function  Process an ANT message (if related to the BlackTrack)
    #
    # inputs    ANT message bytes
    #
    # returns   True if message was handled
    #           False if it should still be handled elsewhere
    #---------------------------------------------------------------------------
    def HandleAntMessage(self, Message):
        _sync, _length, msgId, info, _checksum, _rest, \
            channel, dataPageNumber = ant.DecomposeMessage(Message)
        dataHandled = False
        messages = []

        if channel == self._Channel:

            #-------------------------------------------------------------------
            # BroadcastData - info received from the master device
            #-------------------------------------------------------------------
            if msgId == ant.msgID_BroadcastData:

                #---------------------------------------------------------------
                # Ask what device is connected
                #---------------------------------------------------------------
                if self._DeviceNumber is None:
                    msg = ant.msg4D_RequestMessage(self._Channel, ant.msgID_ChannelID)
                    messages.append(msg)

                #---------------------------------------------------------------
                # Keep BlackTrack from turning off (send page 0x01)
                #---------------------------------------------------------------
                keepAliveInterval = 10  # in s
                timeElapsed = time.time() - self._KeepAliveTime

                if timeElapsed > keepAliveInterval:
                    keep_alive = ant.msgPage01_TacxBlackTrackKeepAlive (self._Channel)
                    msg  = ant.ComposeMessage (ant.msgID_BroadcastData, keep_alive)
                    messages.append ( msg )

                    if debug.on(debug.Function):
                        logfile.Write("Tacx BlackTrack Page=1 (OUT)  Keep-alive")

                    # reset keep-alive timer
                    self._KeepAliveTime = time.time()

                # -------------------------------------------------------------------
                # Data page 0x00 BlackTrack Angle
                # -------------------------------------------------------------------
                if dataPageNumber == 0:
                    rawAngle, _reserved = ant.msgUnpage00_TacxBlackTrackAngle(info)

                    if debug.on(debug.Function):
                        logfile.Write('Tacx BlackTrack Page=%d (IN)  RawAngle=%d' %
                            (dataPageNumber, rawAngle))

                    self.Steering.Update(rawAngle)

                    dataHandled = True

            #-------------------------------------------------------------------
            # ChannelID - the info that a master on the network is connected
            #-------------------------------------------------------------------
            elif msgId == ant.msgID_ChannelID:
                _channel, deviceNumber, deviceTypeID, _transmissionType = \
                    ant.unmsg51_ChannelID(info)

                if deviceTypeID == ant.DeviceTypeID_BLTR:
                    self._DeviceNumber = deviceNumber
                    logfile.Console("Tacx BlackTrack connected (%d)" % deviceNumber)

                dataHandled = True

        # -------------------------------------------------------------------
        # Send ANT messages (if any)
        # -------------------------------------------------------------------
        if messages:
            self._AntDevice.Write(messages, False, False)

        return dataHandled
