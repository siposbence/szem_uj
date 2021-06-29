import cv2
import face_recognition
import numpy as np
import configparser
from pose_engine import PoseEngine
from PIL import Image


class face2coord:
    def __init__(self, camera, rotate, multi, method, confid):
        self.cap = cv2.VideoCapture(camera)
        self.rotate = rotate
        self.multi = multi
        self.method = method
        self.confid = confid
        self.small_frame = np.zeros([640,480,3], dtype = 'uint8')
        
        if self.method == "tf":
            print("faced")
            from faced import FaceDetector
            from faced.utils import annotate_image            
            self.detector = FaceDetector()
        elif self.method == "coral":
            print("coral")
            self.engine = PoseEngine('posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite')
        else:
            print("face_recognition")
        

            
    
    def get_image(self):
        ret, frame = self.cap.read()
        
        # camera works 
        if ret:
            
            # Camera rotation
            if self.rotate == "none":
                pass 
            if self.rotate == "clockwise":
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            if self.rotate == "counterclockwise":
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # resize image    
            #self.frame = frame
            self.small_frame = cv2.resize(frame, (0, 0), fx=1/self.multi, fy=1/self.multi)
            self.width_cap, self.height_cap, depth = self.small_frame.shape
        
        # no image
        else:
            print("No image from camera")
    def release(self):
        self.cap.release()
        
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

    
Config = configparser.ConfigParser()
Config.read("eyes_coral.conf")
cam = face2coord(camera = int(Config.get("Facedetection", "camera")), 
                              rotate = Config.get("Facedetection", "rotate"),
                              multi = float(Config.get("Facedetection", "multi")), 
                              method = "coral", #Config.get("Facedetection", "method"), 
                              confid = Config.get("Facedetection", "confid"))