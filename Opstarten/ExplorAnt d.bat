rem cd ..\pythoncode
del ExplorANT*.log
rem No              = 0x00      # 0
rem Application     = 0x01      # 1
rem Function        = 0x02      # 2
rem Data1           = 0x04      # 4			antDongle
rem Data2           = 0x08      # 8			usbTrainer
rem Print           = 0x10      # 16
rem ExplorAnt.py -h
rem pause
rem ExplorAnt.py -d1 -D 4105
rem ExplorAnt.py -d1 -D 4105 -H 507
..\pythoncode\ExplorAnt.py -d127
pause