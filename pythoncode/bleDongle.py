#---------------------------------------------------------------------------
# Version info
#---------------------------------------------------------------------------
__version__ = "2020-12-18"
# 2020-12-18        First version, obtained from @MarcoVeeneman
#---------------------------------------------------------------------------
from   constants                    import mode_Power, mode_Grade, UseBluetooth

import debug
import logfile
import time

if UseBluetooth:
    import json
    import requests
    import subprocess
from   pathlib                      import Path
import atexit

import FortiusAntCommand    as cmd

#---------------------------------------------------------------------------
# c l s B l e I n t e r f a c e
#---------------------------------------------------------------------------
# Input:    UseBluetooth
#               If False, it will be a 'dummy' class, just providing the data-
#               structure so that the caller can refer without checking the
#               directory on every location.
#
#           host and port are variable, but note that Node.js must be
#               redefined as well in that case.
#
# Function  The Bluetooth interface object
#           Providing elementary functions to Send/receive data
#
#---------------------------------------------------------------------------
class clsBleInterface():
    def __init__(self, clv, host = 'localhost', port = 9999):
        self.OK        = False
        self.host      = host
        self.port      = port
        self.interface = None
        self.jsondata  = None
        self.clv       = clv
        if UseBluetooth and clv.ble:
            self.Message   = ", Bluetooth interface available"
            #---------------------------------------------------------------
            # register self.Close() to make sure the BLE server is stopped
            #   ON program termination
            # Note that __del__ is called too late to be able to close.
            #---------------------------------------------------------------
            atexit.register(self.Close)
        else:
            self.Message   = "" # Bluetooth disabled or not used

    def __del__(self):
        pass

    if UseBluetooth:
        #-------------------------------------------------------------------
        # O p e n
        #-------------------------------------------------------------------
        # input     none
        #
        # function  The Bluetooth interface is opened
        #
        # returns   self.interface
        #-------------------------------------------------------------------
        def Open(self):
            self.OK = False
            self.Message = ", Bluetooth interface cannot be opened"
            if debug.on(debug.Ble): logfile.Write ("BleInterface.Open() ...")

            if self.interface:
                if debug.on(debug.Ble): logfile.Write('... already open')
            else:
                #-----------------------------------------------------------
                # Create interface as sub-process
                #-----------------------------------------------------------
                command = [
                    "node",
                    "server.js"
                ]

                if self.clv.steering:
                    command.append("steering")

                directory = Path.cwd().parent / "node"
                if debug.on(debug.Ble): logfile.Write("... Popen(%s,%s)" % (directory, command) )
                try:
                    if debug.on(debug.Any):
                        self.interface = subprocess.Popen(command, cwd=directory, stdout=logfile.fLogfile, stderr=logfile.fLogfile)
                    else:
                        self.interface = subprocess.Popen(command, cwd=directory)
                except Exception as e:
                    self.Message += "; " + str(e)
                    if debug.on(debug.Ble): logfile.Write ("... " + str(e))
                else:
                    if debug.on(debug.Ble): logfile.Write('... completed')
                    self.Message = ", Bluetooth interface opened to CTP"
                    self.OK = True

            if self.OK: logfile.Console("FortiusANT exchanges data with a bluetooth Cycling Training Program")
            return self.OK
        #-------------------------------------------------------------------
        # W r i t e
        #-------------------------------------------------------------------
        # input     data
        #
        # function  The provided data is posted to the Bluetooth interface
        #
        # returns   none
        #-------------------------------------------------------------------
        def Write(self, data):
            rtn = False
            if debug.on(debug.Ble): logfile.Write('BleInterface.Write(%s)' % data)
            if self.interface:
                url = f'http://{self.host}:{self.port}/ant'
                try:
                    r = requests.post(url, data=data)
                except Exception as e:
                    logfile.Console ("... requests.post() error " + str(e))
                else:
                    rtn = r.ok
            return rtn

        #-------------------------------------------------------------------
        # R e a d
        #-------------------------------------------------------------------
        # input     none
        #
        # function  Data is obtained from Bluetooth interface
        #
        # returns   rtn = False/True
        #           msg = received data
        #-------------------------------------------------------------------
        def Read(self):
            if debug.on(debug.Ble): logfile.Write ("BleInterface.Read() ...")
            rtn = False
            self.jsondata = None
            if self.interface:
                #-----------------------------------------------------------
                # Read from bluetooth interface
                #-----------------------------------------------------------
                try:
                    r = requests.get(f'http://{self.host}:{self.port}/ant')
                except Exception as e:
                    logfile.Console ("... requests.get() error " + str(e))
                else:
                    #-------------------------------------------------------
                    # Now we have a response object r
                    # Which should contain a JSON object
                    #-------------------------------------------------------
                    if r.ok and r.text != "":
                        try:
                            self.jsondata = json.loads(r.text)
                        except Exception as e:
                            logfile.Console ("... json.loads() error " + str(e))
                        else:
                            rtn = True

            if debug.on(debug.Ble): logfile.Write ("... returns: %s (%s)" % (rtn, self.jsondata) )
            return rtn

        #-------------------------------------------------------------------
        # C l o s e
        #-------------------------------------------------------------------
        # input     none
        #
        # function  The Bluetooth interface is closed
        #
        # returns   self.interface
        #-------------------------------------------------------------------
        def Close(self):
            if self.interface:
                if debug.on(debug.Ble): logfile.Write ("BleInterface.Close() ...")
                self.interface.terminate()
                self.interface.wait()
                self.interface = None
                self.Message   = ", Bluetooth interface closed"
                self.OK        = False
                if debug.on(debug.Ble): logfile.Write ("... completed")
            else:
                pass

#---------------------------------------------------------------------------
# c l s B l e C T P (Cycling Training Program)
#---------------------------------------------------------------------------
# This class communicates with a CTP (Zwift, Trainer Road, ...)
#
# The user can provide the actual data of the Athlete and the trainer; this
# data will be sent to the CTP.
#
# The user can obtain commands from the CTP
#---------------------------------------------------------------------------
class clsBleCTP(clsBleInterface):
    #-----------------------------------------------------------------------
    # Athlete data
    #-----------------------------------------------------------------------
    HeartRate           = 0

    #-----------------------------------------------------------------------
    # Trainer data
    #-----------------------------------------------------------------------
    CurrentSpeed        = 0
    Cadence             = 0
    CurrentPower        = 0

    #-----------------------------------------------------------------------
    # CTP data
    #-----------------------------------------------------------------------
    TargetMode          = None      # No target received
    TargetGrade         = 0
    TargetPower         = 0

    WindResistance      = None
    WindSpeed           = None
    DraftingFactor      = 1         # Default since not supplied
    RollingResistance   = None

    def SetAthleteData(self, HeartRate):
        self.HeartRate      = HeartRate

    def SetTrainerData(self, CurrentSpeed, Cadence, CurrentPower):
        self.CurrentSpeed   = CurrentSpeed
        self.Cadence        = Cadence
        self.CurrentPower   = CurrentPower
    
    def Refresh(self):
        rtn                 = False

        if UseBluetooth:
            #----------------------------------------------------------------
            # Send data to CTP and receive 'further instructions' from CTP
            #----------------------------------------------------------------
            data                = {}
            data['heart_rate']  = self.HeartRate

            data['watts']       = self.CurrentPower
            data['cadence']     = self.Cadence

            if self.OK and self.Write(data):
                if self.Read():
                    #--------------------------------------------------------
                    # Let's see what we got back
                    # The caller of the class can use these variables
                    #--------------------------------------------------------
                    try:
                        self.TargetPower        = self.jsondata["target_power"]
                        self.TargetMode         = mode_Power
                        rtn                     = True
                    except:
                        pass

                    try:
                        self.TargetGrade        = self.jsondata["grade"]
                        self.TargetMode         = mode_Grade
                        rtn                     = True
                    except:
                        pass

                    try:
                        self.WindResistance     = self.jsondata["wind_resistance_coefficient"]
                        rtn                     = True
                    except:
                        pass

                    try:
                        self.WindSpeed          = self.jsondata["wind_speed"]
                        rtn                     = True
                    except:
                        pass

                    try:
                        self.RollingResistance  = self.jsondata["rolling_resistance_coefficient"]
                        rtn                     = True
                    except:
                        pass

        #--------------------------------------------------------------------
        # Return something may have changed
        #--------------------------------------------------------------------
        return rtn

# ==============================================================================
# Main program
# ==============================================================================
if __name__ == "__main__":
    global clv

    # --------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------
    debug.deactivate()
    clv = cmd.CommandLineVariables()
    debug.activate(clv.debug)

    if debug.on(debug.Ble):
        logfile.Open()
        logfile.Console("bleDongle started")
        clv.print()
        logfile.Console("------------------")

    if clv.ble:
        bleCTP = clsBleCTP(clv)
        if bleCTP.Open():
            print(bleCTP.Message)
            try:
                while True:
                    bleCTP.SetAthleteData(135)
                    bleCTP.SetTrainerData(34.5, 123, 246)

                    if bleCTP.Refresh():
                        print('Target Mode=%s, Power=%s, Grade=%s' % (bleCTP.TargetMode, bleCTP.TargetPower, bleCTP.TargetGrade) )
                    else:
                        print('No data')
                    time.sleep(0.25)
            except KeyboardInterrupt:
                logfile.Console ("Stopped (keyboard interrupt)")
            except Exception as e:
                print (str(e))
            bleCTP.Close()
        else:
            print(bleCTP.Message)

    #-------------------------------------------------------------------------------
    # Done
    #-------------------------------------------------------------------------------
    if debug.on(debug.Ble):
        logfile.Console("bleDongle ended")
