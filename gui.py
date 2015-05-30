import sys
import time
import cv2
import numpy as np
class DiceGui:
  frames = {}
  window_name = 'Dice'
  subscribers = {
    "color_threshold": [],
    "blob_threshold": [],
    "area_threshold": [],
  }

  def __init__(self, layout='default', window_name = 'Dice'):
    self.color_threshold = 170
    self.blob_threshold = 11
    self.area_threshold = 1000
    self.window_name = window_name
    self.layout = layout
    self.setup()
    self.frame = np.zeros((600, 1024, 3), np.uint8)
    
  def place(self, name, x, y):
    if name not in self.frames: return
    picture = self.frames[name]
    
    h,w = picture.shape[:2]
    if len(picture.shape) == 2:
      self.frame[y:y+h, x:x+w, 0] = picture
      self.frame[y:y+h, x:x+w, 1] = picture
      self.frame[y:y+h, x:x+w, 2] = picture
    else:
      self.frame[y:y+h, x:x+w, :] = picture
    
  def render(self):
    self.place('Blob', 0, 0)
    self.place('Points', 800,0)
    self.place('Angle', 800,120)
   # show_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    cv2.imshow(self.window_name, self.frame)
    
  def subscribe(self, name, subscriber):
    if self.subscribers[name] == None: self.subscribers[name] = []
    self.subscribers[name].append(subscriber)
  
  def set_frame(self, name, frame):
    self.frames[name] = frame
    self.render()
    
  def notify_subscribers(self, name, value):
    for subscriber in self.subscribers[name]:
      subscriber.set_parameter(name, value)
    
  def on_color_trackbar(self,value):
    self.notify_subscribers('color_threshold', value)
  
  def on_blob_trackbar(self,value):
    self.notify_subscribers('blob_threshold', value)
  
  def on_area_trackbar(self,value):
    self.notify_subscribers('area_threshold', value)
  
  def setup(self):
    self.window = cv2.namedWindow(self.window_name)
    cv2.createTrackbar('Threshold',self.window_name,self.color_threshold,255,self.on_color_trackbar)
    cv2.createTrackbar('Area',self.window_name,self.area_threshold / 100,100,self.on_blob_trackbar)
    cv2.createTrackbar('Blobs',self.window_name,self.blob_threshold,255,self.on_area_trackbar)

  def teardown(self):
    cv2.destroyAllWindows()
    