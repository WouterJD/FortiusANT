del *.log
rem No              = 0x00      # 0
rem Application     = 0x01      # 1
rem Function        = 0x02      # 2
rem Data1           = 0x04      # 4			antDongle
rem Data2           = 0x08      # 8			usbTrainer
rem Print           = 0x10      # 16
..\pythoncode\FortiusAnt.py -a -g -n -s -d127 -H 0
pause