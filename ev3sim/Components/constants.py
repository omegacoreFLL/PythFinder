from ev3sim.Components.BetterClasses.mathEx import *
import pygame


default_width = 1500
default_length = 1000
half_w = default_width / 2
half_l = default_length / 2

frame_rate = 100 #fps

default_background_color = "black"
default_coordinate_system_color = "white"
default_text_color = "white"
default_grid_color = (63, 63, 63) #rgb
default_system_font = 'graffitiyouthregular'

#pixels
pixels_to_decimeters = 100
positive_direction_arrow = 25
half_unit_measure_line = 10

robot_image_name = 'bot_from_above'
robot_image_source = "ev3sim/Images/{0}.png".format(robot_image_name)
robot_width = 15 #cm
robot_length = 20 #cm

turn_sensitivity = 0.04
distance_between_wheels = 9.97
robot_wheel_distance = distance_between_wheels / turn_sensitivity  #cm

robot_scaling_factor = 1 #from field dimensions

robot_velocity = 20 #cm / sec | has an error of +- 0.03 cm
multiplier = 1.97

menu_color = (0, 100, 0)
fade_percent = 0.9
time_until_fade = 0.45 #sec
fade_l = 200
fade_w = 300

trail_len = 2000 #pixels
trail_color = "yellow"
trail_width = 2
backing_distance = 1 #pixels

menu_percent = 70 # % of window size
menu_width = menu_percent / 100 * default_width
menu_length = menu_percent / 100 * default_length

acceleration_dc = 2
acceleration_interval = 0.04


velocity_multiplier = multiplier * robot_velocity * pixels_to_decimeters / 10

robot_width_in_pixels = robot_scaling_factor * (robot_width * pixels_to_decimeters / 10)
robot_length_in_pixels =  robot_scaling_factor * (robot_length * pixels_to_decimeters / 10)

button_stop_joystick = True
using_joystick = False
manual_control = True
field_centric = True
tracking = False
using_border = True
draw_border = False


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
xbox_menu_button = 5
xbox_trail_button = 0

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
ps4_menu_button = 10
ps4_trail_button = 0

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
ps5_menu_button = 10
ps5_trail_button = 0

ps5_turn_0 = (0, 1)
ps5_turn_45 = (1, 1)
ps5_turn_90 = (1, 0)
ps5_turn_135 = (1, -1)
ps5_turn_180 = (0, -1)
ps5_turn_225 = (-1, -1)
ps5_turn_270 = (-1, 0)
ps5_turn_315 = (-1, 1)


def toFieldCoords(pose):
    return Pose(half_l - pose.y, pose.x - half_w, normalizeDegrees(pose.head - 90))
    
def toWindowCoords(pose):
    return Pose(half_w + pose.y, half_l - pose.x, normalizeDegrees(pose.head + 90))

def toFieldPoint(point):
    return (half_l - point.y, point.x - half_w)

def toWindowPoint(point):
    return (half_w + point.y, half_l - point.x)

def pixels_to_cm(point):
    return Point(point.x / pixels_to_decimeters * 10, point.y / pixels_to_decimeters * 10)

    #refers to Field coordinate system

def symmetrical(point, axis):
    if axis == "x":
        new_x = 2 * half_w - point.x
        return Point(new_x, point.y)

    if axis == "y":
        new_y = 2 * half_l - point.y
        return Point(point.x, new_y)

    raise Exception("Not a valid ---axis---")

def point2Tuple(point):
    return (point.x, point.y)

def tuple2Point(tuple):
    return Point(tuple[0], tuple[1])

def percent2Alpha(value):
    return value * 2.25

    
    