#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
WindowTitle = "Fortius Antifier v3.1.1"
__version__ = "2020-05-24"
# 2020-05-24    Initial GUI messages made more general
#               TargetResistance not displayed when zero (for i-Vortex)
# 2020-05-15    Window title adjusted to version 3.0, comment on teeth.
# 2020-05-11    Small corrections
# 2020-04-30    Pedal stroke analysis added
#               form class requires clv to be provided when created
#               Occasional crash in OnClose() resolved
# 2020-04-29    Speedmeter optimizations removed (no need due to child-process)
#               StaticValues class removed, fields moved to frmFortiusAntGui.
# 2020-04-27    OnTimer() event restarts too early, OnTimerEnabled flag added.
# 2020-04-20    txtAntHRM added, message size reduced
# 2020-04-07    Messages enlarged to improve readability
#               Message with PowerFactor is no longer displayed
#                   PowerFactor is an antifier inherited way of calibrating
#                   which is not used anymore, although still suppported.
#                   Since the value is not dynamic, the message is obsolete.
#               Digital Gearbox display as a graphic in number of teeth,
#                   as if enlarging/reducing the cassette of the bicycle.
# 2020-03-29    PowercurveFactor added to console
# 2020-02-09    Suffix to refresh text-fields removed (?(
# 2020-02-07    Text resized; as large as possible. Units abbreviated
#               Heartrate positioned left
# 2020-01-24    ico and jpg can be embedded in pyinstaller executable
# 2020-01-22    In GradeMode, TargetPower is also displayed for reference
# 2020-01-01    SetValues, TargetMode added
# 2019-12-30    Version 2.1
#               SetValues() input: TargetPower/TargetGrade to be inline with
#                   FortiusAnt.py itself.
# 2019-12-24    Heartbeat performance optimized
#               "Target x Watt" or "Target grade x %"
# 2019-12-11    Icon added
# 2019-12-06    Frame not resizable, no maximize button
# 2019-12-05    Buttons are enabled and SetFocus in the button event.
#               If done in the thread(), the SetFocus seems not working.
#
#               Also, text fields are flickering, therefore updated every second
#-------------------------------------------------------------------------------
import array
import math
import numpy
import os
import random
import sys
import threading
import time
import wx
import wx.lib.agw.speedmeter as SM

import debug
import logfile
import FortiusAntCommand as cmd
import RadarGraph

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
LargeTexts          = True  # 2020-02-07

mode_Basic          = 0     # Basic Resistance
mode_Power          = 1     # Target Power
mode_Grade          = 2     # Target Resistance

bg                  = wx.Colour(220,220,220) # Background colour [for self.Speedometers]
colorTacxFortius    = wx.Colour(120,148,227)
Margin              = 4

# ------------------------------------------------------------------------------
# Create the FortiusAnt frame
# ------------------------------------------------------------------------------
# Execute:      If this file is executed as main, the user-interface can be
#                   tested without the program functionality
#               If this file is included, the following functions must be defined:
#
# Functions:    Autostart
#               SetValues, ResetValues
#               SetMessages
#
# Three functions to be provided:
#               callIdleFunction(self)
#               callLocateHW(self)          returns True/False
#               callRunoff(self)
#               callTacx2Dongle(self)
# ------------------------------------------------------------------------------
class frmFortiusAntGui(wx.Frame):
    clv        = None
    LastFields = 0  # Time when SetValues() updated the fields
    LastHeart  = 0  # Time when heartbeat image was updated
    IdleDone   = 0  # Counter to warn that callIdleFunction is not redefined
    power      = [] # Array with power-tuples

    def __init__(self, parent, pclv):
        wx.Frame.__init__(self, parent, -1, WindowTitle, \
               style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.clv = pclv     # clv = Command Line Variables
        # ----------------------------------------------------------------------
		# Images are either in directory of the .py or embedded in .exe
        # ----------------------------------------------------------------------
        if getattr(sys, 'frozen', False):
            dirname = sys._MEIPASS
        else:
            dirname = os.path.dirname(__file__)

        FortiusAnt_ico = os.path.join(dirname, "FortiusAnt.ico")
        FortiusAnt_jpg = os.path.join(dirname, "FortiusAnt.jpg")
        Heart_jpg      = os.path.join(dirname, "Heart.jpg"     )

        try:
            ico = wx.Icon(FortiusAnt_ico, wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            print('Cannot load '+ FortiusAnt_ico)
            pass

        # ----------------------------------------------------------------------
		# Default initial actions, bind functions to frame
        # ----------------------------------------------------------------------
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_PAINT, self.OnPaint)              # Draw the bitmap
        self.Iconize(False)                                # un-iconize
#       print(self.GetPosition())
#       self.Center()                                      # It does not center the frame on the screen...
#       print(self.GetPosition())

        if True:
            TIMER_ID = 250
            self.timer = wx.Timer(self, TIMER_ID)
            self.Bind(wx.EVT_TIMER, self.OnTimer)
            self.timer.Start(250)
            self.OnTimerEnabled = True

        # ----------------------------------------------------------------------
		# Thread handling
        # ----------------------------------------------------------------------
        self.RunningSwitch = False
        self.CloseButtonPressed = False

        # ----------------------------------------------------------------------
		# Load Background image
        # ----------------------------------------------------------------------
        self.BackgroundBitmap = False
        BitmapW = 900
        BitmapH = 600
        try:
            self.BackgroundBitmap = wx.Bitmap(FortiusAnt_jpg)       # Image on the window background
            BitmapW = self.BackgroundBitmap.Size.GetWidth()
            BitmapH = self.BackgroundBitmap.Size.GetHeight()
        except:
            print('Cannot load '+ FortiusAnt_jpg)
        # ----------------------------------------------------------------------
		# Load HeartRate image
        # ----------------------------------------------------------------------
        self.HeartRate      = 123
        self.HeartRateWH    = 40
                            # 2020-04-07    # 2020-02-07    # 2020-01-25
        self.HeartRateX     = Margin        # 25            # BitmapW - 25 - self.HeartRateWH
        self.HeartRateY     = BitmapH - 50 - self.HeartRateWH
        self.HeartRateImage = False
        try:
            self.HeartRateImage = wx.Image(Heart_jpg)  # HeartRate

            img           = self.HeartRateImage.Scale(36, 36, wx.IMAGE_QUALITY_HIGH)
            self.bmp36x36 = wx.Bitmap(img)

            img           = self.HeartRateImage.Scale(40, 40, wx.IMAGE_QUALITY_HIGH)
            self.bmp40x40 = wx.Bitmap(img)

        except:
            # print('Cannot load ' + Heart_jpg)
            pass
        # ----------------------------------------------------------------------
		# Calculate location of Gearbox image
        # Positioned above HeartRate_img, equally wide/heigh
        # ----------------------------------------------------------------------
        self.GearboxTeeth  = 0
        self.GearboxWH     = self.HeartRateWH
        self.GearboxX      = self.HeartRateX
        self.GearboxY      = self.HeartRateY - self.HeartRateWH - Margin
        
        # ----------------------------------------------------------------------
        # Idea to generate the bitmap, but the "gearbox" can as easily be drawn
        # Code left for reference, even though not correct/complete yet.
        # ----------------------------------------------------------------------
        if False:
            print(1)
            print(self.GearboxImage)
            print('width=%s height=%s' % (self.GearboxImage.GetWidth(), self.GearboxImage.GetHeight()))
            print(2)
            print(self.GearboxBitmap)
            print('width=%s height=%s' % (self.GearboxBitmap.GetWidth(), self.GearboxBitmap.GetHeight()))
            print(3)


            self.GearboxBitmap  = wx.Bitmap(self.GearboxImage)

            bitDepth = self.GearboxBitmap.GetDepth()
            if bitDepth == 24:
                bpp = 3  # bytes per pixel
                buffer_length = self.GearboxBitmap.GetWidth() * self.GearboxBitmap.GetHeight() * bpp
                buffer = array.array('B', [0] * buffer_length )
                self.GearboxBitmap.CopyToBuffer(buffer, wx.BitmapBufferFormat_RGB)
                
                print ('  :0         1         2         3         ')
                print ('  : 123456789 123456789 123456789 123456789')
                for y in range(0, self.GearboxBitmap.GetHeight()):
                    print('%2.0f:' % y, end='')
                    for x in range(0, self.GearboxBitmap.GetWidth()):
                        index = (y * self.GearboxBitmap.GetWidth() + x ) * bpp
                        r = buffer[index]
                        g = buffer[index + 1]
                        b = buffer[index + 2]
                        if r==255 and g==255 and b==255: print ('.', end='')
                        else:                            print ('x', end='')
                        # if r==255 and g==255 and b==255: print ('......... ', end='')
                        # else:                            print ('%3.0f%3.0f%3.0f ' % (r,g,b), end='')
                    print('')
            print(4)
             
            print(5)
            
        # ----------------------------------------------------------------------
		# Calculate Width and X
        # ----------------------------------------------------------------------
        #
        # x [button] x [speed] x [revs] x [power] x
        #
        ButtonX = Margin
        ButtonW = 80

        SpeedWH     = int((BitmapW - ButtonW - 5 * Margin) / 3) # width/height equal (square)
        RevsWH      = SpeedWH
        PowerWH     = SpeedWH

        SpeedX      = ButtonX + ButtonW + Margin
        RevsX       = SpeedX  + SpeedWH + Margin
        PowerX      = RevsX   + RevsWH  + Margin

        SpeedY      = Margin
        RevsY       = Margin
        PowerY      = Margin

        BitmapX     = 0
        BitmapY     = 0

        self.SetSize (BitmapX + BitmapW + 15, BitmapY + BitmapH)

        # ----------------------------------------------------------------------
		# Speedometer values and colours
        # ----------------------------------------------------------------------
        MiddleTextFontSize  = 10
        TicksFontSize       = 10

        # ----------------------------------------------------------------------
		# self.Speedometer
        # ----------------------------------------------------------------------
        if True:
            self.Speed = SM.SpeedMeter(self, agwStyle=SM.SM_DRAW_HAND|SM.SM_DRAW_GRADIENT|SM.SM_DRAW_MIDDLE_TEXT|SM.SM_DRAW_SECONDARY_TICKS)
            self.Speed.SetSize (SpeedX, SpeedY, SpeedWH, SpeedWH)

            self.Speed.SetSpeedBackground(bg)
            self.Speed.SetFirstGradientColour(colorTacxFortius)             # Colours for SM_DRAW_GRADIENT
            self.Speed.SetSecondGradientColour(wx.WHITE)
            self.Speed.DrawExternalArc(True)                                # Do (Not) Draw The External (Container) Arc.
            self.Speed.SetArcColour(wx.BLACK)

            self.Speed.SetAngleRange(-math.pi / 6, 7 * math.pi / 6)         # Set The Region Of Existence Of self.SpeedMeter (Always In Radians!!!!)
            self.Speed.SetHandColour(wx.Colour(255, 50, 0))                	# Set The Colour For The Hand Indicator

            self.Speed.SetMiddleText("Speed")                               # Set The Text In The Center Of self.SpeedMeter
            self.Speed.SetMiddleTextColour(wx.BLUE)                         # Assign The Colour To The Center Text
            self.Speed.SetMiddleTextFont(wx.Font(MiddleTextFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                                                                            # Assign A Font To The Center Text

            Min = 0
            NrIntervals = 10
            Step  = 5
            Max   = Min + Step * NrIntervals
            self.SpeedMax = Max

            intervals = range(Min, Max+1, Step)                             # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
            self.Speed.SetIntervals(intervals)

#           colours = [wx.BLUE] * NrIntervals                               # Assign The Same Colours To All Sectors (We Simulate A Car Control For self.Speed)
#           self.Speed.SetIntervalColours(colours)

            ticks = [str(interval) for interval in intervals]               # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
            self.Speed.SetTicks(ticks)
            self.Speed.SetTicksColour(wx.WHITE)                             # Set The Ticks/Tick Markers Colour
            self.Speed.SetNumberOfSecondaryTicks(5)                         # We Want To Draw 5 Secondary Ticks Between The Principal Ticks

            self.Speed.SetTicksFont(wx.Font(TicksFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                                                                            # Set The Font For The Ticks Markers

        # ----------------------------------------------------------------------
		# self.Revs
        # ----------------------------------------------------------------------
        if True:
            # SM_ROTATE_TEXT            Draws the ticks rotated: the ticks are rotated accordingly to the tick marks positions.
            # SM_DRAW_SECTORS           Different intervals are painted in differend colours (every sector of the circle has its own colour).
            # SM_DRAW_PARTIAL_SECTORS   Every interval has its own colour, but only a circle corona is painted near the ticks.
            # SM_DRAW_HAND              The hand (arrow indicator) is drawn.
            # SM_DRAW_SHADOW            A shadow for the hand is drawn.
            # SM_DRAW_PARTIAL_FILLER    A circle corona that follows the hand position is drawn near the ticks.
            # SM_DRAW_SECONDARY_TICKS   Intermediate (smaller) ticks are drawn between principal ticks.
            # SM_DRAW_MIDDLE_TEXT       Some text is printed in the middle of the control near the center.
            # SM_DRAW_MIDDLE_ICON       An icon is drawn in the middle of the control near the center.
            # SM_DRAW_GRADIENT          A gradient of colours will fill the control.
            # SM_DRAW_FANCY_TICKS       With this style you can use xml tags to create some custom text and draw it at the ticks position. See lib.fancytext for the tags.
            self.Revs = SM.SpeedMeter(self, agwStyle=SM.SM_DRAW_GRADIENT | SM.SM_DRAW_PARTIAL_SECTORS | SM.SM_DRAW_HAND | SM.SM_DRAW_SECONDARY_TICKS | SM.SM_DRAW_MIDDLE_TEXT)
            self.Revs.SetSize (RevsX, RevsY, RevsWH, RevsWH) # x,y and width, height

            self.Revs.SetSpeedBackground(bg)
            self.Revs.SetFirstGradientColour(wx.BLUE)                       # Colours for SM_DRAW_GRADIENT
            self.Revs.SetSecondGradientColour(wx.WHITE)
            self.Revs.DrawExternalArc(True)                                 # Do (Not) Draw The External (Container) Arc.
            self.Revs.SetArcColour(wx.BLUE)

            self.Revs.SetAngleRange(-math.pi / 6, 7 * math.pi / 6)          # Set The Region Of Existence Of self.RevsMeter (Always In Radians!!!!)
            self.Revs.SetHandColour(wx.Colour(255, 50, 0))                	# Set The Colour For The Hand Indicator

            self.Revs.SetMiddleText("Cadence")                              # Set The Text In The Center Of self.RevsMeter
            self.Revs.SetMiddleTextColour(wx.BLUE)                          # Assign The Colour To The Center Text
            self.Revs.SetMiddleTextFont(wx.Font(MiddleTextFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                                                                            # Assign A Font To The Center Text

            Min = 0
            NrIntervals = 12
            Step  = 10                                                      # For me, 120/min is enough
            Max   = Min + Step * NrIntervals
            self.RevsMax = Max

            intervals = range(Min, Max+1, Step)                             # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
            self.Revs.SetIntervals(intervals)

            colours = [wx.BLACK]                                            # Assign colours, per range
            i = 2
            while i <= NrIntervals:
                if i * Step <= 40:                                          # <= 40 is special case for resistance calculation
                    colours.append(wx.BLACK)
                elif i * Step <= 60:
                    colours.append(wx.BLUE)
                elif i * Step <= 90:
                    colours.append(wx.GREEN)
                elif i * Step <= 110:
                    colours.append(wx.Colour(244,144,44))                   # Orange
                else:
                    colours.append(wx.RED)
                i += 1
            self.Revs.SetIntervalColours(colours)

            ticks = [str(interval) for interval in intervals]               # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
            self.Revs.SetTicks(ticks)
            self.Revs.SetTicksColour(wx.WHITE)                        		# Set The Ticks/Tick Markers Colour
            self.Revs.SetNumberOfSecondaryTicks(5)                        	# We Want To Draw 5 Secondary Ticks Between The Principal Ticks

            self.Revs.SetTicksFont(wx.Font(TicksFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                                                                            # Set The Font For The Ticks Markers

        # ----------------------------------------------------------------------
		# self.Power
        # ----------------------------------------------------------------------
        if True:
            self.Power = SM.SpeedMeter(self, agwStyle=SM.SM_DRAW_HAND|SM.SM_DRAW_GRADIENT|SM.SM_DRAW_MIDDLE_TEXT|SM.SM_DRAW_SECONDARY_TICKS)
            self.Power.SetSize (PowerX, PowerY, PowerWH, PowerWH) # x,y and width, height

            self.Power.SetSpeedBackground(bg)
            self.Power.SetFirstGradientColour(colorTacxFortius)             # Colours for SM_DRAW_GRADIENT
            self.Power.SetSecondGradientColour(wx.WHITE)
            self.Power.DrawExternalArc(True)                                # Do (Not) Draw The External (Container) Arc.
            self.Power.SetArcColour(wx.BLACK)

            self.Power.SetAngleRange(-math.pi / 6, 7 * math.pi / 6)         # Set The Region Of Existence Of self.PowerMeter (Always In Radians!!!!)
            self.Power.SetHandColour(wx.Colour(255, 50, 0))                	# Set The Colour For The Hand Indicator

            self.Power.SetMiddleText("Power")                               # Set The Text In The Center Of self.PowerMeter
            self.Power.SetMiddleTextColour(wx.BLUE)                         # Assign The Colour To The Center Text
            self.Power.SetMiddleTextFont(wx.Font(MiddleTextFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                                                                            # Assign A Font To The Center Text

            Min = 0
            NrIntervals = 10
            Step  = 40
            Max   = Min + Step * NrIntervals
            self.PowerMax = Max
            self.PowerArray = numpy.array([0,0,0,0,0,0,0,0,0,0])            # Array for running everage

            intervals = range(Min, Max+1, Step)                             # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
            self.Power.SetIntervals(intervals)

#           colours = [wx.BLACK] * NrIntervals                              # Assign The Same Colours To All Sectors (We Simulate A Car Control For self.Speed)
#           self.Power.SetIntervalColours(colours)

            ticks = [str(interval) for interval in intervals]               # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
            self.Power.SetTicks(ticks)
            self.Power.SetTicksColour(wx.WHITE)                        		# Set The Ticks/Tick Markers Colour
            self.Power.SetNumberOfSecondaryTicks(5)                        	# We Want To Draw 5 Secondary Ticks Between The Principal Ticks

            self.Power.SetTicksFont(wx.Font(TicksFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                                                                            # Set The Font For The Ticks Markers

        # ----------------------------------------------------------------------
		# Font sizing for all measurements
        # ----------------------------------------------------------------------
        TextCtrlFont = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        TextCtrlH    = 40
        TextCtrlW    = int(SpeedWH/2)

        TextCtrlFont2= wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        TextCtrlH2   = 25
        _TextCtrlW2  = int(SpeedWH/2)

        # ----------------------------------------------------------------------
		# self.Speed label & text
        # ----------------------------------------------------------------------
        self.txtSpeed = wx.TextCtrl(self, value="99.9 km/h", size=(int(TextCtrlW * 1.2),TextCtrlH), style=wx.TE_CENTER | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtSpeed.SetBackgroundColour(bg)
        self.txtSpeed.SetPosition((int(self.Speed.Position[0] + (self.Speed.Size[0] - self.txtSpeed.Size[0])/2), \
                                    self.Speed.Position[1] + self.Speed.Size[1] - 2 * self.txtSpeed.Size[1]))

        # ----------------------------------------------------------------------
		# self.Revs
        # ----------------------------------------------------------------------
        self.txtRevs = wx.TextCtrl(self, value="999/min", size=(int(TextCtrlW * 1.2),TextCtrlH), style=wx.TE_CENTER | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtRevs.SetBackgroundColour(bg)
        self.txtRevs.SetPosition((int(self.Revs.Position[0] + (self.Revs.Size[0] - self.txtRevs.Size[0])/2), \
                                    self.Revs.Position[1] + self.Revs.Size[1] - 2 * self.txtRevs.Size[1]))

        # ----------------------------------------------------------------------
		# self.Power
        # ----------------------------------------------------------------------
        self.txtPower = wx.TextCtrl(self, value="999 Watt", size=(TextCtrlW,TextCtrlH), style=wx.TE_CENTER | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtPower.SetBackgroundColour(bg)
        self.txtPower.SetPosition((int(self.Power.Position[0] + (self.Power.Size[0] - self.txtPower.Size[0])/2), \
                                    self.Power.Position[1] + self.Power.Size[1] - 2 * self.txtPower.Size[1]))

        self.txtTarget = wx.TextCtrl(self, value="Target=999 Watt", size=(int(TextCtrlW *1.3),TextCtrlH), style=wx.TE_LEFT | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtTarget.SetBackgroundColour(bg)
        self.txtTarget.SetPosition((self.Power.Position[0], \
                                    self.Power.Position[1] + self.Power.Size[1] - self.txtTarget.Size[1]))

        self.txtTacx = wx.TextCtrl(self, value="Tacx=9999", size=(int(TextCtrlW * 0.7),TextCtrlH), style=wx.TE_RIGHT | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtTacx.SetBackgroundColour(bg)
        self.txtTacx.SetPosition((self.Power.Position[0] + self.Power.Size[0] - self.txtTacx.Size[0], \
                                    self.Power.Position[1] + self.Power.Size[1] - self.txtTacx.Size[1]))

        # ----------------------------------------------------------------------
		# USB Trainer
        # - Is positioned UNDER the Speed control
        # - Has width of Speed + Cadence control
        # ----------------------------------------------------------------------
        self.txtUsbTrainer = wx.TextCtrl(self, value="txtUsbTrainer", size=(10,TextCtrlH2), style=wx.TE_LEFT | wx.TE_READONLY)
        self.txtUsbTrainer.SetSize((self.Revs.Position[0] + self.Revs.Size[0] - Margin, -1))
        self.txtUsbTrainer.SetPosition((Margin, self.Speed.Position[1] + self.Speed.Size[1] + 5))
        self.txtUsbTrainer.SetBackgroundColour(bg)

        # ----------------------------------------------------------------------
		# ANT Dongle
        # ----------------------------------------------------------------------
        self.txtAntDongle = wx.TextCtrl(self, value="txtAntDongle", size=(10,TextCtrlH2), style=wx.TE_LEFT | wx.TE_READONLY)
        self.txtAntDongle.SetSize((self.txtUsbTrainer.Size[0], -1))
        self.txtAntDongle.SetPosition((Margin, self.txtUsbTrainer.Position[1] + self.txtUsbTrainer.Size[1] + 5))
        self.txtAntDongle.SetBackgroundColour(bg)

        # ----------------------------------------------------------------------
		# ANT Heart Rate Monitor
        # ----------------------------------------------------------------------
        self.txtAntHRM = wx.TextCtrl(self, value="txtAntHRM", size=(10,TextCtrlH2), style=wx.TE_LEFT | wx.TE_READONLY)
        self.txtAntHRM.SetSize((self.txtUsbTrainer.Size[0], -1))
        self.txtAntHRM.SetPosition((Margin, self.txtAntDongle.Position[1] + self.txtAntDongle.Size[1] + 5))
        self.txtAntHRM.SetBackgroundColour(bg)

        # ----------------------------------------------------------------------
		# self.HeartRate, shown to the right of the Heartrate image
        # ----------------------------------------------------------------------
        self.txtHeartRate = wx.TextCtrl(self, value="123", size=(int(self.HeartRateWH*2),TextCtrlH), style=wx.TE_CENTER | wx.TE_READONLY)
        self.txtHeartRate.SetBackgroundColour(bg)
        self.txtHeartRate.SetPosition(( self.HeartRateX + self.HeartRateWH + Margin, self.HeartRateY))

        # ----------------------------------------------------------------------
		# self.Gearbox, shown to the right of the Gearbox image
        # ----------------------------------------------------------------------
        self.txtGearbox = wx.TextCtrl(self, value="123", size=(int(self.GearboxWH*2),TextCtrlH), style=wx.TE_CENTER | wx.TE_READONLY)
        self.txtGearbox.SetBackgroundColour(bg)
        self.txtGearbox.SetPosition(( self.GearboxX + self.GearboxWH + Margin, self.GearboxY))

        # ----------------------------------------------------------------------
        # Add a radar graph for pedal stroke analysis
        # - To the right of the gearbox text
        # - Under txtAntHRM
        # - Vertically aligning with txtGearbox
        # ----------------------------------------------------------------------
        if self.clv.PedalStrokeAnalysis:
            x  = self.txtHeartRate.Position [0] + self.txtHeartRate.Size [0] + Margin
            y  = self.txtAntHRM.Position    [1] + self.txtAntHRM.Size    [1] + 5
            wh = self.txtHeartRate.Position [1] + self.txtHeartRate.Size [1] - y
            self.RadarGraph = RadarGraph.clsRadarGraph(self, "Pedal stroke analysis", x, y, wh)
        
        # ----------------------------------------------------------------------
		# Font setting for all measurements
        # ----------------------------------------------------------------------
        self.txtSpeed.SetFont(TextCtrlFont)
        self.txtRevs.SetFont(TextCtrlFont)
        self.txtPower.SetFont(TextCtrlFont)
        self.txtTarget.SetFont(TextCtrlFont)
        self.txtTacx.SetFont(TextCtrlFont)
        self.txtHeartRate.SetFont(TextCtrlFont)
        self.txtGearbox.SetFont(TextCtrlFont)
        
        self.txtUsbTrainer.SetFont(TextCtrlFont2)
        self.txtAntDongle.SetFont(TextCtrlFont2)
        self.txtAntHRM.SetFont(TextCtrlFont2)

        # ----------------------------------------------------------------------
		# Buttons
        # ----------------------------------------------------------------------
        self.btnLocateHW = wx.Button(self, label="Locate HW", size=(ButtonW, -1))
        self.btnLocateHW.SetPosition((ButtonX, self.btnLocateHW.Size[1]))
        self.btnLocateHW.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnLocateHW, self.btnLocateHW)

        self.btnRunoff   = wx.Button(self, label="Runoff", size=(ButtonW, -1))
        self.btnRunoff.SetPosition((ButtonX, self.btnLocateHW.Position[1] + self.btnLocateHW.Size[1]))
        self.btnRunoff.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnRunoff, self.btnRunoff)

        self.btnStart    = wx.Button(self, label="Start", size=(ButtonW, -1))
        self.btnStart.SetPosition((ButtonX, self.btnRunoff.Position[1] + self.btnRunoff.Size[1]))
        self.btnStart.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnStart, self.btnStart)

        self.btnStop     = wx.Button(self, label="Stop", size=(ButtonW, -1))
        self.btnStop.SetPosition((ButtonX, self.btnStart.Position[1] + self.btnStart.Size[1]))
        self.btnStop.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnStop, self.btnStop)

        # ----------------------------------------------------------------------
		# Set initial values
        # ----------------------------------------------------------------------
        self.ResetValues()
        self.SetMessages(Tacx  ="Tacx Trainer")
        self.SetMessages(Dongle="ANT+ Dongle")
        self.SetMessages(HRM   ="ANT+ Heart Rate Monitor")

    # --------------------------------------------------------------------------
    # F u n c t i o n s  --  to be provided by subclass.
    #
    # The structure is as follows:
    # - The user interface calls "callXYZ" which is to be provided
    # - The form class defines the functions and calls the function
    # - The function being called is independant of the user interface
    #
    # The code below provides functionality so that the GUI works and can be tested
    # --------------------------------------------------------------------------
    def callIdleFunction(self):
        if self.IdleDone < 10:
            print("callIdleFunction not defined by application class")
            self.IdleDone += 1
        return True

    def callLocateHW(self):
        print("callLocateHW not defined by application class")

        if self.clv.PedalStrokeAnalysis:
            # Fill list and show it 
            for i in range(0,360,int(9)):                           # 9 degrees
                self.power.append((i, random.randint(75, 125)))
            self.RadarGraph.ShowRadarGraph(self.power)

        return True

    def callRunoff(self):
        print("callRunoff not defined by application class")
        f = 1
        while self.RunningSwitch == True:
            t = time.localtime()
            f += 1
            self.SetValues(f/100 * self.SpeedMax, f/100 * self.RevsMax, f/100 * self.PowerMax, t[5], False, t[0] + t[5], 123, 10, random.randint(9,27))
            time.sleep(1/8)                         # sleep 0.125 second (like Tacx2Dongle)
            if f > 100:
                self.RunningSwitch == False

            if self.clv.PedalStrokeAnalysis:
                for i, p in enumerate(self.power):
                    self.power[i] = (p[0], p[1] + random.uniform(-15, 15))
                self.RadarGraph.ShowRadarGraph(self.power)

        self.ResetValues()
        return True

    def callTacx2Dongle(self):
        print("callTacx2Dongle not defined by application class")
#       tr = 255                                    # experimental purpose only
        while self.RunningSwitch == True:
            #t = time.localtime()
            r = (90 + random.randint(1,20)) / 100   # 0.9 ... 1.1
#           r = .5
#           self.SetTransparent(tr)                 # frame can be made transparent
#           self.Speed.SetTransparent(tr)           # control on frame cannot be made transparent
#           tr -= 5
#           self.SetValues(r * self.SpeedMax, r * self.RevsMax, r * self.PowerMax, t[5], t[0] + t[5])
#           self.SetValues(35.6, 234, 123, mode_Grade, 345, 19.5, 2345, 123)
            self.SetValues(r * 35.6, r * 234, r * 123, mode_Grade, r * 345, r * 19.5, r * 2345, r * 123, random.randint(9,27))

            if self.clv.PedalStrokeAnalysis:
                for i, p in enumerate(self.power):
                    self.power[i] = (p[0], p[1] + random.uniform(-15, 15))
                self.RadarGraph.ShowRadarGraph(self.power)

            time.sleep(0.250)                       # sleep 0.250 second (like Tacx2Dongle)
        return True

    # --------------------------------------------------------------------------
    # A u t o s t a r t
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Press two buttons: [LocateHW] and [Start]
    #               Button-press simulate so that buttons are emabled/disabled
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def Autostart(self):
        if self.OnClick_btnLocateHW():
            self.OnClick_btnStart()

    # --------------------------------------------------------------------------
    # N a v i g a t e
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Enter-button on headunit is pressed.
    #               Simulate click on active button
    #
    #               Note: when btnLocateHW is enabled, we do not have a trainer
    #                     yet and therefore no Enter button to find the trainer
    #                     will ever be recieved.
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def Navigate_Enter(self):
        if   self.btnLocateHW.HasFocus(): self.OnClick_btnLocateHW(self)        # Will never occur
        elif   self.btnRunoff.HasFocus(): self.OnClick_btnRunoff(self)
        elif    self.btnStart.HasFocus(): self.OnClick_btnStart(self)
        elif     self.btnStop.HasFocus(): self.OnClick_btnStop(self)
        else:                             pass

    def Navigate_Up(self):
        if   self.btnLocateHW.HasFocus(): pass          # is first button
        elif   self.btnRunoff.HasFocus(): pass          # previous cannot be enabled
        elif    self.btnStart.HasFocus(): self.btnRunoff.SetFocus()
        elif     self.btnStop.HasFocus(): pass          # stop first
        else:                             pass

    def Navigate_Down(self):
        if   self.btnLocateHW.HasFocus(): pass          # must be done first
        elif   self.btnRunoff.HasFocus(): self.btnStart.SetFocus()
        elif    self.btnStart.HasFocus(): pass          # must start first
        elif     self.btnStop.HasFocus(): pass          # is last button
        else:                             pass

    def Navigate_Back(self):
        if self.RunningSwitch == True:
            self.RunningSwitch = False                  # Stop running thread
            self.CloseButtonPressed = False             # Do not stop the program
        else:
            self.Close()                              # Stop program
            pass
    # --------------------------------------------------------------------------
    # S e t V a l u e s
    # --------------------------------------------------------------------------
    # input:        User interface values
    #               fSpeed          Actual speed in km/hr
    #               iRevs           Revolutions in /min
    #               iPower          Actual Power in Watts
    #               iTargetMode     basic, power or grade
    #               iTargetPower    Target Power in Watts
    #               fTargetGrade    Target Grade in %
    #               iTacx           Target resistance for the Tacx
    #               iHeartRate      Heartrate in beats/min
    #               iTeeth          Number of teeth on the cassette of
    #                               the virtual gearbox.
    #
    # Description:  Show the values in SpeedoMeter and text-fields
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def ResetValues(self):
        self.SetValues(0,0,0,0,0,0,0,0,0)
    def SetValues(self, fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, iTacx, iHeartRate, iTeeth):
        # ----------------------------------------------------------------------
        # Average power over the last 10 readings
        # ----------------------------------------------------------------------
        self.PowerArray = numpy.append(self.PowerArray, iPower)     # Add new value to array
        self.PowerArray = numpy.delete(self.PowerArray, 0)          # Remove oldest from array
        iPowerMean = int(numpy.mean(self.PowerArray))               # Calculate average

        # ----------------------------------------------------------------------
        # Values are needed on OnPaint() event
        # ----------------------------------------------------------------------
        if iHeartRate > 40:
            self.HeartRate    = iHeartRate
        else:
            self.HeartRate    = 0

        if iTargetMode == mode_Grade:
            self.GearboxTeeth = iTeeth          # Only valid in Resistance-mode
        else:
            self.GearboxTeeth = 0               # Not valid in PowerMode

        # ----------------------------------------------------------------------
        # Update measurements once per second only (otherwise too much flicker)
        # .SetSpeedValue requires quite some processing, but since we are in our
        #   own process since 29-4-2020 refresh all, no optimize needed.
        # ----------------------------------------------------------------------
        delta = time.time() - self.LastFields # Delta time since previous
        if delta >= 1:                        # Refresh once per second
            self.LastFields = time.time()     # Time in seconds

            self.Speed.SetSpeedValue(float(min(max(0, fSpeed),     self.SpeedMax)))
            self.Revs.SetSpeedValue (float(min(max(0, iRevs),      self.RevsMax )))
            self.Power.SetSpeedValue(float(min(max(0, iPowerMean), self.PowerMax)))

            if True:
                # Alternating suffix makes the texts being refreshed
                suffix1 = '.'                       # str(0x32) # space
                suffix2 = ','                       # str(0xa0) # no break space
                suffix = self.txtSpeed.Value[-1:]
                suffix = suffix2 if suffix == suffix1 else suffix1
            else:
                # Such a measurement is not needed (anymore)
                suffix = ''

            # 2020-02-07: LargeTexts implemented
            if LargeTexts:
                self.txtSpeed.SetValue ("%4.1fkm/h"   % fSpeed  + suffix)
                self.txtRevs.SetValue  ("%i/min"      % iRevs   + suffix)
                self.txtPower.SetValue ("%iW"         % iPower  + suffix)
                if iTacx == 0:
                    self.txtTacx.SetValue  ("")
                else:
                    self.txtTacx.SetValue  ("%i"      % iTacx   + suffix)
                fTargetPower = "%iW"
            else:
                self.txtSpeed.SetValue ("%4.1f km/h"  % fSpeed  + suffix)
                self.txtRevs.SetValue  ("%i revs/min" % iRevs   + suffix)
                self.txtPower.SetValue ("%i Watt"     % iPower  + suffix)
                self.txtTacx.SetValue  ("Tacx=%i"     % iTacx   + suffix)
                fTargetPower = "%i Watt"

            if   iTargetMode == mode_Power:
                self.txtTarget.SetValue(fTargetPower % iTargetPower + suffix)

            elif iTargetMode == mode_Grade:
                s = "%2.0f%%" % fTargetGrade
                s += "%iW" % iTargetPower        # Target power added for reference
                                                 # Can be negative!
                self.txtTarget.SetValue(s + suffix)

            else:
                self.txtTarget.SetValue("No target"  + suffix)

            if logfile.IsOpen() and debug.on(debug.Data1 | debug.Data2):
                Elapsed = time.time() - self.LastFields
                logfile.Write ("SetValues() done in %s ms" % int(Elapsed*1000))

        # ----------------------------------------------------------------------
        # If there is a HeartRate, bounce the image
        # We pass here every 0.250 second = 400 times/minute
        # Do not process more often than heartbeat
        # ----------------------------------------------------------------------
        bRefreshRequired = False
        delta = time.time() - self.LastHeart # Delta time since previous
        if delta >= 60 / max(60, self.HeartRate * 2):   # At HeartRate, not slower than 1/second
                                                        # *2 because one heartbeat = 2 cycles
            self.LastHeart = time.time()     # Time in seconds
            if self.HeartRate > 0:
                if not self.txtHeartRate.IsShown():
                    self.txtHeartRate.Show()
                self.txtHeartRate.SetValue  ("%i" % self.HeartRate)

                if self.HeartRateWH  == 40:             # Show 36x36 on every other passage
                    self.HeartRateWH  = 36
                    self.HeartRateX  += 2               # center in the 40x40 area
                    self.HeartRateY  += 2               # center in the 40x40 area
                    bRefreshRequired  = True

                elif self.HeartRateWH  == 36:           # Show 40x40 on every other passage
                    self.HeartRateWH  = 40
                    self.HeartRateX  -= 2               # use the 40x40 area
                    self.HeartRateY  -= 2               # use the 40x40 area
                    bRefreshRequired  = True

            else:
                if self.txtHeartRate.IsShown():
                    self.txtHeartRate.Hide()
                    bRefreshRequired  = True

        # ----------------------------------------------------------------------
        # Gearbox
        # Show the size of the selected sprocket.
        # The cassette is displayed in OnPaint()!
        # ----------------------------------------------------------------------
        if self.GearboxTeeth > 0:
            if not self.txtGearbox.IsShown():
                self.txtGearbox.Show()

            self.txtGearbox.SetValue  ("%i" % self.GearboxTeeth)
            bRefreshRequired  = True            # So that gearbox is painted
            
        else:
            if self.txtGearbox.IsShown():
                self.txtGearbox.Hide()
                bRefreshRequired  = True

        # ----------------------------------------------------------------------
        # Refresh if required; so that JPGs are drawn in the OnPaint() event
        # ----------------------------------------------------------------------
        if bRefreshRequired: self.Refresh()

    def SetMessages(self, Tacx=None, Dongle=None, HRM=None):
        if Tacx   != None:
            if Tacx[:4] == '* * ': self.txtUsbTrainer.SetForegroundColour(wx.BLUE)
            else:                  self.txtUsbTrainer.SetForegroundColour(wx.BLACK)
            self.txtUsbTrainer.SetBackgroundColour(bg)
            self.txtUsbTrainer.SetValue(Tacx)

        if Dongle != None:
            self.txtAntDongle.SetValue(Dongle)

        if HRM != None:
            self.txtAntHRM.SetValue(HRM)
            
    # --------------------------------------------------------------------------
    # P e d a l S t r o k e A n a l y s i s
    # --------------------------------------------------------------------------
    # input:        User interface values
    #               info = list of tuples(Time,  Power)
    #
    # Description:  Show the Pedal Stroke Analysis in the RadarGraph
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def PedalStrokeAnalysis(self, info, Cadence):
        self.RadarGraph.PedalStrokeAnalysis(info, Cadence)

    # --------------------------------------------------------------------------
    # O n P a i n t
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Paint the frame, the bitmap and the HeartRate
    #               Ref: http://zetcode.com/wxpython/gdi/
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnPaint(self, event):
        # ----------------------------------------------------------------------
        # Draw background (to be done on every OnPaint() otherwise disappears!
        # ----------------------------------------------------------------------
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.BackgroundBitmap, 0, 0)          # LeftTop in pixels

        # ----------------------------------------------------------------------
        # Draw HeartRate
        #       Image functions done once, instead of every OnPaint()
        # ----------------------------------------------------------------------
        if self.HeartRateImage and self.HeartRate > 40:
#           img = self.HeartRateImage.Scale(self.HeartRateWH, self.HeartRateWH, wx.IMAGE_QUALITY_HIGH)
#           bmp = wx.Bitmap(img)
            if   self.HeartRateWH == 36:
                dc.DrawBitmap(self.bmp36x36, self.HeartRateX, self.HeartRateY)
            elif self.HeartRateWH == 40:
                dc.DrawBitmap(self.bmp40x40, self.HeartRateX, self.HeartRateY)
            else:
                logfile.Write("Unsupported image size")
        else:
            pass

        # ----------------------------------------------------------------------
        # Draw 12speed Digital Gearbox with interval of 10% lineair
        # 12speed since 12*3 pixels fits in the 40x40 area we have chosen to use
        # ----------------------------------------------------------------------
        if self.GearboxTeeth > 0:
            # Cassette corresponds to the shifting +/- with factor 1.1
            # FortiusANT takes 15 as midpoint,
            # so we have a "realistic" smallest sprocket of 9 teeth
            # The graphical size must decrease with even pixels and is
            #   therefore not calculated but a static table.
            #   Size are determined so that it approximately "looks good".
            #
            # The sizes[] table should not be modified without checking UI-design
            # The casette[] table could be changed,
            # - the 27,24..9 steps on every gear-change, but at either end
            #   the displayed cassette remains equal for changing teeth
            # - if 1.21 steps would be used, the displayed cassette steps once
            #   on every two gearchanges.
            # I'm curious whether when a question will be raised on this...
            #
            #            1   2   3   4   5   6   7   8   9  10  11  12
            cassette = [27, 24, 22, 20, 18, 17, 15, 14, 12, 11, 10, 9] # teeth
            sizes    = [40, 36, 32, 28, 24, 20, 16, 14, 12, 10,  8, 6] # pixels
            drawn = False
            
            for i in range(0,12):
                teeth=cassette[i]
                if teeth <= self.GearboxTeeth and not drawn:
                    dc.SetPen(wx.Pen(wx.RED))                     # Selected gear
                    drawn = True
                else:
                    dc.SetPen(wx.Pen(colorTacxFortius))           # Other gears

                x = self.GearboxX + 1 + i * 3                     # horizontal position
                w = 2                                             # width
                h = sizes [i]                                     # heigth
                y = self.GearboxY + int((self.GearboxWH - h) / 2) # vertical
                dc.DrawRectangle(self.GearboxX + x, y, w, h)
        else:
            pass
        # ----------------------------------------------------------------------
        # Draw Pedal Stroke Analysis
        # ----------------------------------------------------------------------
        if self.clv.PedalStrokeAnalysis:
            self.RadarGraph.OnPaint(dc)

    # --------------------------------------------------------------------------
    # O n T i m e r
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Is called every second; if we are IDLE, use function called
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnTimer(self, event):
        if self.OnTimerEnabled:
            # If we are not running and STOP has focus, correct it!
            # This is caused by setting focus from the thread, for which I did
            #   not find a proper solution
            if not self.RunningSwitch and self.btnStop.HasFocus():
                self.btnStart.SetFocus()

            self.callIdleFunction()

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n L o c a t e H W
    # --------------------------------------------------------------------------
    # input:        [Locate HW] pressed
    #
    # Description:  Enable [RUNOFF], [START]
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnLocateHW(self, event=False):
        if __name__ == "__main__": print ("OnClick_btnLocateHW()")

        self.OnTimerEnabled = False
        rtn = self.callLocateHW()
        self.OnTimerEnabled = True
        if rtn:
            self.btnRunoff.Enable()
            self.btnStart.Enable()
            self.btnLocateHW.Disable()
            self.btnStart.SetFocus()
        return rtn

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n R u n o f f
    # --------------------------------------------------------------------------
    # input:        [RUNOFF] pressed
    #
    # Description:  Start RunoffThread
    #               Enable [STOP], Disable [START] and [RUNOFF]
    #               If CloseButtonPressed, stop the program after the thread
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnRunoff(self, event):
        if __name__ == "__main__":  print ("OnClick_btnRunoff()")

        self.btnStop.Enable()
        self.btnStart.Disable()
        self.btnRunoff.Disable()
        self.btnStop.SetFocus()

        thread = threading.Thread(target=self.OnClick_btnRunoff_Thread)
        thread.start()

    def OnClick_btnRunoff_Thread(self):
        if __name__ == "__main__": print ("OnClick_btnRunoff_Thread()")

        self.RunningSwitch = True               # callRunoff() will loop
        self.CloseButtonPressed = False
        self.OnTimerEnabled = False
        self.callRunoff()
        self.OnTimerEnabled = True
        self.RunningSwitch = False              # Just to be sure
        self.OnClick_btnStop()                  # Thread may stop for any reason
                                                # Do GUI actions to enable the
                                                # correct buttons.

        if self.CloseButtonPressed == True:
            self.CloseButtonPressed = False     # Otherwise self.Close() is blocked
            self.Close()

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n S t a r t
    # --------------------------------------------------------------------------
    # input:        [START] pressed
    #
    # Description:  Start RunningThread
    #               Enable [STOP], Disable [START] and [RUNOFF]
    #               If CloseButtonPressed, stop the program after the thread
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnStart(self, event=False):
        if __name__ == "__main__": print ("OnClick_btnStart()")

        self.btnStop.Enable()
        self.btnStart.Disable()
        self.btnRunoff.Disable()
        self.btnStop.SetFocus()

        thread = threading.Thread(target=self.OnClick_btnStart_Thread)
        thread.start()

    def OnClick_btnStart_Thread(self):
        if __name__ == "__main__": print ("OnClick_btnStart_Thread()")

        self.RunningSwitch = True               # callTacx2Dongle() will loop
        self.CloseButtonPressed = False
        self.OnTimerEnabled = False
        self.callTacx2Dongle()
        self.OnTimerEnabled= True
        self.RunningSwitch = False              # Just to be sure
        self.OnClick_btnStop()                  # Thread may stop for any reason
                                                # Do GUI actions to enable the
                                                # correct buttons.

        if self.CloseButtonPressed == True:
            self.CloseButtonPressed = False     # Otherwise self.Close() is blocked
            self.Close()

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n S t o p
    # --------------------------------------------------------------------------
    # input:        [STOP] pressed
    #
    # Description:  Stop RunningThread; when that was not running, no effect
    #               Enable [START] and [RUNOFF], Disable [STOP]
    #
    # Output:       self.RunningSwitch
    # --------------------------------------------------------------------------
    def OnClick_btnStop(self, event=False):
        if __name__ == "__main__": print ("OnClick_btnStop()")
        self.RunningSwitch = False
        self.ResetValues()
        self.btnRunoff.Enable()
        self.btnStart.Enable()
        self.btnStop.Disable()
        self.btnStart.SetFocus()            # SetFocus in thread would be nicer, setting focus to either Runoff or Start

    # --------------------------------------------------------------------------
    # O n C l o s e
    # --------------------------------------------------------------------------
    # input:        ALT-F4 is pressed
    #
    # Description:  if the thread is running, stop thread and indicate to stop
    #                   the program after the thread
    #               if the thread is NOT running, stop immediatly
    #
    # Output:       self.RunningSwitch
    #               self.CloseButtonPressed
    # --------------------------------------------------------------------------
    def OnClose(self, event):
        if __name__ == "__main__": print("OnClose()")

        if self.RunningSwitch == True:          # Thread is running
            self.RunningSwitch = False          # Stop the thread
                                                # More accurately: ask the thread to finish!
            self.CloseButtonPressed = True      # Indicate to stop program
            # Expected behaviour from the thread:
            # - stop because RunningSwitch == False
            # - check CloseButtonPressed == True and
            #       1. set CloseButtonPressed = False
            #       2. call self.Close()
            # This event will be called again and go through the else and end.
        elif self.CloseButtonPressed:           # Waiting for thread to finish;
                                                # Do not close again!
            print('Please wait for thread to end...')
            pass

        else:                                   # No thread is running;
            event.Skip()				        # Do default actions (stop program)

# ------------------------------------------------------------------------------
# our normal wxApp-derived class, as usual
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    clv = cmd.CommandLineVariables()
    app = wx.App(0)

    frame = frmFortiusAntGui(None, clv)
    app.SetTopWindow(frame)
    frame.Show()
    frame.Autostart()

    app.MainLoop()
