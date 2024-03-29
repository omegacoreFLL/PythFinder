from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.controls import *
import pygame

class Menu():
    def __init__(self):
        self.joystick = None
        self.screen = None

    
    def onScreen(self, screen, joystick : Controls,):  
        self.joystick = joystick
        self.__backround(screen)
    
    def __backround(self, screen):
        pygame.draw.rect(screen, "blue", ((default_width - menu_width) / 2, 
                                          (default_length - menu_length) / 2, menu_width, menu_length))
    