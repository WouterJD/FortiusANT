#---------------------------------------------------------------------------
# Version info
#---------------------------------------------------------------------------
__version__ = "2021-01-29"
# 2021-01-29  If the -L is set as commandline parameter it enables the
# RasperryPi IO functions. This is for compatibility to PC-systems.
# May be there exists a better way but it works
#-------------------------------------------------------------------------------


import FortiusAntCommand    as cmd

clv = cmd.CommandLineVariables()

if clv.Raspi_LED: 
      import sys
     from gpiozero import LED          # this module is a preinstalled module on Raspbian

# ==============================================================================
# Initialisation of IO-Port's for the LED's
# ------------------------------------------------------------------------------
# 
#       Raspberry Pi Pin  Pin Raspberry Pi
#    + 3,3 V           1  2   + 5 V
#  (SDA1) GPI_O2       3  4   + 5 V
#  (SCL1) GPI_O3       5  6   GND
#  (GPIO_GCLK) GPI_O4  7  8   GPIO_14 (TXD0)
#    GND               9  10  GPIO_15 (RXD0)
# (GPIO_GEN0) GPIO_17 11  12  GPIO_18 (GPIO_GEN1)
# (GPIO_GEN2) GPIO_27 13  14  GND                    ---> GND
# (GPIO_GEN3) GPIO_22 15  16  GPIO_23 (GPIO_GEN4)    ---> LED_Dongle
#    + 3,3 V          17  18  GPIO_24 (GPIO_GEN5)    ---> LED_Cadence
# (SPI_MISO) GPIO_9   21  22  GPIO_25 (GPIO_GEN6)    ---> LED_Tacx
# (SPI_SLCK) GPIO_11  23  24  GPIO_8 (SPI_CE0_N)
#    GND              25  26  GPIO_7 (SPI_CE1_N)
# (für I2C) ID_SD     27  28  ID_SC (nur für I2C)
#    GPI_O5           29  30  GND
#    GPI_O6           31  32  GPIO_12
#    GPI_O13          33  34  GND
#    GPI_O19          35  36  GPIO_16
#    GPIO_26          37  38  GPIO 20
#    GND              39  40  GPIO 21
#
# ==============================================================================
if clv.Raspi_LED:           # if LED option is anabled these Pins were inizialized as outputs
    LED_Dongle = LED(23)    # the numbers are the numbers of the IO-Pins of the Raspi         
    LED_Cadence = LED(24)   # Don't forget to add the series resisor of 470 Ohm
    LED_Tacx = LED(25)    

# ==============================================================================
# Functions:    Toggle_LED_Tacx()
#                      
# Called:       toggle()
# ==============================================================================
def Toggle_LED_Tacx():              
     if clv.Raspi_LED:
       LED_Tacx.toggle()

# ==============================================================================
# Functions:    Set_LED_XXX()
#                      
# Set's LED intensity value  0.0 => off  , 1.0 => on
# 
# ==============================================================================
def Set_LED_Tacx(value):
     if clv.Raspi_LED: 
        LED_Tacx.value = value
     
def Set_LED_Dongle(value):
    if clv.Raspi_LED:
        LED_Dongle.value = value

def Set_LED_Cadence(value):
    if clv.Raspi_LED: 
        LED_Cadence.value = value
