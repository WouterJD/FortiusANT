#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-05-07"
# 2020-05-07    pylint error free
# 2020-05-01    First version
#-------------------------------------------------------------------------------

# https://github.com/wxWidgets/wxPython-Classic/blob/master/samples/wxPIA_book/Chapter-12/radargraph.py

import wx
import math
import random
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

    # --------------------------------------------------------------------------
    # P e d a l S t r o k e A n a l y s i s
    # S h o w R a d a r G r a p h
    # --------------------------------------------------------------------------
    # input:        User interface values
    #               info = list of tuples(Time,  Power)
    #               data = list of tuples(Angle, Power)
    #
    # Description:  Show the Pedal Stroke Analysis in the RadarGraph
    #               When the right pedal is to the front (0 degrees) then the
    #               pedalecho is given (left pedal is back). "Adjust" is for
    #               possible improvement if ever needed.
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def PedalStrokeAnalysis(self, info, Cadence):
        Adjust = 0
        StartTime = info[0][0]                  # First element = at pedelecho
        data      = []
        for i in info:
            Timestamp = i[0]                    # Time of the measurement
            Delta     = (Timestamp - StartTime) # Elapsed time in seconds
            dps       = Cadence / 60 * 360      # Cadence = Rotations/minute
                                                # dps = Degrees/second

            Angle     = int( Delta * dps )      # Angle since PedalEcho
            Angle    += Adjust
            if Angle >= 360:
                Angle -= 360

            Power     = int( i[1] )
            d = (Angle, Power)
            # s = ""
            # logfile.Write('Angle=%3s power=%5s Time=%s' % (Angle, Power, i[0]))
            data.append(d)
        self.ShowRadarGraph(data)
        pass

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
            self.RadarGraph.Show(self.power)    # pylint: disable=maybe-no-member

            # ------------------------------------------------------------------
            # Get the paint event to draw the RadarGraph
            # ------------------------------------------------------------------
            self.Bind(wx.EVT_PAINT, self.OnPaint)

            # ------------------------------------------------------------------
            # Create a timer to update the data values, to serve as demo
            # ------------------------------------------------------------------
            self.Bind(wx.EVT_TIMER, self.OnTimeout)
            self.timer = wx.Timer(self)
            self.timer.Start(500)


        def OnTimeout(self, evt):
            for i, p in enumerate(self.power):
                self.power[i] = (p[0], p[1] + random.uniform(-15, 15))
            self.RadarGraph.Show(self.power)          # pylint: disable=maybe-no-member
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

