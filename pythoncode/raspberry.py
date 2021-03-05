#---------------------------------------------------------------------------
# Version info
#---------------------------------------------------------------------------
__version__ = "2021-03-01"
# 2021-03-01  Five leds defined; blinking when events occur.
#             Now activity on the interfaces is visible.
#             Pin 29...39 are selected because it's 6 pins in a row for all leds
#
#             Button defined on pins 30/32 to gracefully shutdown
#
# 2021-01-29  As provided by @decodais.
#             If the -L is set as commandline parameter it enables the
#             RasperryPi IO functions. This is for compatibility to PC-systems.
#             May be there exists a better way but it works
#-------------------------------------------------------------------------------
import subprocess
import sys
import time

try:
                    # this module is a preinstalled module on Raspbian
    import gpiozero # pylint: disable=import-error
except:
    UseLeds = False
else:
    UseLeds = True

# ------------------------------------------------------------------------------
# P r e p a r e S h u t d o w n
# ------------------------------------------------------------------------------
# Input     None
#
# Function  The shutdown button was pressed, mark that we're going to shutdown
#
# Output    PrepareShutdown
# ------------------------------------------------------------------------------
def PrepareShutdown():
    global ShutdownRequested
    ShutdownRequested = True

# ------------------------------------------------------------------------------
# I s S h u t d o w n R e q u e s t e d
# ------------------------------------------------------------------------------
# Input     ShutdownRequested
#
# Function  Informs the caller to stop and call ShutdownIfRequested() asap.
#
# Returns   True/False
# ------------------------------------------------------------------------------
def IsShutdownRequested():
    global ShutdownRequested
    try:
        return ShutdownRequested
    except:
        return False

# ------------------------------------------------------------------------------
# S h u t d o w n I f R e q u e s t e d
# ------------------------------------------------------------------------------
# Input     ShutdownRequested
#
# Function  If the shutdown button was pressed, powerdown the Raspberry
#           This function should be called as last statement of an application
#           stopping.
#
# Returns   None
# ------------------------------------------------------------------------------
def ShutdownIfRequested():
    if IsShutdownRequested():
        print("Powerdown raspberry now")
        subprocess.call("sudo shutdown -P now", shell=True)

# ==============================================================================
# Initialisation of IO-Port's for the LED's
# ------------------------------------------------------------------------------
# 
#                      Raspberry Pi Pin  Pin Raspberry Pi
#                   + 3,3 V           1  2   + 5 V
#                 (SDA1) GPI_O2       3  4   + 5 V
#                 (SCL1) GPI_O3       5  6   GND
#                 (GPIO_GCLK) GPI_O4  7  8   GPIO_14 (TXD0)
#                   GND               9  10  GPIO_15 (RXD0)
#                (GPIO_GEN0) GPIO_17 11  12  GPIO_18 (GPIO_GEN1)
#                (GPIO_GEN2) GPIO_27 13  14  GND                    
#                (GPIO_GEN3) GPIO_22 15  16  GPIO_23 (GPIO_GEN4)    
#                   + 3,3 V          17  18  GPIO_24 (GPIO_GEN5)    
#                (SPI_MISO) GPIO_9   21  22  GPIO_25 (GPIO_GEN6)    
#                (SPI_SLCK) GPIO_11  23  24  GPIO_8 (SPI_CE0_N)
#                   GND              25  26  GPIO_7 (SPI_CE1_N)
#                (für I2C) ID_SD     27  28  ID_SC (nur für I2C)
#      LedTacx <--  GPI_O5           29  30  GND                   
#  LedShutdown <--  GPI_O6           31  32  GPIO_12  <-- BtnShutdown
#   LedCadence <--  GPI_O13          33  34  GND      --> GND
#       LedBLE <--  GPI_O19          35  36  GPIO_16
#       LedANT <--  GPIO_26          37  38  GPIO 20
#                   GND              39  40  GPIO 21
#
#
# Reference https://gpiozero.readthedocs.io/en/stable/api_output.html#led
#           https://gpiozero.readthedocs.io/en/stable/api_input.html#button
# ==============================================================================
class clsRaspberry:
    def __init__(self, clv):
        # ----------------------------------------------------------------------
        # Activate leds, if we are on Raspberry
        # ----------------------------------------------------------------------
        self.OK = UseLeds

        # ----------------------------------------------------------------------
        # Activate leds, if -L defined
        # Reason for -L is that usage of GPIO might be conflicting with other
        #       applications on the Raspberry
        # ----------------------------------------------------------------------
        if self.OK and clv != None:
            self.OK = clv.rpiLeds

        # ----------------------------------------------------------------------
        # Create 5 leds on these Pins as outputs.
        # The numbers are the numbers of the IO-Pins of the Raspi
        # Don't forget to add the series resistor of 470 Ohm
        # ----------------------------------------------------------------------
        if self.OK:
            self.LedTacx     = gpiozero.LED(5)          # Orange
            self.LedShutdown = gpiozero.LED(6)          # Red
            self.LedCadence  = gpiozero.LED(13)         # White
            self.LedBLE      = gpiozero.LED(19)         # Blue
            self.LedANT      = gpiozero.LED(26)         # Green

            self.BtnShutdown = gpiozero.Button(12)

        # ----------------------------------------------------------------------
        # Show leds for power-up
        # ----------------------------------------------------------------------
        if self.OK:
            self.PowerupTest()

    # --------------------------------------------------------------------------
    #  T o g g l e
    # --------------------------------------------------------------------------
    # Input     OK, led, event
    #
    # Function  If no event occurred, led is switched off
    #           If an event occurred, led is toggled on/off
    #
    #           If this function is called in a 250ms cycle, the led will
    #           blink on/off when events are received; when no events received
    #           the led willl go off.
    #
    #           Set's LED intensity value  0.0 => off, 1.0 => on
    #
    # Output    led-value is set
    # --------------------------------------------------------------------------
    def Toggle(self, led, event):
        if self.OK:
            if not event:
                led.off()
            else:
                led.toggle()

    # --------------------------------------------------------------------------
    #  Toggles for the five leds
    # --------------------------------------------------------------------------
    def ANT(self, event):
        if self.OK: self.Toggle(self.LedANT,      event)

    def BLE(self, event):
        if self.OK: self.Toggle(self.LedBLE,      event)

    def Cadence(self, event):
        if self.OK: self.Toggle(self.LedCadence,  event)

    def Shutdown(self, event):
        if self.OK: self.Toggle(self.LedShutdown, event)

    def Tacx(self, event):
        if self.OK: self.Toggle(self.LedTacx,     event)

    # --------------------------------------------------------------------------
    #  Powerup test TSCBA
    # --------------------------------------------------------------------------
    def PowerupTest(self):
        self.Tacx    (True)
        time.sleep(.25)

        self.Tacx    (False)
        self.Shutdown(True)
        time.sleep(.25)

        self.Shutdown(False)
        self.Cadence (True)
        time.sleep(.25)

        self.Cadence (False)
        self.BLE     (True)
        time.sleep(.25)

        self.BLE     (False)
        self.ANT(True)
        time.sleep(.25)

        self.ANT     (False)

    # --------------------------------------------------------------------------
    # C h e c k S h u t d o w n
    # --------------------------------------------------------------------------
    # Input     nothing
    #
    # Function  toggle Shutdown led during button press
    #           return True if kept pressed for the define timeout
    #
    #           usage: when button is pressed firmly, FortiusAnt must close 
    #                  down and shutdown Raspberry
    #
    # Returns   True when button pressed firmly
    # --------------------------------------------------------------------------
    def CheckShutdown(self):
        repeat = 20      # timeout = n * .25 seconds
        rtn    = self.OK # Assume button will remain pressed
                         # If we don't use leds/buttons ==> False

        if self.OK and not IsShutdownRequested():
            # ------------------------------------------------------------------
            # Switch off all leds
            # ------------------------------------------------------------------
            if self.BtnShutdown.is_held:
                self.ANT     (False)
                self.BLE     (False)
                self.Tacx    (False)
                self.Cadence (False)

            self.Shutdown(False)

            # ------------------------------------------------------------------
            # Blink the (red) Shutdown led while button pressed
            # ------------------------------------------------------------------
            while repeat:
                repeat -= 1
                if not self.BtnShutdown.is_held:
                    rtn = False
                    break
                self.Shutdown(True)
                time.sleep(.25)

            # ------------------------------------------------------------------
            # Final warning
            # ------------------------------------------------------------------
            if rtn:
                self.PowerupTest()
                rtn = self.BtnShutdown.is_held

            # ------------------------------------------------------------------
            # Now it's sure we will shutdown
            # The application has to do it, though.
            # ------------------------------------------------------------------
            if rtn: PrepareShutdown()

        # ----------------------------------------------------------------------
        # Return True/False; may be of previous shutdown-request!
        # ----------------------------------------------------------------------
        return IsShutdownRequested()

# ------------------------------------------------------------------------------
# Code for test-purpose
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    rpi = clsRaspberry(None)
    event = True                        # Use same event-flag for each led
    first = True

    while True:
            if first: print('Test leds')
            rpi.ANT     (event)
            rpi.BLE     (event)
            rpi.Tacx    (event)
            rpi.Cadence (event)
            rpi.Shutdown(event)
            time.sleep(.25)
            event = not event

            if first: print('Until button pressed')
            if rpi.CheckShutdown(): break

            first = False

    ShutdownIfRequested()
