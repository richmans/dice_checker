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
    self.success_pickups = 0
    self.fail_pickups = 0
    self.results = [0,0,0,0,0,0]
    dice = None
    self.sleep(4000)
    while dice == None:
      print("Trying to detect dice")
      self.camera.process()
      dice = self.camera.detected_dice()
      self.sleep(2000)
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
    if total > 0:
      for i in range(1,6):
        ratio = float(self.results[i]) / total
        less = "less" if ratio < expected else "more"
        difference = abs(ratio - expected) * 100
        print("%d was thrown %d%% %s than expected" % (i+1, difference, less))
    pickup_ratio = 0
    total_pickups = self.success_pickups + self.fail_pickups
    if (self.success_pickups > 0): pickup_ratio = (float(self.success_pickups) / total_pickups) * 100
    print("Total %d pickups, %d good ones (%d%%)" % (total_pickups, self.success_pickups, pickup_ratio))
 
  def handle_key(self, key):
    if key & 0xFF == ord('x'):
      sys.exit(0)
    if key & 0xFF == ord('s'):
      self.camera.save_frame()
    if key & 0xFF == ord('r'):
      self.report_results() 
      
  def sleep(self, duration):
    key = cv2.waitKey(duration) 
    if key != -1:
      self.handle_key(key)    
      cv2.waitKey(duration)
    
  def run(self): 
    while True:
       print("Detection")
       dice = self.camera.detected_dice()
       if dice == None:
         print("Error: no dice detected")
         self.sleep(2000)
         self.camera.process();
         continue
       print("Pickup")
       self.robot.pickup(*dice);
       key = self.sleep(10000)
       self.camera.process();
       dice = self.camera.detected_dice()
       if dice != None:
         print("Error: wrong pickup, trying again")
         self.robot.release()
         self.fail_pickups += 1
         self.sleep(3000)
         continue
        
       print("Pickup ok. Releasing")
       self.success_pickups += 1
       self.robot.release()
       self.sleep(4000)
       print("Camproc")
       self.camera.process();
       print("Resultcount")
       self.count_results(self.camera.analyzer.points)
       
DiceChecker(sys.argv).run()