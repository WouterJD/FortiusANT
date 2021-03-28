#---------------------------------------------------------------------------
# Version info
#---------------------------------------------------------------------------
__version__ = "2021-03-25"
# 2021-03-25  OutputDisplay added
# 2021-03-22  constants.py imported; OnRaspberry used
# 2021-03-07  @MeanHat TFT screen v2.1
# 2021-03-08  GPIO3 used for the button, so that can be used for poweron
#                   Thanks As provided by @decodais, #
#             5 blinks before shutdown, is enough
#             before shutdown all leds on()
#
# # 2021-03-01  Five leds defined; blinking when events occur.
#             Now activity on the interfaces is visible.
#             Pin 29...39 are selected because it's 6 pins in a row for all leds
#
#             Button defined on GPIO 3 (since Mar 8th) to gracefully shutdown
#
# 2021-01-29  As provided by @decodais.
#             If the -L is set as commandline parameter it enables the
#             RasperryPi IO functions. This is for compatibility to PC-systems.
#             May be there exists a better way but it works
#-------------------------------------------------------------------------------
import os
import subprocess
import sys
import time

MySelf = None
from   constants import OnRaspberry
import constants
import FortiusAntCommand    as cmd
import logfile

UseOutputDisplay = False
if OnRaspberry:
    import gpiozero                                     # pylint: disable=import-error

    try:
        from adafruit_rgb_display.rgb import color565   # pylint: disable=import-error
        import adafruit_rgb_display.st7789 as st7789    # pylint: disable=import-error
        import board                                    # pylint: disable=import-error
        import digitalio                                # pylint: disable=import-error
        from PIL import Image, ImageDraw, ImageFont     # pylint: disable=import-error
    except:
        pass
    UseOutputDisplay = True

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
        if MySelf != None and MySelf.StatusLeds:
            MySelf.LedTacx     .on()
            MySelf.LedShutdown .on()
            MySelf.LedCadence  .on()
            MySelf.LedBLE      .on()
            MySelf.LedANT      .on()
        subprocess.call("sudo shutdown -P now", shell=True)

# ==============================================================================
# Initialisation of IO-Port's for the LED's
# ------------------------------------------------------------------------------
#       Raspberry Pi Pin  Pin Raspberry Pi          | Default leds/buttons (-L) | OLED display 
#    + 3,3 V           1  2   + 5 V                 |                           | x x
#  (SDA1) GPI_O2       3  4   + 5 V                 |                           | x x
#  (SCL1) GPI_O3       5  6   GND                   | clv.rpiButton  fanGround  | x x
#  (GPIO_GCLK) GPI_O4  7  8   GPIO_14 (TXD0)        |                Fan        | x x
#    GND               9  10  GPIO_15 (RXD0)        | btnGround                 | x x
# (GPIO_GEN0) GPIO_17 11  12  GPIO_18 (GPIO_GEN1)   |                           | x x
# (GPIO_GEN2) GPIO_27 13  14  GND                   |                           | x x
# (GPIO_GEN3) GPIO_22 15  16  GPIO_23 (GPIO_GEN4)   |                           | x x
#    + 3,3 V          17  18  GPIO_24 (GPIO_GEN5)   |                           | x x
# (SPI_MISO) GPIO_9   21  22  GPIO_25 (GPIO_GEN6)   |                           | x x
# (SPI_SLCK) GPIO_11  23  24  GPIO_8 (SPI_CE0_N)    |                           | x x
#    GND              25  26  GPIO_7 (SPI_CE1_N)    |                           |
# (für I2C) ID_SD     27  28  ID_SC (nur für I2C)   |                           |
#    GPI_O5           29  30  GND                   | clv.rpiTacx               | Tacx fanGnd
#    GPI_O6           31  32  GPIO_12               | clv.rpiShutdown           | Shut Fan
#    GPI_O13          33  34  GND                   | clv.rpiCadence            | Cade btnGnd
#    GPI_O19          35  36  GPIO_16               | clv.rpiBLE                | BLE  Button
#    GPIO_26          37  38  GPIO 20               | clv.rpiANT                | ANT
#    GND              39  40  GPIO 21               | clv.rpiGround             | Gnd
#
# Reference https://gpiozero.readthedocs.io/en/stable/api_output.html#led
#           https://gpiozero.readthedocs.io/en/stable/api_input.html#button
# ==============================================================================
class clsRaspberry:
    OK            = False
    display       = None   # callable function

    StatusLeds    = False  # 5 status leds and one button
    OutputDisplay = False  # one mini TFT display connected

    LedTacx       = None
    LedShutdown   = None
    LedCadence    = None
    LedBLE        = None
    LedANT        = None
    BtnShutdown   = None

    def __init__(self, clv):
        global MySelf
        # ----------------------------------------------------------------------
        # Activate leds, if we are on Raspberry
        # ----------------------------------------------------------------------
        self.OK = OnRaspberry
        MySelf = self

        # ----------------------------------------------------------------------
        # Activate leds, if -l defined
        # Reason for -l is that usage of GPIO might be conflicting with other
        #       applications on the Raspberry
        # ----------------------------------------------------------------------
        if self.OK:
            if OnRaspberry: self.StatusLeds  = clv.StatusLeds                           # boolean
            if OnRaspberry: self.OutputDisplay = clv.OutputDisplay and UseOutputDisplay # string

            self.OK = self.StatusLeds or self.OutputDisplay

        # ----------------------------------------------------------------------
        # Create 5 leds on these Pins as outputs.
        # The numbers are the numbers of the IO-Pins of the Raspi
        # Don't forget to add the series resistor of 470 Ohm
        # ----------------------------------------------------------------------
        if self.StatusLeds:
            self.LedTacx     = gpiozero.LED(clv.rpiTacx)        # Orange
            self.LedShutdown = gpiozero.LED(clv.rpiShutdown)    # Red
            self.LedCadence  = gpiozero.LED(clv.rpiCadence)     # White
            self.LedBLE      = gpiozero.LED(clv.rpiBLE)         # Blue
            self.LedANT      = gpiozero.LED(clv.rpiANT)         # Green

            self.BtnShutdown = gpiozero.Button(clv.rpiButton)

        # ----------------------------------------------------------------------
        # Initialize OLED display
        # ----------------------------------------------------------------------
        self.display = self.displayConsole         # If invalid, on console

        if   clv.OutputDisplay == False:           # Not specified, no output
            self.display = self.displayNone

        elif clv.OutputDisplay == 'console':       # Test output on console
            pass

        elif clv.OutputDisplay == 'st7789':        # TFT mini OLED display
            if self.SetupDisplaySt7789():
                self.display = self.displaySt7789

        else:
            logfile.Console('Unexpected value for -O %s' % clv.OutputDisplay)

        # ----------------------------------------------------------------------
        # Show leds for power-up
        # ----------------------------------------------------------------------
        if self.StatusLeds:
            self.PowerupTest()

    # --------------------------------------------------------------------------
    # [ L E D ]   T o g g l e
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
        if self.StatusLeds:
            if not event:
                led.off()
            else:
                led.toggle()

    # --------------------------------------------------------------------------
    # [ L E D ]   Toggles for the five leds
    # --------------------------------------------------------------------------
    def ANT(self, event):
        self.Toggle(self.LedANT,      event)

    def BLE(self, event):
        self.Toggle(self.LedBLE,      event)

    def Cadence(self, event):
        self.Toggle(self.LedCadence,  event)

    def Shutdown(self, event):
        self.Toggle(self.LedShutdown, event)

    def Tacx(self, event):
        self.Toggle(self.LedTacx,     event)

    def SetLeds(self, ANT=None, BLE=None, Cadence=None, Shutdown=None, Tacx=None):
        if ANT      != None: self.ANT(ANT)
        if BLE      != None: self.BLE(BLE)
        if Cadence  != None: self.Cadence(Cadence)
        if Shutdown != None: self.Shutdown(Shutdown)
        if Tacx     != None: self.Tacx(Tacx)

    # --------------------------------------------------------------------------
    # [ L E D ]   Powerup test TSCBA
    # --------------------------------------------------------------------------
    def PowerupTest(self):
        self.SetLeds(False, False, False, False, False)                  # off
        self.SetLeds(False, False, False, False, True ); time.sleep(.25) # Tacx
        self.SetLeds(False, False, False, True,  False); time.sleep(.25) # Shutdown
        self.SetLeds(False, False, True,  False, False); time.sleep(.25) # Cadence
        self.SetLeds(False, True,  False, False, False); time.sleep(.25) # BLE
        self.SetLeds(True,  False, False, False, False); time.sleep(.25) # ANT
        self.SetLeds(False, False, False, False, False)                  # off

    # --------------------------------------------------------------------------
    # [ L E D ]   C h e c k S h u t d o w n
    # --------------------------------------------------------------------------
    # Input     FortiusAntGui
    #
    # Function  toggle Shutdown led during button press
    #           return True if kept pressed for the define timeout
    #
    #           usage: when button is pressed firmly, FortiusAnt must close 
    #                  down and shutdown Raspberry
    #
    # Returns   True when button pressed firmly
    # --------------------------------------------------------------------------
    def CheckShutdown(self, FortiusAntGui=None):
        repeat = 5                  # timeout = n * .25 seconds        # 5 blinks is enough
        rtn    = self.StatusLeds    # Assume button will remain pressed
                                    # If we don't use leds/buttons ==> False
        ResetLeds= False

        if self.StatusLeds and not IsShutdownRequested():
            # ------------------------------------------------------------------
            # Switch off shutdown led, just in case (only local)
            # ------------------------------------------------------------------
            self.Shutdown(False)

            # ------------------------------------------------------------------
            # Blink the (red) Shutdown led while button pressed
            # ------------------------------------------------------------------
            while repeat:
                repeat -= 1
                if self.BtnShutdown.is_held:
                    self.SetLeds             (False, False, False, True, False)
                    if FortiusAntGui != None:
                        FortiusAntGui.SetLeds(False, False, False, True, False)
                    ResetLeds = True
                    time.sleep(.25)
                else:
                    rtn = False
                    break

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
            if rtn:
                PrepareShutdown()

            # ------------------------------------------------------------------
            # If leds were touched, switch off all - application must set again
            # ------------------------------------------------------------------
            if not rtn and ResetLeds:
                self.SetLeds             (False, False, False, False, False)
                if FortiusAntGui != None:
                    FortiusAntGui.SetLeds(False, False, False, False, False)

        # ----------------------------------------------------------------------
        # Return True/False; may be of previous shutdown-request!
        # ----------------------------------------------------------------------
        return IsShutdownRequested()

    # --------------------------------------------------------------------------
    # [ T F T ]   S e t u p D i s p l a y
    # --------------------------------------------------------------------------
    # Input     None
    #
    # Function  see https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-setup
    #           define display and produce startup image
    #           configure CS and DC pins (these are FeatherWing defaults on M0/M4):
    #
    # Returns   True for success
    # --------------------------------------------------------------------------
    def SetupDisplaySt7789(self):
        rtn = True
        # ----------------------------------------------------------------------
        # Create the ST7789 display (this is 240x240 version):
        # ----------------------------------------------------------------------
        cs_pin    = digitalio.DigitalInOut(board.CE0)
        dc_pin    = digitalio.DigitalInOut(board.D25)
        reset_pin = None

        BAUDRATE  = 64000000        # Default max is 24Mhz
        try:
            spi   = board.SPI()     # Setup SPI bus using hardware SPI
        except Exception as e:
            logfile.Console ("OLED display st7789 cannot be initialized: %s" % e)
            rtn   = False
        else:
            # ------------------------------------------------------------------
            # Now initialize the display
            # ------------------------------------------------------------------
            self.st7789 = st7789.ST7789(
                spi,
                cs=cs_pin,
                dc=dc_pin,
                rst=reset_pin,
                baudrate=BAUDRATE,
                width=240,
                height=240,
                x_offset=0,
                y_offset=80,
            )

            # ------------------------------------------------------------------
            # As copied from https://learn.adafruit.com
            # For testing
            # ------------------------------------------------------------------
            self.backlight = digitalio.DigitalInOut(board.D22)
            self.backlight.switch_to_output()
            self.backlight.value = True
            self.buttonA = digitalio.DigitalInOut(board.D23)
            self.buttonB = digitalio.DigitalInOut(board.D24)
            self.buttonA.switch_to_input()
            self.buttonB.switch_to_input()

            # ------------------------------------------------------------------
            # Swap height/width to rotate it to landscape:
            # ------------------------------------------------------------------
            width  = self.st7789.width  
            height = self.st7789.height
                
            image = Image.new("RGB", (width, height))

            # ------------------------------------------------------------------
            # get drawing object to draw on image:
            ## draw = ImageDraw.Draw(image)

            # draw a black filled box to clear the image:
            ## draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
            ## disp.image(image)
            # ------------------------------------------------------------------

            # ------------------------------------------------------------------
            # Startup images is in directory of the .py [or embedded in .exe]
            # ------------------------------------------------------------------
            dirname = os.path.dirname(__file__)
            FortiusAnt_jpg = os.path.join(dirname, "FortiusAnt.jpg")
            image = Image.open(FortiusAnt_jpg)

            # ------------------------------------------------------------------
            # Scale the image to the smaller screen dimension:
            # ------------------------------------------------------------------
            image_ratio  = image.width / image.height
            screen_ratio = width / height
            if screen_ratio < image_ratio:
                scaled_width  = image.width * height // image.height
                scaled_height = height
            else:
                scaled_width  = width
                scaled_height = image.height * width // image.width
            image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

            # ------------------------------------------------------------------
            # Crop and center the image:
            # ------------------------------------------------------------------
            x_jpg = scaled_width  // 2 - width  // 2
            y_jpg = scaled_height // 2 - height // 2
            image = image.crop((x_jpg, y_jpg, x_jpg + width, y_jpg + height))

            # ------------------------------------------------------------------
            # Display image:
            # ------------------------------------------------------------------
            self.st7789.image(image)

        return rtn

    # --------------------------------------------------------------------------
    # [ T F T ]   d i s p l a y
    # --------------------------------------------------------------------------
    # Input     FortiusAntState; as defined in constants
    #
    # Function  For each FortiusAnt state display the appropriate messages on
    #           the small attached screen.
    #           2021-03 - only one screen implemented; other screens could
    #                     be implemented in future.
    #
    # Returns   None
    # --------------------------------------------------------------------------
    def displayNone(self, FortiusAntState):
        pass

    def displayConsole(self, FortiusAntState):
        if True or self.OutputDisplay:
            if   FortiusAntState == constants.faStarted:
                print('+++++ faStarted')
            elif FortiusAntState == constants.faTrainer:
                print('+++++ faTrainer')
            elif FortiusAntState == constants.faWait2Calibrate:
                print('+++++ faWait2Calibrate')
            elif FortiusAntState == constants.faCalibrating:
                print('+++++ faCalibrating')
            elif FortiusAntState == constants.faActivate:
                print('+++++ faActivate')
            elif FortiusAntState == constants.faOperational:
                print('+++++ faOperational')
            elif FortiusAntState == constants.faStopped:
                print('+++++ faStopped')
            elif FortiusAntState == constants.faDeactivated:
                print('+++++ faDeactivated')
            else:
                pass

    def displaySt7789(self, FortiusAntState):
        if True or self.OutputDisplay:
            if   FortiusAntState == constants.faStarted:
                print('+++++ faStarted (st7789)')
            elif FortiusAntState == constants.faTrainer:
                print('+++++ faTrainer (st7789)')
            elif FortiusAntState == constants.faWait2Calibrate:
                print('+++++ faWait2Calibrate (st7789)')
            elif FortiusAntState == constants.faCalibrating:
                print('+++++ faCalibrating (st7789)')
            elif FortiusAntState == constants.faActivate:
                print('+++++ faActivate (st7789)')
            elif FortiusAntState == constants.faOperational:
                print('+++++ faOperational (st7789)')
            elif FortiusAntState == constants.faStopped:
                print('+++++ faStopped (st7789)')
            elif FortiusAntState == constants.faDeactivated:
                print('+++++ faDeactivated (st7789)')
            else:
                pass

# ------------------------------------------------------------------------------
# Code for test-purpose
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # --------------------------------------------------------------------------
    # Get command line variables; -l, -L and -O are relevant
    # --------------------------------------------------------------------------
    clv=cmd.CommandLineVariables()
    if OnRaspberry:                 # switch on in testmode, so that -l -O not needed
        clv.StatusLeds    = True
        clv.OutputDisplay = 'st7789'
        clv.rpiButton     = 16
    clv.print()

    # --------------------------------------------------------------------------
    # Create RaspberryPi object
    # --------------------------------------------------------------------------
    rpi = clsRaspberry(clv)

    event   = True                        # Use same event-flag for each led
    first   = True
    repeat  = 5
    while True:
        # ----------------------------------------------------------------------
        # Test leds (-l flag)
        # ----------------------------------------------------------------------
        if rpi.StatusLeds:
            if first: print('Test leds')
            rpi.ANT     (event)
            rpi.BLE     (event)
            rpi.Tacx    (event)
            rpi.Cadence (event)
            rpi.Shutdown(event)
            event = not event

            if first: print('Until button pressed')
            if rpi.CheckShutdown(): break

        # ----------------------------------------------------------------------
        # Test leds (-l flag)
        # ----------------------------------------------------------------------
        if rpi.OutputDisplay:
            if first: print('Test OutputDisplay')

            print('a, b, repeat', rpi.buttonA.value, rpi.buttonB.value, repeat)

            if rpi.buttonA.value and rpi.buttonB.value:
                rpi.backlight.value = False                     # turn off backlight
                repeat -= 1
                if repeat == 0: print('break, repeat = 0')                           # Stop no powerdown
            else:
                rpi.backlight.value = True                      # turn on backlight

            if rpi.buttonB.value and not rpi.buttonA.value:     # just button A pressed
                rpi.st7789.fill(color565(255, 0, 0))            # red

            if rpi.buttonA.value and not rpi.buttonB.value:     # just button B pressed
                rpi.st7789.fill(color565(0, 0, 255))            # blue

            if not rpi.buttonA.value and not rpi.buttonB.value: # none pressed
                rpi.st7789.fill(color565(0, 255, 0))            # green

        # ----------------------------------------------------------------------
        # Stop for next button press
        # ----------------------------------------------------------------------
        first = False
        time.sleep(.25)

    ShutdownIfRequested()