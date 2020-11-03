
import requests
import logfile


class BleInterface:
  def __init__(self, host, port):
    self.host = host
    self.port = port

  def write(self, data):
    r = requests.post(f'http://{self.host}:{self.port}/ant', data=data)
    print(r.text)

  def read(self, data):
    r = requests.get(f'http://{self.host}:{self.port}/ant')
    print(r.text)


class BleDongle:
  OK = True
  Message = 'BleDongle'
  DongleReconnected = False

  def __init__(self):
    self.interface = BleInterface('localhost', 9999)

  def __GetDongle(self):
    pass

  def Write(self, data, receive=True, drop=True):
    self.interface.write(data)
    return []

  def ApplicationRestart(self):
    pass

  def __ReadAndRetry(self):
    pass

  def Read(self, drop):
    return []

  def Calibrate(self):
    pass

  def ResetDongle(self):
    pass

  def SlavePair_ChannelConfig(self, channel_pair, DeviceNumber=0, DeviceTypeID=0, TransmissionType=0):
    pass

  def Trainer_ChannelConfig(self):
    pass

  def SlaveTrainer_ChannelConfig(self, DeviceNumber):
    pass

  def HRM_ChannelConfig(self):
    pass

  def SlaveHRM_ChannelConfig(self, DeviceNumber):
    pass

  def PWR_ChannelConfig(self, DeviceNumber):
    pass

  def SCS_ChannelConfig(self, DeviceNumber):
    pass

  def SlaveSCS_ChannelConfig(self, DeviceNumber):
    pass

  def VTX_ChannelConfig(self):                         # Pretend to be a Tacx i-Vortex
    pass

  def SlaveVTX_ChannelConfig(self, DeviceNumber):     # Listen to a Tacx i-Vortex
    pass

  def SlaveVHU_ChannelConfig(self, DeviceNumber):
    pass

  def PowerDisplay_unused(self):
    pass

