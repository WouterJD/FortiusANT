#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2021-02-21"
# 2021-02-21    .Show replaced by .ShowRadarGraph (now can be tested again)
#               added: Angle()
#               ToDo: show the rotating pedal.
# 2020-05-07    pylint error free
# 2020-05-01    First version
#-------------------------------------------------------------------------------

# https://github.com/wxWidgets/wxPython-Classic/blob/master/samples/wxPIA_book/Chapter-12/radargraph.py

import math
import random
import time
import wx
import logfile

# ------------------------------------------------------------------------------
# Create the RadarGraph window
# ------------------------------------------------------------------------------
# Execute:      The radar graph plots a polygon, showing power-values on the
#               pedal-stroke angle.
#
# Functions:    Show, providing a list of tuples (angle, power)
#
# Three functions to be provided:
#               callIdleFunction(self)
#               callLocateHW(self)          returns True/False
#               callRunoff(self)
#               callTacx2Dongle(self)
# ------------------------------------------------------------------------------
class clsRadarGraph():
    def __init__(self, parent, title, x, y, wh):
        self.parent     = parent
        self.title      = title             # Horizontal axis title
        self.maxval     = 100               # The wattage at 100% outer circle
        self.polypoints = []                # The polygon points to be drawn
        self.x          = x                 # Horizontal position of graph
        self.y          = y                 # Vertical position
        self.wh         = wh                # width and height
        self.data       = []                # There is no data yet
                                            # List of tuples (angle, power)
        self.cx         = x + int( wh / 2 ) # Center of the polygon (circles)
        self.cy         = y + int( wh / 2 )
        self.radius100  = self.wh / 2 / 1.1 # 10% space around the 100% circle

        self.StartTime  = 0                 # Time at PedelEcho
        self.Cadence    = 0                 # Last received Cadence

    # --------------------------------------------------------------------------
    # P e d a l S t r o k e A n a l y s i s
    # S h o w R a d a r G r a p h
    # --------------------------------------------------------------------------
    # input:        User interface values
    #               info = list of tuples(Time,  Power)
    #
    # Description:  Show the Pedal Stroke Analysis in the RadarGraph
    #
    # Output:       data = list of tuples(Angle, Power)
    # --------------------------------------------------------------------------
    def PedalStrokeAnalysis(self, info, Cadence):
        self.Cadence    = Cadence
        self.StartTime  = info[0][0]            # First element = at pedelecho
        data            = []
        logfile.Write('PedalStrokeAnalysis - Cadence=%3s info=%3s StartTime=%s' % \
                        (self.Cadence, len(info), self.StartTime))
        for i in info:
            Angle = self.Angle(i[0])
            if Angle == -1: break

            Power = i[1]

            d = (Angle, Power)
            logfile.Write('Angle=%3s power=%5s Time=%s' % (Angle, Power, i[0]))
            data.append(d)
        self.ShowRadarGraph(data)

    def ShowRadarGraph(self, data):
        # logfile.Console('ShowRadarGraph')
        # ----------------------------------------------------------------------
        # Calculate a scale factor to use for drawing the graph
        # The maximum power is 100% and all other powers are inside the circles
        # ----------------------------------------------------------------------
        self.maxval = 100   # at low power, outer circle = 100Watt
        for d in data:
            self.maxval = max(d[1], self.maxval)
        self.maxval /= 0.75 # If nice round move, we're at 75% border.
        self.scale = self.radius100 / self.maxval
        # ----------------------------------------------------------------------
        # Now find the coordinates for each data point
        # d[0]=Angle and d[1]=Power are calculated into a point
        # ----------------------------------------------------------------------
        self.polypoints = []
        for d in data:
            point = self.PolarToCartesian(d[0], d[1] * self.scale, self.cx, self.cy)
            self.polypoints.append(point)
        # ----------------------------------------------------------------------
        # Force OnPaint()
        # ----------------------------------------------------------------------
        self.parent.Refresh()

    # --------------------------------------------------------------------------
    # A n g l e
    # --------------------------------------------------------------------------
    # input:        TimeStamp
    #               self.StartTime
    #
    # Description:  Calculate angle, compared to PedalEcho position
    #               When the right pedal is to the front (0 degrees) then the
    #               pedalecho is given (left pedal is back). 
    #               "Adjust" is for possible improvement if ever needed.
    #
    # Return:       0 <= Angle < 360
    #               -1 means: ignore this
    # --------------------------------------------------------------------------
    def Angle(self, Timestamp):
        rtn    = -1
        Adjust = 0                              # Adjust position of PedalEcho magnet
        Delta  = (Timestamp - self.StartTime)   # Elapsed time in seconds
        dps    = self.Cadence / 60 * 360        # Cadence = Rotations/minute
                                                # dps = Degrees/second

        rtn    = int( Delta * dps )             # Angle since PedalEcho
        if rtn >= 360:                          # Since called on PedalEcho
            rtn = -1                            # Only one circle expected
        else:
            rtn += Adjust
            if rtn >= 360: rtn -= 360

        return rtn

    def PolarToCartesian(self, angle, radius, cx, cy):
        x = int(radius * math.cos(math.radians(angle)))
        y = int(radius * math.sin(math.radians(angle)))
        return (cx + x, cy - y)

    def OnPaint(self, dc):
        # dc = wx.PaintDC(self) of the parent frame, we draw on the background
        # ----------------------------------------------------------------------
        # Draw the graph axis and "bulls-eye" with rings at 25%, 50%, 75% and
        # 100% positions
        # ----------------------------------------------------------------------
        dc.SetPen(wx.Pen("black", 1))                                               # pylint: disable=maybe-no-member

        dc.SetBrush(wx.Brush(wx.Colour(139,193,227)))                               # pylint: disable=maybe-no-member
        dc.DrawCircle(self.cx, self.cy, int(1.00 * self.radius100) )

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawCircle(self.cx, self.cy, int(0.75 * self.radius100) )
        dc.DrawCircle(self.cx, self.cy, int(0.50 * self.radius100) )
        dc.DrawCircle(self.cx, self.cy, int(0.25 * self.radius100) )

        dc.SetFont(wx.Font( int(12 * self.wh/300), wx.SWISS, wx.NORMAL, wx.NORMAL)) # pylint: disable=maybe-no-member
        tw, th = dc.GetTextExtent(self.title)
        dc.DrawText( self.title, int(self.cx - tw/2 ), int(self.cy - th) )

        dc.SetFont(wx.Font( int(8 * self.wh/300), wx.SWISS, wx.NORMAL, wx.NORMAL))  # pylint: disable=maybe-no-member
        tw, th = dc.GetTextExtent("100%")
        dc.DrawText( "%sW" % int(0.25 * self.maxval), int(self.cx + 0.25 * self.radius100 - tw), self.cy)
        dc.DrawText( "%sW" % int(0.50 * self.maxval), int(self.cx + 0.50 * self.radius100 - tw), self.cy)
        dc.DrawText( "%sW" % int(0.75 * self.maxval), int(self.cx + 0.75 * self.radius100 - tw), self.cy)
        dc.DrawText( "%sW" % int(1.00 * self.maxval), int(self.cx + 1.00 * self.radius100 - tw), self.cy)

        # ----------------------------------------------------------------------
        # Draw cross lines (horizontal, vertical)
        # ----------------------------------------------------------------------
        dc.SetPen(wx.Pen("black", 2))                                               # pylint: disable=maybe-no-member
        dc.DrawLine(int(self.cx-self.radius100 * 1.1), int(self.cy), int(self.cx+self.radius100 * 1.1), int(self.cy))
        dc.DrawLine(int(self.cx), int(self.cy-self.radius100 * 1.1), int(self.cx), int(self.cy+self.radius100 * 1.1))

        # ----------------------------------------------------------------------
        # Draw the plot data as a filled polygon
        # ----------------------------------------------------------------------
        # dc.SetBrush(wx.Brush("forest green"))
        # dc.SetBrush(wx.Brush(wx.Colour(139,193,227)))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen("red", 3))            # pylint: disable=maybe-no-member
        dc.DrawPolygon(self.polypoints)

        # ----------------------------------------------------------------------
        # Draw the location of the right pedal
        # I admit: I do not know how to get a moving object but not make the
        #          screen flicker. So left for future improvement.
        # ----------------------------------------------------------------------
        Angle = int( self.Angle( time.time() ) )            # Where is the pedal now?
        if False and Angle >= 0:
            dc.SetPen(wx.Pen("black", 1))                   # pylint: disable=maybe-no-member
            if -2 < Angle < 2:
                dc.SetBrush(wx.Brush(wx.Colour(255,0,0)))   # pylint: disable=maybe-no-member
            else:
                dc.SetBrush(wx.Brush(wx.Colour(0,0,255)))   # pylint: disable=maybe-no-member

            if Angle in (90,270):
                x = 0
                y = self.radius100
            elif Angle in (0,180):
                x = self.radius100
                y = 0
            else:
                x = self.radius100 / math.cos(math.radians(Angle))
                y = self.radius100 / math.sin(math.radians(Angle))

            x = int(self.cx + x)
            y = int(self.cy + y)
            print('pedal circle Angle=%3s x=%3s y=%3s' % (Angle, x, y))
            dc.DrawCircle(x, y, 5)

# ------------------------------------------------------------------------------
# Demo- and testcode
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    class TestFrame(wx.Frame):                 # pylint: disable=maybe-no-member
        power  = [] # Array with power-tuples
        step   = 9  # Degrees. Good values: 1, 9, 15, 18, 30, 90

        def __init__(self):
            # pylint: disable=maybe-no-member
            wx.Frame.__init__(self, None, title="Double Buffered Drawing", size=(680,680))
            # ------------------------------------------------------------------
            # This is what another program could do:
            # ------------------------------------------------------------------
            self.RadarGraph = clsRadarGraph(self, "Pedal stroke analysis", 25, 25, 200)

            # Fill list and show it 
            for i in range(0,360,int(self.step)):
                self.power.append((i, random.randint(75, 125)))
            self.RadarGraph.ShowRadarGraph(self.power)

            # ------------------------------------------------------------------
            # Get the paint event to draw the RadarGraph
            # ------------------------------------------------------------------
            self.Bind(wx.EVT_PAINT, self.OnPaint)

            # ------------------------------------------------------------------
            # Create a timer to update the data values, to serve as demo
            # ------------------------------------------------------------------
            self.Bind(wx.EVT_TIMER, self.OnTimeout)
            self.timer = wx.Timer(self)
            self.timer.Start(50)
            self.CountDown = 0

        def OnTimeout(self, evt):
            if self.CountDown == 0:
                for i, p in enumerate(self.power):
                    self.power[i] = (p[0], p[1] + random.uniform(-15, 15))
                self.RadarGraph.ShowRadarGraph(self.power)
                self.CountDown = 10
            else:
                self.CountDown -= 1
            self.Refresh()
            
        def OnPaint(self, event):
            self.RadarGraph.OnPaint(wx.PaintDC(self)) # pylint: disable=maybe-no-member
            
    # --------------------------------------------------------------------------
    # Startup
    # --------------------------------------------------------------------------
    app = wx.App()
    frm = TestFrame()
    frm.Show()
    app.MainLoop()

