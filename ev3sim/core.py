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

    def setConstants(self, constants: Constants):
        self.constants = constants

        self.screen = pygame.display.set_mode(self.constants.screen_size.get())

        self.background.setConstants(constants)
        self.robot.setConstants(constants)
        self.fade.setConstants(constants)



    def RUNNING(self):
        return self.running.compare()



    def chooseFieldCentric(self, fun, bool = None):
        self.constants.FIELD_CENTRIC.choose(fun, bool)
    
    def chooseDrawRobotBorder(self, fun, bool = None):
        self.constants.DRAW_BORDER.choose(fun, bool)
    
    def chooseUsingScreenBorder(self, fun, bool = None):
        self.constants.USE_SCREEN_BORDER.choose(fun, bool)




    def matchScreenSize(self, image, width):
        size_multiplier = self.constants.WIDTH_PERCENT / 100 * width / self.constants.screen_size.MAX_WIDTH

        return pygame.transform.scale(image, 
            (size_multiplier * image.get_width(),
            size_multiplier * image.get_height()))




    def update(self):
        self.__updateEventManager()

        #reset frame
        self.screen.fill(default_background_color)

        if self.manual_control.compare():
            self.__updateControls()
        self.robot.update(self.dt)

        self.background.onScreen(self.screen)
        self.robot.onScreen(self.screen)
        self.fade.onScreen(self.screen)
        if self.controls.menu_entered.compare():
            #self.menu.onScreen(self.screen, self.controls.joystick)
            pass

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

        left_speed = self.constants.cmToPixels(inverse[0])
        right_speed = self.constants.cmToPixels(inverse[1]) 
        self.robot.setWheelPowers(left = left_speed, right = right_speed)

    def __updateJoystickFieldCentric(self, values):    
        left_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        if self.controls.menu_entered.compare():
            return (0,0)

        if (abs(left_x) > joystick_threshold or abs(left_y) > joystick_threshold):
        
            self.robot.target_head = normalizeDegrees(math.degrees(math.atan2(left_y, left_x) + math.pi / 2))
            joy_y = math.hypot(left_y, left_x)

            if not self.controls.forwards.compare():
                joy_y = -joy_y
                self.robot.target_head = normalizeDegrees(self.robot.target_head + 180)

        else: 
            joy_y = 0
        
        joy_x = findShortestPath(self.robot.pose.head, self.robot.target_head) * 0.02

        return (joy_x, joy_y)

    def __updateJoystickRobotCentric(self, values):
        right_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        if self.controls.menu_entered.compare():
            return (0,0)

        if abs(right_x) > joystick_threshold:
            joy_x = -right_x
        else: joy_x = 0

        if abs(left_y) > joystick_threshold:
            joy_y = -left_y
        else: joy_y = 0

        return (joy_x, joy_y)

    def __updateJoystickButtons(self):
        if self.controls.joystick_detector[self.controls.keybinds.disable_button].rising:
            self.controls.menu_entered.negate()

            if self.controls.menu_entered.compare():
                pass
            else: pass
        
        if self.controls.menu_entered.compare():
            return 0
        
        if self.controls.joystick_detector[self.controls.keybinds.erase_trail_button].rising:
            self.robot.trail.hide_trail.set(True)

        if self.constants.FIELD_CENTRIC.compare():
            if self.controls.joystick_detector[self.controls.keybinds.direction_button].rising:
                self.controls.forwards.negate()

                if self.controls.forwards.compare():  
                    self.fade.reset(self.matchScreenSize(img_forwards, self.constants.screen_size.width))
                else: self.fade.reset(self.matchScreenSize(img_backwards, self.constants.screen_size.width))


        if self.controls.joystick_detector[self.controls.keybinds.zero_button].rising:
            self.robot.setPoseEstimate(Pose(0,0,0))
        


        if self.controls.joystick_detector[self.controls.keybinds.menu_button].high:
            self.controls.head_selection.set(True)
        else: self.controls.head_selection.set(False)

        if self.controls.joystick_detector[self.controls.keybinds.menu_button].rising:
                self.fade.reset(self.matchScreenSize(img_selecting_on, self.constants.screen_size.width))
        elif self.controls.joystick_detector[self.controls.keybinds.menu_button].falling:
                self.fade.reset(self.matchScreenSize(img_selecting_off, self.constants.screen_size.width))

        
        if self.controls.joystick_detector[self.controls.keybinds.trail_button].rising:
            self.robot.trail.draw_trail.negate()

            if self.robot.trail.draw_trail.compare():
                self.fade.reset(self.matchScreenSize(img_show_trail, self.constants.screen_size.width))
            else: self.fade.reset(self.matchScreenSize(img_hide_trail, self.constants.screen_size.width))



        if self.controls.head_selection.compare():
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




    