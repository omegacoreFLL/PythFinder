import pygame
from pythfinder.Components.Constants.constants import Constants

# File containing a primitive approach to the fading effect
# Repetitively lowering the opacity from 100% until it reaches 0%
# Can handle text and images

class Fade:
    def __init__(self, constants: Constants):
        self.is_text = False
        self.opacity = -1
        self.obj_rectangle = None
        self.font = None
        self.obj = None
        self.reset_time = 0
        self.constants = constants
        self.center = self.constants.screen_size.get_half()
        self.font = pygame.font.SysFont(self.constants.TEXT_FONT, 150, 0, 40)

    def reset(self, obj):
        self.opacity = 100
        self.reset_time = pygame.time.get_ticks()

        if isinstance(obj, str):
            self.is_text = True
            self.obj = self.font.render(obj, True, self.constants.TEXT_COLOR, "blue")
        else:
            self.obj = obj
            self.is_text = False

        self.obj_rectangle = self.obj.get_rect()
        self.obj_rectangle.center = self.center

    def on_screen(self, screen: pygame.Surface):
        if self.opacity < 0:
            return

        current_time = pygame.time.get_ticks()
        if ms_to_sec(current_time - self.reset_time) > self.constants.TIME_UNTIL_FADE:
            self.opacity -= self.constants.FADE_PERCENT
            self.opacity = max(0, self.opacity)
            self.obj.set_alpha(percentage_to_alpha(self.opacity))

        screen.blit(self.obj, self.obj_rectangle)

    def recalculate(self):
        self.center = self.constants.screen_size.get_half()
        self.font = pygame.font.SysFont(self.constants.TEXT_FONT, 150, 0, 40)

def ms_to_sec(milliseconds: int) -> float:
    return milliseconds / 1000.0

def percentage_to_alpha(percentage: int) -> int:
    return int(percentage * 2.55)