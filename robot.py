import time
import serial
import threading
class Robot:
  def __init__(self, path):
    self.serial = serial.Serial(path)
    self.reader = threading.Thread(target=self.read_input)
    self.reader.setDaemon(True)
    self.reader.start()
    time.sleep(2)
  
  def read_input(self):
    while True:
      print("ROBOT: %s" % self.serial.readline().rstrip())
      
  def interactive(self):
    self.send_command([i])
    
  def pickup(self, angle, stretch):
    self.send_command([112, angle, stretch])
    
    
  def send_command(self, command):
    command_bytes = bytearray(command)
    self.serial.write(command_bytes)
  