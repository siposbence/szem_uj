import configparser
#from face2coord_2 import face2coord
import pygame
from pygame.locals import *
import numpy as np
import cv2
import numpy as np
import configparser
from PIL import Image

# Face detection to x-y coordinates
class face2coord:
    def __init__(self, camera, rotate, multi, method, confid):
        # Camera ID
        self.cap = cv2.VideoCapture(camera)
        # Is the camera rotated
        self.rotate = rotate
        # Resolution multiplier (imsize = imsize/multi)
        self.multi = multi
        # Detection method
        self.method = method
        # Some methods require confidence level
        self.confid = confid

        self.small_frame = np.zeros([640,480,3], dtype = 'uint8')
        # Faced package
        if self.method == "tf":
            print("faced")
            from faced import FaceDetector
            from faced.utils import annotate_image            
            self.detector = FaceDetector()
        # Coral skeleton detection
        elif self.method == "coral":
            print("coral")
            from pose_engine import PoseEngine
            self.engine = PoseEngine('posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite')
        # Face recognition package
        else:
            import face_recognition
            print("face_recognition")
        

            
    # Function for reading a frame from camera
    def get_image(self):
        ret, frame = self.cap.read()
        
        # camera works 
        if ret:
            
            # Camera rotation correction
            if self.rotate == "none":
                pass 
            if self.rotate == "clockwise":
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            if self.rotate == "counterclockwise":
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # resize image    
            self.small_frame = cv2.resize(frame, (0, 0), fx=1/self.multi, fy=1/self.multi)
            self.width_cap, self.height_cap, depth = self.small_frame.shape
            
            # For coral we need a specific frame size
            if self.method == "coral":
                self.width_cap, self.height_cap =  (641, 481)
        
        # no image - not connected or in use
        else:
            print("No image from camera")
    
    # function to release the camera
    def release(self):
        self.cap.release()
    
    # face coordinates
    def get_face_coords(self):
        self.get_image()
        if self.method == "tf":
            x, y, w, h, p = (0,0,0,0,0) 
            coords = self.detector.predict(self.small_frame, self.confid)
            if len(coords)==0:
                self.coords = (0.5,0.5)
            for i in coords:
                if i[3]>h:
                    x, y, w, h, p = i
                    self.coords = ((x+w)/2/self.width_cap, (y+h)/2/self.height_cap)
            #top, right, bottom, left, tmp
            #x, y, w, h
        elif self.method == "coral":
            poses, inference_time = self.engine.DetectPosesInImage(Image.fromarray(self.small_frame))
            print(1/inference_time)
            self.coords = (0.5,0.5)
            #print(poses)
            for pose in poses:
                if pose.score < 0.3: continue
                print('\nPose Score: ', pose.score)
                for label, keypoint in pose.keypoints.items():
                    if label.name == "NOSE" and keypoint.score>0.4:
                        self.coords = (keypoint.point[0]/self.width_cap, keypoint.point[1]/self.height_cap)
                        print('  %-20s x=%-4d y=%-4d score=%.1f' %
                              (label.name, keypoint.point[0], keypoint.point[1], keypoint.score))

                    
        else:
            coords = face_recognition.face_locations(self.small_frame)
            top, right, bottom, left, h = (0,0,0,0,0)
            if len(coords)<1:
                self.coords = [0.5, 0.5] # np.random.normal(size = [2])/300 + 0.5
            for i in coords:
                if i[2]- i[0]>h:
                    top, right, bottom, left = i
                    h = -top+bottom
                    self.coords = ((top+bottom)/2/self.width_cap, (right+left)/2/self.height_cap) 
                    #self.width_cap, self.height_cap
        print(self.coords)
        return self.coords

class pygame_eyes():
    def __init__(self, config):
        Config = configparser.ConfigParser()
        Config.read("eyes_coral.conf")
        self.cam = face2coord(camera = int(Config.get("Facedetection", "camera")), 
                              rotate = Config.get("Facedetection", "rotate"),
                              multi = float(Config.get("Facedetection", "multi")), 
                              method = Config.get("Facedetection", "method"), 
                              confid = Config.get("Facedetection", "confid"))

        self.prev_x, self.prev_y = [[0.5],[0.5]]
        self.w, self.h = (int(Config.get("Display", "size_w")),int(Config.get("Display", "size_h")))
        self.screen = pygame.display.set_mode((self.w, self.h), 0, 32)
        pygame.display.set_caption('eyes')
        self.clock = pygame.time.Clock()
        self.running = True
        self.no_face = 0
        self.patienete = 8 
        
    
    def x_y(self):
        return(self.prev_x[-1], self.prev_y[-1])
    
    def display(self, x,y):
        self.screen.fill((255,255,255))
        #x,y = self.x_y()
        pygame.draw.circle(self.screen, (0,0,0), (int(self.h-y*self.h), int(x*self.h)), 100, 0)
        pygame.draw.circle(self.screen, (0,0,0), (int((self.h-y*self.h)+self.h), int(x*self.h)), 100, 0)
    
    def update(self):
        x,y = self.cam.get_face_coords()
        if x == 0.5 and y == 0.5:
            self.no_face += 1
        else:
            self.no_face = 0
        
        if self.no_face > self.patienete or self.no_face == 0:
            self.prev_x.append(x)
            self.prev_y.append(y)
            pygame.display.update()
            #self.clock.tick(90)
        else:
            self.display(self.prev_y[-1], self.prev_x[-1])
            pygame.display.update()
            #self.clock.tick(90)
        
    def kill(self):
        pygame.quit()
        self.cam.release()
        self.running = False
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    run = False
                    
            print("fds")
            self.display()
            pygame.display.update()
            self.clock.tick(30)


import time
tmp = pygame_eyes("eyes_coral.conf")
time.sleep(0.3)
p_time = time.time()
for i in range(200):
    tmp.update()
    c_time = time.time()
    print(1/(c_time-p_time))
    p_time = c_time
    #time.sleep(0.05)
    
tmp.kill()

