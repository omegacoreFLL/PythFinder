from ev3sim.Components.background import *
from ev3sim.Components.constants import *
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
        self.running = True

        self.dt = 0

        self.screen = pygame.display.set_mode((default_width, default_length))
        self.clock = pygame.time.Clock()

        self.background = Background()
        self.controls = Controls()
        self.robot = Robot()
        self.fade = Fade()
        self.menu = Menu()
    
    def update(self):
        self.__updateEventManager()

        #reset frame
        self.screen.fill(default_background_color)

        self.__updateControls()
        self.robot.update(self.dt)

        self.background.onScreen(self.screen)
        self.robot.onScreen(self.screen)
        self.fade.onScreen(self.screen)
        if self.controls.menu_entered:
            self.menu.onScreen(self.screen, self.controls.joystick)

        pygame.display.update()
        self.dt = self.clock.tick(frame_rate) / 2000
    


    def __updateEventManager(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                using_joystick = True
                self.controls.addJoystick(pygame.joystick.Joystick(event.device_index))
            
            elif event.type == pygame.JOYDEVICEREMOVED:
                using_joystick = False
                self.controls.addJoystick(None)

            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()

    def __updateControls(self):
        self.controls.update()

        if self.controls.using_joystick:
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

        self.robot.setWheelPowers(left = velocity_multiplier * left_sign, 
                                    right = velocity_multiplier * right_sign)

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

        if field_centric:
            joy_x, joy_y = self.__updateJoystickFieldCentric((left_x, left_y))
        else: joy_x, joy_y = self.__updateJoystickRobotCentric((right_x, left_y))

        left_speed = (joy_y + joy_x) * velocity_multiplier
        right_speed = (joy_y - joy_x) * velocity_multiplier 
        self.robot.setWheelPowers(left = left_speed, right = right_speed)

    def __updateJoystickFieldCentric(self, values):    
        left_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        if self.controls.menu_entered:
            return (0,0)

        if (abs(left_x) > joystick_threshold or abs(left_y) > joystick_threshold):
        
            self.robot.target_head = normalizeDegrees(math.degrees(math.atan2(left_y, left_x) + math.pi / 2))
            joy_y = math.hypot(left_y, left_x)

            if not self.controls.forwards:
                joy_y = -joy_y
                self.robot.target_head = normalizeDegrees(self.robot.target_head + 180)

        else: 
            joy_y = 0
        
        joy_x = findShortestPath(self.robot.pose.head, self.robot.target_head) * 0.02

        return (joy_x, joy_y)

    def __updateJoystickRobotCentric(self, values):
        right_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        if self.controls.menu_entered:
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
            self.controls.menu_entered = not self.controls.menu_entered

            if self.controls.menu_entered:
                self.fade.reset("menu entered")
            else: self.fade.reset("menu exited")
        
        if self.controls.menu_entered:
            return 0

        if field_centric:
            if self.controls.joystick_detector[self.controls.keybinds.direction_button].rising:
                self.controls.forwards = not self.controls.forwards

                if self.controls.forwards:  
                    self.fade.reset("forwards")
                else: self.fade.reset("backwards")


        if self.controls.joystick_detector[self.controls.keybinds.zero_button].rising:
            self.robot.setPoseEstimate(Pose(0,0,0))
        


        if self.controls.joystick_detector[self.controls.keybinds.menu_button].high:
            self.controls.head_selection = True
        else: self.controls.head_selection = False

        if self.controls.joystick_detector[self.controls.keybinds.menu_button].rising:
                self.fade.reset("head selection: ON")
        elif self.controls.joystick_detector[self.controls.keybinds.menu_button].falling:
                self.fade.reset("head selection: OFF")

        
        if self.controls.joystick_detector[self.controls.keybinds.trail_button].rising:
            self.robot.draw_trail = not self.robot.draw_trail

            if self.robot.draw_trail:
                self.fade.reset("show trail")
            else: self.fade.reset("hide trail")



        if self.controls.head_selection:
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




    