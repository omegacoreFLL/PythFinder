import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Check All Keys')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Check for key down events
        elif event.type == pygame.KEYDOWN:
            print(f"Key {pygame.key.name(event.key)} (constant: {event.key}) is pressed")
        
        # Check for key up events
        elif event.type == pygame.KEYUP:
            print(f"Key {pygame.key.name(event.key)} (constant: {event.key}) is released")

    # Fill the screen with white
    screen.fill((255, 255, 255))
    
    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()
