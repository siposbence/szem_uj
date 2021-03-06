import random
import time
import threading
import configparser
#from face2coord_2 import face2coord
import pygame
from pygame.locals import *
import numpy as np
import cv2
import numpy as np
import configparser
from PIL import Image
import sys
import multiprocessing


from quart import Quart, request, jsonify

#from flask import Flask, request, jsonify

#app=Flask(__name__)

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


class SharedObj(object):
    x = 0
    y = 0
    die = False



class CalcThread(threading.Thread): #.Process):
    def __init__(self, shared, *args, **kwargs):
        super(CalcThread,self).__init__(*args, **kwargs)
        self.shared = shared
        Config = configparser.ConfigParser()
        Config.read("eyes_coral.conf")
        self.cam = face2coord(camera = int(Config.get("Facedetection", "camera")), 
                              rotate = Config.get("Facedetection", "rotate"),
                              multi = float(Config.get("Facedetection", "multi")), 
                              method = Config.get("Facedetection", "method"), 
                              confid = Config.get("Facedetection", "confid"))

    def run(self):
        while(not self.shared.die):
            x,y = self.cam.get_face_coords()
            self.shared.x = x
            self.shared.y = y
            print("coral")
            #time.sleep(1)
        self.cam.release()

app=Quart(__name__)


@app.route('/control', methods=['POST'])
def control():
    data = request.get_json(force = True)
    print('control/ called')
    print('data: ' + str(data))

    if data and 'command' in data:
        if data['command'] == 'start':
            if 'mode' in data:
                if data['mode'] == 'black':
                    print('Set eyes to black')
                elif data['mode'] == 'normal':
                    print('Set eyes to normal')
                elif data['mode'] == 'anime':
                    print('Set eyes to kawai')
            else:
                print('No mode was specified fallback to default')
            print('Eyes are turned on')
        elif data['command'] == 'stop':
            print('Everithing is black now')
        else:
            print('Invalid command is provided')
            return "error: invalid command"
            
    return "ok"




shared_obj = SharedObj()
thread = CalcThread(shared_obj)
thread.start()

print("Szia")
target = app.run(host='0.0.0.0', port=5005, debug=False, threaded=True)
print("GEC??")
pygame.init()

window = pygame.display.set_mode((1600, 800))

background = pygame.Surface((window.get_size()))
background.fill((255, 255, 255))
image  = pygame.image.load('pupilla_2.png').convert_alpha()
image = pygame.transform.scale(image, (800, 800))

image_bg_R = pygame.image.load('szem_2.png')
image_bg_R = pygame.transform.scale(image_bg_R, (800, 800))

image_bg_L = pygame.transform.flip(image_bg_R, True, False)
image_bg_L = pygame.transform.scale(image_bg_L, (800, 800))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    window.fill((255, 255, 255))
    window.blit(background, background.get_rect())
    window.blit(image_bg_L, (0,0))
    window.blit(image_bg_R, (800,0))
    window.blit(image, ((shared_obj.x-.5)*50+100, (shared_obj.y-.5)*50))
    window.blit(image, ((shared_obj.x-.5)*50+800, (shared_obj.y-.5)*50))
    print(shared_obj.x)
    
    #pygame.draw.circle(background, (0, 0, 255), (shared_obj.x, shared_obj.y), 75)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

shared_obj.die = True
time.sleep(0.1)
#app.shutdown()
thread.join()
pygame.quit()



