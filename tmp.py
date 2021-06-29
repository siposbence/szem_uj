import configparser
from face2coord_2 import face2coord


Config = configparser.ConfigParser()
Config.read("eyes_coral.conf")
cam = face2coord(camera = int(Config.get("Facedetection", "camera")), 
                              rotate = Config.get("Facedetection", "rotate"),
                              multi = float(Config.get("Facedetection", "multi")), 
                              method = "coral", #Config.get("Facedetection", "method"), 
                              confid = Config.get("Facedetection", "confid"))


"""
class test():
    def __init__(self, config):
        Config = configparser.ConfigParser()
        Config.read(config)
        self.cam = face2coord(camera = int(Config.get("Facedetection", "camera")), 
                              rotate = Config.get("Facedetection", "rotate"),
                              multi = float(Config.get("Facedetection", "multi")), 
                              method = "coral", #Config.get("Facedetection", "method"), 
                              confid = Config.get("Facedetection", "confid"))

    
    
    def update(self):
        x,y = self.cam.get_face_coords()
        print(x,y)
        
        
    def kill(self):
        self.cam.release()
    

"""

import time
#tmp = test("eyes_coral.conf")
time.sleep(0.3)
for i in range(100):
    cam.get_face_coords()
    #tmp.update()
    time.sleep(0.3)
    
#tmp.kill()