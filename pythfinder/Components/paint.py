from pythfinder.Components.BetterClasses.edgeDetectorEx import *
from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Components.Constants.constants import *

import pygame


class Shape(Enum):
    LINE = "l"
    CIRCLE = "c"
    TRIANGLE = "t"
    RECTANGLE = "r"

    ERASE = "e"
    NOTHING = "enter"

class Paint():
    def __init__(self, constants: Constants) -> None:
        self.constants = constants

        self.ENABLED = EdgeDetectorEx()

        self.drawing_surface = pygame.Surface((self.constants.screen_size.MAX_WIDTH, 
                                               self.constants.screen_size.MAX_HEIGHT), pygame.SRCALPHA)
        
        
        self.last_surface = self.drawing_surface.copy()
        self.surf_show_pose = (0, 0)

        self.delta_start_pose = (0, 0)
        self.start_pose = None
        self.shape = None

        self.draw = BooleanEx(False)

        self.WIDTH = 6

    def add_key(self, event, clicked: bool, pose: tuple | None = None):
        if pose is not None:
            self.start_pose = (pose[0] + self.delta_start_pose[0],
                               pose[1] + self.delta_start_pose[1])

        self.key = event.key if event is not None else None

        self.__update_shape()
        self.draw.set(clicked)
    
    def __set_cursor(self, img: pygame.Surface):
        self.constants.cursor.apply(pygame.cursors.Cursor((16, 16), img))



    def default(self):
        self.shape = Shape.NOTHING
        self.last_surface = pygame.Surface((pygame.display.Info().current_w, 
                                            pygame.display.Info().current_h), pygame.SRCALPHA)

        self.recalculate()

    def recalculate(self):
        self.surf_show_pose = ((self.constants.screen_size.get()[0] - self.drawing_surface.get_size()[0]) * 0.5,
                               (self.constants.screen_size.get()[1] - self.drawing_surface.get_size()[1]) * 0.5)    
        self.delta_start_pose = ((self.constants.screen_size.MAX_WIDTH - self.constants.screen_size.get()[0]) * 0.5,
                                 (self.constants.screen_size.MAX_HEIGHT - self.constants.screen_size.get()[1]) * 0.5)



    def update(self, mouse_pose: tuple):
        if self.draw.compare(False):
            self.last_surface = self.drawing_surface.copy()
            return None
        
        self.drawing_surface = self.last_surface.copy()

        match self.shape:
            case Shape.LINE:
                pygame.draw.line(self.drawing_surface, self.constants.PAINT_COLOR, self.start_pose, mouse_pose, self.WIDTH)

            case Shape.CIRCLE:
                radius = int(((mouse_pose[0] - self.start_pose[0]) ** 2 + (mouse_pose[1] - self.start_pose[1]) ** 2) ** 0.5)
                pygame.draw.circle(self.drawing_surface, self.constants.PAINT_COLOR, self.start_pose, radius, self.WIDTH)

            case Shape.TRIANGLE:
                pygame.draw.polygon(self.drawing_surface, self.constants.PAINT_COLOR, [self.start_pose, mouse_pose, (self.start_pose[0], mouse_pose[1])], self.WIDTH)

            case Shape.RECTANGLE:
                top_left = (min(self.start_pose[0], mouse_pose[0]), min(self.start_pose[1], mouse_pose[1]))
                width = abs(mouse_pose[0] - self.start_pose[0])
                height = abs(mouse_pose[1] - self.start_pose[1])

                pygame.draw.rect(self.drawing_surface, self.constants.PAINT_COLOR, pygame.Rect(top_left, (width, height)), self.WIDTH)

            case Shape.ERASE:
                pygame.draw.circle(self.last_surface, (0, 0, 0, 0), mouse_pose, radius = 30)

    def __update_shape(self):
        match self.key:
            case pygame.K_l: 
                self.shape = Shape.LINE
                self.__set_cursor(img_line_cursor)

            case pygame.K_c: 
                self.shape = Shape.CIRCLE
                self.__set_cursor(img_circle_cursor)

            case pygame.K_t: 
                self.shape = Shape.TRIANGLE
                self.__set_cursor(img_triangle_cursor)

            case pygame.K_r: 
                self.shape = Shape.RECTANGLE
                self.__set_cursor(img_rectangle_cursor)

            case pygame.K_e: 
                self.shape = Shape.ERASE
                self.__set_cursor(img_eraser_cursor)

            case pygame.K_RETURN: 
                self.shape = Shape.NOTHING
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)


    def on_screen(self, screen: pygame.Surface, mouse_pose: tuple):
        self.ENABLED.set(self.constants.HAND_DRAWING.get())
        self.ENABLED.update()
        
        if self.ENABLED.rising:
            self.default()
        
        if self.ENABLED.falling:
            self.constants.cursor.apply_system(pygame.SYSTEM_CURSOR_ARROW)
        
        if self.ENABLED.high:
            if self.constants.MENU_ENTERED.compare(False):
                mouse_pose = (mouse_pose[0] + self.delta_start_pose[0],
                            mouse_pose[1] + self.delta_start_pose[1]) 
                        
                self.update(mouse_pose)

        if self.constants.DRAWING_VISIBLE.compare():
            screen.blit(self.drawing_surface, self.surf_show_pose)
