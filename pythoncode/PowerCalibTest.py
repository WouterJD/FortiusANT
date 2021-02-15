import PowerCalibTab as cal
import numpy as np



PowerTab=cal.OpenPowerTab('../PowerTab/ActivPwTab.dat')
print(PowerTab)
#while True:
#    speed = float(input("speed/kmh? "))
#    power = float(input("power/W? "))
#    CorrFactor=cal.CalcCorrFactor(PowerTab,speed,power)
#    PowerCorr=power/CorrFactor
#    print(speed,"kmh	",power,"W	",PowerCorr,"W")
    
x = np.array([[power/cal.CalcCorrFactor(PowerTab,speed,power) for power in range(0,350,25)] for speed in range(0,80,5)])
np.set_printoptions(precision=0)
print (x) 