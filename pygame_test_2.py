import time

#screen = pygame.display.set_mode((self.w, self.h), pygame.FULLSCREEN)

#pygame.display.set_caption('eyes')

#clock = pygame.time.Clock()

# Simple pygame program

# Import and initialize the pygame library
import pygame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([500, 500])
clock = pygame.time.Clock()

# Run until the user asks to quit
running = True
p_time = time.time()
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw a solid blue circle in the center
    pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    # Flip the display
    pygame.display.flip()
    
    
    clock.tick(30)
    
    c_time = time.time()
    print(1/(c_time-p_time))
    p_time = c_time

# Done! Time to quit.
pygame.quit()

