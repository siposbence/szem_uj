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


class pygame_eyes():
    def __init__(self, config):

        self.prev_x, self.prev_y = [[0.5],[0.5]]
        self.w, self.h = (int(Config.get("Display", "size_w")),int(Config.get("Display", "size_h")))
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.FULLSCREEN)
        #DISPLAYSURF = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

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
        x,y = 0.51, 0.6 #self.cam.get_face_coords()
        if x == 0.5 and y == 0.5:
            self.no_face += 1
        else:
            self.no_face = 0
        
        if self.no_face > self.patienete or self.no_face == 0:
            self.prev_x.append(x)
            self.prev_y.append(y)
            x_list = np.linspace(self.prev_x[-2], self.prev_x[-1], num = 5)
            y_list = np.linspace(self.prev_y[-2], self.prev_y[-1], num = 5)
            #self.prev_x.append(0)
            #self.prev_y.append(0)
            self.display(y_list[0], x_list[0])
            
            pygame.display.update()
            
            self.clock.tick(1000)
            #for i in range(5):
            #    self.display(y_list[i], x_list[i])
            #    pygame.display.update()
            #    self.clock.tick(90)
        else:
            self.display(self.prev_y[-1], self.prev_x[-1])
            pygame.display.update()
            self.clock.tick(30)
        
    def kill(self):
        pygame.quit()
        sys.exit()
        self.cam.release()
        self.running = False
    


import time
Config = configparser.ConfigParser()
Config.read("eyes_coral.conf")

tmp = pygame_eyes("eyes_coral.conf")
time.sleep(0.3)
p_time = time.time()
for i in range(200):
    tmp.update()
    c_time = time.time()
    print(1/(c_time-p_time))
    p_time = c_time
    
tmp.kill()