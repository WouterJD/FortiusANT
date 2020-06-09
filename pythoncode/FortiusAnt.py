#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2020-05-24"
# 2020-05-24    WindowTitle in logfile
# 2020-04-23    First version; core functions separated into FortiusAntBody.py
#               This module contains program startup, GUI-binding and
#               multi-processing functionality only
#-------------------------------------------------------------------------------
import argparse
from datetime                           import datetime
import multiprocessing
import numpy
import pickle
import platform, glob
import os
import random
import sys
import struct
import threading
import time
import usb.core
import wx

import antDongle            as ant
import antHRM               as hrm
import antFE                as fe
import debug
import logfile
import FortiusAntBody
import FortiusAntCommand    as cmd
import FortiusAntGui        as gui
import usbTrainer
import structConstants      as sc

#-------------------------------------------------------------------------------
# Directives for this module
#-------------------------------------------------------------------------------
testMode            = False         # Production version should be False
useMultiProcessing  = True          # Production version can be either two

#-------------------------------------------------------------------------------
# Constants between the two processes, exchanged through the pipe
#-------------------------------------------------------------------------------
cmd_EndExecution        = 19590         # Child->Main; No response expected
cmd_Idle                = 19591         # Child->Main; Response = Buttons
cmd_LocateHW            = 19592         # Child->Main; Response = True/False for success/failure
cmd_Runoff              = 19593         # Child->Main; Response = True
cmd_Tacx2Dongle         = 19594         # Child->Main; Response = True
cmd_StopButton          = 19595         # Child->Main; Response = True

cmd_SetMessages         = 19596         # Main->Child; No response expected
cmd_SetValues           = 19597         # Main->Child; No response expected
cmd_PedalStrokeAnalysis = 19598         # Main->Child; No response expected

# ==============================================================================
# The following functions are called from the GUI, Console or multi-processing
# parent process.
# The functions are used to test the multi-processing and/or GUI without
# being bothered by the actual FortiusAntBody/usbTrainer/antDongle functionality.
# ==============================================================================
def IdleFunction(self):
    if testMode:
        print ('i', end='')
        sys.stdout.flush()
        s = time.gmtime().tm_sec
        if s % 4 == 0:
            Buttons = usbTrainer.DownButton
        else:
            Buttons = 0
    else:
        Buttons = FortiusAntBody.IdleFunction(self)
    return Buttons

def LocateHW(self):
    if testMode:
        print('')
        logfile.Console ('Checking for HW')
        time.sleep(1)
        logfile.Console ('Done')
        rtn = True
    else:
        rtn = FortiusAntBody.LocateHW(self)
    return rtn

def Runoff(self):
    if testMode:
        print('')
        while self.RunningSwitch:
            logfile.Console ('Doing runoff')
            self.SetMessages('Doing runoff', datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S'), str(time.gmtime().tm_sec))
            self.SetValues(0,1,time.gmtime().tm_sec,3,4,5,6,7,8)
            time.sleep(1)
        logfile.Console ('Runoff done')
        rtn = True
    else:
        rtn = FortiusAntBody.Runoff(self)
    return rtn

def Tacx2Dongle(self):
    if testMode:
        print('')
        while self.RunningSwitch:
            logfile.Console ('Translate Tacx 2 Dongle')
            self.SetMessages('Translate Tacx 2 Dongle', datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S'), str(time.gmtime().tm_sec))
            self.SetValues(0,1,time.gmtime().tm_sec,3,4,5,6,7,8)
            time.sleep(1)
        logfile.Console ('Tacx2Dongle done')
        rtn = True
    else:
        rtn = FortiusAntBody.Tacx2Dongle(self)
    return rtn

# ==============================================================================
# Subclass FortiusAnt GUI with our directly called functions
# ------------------------------------------------------------------------------
# Called:       IdleFunction, LocateHW(), Runoff() and Tacx2Dongle() are called
#                    to provide the required functionality.
# ==============================================================================
class frmFortiusAnt(gui.frmFortiusAntGui):
    def callIdleFunction(self):
        Buttons = IdleFunction(self)
        # ----------------------------------------------------------------------
        # IdleFunction checks trainer for headunit button press
        # Since the GUI does not know the usbTrainer, we do this here
        # ----------------------------------------------------------------------
        if   Buttons == usbTrainer.EnterButton: self.Navigate_Enter()
        elif Buttons == usbTrainer.DownButton:  self.Navigate_Down()
        elif Buttons == usbTrainer.UpButton:    self.Navigate_Up()
        elif Buttons == usbTrainer.CancelButton:self.Navigate_Back()
        else:                                   pass
        return True

    def callLocateHW(self):
        return LocateHW(self)

    def callRunoff(self):
        return Runoff(self)

    def callTacx2Dongle(self):
        return Tacx2Dongle(self)

# ==============================================================================
# Class to create a Console-GUI
# ------------------------------------------------------------------------------
# Functions:    Autostart() is similar to frmFortiusAntGui.autostart
#                   and executes all program-functionality
#               SetValues() and SetMessages() to show the progress on the console
#
# Called:       LocateHW() and Tacx2Dongle() are called to provide the required
#               functionality.
# ==============================================================================
class clsFortiusAntConsole:

    def __init__(self):
        self.RunningSwitch       = False
        self.LastTime            = 0

    def Autostart(self):
        if LocateHW(self):
            self.RunningSwitch = True
            Tacx2Dongle(self)

    def SetValues(self, fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, iTacx, iHeartRate, iTeeth):
        # ----------------------------------------------------------------------
        # Console: Update current readings, once per second
        # ----------------------------------------------------------------------
        delta = time.time() - self.LastTime   # Delta time since previous
        if delta >= 1 and (not clv.gui or debug.on(debug.Application)):
            self.LastTime = time.time()           # Time in seconds

            if   iTargetMode == gui.mode_Power:
                sTarget = "%3.0fW" % iTargetPower
            elif iTargetMode == gui.mode_Grade:
                sTarget = "%3.1f%%" % fTargetGrade
                if iTargetPower > 0:                         # 2020-01-22
                    sTarget += "(%iW)" % iTargetPower        # Target power added for reference
            else:
                sTarget = "None"
            msg = "Target=%s Speed=%4.1fkmh hr=%3.0f Current=%3.0fW Cad=%3.0f r=%4.0f T=%3.0f" % \
                  (  sTarget,    fSpeed,  iHeartRate,       iPower,     iRevs,  iTacx, int(iTeeth) )
            logfile.Console (msg)

    def SetMessages(self, Tacx=None, Dongle=None, HRM=None):
        if Tacx   != None:
            logfile.Console ("Tacx   - " + Tacx)

        if Dongle != None:
            logfile.Console ("Dongle - " + Dongle)

        if HRM != None:
            logfile.Console ("AntHRM - " + HRM)

# ==============================================================================
# Subclass FortiusAnt GUI with our multi-processing functions
# ------------------------------------------------------------------------------
# Description:  This class is functionally identical to frmFortiusAnt, with that
#               difference that the required functions are not called, but
#               requested through the multiprocessing pipe.
#
# Called:       cmd_IdleFunction, cmd_LocateHW, cmd_Runoff and cmd_Tacx2Dongle
#               are sent to the main process for execution and the response is
#               received.
#
# Functions:    For this purpose, GuiMessageToMain() is available.
# ==============================================================================
class frmFortiusAntChild(gui.frmFortiusAntGui):
    # --------------------------------------------------------------------------
    # gui_conn is the child-connection to the parent process
    # --------------------------------------------------------------------------
    def __init__(self, parent, conn, pclv):
        self.gui_conn = conn
        super(frmFortiusAntChild, self).__init__(parent, pclv)

    def GuiMessageToMain(self, command, wait=True):
        # ----------------------------------------------------------------------
        # Step 1. GUI sends a command to main
        # ----------------------------------------------------------------------
        if debug.on(debug.MultiProcessing) and not (command == cmd_Idle):
            logfile.Write ("mp-GuiMessageToMain(conn, %s, %s)" % (command, wait))
        self.gui_conn.send(command)

        rtn = True
        while wait:
            # ------------------------------------------------------------------
            # Check if requested command is ended
            # OR that information is received from Main
            # ------------------------------------------------------------------
            # Will be more efficient than self.gui_conn.poll() / sleep loop...
            # ------------------------------------------------------------------
            # Step 4. GUI receives the response (command, rtn)
            # ------------------------------------------------------------------
            msg = self.gui_conn.recv()
            cmd = msg[0]
            rtn = msg[1]
            if debug.on(debug.MultiProcessing) and not (command == cmd_Idle and rtn == 0):
                logfile.Write ("mp-GuiAnswerFromMain(conn) returns (%s, %s)" % (cmd, rtn))

            # ------------------------------------------------------------------
            # We wait for the response on the command
            # and in the meantime receive data to displayed
            #
            # cmd_StopButton is treated differently, since that command is sent
            # while we are waiting for the response on cmd_Runoff or cmd_Tacx2Dongle
            # we ignore the response here and cmd_StopButton does not start wait-loop
            # to avoid some sort of nesting or so.
            # ------------------------------------------------------------------
            if cmd == command:
                break                   # command is ready
            elif cmd == cmd_StopButton:
                pass
            elif cmd == cmd_SetValues:
                self.SetValues(rtn[0], rtn[1], rtn[2], rtn[3], rtn[4], rtn[5], rtn[6], rtn[7], rtn[8])# rtn is tuple
            elif cmd == cmd_SetMessages:
                self.SetMessages(rtn[0], rtn[1], rtn[2])# rtn is (Tacx, Dongle, HRM) tuple
            elif cmd == cmd_PedalStrokeAnalysis:
                self.PedalStrokeAnalysis(rtn[0], rtn[1])# rtn is (info, Cadence) tuple
                pass
            else:
                logfile.Console('%s active but unknown response received (%s, %s); the message is ignored.' % (command, cmd, rtn))
                break
        return rtn

    # --------------------------------------------------------------------------
    # Multiprocessing;
    #       a command is sent to the parent process and the function waits for
    #       a response.
    #       Idle/LocateHW:      the only response expected is the answer from the function
    #       Runoff/Tacx2Dongle: the main process can also send information to be displayed!
    # --------------------------------------------------------------------------
    def callIdleFunction(self):
        Buttons = self.GuiMessageToMain(cmd_Idle)     # Send command and wait response
        # ----------------------------------------------------------------------
        # IdleFunction checks trainer for headunit button press
        # Since the GUI does not know the usbTrainer, we do this here
        # ----------------------------------------------------------------------
        if   Buttons == usbTrainer.EnterButton: self.Navigate_Enter()
        elif Buttons == usbTrainer.DownButton:  self.Navigate_Down()
        elif Buttons == usbTrainer.UpButton:    self.Navigate_Up()
        elif Buttons == usbTrainer.CancelButton:self.Navigate_Back()
        else:                                   pass
        return True

    def callLocateHW(self):
        rtn = self.GuiMessageToMain(cmd_LocateHW) # Send command and wait response
        return rtn

    def callRunoff(self):
        rtn = self.GuiMessageToMain(cmd_Runoff)
        return rtn

    def callTacx2Dongle(self):
        rtn = self.GuiMessageToMain(cmd_Tacx2Dongle)
        return rtn

    def OnClick_btnStop(self, event=False):
        gui.frmFortiusAntGui.OnClick_btnStop(self, event)
        self.GuiMessageToMain(cmd_StopButton, False)

    def OnClose(self, event):
        if self.RunningSwitch == True:          # Thread is running
            self.GuiMessageToMain(cmd_StopButton, False)
        gui.frmFortiusAntGui.OnClose(self, event)

# ==============================================================================
# Class to create a parent-process
# ------------------------------------------------------------------------------
# Description:  This class creates the parent, which receives commands from the
#               GUI child process, calls the required function and returns the
#               result.
#
# Called:       cmd_IdleFunction, cmd_LocateHW, cmd_Runoff and cmd_Tacx2Dongle
#               are called and the response is sent to the child process.
#
# Functions:    For this purpose, MainCommandFromGui() and MainRespondToGUI()
#               are available.
#
#               SetMessages() and SetValues() are called by the functions and
#               send the data to be displayed to the child, not awaiting an
#               answer.
#
#               RunoffThread() and Tacx2DongleThread() act as function to create
#               a thread to execute the functions, whilst not blocking the
#               the process to receive messages from the GUI client, which can
#               order to stop.
# ==============================================================================
class clsFortiusAntParent:
    def __init__(self, app_conn):
        self.RunningSwitch      = False
        self.app_conn           = app_conn
        self.LastTime           = 0
        self.PreviousMessages   = None

    def MainCommandFromGui(self):               # Step 2. Main receives command from GUI
        command = self.app_conn.recv()
        if debug.on(debug.MultiProcessing) and not (command == cmd_Idle):
            logfile.Write ("mp-MainCommandFromGui() returns %s" % (command))
        return command

    def MainRespondToGUI(self, command, rtn):
        if debug.on(debug.MultiProcessing) and not (command == cmd_Idle and rtn == 0):
            logfile.Write ("mp-MainRespondToGUI(%s, %s)" % (command, rtn))
        self.app_conn.send((command, rtn))      # Step 3. Main sends the response to GUI

    def SetValues(self, fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, iTacx, iHeartRate, iTeeth):
        delta = time.time() - self.LastTime     # Delta time since previous call
        if delta >= 1:                          # Do not send faster than once per second
            self.LastTime = time.time()         # Time in seconds
            if debug.on(debug.MultiProcessing): logfile.Write ("mp-MainDataToGUI(%s, (%s, %s, %s, %s, %s, %s, %s, %s, %s))" % \
                    (cmd_SetValues, fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, iTacx, iHeartRate, iTeeth))
            self.app_conn.send((cmd_SetValues, (fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, iTacx, iHeartRate, iTeeth)))

    def SetMessages(self, Tacx=None, Dongle=None, HRM=None):
        newMessages = (Tacx, Dongle, HRM)
        if newMessages != self.PreviousMessages:    # Send immediatly if changed
            self.PreviousMessages = newMessages
            if debug.on(debug.MultiProcessing): logfile.Write ("mp-MainDataToGUI(%s, (%s, %s, %s))" % (cmd_SetMessages, Tacx, Dongle, HRM))
            self.app_conn.send((cmd_SetMessages, (Tacx, Dongle, HRM)))  # x. Main sends messages to GUI; no response expected

    def PedalStrokeAnalysis(self, info, Cadence):
        if debug.on(debug.MultiProcessing): logfile.Write ("mp-MainDataToGUI(%s, (info, %s))" % (cmd_PedalStrokeAnalysis, Cadence))
        self.app_conn.send((cmd_PedalStrokeAnalysis, (info, Cadence)))  # x. Main sends messages to GUI; no response expected
        pass

    def RunoffThread(self):
        rtn = Runoff(self)
        self.MainRespondToGUI(cmd_Runoff, rtn)

    def Tacx2DongleThread(self):
        rtn = Tacx2Dongle(self)
        self.MainRespondToGUI(cmd_Tacx2Dongle, rtn)

    def ListenToChild(self):
        # ----------------------------------------------------------------------
        # Poll the GUI what we are expected to do
        # Note that we never end (on our initiative)!!
        # ----------------------------------------------------------------------
        while True:
            gui_command = self.MainCommandFromGui()

            if   gui_command == cmd_EndExecution:
                break

            elif gui_command == cmd_Idle:
                rtn = IdleFunction(self)
                self.MainRespondToGUI(cmd_Idle, rtn)

            elif gui_command == cmd_LocateHW:
                rtn = LocateHW(self)
                self.MainRespondToGUI(cmd_LocateHW, rtn)

            elif gui_command == cmd_Runoff:
                self.RunningSwitch = True
                thread = threading.Thread(target=self.RunoffThread)
                thread.start()

            elif gui_command == cmd_Tacx2Dongle:
                self.RunningSwitch = True
                thread = threading.Thread(target=self.Tacx2DongleThread)
                thread.start()

            elif gui_command == cmd_StopButton:
                if testMode:
                    print('')
                    logfile.Console ('Stop button pressed')
                self.RunningSwitch = False
                self.MainRespondToGUI(cmd_StopButton, True)

            else:
                logfile.Console('Unexpected command from GUI: %s' % gui_command)
                rtn = False

# ------------------------------------------------------------------------------
# F o r t i u s A n t C h i l d
# ------------------------------------------------------------------------------
# Input:        clv     Command line variables
#               conn    the child-side of the multiprocessing pipe
#
# Description:  Here the user-interface is created.
#               The user-interface will call the callback functions as defined
#               above.
#
# Output:       none
# ------------------------------------------------------------------------------
def FortiusAntChild(clv, conn):
    # --------------------------------------------------------------------------
    # Initialize the child process, create our own logfile
    # --------------------------------------------------------------------------
    debug.activate(clv.debug)
    if debug.on(debug.Any):
        logfile.Open('FortiusAntGUI')
        logfile.Console('FortiusAnt GUI started in child-process')

    FortiusAntBody.Initialize(clv)

    # --------------------------------------------------------------------------
    # Start the user-interface
    # --------------------------------------------------------------------------
    app = wx.App(0)
    frame = frmFortiusAntChild(None, conn, clv)
    app.SetTopWindow(frame)
    frame.Show()
    if clv.autostart:
        frame.Autostart()
    app.MainLoop()

    # --------------------------------------------------------------------------
    # Signal parent that we're done
    # --------------------------------------------------------------------------
    frame.GuiMessageToMain(cmd_EndExecution, False)
    if debug.on(debug.Any):
        logfile.Console('FortiusAnt GUI ended')

# ==============================================================================
# Main program
# ==============================================================================
if __name__ == "__main__":
    multiprocessing.freeze_support()
    global clv

    # --------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------
    debug.deactivate()
    clv = cmd.CommandLineVariables()
    debug.activate(clv.debug)
    FortiusAntBody.Initialize(clv)

    if debug.on(debug.Any):
        logfile.Open()
        logfile.Console("FortiusANT started")
        clv.print()
        logfile.Console("------------------")

    #-------------------------------------------------------------------------------
    # Component info
    #-------------------------------------------------------------------------------
    if debug.on(debug.Any):
        logfile.Write('Version info for the components' )
        logfile.Write(gui.WindowTitle)
        s = " %20s = %s"
        logfile.Write(s % ('FortiusAnt',                    __version__ ))
        logfile.Write(s % ('antDongle',                 ant.__version__ ))
        logfile.Write(s % ('antHRM',                    hrm.__version__ ))
        logfile.Write(s % ('antFE',                      fe.__version__ ))
        logfile.Write(s % ('debug',                   debug.__version__ ))
        logfile.Write(s % ('FortiusAntBody', FortiusAntBody.__version__ ))
        logfile.Write(s % ('FortiusAntCommand',         cmd.__version__ ))
        logfile.Write(s % ('FortiusAntGui',             gui.__version__ ))
        logfile.Write(s % ('logfile',               logfile.__version__ ))
        logfile.Write(s % ('structConstants',            sc.__version__ ))
        logfile.Write(s % ('usbTrainer',         usbTrainer.__version__ ))

        logfile.Write(s % ('argparse',             argparse.__version__ ))
    #   logfile.Write(s % ('binascii',             binascii.__version__ ))
    #   logfile.Write(s % ('math',                     math.__version__ ))
        logfile.Write(s % ('numpy',                   numpy.__version__ ))
        logfile.Write(s % ('os',                         os.name        ))
        if os.name == 'nt':
            v = sys.getwindowsversion()
            logfile.Write((s + '.%s') %    ('windows',  v.major, v.minor))
        logfile.Write(s % ('pickle',                 pickle.format_version ))
        logfile.Write(s % ('platform',             platform.__version__ ))
    #   logfile.Write(s % ('glob',                     glob.__version__ ))
    #   logfile.Write(s % ('random',                 random.__version__ ))
        logfile.Write(s % ('sys (python)',              sys.version ))
    #   logfile.Write(s % ('struct',                 struct.__version__ ))
    #   logfile.Write(s % ('threading',           threading.__version__ ))
    #   logfile.Write(s % ('time',                     time.__version__ ))
        logfile.Write(s % ('usb',                       usb.__version__ ))
        logfile.Write(s % ('wx',                         wx.__version__ ))

        logfile.Write('FortiusANT code flags')
        logfile.Write(s % ('useMultiProcessing',            useMultiProcessing))
        logfile.Write("------------------")

    if not clv.gui:
        # --------------------------------------------------------------------------
        # Console only, no multiprocessing required to separate GUI
        # --------------------------------------------------------------------------
        Console = clsFortiusAntConsole()
        Console.Autostart()

    elif not useMultiProcessing:
        # --------------------------------------------------------------------------
        # No multiprocessing wanted, start GUI immediatly
        # --------------------------------------------------------------------------
        clv.PedalStrokeAnalysis = False
        app = wx.App(0)
        frame = frmFortiusAnt(None, clv)
        app.SetTopWindow(frame)
        frame.Show()
        if clv.autostart:
            frame.Autostart()
        app.MainLoop()

    else:
        # --------------------------------------------------------------------------
        # Multiprocessing wanted, start GUI in it's own process
        # --------------------------------------------------------------------------
        # https://docs.python.org/3/library/multiprocessing.html
        # Create queue and sub-process
        # --------------------------------------------------------------------------
        app_conn, gui_conn = multiprocessing.Pipe(True)
        pChild = multiprocessing.Process(target=FortiusAntChild, args=(clv, gui_conn) )
        pChild.start()

        # --------------------------------------------------------------------------
        # Poll child-process untill done
        # --------------------------------------------------------------------------
        parent = clsFortiusAntParent(app_conn)  # The child process has the GUI
        parent.ListenToChild()

        # --------------------------------------------------------------------------
        # Wait for child-process to complete
        # --------------------------------------------------------------------------
        pChild.join()
    # ------------------------------------------------------------------------------
    # We're done
    # ------------------------------------------------------------------------------
    if debug.on(debug.Any):
        logfile.Console('FortiusAnt ended')
