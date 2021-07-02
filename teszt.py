import pygame
import random
import time
import threading
class SharedObj(object):
    x = 0
    y = 0
    die = False
class CalcThread(threading.Thread):
    def __init__(self, shared, *args, **kwargs):
        super(CalcThread,self).__init__(*args, **kwargs)
        self.shared = shared
    def run(self):
        while(not self.shared.die):
            self.shared.x = random.randrange(0, 500, 1)
            self.shared.y = random.randrange(0, 500, 1)
            print("flip")
            time.sleep(1)
shared_obj = SharedObj()
thread = CalcThread(shared_obj)
thread.start()
pygame.init()
screen = pygame.display.set_mode([500, 500])
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (0, 0, 255), (shared_obj.x, shared_obj.y), 75)
    pygame.display.flip()
shared_obj.die = True
time.sleep(0.1)
thread.join()
pygame.quit()
