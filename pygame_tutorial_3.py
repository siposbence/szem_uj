import pygame, sys

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




while True:
  for event in pygame.event.get():
    if event.type == 12:
      pygame.quit()
      sys.exit()

  window.fill((255, 255, 255))
  window.blit(background, background.get_rect())
  window.blit(image_bg_L, (0,0))
  window.blit(image_bg_R, (800,0))
  window.blit(image, (0,-100))
  window.blit(image, (800,-100))

  pygame.display.update()
  pygame.time.Clock().tick(60)