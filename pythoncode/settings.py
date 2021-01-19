#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2021-01-19"
# 2021-01-19    PowerFactor limit changed to 0.5 ... 1.5 (50 ... 150)
# 2021-01-18    help texts defined as 'constants' to be used for commandline.
#               texts in Json file different from variable name
#               unknown variables are reported, but remain present
#               an incorrect json-file is replaced completely when written
# 2021-01-10    self.ant_tacx_models used
# 2021-01-06    First version
#-------------------------------------------------------------------------------
import json
import lib_programname
import os
import sys
import constants
import debug
import logfile

if constants.UseGui:
    import webbrowser
    import wx

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
TitleText       = "FortiusAnt settings"

#-------------------------------------------------------------------------------
# The name of below json_ texts match the clv; the texts are in the JSON file
# If a text changes; old json-files will not match anymore (increment Version)!
#-------------------------------------------------------------------------------
Version                 = '1'                 # Increment when literal changes!!

json_Version            = 'version'

json_General            = 'general'
json_autostart          = 'autostart'
#json_CtrlCommand       = 'CtrlCommand'
json_debug              = 'debug'
json_gui                = 'gui'
json_hrm                = 'hrm'
#json_scs               = 'scs'
json_exportTCX          = 'export TCX-file'

json_Simulation         = 'simulation'
json_manual             = 'manual power'
json_manualGrade        = 'manual grade'
json_Resistance         = 'resistance'
json_simulate           = 'simulate'

json_Bluetooth          = 'bluetooth'
json_ble                = 'enable'

json_Ant                = 'ant'
json_antDeviceID        = 'device ID'

json_Trainer            = 'trainer'
json_PedalStrokeAnalysis= 'pedal stroke analysis'
json_CalibrateRR        = 'calibrate rolling resistance'
json_calibrate          = 'auto calibrate'
json_factor             = 'factor'
json_GradeFactor        = 'grade factor'
json_GradeFactorDH      = 'grade factor downhill'
json_PowerMode          = 'power mode'
json_TacxType           = 'type'
json_Transmission       = 'transmission'

json_Runoff             = 'runoff'
json_RunoffMaxSpeed     = 'max speed'
json_RunoffDip          = 'dip'
json_RunoffMinSpeed     = 'min speed'
json_RunoffTime         = 'time'
json_RunoffPower        = 'power'

# ------------------------------------------------------------------------------
#  J s o n F i l e N a m e
# ------------------------------------------------------------------------------
# input:        Environment where we are running
#
# Description:  Return path of json-file in:
#               # --removed-- location of the started executable OR
#               - the current working directory
#               
# Output:       None
#
# Returns:      Full path to json file
# ------------------------------------------------------------------------------
def JsonFileName():
#    if getattr(sys, 'frozen', False):
#        dirname = os.path.realpath(sys.argv[0]) # the started executable
#        dirname = os.path.dirname(dirname)		 # Remove /filename.exe
#    else:
    dirname = '.'                                # Current directory
    return dirname + '/FortiusAntSettings.json'

def JsonFileExists():
    return os.path.isfile(JsonFileName()) 

# ------------------------------------------------------------------------------
#  R e a d J s o n F i l e
# ------------------------------------------------------------------------------
# input:        Existing jsonfile
#
# Description:  Read jsonfile and set all command line fields
#               'Empty' fields are set to False (unspecified)
#               
# Output:       args, data
#
# Returns:      None
# ------------------------------------------------------------------------------
def ReadJsonFile (args):
    global data
    if debug.on(debug.Function):
        logfile.Write ("ReadJsonFile () ...")
    # --------------------------------------------------------------------------
    # Open json file
    # --------------------------------------------------------------------------
    try:
        jsonFile = open(JsonFileName())
    except:
        if debug.on(debug.Any):
            logfile.Write ("Json file does not exist: " + JsonFileName())
    else:
        # ----------------------------------------------------------------------
        # Read json file
        # ----------------------------------------------------------------------
        try:
            data = json.load(jsonFile)
        except:
            logfile.Console ("Json file cannot be interpreted: " + JsonFileName())
            del data    # Delete, now it is not defined anymore
        else:
            # ------------------------------------------------------------------
            # Handle content AND check for unknown/incorrectly spelled params.
            # ------------------------------------------------------------------
            ActualVersion   = -1
            G               = 0
            R               = 0
            for p in data:
                w = data[p]
                if   p == json_Ant:
                    for q in w:
                        if   q == json_antDeviceID:         args.antDeviceID          = w[q]
                        #'CtrlCommand':                   args.CtrlCommand
                        #'scs':                           args.scs                  = p[q]
                        else: logfile.Console ('Json file contains unknown parameter %s %s' % (p, q))

                elif p == json_Bluetooth:
                    for q in data[json_Bluetooth]:
                        if   q == json_ble:                 args.ble                  = w[q]
                        else: logfile.Console ('Json file contains unknown parameter %s %s' % (p, q))

                elif p == json_General:
                    for q in data[json_General]:
                        if   q == json_autostart:           args.autostart            = w[q]
                        elif q == json_debug:               args.debug                = w[q]
                        elif q == json_gui:                 args.gui                  = w[q]
                        elif q == json_hrm:                 args.hrm                  = w[q]
                        elif q == json_exportTCX:           args.exportTCX            = w[q]
                        else: logfile.Console ('Json file contains unknown parameter %s %s' % (p, q))

                elif p == json_Simulation:
                    for q in data[json_Simulation]:
                        if   q == json_manual:              args.manual               = w[q]
                        elif q == json_manualGrade:         args.manualGrade          = w[q]
                        elif q == json_Resistance:          args.Resistance           = w[q]
                        elif q == json_simulate:            args.simulate             = w[q]
                        else: logfile.Console ('Json file contains unknown parameter %s %s' % (p, q))

                elif p == json_Trainer:
                    for q in data[json_Trainer]:
                        if   q == json_PedalStrokeAnalysis: args.PedalStrokeAnalysis  = w[q]
                        elif q == json_CalibrateRR:         args.CalibrateRR          = w[q]
                        elif q == json_antDeviceID:         args.antDeviceID          = w[q]
                        elif q == json_GradeFactor:         G += 1
                        elif q == json_GradeFactorDH:       G += 1
                        elif q == json_calibrate:           args.calibrate            = w[q]
                        elif q == json_factor:              args.factor               = w[q]
                        elif q == json_PowerMode:           args.PowerMode            = w[q]
                        elif q == json_TacxType:            args.TacxType             = w[q]
                        elif q == json_Transmission:        args.Transmission         = w[q]
                        elif q == json_Runoff:
                            for r in w[q]:
                                if   r == json_RunoffMaxSpeed: R += 1
                                elif r == json_RunoffDip:      R += 1
                                elif r == json_RunoffMinSpeed: R += 1
                                elif r == json_RunoffTime:     R += 1
                                elif r == json_RunoffPower:    R += 1
                                else: logfile.Console ('Json file contains unknown parameter %s %s %s' % (p, q, r))
                        else: logfile.Console ('Json file contains unknown parameter %s %s' % (p, q))

                elif p == json_Version:
                    ActualVersion = data[json_Version]

                else:
                    logfile.Console ('Json file contains unknown parameter %s' % (p))

            # ------------------------------------------------------------------
            # Correct values, to be compatibel with command-line
            # ------------------------------------------------------------------
            if args.debug       == '':    args.debug        = False
            if args.antDeviceID == '':    args.antDeviceID  = False
            if args.factor      == '100': args.factor       = False
            if args.TacxType    == '':    args.TacxType     = False

            # ------------------------------------------------------------------
            # Warn for (possibly) incompatible json-file
            # ------------------------------------------------------------------
            if ActualVersion != Version:
                logfile.Console('JSON file has old format (%s=%s expected %s), not all parameters may be recognized.' % \
                    (json_Version, ActualVersion, Version))

            # ------------------------------------------------------------------
            # From the json-file ALL parts for -G and -R are expected
            # just to reduce complexity to compose partially defined sets
            # ------------------------------------------------------------------
            if G == 2:
                p = data[json_Trainer]
                GradeFactor   = p[json_GradeFactor]
                GradeFactorDH = p[json_GradeFactorDH]
                if GradeFactor == '100' and GradeFactorDH == '100':
                    args.GradeAdjust = False
                else:
                    args.GradeAdjust = "%s/%s" % (GradeFactor, GradeFactorDH)

            if R == 5:
                w = data[json_Trainer][json_Runoff]
                RunoffMaxSpeed = w[json_RunoffMaxSpeed]
                RunoffDip      = w[json_RunoffDip]
                RunoffMinSpeed = w[json_RunoffMinSpeed]
                RunoffTime     = w[json_RunoffTime]
                RunoffPower    = w[json_RunoffPower]
                if RunoffMaxSpeed == '40' and RunoffDip == '2' and RunoffMinSpeed == '1' \
                    and RunoffTime == '7.0' and RunoffPower == '100':
                    args.Runoff = False
                else:
                    args.Runoff = "%s/%s/%s/%s/%s" % (RunoffMaxSpeed, RunoffDip, RunoffMinSpeed, RunoffTime, RunoffPower)
        # ----------------------------------------------------------------------
        # Close json file
        # ----------------------------------------------------------------------
        if debug.on(debug.Function):
            logfile.Write   ("... completed")

        jsonFile.close

    # --------------------------------------------------------------------------
    # Done
    # --------------------------------------------------------------------------
    if debug.on(debug.Function):
        logfile.Write ("... completed")

if constants.UseGui:
    # ------------------------------------------------------------------------------
    #  O p e n D i a l o g
    # ------------------------------------------------------------------------------
    # input:        Current command line variables
    #
    # Description:  Display dialog box to define all command-line paramaters
    #               interactively
    #               
    # Output:       When OK is pressed:
    #               - a json file is created with all settings
    #               - all command line parameters are adjusted accordingly
    #               When significant parameters are changed, True is returned
    #
    # Returns:      True/False indicating whether program must be restarted
    #               None = cancel pressed,nothing changed
    # ------------------------------------------------------------------------------
    def OpenDialog(app, parent=None, pclv=None):
        global RestartApplication, clv

        RestartApplication  = None # Cancel pressed, nothing done
        clv                 = pclv
        
        dlg = dlgFortiusAntSettings(parent)
        if parent:
            dlg.SetPosition((parent.Position[0] + parent.Speed.Position[0], \
                            parent.Position[1] + parent.Speed.Position[1] + 32))
        dlg.ShowModal()
        dlg.Destroy()

        if debug.on(debug.Function):
            logfile.Write ('settings.OpenDialog returns restart=%s debug=%s' % (RestartApplication, clv.debug))

        return RestartApplication, clv

    # ------------------------------------------------------------------------------
    #  W r i t e J s o n F i l e
    # ------------------------------------------------------------------------------
    # input:        Dialogue window
    #               Current command line variables
    #               clv, data
    #
    # Description:  Store data from dialogue box into Json file
    #               
    # Output:       json-file
    #               data
    #
    # Returns:      None
    # ------------------------------------------------------------------------------
    def WriteJsonFile (DialogWindow):
        global clv, data
        if debug.on(debug.Function):
            logfile.Write ("WriteJsonFile () ...")

        # --------------------------------------------------------------------------
        # If data was read from Json before, overwrite add / but do not replace!
        # --------------------------------------------------------------------------
        try:
            _d = data               # Check that data exists
        except:
            data = {}               # If not, cause re-initialization

        # --------------------------------------------------------------------------
        # Add/replace data
        # --------------------------------------------------------------------------
        data[json_Version] = Version

        data[json_General] = {
            json_autostart:             DialogWindow.cb_a   .GetValue(),
            #'CtrlCommand':             DialogWindow.na_C   .GetValue(),
            json_debug:                 DialogWindow.txt_d  .GetValue(),
            json_gui:                   DialogWindow.cb_g   .GetValue(),
            json_hrm:                   DialogWindow.txt_H  .GetValue(),
            #'scs':                     DialogWindow.txt_S  .GetValue(),
            json_exportTCX:             DialogWindow.cb_x   .GetValue(),
        }

        data[json_Simulation] = {
            json_manual:                DialogWindow.cb_m   .GetValue(),
            json_manualGrade:           DialogWindow.cb_M   .GetValue(),
            json_Resistance:            DialogWindow.cb_r   .GetValue(),
            json_simulate:              DialogWindow.cb_s   .GetValue(),
        }

        data[json_Bluetooth] = {
            json_ble:                   DialogWindow.cb_b   .GetValue(),
        }

        data[json_Ant] = {
            json_antDeviceID:           DialogWindow.txt_D  .GetValue(),
        }

        data[json_Trainer] = {
            json_PedalStrokeAnalysis:   DialogWindow.cb_A   .GetValue(),
            json_CalibrateRR:           DialogWindow.txt_c  .GetValue(),
            json_calibrate:         not DialogWindow.cb_n   .GetValue(),
            json_factor:                DialogWindow.txt_p  .GetValue(),
            json_GradeFactor:           DialogWindow.txt_G1 .GetValue(),
            json_GradeFactorDH:         DialogWindow.txt_G2 .GetValue(),
            json_PowerMode:             DialogWindow.cb_P   .GetValue(),
            json_TacxType:              DialogWindow.combo_t.GetValue(),
            json_Transmission:          clv.Transmission,   # Not defined in user-interface
            json_Runoff: {
                json_RunoffMaxSpeed:    DialogWindow.txt_R1 .GetValue(),
                json_RunoffDip:         DialogWindow.txt_R2 .GetValue(),
                json_RunoffMinSpeed:    DialogWindow.txt_R3 .GetValue(),
                json_RunoffTime:        DialogWindow.txt_R4 .GetValue(),
                json_RunoffPower:       DialogWindow.txt_R5 .GetValue()
            }
        }

        # --------------------------------------------------------------------------
        # Write json file
        # --------------------------------------------------------------------------
        try:
            jsonFile = open(JsonFileName(),"w")
        except:
            logfile.Console ("Json file cannot be written: " + JsonFileName())
        else:
            json.dump(data, jsonFile, sort_keys=True, indent=4)
            jsonFile.close

        if debug.on(debug.Function):
            logfile.Write ("... completed")

    # ------------------------------------------------------------------------------
    # U S E R   I N T E R F A C E   S T A N D A R D   F U N C T I O N S
    # ------------------------------------------------------------------------------
    # U n d e r
    # ------------------------------------------------------------------------------
    # input:        existing control
    #               Yoffset = number of pixels of space between the two controls
    #
    # Description:  Return position for a new control,
    #               Yoffset (optional) under the provided control
    #               
    # Returns:      Position
    # ------------------------------------------------------------------------------
    def Under(control, Yoffset = 1):
        return (control.Position[0], control.Position[1] + control.Size[1] + Yoffset)

    # ------------------------------------------------------------------------------
    # R i g h t O f
    # ------------------------------------------------------------------------------
    # input:        existing control
    #               Xoffset, Yoffset = number of pixels of space between the two controls
    #
    # Description:  Return position for a new control,
    #               Xoffset (optional) to the right of the provided control
    #               Since a StaticText is smaller than a TextCtrl,
    #                   the new control is moved Yoffset down (by default)
    #               
    # Returns:      Position
    # ------------------------------------------------------------------------------
    def RightOf(control, Xoffset = 5, Yoffset = 2):
        return (control.Position[0] + control.Size[0] + Xoffset, control.Position[1] + Yoffset)

    # ------------------------------------------------------------------------------
    # E V T _ C H A R _ u i n t
    # ------------------------------------------------------------------------------
    # input:        CHAR event on an TextCtrl (some character entered)
    #
    # Description:  Allow 'unsigned integer' input only
    #               
    # Returns:      Nothing, but illegal entry is blocked
    # ------------------------------------------------------------------------------
    def EVT_CHAR_uint(event):
        key_code = event.GetKeyCode()

        # Allow ASCII numerics
        # Allow tabs, for tab navigation between TextCtrls
        # Delete, Backspace, Left, Right
        if ord('0') <= key_code <= ord('9') \
        or key_code == ord('\t') \
        or key_code in (8, 127, 314, 316):
            event.Skip()  # Accept this CHAR for default processing
        else:
            pass          # No event.Skip blocks everything else

        return

    # ------------------------------------------------------------------------------
    # E V T _ K I L L _ F O C U S _ i n t _ r a n g e
    # ------------------------------------------------------------------------------
    # input:        KILL_FOCUS event on an TextCtrl (field is left)
    #               VoidAllowed: False:
    #
    # Description:  Check whether the field is in provided range
    #               
    # Returns:      KILL_FOCUS is always allowed
    #               The control can be adjusted when outside range
    #
    # Note:         When a field is outside the range and only entered and left
    #               the field is adjusted, even when original is empty.
    # ------------------------------------------------------------------------------
    def EVT_KILL_FOCUS_int_range(control, event, MinValue, MaxValue, VoidValue=0):
        if control.GetValue() == '':
            control.SetValue(str(VoidValue))
        else:
            i = 0
            try:
                i = int(control.GetValue())
            except:
                pass
            i = max(MinValue, i)
            i = min(MaxValue, i)
            control.SetValue(str(i))
        event.Skip()

    # ------------------------------------------------------------------------------
    # E V T _ C H A R _ f l o a t
    # ------------------------------------------------------------------------------
    # input:        CHAR event on an TextCtrl (some character entered)
    #
    # Description:  Allow 'unsigned float' input only
    #               
    # Returns:      Nothing, but illegal entry is blocked
    #
    # Note:         multiple dots allowed, no decimal point is comma, no hyphen
    # ------------------------------------------------------------------------------
    def EVT_CHAR_ufloat(event):
        key_code = event.GetKeyCode()

        # Allow ASCII numerics
        # Allow tabs, for tab navigation between TextCtrls
        # Delete, Backspace, Left, Right
        # Allow decimal points
        if ord('0') <= key_code <= ord('9') \
        or key_code == ord('\t') \
        or key_code in (8, 127, 314, 316) \
        or key_code == ord('.'):
            event.Skip()  # Accept this CHAR for default processing
        else:
            pass          # No event.Skip blocks everything else
        return

    def EVT_KILL_FOCUS_float_range(control, event, MinValue, MaxValue):
        i = 0
        try:
            i = float(control.GetValue())
        except:
            pass
        i = max(MinValue, i)
        i = min(MaxValue, i)
        control.SetValue(str(i))
        event.Skip()

    class dlgFortiusAntSettings(wx.Dialog):
        # --------------------------------------------------------------------------
        # _ _ i n i t _ _
        # --------------------------------------------------------------------------
        # input:        None
        #
        # Description:  Create dialgue and all the controls
        #
        # Output:       None
        # --------------------------------------------------------------------------
        def __init__(self, parent):
            wx.Dialog.__init__(self, parent, -1, TitleText, size=(1000, 1000))
            panel = wx.Panel(self)

            ButtonW         = 80
            EntryBg         = wx.Colour(255,255,255) # Background colour [for entry-fields]
            EntrySizeY      = 20                     # Somewhat smaller than default
            Margin          = 4                      # Space at top/left side in dialog
            GroupLabelFont  = wx.Font(-1, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD)

            # ----------------------------------------------------------------------
            # BASIC 
            # ----------------------------------------------------------------------
            l = "Basic arguments:"
            s = (-1, -1)
            p = (Margin * 2, Margin * 2)
            self.lblBasic = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)
            self.lblBasic.SetFont(GroupLabelFont)

            l = constants.help_a + " (-a *)"
            s = (-1, -1)
            p = Under(self.lblBasic)
            self.cb_a = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_a.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_a)
            
            l = constants.help_b + " (-b *)"
            s = (-1, -1)
            p = Under(self.cb_a)
            self.cb_b = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_b.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_b)
            
            l = constants.help_g + " (-g *)"
            s = (-1, -1)
            p = Under(self.cb_b)
            self.cb_g = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_g.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_g)
            
            v = ""
            s = (-1, -1)
            p = Under(self.cb_g)
            c = clv.ant_tacx_models
            if True:                # Required?? platform.system() in [ 'Windows' ]:
                self.combo_t = wx.ComboBox(panel, id=wx.ID_ANY, value=v, pos=p, size=s, choices=c, style=0, validator=wx.DefaultValidator, name=wx.ComboBoxNameStr)
                self.combo_t.Bind(wx.EVT_COMBOBOX, self.EVT_COMBOBOX_combo_t)
            else:
                self.combo_t = wx.ListBox(panel, id=wx.ID_ANY, pos=p, size=s, choices=c, style=0, validator=wx.DefaultValidator, name=wx.ListBoxNameStr)
                self.combo_t.Bind(wx.EVT_LISTBOX, self.EVT_COMBOBOX_combo_t)

            l = constants.help_t + " (-t *)"
            s = (-1, -1)
            p = RightOf(self.combo_t)
            self.lbl_t = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)
            
            # ----------------------------------------------------------------------
            # POWER CURVE
            # ----------------------------------------------------------------------
            l = "Power curve adjustment:"
            s = (-1, -1)
            p = Under(self.combo_t, 15)
            self.lblPower = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=wx.BOLD, name=wx.StaticTextNameStr)
            self.lblPower.SetFont(GroupLabelFont)

            s = (65, EntrySizeY)
            p = Under(self.lblPower)
            self.txt_c = wx.TextCtrl(panel, value='', pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_c.SetBackgroundColour(EntryBg)
            self.txt_c.Bind(wx.EVT_CHAR, EVT_CHAR_ufloat)

            l = constants.help_c + " (-c)"
            s = (-1, -1)
            p = RightOf(self.txt_c)
            self.lbl_c = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)

            s = (30, EntrySizeY)
            p = Under(self.txt_c)
            self.txt_G1 = wx.TextCtrl(panel, value='', pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_G1.SetBackgroundColour(EntryBg)
            self.txt_G1.Bind(wx.EVT_CHAR, EVT_CHAR_uint)
            self.txt_G1.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_G1)

            s = (30, EntrySizeY)
            p = RightOf(self.txt_G1, Yoffset = 0)
            self.txt_G2 = wx.TextCtrl(panel, value='', pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_G2.SetBackgroundColour(EntryBg)
            self.txt_G2.Bind(wx.EVT_CHAR, EVT_CHAR_uint)
            self.txt_G2.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_G2)

            l = constants.help_G + " (-G)"
            s = (-1, -1)
            p = RightOf(self.txt_G2)
            self.lbl_G = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)

            s = (65, -1)
            p = Under(self.txt_G1)
            self.txt_p = wx.TextCtrl(panel, value='', pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_p.SetBackgroundColour(EntryBg)
            self.txt_p.Bind(wx.EVT_CHAR, EVT_CHAR_uint)
            self.txt_p.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_p)

            l = constants.help_p + " (-p)"
            s = (-1, -1)
            p = RightOf(self.txt_p)
            self.lbl_p = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)

            # ----------------------------------------------------------------------
            # ADVANCED 
            # ----------------------------------------------------------------------
            l = "Advanced arguments:"
            s = (-1, -1)
            p = Under(self.txt_p, 15)
            self.lblAdvanced = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=wx.BOLD, name=wx.StaticTextNameStr)
            self.lblAdvanced.SetFont(GroupLabelFont)

            l = constants.help_A + " (-A *)"
            s = (-1, -1)
            p = Under(self.lblAdvanced)
            self.cb_A = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_A.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_A)
            
            v = ""
            s = (50, EntrySizeY)
            p = Under(self.cb_A)
            self.txt_D = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_D.SetBackgroundColour(EntryBg)
            self.txt_D.Bind(wx.EVT_CHAR, self.EVT_CHAR_txt_D)

            l = constants.help_D + " (-D *)"
            s = (-1, -1)
            p = RightOf(self.txt_D)
            self.lbl_D = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)

            v = ""
            s = (50, EntrySizeY)
            p = Under(self.txt_D)
            self.txt_H = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_H.SetBackgroundColour(EntryBg)
            self.txt_H.Bind(wx.EVT_CHAR, self.EVT_CHAR_txt_H)

            l = constants.help_H + " (-H *)"
            s = (-1, -1)
            p = RightOf(self.txt_H)
            self.lbl_H = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)

            l = constants.help_m + " (-m)"
            s = (-1, -1)
            p = Under(self.txt_H)
            self.cb_m = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_m.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_m)
            
            l = constants.help_M + " (-M)"
            s = (-1, -1)
            p = Under(self.cb_m)
            self.cb_M = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_M.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_M)

            l = constants.help_n + " (-n)"
            s = (-1, -1)
            p = Under(self.cb_M)
            self.cb_n = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)

            l = constants.help_P + " (-P)"
            s = (-1, -1)
            p = Under(self.cb_n)
            self.cb_P = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)

            v = ""
            s = (30, EntrySizeY)
            p = Under(self.cb_P)
            self.txt_R1 = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_R1.SetBackgroundColour(EntryBg)
            self.txt_R1.Bind(wx.EVT_CHAR, EVT_CHAR_uint)
            self.txt_R1.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_R1)

            v = ""
            s = (30, EntrySizeY)
            p = RightOf(self.txt_R1, Yoffset = 0)
            self.txt_R2 = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_R2.SetBackgroundColour(EntryBg)
            self.txt_R2.Bind(wx.EVT_CHAR, EVT_CHAR_uint)
            self.txt_R2.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_R2)

            v = ""
            s = (30, EntrySizeY)
            p = RightOf(self.txt_R2, Yoffset = 0)
            self.txt_R3 = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_R3.SetBackgroundColour(EntryBg)
            self.txt_R3.Bind(wx.EVT_CHAR, EVT_CHAR_uint)
            self.txt_R3.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_R3)

            v = ""
            s = (30, EntrySizeY)
            p = RightOf(self.txt_R3, Yoffset = 0)
            self.txt_R4 = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_R4.SetBackgroundColour(EntryBg)
            self.txt_R4.Bind(wx.EVT_CHAR, EVT_CHAR_ufloat)
            self.txt_R4.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_R4)

            v = ""
            s = (30, EntrySizeY)
            p = RightOf(self.txt_R4, Yoffset = 0)
            self.txt_R5 = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_R5.SetBackgroundColour(EntryBg)
            self.txt_R5.Bind(wx.EVT_CHAR, EVT_CHAR_uint)
            self.txt_R5.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_R5)

            l = constants.help_R + " (-R)"
            s = (-1, -1)
            p = RightOf(self.txt_R5)
            self.lbl_R = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)

            l = constants.help_x + " (-x)"
            s = (-1, -1)
            p = Under(self.txt_R1)
            self.cb_x = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)

            # ----------------------------------------------------------------------
            # DEVELOPER 
            # ----------------------------------------------------------------------
            l = "Developer arguments:"
            s = (-1, -1)
            p = Under(self.cb_x, 15)
            self.lblDeveloper = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=wx.BOLD, name=wx.StaticTextNameStr)
            self.lblDeveloper.SetFont(GroupLabelFont)

            v = ""
            s = (30, EntrySizeY)
            p = Under(self.lblDeveloper)
            self.txt_d = wx.TextCtrl(panel, value=v, pos=p, size=s, style=wx.TE_RIGHT)
            self.txt_d.SetBackgroundColour(EntryBg)
            self.txt_d.Bind(wx.EVT_CHAR, self.EVT_CHAR_txt_d)
            self.txt_d.Bind(wx.EVT_KILL_FOCUS, self.EVT_KILL_FOCUS_txt_d)

            l = constants.help_d + " (-d *)"
            s = (-1, -1)
            p = RightOf(self.txt_d)
            self.lbl_d = wx.StaticText(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, name=wx.StaticTextNameStr)

            #s = (-1, -1)
            #p = RightOf(self.lbl_d)
            #c = ['1 = Application', '2 = Function', '4 = ANT-interface', '8 = USBtrainer', '16 = MultiProcessing', '32 = Create Json file', '64 = Bluetooth']
            #self.combo_d = wx.ListBox(panel, id=wx.ID_ANY, pos=p, size=s, choices=c, style=wx.LB_MULTIPLE, validator=wx.DefaultValidator, name=wx.ListBoxNameStr)

            l = "Application"
            s = (-1, -1)
            p = RightOf(self.lbl_d, Yoffset = 0)
            self.cb_d1 = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_d1.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_d)

            l = "Function"
            s = (-1, -1)
            p = RightOf(self.cb_d1, Yoffset = 0)
            self.cb_d2 = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_d2.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_d)

            l = "ANT-interface"
            s = (-1, -1)
            p = RightOf(self.cb_d2, Yoffset = 0)
            self.cb_d4 = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_d4.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_d)

            l = "USB-interface"
            s = (-1, -1)
            p = RightOf(self.cb_d4, Yoffset = 0)
            self.cb_d8 = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_d8.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_d)

            l = "MultiProcessing"
            s = (-1, -1)
            p = RightOf(self.cb_d8, Yoffset = 0)
            self.cb_d16 = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_d16.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_d)

            l = "Json"
            s = (-1, -1)
            p = RightOf(self.cb_d16, Yoffset = 0)
            self.cb_d32 = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_d32.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_d)

            l = "Bluetooth"
            s = (-1, -1)
            p = RightOf(self.cb_d32, Yoffset = 0)
            self.cb_d64 = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_d64.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_d)

            l = constants.help_r + " (-r)"
            s = (-1, -1)
            p = Under(self.txt_d)
            self.cb_r = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            
            l = constants.help_s + " (-s *)"
            s = (-1, -1)
            p = Under(self.cb_r)
            self.cb_s = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_s.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_s)

            # ----------------------------------------------------------------------
            # Closure: OK, Cancel, Help
            # ----------------------------------------------------------------------
            l = "*) Restart FortiusANT to effectuate settings"
            s = (-1, -1)
            p = Under(self.cb_s)
            self.cb_restart = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)
            self.cb_restart.Bind(wx.EVT_CHECKBOX, self.EVT_CHECKBOX_cb_restart)

            l = "Save settings in JSON file"
            s = (-1, -1)
            p = Under(self.cb_restart)
            self.cb_saveJson = wx.CheckBox(panel, id=wx.ID_ANY, label=l, pos=p, size=s, style=0, validator=wx.DefaultValidator, name=wx.CheckBoxNameStr)

            l = "OK"
            s = (ButtonW, -1)
            p = Under(self.cb_saveJson, 15)
            self.btnOK = wx.Button(panel, label=l, pos=p, size=s)
            self.btnOK.Bind(wx.EVT_BUTTON, self.EVT_BUTTON_btnOK)

            l = "Cancel"
            s = (ButtonW, -1)
            p = RightOf(self.btnOK, Yoffset = 0)
            self.btnCancel = wx.Button(panel, label=l, pos=p, size=s)
            self.btnCancel.Bind(wx.EVT_BUTTON, self.EVT_BUTTON_btnCancel)
            
            l = "Help"
            s = (ButtonW, -1)
            p = RightOf(self.btnCancel, Yoffset = 0)
            self.btnHelp = wx.Button(panel, label=l, pos=p, size=s)
            self.btnHelp.Bind(wx.EVT_BUTTON, self.EVT_BUTTON_btnHelp)
            
            # ----------------------------------------------------------------------
            # Move buttons right/bottom under the rightmost control
            # ----------------------------------------------------------------------
            moveRight =  (self.cb_d64. Position[0] + self.cb_d64. Size[0]) - \
                        (self.btnHelp.Position[0] + self.btnHelp.Size[0])
            self.cb_restart. SetPosition((self.cb_restart. Position[0] + moveRight, self.cb_restart. Position[1]))
            self.cb_saveJson.SetPosition((self.cb_saveJson.Position[0] + moveRight, self.cb_saveJson.Position[1]))
            self.btnOK.      SetPosition((self.btnOK.      Position[0] + moveRight, self.btnOK.      Position[1]))
            self.btnCancel.  SetPosition((self.btnCancel.  Position[0] + moveRight, self.btnCancel.  Position[1]))
            self.btnHelp.    SetPosition((self.btnHelp.    Position[0] + moveRight, self.btnHelp.    Position[1]))

            # ----------------------------------------------------------------------
            # No changes as default button
            # ----------------------------------------------------------------------
            self.btnCancel.SetFocus()

            # ----------------------------------------------------------------------
            # Resize frame to controls
            # +40 +50 added; I do not know why that is required
            # ----------------------------------------------------------------------
            self.SetSize((self.btnHelp.Position[0] + self.btnHelp.Size[0] + Margin * 2 + 40, \
                        self.btnHelp.Position[1] + self.btnHelp.Size[1] + Margin * 2 + 50
                        ))

            # ----------------------------------------------------------------------
            # Set existing values (clv --> dialog)
            # ----------------------------------------------------------------------
            self.cb_restart. SetValue(False)
            self.cb_saveJson.SetValue(JsonFileExists())

            if clv:
                self.cb_a   .SetValue(clv.autostart)
                self.cb_A   .SetValue(clv.PedalStrokeAnalysis)
                self.cb_b   .SetValue(clv.ble)
                self.txt_d  .SetValue(str(clv.debug))
                self.EVT_KILL_FOCUS_txt_d()
                self.cb_g   .SetValue(clv.gui)
                self.txt_G1 .SetValue(str(int(clv.GradeFactor   * 100)))
                self.txt_G2 .SetValue(str(int(clv.GradeFactorDH * 100)))
            #self.txt_G3 .SetValue(clv.GradeShiftGradeShift)
                self.cb_m   .SetValue(clv.manual)
                self.cb_M   .SetValue(clv.manualGrade)
                self.cb_n   .SetValue(not clv.calibrate)
                self.txt_p  .SetValue(str(int(clv.PowerFactor * 100)))
                self.cb_P   .SetValue(clv.PowerMode)
                self.cb_r   .SetValue(clv.Resistance)
                self.txt_R1 .SetValue(str(int(clv.RunoffMaxSpeed)))
                self.txt_R2 .SetValue(str(int(clv.RunoffDip)))
                self.txt_R3 .SetValue(str(int(clv.RunoffMinSpeed)))
                self.txt_R4 .SetValue(str(float(clv.RunoffTime)))
                self.txt_R5 .SetValue(str(int(clv.RunoffPower)))
                self.cb_s   .SetValue(clv.SimulateTrainer)
            #self.txt_S  .SetValue(clv.scs)
                self.cb_x   .SetValue(clv.exportTCX)

                if clv.antDeviceID:     self.txt_D  .SetValue(str(clv.antDeviceID))
                if clv.hrm:             self.txt_H  .SetValue(str(clv.hrm))
                if clv.CalibrateRR:     self.txt_c  .SetValue(str(float(clv.CalibrateRR)))
                if clv.TacxType:        self.combo_t.SetValue(str(clv.TacxType))

                if not clv.args.debug:  self.txt_d  .SetValue('')   # make difference between 0 and not-specified

        # --------------------------------------------------------------------------
        # E V E N T   H A N D L E R S
        # --------------------------------------------------------------------------
        # Checkbox -a
        # --------------------------------------------------------------------------
        def EVT_CHECKBOX_cb_a (self, event):
            self.cb_restart.SetValue(True)
            
        # --------------------------------------------------------------------------
        # Checkbox -A
        # --------------------------------------------------------------------------
        def EVT_CHECKBOX_cb_A (self, event):
            self.cb_restart.SetValue(True)
            
        # --------------------------------------------------------------------------
        # Checkbox -b
        # --------------------------------------------------------------------------
        def EVT_CHECKBOX_cb_b (self, event):
            self.cb_restart.SetValue(True)
            
        # --------------------------------------------------------------------------
        # Checkbox -d
        # --------------------------------------------------------------------------
        def EVT_CHAR_txt_d (self, event):
            EVT_CHAR_uint(event)

        def EVT_CHECKBOX_cb_d (self, event):
            i = 0
            i |= self.cb_d1. GetValue() *  1
            i |= self.cb_d2. GetValue() *  2
            i |= self.cb_d4. GetValue() *  4
            i |= self.cb_d8. GetValue() *  8
            i |= self.cb_d16.GetValue() * 16
            i |= self.cb_d32.GetValue() * 32
            i |= self.cb_d64.GetValue() * 64
            self.txt_d.SetValue(str(i))

            if clv.debug == 0 and i != 0: self.cb_restart.SetValue(True)

        def EVT_KILL_FOCUS_txt_d (self, event=None):
            if event: EVT_KILL_FOCUS_int_range(self.txt_d, event, 0, 127, '')
            try:
                i = int(self.txt_d.GetValue())
            except:
                i = 0
            self.cb_d1. SetValue(i & 1 )
            self.cb_d2. SetValue(i & 2 )
            self.cb_d4. SetValue(i & 4 )
            self.cb_d8. SetValue(i & 8 )
            self.cb_d16.SetValue(i & 16)
            self.cb_d32.SetValue(i & 32)
            self.cb_d64.SetValue(i & 64)

            if clv.debug == 0 and i != 0: self.cb_restart.SetValue(True)

        # --------------------------------------------------------------------------
        # Checkbox -D
        # --------------------------------------------------------------------------
        def EVT_CHAR_txt_D (self, event):
            self.cb_restart.SetValue(True)
            EVT_CHAR_uint(event)
            
        # --------------------------------------------------------------------------
        # Checkbox -g
        # --------------------------------------------------------------------------
        def EVT_CHECKBOX_cb_g (self, event):
            self.cb_restart.SetValue(True)
            msg = 'Are you sure you want to restart without Graphical User Interface?'
            if  self.cb_g.GetValue() == False and \
                wx.MessageBox(msg, TitleText, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.NO:
                self.cb_g.SetValue(True)
                
        # --------------------------------------------------------------------------
        # Checkbox -G
        # --------------------------------------------------------------------------
        def EVT_KILL_FOCUS_txt_G1 (self, event):
            EVT_KILL_FOCUS_int_range(self.txt_G1, event, 0, 100, 100)

        def EVT_KILL_FOCUS_txt_G2 (self, event):
            EVT_KILL_FOCUS_int_range(self.txt_G2, event, 0, 100, 100)
            
        # --------------------------------------------------------------------------
        # Checkbox -H
        # --------------------------------------------------------------------------
        def EVT_CHAR_txt_H (self, event):
            self.cb_restart.SetValue(True)
            EVT_CHAR_uint(event)
            
        # --------------------------------------------------------------------------
        # Checkbox -m -M
        # --------------------------------------------------------------------------
        def EVT_CHECKBOX_cb_m (self, event):
            if  self.cb_m.GetValue():
                self.cb_M.SetValue(False)
                self.cb_x.SetValue(True)
                
        def EVT_CHECKBOX_cb_M (self, event):
            if  self.cb_M.GetValue():
                self.cb_m.SetValue(False)
                self.cb_x.SetValue(True)
                
        # --------------------------------------------------------------------------
        # Checkbox -p
        # --------------------------------------------------------------------------
        def EVT_KILL_FOCUS_txt_p (self, event):
            EVT_KILL_FOCUS_int_range(self.txt_p, event, 50, 150, 100)
            
        # --------------------------------------------------------------------------
        # Checkbox -R
        # --------------------------------------------------------------------------
        def EVT_KILL_FOCUS_txt_R1 (self, event):
            EVT_KILL_FOCUS_int_range(self.txt_R1, event, 20,  50)

        def EVT_KILL_FOCUS_txt_R2 (self, event):
            EVT_KILL_FOCUS_int_range(self.txt_R2, event,  0,   5)

        def EVT_KILL_FOCUS_txt_R3 (self, event):
            EVT_KILL_FOCUS_int_range(self.txt_R3, event,  0,  10)

        def EVT_KILL_FOCUS_txt_R4 (self, event):
            EVT_KILL_FOCUS_float_range(self.txt_R4, event,  0,  10)

        def EVT_KILL_FOCUS_txt_R5 (self, event):
            EVT_KILL_FOCUS_int_range(self.txt_R5, event,  0, 500)
            
        # --------------------------------------------------------------------------
        # Checkbox -s
        # --------------------------------------------------------------------------
        def EVT_CHECKBOX_cb_s (self, event):
            self.cb_restart.SetValue(True)

        # --------------------------------------------------------------------------
        # Checkbox -t
        # --------------------------------------------------------------------------
        def EVT_COMBOBOX_combo_t (self, event):
            self.cb_restart.SetValue(True)

        # --------------------------------------------------------------------------
        # Checkbox -restart
        # --------------------------------------------------------------------------
        def EVT_CHECKBOX_cb_restart (self, event):
            msg = 'Some settings will be activated the next time that you start FortiusAnt!'
            if  self.cb_restart.GetValue() == False and \
                wx.MessageBox(msg, TitleText, wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION) == wx.CANCEL:
                self.cb_restart.SetValue(True)
                
        # --------------------------------------------------------------------------
        # Button OK: save settings in JSON file and close dialog
        # --------------------------------------------------------------------------
        def EVT_BUTTON_btnOK (self, event):
            global RestartApplication, clv
            # ----------------------------------------------------------------------
            # Restart FortiusAnt if requested
            # ----------------------------------------------------------------------
            RestartApplication = self.cb_restart.GetValue()

            # ----------------------------------------------------------------------
            # Set command-line variables
            # ----------------------------------------------------------------------
            clv.GradeFactor     = int(  self.txt_G1 .GetValue()) / 100
            clv.GradeFactorDH   = int(  self.txt_G2 .GetValue()) / 100
            # clv.GradeShift
            clv.manual          =       self.cb_m   .GetValue()
            clv.manualGrade     =       self.cb_M   .GetValue()
            clv.calibrate       = not   self.cb_n   .GetValue()
            clv.PowerFactor     = int(  self.txt_p  .GetValue()) / 100
            clv.PowerMode       =       self.cb_P   .GetValue()
            clv.Resistance      =       self.cb_r   .GetValue()
            clv.RunoffMaxSpeed  = int(  self.txt_R1 .GetValue())
            clv.RunoffDip       = int(  self.txt_R2 .GetValue())
            clv.RunoffMinSpeed  = int(  self.txt_R3 .GetValue())
            clv.RunoffTime      = float(self.txt_R4 .GetValue())
            clv.RunoffPower     = int(  self.txt_R5 .GetValue())
            clv.SimulateTrainer =       self.cb_s   .GetValue()
            #clv.scs
            clv.exportTCX       =       self.cb_x   .GetValue()

            if self.txt_c.GetValue() == '':
                clv.CalibrateRR = False
            else:
                clv.CalibrateRR = float(self.txt_c  .GetValue())

            # ----------------------------------------------------------------------
            # To change the following parameters, the application must be restarted
            # This is an inconstent state untill the application is restarted,
            #   which is most likely not an issue.
            # ----------------------------------------------------------------------
            if RestartApplication:
                clv.autostart           = self.cb_a.GetValue()
                clv.PedalStrokeAnalysis = self.cb_A.GetValue()
                clv.ble                 = self.cb_b.GetValue()
                clv.gui                 = self.cb_g.GetValue()

                if self.txt_d.GetValue() == '':
                    clv.debug           = 0
                else:
                    clv.debug           = int(self.txt_d.GetValue())

                if self.txt_D.GetValue() == '':
                    clv.antDeviceID     = None
                else:
                    clv.antDeviceID     = int(self.txt_D.GetValue())

                if self.txt_H.GetValue() == '':
                    clv.hrm             = None
                else:
                    clv.hrm             = int(self.txt_H.GetValue())

                if self.combo_t.GetValue() == '':
                    clv.TacxType        = False
                else:
                    clv.TacxType        = self.combo_t.GetValue()

            # ----------------------------------------------------------------------
            # Store values in json file
            # ----------------------------------------------------------------------
            if self.cb_saveJson.GetValue():
                WriteJsonFile (self)

            # ----------------------------------------------------------------------
            # Done
            # ----------------------------------------------------------------------
            self.Close()                              # Close dialog box

        # --------------------------------------------------------------------------
        # Button Cancel: close dialog without further actions
        # --------------------------------------------------------------------------
        def EVT_BUTTON_btnCancel (self, event):
            self.Close()                              # Close dialog box

        # --------------------------------------------------------------------------
        # Button Help: open manual from github
        # --------------------------------------------------------------------------
        def EVT_BUTTON_btnHelp (self, event):
            webbrowser.open_new_tab('https://github.com/WouterJD/FortiusANT/blob/master/doc/FortiusANTUserManual.pdf')

# ------------------------------------------------------------------------------
# our normal wxApp-derived class, as usual
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    class clsData:
	    pass

    args = clsData
    ReadJsonFile(args)
    for i in dir(args):
        if not callable(getattr(args, i)) and not i.startswith("__"):
            print ("%s=%s" % (i, getattr(args, i) ) )