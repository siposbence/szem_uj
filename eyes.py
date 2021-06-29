import screeninfo
import cv2
import numpy as np
import socket 
import time


class eyes:
    def __init__(self):
        screen_id = 0
        screen = screeninfo.get_monitors()[screen_id]
        width, height = screen.width, screen.height
        print(width, height)

        self.window_name = 'projector'
        #cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        #cv2.moveWindow(self.window_name, screen.x - 1, screen.y - 1)
        #cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        self.img = np.zeros((800, 800, 3))+255
      
    def simple_eye(self, x, y):
        self.img = np.zeros((800, 800, 3))+255
        self.img = cv2.circle(self.img,(int(800*x), int(800*y)), 100, (0,0,0), -1)
        return self.img
        
    
    
    def run_simple_eye(self):
        while 1:   
            last_t = time.time()
            #string=  #s.recv(1024)
            print(string)
            if len(string)>4:
                x,y = str(string).split("\'")[1].split("-")
                self.simple_eye(int(x), int(y)) 
            cv2.imshow(self.window_name, self.img)
            if cv2.waitKey(50) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                s.close() 
                break
            print(time.time()-last_t)
