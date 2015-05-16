import time
import serial
import threading
import sys
class Robot:
  def __init__(self, path):
    self.serial = serial.Serial(path)
    self.reader = threading.Thread(target=self.read_input)
    self.reader.setDaemon(True)
    self.reader.start()
    # default callibration
    self.stretch_distance = 14
    self.zero_angle_x = 170
    # wait for the arm to activate
    time.sleep(2)
    
  def callibrate(self):
    input("Press enter when the dice is placed on the holder")
    self.send_command([99])
    time.sleep(2000)
    callibrated_dice = parent.get_dice()
    self.stretch_distance = callibrated_dice[1] - 80
    self.zero_angle_x = callibrated_dice[0]
  
  def read_input(self):
    while True:
      sys.stdout.write("ROBOT: %s" % self.serial.readline())
      
  def interactive(self):
    self.send_command([i])
  
   
  def pickup(self, x, y):
    # calculate the distance to the center of the arm, that is the stretch
    stretch = self.calculate_distance((x,y), (self.zero_angle_x, -1 * self.stretch_distance))
    # sin(a) = distx / stretch
    distx = x - self.zero_angle_x
    angle = math.asin(distx / stretch)
    self.send_command([112, angle, stretch])
    
    
  def send_command(self, command):
    command_bytes = bytearray(command)
    self.serial.write(command_bytes)
  