import numpy as np
import cv2
import math 
from utils import calculate_distance
class Analyzer: 
    def __init__(self, gui):
        self.color_threshold = gui.color_threshold
        self.blob_threshold = gui.blob_threshold
        self.area_threshold = gui.area_threshold
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
        self.callibration_points = [(728,573),(43,143)]
        self.callibration_reference = [
            (200,155),
            (20,30)
        ]
        self.check_parameter = 0
        self.points = 0
        self.gui = gui
        
    def set_area_threshold(self, threshold):
        self.area_threshold = threshold
        self.params.minArea = self.area_threshold
        self.detector = cv2.SimpleBlobDetector(self.params)
    
    def set_callibration(self, point_index, point):
        self.callibration_points[point_index] = point
    
    
    # calculate the angle a in a triangle with three known lengths
    # to calculate other angles, just juggle the arguments around
    def calculate_angle_from_lengths(self, vla, vlb, vlc):
        return math.acos((vla ** 2 - vlb ** 2 - vlc ** 2) / (-2 * vlb * vlc))
    
    def calculate_length_from_angles_and_length(self, vaa, vab, vlb):
        return  (vlb / math.sin(vab)) * math.sin(vaa)
            
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
      
        # check if the point is above or below the callibration line.. usefull later
        # Note: This asumes that the camera is at least a little straight!
        above_line = (float(vpa[1] - vpb[1]) / (vpa[0] - vpb[0]) * (vpc[0] - vpb[0]) + vpb[1]) > vpc[1]
        
        # step 1, calculate the virtual distance between all points
        # vla is the line that does not connect to vpa, etc
        vla = calculate_distance(vpc, vpb)
        vlb = calculate_distance(vpa, vpc)
        vlc = calculate_distance(vpb, vpa)
        # The easy case: the dice is on one of the reference points
        if vla < 5: return rpb
        if vlb < 5: return rpa
        
        #print("Virtual distances: vla %f, vlb %f, vlc %f " % (vla, vlb, vlc))
        # step 2, calculate the angles of each point
        vaa = self.calculate_angle_from_lengths(vla, vlb, vlc)
        vab = self.calculate_angle_from_lengths(vlb, vla, vlc)
        vac = math.pi - vaa - vab
        #print("Virtual angles: vaa %f, vab %f, vac %f" % (vaa, vab, vac))
        # step 3, calculate the triangle lengths in real
        # rlc is the line not connected to c, between the two reference points
        rlc = calculate_distance(rpa, rpb)
        rla = self.calculate_length_from_angles_and_length(vaa, vac, rlc)
        rlb = self.calculate_length_from_angles_and_length(vab, vaa, rla)
        #print("Real lengths rla %f, rlb %f, rlc %f" % (rla, rlb, rlc))
        ## step 4 calculate the angles of the real reference points with horizontal and vertical
        ## These 2 corners d and e are added to corners a and b
        rld = rpa[0] - rpb[0]
        rle = rpa[1] - rpb[1]
        #print("Lengths of the callibration triangle %f %f %f" % (rld, rle, rlc))
        rad = self.calculate_angle_from_lengths(rld, rle, rlc)
        rae = self.calculate_angle_from_lengths(rle, rlc, rld)
        #print("Callibration angles rad %f, rae %f" % (rad, rae))
        
        rabx =   rae-vab if above_line else rae+vab
        #print("Angle of rla to horizontal %f" % rabx)
        ## calculate x distance from refrence point b
        rlx = math.cos(rabx) * rla
        #self.calculate_length_from_angles_and_length(rabx, 0.5 * math.pi, rla)
        
        
        rly = math.sqrt(rla ** 2 - rlx ** 2)
        #print("Distances rlx %f rly %f" % (rlx, rly))
        return (rpb[0] + rlx, rpb[1] + rly)
    
    def analyze(self, im, original):
        oim = im
        kernel = np.ones((5,5), np.uint8)
        im = cv2.GaussianBlur(im, (7,7), 0)
        #im = cv2.erode(im, kernel, iterations=1)
        what, im = cv2.threshold(im, self.color_threshold, 256, 1)
    
        im = cv2.GaussianBlur(im, (5,5), 0)
        cimg = cv2.split(im)[2]
        self.keypoints = self.detector.detect(cimg)
        im_with_keypoints = 255 - cimg
        im_with_keypoints = cv2.drawKeypoints(im_with_keypoints, self.keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #print("Found %d blobs" % len(keypoints)) 
        #print("Area %f" % keypoints[0].size)
        self.detected_dice = map(lambda x: self.convert_coordinates((x.pt[0], x.pt[1])), self.keypoints)
        
        info = "treshold %d, area %d, %d blobs" % (self.color_threshold, self.area_threshold, len(self.keypoints))
        cv2.putText(im_with_keypoints, info, (0, 580), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0),1)
        if len(self.detected_dice) > 0:
            x,y= self.detected_dice[0]
            self.points = self.analyze_points(original, self.keypoints[0].pt)
            self.angle = self.analyze_angle(original, self.keypoints[0].pt)
            if  x != None and y != None and self.points != None:
                dice_info = "Dice (%d, %d) %d" % (x, y, self.points)
                cv2.putText(im_with_keypoints, dice_info, (0, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0),1)
        self.gui.set_frame("Blob", im_with_keypoints)
    # detects the orientation of the dice, so that the arm knows how far to rotate
    # the gripper for optimal pickup. Returns a number between 0 and 90, 0 if unable
    # to detect the dice
    # This function does not take into account that optimal gripper rotation may differ
    # from dice orientation when the location is close to the edge of the arena
    def analyze_angle(self, im, coordinates):
        if im == None: return
        x=coordinates[0]
        y=coordinates[1]
        dice_size = 100
        dice = np.copy(im[y*2-dice_size:y*2+dice_size, x*2-dice_size:x*2+dice_size])  
        original_dice = dice
        
        kernel = np.ones((5,5), np.uint8)
        
        # use thresholds to get shap edges, and convert to grayscale
        dice = cv2.GaussianBlur(dice, (7,7), 0)
        what, dice = cv2.threshold(dice, self.color_threshold, 256, 1)
        dice = cv2.GaussianBlur(dice, (5,5), 0)
        if dice == None: return
        dice = cv2.split(dice)[2]
        
        dice = cv2.Canny(dice,50,150,apertureSize = 3)
        
        lines = cv2.HoughLines(dice,1,np.pi/180,30) 
        if lines == None: return 0
        theta = lines[0][0][1]
        rho = lines[0][0][0]
        formatted_angle = int(math.degrees(theta))  % 90

        print("Detected angle: %d" % formatted_angle)
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        

        cv2.line(original_dice,(x1,y1),(x2,y2),(0,0,255),2)
        self.gui.set_frame("Angle", original_dice)  
        return formatted_angle 
        
    def analyze_points(self, im, coordinates):
        self.points = 0
        if im == None: return
        x=coordinates[0]
        y=coordinates[1]
        dice_size = 60
        dice = np.copy(im[y*2-dice_size:y*2+dice_size, x*2-dice_size:x*2+dice_size])  
        original_dice = dice
        dice = cv2.cvtColor(dice, cv2.COLOR_BGR2GRAY);
        dice = cv2.GaussianBlur(dice, (11,11), 0)   
        if dice == None: return
        circles = cv2.HoughCircles(dice,cv2.HOUGH_GRADIENT,1,10,
                                    param1=130,param2=15,minRadius=5 ,maxRadius=20)
        
        result = 0 if circles == None else len(circles[0])
        if result > 0:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # draw the outer circle
                cv2.circle(original_dice,(i[0],i[1]),i[2],(0,255,0),2)
            
        self.gui.set_frame("Points", original_dice)
        return result
        
    def report(self):
        print("Printing keypoints")
        if len(self.keypoints) == 0:
            print("No keypoints detected")
            
        for dice in self.detected_dice:
            print("Dice: (%d,%d)" % dice)