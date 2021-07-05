import pygame as pg
from glob import glob
 
screen = pg.display.set_mode((800, 800))
pg.display.set_caption("Game")
clock = pg.time.Clock()
 
 
class Sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.acount = 0
 
        # Coordinates for movement
        self.x = 0
        self.y = 0
        self.action = "idle"
 
        #self.animation = [
        #    pg.image.load(f) for f in glob("..\\cat\\Idle *.png")]
        self.pupil = pg.image.load("pupil4.png").convert_alpha()
        #self.image = self.animation[0]
        self.rect = self.pupil.get_rect()
        print(self.image)
 
    def update(self):
        self.acount += 1
        if self.acount == len(self.animation):
            self.acount = 0
        self.image = self.animation[self.acount]
 
    def change_to(self, action):
        self.acount = 0
        self.action = action
        self.animation = [
            pg.image.load(f) for f in glob(f"..\\cat\\{self.action} *.png")]
 
 
g = pg.sprite.Group()
sprite = Sprite()
g.add(sprite)
print(sprite)
 
loop = 1
jumpcount = 0
jumpstate = 0
walkstate = 0
while loop:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            loop = 0
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                walkstate = 1
                sprite.change_to("walk")
            if event.key == pg.K_LEFT:
                walkstate = 0
                sprite.change_to("idle")
            if event.key == pg.K_UP:
                jumpstate = 1
                sprite.change_to("jump")
    if jumpstate:
        jumpcount += 1
        print(jumpcount)
        if jumpcount > 8:
            jumpstate = 0
            jumpcount = 0
            if walkstate:
                sprite.change_to("walk")
            else:
                sprite.change_to("idle")
    screen.fill((0, 0, 0))
    g.draw(screen)
    g.update()
    pg.display.flip()
    clock.tick(30)
 
pg.quit()