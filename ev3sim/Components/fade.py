from ev3sim.Components.Constants.constants import *
import pygame




class Fade():
    def __init__(self, constants: Constants):
        self.isText = False

        self.screen_size = 0
        self.text_color = 0
        self.center = 0
        
        self.opacity = -1

        self.obj_rectangle = 0
        self.font = 0
        self.obj = 0

        self.reset_time = 0

        self.fade_percent = 0
        self.menu_color = 0

        self.setConstants(constants)

    
    def reset(self, object):
        self.opacity = 100
        self.reset_time = pygame.time.get_ticks()

        if isinstance(object, str):
            self.isText = True
            self.obj = self.font.render(object, True, self.constants.TEXT_COLOR, "blue")
        else: 
            self.obj = object
            self.isText = False

        self.obj_rectangle = self.obj.get_rect()
        self.obj_rectangle.center = self.center
    
    def onScreen(self, screen):
        if self.opacity >= 0:
            current_time = pygame.time.get_ticks()

            if msToS(current_time - self.reset_time) > self.constants.TIME_UNTIL_FADE:
                self.opacity -= self.constants.FADE_PERCENT
            
            if self.opacity < 0:
                self.opacity = 0

            self.obj.set_alpha(percent2Alpha(self.opacity))
            screen.blit(self.obj, self.obj_rectangle)


    def setConstants(self, constants: Constants):
        self.constants = constants

        self.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h)
        self.font = pygame.font.SysFont(constants.TEXT_FONT, 150, 0, 40)
    