del *.log FortiusAnt.*.json *.tcx
rem No              = 0x00      # 0
rem Application     = 0x01      # 1
rem Function        = 0x02      # 2
rem Data1           = 0x04      # 4			antDongle
rem Data2           = 0x08      # 8			usbTrainer
rem Multiprocessing = 0x10      # 16
..\pythoncode\FortiusAnt.py -g -H0 -d127
pause