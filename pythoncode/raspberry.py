#---------------------------------------------------------------------------
# Version info
#---------------------------------------------------------------------------
__version__ = "2021-04-13"
# 2021-04-13  clv.imperial: speed in mph
# 2021-04-12  StatusLeds (-l) flag means that GPIO leds/buttons are used,
#                   the status of the leds is processed on behalf of the
#                   -O display.
# 2021-04-09  Display realized; only [st7789 240x240 1.3"] supported!
#                   No other form-factors considered
#                   e.g. 120x240 would need other layout
# 2021-03-29  "Raspberry will shutdown" messages given
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
from   constants            import mode_Power, mode_Grade, OnRaspberry, mile
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
# Output    ShutdownRequested
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
        if MySelf != None and MySelf.OutputDisplay:
            MySelf._DrawTextTable ( [ [ '',                     None ],\
                                      [ '',                     None ],\
                                      [ '',                     None ],\
                                      [ '',                     None ],\
                                      [ '',                     None ],\
                                      [ '',                     None ],\
                                      [ '',                     None ],\
                                      [ 'Power',                constants.FORTIUS ],\
                                      [ 'can be disconnected',  constants.FORTIUS ]])
        subprocess.call("sudo shutdown -P now", shell=True)

# ==============================================================================
# Initialisation of IO-Port's for the LED's
# ------------------------------------------------------------------------------
#       Raspberry Pi Pin  Pin Raspberry Pi          | Default leds/buttons (-L) | OLED display 
#    + 3,3 V           1  2   + 5 V                 |                           | x x
#  (SDA1) GPIO_2       3  4   + 5 V                 |                           | x x
#  (SCL1) GPIO_3       5  6   GND                   | clv.rpiButton  fanGround  | x x
#  (GPIO_GCLK) GPIO_4  7  8   GPIO_14 (TXD)         |                Fan        | x x
#    GND               9  10  GPIO_15 (RXD)         | btnGround                 | x x
# (GPIO_GEN0) GPIO_17 11  12  GPIO_18 (GPIO_GEN1)   |                           | x x
# (GPIO_GEN2) GPIO_27 13  14  GND                   |                           | x x
# (GPIO_GEN3) GPIO_22 15  16  GPIO_23 (GPIO_GEN4)   |                           | x x
#    + 3,3 V          17  18  GPIO_24 (GPIO_GEN5)   |                           | x x
# (SPI_MISO) GPIO_9   21  22  GPIO_25 (GPIO_GEN6)   |                           | x x
# (SPI_SLCK) GPIO_11  23  24  GPIO_8  (SPI_CE0_N)   |                           | x x
#    GND              25  26  GPIO_7  (SPI_CE1_N)   |                           |
# (für I2C) ID_SD     27  28  ID_SC (nur für I2C)   |                           |
#    GPIO_5           29  30  GND                   | clv.rpiTacx               | Tacx fanGnd
#    GPIO_6           31  32  GPIO_12               | clv.rpiShutdown           | Shut Fan
#    GPIO_13          33  34  GND                   | clv.rpiCadence            | Cade btnGnd
#    GPIO_19          35  36  GPIO_16               | clv.rpiBLE                | BLE  Button
#    GPIO_26          37  38  GPIO 20               | clv.rpiANT                | ANT
#    GND              39  40  GPIO 21               | clv.rpiGround             | Gnd
#
# References:
#           https://www.raspberrypi.org/documentation/usage/gpio/ 
#           https://gpiozero.readthedocs.io/en/stable/api_output.html#led
#           https://gpiozero.readthedocs.io/en/stable/api_input.html#button
# ==============================================================================
class clsRaspberry:
    # --------------------------------------------------------------------------
    # External attributes
    # --------------------------------------------------------------------------
    OK              = False  # True if raspberry AND (leds or display)
    DisplayState    = None   # callable function
    SetValues       = None   # callable function
    DrawLeds        = None   # callable function

    # --------------------------------------------------------------------------
    # Internal attributes
    # --------------------------------------------------------------------------
    StatusLeds      = False  # 5 status leds and one button
    OutputDisplay   = False  # one mini TFT display connected

    LedTacx         = None
    LedShutdown     = None
    LedCadence      = None
    LedBLE          = None
    LedANT          = None
    BtnShutdown     = None

    LedTacxState    = False
    LedShutdownState= False
    LedCadenceState = False
    LedBLEState     = False
    LedANTState     = False

    # --------------------------------------------------------------------------
    # Internal attributes for st7789
    # --------------------------------------------------------------------------
    st7789          = None      # Oled display object
    faImage         = None      # image object, with scaled FortiusAnt image
    image           = None      # image object
    draw            = None      # text draw object on image
    fontS           = None      # Small font
    fontLb          = None      # Large,Bold font
    rotation        = 0

    buttonA         = None
    buttonB         = None
    buttonUp        = False     # button was pressed, must be reset by user
    buttonDown      = False     # same

    ButtonDefaultValue = True   # The value when the button is NOT pressed

    def __init__(self, clv):
        global MySelf
        # ----------------------------------------------------------------------
        # Initialize
        # ----------------------------------------------------------------------
        self.clv = clv
        self.OK = OnRaspberry
        MySelf = self

        # ----------------------------------------------------------------------
        # Activate leds, if -l defined
        # Reason for -l is that usage of GPIO might be conflicting with other
        #       applications on the Raspberry
        # Activate display, if -O defined
        # ----------------------------------------------------------------------
        if self.OK:
            if OnRaspberry: self.StatusLeds    = clv.StatusLeds                         # boolean
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
        # If NO display, the callable functions do nothing!
        # ----------------------------------------------------------------------
        # Currently the module is only written for st77889 240x240 pixels
        # future requests to implement other displays will reveal how much
        # must be changed to accomodate.
        # ----------------------------------------------------------------------
        self.DisplayState = self._DisplayStateConsole   # If invalid, on console
        self.SetValues    = self._SetValuesConsole      # If invalid, on console
        self.DrawLeds     = self._DrawLedsConsole       # If invalid, on console

        if   clv.OutputDisplay == False:                # Not specified, no output
            self.DisplayState = self._DisplayStateNone
            self.SetValues    = self._SetValuesNone
            self.DrawLeds     = self._DrawLedsNone

        elif clv.OutputDisplay == 'console':            # Test output on console
            pass

        elif clv.OutputDisplay == 'st7789':             # TFT mini OLED Display
            self.rotation = clv.OutputDisplayR
            if self._SetupDisplaySt7789():
                self.DisplayState = self._DisplayStateSt7789
                self.SetValues    = self._SetValuesSt7789
                self.DrawLeds     = self._DrawLedsSt7789

        else:
            logfile.Console('Unexpected value for -O %s' % clv.OutputDisplay)

        self.DisplayState()

        # ----------------------------------------------------------------------
        # Show leds for power-up
        # ----------------------------------------------------------------------
        if self.StatusLeds:
            self.PowerupTest()

    # --------------------------------------------------------------------------
    # [ L E D ]   T o g g l e
    # --------------------------------------------------------------------------
    # Input     led, event, ledState
    #           self.StatusLeds: 
    #
    # Function  If no event occurred, led is switched off
    #           If an event occurred, led is toggled on/off
    #
    #           If this function is called in a 250ms cycle, the led will
    #           blink on/off when events are received; when no events received
    #           the led willl go off.
    #
    #           Only if self.StatusLeds, the GPIO functions are called.
    #
    # Output    Led is switched off or toggled
    #
    # Returns   new state of the led
    # --------------------------------------------------------------------------
    def _Toggle(self, led, event, ledState):
        rtn = None
        if not event:
            if self.StatusLeds: led.off()
            rtn = False
        else:
            if self.StatusLeds: led.toggle()
            rtn = not ledState
        return rtn

    # --------------------------------------------------------------------------
    # [ L E D ]   Toggles for the five leds
    # --------------------------------------------------------------------------
    def _ANT(self, event):
        self.LedANTState        = self._Toggle(self.LedANT,      event,    self.LedANTState)

    def _BLE(self, event):
        self.LedBLEState        = self._Toggle(self.LedBLE,      event,    self.LedBLEState)

    def _Cadence(self, event):
        self.LedCadenceState    = self._Toggle(self.LedCadence,  event,    self.LedCadenceState)

    def _Shutdown(self, event):
        self.LedShutdownState   = self._Toggle(self.LedShutdown, event,    self.LedShutdownState)

    def _Tacx(self, event):
        self.LedTacxState       = self._Toggle(self.LedTacx,     event,    self.LedTacxState)

    # --------------------------------------------------------------------------
    # [ L E D ]   S e t L e d s
    # --------------------------------------------------------------------------
    # Input     Five LED-events
    #
    # Function  Toggle the five leds.
    #           If there's a display, draw the leds on the display
    #
    # Output    None
    #
    # Returns   None
    # --------------------------------------------------------------------------
    def SetLeds(self, ANT=None, BLE=None, Cadence=None, Shutdown=None, Tacx=None):
        if ANT      != None: self._ANT(ANT)
        if BLE      != None: self._BLE(BLE)
        if Cadence  != None: self._Cadence(Cadence)
        if Shutdown != None: self._Shutdown(Shutdown)
        if Tacx     != None: self._Tacx(Tacx)

        # ----------------------------------------------------------------------
        # If there's a display; add leds to the image and show it
        # ----------------------------------------------------------------------
        if self.OutputDisplay:
            self.DrawLeds()

    # --------------------------------------------------------------------------
    # [ L E D ]   Powerup test TSCBA; blink one by one then switch off
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
        repeat = 7      # timeout = n * .25 seconds        # 5 blinks is enough
                        # 7 because the first two cycles are blink to allow
                        #       for a "short button press" without messages.
        rtn    = True   # Assume button will remain pressed
                        # If we don't use leds/buttons ==> False
        ResetLeds= False

        if OnRaspberry and not IsShutdownRequested():
            # ------------------------------------------------------------------
            # Switch off shutdown led, just in case (only local)
            # ------------------------------------------------------------------
            self._Shutdown(False)

            # ------------------------------------------------------------------
            # Blink the (red) Shutdown led while button pressed
            # ------------------------------------------------------------------
            while repeat:
                if self.ShutdownButtonIsHeld():
                    if repeat <= 5:
                        self.SetLeds             (False, False, False, True, False)
                        if FortiusAntGui != None:
                            FortiusAntGui.SetLeds(False, False, False, True, False)
                        logfile.Console('Raspberry will be shutdown ... %s ' % repeat)
                    ResetLeds = True
                    time.sleep(.25)
                else:
                    rtn = False
                    break
                repeat -= 1

            # ------------------------------------------------------------------
            # Final warning
            # ------------------------------------------------------------------
            if rtn:
                self.PowerupTest()
                rtn = self.ShutdownButtonIsHeld()

            # ------------------------------------------------------------------
            # Now it's sure we will shutdown
            # The application has to do it, though.
            # ------------------------------------------------------------------
            if rtn:
                logfile.Console('Raspberry will shutdown')
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

    def ShutdownButtonIsHeld(self):
        # ----------------------------------------------------------------------
        # Self-defined button
        # ----------------------------------------------------------------------
        if     self.StatusLeds \
           and self.BtnShutdown.is_held: return True

        # ----------------------------------------------------------------------
        # Buttons on the ST7789 display
        # ----------------------------------------------------------------------
        if     self.buttonA       != None  \
           and self.buttonB       != None  \
           and self.buttonA.value != self.ButtonDefaultValue \
           and self.buttonB.value != self.ButtonDefaultValue: return True
        return False

    # --------------------------------------------------------------------------
    # [ O U T P U T ]   S e t u p D i s p l a y
    # --------------------------------------------------------------------------
    # Input     None
    #
    # Function  see https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-setup
    #           define display and produce startup image
    #           configure CS and DC pins (these are FeatherWing defaults on M0/M4):
    #
    # Output    self.st7789
    #           self.image
    #           self.draw
    #           self.fontS
    #           self.fontLb
    #
    # Returns   True for success
    # --------------------------------------------------------------------------
    def _SetupDisplaySt7789(self):
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

            self.ButtonDefaultValue = self.buttonA.value
            # ------------------------------------------------------------------
            # Startup image is in directory of the .py [or embedded in .exe]
            # ------------------------------------------------------------------
            dirname = os.path.dirname(__file__)
            FortiusAnt_jpg = os.path.join(dirname, "FortiusAnt.jpg")
            self.faImage = Image.open(FortiusAnt_jpg)

            # ------------------------------------------------------------------
            # Scale the image to the smaller screen dimension:
            # ------------------------------------------------------------------
            image_ratio  = self.faImage.width / self.faImage.height
            screen_ratio = self.st7789 .width / self.st7789 .height
            if screen_ratio < image_ratio:
                scaled_width  = self.faImage.width  * self.st7789.height // self.faImage.height
                scaled_height = self.st7789.height
            else:
                scaled_width  = self.st7789.width
                scaled_height = self.faImage.height * self.st7789.width  // self.faImage.width
            self.faImage = self.faImage.resize((scaled_width, scaled_height), Image.BICUBIC)

            # ------------------------------------------------------------------
            # Crop and center the image:
            # ------------------------------------------------------------------
            x_jpg = scaled_width  // 2 - self.st7789.width  // 2
            y_jpg = scaled_height // 2 - self.st7789.height // 2
            self.faImage = self.faImage.crop((x_jpg, y_jpg, x_jpg + self.st7789.width, y_jpg + self.st7789.height))

            #-------------------------------------------------------------------
            # Load a TTF font - other good fonts available from: http://www.dafont.com/bitmap.php
            #-------------------------------------------------------------------
            self.fontS  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            self.fontLb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)

            # ------------------------------------------------------------------
            # Display image, for at least three seconds
            # ------------------------------------------------------------------
            self._ShowImage()
            time.sleep(3)

            #-------------------------------------------------------------------
            # Part 2: display control text
            # Create blank image for drawing with mode 'RGB' for full color
            # Get drawing object to draw on image
            #-------------------------------------------------------------------
            self.image  = Image.new("RGB", (self.st7789.width, self.st7789.height))
            self.draw   = ImageDraw.Draw(self.image)

        return rtn

    # --------------------------------------------------------------------------
    # [ O U T P U T ]   S h o w I m a g e
    # --------------------------------------------------------------------------
    # Input     faImage (FortiusAnt image)
    #
    # Function  show the image on the display
    #
    # Returns   none
    # --------------------------------------------------------------------------
    def _ShowImage(self):
        if False:
            # Show image without text on top
            self.image  = self.faImage    
        else:
            # Show image with text on top
            self.image  = self.faImage
            self.draw   = ImageDraw.Draw(self.image)
            self.draw.text    ( (10, 0     ), 'FortiusAnt',          font=self.fontLb, fill=constants.FORTIUS)

        self.st7789.image(self.faImage, self.rotation)

    # --------------------------------------------------------------------------
    # [ O U T P U T ]   D r a w T e x t T a b l e
    # --------------------------------------------------------------------------
    # Input     t table with text and fill_colour (or 2nd text)
    #           values: False: table contains text, colour
    #                   True:  table contains text, values
    #
    # Function  Draw the elements on the display
    #
    # Output    self.image, containing the displayed text
    #           self.draw,  used to draw on the image
    #
    # Returns   none
    # --------------------------------------------------------------------------
    def _DrawTextTable(self, t, values=False):
        # ----------------------------------------------------------------------
        # True:  Draw a black filled box to clear the image
        # False: Draw text on top of image (as background); like this not usable
        # ----------------------------------------------------------------------
        if True:
            self.image  = Image.new("RGB", (self.st7789.width, self.st7789.height))
            self.draw   = ImageDraw.Draw(self.image)
            # background colour FORTIUS is not a success
            # GREY/WHITE on black background is not so bad after all
            self.draw.rectangle((0, 0, self.st7789.width, self.st7789.height), outline=0, fill=(0, 0, 0))
        else:
            self.image  = self.faImage
            self.draw   = ImageDraw.Draw(self.image)

        # ----------------------------------------------------------------------
        # Draw each of supplied lines
        # h       = line heigth, depending on number of lines provided
        #           23 for 9 lines proved OK, now dynamic for 1...9 lines
        #           Note: if (many) more lines provided, it will be a mess!
        # x=0/120 = column 1, 2
        # ----------------------------------------------------------------------
        h = int(207 / max(1,len(t)))
        for i in range(0, len(t)):
            if values:
                self.draw.text( (  0, i * h), t[i][0], font=self.fontS, fill=constants.GREY)
                self.draw.text( (120, i * h), t[i][1], font=self.fontS, fill=constants.WHITE)
            else:
                self.draw.text( (  0, i * h), t[i][0], font=self.fontS, fill=t[i][1])

        # ----------------------------------------------------------------------
        # Add leds and show image
        # ----------------------------------------------------------------------
        self.DrawLeds()
        
        # ----------------------------------------------------------------------
        # Do not delay here; it delays the FortiusAntBody-loop!!
        # time.sleep(1.5)
        # ----------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # [ O U T P U T ]   D r a w L e d s
    # --------------------------------------------------------------------------
    # Input     self.image, self.draw
    #
    # Function  Draw the leds on the display, under a separation line
    #
    #           Is called when text is displayed
    #                  or when leds are modified
    #           in both cases using the image as created by _DrawTextTable()
    #
    # Output    self.image, leds added
    #
    # Returns   none
    # --------------------------------------------------------------------------
    def _DrawLedsNone(self):
        pass
    def _DrawLedsConsole(self):
        pass
    def _DrawLedsSt7789(self):
        # ----------------------------------------------------------------------
        # Calculate dimensions
        # ----------------------------------------------------------------------
        nrLeds = 2
        if self.clv.Tacx_Cadence:       nrLeds += 1
        if self.clv.ble:                nrLeds += 1
        if self.clv.antDeviceID != -1:  nrLeds += 1

        d = 10                          # Diameter of a led
        y = self.st7789.height - 20     # Vertical top of leds
        dx= self.st7789.width  / nrLeds # Space per led

        # ----------------------------------------------------------------------
        # Fill depending on led-state
        # ----------------------------------------------------------------------
        f1 = constants.AMBER if self.LedTacxState     else constants.BLACK
        f2 = constants.RED   if self.LedShutdownState else constants.BLACK
        f3 = constants.WHITE if self.LedCadenceState  else constants.BLACK
        f4 = constants.BLUE  if self.LedBLEState      else constants.BLACK
        f5 = constants.GREEN if self.LedANTState      else constants.BLACK

        # ----------------------------------------------------------------------
        # Separating line
        # ----------------------------------------------------------------------
        self.draw.line((0, y - 8, self.st7789.width, y - 8), fill=constants.FORTIUS, width=1, joint=None)

        # ----------------------------------------------------------------------
        # Five circles to represent the leds
        # ----------------------------------------------------------------------
        #                                         x1 y2 x2     y2
        x  = int(dx/2 - d/2); self.draw.ellipse( (x, y, x + d, y + d), fill=f1, outline=constants.AMBER, width=1)
        x += int(dx);         self.draw.ellipse( (x, y, x + d, y + d), fill=f2, outline=constants.RED,   width=1)
        if self.clv.Tacx_Cadence:
            x += int(dx);     self.draw.ellipse( (x, y, x + d, y + d), fill=f3, outline=constants.WHITE, width=1)
        if self.clv.ble:
            x += int(dx);     self.draw.ellipse( (x, y, x + d, y + d), fill=f4, outline=constants.BLUE,  width=1)
        if self.clv.antDeviceID != -1:
            x += int(dx);     self.draw.ellipse( (x, y, x + d, y + d), fill=f5, outline=constants.GREEN, width=1)

        # ----------------------------------------------------------------------
        # Show the image
        # ----------------------------------------------------------------------
        self.st7789.image(self.image, self.rotation)

        # ----------------------------------------------------------------------
        # Translate buttons on the ST7789 display to Up/DOWN
        # Rotation-dependant: Left/Bottom = Down, Right/Top   = Up
        # ----------------------------------------------------------------------
        if self.rotation in (180,270):
            if self.buttonA.value != self.ButtonDefaultValue: self.buttonUp   = True
            if self.buttonB.value != self.ButtonDefaultValue: self.buttonDown = True
        else:
            if self.buttonA.value != self.ButtonDefaultValue: self.buttonDown = True
            if self.buttonB.value != self.ButtonDefaultValue: self.buttonUp   = True

    # --------------------------------------------------------------------------
    # [ O U T P U T ] D i s p l a y S t a t e - implementations for the -L displays
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
    def _DisplayStateNone(self, *argv):
        pass

    def _DisplayStateConsole(self, FortiusAntState=None, TacxTrainer=None):
        # ----------------------------------------------------------------------
        # Show texts, corresponding to state of FortiusAnt
        # One line is enough, since colouring/enhancing is not possible
        # ----------------------------------------------------------------------
        if True or self.OutputDisplay:
            if   FortiusAntState == None:
                print('+++++ initialized')
            elif FortiusAntState == constants.faStarted:
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
            elif FortiusAntState == constants.faTerminated:
                print('+++++ faTerminated')
            else:
                pass

    def _DisplayStateSt7789(self, FortiusAntState=None, TacxTrainer=None):
        global PreviousState
        # ----------------------------------------------------------------------
        # If no state provided, show previous state
        # ----------------------------------------------------------------------
        if FortiusAntState == None:
            try:
                FortiusAntState = PreviousState   # pylint: disable=used-before-assignment
            except:
                FortiusAntState = constants.faStarted

        # ----------------------------------------------------------------------
        # Show texts, corresponding to state of FortiusAnt AND trainer.
        # ----------------------------------------------------------------------
        if self.OutputDisplay:
            if TacxTrainer == None:
                # There is no trainer yet, so trainer-dependant text is not there
                # FortiusAnt is started, next step will be connecting to trainer
                # FortiusAnt is stopped, no trainer ever connected
                # First and last line according the contents in usbTrainer.py
                c0  = constants.WHITE if FortiusAntState == constants.faStarted    else constants.BLACK
                c0a = constants.GREY  if FortiusAntState == constants.faStarted    else constants.BLACK
                c8  = constants.WHITE if FortiusAntState == constants.faTerminated else constants.BLACK
                t = [[ 'FortiusAnt started', c0   ],\
                     [ '',                   None ],\
                     [ 'Press [Locate HW]',  c0a  ],\
                     [ 'to continue',        c0a  ],\
                     [ '',                   None ],\
                     [ '',                   None ],\
                     [ '',                   None ],\
                     [ '',                   None ],\
                     [ 'FortiusAnt stopped', c8   ],\
                    ]
            else:
                # Show the trainer-enhanced status
                t = TacxTrainer.DisplayStateTable(FortiusAntState)
            self._DrawTextTable (t)
        PreviousState = FortiusAntState

    # --------------------------------------------------------------------------
    # [ O U T P U T ] S e t V a l u e s - implementations for the -L displays
    # --------------------------------------------------------------------------
    # Input     FortiusAnt parameters
    #
    # Function  Show the actual state
    #
    # Returns   None
    # --------------------------------------------------------------------------
    def _SetValuesNone(self, *argv):
        pass

    def _SetValuesConsole(self, fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, \
                    iTacx, iHeartRate, \
                    iCrancksetIndex, iCassetteIndex, fReduction):
        print('Speed=%s, Cadence=%s, Power=%s, Mode=%s, Target Power=%s, Target Grade=%s, \
               Tacx=%s, Cranckset=%s, Cassette=%s, Reduction=%s' % \
                    (fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, \
                    iTacx, iCrancksetIndex, iCassetteIndex, fReduction))

    def _SetValuesSt7789(self, fSpeed, iRevs, iPower, iTargetMode, iTargetPower, fTargetGrade, \
                    iTacx, iHeartRate, \
                    iCrancksetIndex, iCassetteIndex, fReduction):

            # ------------------------------------------------------------------
            # Format Speed
            # ------------------------------------------------------------------
            if self.clv.imperial:
                s = "{:<4.1f}mph".format(fSpeed / mile)
            else:
                s = "{:<4.1f}km/h".format(fSpeed)

            # ------------------------------------------------------------------
            # Format Power
            # ------------------------------------------------------------------
            if   iTargetMode == mode_Power:
                t = "{:d}Watt".format(iTargetPower)

            elif iTargetMode == mode_Grade:
                t  = "{:<2.0f}%".format(fTargetGrade)
                t += "{:d}Watt" .format(iTargetPower)   # Target power added for reference
                                                        # Can be negative!
            else:
                t = "No target"

            # ------------------------------------------------------------------
            # Format Gears
            # ------------------------------------------------------------------
            if iCassetteIndex < 0:      # IF out of bounds: Reduction <> 1
                teeth = self.clv.Cassette[0]
            elif iCassetteIndex >= len(self.clv.Cassette):
                teeth = self.clv.Cassette[len(self.clv.Cassette) - 1]
            else:
                teeth = self.clv.Cassette[iCassetteIndex]
            g = "%i : %i" % (self.clv.Cranckset[iCrancksetIndex], teeth ) # int(round(teeth / self.Reduction)

            # ------------------------------------------------------------------
            # And draw on the display
            # ------------------------------------------------------------------
            self._DrawTextTable ( [ [ 'Speed'  , s                         ],\
                                    [ 'Cadence', "{:d}/min".format(iRevs)  ],\
                                    [ 'Power'  , "{:d}Watt".format(iPower) ],\
                                    [ 'Target ', t                         ],\
                                    [ 'Gears'  , g                         ]], True)

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
            rpi.SetLeds(event, event, event, event, event)
            event = not event

            if first: print('Until button pressed')
            if rpi.CheckShutdown(): break

        # ----------------------------------------------------------------------
        # Test leds (-O flag)
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