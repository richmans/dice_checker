import cv2
import numpy as np
import sys
from analyzer import Analyzer
import time
import uuid
import os
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
    self.create_images_dir()
  
  def create_images_dir(self):
    try:
      os.mkdir("images")
    except:
      pass
      
  def handle_callibration_click(self, event,x,y,flags,param):
    if event == 1:
      self.analyzer.set_callibration(self.callibration_state, (x,y))
      print("Setting callibration point %d to (%d, %d)" % (self.callibration_state, x, y))
      self.callibration_state += 1
      print(self.callibration_message[self.callibration_state])
      
  def callibrate(self):
    cv2.namedWindow('callibration')
    cv2.setMouseCallback('callibration',self.handle_callibration_click)
    print(self.callibration_message[self.callibration_state])
    while self.callibration_state < 2:
      ret, frame = self.cap.read()
      resized = cv2.resize(frame, (800,600))
      cv2.imshow( "callibration" ,resized)
      cv2.waitKey(1)
    cv2.destroyWindow("callibration")
    
  def detected_dice(self):
    if len(self.analyzer.detected_dice) == 0: return None 
    return self.analyzer.detected_dice[0]
  
  def save_frame(self):
    filename = "images/%s.jpg" % str(uuid.uuid4())
    ret, frame = self.cap.read()
    print("Writing %s" % filename)
    cv2.imwrite(filename, frame)
    
  def process(self):
    ret, frame = self.cap.read()
    self.process_image(frame)
    
  def process_image(self, frame):
    resized = cv2.resize(frame, (800,600))
    self.analyzer.analyze(resized, frame, 'frame')
  
  def on_trackbar(self,value):
    self.analyzer.color_threshold = value
  
  def on_blob_trackbar(self,value):
    self.analyzer.blob_threshold = value
  
  def on_area_trackbar(self,value):
    self.analyzer.set_area_threshold(value * 100)
    
  def report_blobs(self):
    self.analyzer.report()
  
  def setup(self):
    self.window = cv2.namedWindow('frame')
    cv2.createTrackbar('Threshold','frame',self.analyzer.color_threshold,255,self.on_trackbar)
    cv2.createTrackbar('Area','frame',self.analyzer.area_threshold / 100,100,self.on_area_trackbar)
    cv2.createTrackbar('Blobs','frame',self.analyzer.blob_threshold,255,self.on_blob_trackbar)
  def teardown(self):
    self.cap.release()
    cv2.destroyAllWindows()
    
  def run_test(self):
    self.setup();
    while True:
      self.process()
      key = cv2.waitKey(1)
      if key & 0xFF == ord('q'):
        break
      if key & 0xFF == ord('r'):
        self.report_blobs()
      if key & 0xFF == ord('s'):
        self.save_frame()
    self.teardown()
