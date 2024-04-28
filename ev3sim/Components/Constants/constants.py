from ev3sim.Components.Controllers.PIDCoefficients import *
from ev3sim.Components.BetterClasses.booleanEx import *
from ev3sim.Components.Constants.screenSize import *
from ev3sim.Components.Constants.constrains import *
from ev3sim.Components.BetterClasses.mathEx import *

import pygame
import math



default_robot_image_name = 'bot_from_above'
default_robot_image_path = 'ev3sim/Images/Robot/'
default_robot_image_extension = 'png'
default_robot_image_source = 'ev3sim/Images/Robot/bot_from_above.png'

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
default_erase_trail = True
default_joystick_enabled = True
default_freeze_trail = False

default_kP_joystick_head = 6
default_kI_joystick_head = 0
default_kD_joystick_head = 0



#pixels
default_max_trail_length = math.inf
default_max_segment_length = 100

default_drawing_trail_threshold = 20
default_trail_color = "yellow"
default_trail_loops = 300
default_trail_width = 2

default_pixels_to_decimeters = 100

default_positive_direction_arrow_offset = 25
default_half_unit_measure_line = 10

default_backing_distance = 1




class Constants():
    def __init__(self, screen_size = None):
        self.recalculate = BooleanEx(False)

        self.PIXELS_2_DEC = 0
        self.FPS = 0

        self.ROBOT_IMG_NAME = 0
        self.ROBOT_IMG_EX = 0
        self.ROBOT_IMG_PATH = 0
        self.ROBOT_IMG_SOURCE = 0

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
        self.ERASE_TRAIL = 0
        self.JOYSTICK_ENABLED = 0
        self.FREEZE_TRAIL = 0

        self.COEFF_JOY_HEAD = 0

        self.default()

        if exists(screen_size):
            self.screen_size = screen_size


    def default(self):
        self.PIXELS_2_DEC = default_pixels_to_decimeters
        self.FPS = default_frame_rate

        self.ROBOT_IMG_NAME = default_robot_image_name
        self.ROBOT_IMG_EX = default_robot_image_extension
        self.ROBOT_IMG_PATH = default_robot_image_path
        self.updateRobotImgSource()

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

        self.COEFF_JOY_HEAD = PIDCoefficients(kP = default_kP_joystick_head,
                                              kI = default_kI_joystick_head,
                                              kD = default_kD_joystick_head)

        self.DRAW_ROBOT_BORDER = BooleanEx(default_draw_robot_border)
        self.FIELD_CENTRIC = BooleanEx(default_field_centric)
        self.USE_SCREEN_BORDER = BooleanEx(default_use_screen_border)
        self.MENU_ENTERED = BooleanEx(default_menu_entered)
        self.HEAD_SELECTION = BooleanEx(default_head_selection)
        self.FORWARDS = BooleanEx(default_forwards)
        self.ERASE_TRAIL = BooleanEx(default_erase_trail)
        self.JOYSTICK_ENABLED = BooleanEx(default_joystick_enabled)
        self.FREEZE_TRAIL = BooleanEx(default_freeze_trail)

        self.screen_size = ScreenSize()
    
    def updateRobotImgSource(self, path = None, name = None, extension = None):
        if path is not None:
            self.ROBOT_IMG_PATH = path
        if name is not None:
            self.ROBOT_IMG_NAME = name
        if extension is not None:
            self.ROBOT_IMG_EX = extension

        self.ROBOT_IMG_SOURCE = "{0}{1}.{2}".format(self.ROBOT_IMG_PATH, 
                                                    self.ROBOT_IMG_NAME, 
                                                    self.ROBOT_IMG_EX)
        
    
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
    return value is not None


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







img_main_menu_source = "ev3sim/Images/Menu/Main/menu_main.png"
img_forwards_source = "ev3sim/Images/Controls/btn_forwards.png"
img_backwards_source = "ev3sim/Images/Controls/btn_backwards.png"
img_menu_button_source = "ev3sim/Images/Menu/Main/menu_button.png"
img_show_trail_source = "ev3sim/Images/Controls/btn_show_trail.png"
img_hide_trail_source = "ev3sim/Images/Controls/btn_hide_trail.png"
img_home_button_source = "ev3sim/Images/Menu/Main/menu_home_button.png"
img_selecting_on_source = "ev3sim/Images/Controls/btn_selecting_on.png"
img_selecting_off_source = "ev3sim/Images/Controls/btn_selecting_off.png"
img_selected_menu_button_source = "ev3sim/Images/Menu/Main/selected_menu_button.png"
img_selected_home_button_source = "ev3sim/Images/Menu/Main/selected_menu_home_button.png"


img_other_button_source = "ev3sim/Images/Menu/Selection/other_button.png"
img_robot_button_source = "ev3sim/Images/Menu/Selection/robot_button.png"
img_trail_button_source = "ev3sim/Images/Menu/Selection/trail_button.png"
img_selection_menu_source = "ev3sim/Images/Menu/Selection/selection_menu.png"
img_pathing_button_source = "ev3sim/Images/Menu/Selection/pathing_button.png"
img_interface_button_source = "ev3sim/Images/Menu/Selection/interface_button.png"
img_selected_other_button_source = "ev3sim/Images/Menu/Selection/selected_other_button.png"
img_selected_robot_button_source = "ev3sim/Images/Menu/Selection/selected_robot_button.png"
img_selected_trail_button_source = "ev3sim/Images/Menu/Selection/selected_trail_button.png"
img_selected_pathing_button_source = "ev3sim/Images/Menu/Selection/selected_pathing_button.png"
img_selected_interface_button_source = "ev3sim/Images/Menu/Selection/selected_interface_button.png"


img_general_menu_source = "ev3sim/Images/Menu/General/general_menu.png"
img_left_arrow_source = "ev3sim/Images/Menu/General/Arrows/Left/left_arrow.png"
img_right_arrow_source = "ev3sim/Images/Menu/General/Arrows/Right/right_arrow.png"
img_selected_left_arrow_source = "ev3sim/Images/Menu/General/Arrows/Left/selected_left_arrow.png"
img_selected_right_arrow_source = "ev3sim/Images/Menu/General/Arrows/Right/selected_right_arrow.png"


img_other_quadrant_source = "ev3sim/Images/Menu/Other/other_quadrant.png"
img_selected_none_source = "ev3sim/Images/selected_none.png"
img_none_source = "ev3sim/Images/none.png"


img_field_centric_on_source = "ev3sim/Images/Menu/Other/FieldCentric/field_centric_on.png"
img_field_centric_off_source = "ev3sim/Images/Menu/Other/FieldCentric/field_centric_off.png"
img_selected_field_centric_on_source = "ev3sim/Images/Menu/Other/FieldCentric/selected_field_centric_on.png"
img_selected_field_centric_off_source = "ev3sim/Images/Menu/Other/FieldCentric/selected_field_centric_off.png"


img_robot_border_on_source = "ev3sim/Images/Menu/Other/RobotBorder/robot_border_on.png"
img_robot_border_off_source = "ev3sim/Images/Menu/Other/RobotBorder/robot_border_off.png"
img_selected_robot_border_on_source = "ev3sim/Images/Menu/Other/RobotBorder/selected_robot_border_on.png"
img_selected_robot_border_off_source = "ev3sim/Images/Menu/Other/RobotBorder/selected_robot_border_off.png"


img_screen_border_on_source = "ev3sim/Images/Menu/Other/ScreenBorder/screen_border_on.png"
img_screen_border_off_source = "ev3sim/Images/Menu/Other/ScreenBorder/screen_border_off.png"
img_selected_screen_border_on_source = "ev3sim/Images/Menu/Other/ScreenBorder/selected_screen_border_on.png"
img_selected_screen_border_off_source = "ev3sim/Images/Menu/Other/ScreenBorder/selected_screen_border_off.png"


img_scale_source = "ev3sim/Images/Menu/Robot/scale.png"
img_width_source = "ev3sim/Images/Menu/Robot/width.png"
img_height_source = "ev3sim/Images/Menu/Robot/height.png"
img_robot_image_path_source = "ev3sim/Images/Menu/Robot/robot_path.png"
img_selected_scale_source = "ev3sim/Images/Menu/Robot/selected_scale.png"
img_selected_width_source = "ev3sim/Images/Menu/Robot/selected_width.png"
img_selected_height_source = "ev3sim/Images/Menu/Robot/selected_height.png"
img_path_quadrant_source = "ev3sim/Images/Menu/Robot/robot_path_quadrant.png"
img_specs_quadrant_source = "ev3sim/Images/Menu/Robot/robot_specs_quadrant.png"
img_selected_robot_image_path_source = "ev3sim/Images/Menu/Robot/selected_robot_path.png"

img_robot_indicator_source = "ev3sim/Images/Menu/Robot/robot_indicator.png"
img_other_indicator_source = "ev3sim/Images/Menu/Other/other_indicator.png"


img_forwards = pygame.image.load(img_forwards_source)
img_main_menu = pygame.image.load(img_main_menu_source)
img_backwards = pygame.image.load(img_backwards_source)
img_show_trail = pygame.image.load(img_show_trail_source)
img_hide_trail = pygame.image.load(img_hide_trail_source)
img_menu_button = pygame.image.load(img_menu_button_source)
img_home_button = pygame.image.load(img_home_button_source)
img_selecting_on = pygame.image.load(img_selecting_on_source)
img_selecting_off = pygame.image.load(img_selecting_off_source)
img_selected_menu_button = pygame.image.load(img_selected_menu_button_source)
img_selected_home_button = pygame.image.load(img_selected_home_button_source)


img_other_button = pygame.image.load(img_other_button_source)
img_robot_button = pygame.image.load(img_robot_button_source)
img_trail_button = pygame.image.load(img_trail_button_source)
img_pathing_button= pygame.image.load(img_pathing_button_source)
img_selection_menu = pygame.image.load(img_selection_menu_source)
img_interface_button = pygame.image.load(img_interface_button_source)
img_selected_other_button= pygame.image.load(img_selected_other_button_source)
img_selected_robot_button = pygame.image.load(img_selected_robot_button_source)
img_selected_trail_button = pygame.image.load(img_selected_trail_button_source)
img_selected_pathing_button = pygame.image.load(img_selected_pathing_button_source)
img_selected_interface_button= pygame.image.load(img_selected_interface_button_source)


img_general_menu = pygame.image.load(img_general_menu_source)
img_left_arrow = pygame.image.load(img_left_arrow_source)
img_right_arrow = pygame.image.load(img_right_arrow_source)
img_selected_left_arrow = pygame.image.load(img_selected_left_arrow_source)
img_selected_right_arrow = pygame.image.load(img_selected_right_arrow_source)

img_other_quadrant = pygame.image.load(img_other_quadrant_source)
img_selected_none = pygame.image.load(img_selected_none_source)
img_none = pygame.image.load(img_none_source)

img_field_centric_on = pygame.image.load(img_field_centric_on_source)
img_field_centric_off = pygame.image.load(img_field_centric_off_source)
img_selected_field_centric_on = pygame.image.load(img_selected_field_centric_on_source)
img_selected_field_centric_off = pygame.image.load(img_selected_field_centric_off_source)

img_robot_border_on = pygame.image.load(img_robot_border_on_source)
img_robot_border_off = pygame.image.load(img_robot_border_off_source)
img_selected_robot_border_on = pygame.image.load(img_selected_robot_border_on_source)
img_selected_robot_border_off = pygame.image.load(img_selected_robot_border_off_source)

img_screen_border_on = pygame.image.load(img_screen_border_on_source)
img_screen_border_off = pygame.image.load(img_screen_border_off_source)
img_selected_screen_border_on = pygame.image.load(img_selected_screen_border_on_source)
img_selected_screen_border_off = pygame.image.load(img_selected_screen_border_off_source)

img_scale = pygame.image.load(img_scale_source)
img_width = pygame.image.load(img_width_source)
img_height = pygame.image.load(img_height_source)
img_path_quadrant = pygame.image.load(img_path_quadrant_source)
img_specs_quadrant = pygame.image.load(img_specs_quadrant_source)
img_selected_scale = pygame.image.load(img_selected_scale_source)
img_selected_width = pygame.image.load(img_selected_width_source)
img_selected_height = pygame.image.load(img_selected_height_source)
img_robot_image_path = pygame.image.load(img_robot_image_path_source)
img_selected_robot_image_path = pygame.image.load(img_selected_robot_image_path_source)

img_robot_indicator = pygame.image.load(img_robot_indicator_source)
img_other_indicator = pygame.image.load(img_other_indicator_source)






img_main_menu = pygame.transform.scale(img_main_menu, (900, 700))
img_general_menu = pygame.transform.scale(img_general_menu, (900, 700))

img_home_button = pygame.transform.scale(img_home_button, (50, 51))
img_menu_button = pygame.transform.scale(img_menu_button, (63, 52))

img_selected_home_button = pygame.transform.scale(img_selected_home_button, (50, 51))
img_selected_menu_button = pygame.transform.scale(img_selected_menu_button, (63, 52))

img_selection_menu = pygame.transform.scale(img_selection_menu, (279, 516))

img_robot_button = pygame.transform.scale(img_robot_button, (176, 51))
img_selected_robot_button = pygame.transform.scale(img_selected_robot_button, (176, 51))

img_interface_button = pygame.transform.scale(img_interface_button, (245, 51))
img_selected_interface_button = pygame.transform.scale(img_selected_interface_button, (245, 51))

img_trail_button = pygame.transform.scale(img_trail_button, (175, 51))
img_selected_trail_button = pygame.transform.scale(img_selected_trail_button, (175, 51))

img_other_button = pygame.transform.scale(img_other_button, (185, 51))
img_selected_other_button = pygame.transform.scale(img_selected_other_button, (185, 51))

img_pathing_button = pygame.transform.scale(img_pathing_button, (248, 51))
img_selected_pathing_button = pygame.transform.scale(img_selected_pathing_button, (248, 51))

img_other_quadrant = pygame.transform.scale(img_other_quadrant, (310, 103))
img_selected_none = pygame.transform.scale(img_selected_none, (230, 100))
img_none = pygame.transform.scale(img_none, (230, 100))

img_field_centric_on = pygame.transform.scale(img_field_centric_on, (390, 110))
img_field_centric_off = pygame.transform.scale(img_field_centric_off, (390, 110))
img_selected_field_centric_on = pygame.transform.scale(img_selected_field_centric_on, (390, 110))
img_selected_field_centric_off = pygame.transform.scale(img_selected_field_centric_off, (390, 110))

img_robot_border_on = pygame.transform.scale(img_robot_border_on, (390, 110))
img_robot_border_off = pygame.transform.scale(img_robot_border_off, (390, 110))
img_selected_robot_border_on = pygame.transform.scale(img_selected_robot_border_on, (390, 110))
img_selected_robot_border_off = pygame.transform.scale(img_selected_robot_border_off, (390, 110))

img_screen_border_on = pygame.transform.scale(img_screen_border_on, (390, 110))
img_screen_border_off = pygame.transform.scale(img_screen_border_off, (390, 110))
img_selected_screen_border_on = pygame.transform.scale(img_selected_screen_border_on, (390, 110))
img_selected_screen_border_off = pygame.transform.scale(img_selected_screen_border_off, (390, 110))

img_robot_indicator = pygame.transform.scale(img_robot_indicator, (170, 95))
img_other_indicator = pygame.transform.scale(img_other_indicator, (170, 95))

img_path_quadrant = pygame.transform.scale(img_path_quadrant, (700, 200))
img_specs_quadrant = pygame.transform.scale(img_specs_quadrant, (193, 240))

img_selected_robot_image_path = pygame.transform.scale(img_selected_robot_image_path, (700, 95))
img_robot_image_path = pygame.transform.scale(img_robot_image_path, (700, 95))

img_width = pygame.transform.scale(img_width, (170, 85))
img_selected_width = pygame.transform.scale(img_selected_width, (170, 85))
img_height = pygame.transform.scale(img_height, (175, 100))
img_selected_height = pygame.transform.scale(img_selected_height, (175, 100))
img_scale = pygame.transform.scale(img_scale, (170, 85))
img_selected_scale = pygame.transform.scale(img_selected_scale, (170, 85))


#pathing constants
kP_head = 30
kD_head = 1
kS_head = 0.6

kP_fwd = 5.5 * 1.2
kS_fwd = 20 
kP_correction_agresive = 20
kP_correction_mild = 6
kD_correction = 2

forward_threshold = 18 

kP_interpolating = 5 



