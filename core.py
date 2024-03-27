from BetterClasses.EdgeDetectorEx import *
from BetterClasses.MathEx import *
from TankDrive.constants import *
from constants import *

from queue import Queue
import pygame
import math

class Fade():
    def __init__(self):
        self.center = (half_w, half_l)
        self.opacity = -1

        self.font = pygame.font.SysFont(default_system_font, 150, 0, 40)
        self.text_rectangle = 0
        self.text = 0

        self.reset_time = 0
    
    def reset(self, text):
        self.opacity = 100
        self.reset_time = pygame.time.get_ticks()

        self.text = self.font.render(text, True, default_text_color, menu_color)
        self.text_rectangle = self.text.get_rect()
        self.text_rectangle.center = self.center
    
    def onScreen(self, screen):
        if self.opacity >= 0:
            current_time = pygame.time.get_ticks()

            if msToS(current_time - self.reset_time) > time_until_fade:
                self.opacity -= fade_percent
            
            if self.opacity < 0:
                self.opacity = 0

            self.text.set_alpha(percent2Alpha(self.opacity))
            screen.blit(self.text, self.text_rectangle)


class RobotSim():
    def __init__(self):
        self.image = pygame.image.load(robot_image_source)
        self.pose_font = pygame.font.SysFont(default_system_font, 50)

        #resize to match unit measure
        self.image = pygame.transform.scale(self.image, 
                (robot_length_in_pixels, robot_width_in_pixels))

        self.rotating_instance = self.image
        self.rotating_instance = pygame.transform.rotate(self.rotating_instance, -90)

        self.rectangle = self.rotating_instance.get_rect()
        self.mask = pygame.mask.from_surface(self.rotating_instance)

        self.pose = Pose(0, 0, 0)
        self.window_pose = toWindowCoords(self.pose)
        self.target_head = 0

        self.velocity = 0
        self.left_speed = 0
        self.right_speed = 0

        self.is_stopped = True
        self.start_time = 0

        self.trail_point_list = []
        self.draw_trail = False
 
    def elapsed_time(self):
        return time.perf_counter() - self.start_time

    def slewRateLimiter(self, targetSpeed):
        if self.is_stopped:
            self.start_time = pygame.time.get_ticks()
            self.is_stopped = False
        
        acceleration = (msToS(self.elapsed_time()) / acceleration_interval) * acceleration_dc
        if abs(acceleration) < abs(targetSpeed):
            return acceleration * signum(targetSpeed)
        return targetSpeed
    
    def setWheelPowers(self, left, right, sensitivity = 1, accelerating = False):
        if accelerating:
            left = self.slewRateLimiter(left)
            right = self.slewRateLimiter(right)

        self.left_speed = left * sensitivity
        self.right_speed = right * sensitivity

        if left == 0 and right == 0:
            self.is_stopped = True
        else: self.is_stopped = False

    def setPoseEstimate(self, pose):
        self.target_head = pose.head
        self.trail_point_list = []
        self.pose = pose
       

    
    def update(self, time):
        self.velocity = (self.right_speed + self.left_speed) / 2

        x, y, head = self.pose.x, self.pose.y, self.pose.head

        delta_x = self.velocity * math.cos(math.radians(head)) * time
        delta_y = self.velocity * math.sin(math.radians(head)) * time
        delta_head = math.degrees((self.right_speed - self.left_speed) / (robot_wheel_distance) * time)

        x += delta_x
        y += delta_y
        head += delta_head

        self.pose = Pose(x, y, normalizeDegrees(head))
        self.window_pose = toWindowCoords(self.pose)

    def onScreen(self, screen):
        self.__drawPose(screen)
        self.__drawTrail(screen)
        self.__drawRobot(screen)
        self.__drawBorder(screen)

    def __drawRobot(self, screen):
        self.rotating_instance = pygame.transform.rotate(self.rotating_instance, 
                        normalizeDegrees(360 - self.window_pose.head))

        self.rectangle = self.rotating_instance.get_rect()
        self.rectangle.center = (self.window_pose.x, self.window_pose.y)

        self.mask = pygame.mask.from_surface(self.rotating_instance)
        screen.blit(self.rotating_instance, self.rectangle)

        self.rotating_instance = self.image

    def __drawPose(self, screen):
        centimeters = pixels_to_cm(self.pose)

        coords = self.pose_font.render("x: {:.2f}  y: {:.2f} h: {:.2f}".format(centimeters.x, centimeters.y, self.pose.head), 
                                True, default_text_color, default_background_color)

        coords_rectangle = coords.get_rect()
        coords_rectangle.center = (3 / 4 * default_width, default_length - 60)

        screen.blit(coords, coords_rectangle)

    def __drawTrail(self, screen):
        if self.draw_trail:
            length = len(self.trail_point_list)

            if length == trail_len:
                self.trail_point_list.pop(0)

            self.trail_point_list.append((int(self.window_pose.x), int(self.window_pose.y)))

            isFirst = True
            for point in range(len(self.trail_point_list)):
                if not isFirst:
                    pygame.draw.line(screen, trail_color, 
                            self.trail_point_list[point - 1], self.trail_point_list[point], width = trail_width)
                isFirst = False
        else: self.trail_point_list = []

    def __drawBorder(self, screen):
        border = self.image.get_rect(center = (self.window_pose.x, self.window_pose.y))

        pivot = pygame.math.Vector2(self.window_pose.x, self.window_pose.y)

        p0 = (pygame.math.Vector2(border.topleft) - pivot).rotate(self.window_pose.head) + pivot 
        p1 = (pygame.math.Vector2(border.topright) - pivot).rotate(self.window_pose.head) + pivot 
        p2 = (pygame.math.Vector2(border.bottomright) - pivot).rotate(self.window_pose.head) + pivot 
        p3 = (pygame.math.Vector2(border.bottomleft) - pivot).rotate(self.window_pose.head) + pivot 

        pygame.draw.lines(screen, "yellow", True, [p0, p1, p2, p3], 3)
        


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


class Controls():
    def __init__(self):
        self.using_joystick = False
        self.keybinds = self.Keybinds()

        self.keyboard_len = 0
        self.joystick_len = 0

        self.joystick = None
        self.joystick_type = None

        self.keyboard_detector = self.__initKeyboardDetector()
        self.joystick_detector = self.__initJoystickDetector()

        self.menu_entered = False
        self.disabled = False
        self.forwards = True

    class Keybinds():
        def __init__(self):
            self.threshold = 0
            self.left_x = 0
            self.left_y = 0
            self.right_x = 0

            self.disable_button = 0
            self.direction_button = 0
            self.zero_button = 0
            self.menu_button = 0
            self.trail_button = 0

            self.turn_0 = 0
            self.turn_45 = 0
            self.turn_90 = 0
            self.turn_135 = 0
            self.turn_180 = 0
            self.turn_225 = 0
            self.turn_270 = 0
            self.turn_315 = 0

            self.state = None
        
        def setType(self, joystick_type):
            if joystick_type == "Xbox 360 Controller":
                self.setXbox()
            elif joystick_type == "PS4 Controller":
                self.setPS4()
            elif joystick_type == "Sony Interactive Entertainment Wireless Controller":
                self.setPS5()
            else: raise Exception ("Not a supported controller")

        def setXbox(self):
            self.state = "xbox"
            self.threshold = xbox_threshold
            self.left_x_number = xbox_left_x
            self.left_y_number = xbox_left_y
            self.right_x_number = xbox_right_x

            self.disable_button = xbox_disable_button
            self.direction_button = xbox_direction_button
            self.zero_button = xbox_zero_button
            self.menu_button = xbox_menu_button
            self.trail_button = xbox_trail_button

            self.turn_0 = xbox_turn_0
            self.turn_45 = xbox_turn_45
            self.turn_90 = xbox_turn_90
            self.turn_135 = xbox_turn_135
            self.turn_180 = xbox_turn_180
            self.turn_225 = xbox_turn_225
            self.turn_270 = xbox_turn_270
            self.turn_315 = xbox_turn_315
        
        def setPS4(self):
            self.state = "ps4"
            self.threshold = ps4_threshold
            self.left_x = ps4_left_x
            self.left_y = ps4_left_y
            self.right_x = ps4_right_x

            self.disable_button = ps4_disable_button
            self.direction_button = ps4_direction_button
            self.zero_button = ps4_zero_button
            self.menu_button = ps4_menu_button
            self.trail_button = ps4_trail_button

            self.turn_0 = ps4_turn_0
            self.turn_45 = ps4_turn_45
            self.turn_90 = ps4_turn_90
            self.turn_135 = ps4_turn_135
            self.turn_180 = ps4_turn_180
            self.turn_225 = ps4_turn_225
            self.turn_270 = ps4_turn_270
            self.turn_315 = ps4_turn_315
        
        def setPS5(self):
            self.state = "ps5"
            self.threshold = ps5_threshold
            self.left_x = ps5_left_x
            self.left_y = ps5_left_y
            self.right_x = ps5_right_x

            self.disable_button = ps5_disable_button
            self.direction_button = ps5_direction_button
            self.zero_button = ps5_zero_button
            self.menu_button = ps5_menu_button
            self.trail_button = ps5_trail_button

            self.turn_0 = ps5_turn_0
            self.turn_45 = ps5_turn_45
            self.turn_90 = ps5_turn_90
            self.turn_135 = ps5_turn_135
            self.turn_180 = ps5_turn_180
            self.turn_225 = ps5_turn_225
            self.turn_270 = ps5_turn_270
            self.turn_315 = ps5_turn_315

        #only for xbox and ps5
        def calculate(self, value):
            if value == self.turn_0:
                return 0
            if value == self.turn_45:
                return 45
            if value == self.turn_90:
                return 90
            if value == self.turn_135:
                return 135
            if value == self.turn_180:
                return 180
            if value == self.turn_225:
                return 225
            if value == self.turn_270:
                return 270
            if value == self.turn_315:
                return 315

            return None
    
    def __initKeyboardDetector(self):
        keyboard_detector = []
        key_states = pygame.key.get_pressed()

        for key in key_states:
            keyboard_detector.append(EdgeDetectorEx())
        
        self.keyboard_len = len(key_states)
        return keyboard_detector
    
    def __initJoystickDetector(self):
        joystick_detector = []
        if not self.joystick == None:
            self.joystick_len = self.joystick.get_numbuttons()                                                                    

            for button in range(self.joystick_len):
                joystick_detector.append(EdgeDetectorEx())
        
        return joystick_detector
    
    def update(self):
        if self.using_joystick:
            self.__updateJoystick()
        else: self.__updateKeyboard()
    
    def __updateKeyboard(self):
        key_states = pygame.key.get_pressed() 

        for key in range(self.keyboard_len):
            self.keyboard_detector[key].update()
            self.keyboard_detector[key].set(key_states[key])
    
    def __updateJoystick(self):
        for button in range(self.joystick_len):
            self.joystick_detector[button].update()

            if self.joystick.get_button(button) == 0:
                boolean = False
            else: boolean = True

            self.joystick_detector[button].set(boolean)
    
    def addJoystick(self, joystick):
        self.joystick = joystick
        
        if not joystick == None:
            self.using_joystick = True
            self.joystick_detector = self.__initJoystickDetector()
            self.joystick_type = self.joystick.get_name()
            self.keybinds.setType(self.joystick_type)
        else: 
            self.using_joystick = False
            self.joystick_type = None


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
        self.robot = RobotSim()
        self.fade = Fade()
    
    def update(self):
        self.__updateEventManager()

        #reset frame
        self.screen.fill(default_background_color)

        self.__updateControls()
        self.robot.update(self.dt)

        self.background.onScreen(self.screen)
        self.robot.onScreen(self.screen)
        self.fade.onScreen(self.screen)

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

        if self.controls.disabled:
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

        if self.controls.disabled:
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
            self.controls.disabled = not self.controls.disabled

            if self.controls.disabled:
                self.fade.reset("disabled")
            else: self.fade.reset("enabled")
        
        if self.controls.disabled:
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
            self.controls.menu_entered = True
        else: self.controls.menu_entered = False

        if self.controls.joystick_detector[self.controls.keybinds.menu_button].rising:
                self.fade.reset("menu entered")
        elif self.controls.joystick_detector[self.controls.keybinds.menu_button].falling:
                self.fade.reset("menu exited")

        
        if self.controls.joystick_detector[self.controls.keybinds.trail_button].rising:
            self.robot.draw_trail = not self.robot.draw_trail

            if self.robot.draw_trail:
                self.fade.reset("show trail")
            else: self.fade.reset("hide trail")



        if self.controls.menu_entered:
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






sim = Simulator()

while sim.running:

    sim.update()

    #if pygame.time.get_ticks() - startTime < 1000 * 1: #sec
    #    sim.robot_position.y -= velocity_multiplier * sim.dt
    