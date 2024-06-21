from pythfinder.Components.Constants.constants import *
from enum import Enum, auto
import pygame

# file containing the logic behind drawing the coordinate system 
#   visible on the screen. Basic math used here, but all values 
#   are in window coordinate system (window_x = field_y, window_y = -field_x)



class Axis(Enum):
    X = auto()
    Y = auto()
    
    
class Background():
    def __init__(self, constants: Constants):
        # define the margins of the field reference frame
        self.positive_y = 0
        self.negative_y = 0

        self.positive_x = 0
        self.negative_x = 0

        # coordinate system units
        self.units_on_screen_x = 0
        self.units_on_screen_y = 0

        # arrow points
        self.x_arrow_point_left = 0
        self.y_arrow_point_up = 0

        self.x_coord = None
        self.y_coord = None
        self.xy_font = None
        self.x_rectangle = None
        self.y_rectangle = None

        self.constants = constants
        self.recalculate()
    
    def recalculate(self):
        self.positive_y = (self.constants.screen_size.width, self.constants.screen_size.half_h) 
        self.negative_y = (0, self.constants.screen_size.half_h)

        self.positive_x = (self.constants.screen_size.half_w, 0)
        self.negative_x = (self.constants.screen_size.half_w, self.constants.screen_size.height)

        # coordinate system units
        self.units_on_screen_x = int(self.constants.screen_size.half_h / self.constants.PIXELS_2_DEC)
        self.units_on_screen_y = int(self.constants.screen_size.half_w / self.constants.PIXELS_2_DEC)

        # arrow points
        self.x_arrow_point_left = (self.positive_x[0] - self.constants.ARROW_OFFSET, self.positive_x[1] + self.constants.ARROW_OFFSET)
        self.y_arrow_point_up = (self.positive_y[0] - self.constants.ARROW_OFFSET, self.positive_y[1] - self.constants.ARROW_OFFSET)

        self.xy_font = pygame.font.SysFont(self.constants.TEXT_FONT, 50)

        self.x_coord = self.xy_font.render("x", True, self.constants.TEXT_COLOR)
        self.y_coord = self.xy_font.render("y", True, self.constants.TEXT_COLOR)
        self.x_rectangle = self.x_coord.get_rect()
        self.y_rectangle = self.y_coord.get_rect()

        self.x_rectangle.center = (self.positive_x[0] + 55, self.positive_x[1] + 35)
        self.y_rectangle.center = (self.positive_y[0] - 35, self.positive_y[1] + 65) 

    # refers to Field coordinate system
    def symmetrical(self, point: Point, axis: Axis):
        if axis is Axis.X:
            new_x = self.constants.screen_size.width - point.x
            return Point(new_x, point.y)

        if axis is Axis.Y:
            new_y = self.constants.screen_size.height - point.y
            return Point(point.x, new_y)

    def onScreen(self, screen: pygame.Surface):
        self.__drawGrid(screen)
        self.__drawAxis(screen)
        self.__drawArrows(screen)
        self.__drawXY(screen)



    def __drawGrid(self, screen: pygame.Surface):
        #draw 'x'
        for line in range(self.units_on_screen_x + 1):
            #mirror one point to all quadrants
            point = Point(self.constants.screen_size.half_w + self.constants.UNIT_SIZE, 
                          self.constants.screen_size.half_h + line * self.constants.PIXELS_2_DEC)
            negative_point = self.symmetrical(point, Axis.Y)

            pygame.draw.line(screen, self.constants.GRID_COLOR, 
                (0, point.y), (self.constants.screen_size.width, point.y), width = 1)
            pygame.draw.line(screen, self.constants.GRID_COLOR, 
                (0, negative_point.y), (self.constants.screen_size.width, negative_point.y), width = 1)
        
        #draw 'y'
        for line in range(self.units_on_screen_y + 1):
            point = Point(self.constants.screen_size.half_w + line * self.constants.PIXELS_2_DEC, 
                          self.constants.screen_size.half_h + self.constants.UNIT_SIZE)
            negative_point = self.symmetrical(point, Axis.X)

            pygame.draw.line(screen, self.constants.GRID_COLOR, 
                (point.x, 0), (point.x, self.constants.screen_size.height), width = 1)
            pygame.draw.line(screen, self.constants.GRID_COLOR, 
                (negative_point.x, 0), (negative_point.x, self.constants.screen_size.height), width = 1)

    def __drawAxis(self, screen: pygame.Surface):
        pygame.draw.line(screen, self.constants.AXIS_COLOR, self.negative_x, self.positive_x, width = 4)
        pygame.draw.line(screen, self.constants.AXIS_COLOR, self.negative_y, self.positive_y, width = 4)

    def __drawArrows(self, screen: pygame.Surface):
        #on 'x' field axis
        pygame.draw.line(screen, self.constants.AXIS_COLOR, 
                self.positive_x, self.x_arrow_point_left, width = 4)
        pygame.draw.line(screen, self.constants.AXIS_COLOR, 
                self.positive_x, 
                point2Tuple(self.symmetrical(tuple2Point(self.x_arrow_point_left), Axis.X)), 
                width = 4)

        #on 'y' field axis
        pygame.draw.line(screen, self.constants.AXIS_COLOR, 
                self.positive_y, self.y_arrow_point_up, width = 4)
        pygame.draw.line(screen, self.constants.AXIS_COLOR, 
                self.positive_y, 
                point2Tuple(self.symmetrical(tuple2Point(self.y_arrow_point_up), Axis.Y)),
                 width = 4)
    
    def __drawXY(self, screen: pygame.Surface):
        screen.blit(self.x_coord, self.x_rectangle)
        screen.blit(self.y_coord, self.y_rectangle)

