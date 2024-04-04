from ev3sim.Components.BetterClasses.booleanEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Components.background import *
from ev3sim.Components.controls import *
from ev3sim.Components.robot import *
from ev3sim.Components.fade import *
from ev3sim.Components.menu import *

import pygame
import math




class Simulator():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("FLL PythFinder simulator")
        self.running = BooleanEx(True)
        self.manual_control = BooleanEx(True)

        self.constants = Constants()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.constants.screen_size.get())

        self.dt = 0

        self.background = Background(self.constants)
        self.robot = Robot(self.constants)
        self.fade = Fade(self.constants)
        self.controls = Controls()
        #self.menu = Menu()


    def build(self, constants = None):
        if exists(constants):
            self.constants = constants
        self.constants.up_to_date = True

        if not self.screen.get_size()  == self.constants.screen_size.get():
            self.screen = pygame.display.set_mode(self.constants.screen_size.get())

        self.background.setConstants(self.constants)
        self.robot.setConstants(self.constants)
        self.fade.setConstants(self.constants)
 
    def set(self, pixels_2_dec = None, fps = None, 
            robot_image_name = None, robot_image_extension = None, robot_image_path = None,
            robot_scale = None, robot_width = None, robot_height = None,
            text_color = None, text_font = None,
            max_trail_length = None, max_trail_segment_length = None,
            draw_trail_threshold = None, trail_color = None, trail_loops = None, trail_width = None,
            backround_color = None, axis_color = None, grid_color = None,
            width_percent = None, backing_distance = None,
            arrow_offset = None, half_unit_measure_line = None,
            time_until_fade = None, fade_percent = None,
            field_centric_kP = None, screen_size = None):
        
        self.constants.up_to_date = False

        if exists(pixels_2_dec):
            self.constants.PIXELS_2_DEC = 0
        if exists(fps):
            self.constants.FPS = 0

        if exists(robot_image_name):
            self.constants.ROBOT_IMG_NAME = robot_image_name
        if exists(robot_image_extension):
            self.constants.ROBOT_IMG_EX = robot_image_extension
        if exists(robot_image_path):
            self.constants.ROBOT_IMG_PATH = robot_image_path

        if exists(robot_scale):
            self.constants.ROBOT_SCALE = robot_scale
        if exists(robot_width):
            self.constants.ROBOT_WIDTH = robot_width
        if exists(robot_height):
            self.constants.ROBOT_HEIGHT = robot_height

        if exists(text_color):
            self.constants.TEXT_COLOR = text_color
        if exists(text_font):
            self.constants.TEXT_FONT = text_font

        if exists(max_trail_length):
            self.constants.MAX_TRAIL_LEN = max_trail_length
        if exists(max_trail_segment_length):
            self.constants.MAX_TRAIL_SEGMENT_LEN = max_trail_segment_length

        if exists(draw_trail_threshold):
            self.constants.DRAW_TRAIL_THRESHOLD = draw_trail_threshold
        if exists(trail_color):
            self.constants.TRAIL_COLOR = trail_color
        if exists(trail_loops):
            self.constants.TRAIL_LOOPS = trail_loops
        if exists(trail_width):
            self.constants.TRAIL_WIDTH = trail_width

        if exists(backround_color):
            self.constants.BACKGROUND_COLOR = backround_color
        if exists(axis_color):
            self.constants.AXIS_COLOR = axis_color
        if exists(grid_color):
            self.constants.GRID_COLOR = grid_color

        if exists(width_percent):
            self.constants.WIDTH_PERCENT = width_percent

        if exists(backing_distance):
            self.constants.BACKING_DISTANCE = backing_distance
        
        if exists(arrow_offset):
            self.constants.ARROW_OFFSET = arrow_offset
        if exists(half_unit_measure_line):
            self.constants.HALF_UNIT_MEASURE_LINE = half_unit_measure_line

        if exists(time_until_fade):
            self.constants.TIME_UNTIL_FADE = time_until_fade
        if exists(fade_percent):
            self.constants.FADE_PERCENT = fade_percent
        
        if exists(field_centric_kP):
            self.constants.FIELD_CENTRIC_kP = field_centric_kP
        if exists(screen_size):
            self.constants.screen_size = screen_size

        return self
    


    def RUNNING(self):
        return self.running.compare()



    def chooseFieldCentric(self, fun, bool = None):
        self.constants.FIELD_CENTRIC.choose(fun, bool)
        self.constants.up_to_date = False
    
    def chooseDrawRobotBorder(self, fun, bool = None):
        self.constants.DRAW_BORDER.choose(fun, bool)
        self.constants.up_to_date = False
    
    def chooseUsingScreenBorder(self, fun, bool = None):
        self.constants.USE_SCREEN_BORDER.choose(fun, bool)
        self.constants.up_to_date = False
    
    def chooseMenuEntered(self, fun, bool = None):
        self.constants.MENU_ENTERED.choose(fun, bool)
        self.constants.up_to_date = False
    
    def chooseHeadSelection(self, fun, bool = None):
        self.constants.HEAD_SELECTION.choose(fun, bool)
        self.constants.up_to_date = False
    
    def chooseForward(self, fun, bool = None):
        self.constants.FORWARDS.choose(fun, bool)
        self.constants.up_to_date = False




    def matchScreenSize(self, image, width):
        size_multiplier = self.constants.WIDTH_PERCENT / 100 * width / self.constants.screen_size.MAX_WIDTH

        return pygame.transform.scale(image, 
            (size_multiplier * image.get_width(),
            size_multiplier * image.get_height()))




    def update(self):
        if not self.constants.up_to_date:
            self.build()
        self.__updateEventManager()

        #reset frame
        self.screen.fill(default_background_color)

        if self.manual_control.compare():
            self.__updateControls()
        self.robot.update(self.dt)

        self.background.onScreen(self.screen)
        self.robot.onScreen(self.screen)
        self.fade.onScreen(self.screen)
        #if self.constants.MENU_ENTERED.compare():
            #self.menu.onScreen(self.screen, self.controls.joystick)
            

        pygame.display.update()
        self.dt = self.clock.tick(self.constants.FPS) / 1000
    


    def __updateEventManager(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                self.controls.addJoystick(pygame.joystick.Joystick(event.device_index))
            
            elif event.type == pygame.JOYDEVICEREMOVED:
                self.controls.addJoystick(None)

            if event.type == pygame.QUIT:
                self.running.set(False)
                pygame.quit()

    def __updateControls(self):
        self.controls.update()

        if self.controls.using_joystick.compare():
            self.__updateJoystick()
        else: self.__updateKeyboard()



    def __updateKeyboard(self):
        self.__updateKeyboardVelocity()
        self.__updateKeyboardTurn()
    
    def __updateKeyboardVelocity(self):
        left_sign = 0
        right_sign = 0

        #drive left wheel
        
        if self.controls.keyboard_detector[left_wheel_forward_key].high:
            left_sign = 1
        elif self.controls.keyboard_detector[left_wheel_backward_key].high:
            left_sign = -1

        #drive right wheel
        if self.controls.keyboard_detector[right_wheel_forward_key].high:
            right_sign = 1
        elif self.controls.keyboard_detector[right_wheel_backward_key].high:
            right_sign = -1

        self.robot.setWheelPowers(left = self.constants.cmToPixels(self.robot.constrains.vel) * left_sign, 
                                    right = self.constants.cmToPixels(self.robot.constrains.vel) * right_sign)

    def __updateKeyboardTurn(self):
        if self.controls.keyboard_detector[turn_0_key].rising:
            self.robot.pose.head = 0
        if self.controls.keyboard_detector[turn_45_key].rising:
            self.robot.pose.head = 45
        if self.controls.keyboard_detector[turn_90_key].rising:
            self.robot.pose.head = 90
        if self.controls.keyboard_detector[turn_135_key].rising:
            self.robot.pose.head = 135
        if self.controls.keyboard_detector[turn_180_key].rising:
            self.robot.pose.head = 180
        if self.controls.keyboard_detector[turn_225_key].rising:
            self.robot.pose.head = 225
        if self.controls.keyboard_detector[turn_270_key].rising:
            self.robot.pose.head = 270
        if self.controls.keyboard_detector[turn_315_key].rising:
            self.robot.pose.head = 315



    def __updateJoystick(self):
        left_x = self.controls.joystick.get_axis(self.controls.keybinds.left_x)
        left_y = self.controls.joystick.get_axis(self.controls.keybinds.left_y)
        right_x = self.controls.joystick.get_axis(self.controls.keybinds.right_x)

        self.__updateJoystickButtons()

        if self.constants.FIELD_CENTRIC.compare():
            joy_x, joy_y = self.__updateJoystickFieldCentric((left_x, left_y))
        else: joy_x, joy_y = self.__updateJoystickRobotCentric((right_x, left_y))

        joy_vel = joy_y * self.robot.constrains.vel
        joy_ang_vel = joy_x * self.robot.constrains.ang_vel
        inverse = self.robot.kinematics.inverseKinematics(joy_vel, joy_ang_vel)

        left_speed = inverse[0]
        right_speed = inverse[1]
        self.robot.setWheelPowers(left = left_speed, right = right_speed)

    def __updateJoystickFieldCentric(self, values):    
        left_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        '''if self.constants.MENU_ENTERED.compare():
            return (0,0)'''

        if (abs(left_x) > joystick_threshold or abs(left_y) > joystick_threshold):
            self.robot.target_head = normalizeDegrees(math.degrees(math.atan2(left_y, left_x) + math.pi / 2))
            joy_y = math.hypot(left_y, left_x)

            if self.constants.FORWARDS.compare(False):
                joy_y = -joy_y
                self.robot.target_head = normalizeDegrees(self.robot.target_head + 180)

        else: 
            joy_y = 0
        
        error = findShortestPath(self.robot.target_head, self.robot.pose.head) / 180
        joy_x = self.robot.head_controller.calculate(error)

        if abs(joy_x) < joystick_threshold:
            joy_x = 0

        return (joy_x, joy_y)

    def __updateJoystickRobotCentric(self, values):
        right_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        '''if self.constants.MENU_ENTERED.compare():
            return (0,0)'''

        if abs(right_x) > joystick_threshold:
            joy_x = right_x
        else: joy_x = 0

        if abs(left_y) > joystick_threshold:
            joy_y = -left_y
        else: joy_y = 0

        return (joy_x, joy_y)

    def __updateJoystickButtons(self):
        if self.controls.joystick_detector[self.controls.keybinds.disable_button].rising:
            self.constants.MENU_ENTERED.negate()
            self.chooseFieldCentric('negate')
            #self.set(screen_size = ScreenSize(self.constants.screen_size.width - 50, self.constants.screen_size.height - 50))
            #self.build()

            if self.constants.MENU_ENTERED.compare():
                pass
            else: pass
        
        '''if self.constants.MENU_ENTERED.compare():
            return 0'''
        
        if self.controls.joystick_detector[self.controls.keybinds.erase_trail_button].rising:
            self.robot.trail.hide_trail.set(True)

        if self.constants.FIELD_CENTRIC.compare():
            if self.controls.joystick_detector[self.controls.keybinds.direction_button].rising:
                self.constants.FORWARDS.negate()

                if self.constants.FORWARDS.compare():  
                    self.fade.reset(self.matchScreenSize(img_forwards, self.constants.screen_size.width))
                else: self.fade.reset(self.matchScreenSize(img_backwards, self.constants.screen_size.width))


        if self.controls.joystick_detector[self.controls.keybinds.zero_button].rising:
            self.robot.setPoseEstimate(Pose(0,0,0))
        


        if self.controls.joystick_detector[self.controls.keybinds.head_selection_button].high:
            self.constants.HEAD_SELECTION.set(True)
        else: self.constants.HEAD_SELECTION.set(False)

        if self.controls.joystick_detector[self.controls.keybinds.head_selection_button].rising:
                self.fade.reset(self.matchScreenSize(img_selecting_on, self.constants.screen_size.width))
        elif self.controls.joystick_detector[self.controls.keybinds.head_selection_button].falling:
                self.fade.reset(self.matchScreenSize(img_selecting_off, self.constants.screen_size.width))

        
        if self.controls.joystick_detector[self.controls.keybinds.trail_button].rising:
            self.robot.trail.draw_trail.negate()

            if self.robot.trail.draw_trail.compare():
                self.fade.reset(self.matchScreenSize(img_show_trail, self.constants.screen_size.width))
            else: self.fade.reset(self.matchScreenSize(img_hide_trail, self.constants.screen_size.width))



        if self.constants.HEAD_SELECTION.compare():
            target = self.robot.pose.head

            if self.controls.keybinds.state == "ps4":
                if self.controls.joystick_detector[self.controls.keybinds.turn_0].rising:
                    target = 0
                elif self.controls.joystick_detector[self.controls.keybinds.turn_90].rising:
                    target = 90
                elif self.controls.joystick_detector[self.controls.keybinds.turn_180].rising:
                    target = 180
                elif self.controls.joystick_detector[self.controls.keybinds.turn_270].rising:
                    target = 270
            elif self.controls.keybinds.calculate(self.controls.joystick.get_hat(0)) != None:
                target = self.controls.keybinds.calculate(self.controls.joystick.get_hat(0))
            
            self.robot.pose.head = self.robot.target_head = target




    