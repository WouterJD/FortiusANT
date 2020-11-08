
import requests
import logfile
import json
import subprocess
from pathlib import Path
import atexit

class Singleton(type):
  instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls.instances:
      cls.instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    
    return cls.instances[cls]

class BleInterface(metaclass=Singleton):
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.interface = None
    self.logfile = None

  def write(self, data):
    if self.interface:
      requests.post(f'http://{self.host}:{self.port}/ant', data=data)

  def read(self):
    response = ""
    if self.interface:
      r = requests.get(f'http://{self.host}:{self.port}/ant')
      response = r.text

    return response

  def open(self):
    if self.interface:
      logfile.Console('BLE Interface already open')
    else:
      logfile.Console('Opening BLE interface')
      command = [
        "node",
        "server.js"
      ]
      self.logfile = open('ble.log', 'w')
      directory = Path.cwd().parent / "node"
      self.interface = subprocess.Popen(command, cwd=directory, stdout=self.logfile, stderr=self.logfile)

      def cleanup():
        if self.interface:
          logfile.Console('Stop BLE server')
          self.close()
          logfile.Console('Stopped BLE server')

      # Make sure the BLE server is stopped on program termination
      atexit.register(cleanup)

  def close(self):
    if self.interface:
      self.interface.terminate()
      self.interface.wait()
      self.interface = None
    else:
      logfile.Console('BLE server already stopped')


class BleDongle:
  OK = True
  Message = 'BleDongle'
  DongleReconnected = False

  def __init__(self):
    self.interface = BleInterface('localhost', 9999)
    self.interface.open()

  def __GetDongle(self):
    pass

  def Write(self, data, receive=True, drop=True):
    self.interface.write(data)
    return self.Read(drop=False)

  def ApplicationRestart(self):
    pass

  def __ReadAndRetry(self):
    pass

  def Read(self, drop):
    messages = []
    while True:
      message = self.interface.read()
      if message:
        messages.append(json.loads(message))
      else:
        break
  
    return messages

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

