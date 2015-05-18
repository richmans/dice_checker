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
    self.results = [0,0,0,0,0,0]
    dice = None
    time.sleep(4)
    while dice == None:
      print("Trying to detect dice")
      self.camera.process()
      dice = self.camera.detected_dice()
      cv2.waitKey(1000)
    self.robot.set_callibration(dice)
    
  def check_arguments(self, argv):
    if (len(argv) < 2):
      sys.exit("Please supply camera number (probably 0 or 1)")
    if(len(sys.argv) != 3):
      print("Usage: python test_robot.py <serial port> <angle> <stretch>")
      print("Please supply the path of the serial port (for instance /dev/tty.usbserial-A6031W5L)")
      sys.exit(1)
    
  def count_results(self, points):
    if (points >6 or points < 1):
      print("Misdetection: %d points" % points)
      return
    self.results[points-1] += 1
    
  def report_results(self):
    total = sum(self.results)
    expected = float(1) / 6
    print("Dice totals: %s" % self.results)
    for i in range(1,5):
      ratio = float(self.results[i]) / total
      less = "less" if ratio < expected else "more"
      difference = abs(ratio - expected) * 100
      print("%d was thrown %d %s than expected" % (i+1, difference, less))
 
  def handle_key(self, key):
    if key & 0xFF == ord('x'):
      sys.exit(0)
    if key & 0xFF == ord('s'):
      self.camera.save_frame()
    if key & 0xFF == ord('r'):
      self.report_results() 
           
  def run(self): 
    while True:
       print("Detection")
       dice = self.camera.detected_dice()
       if dice != None:
         print("Pickup")
         self.robot.pickup(*dice); 
       print("Key wait")
       key = cv2.waitKey(12000)
       self.handle_key(key)
       print("Camproc")
       self.camera.process();
       print("Resultcount")
       self.count_results(self.camera.analyzer.points)
       
DiceChecker(sys.argv).run()