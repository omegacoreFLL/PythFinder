from ev3sim.Components.constants import *
import pygame

class Fade():
    def __init__(self):
        self.center = (half_w, half_l)
        self.opacity = -1

        self.font = pygame.font.SysFont(default_system_font, 150, 0, 40)
        self.obj_rectangle = 0
        self.obj = 0
        self.isText = False

        self.reset_time = 0
    
    def reset(self, object):
        self.opacity = 100
        self.reset_time = pygame.time.get_ticks()

        if isinstance(object, str):
            self.isText = True
            self.obj = self.font.render(object, True, default_text_color, menu_color)
        else: 
            self.obj = object
            self.isText = False

        self.obj_rectangle = self.obj.get_rect()
        self.obj_rectangle.center = self.center
            
    
    def onScreen(self, screen):
        if self.opacity >= 0:
            current_time = pygame.time.get_ticks()

            if msToS(current_time - self.reset_time) > time_until_fade:
                self.opacity -= fade_percent
            
            if self.opacity < 0:
                self.opacity = 0

            self.obj.set_alpha(percent2Alpha(self.opacity))
            screen.blit(self.obj, self.obj_rectangle)

