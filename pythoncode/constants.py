#-------------------------------------------------------------------------------
# Version info
#-------------------------------------------------------------------------------
__version__ = "2021-01-07"
# 2021-01-07    UseMultiProcessing moved here
# 2020-12-20    Constants moved to constants.py
#-------------------------------------------------------------------------------
mode_Basic          = 0     # Basic Resistance
mode_Power          = 1     # Target Power
mode_Grade          = 2     # Target Resistance

#-------------------------------------------------------------------------------
# 'directives' to exclude parts from the code
# For example for small footprint implementations
#-------------------------------------------------------------------------------
UseBluetooth        = True
UseGui              = True      # Not yet tested
UseMultiProcessing  = True      # Production version can be either False or True