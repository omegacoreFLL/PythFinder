from ev3sim.Components.BetterClasses.mathEx import *
import pygame
import math


def setScreenSize(width, length):
    global default_width, default_length, half_l, half_w

    #check width
    if width > max_width:
        default_length = int(max_width * length / width)
        default_width = max_width
    elif width < min_width:
        default_length = int(min_width * length / width)
        default_width =  min_width
    else: default_width = width
            
    #check length
    if length > max_length:
        default_width = int(max_length * width / length)
        default_length = max_length
    elif length < min_length:
        default_width = int(min_length * width / length)
        default_length = min_length
    else: default_length = length

    #recalculate if ratio isn't maintainable
    if default_width > max_width:
        default_width = max_width
    elif default_width < min_width:
        default_width = min_width

    if default_length > max_length:
        default_length = max_length
    elif default_length < min_length:
        default_length = min_length
    
    half_l = default_length / 2
    half_w = default_width / 2

def matchScreenSize(image):
    size_multiplier = width_percent / 100 * default_width / max_width

    return pygame.transform.scale(image, 
        (size_multiplier * image.get_width(),
        size_multiplier * image.get_height()))


default_width = 1500
default_length = 1000
half_w = 0
half_l = 0

max_width = 1700
max_length = 1000

min_width = 500
min_length = 500

setScreenSize(default_width, default_length)




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

robot_velocity = 3000 #cm / sec | has an error of +- 0.03 cm
robot_acceleration = 100
robot_deceleration = -20

menu_color = (0, 100, 0)
fade_percent = 0.9
time_until_fade = 0.45 #sec
fade_l = 200
fade_w = 300

trail_len = math.inf #pixels
trail_color = "yellow"
trail_width = 2
trail_loops = 50
backing_distance = 1 #pixels

menu_percent = 70 # % of window size
menu_width = menu_percent / 100 * default_width
menu_length = menu_percent / 100 * default_length

acceleration_dc = 6
acceleration_interval = 0.04

def pixelsToCm(val):
    return val / pixels_to_decimeters * 10

def cmToPixels(val):
    return val * pixels_to_decimeters / 10


velocity_multiplier = 2 * cmToPixels(robot_velocity)

robot_width_in_pixels = robot_scaling_factor * cmToPixels(robot_width)
robot_length_in_pixels =  robot_scaling_factor * cmToPixels(robot_length)

button_stop_joystick = True
using_joystick = False
field_centric = True
tracking = False
using_border = False
draw_border = False
erase_trail = False

drawing_trail_threshold = 20 #cm

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
ps4_menu_button = 10
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
ps5_menu_button = 10
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


width_percent = 25

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




def toFieldCoords(pose):
    return Pose(half_l - pose.y, pose.x - half_w, normalizeDegrees(pose.head - 90))
    
def toWindowCoords(pose):
    return Pose(half_w + pose.y, half_l - pose.x, normalizeDegrees(pose.head + 90))

def toFieldPoint(point):
    return (half_l - point.y, point.x - half_w)

def toWindowPoint(point):
    return (half_w + point.y, half_l - point.x)

def pixels_to_cm(point):
    return Point(pixelsToCm(point.x), pixelsToCm(point.y))

    #refers to Field coordinate system

def symmetrical(point, axis):
    if axis == "x" or axis == "X":
        new_x = 2 * half_w - point.x
        return Point(new_x, point.y)

    if axis == "y" or axis == "Y":
        new_y = 2 * half_l - point.y
        return Point(point.x, new_y)

    raise Exception("Not a valid ---axis---")

def point2Tuple(point):
    return (point.x, point.y)

def tuple2Point(tuple):
    return Point(tuple[0], tuple[1])

def percent2Alpha(value):
    return value * 2.25

def distance(p1, p2):
    return hypot(p2[0] - p1[0], p2[1] - p1[1])
