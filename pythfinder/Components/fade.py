from pythfinder.Components.Constants.constants import *
import pygame

# file containing a primitive approach to the fading effect
# 
# repetitively lowering the opacity from 100% until it reaches 0% 
#
# can handle text and images


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

        self.constants = constants
        self.recalculate()

    
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
    
    def onScreen(self, screen: pygame.Surface):
        if self.opacity < 0:
            return None
        current_time = pygame.time.get_ticks()

        if msToS(current_time - self.reset_time) > self.constants.TIME_UNTIL_FADE:
            self.opacity -= self.constants.FADE_PERCENT

            self.opacity = max(0, self.opacity)
            self.obj.set_alpha(percent2Alpha(self.opacity))
            
        screen.blit(self.obj, self.obj_rectangle)


    def recalculate(self):
        self.center = (self.constants.screen_size.half_w, self.constants.screen_size.half_h)
        self.font = pygame.font.SysFont(self.constants.TEXT_FONT, 150, 0, 40)
    