
from ev3sim.Components.constants import *
import pygame


class Background():
    def __init__(self):
        #define the margins of the field reference frame
        self.positive_y = (default_width, half_l) 
        self.negative_y = (0, half_l)

        self.positive_x = (half_w, 0)
        self.negative_x = (half_w, default_length)

        #coordinate system units
        self.units_on_screen_x = int(half_l / pixels_to_decimeters)
        self.units_on_screen_y = int(half_w / pixels_to_decimeters)

        #arrow points
        self.x_arrow_point_left = (self.positive_x[0] - positive_direction_arrow, self.positive_x[1] + positive_direction_arrow)
        self.y_arrow_point_up = (self.positive_y[0] - positive_direction_arrow, self.positive_y[1] - positive_direction_arrow)


        self.xy_font = pygame.font.SysFont(default_system_font, 70)

        self.x_coord = self.xy_font.render("x", True, default_text_color, default_background_color)
        self.y_coord = self.xy_font.render("y", True, default_text_color, default_background_color)
        self.x_rectangle = self.x_coord.get_rect()
        self.y_rectangle = self.y_coord.get_rect()

        self.x_rectangle.center = (self.positive_x[0] + 55, self.positive_x[1] + 35)
        self.y_rectangle.center = (self.positive_y[0] - 35, self.positive_y[1] + 65)
    
    def onScreen(self, screen):
        self.__drawGrid(screen)
        self.__drawAxis(screen)
        self.__drawArrows(screen)
        self.__drawXY(screen)

    def __drawGrid(self, screen):
        #draw 'x'
        for line in range(self.units_on_screen_x + 1):
            #mirror one point to all quadrants
            point = Point(half_w + half_unit_measure_line, half_l + line * pixels_to_decimeters)
            negative_point = symmetrical(point, 'y')

            pygame.draw.line(screen, default_grid_color, 
                (0, point.y), (default_width, point.y), width = 1)
            pygame.draw.line(screen, default_grid_color, 
                (0, negative_point.y), (default_width, negative_point.y), width = 1)
        
        #on 'y'
        for line in range(self.units_on_screen_y + 1):
            point = Point(half_w + line * pixels_to_decimeters, half_l + half_unit_measure_line)
            negative_point = symmetrical(point, 'x')

            pygame.draw.line(screen, default_grid_color, 
                (point.x, 0), (point.x, default_length), width = 1)
            pygame.draw.line(screen, default_grid_color, 
                (negative_point.x, 0), (negative_point.x, default_length), width = 1)

    def __drawAxis(self, screen):
        pygame.draw.line(screen, default_coordinate_system_color, self.negative_x, self.positive_x, width = 4)
        pygame.draw.line(screen, default_coordinate_system_color, self.negative_y, self.positive_y, width = 4)

    def __drawArrows(self, screen):
        #on 'x' field axis
        pygame.draw.line(screen, default_coordinate_system_color, 
                self.positive_x, self.x_arrow_point_left, width = 4)
        pygame.draw.line(screen, default_coordinate_system_color, 
                self.positive_x, 
                point2Tuple(symmetrical(tuple2Point(self.x_arrow_point_left), "x")), 
                width = 4)

        #on 'y' field axis
        pygame.draw.line(screen, default_coordinate_system_color, 
                self.positive_y, self.y_arrow_point_up, width = 4)
        pygame.draw.line(screen, default_coordinate_system_color, 
                self.positive_y, 
                point2Tuple(symmetrical(tuple2Point(self.y_arrow_point_up), "y")),
                 width = 4)
    
    def __drawXY(self, screen):
        screen.blit(self.x_coord, self.x_rectangle)
        screen.blit(self.y_coord, self.y_rectangle)

