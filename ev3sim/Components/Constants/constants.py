from ev3sim.Components.BetterClasses.booleanEx import *
from ev3sim.Components.Constants.screenSize import *
from ev3sim.Components.Constants.constrains import *
from ev3sim.Components.BetterClasses.mathEx import *

import pygame
import math



default_robot_image_name = 'bot_from_above'
default_robot_image_path = 'ev3sim/Images/'
default_robot_image_extension = 'png'

default_robot_scaling_factor = 1
default_robot_height_cm = 20
default_robot_width_cm = 15 

default_coordinate_system_color = "white"
default_grid_color = (63, 63, 63) #rgb
default_background_color = "black"

default_frame_rate = 100 #fps
default_system_font = 'graffitiyouthregular'
default_text_color = "white"

default_width_percent = 25

default_time_until_fade = 0.4
default_fade_percent = 1

default_use_screen_border = True
default_field_centric = True
default_draw_robot_border = False
default_menu_entered = False
default_head_selection = False
default_forwards = True

default_field_centric_kP = 6



#pixels
default_max_trail_length = math.inf
default_max_segment_length = 100

default_drawing_trail_threshold = 20
default_trail_color = "yellow"
default_trail_loops = 50
default_trail_width = 2

default_pixels_to_decimeters = 100

default_positive_direction_arrow_offset = 25
default_half_unit_measure_line = 10

default_backing_distance = 1




class Constants():
    def __init__(self, screen_size = None):
        self.up_to_date = True
        
        self.PIXELS_2_DEC = 0
        self.FPS = 0

        self.ROBOT_IMG_NAME = 0
        self.ROBOT_IMG_EX = 0
        self.ROBOT_IMG_PATH = 0

        self.ROBOT_SCALE = 0
        self.ROBOT_WIDTH = 0
        self.ROBOT_HEIGHT = 0

        self.TEXT_COLOR = 0
        self.TEXT_FONT = 0

        self.MAX_TRAIL_LEN = 0
        self.MAX_TRAIL_SEGMENT_LEN = 0

        self.DRAW_TRAIL_THRESHOLD = 0
        self.TRAIL_COLOR = 0
        self.TRAIL_LOOPS = 0
        self.TRAIL_WIDTH = 0

        self.BACKGROUND_COLOR = 0
        self.AXIS_COLOR = 0
        self.GRID_COLOR = 0

        self.WIDTH_PERCENT = 0

        self.BACKING_DISTANCE = 0

        self.ARROW_OFFSET = 0
        self.HALF_UNIT_MEASURE_LINE = 0

        self.TIME_UNTIL_FADE = 0
        self.FADE_PERCENT = 0

        self.DRAW_ROBOT_BORDER = 0
        self.FIELD_CENTRIC = 0
        self.USE_SCREEN_BORDER = 0
        self.MENU_ENTERED = 0
        self.HEAD_SELECTION = 0
        self.FORWARDS = 0

        self.FIELD_CENTRIC_kP = 0

        self.default()

        if exists(screen_size):
            self.screen_size = screen_size


    def default(self):
        self.PIXELS_2_DEC = default_pixels_to_decimeters
        self.FPS = default_frame_rate

        self.ROBOT_IMG_NAME = default_robot_image_name
        self.ROBOT_IMG_EX = default_robot_image_extension
        self.ROBOT_IMG_PATH = default_robot_image_path

        self.ROBOT_SCALE = default_robot_scaling_factor
        self.ROBOT_WIDTH = default_robot_width_cm
        self.ROBOT_HEIGHT = default_robot_height_cm

        self.TEXT_COLOR = default_text_color
        self.TEXT_FONT = default_system_font

        self.MAX_TRAIL_LEN = default_max_trail_length
        self.MAX_TRAIL_SEGMENT_LEN = default_max_segment_length

        self.DRAW_TRAIL_THRESHOLD = default_drawing_trail_threshold
        self.TRAIL_COLOR = default_trail_color
        self.TRAIL_LOOPS = default_trail_loops
        self.TRAIL_WIDTH = default_trail_width

        self.BACKGROUND_COLOR = default_background_color
        self.AXIS_COLOR = default_coordinate_system_color
        self.GRID_COLOR = default_grid_color

        self.WIDTH_PERCENT = default_width_percent

        self.BACKING_DISTANCE = default_backing_distance

        self.ARROW_OFFSET = default_positive_direction_arrow_offset
        self.HALF_UNIT_MEASURE_LINE = default_half_unit_measure_line

        self.TIME_UNTIL_FADE = default_time_until_fade
        self.FADE_PERCENT = default_fade_percent

        self.FIELD_CENTRIC_kP = default_field_centric_kP

        self.DRAW_ROBOT_BORDER = BooleanEx(default_draw_robot_border)
        self.FIELD_CENTRIC = BooleanEx(default_field_centric)
        self.USE_SCREEN_BORDER = BooleanEx(default_use_screen_border)
        self.MENU_ENTERED = BooleanEx(default_menu_entered)
        self.HEAD_SELECTION = BooleanEx(default_head_selection)
        self.FORWARDS = BooleanEx(default_forwards)

        self.screen_size = ScreenSize()
    
    def pixelsToCm(self, val):
        return val / self.PIXELS_2_DEC * 10

    def cmToPixels(self, val):
        return val * self.PIXELS_2_DEC / 10
    
    def pixelsToCmPoint(self, point: Point):
        return Point(self.pixelsToCm(point.x), self.pixelsToCm(point.y))
        
    


def point2Tuple(point: Point):
    return (point.x, point.y)

def tuple2Point(tuple: tuple):
    return Point(tuple[0], tuple[1])

def percent2Alpha(value):
    return value * 2.25

def distance(p1: tuple, p2: tuple):
    return hypot(p2[0] - p1[0], p2[1] - p1[1])

def exists(value):
    return not value == None


#KEY BINDS
left_wheel_forward_key = pygame.K_q
right_wheel_forward_key = pygame.K_w

left_wheel_backward_key = pygame.K_a
right_wheel_backward_key = pygame.K_s

turn_0_key = pygame.K_1
turn_45_key = pygame.K_2
turn_90_key = pygame.K_3
turn_135_key = pygame.K_4
turn_180_key = pygame.K_5
turn_225_key = pygame.K_6
turn_270_key = pygame.K_7
turn_315_key = pygame.K_8




#XBOX
xbox_threshold = 0.0001
xbox_left_x = 0
xbox_left_y = 1
xbox_right_x = 2

xbox_disable_button = 2
xbox_direction_button = 3
xbox_zero_button = 1
xbox_head_selection_button = 5
xbox_trail_button = 0
xbox_erase_trail_button = 4

xbox_turn_0 = (0, 1)
xbox_turn_45 = (1, 1)
xbox_turn_90 = (1, 0)
xbox_turn_135 = (1, -1)
xbox_turn_180 = (0, -1)
xbox_turn_225 = (-1, -1)
xbox_turn_270 = (-1, 0)
xbox_turn_315 = (-1, 1)

#PS4
ps4_threshold = 0.06
ps4_left_x = 0
ps4_left_y = 1
ps4_right_x = 2

ps4_disable_button = 2
ps4_direction_button = 3
ps4_zero_button = 1
ps4_head_selection_button = 10
ps4_trail_button = 0
ps4_erase_trail_button = 9

ps4_turn_0 = 11
ps4_turn_45 = None
ps4_turn_90 = 14
ps4_turn_135 = None
ps4_turn_180 = 12
ps4_turn_225 = None
ps4_turn_270 = 13
ps4_turn_315 = None

#PS5
ps5_threshold = 0.05 #to be tuned
ps5_left_x = 0
ps5_left_y = 1
ps5_right_x = 2

ps5_disable_button = 2
ps5_direction_button = 3
ps5_zero_button = 1
ps5_head_selection_button = 10
ps5_trail_button = 0
ps5_erase_trail_button = 9

ps5_turn_0 = (0, 1)
ps5_turn_45 = (1, 1)
ps5_turn_90 = (1, 0)
ps5_turn_135 = (1, -1)
ps5_turn_180 = (0, -1)
ps5_turn_225 = (-1, -1)
ps5_turn_270 = (-1, 0)
ps5_turn_315 = (-1, 1)


img_forwards_source = "ev3sim/Images/btn_forwards.png"
img_backwards_source = "ev3sim/Images/btn_backwards.png"
img_show_trail_source = "ev3sim/Images/btn_show_trail.png"
img_hide_trail_source = "ev3sim/Images/btn_hide_trail.png"
img_selecting_on_source = "ev3sim/Images/btn_selecting_on.png"
img_selecting_off_source = "ev3sim/Images/btn_selecting_off.png"

img_forwards = pygame.image.load(img_forwards_source)
img_backwards = pygame.image.load(img_backwards_source)
img_show_trail = pygame.image.load(img_show_trail_source)
img_hide_trail = pygame.image.load(img_hide_trail_source)
img_selecting_on = pygame.image.load(img_selecting_on_source)
img_selecting_off = pygame.image.load(img_selecting_off_source)





#pathing constants
kP_head = 9
kD_head = 1
kS_head = 13

kP_fwd = 5.5 * 1.2
kS_fwd = 20 
kP_correction_agresive = 20
kP_correction_mild = 6
kD_correction = 2

forward_threshold = 18 

kP_interpolating = 5 



