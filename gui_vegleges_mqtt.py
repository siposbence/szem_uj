import random
import time
import threading
import configparser

from numpy.lib.twodim_base import triu
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
import threading
import time
import paho.mqtt.client as mqtt
import os
import json



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
            #LEFT_EYE = 1
            #RIGHT_EYE = 2
            max_dist = 0
            for pose in poses:
                if pose.score < self.confid: continue
                #print('\nPose Score: ', pose.score)
                left_coords = right_coords = 0
                left_bool = right_bool = False
                save_bool = True
                for label, keypoint in pose.keypoints.items():
                    if label.name == "LEFT_EYE" and keypoint.score>self.confid:
                        left_coords = keypoint.point[0]/self.width_cap
                        left_bool = True
                    if label.name == "RIGHT_EYE" and keypoint.score>self.confid:
                        right_coords = keypoint.point[0]/self.width_cap
                        right_bool = True
                    
                    if left_bool and right_bool:
                        if abs(left_coords-right_coords)>max_dist:
                            max_dist = abs(left_coords-right_coords)
                            save_bool = True

                    if label.name == "NOSE" and keypoint.score>self.confid:
                        if save_bool:
                            self.coords = (keypoint.point[0]/self.width_cap, keypoint.point[1]/self.height_cap)
                        #print(max_dist)
                        #print('  %-20s x=%-4d y=%-4d score=%.1f' %
                        #      (label.name, keypoint.point[0], keypoint.point[1], keypoint.score))

                    
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
        ################################x
        #print(self.coords)
        return self.coords


class SharedObj(object):
    x = 0
    y = 0
    x_list = []
    y_list = []
    blink_seq = 0 
    no_face_since = 0
    die = False
    running_coral = True



class CalcThread(threading.Thread): #.Process):
    def __init__(self, shared, *args, **kwargs):
        super(CalcThread,self).__init__(*args, **kwargs)
        self.shared = shared
        Config = configparser.ConfigParser()
        Config.read("eyes_coral.conf")
        self.cam = face2coord(camera = -1,     #int(Config.get("Facedetection", "camera")), 
                              rotate = 'none', #Config.get("Facedetection", "rotate"),
                              multi = 1,       #float(Config.get("Facedetection", "multi")), 
                              method = 'coral',#Config.get("Facedetection", "method"), 
                              confid = 0.3)    #Config.get("Facedetection", "confid"))

    def run(self):
        while(not self.shared.die):
            while(self.shared.running_coral):
                x,y = self.cam.get_face_coords()

                if x == 0.5 and y == 0.5:
                    self.shared.no_face_since += 1
                else:
                    self.shared.no_face_since = 0

                if self.shared.no_face_since == 0 or self.shared.no_face_since > 15:
                    self.shared.x_list.append(x)
                    self.shared.y_list.append(y)
                    
                if len(self.shared.x_list)>10:
                    self.shared.x_list.pop(0)
                    self.shared.y_list.pop(0)
                self.shared.x = np.mean(self.shared.x_list)
                self.shared.y = np.mean(self.shared.y_list)
            #print("coral")
            #time.sleep(1)
        self.cam.release()





shared_obj = SharedObj()
thread = CalcThread(shared_obj)
thread.start()

os.system("echo \"python\" >> /home/pi/Desktop/szem_uj/fut_p.txt")
time.sleep(5)

eye_multi = 100

topic="control"
broker="localhost"
port=1884
def on_connect(client, userdata, flags, rc):
    print("CONNECTED")
    print("Connected with result code: ", str(rc))
    client.subscribe(topic)
    print("subscribing to topic : "+topic)


def on_message(client, userdata, message):
    print("Data requested "+str(message.payload))
    print((message.payload).decode("utf-8"))
    global image_R2, image_L2, image_bg_R2, image_bg_L2, shared_obj, new_surface, eye_multi

    if (message.payload).decode("utf-8") =='anime':
        print("anime eyes")
        shared_obj.running_coral = True
        new_surface = True
        eye_multi = 100

        image_R2 = pygame.image.load('pupilla_2.png').convert_alpha()
        image_R2 = pygame.transform.rotate(pygame.transform.scale(image_R2, (800, 800)),90)

        image_L2 = pygame.transform.flip(image_R2, True, False)
        image_L2 = pygame.transform.rotate(pygame.transform.scale(image_L2, (800, 800)),0)

        image_bg_R2 = pygame.image.load('szem_2.png')
        image_bg_R2 = pygame.transform.rotate(pygame.transform.scale(image_bg_R2, (800, 800)), 90)

        image_bg_L2 = pygame.transform.flip(image_bg_R2, True, False)
        image_bg_L2 = pygame.transform.rotate(pygame.transform.scale(image_bg_L2, (800, 800)), 0)

    elif (message.payload).decode("utf-8") =='normal':
        print("normal eyes")
        shared_obj.running_coral = True
        new_surface = True
        eye_multi = 200

        image_R2 = image_L2 = pygame.image.load('pupil4.png').convert_alpha()
        image_R2 = image_L2 = pygame.transform.scale(image_R2, (800, 800))

        image_bg_R2 = pygame.image.load('szem_2.png')
        image_bg_R2 = pygame.transform.rotate(pygame.transform.scale(image_bg_R2, (800, 800)), 90)

        image_bg_L2 = pygame.transform.flip(image_bg_R2, True, False)
        image_bg_L2 = pygame.transform.rotate(pygame.transform.scale(image_bg_L2, (800, 800)), 0)

    elif (message.payload).decode("utf-8") =='black':
        print("black eyes")
        shared_obj.running_coral = True
        new_surface = True
        eye_multi = 200

        image_R2 = image_L2 = pygame.image.load('fekete_pupilla.png').convert_alpha()
        image_R2 = image_L2 = pygame.transform.scale(image_R2, (800, 800))

        image_bg_R2 = pygame.image.load('szem_2.png')
        image_bg_R2 = pygame.transform.scale(image_bg_R2, (800, 800))

        image_bg_L2 = pygame.transform.flip(image_bg_R2, True, False)
        image_bg_L2 = pygame.transform.scale(image_bg_L2, (800, 800))

#######################################################
    elif (message.payload).decode("utf-8") =='blink':
        print("blink")
        shared_obj.running_coral = True
        new_surface = True
        eye_multi = 200
        shared_obj.blink_seq = 1
        """
                if shared_obj.blink_seq>6:
            image_R2 = pygame.image.load('pupilla_2.png').convert_alpha()
            image_R2 = pygame.transform.rotate(pygame.transform.scale(image_R2, (800, 800)),90)

            image_L2 = pygame.transform.flip(image_R2, True, False)
            image_L2 = pygame.transform.rotate(pygame.transform.scale(image_L2, (800, 800)),0)

            image_bg_R2 = pygame.image.load('szem_2.png')
            image_bg_R2 = pygame.transform.rotate(pygame.transform.scale(image_bg_R2, (800, 800)), 90)

            image_bg_L2 = pygame.transform.flip(image_bg_R2, True, False)
            image_bg_L2 = pygame.transform.rotate(pygame.transform.scale(image_bg_L2, (800, 800)), 0)

        else:
            
            image_R2 = pygame.image.load('blink/' + str(shared_obj.blink_seq) + '.jpg')
            image_R2 = pygame.transform.rotate(pygame.transform.scale(image_R2, (800, 800)),90)

            image_L2 = pygame.transform.flip(image_R2, True, False)
            image_L2 = pygame.transform.rotate(pygame.transform.scale(image_L2, (800, 800)),0)
            
            
            #image_R2 = image_L2 = pygame.image.load('blink/' + str(shared_obj.blink_seq) + '.jpg')
            #image_R2 = image_L2 = pygame.transform.scale(image_R2, (800, 800))

            shared_obj.blink_seq += 1

            image_bg_R2 = pygame.image.load('szem_2.png')
            image_bg_R2 = pygame.transform.scale(image_bg_R2, (800, 800))

            image_bg_L2 = pygame.transform.flip(image_bg_R2, True, False)
            image_bg_L2 = pygame.transform.scale(image_bg_L2, (800, 800))
        """

#######################################################

    elif (message.payload).decode("utf-8") =='kill':
        pygame.quit()
        raise SystemExit
        sys.exit()
        os._exit()
    else:
        print("black bg")
        shared_obj.running_coral = False



### MQTT ###
client = mqtt.Client()
client.connect(broker, port)
client.on_connect = on_connect

#client.on_disconnect = on_disconnect
def subscribing():
    client.on_message = on_message
    client.loop_forever()

sub=threading.Thread(target=subscribing)
sub.start()
pygame.init()

window = pygame.display.set_mode((1600, 800)) #, pygame.FULLSCREEN)

background = pygame.Surface((window.get_size()))
background.fill((255, 255, 255))

image_R  = pygame.image.load('pupilla_2.png').convert_alpha()
image_R = image_R2 = pygame.transform.rotate(pygame.transform.scale(image_R, (800, 800)),90)

image_L  = pygame.transform.flip(image_R, True, False)
image_L = image_L2 = pygame.transform.rotate(pygame.transform.scale(image_L, (800, 800)),0)

image_bg_R = pygame.image.load('szem_2.png')
image_bg_R = image_bg_R2 = pygame.transform.rotate(pygame.transform.scale(image_bg_R, (800, 800)), 90)

image_bg_L = pygame.transform.flip(image_bg_R, True, False)
image_bg_L = image_bg_L2 = pygame.transform.rotate(pygame.transform.scale(image_bg_L, (800, 800)), 0)

running = True

new_surface = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if shared_obj.running_coral:
        if shared_obj.blink_seq>0:
            image_R = pygame.image.load('blink/' + str(shared_obj.blink_seq) + '.jpg')
            image_R = pygame.transform.rotate(pygame.transform.scale(image_R, (800, 800)),90)

            image_L = pygame.transform.flip(image_R, True, False)
            image_L = pygame.transform.rotate(pygame.transform.scale(image_L, (800, 800)),0)
            
            shared_obj.blink_seq += 1

            image_bg_R = pygame.image.load('szem_2.png')
            image_bg_R = pygame.transform.scale(image_bg_R, (800, 800))

            image_bg_L = pygame.transform.flip(image_bg_R, True, False)
            image_bg_L = pygame.transform.scale(image_bg_L, (800, 800))

            if shared_obj.blink_seq>6:
                shared_obj.blink_seq = 0
                new_surface = True



        window.fill((255, 255, 255))
        window.blit(background, background.get_rect())
        window.blit(image_bg_L, (0,0))
        window.blit(image_bg_R, (800,0))
        window.blit(image_L, (-(shared_obj.y-.5)*eye_multi+0, -(shared_obj.x-.5)*eye_multi))
        window.blit(image_R, ((shared_obj.y-.5)*eye_multi+800, (shared_obj.x-.5)*eye_multi))
        pygame.display.flip()

        if new_surface:
            image_L = image_L2
            image_R = image_R2
            image_bg_L = image_bg_L2
            image_bg_R = image_bg_R2
            new_surface = False

    else:
        window.fill((0, 0, 0))
        pygame.display.flip()

    pygame.time.Clock().tick(60)

shared_obj.die = True
time.sleep(0.1)
#app.shutdown()
thread.join()
pygame.quit()
sys.exit()



