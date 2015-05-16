import sys
import time
import serial
import cv2
import threading
from getch import getch, pause
from robot import Robot
from camera import CameraProcessor

class DiceChecker:
  def __init__(self, argv):
    self.check_arguments(argv)
    self.robot = Robot(argv[2])
    self.camera = CameraProcessor(int(argv[1]))
    self.camera.callibrate()
    self.camera.setup()
    self.robot.do_callibration()
    dice = None
    time.sleep(4)
    while dice == None:
      print("Trying to detect dice")
      self.camera.process()
      dice = self.camera.detected_dice()
      time.sleep(1)
    self.robot.set_callibration(dice)
    
  def check_arguments(self, argv):
    if (len(argv) < 2):
      sys.exit("Please supply camera number (probably 0 or 1)")
    if(len(sys.argv) != 3):
      print("Usage: python test_robot.py <serial port> <angle> <stretch>")
      print("Please supply the path of the serial port (for instance /dev/tty.usbserial-A6031W5L)")
      sys.exit(1)
    
  def run_analyzer(self):
    while True:
      self.camera.process();
      key = cv2.waitKey(1)
      if key & 0xFF == ord('s'):
        self.camera.save_frame()
      
  def run(self): 
    self.analyze_thread = threading.Thread(target=self.run_analyzer)
    self.analyze_thread.setDaemon(True)
    self.analyze_thread.start()
    while True:
       dice = self.camera.detected_dice()
       if dice != None:
         self.robot.pickup(*dice); 
       time.sleep(10)
       
DiceChecker(sys.argv).run()