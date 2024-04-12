from ev3sim.Components.BetterClasses.edgeDetectorEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Components.Menu.enums import *
import pygame

class Button():
    def __init__(self, name: Selected, value,
                 quadrant_surface: pygame.Surface, 
                 title_surface: pygame.Surface, selected_title_surface: pygame.Surface,
                 size, font = default_system_font,):
        self.name = name
        self.value = value

        self.quadrant = quadrant_surface

        self.title = title_surface
        self.selected_title = selected_title_surface
        self.display_title = title_surface

        self.quadrant_rect = quadrant_surface.get_rect()
        self.title_rect = title_surface.get_rect()

        self.font = pygame.font.SysFont(font, size)

        self.quad_center = None
        self.title_center = None

        self.SELECTED = EdgeDetectorEx()


    
    def quadrantCenter(self, center: tuple):
        self.quadrant_rect.center = center
        self.quad_center = center

    def titleCenter(self, center: tuple):
        self.title_rect.center = center
        self.title_center = center

    def initialized(self):
        return not self.quad_center == None and not self.title_center == None

    def update(self, selected, clicked, value = None):

        if selected is self.name:
            if clicked:
                pass
            
            self.SELECTED.set(True)
        else: self.SELECTED.set(False)

        self.SELECTED.update()

        if self.SELECTED.high:
            self.display_title = self.selected_title
        
        if self.SELECTED.low:
            self.display_title = self.title




            

    def display(self, screen: pygame.Surface):
        screen.blit(self.quadrant, self.quadrant_rect)
        screen.blit(self.display_title, self.title_rect)


    def updateAndDisplay(self, screen: pygame.Surface, 
                         clicked, value = None):
        if not self.initialized():
            raise Exception("please initiate {0} button".format(self.name.name))

        self.update(value, clicked)
        self.display(screen)