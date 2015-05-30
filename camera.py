import cv2
import numpy as np
import sys
from analyzer import Analyzer
import time
import uuid
import os
class CameraProcessor:
  def __init__(self, camera, gui):
    self.analyzer = Analyzer(gui)
    self.cap = cv2.VideoCapture(camera)
    self.callibration_state = 0
    self.callibration_message = [
      "Please click the plus sign with the circle around it",
      "Please click the plus sign WITHOUT the circle around it",
      "Got it!"
    ]
    self.create_images_dir()
    self.gui = gui
    gui.subscribe('color_threshold', self)
    gui.subscribe('blob_threshold', self)
    gui.subscribe('area_threshold', self)
    
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
    self.analyzer.analyze(resized, frame)
  
  
  def set_parameter(self, name, value):
    if name == 'color_threshold':
      self.analyzer.color_threshold = value
    elif name == 'blob_threshold':
      self.analyzer.blob_threshold = value
    elif name == 'area_threshold':
      self.analyzer.set_area_threshold(value * 100)
    
  def report_blobs(self):
    self.analyzer.report()
  
  def teardown(self):
    self.cap.release()
    
  def run_test(self):
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
