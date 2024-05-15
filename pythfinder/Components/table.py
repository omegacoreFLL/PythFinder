from pythfinder.Components.BetterClasses.edgeDetectorEx import *
from pythfinder.Components.Constants.constants import *


# file containing the Table class
#
# used for toggling the displaying of the FLL table
#
# the scale of the image depends of the source and should be tuned 
#   everytime you change it, to match the actual real dimensions


class Table():
    def __init__(self, constants: Constants):
        self.ENABLE = EdgeDetectorEx()
        self.constants = constants

        self.image = None
        self.rectangle = None

        self.last_screen_size = None
        self.last_pixels_2_dec = None

        self.width_in_pixels = 0
        self.height_in_pixels = 0

        self.recalculate()
    
    def recalculate(self):
        self.getTableSizeInPixels()

        self.image = pygame.transform.scale(fll_table_image, 
                (self.width_in_pixels, self.height_in_pixels))

        self.rectangle = self.image.get_rect()
        self.rectangle.center = (self.constants.screen_size.getHalf())  

    def getTableSizeInPixels(self):
        self.width_in_pixels = self.constants.cmToPixels(fll_table_width_cm)
        self.height_in_pixels =  self.constants.cmToPixels(fll_table_height_cm)

    def onScreen(self, screen: pygame.Surface):
        self.ENABLE.set(self.constants.DRAW_TABLE.get())
        self.ENABLE.update()

        if self.ENABLE.high:
            screen.blit(self.image, self.rectangle)
        
        elif self.ENABLE.rising:
            self.last_screen_size = self.constants.screen_size.get()
            self.last_pixels_2_dec = self.constants.PIXELS_2_DEC

            self.constants.screen_size.setTable()
            self.constants.PIXELS_2_DEC = 60
            self.constants.TRAIL_WIDTH = 8
            self.constants.recalculate.set(True)
        
        elif self.ENABLE.falling:
            self.constants.screen_size.set(self.last_screen_size[0],
                                           self.last_screen_size[1])
            self.constants.PIXELS_2_DEC = self.last_pixels_2_dec

            self.constants.recalculate.set(True)
