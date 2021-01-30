
import FortiusAntCommand    as cmd


clv = cmd.CommandLineVariables()
if clv.Raspi_LED: 
 
     import sys
     from gpiozero import LED

if clv.Raspi_LED:
    LED_Tacx = LED(25)
    LED_Dongle = LED(23)
    LED_Cadence = LED(24)


def Toggle_LED_Tacx():
     if clv.Raspi_LED:
       LED_Tacx.toggle()


def Set_LED_Tacx(value):
     if clv.Raspi_LED: 
        LED_Tacx.value = value
     
def Set_LED_Dongle(value):
    if clv.Raspi_LED:
        LED_Dongle.value = value

def Set_LED_Cadence(value):
    if clv.Raspi_LED: 
        LED_Cadence.value = value
