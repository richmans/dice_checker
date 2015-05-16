import cv2
import numpy as np
import sys
from analyzer import Analyzer
import time

class CameraProcessor:
  def __init__(self, camera):
    self.analyzer = Analyzer()
    self.cap = cv2.VideoCapture(camera)
    self.callibration_state = 0
    self.callibration_message = [
      "Please click the plus sign with the circle around it",
      "Please click the plus sign WITHOUT the circle around it",
      "Got it!"
    ]
  def handle_callibration_click(self, event,x,y,flags,param):
    if event == 1:
      self.analyzer.set_callibration(self.callibration_state, (x,y))
      print("Setting callibration point %d to (%d, %d)" % (self.callibration_state, x, y))
      self.callibration_state += 1
      print(self.callibration_message[self.callibration_state])
      
  def callibrate(self):
    ret, frame = self.cap.read()
    resized = cv2.resize(frame, (800,600))
    cv2.imshow( "callibration" ,resized)
    cv2.setMouseCallback('callibration',self.handle_callibration_click)
    print(self.callibration_message[self.callibration_state])
    while self.callibration_state < 2:
      cv2.waitKey(1)
    cv2.destroyWindow("callibration")
    
  def process(self):
    ret, frame = self.cap.read()
    resized = cv2.resize(frame, (800,600))
    self.analyzer.analyze(resized, 'frame')
    
  def on_trackbar(self,value):
    self.analyzer.color_threshold = value
  
  def on_area_trackbar(self,value):
    self.analyzer.set_area_threshold(value * 100)
    
  def report_blobs(self):
    self.analyzer.report()
    
  def main(self):
    self.window = cv2.namedWindow('frame')
    cv2.createTrackbar('Threshold','frame',self.analyzer.color_threshold,255,self.on_trackbar)
    cv2.createTrackbar('Area','frame',self.analyzer.area_threshold / 100,100,self.on_area_trackbar)
    
    while True:
      self.process()
      key = cv2.waitKey(1)
      if key & 0xFF == ord('q'):
        break
      if key & 0xFF == ord('r'):
        self.report_blobs()
    self.cap.release()
    cv2.destroyAllWindows()
