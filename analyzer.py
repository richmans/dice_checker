import numpy as np
import cv2
import math 
class Analyzer: 
    def __init__(self):
        self.color_threshold = 183
        self.area_threshold = 1000
        self.params = cv2.SimpleBlobDetector_Params()
        self.params.filterByArea = True
        self.params.minArea = self.area_threshold
        self.params.maxArea = 10000
        self.params.filterByCircularity = False
        self.params.filterByConvexity = False
        self.params.filterByInertia = False
        self.params.filterByColor = False
        self.params.minRepeatability = 1
        self.detector = cv2.SimpleBlobDetector(self.params)
        self.detected_dice = []
        self.callibration_points = [(10,10),(0,0)]
        self.callibration_reference = [
            (20,15.5),
            (2,3)
        ]
    def set_area_threshold(self, threshold):
        self.area_threshold = threshold
        self.params.minArea = self.area_threshold
        self.detector = cv2.SimpleBlobDetector(self.params)
    
    def set_callibration(self, point_index, point):
        self.callibration_points[point_index] = point
    
    # Calculate distance between two points using pythagoras
    def calculate_distance(self, point1, point2):
        legx = (point1[0] - point2[0]) ** 2
        legy = (point1[1] - point2[1]) ** 2
        return math.sqrt(legx + legy)

    # calculate the angle a in a triangle with three known lengths
    # to calculate other angles, just juggle the arguments around
    def calculate_angle_from_lengths(self, vla, vlb, vlc):
        return math.acos((vla ** 2 - vlb ** 2 - vlc ** 2) / (-2 * vlb * vlc))
    
    def calculate_length_from_angles_and_length(self, vaa, vab, vlb):
        return math.asin( (vlb / math.sin(vab)) * math.sin(vaa))
            
    # Converts measured coordinates to real coordinates
    # Lots of math in here, hope the documentation helps.
    # variable convention: 
    # * first letter r for real, v for virtual
    # * second: p for point, a for angle, l for length
    # * third: index, mostly a-z
    # * Output: x/y coordinates in real space
    def convert_coordinates(self, vpc):
        vpa = self.callibration_points[0]
        vpb = self.callibration_points[1]
        rpa = self.callibration_reference[0]
        rpb = self.callibration_reference[1]
        
        # step 1, calculate the virtual distance between all points
        # vla is the line that does not connect to vpa, etc
        vla = self.calculate_distance(vpc, vpb)
        vlb = self.calculate_distance(vpa, vpc)
        vlc = self.calculate_distance(vpb, vpc)
        
        # step 2, calculate the angles of each point
        vaa = self.calculate_angle_from_lengths(vla, vlb, vlc)
        vab = self.calculate_angle_from_lengths(vlb, vla, vlc)
        vac = self.calculate_angle_from_lengths(vlc, vla, vla)
        
        # step 3, calculate the triangle lengths in real
        # rlc is the line not connected to c, between the two reference points
        rlc = self.calculate_distance(rpa, rpb)
        rla = self.calculate_length_from_angles_and_length(vaa, vac, rlc)
        rlb = self.calculate_length_from_angles_and_length(vab, vac, rlc)
        
        ## step 4 calculate the angles of the real reference points with horizontal and vertical
        ## These 2 corners d and e are added to corners a and b
        rld = rpb[0] - rpa[0]
        rle = rpa[1] - rpb[1]
        rad = self.calculate_angle_from_lengths(rld, rle, rlc)
        rae = self.calculate_angle_from_lengths(rle, rld, rlc)
        
        racx = 90 - (rab+rae) # angle of b-c at rpc with vertical
        
        ## calculate x distance from refrence point b
        rlx = self.calculate_length_from_angles_and_length(racx, 90, rlb)
        rly = math.sqrt(rlb ** 2 - rlx ** 2)
        
        return (rpb[0] - rlx, rpb[1] - rly)
        
    def analyze(self, im, window_name):
        original = im
        kernel = np.ones((5,5), np.uint8)
        im = cv2.GaussianBlur(im, (7,7), 0)
        #im = cv2.erode(im, kernel, iterations=1)
        what, im = cv2.threshold(im, self.color_threshold, 256, 1)
        
        im = cv2.GaussianBlur(im, (5,5), 0)
        cimg = cv2.split(im)[2]
        self.keypoints = self.detector.detect(cimg)
        im_with_keypoints = cv2.drawKeypoints(original, self.keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #print("Found %d blobs" % len(keypoints)) 
        #print("Area %f" % keypoints[0].size)
        self.detected_dice = map(lambda x: self.convert_coordinates((x.pt[0], x.pt[1])), self.keypoints)
        info = "treshold %d, area %d, %d blobs" % (self.color_threshold, self.area_threshold, len(self.keypoints))
        cv2.putText(im_with_keypoints, info, (0, 580), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0),1)
        if len(self.detected_dice) > 0:
            cv2.putText(im_with_keypoints, "Dice (%d, %d)", (0, 10), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0),1)
        cv2.imshow( "frame" ,im_with_keypoints)

        
        
    def report(self):
        print("Printing keypoints")
        if len(self.keypoints) == 0:
            print("No keypoints detected")
            
        for dice in self.detected_dice:
            print("Dice: (%d,%d)" % dice)