import time
import serial
import threading
import sys
import math
from utils import calculate_distance
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
    
  def do_callibration(self):
    raw_input("Press enter when the dice is placed on the holder")
    self.send_command([99])
    time.sleep(2)

  def set_callibration(self, callibrated_dice):
    self.stretch_distance = callibrated_dice[1] - 180
    self.zero_angle_x = callibrated_dice[0]
    print("Callibration %d, %d" % (self.zero_angle_x, self.stretch_distance))
    
  def read_input(self):
    while True:
      sys.stdout.write("ROBOT: %s" % self.serial.readline())
      
  def interactive(self):
    self.send_command([i])
  
  def release(self):
    self.send_command([111])
    
  def pickup(self, x, y):
    # calculate the distance to the center of the arm, that is the stretch
    stretch = int(calculate_distance((x,y), (self.zero_angle_x, self.stretch_distance)))
    #print("Stretch calc: distance((%d,%d),(%d,%d) = %d" % (x,y,self.zero_angle_x,  self.stretch_distance, stretch) )
    # sin(a) = distx / stretch
    robot_stretch = stretch - 100
    distx = x - self.zero_angle_x
    print("Distx %f, stretch %d" % (distx, robot_stretch))
    angle = int(round(math.degrees(math.asin(float(distx) / stretch))))
    # set the first bit to 1 if angle is positive
    angle_byte = abs(angle)
    if angle > 0: angle_byte += 128 
    print("Sending command 112, %d, %d" % (angle_byte, robot_stretch))
    self.send_command([112, angle_byte, robot_stretch])
    
    
  def send_command(self, command):
    command_bytes = bytearray(command)
    self.serial.write(command_bytes)
  