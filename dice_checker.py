import sys
import time
import serial
from getch import getch, pause
from robot import Robot
from camera import CameraProcessor

class DiceChecker:
  def __init__(self):
    self.check_arguments(argv)
    self.camera = CameraProcessor(int(argv[1]))
    self.camera.callibrate()
    self.camera.setup()
    self.robot = Robot(argv[2])
    self.robot.do_callibration()
    dice = None
    while dice == None:
      dice = self.camera.detected_dice()
    self.robot.set_callibration(dice)
    
  def check_arguments(self, argv):
    if (len(argv) < 2):
      sys.exit("Please supply camera number (probably 0 or 1)")
    if(len(sys.argv) != 3):
      print("Usage: python test_robot.py <serial port> <angle> <stretch>")
      print("Please supply the path of the serial port (for instance /dev/tty.usbserial-A6031W5L)")
      sys.exit(1)
    
  def run(argv): 
    while True:
      try:
         camera.process()
         dice = camera.detected_dice()
         robot.pickup(&dice); 
         time.sleep(3000)
      except Exception as e:
        print(e)
    
   
DiceChecker(argv).run()