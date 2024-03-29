from ev3sim.Components.constants import *
import pygame

class Fade():
    def __init__(self):
        self.center = (half_w, half_l)
        self.opacity = -1

        self.font = pygame.font.SysFont(default_system_font, 150, 0, 40)
        self.text_rectangle = 0
        self.text = 0

        self.reset_time = 0
    
    def reset(self, text):
        self.opacity = 100
        self.reset_time = pygame.time.get_ticks()

        self.text = self.font.render(text, True, default_text_color, menu_color)
        self.text_rectangle = self.text.get_rect()
        self.text_rectangle.center = self.center
    
    def onScreen(self, screen):
        if self.opacity >= 0:
            current_time = pygame.time.get_ticks()

            if msToS(current_time - self.reset_time) > time_until_fade:
                self.opacity -= fade_percent
            
            if self.opacity < 0:
                self.opacity = 0

            self.text.set_alpha(percent2Alpha(self.opacity))
            screen.blit(self.text, self.text_rectangle)

