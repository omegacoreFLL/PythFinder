from pythfinder.Components.BetterClasses.booleanEx import *
from pythfinder.Components.Constants.constants import *
from pythfinder.Components.Menu.mainMenu import *
from pythfinder.Components.background import *
from pythfinder.Components.controls import *
from pythfinder.Components.presets import *
from pythfinder.Components.robot import *
from pythfinder.Components.paint import *
from pythfinder.Components.fade import *

from datetime import datetime
import pygame


# This file connects all the features into one big ecosystem of classes.
#
# The Simulator object allows access and modification of different aspects of the simulator.
#
# One major feature is the implementation of dynamic constants. Any lower-hierarchical objects or the user can modify the simulator constants. 
# The simulator ensures that all objects run with the latest available constants through an update system based on change detection.
#
# The controller logic is also implemented in this class, along with updates, screen drawings, and simulator quitting events.


class Simulator():
    def __init__(self, constants: Constants = Constants()):
        """
        Initializes the Simulator class.

        Args:
            constants (Constants): The constants object containing simulation parameters.
        """
        pygame.display.set_caption("PythFinder")
        
        self.running = BooleanEx(True)
        self.manual_control = BooleanEx(True)

        self.constants = constants
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.constants.screen_size.get(), flags = pygame.RESIZABLE)

        self.dt = 0
        self.mouse_click = EdgeDetectorEx()
        self.mouse_pose = None

        self.background = Background(self.constants)
        self.presets = PresetManager(self.constants)
        self.fade = Fade(self.constants)
        self.controls = Controls()
        self.menu = Menu(MenuType.UNDEFINED, self.constants, self.controls, None)
        self.robot = Robot(constants = self.constants)
        self.paint = Paint(constants = self.constants)

        self.__add_default_presets()



    def add_preset(self, 
                  name: str, 
                  constants: Constants, 
                  image: pygame.Surface | None = None,
                  size: Size | None = None,
                  key: None | int = None):
        
        constants.reset_buttons_default = True
        self.presets.add(Preset(name, self.constants, constants, image, size), key)


    def recalculate(self):
        resize_screen = self.constants.check_screen_size(self.screen.get_size())

        if self.constants.recalculate.compare(False):
            return 0
        
        if resize_screen:
            self.screen = pygame.display.set_mode(self.constants.screen_size.get(), pygame.RESIZABLE)
        else: self.constants.screen_size = ScreenSize(self.screen.get_size()[0], self.screen.get_size()[1])

        self.menu.recalculate()
        self.fade.recalculate()
        self.paint.recalculate()
        self.robot.recalculate()
        self.presets.recalculate()
        self.background.recalculate()

        self.menu.check()
        self.constants.recalculate.set(False)


    def RUNNING(self):
        return self.running.compare()

    def update(self):
        self.mouse_pose = pygame.mouse.get_pos()

        self.recalculate()
        self.__update_event_manager()

        #reset frame
        self.screen.fill(default_background_color)

        if self.manual_control.compare():
            self.__update_controls()
        self.robot.update(self.dt)

        self.presets.on_screen(self.screen)
        self.background.on_screen(self.screen)
        self.paint.on_screen(self.screen, self.mouse_pose)
        self.robot.on_screen(self.screen)
        self.fade.on_screen(self.screen)
        if self.constants.MENU_ENTERED.compare():
            self.menu.on_screen(self.screen)

        pygame.display.flip()
        self.dt = self.clock.tick(self.constants.FPS) / 1000

        self.__update_screenshoots()
    
    
    def __update_event_manager(self):
        if self.manual_control.compare():
            self.presets.WRITING.set(not self.constants.MENU_ENTERED.get())

        self.paint.add_key(None, self.mouse_click.get(), self.mouse_pose if self.mouse_click.rising else None)
        self.controls.add_key(None)
        self.presets.add_key(None)
        self.menu.add_key(None)

        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                self.controls.add_joystick(pygame.joystick.Joystick(event.device_index))
                    
            elif event.type == pygame.JOYDEVICEREMOVED:
                self.controls.add_joystick(None)
                    
            if event.type == pygame.KEYDOWN:
                if self.constants.MENU_ENTERED.compare(False) and self.constants.HAND_DRAWING.compare():
                        self.paint.add_key(event, self.mouse_click.get())
                self.controls.add_key(event)
                self.presets.add_key(event)
                self.menu.add_key(event)

            if event.type == pygame.QUIT:
                self.running.set(False)
                print('\n\n')
                pygame.quit()



    def __update_controls(self):
        self.controls.update()

        if self.controls.using_joystick.compare() and self.constants.JOYSTICK_ENABLED.compare():
            self.__update_controller()
        self.__update_keyboard_buttons()

        self.__update_cursor_robot_move()


    def __update_cursor_robot_move(self):
        self.mouse_click.set(pygame.mouse.get_pressed()[0]) # left click
        self.mouse_click.update()

        if self.manual_control.compare() and self.constants.MENU_ENTERED.compare(False):   # move only manual control is enabled and not entered meny
            self.robot.update_cursor_move(clicked = self.mouse_click.rising, released = self.mouse_click.falling,
                                        cursor_point = Point(self.mouse_pose[0], self.mouse_pose[1]))


    def __update_controller(self):
        left_x = round(self.controls.joystick.get_axis(self.controls.keybinds.left_x), 4)
        left_y = round(self.controls.joystick.get_axis(self.controls.keybinds.left_y), 4)
        right_x = round(self.controls.joystick.get_axis(self.controls.keybinds.right_x), 4)

        self.__update_controller_buttons()

        match self.robot.kinematics.get_type():
            case ChassisType.NON_HOLONOMIC:
                if self.constants.FIELD_CENTRIC.compare():
                    angular_multiplier, linear_x_multiplier = self.__update_controller_field_centric((left_x, left_y))
                else: angular_multiplier, linear_x_multiplier = self.__update_controller_robot_centric((right_x, left_y))

                linear_y_multiplier = linear_x_multiplier * math.sin(math.radians(self.robot.pose.head))
                linear_x_multiplier = linear_x_multiplier * math.cos(math.radians(self.robot.pose.head))

            case ChassisType.HOLONOMIC:
                if self.constants.FIELD_CENTRIC.compare():
                    linear_x_multiplier, linear_y_multiplier = -left_y, left_x
                else:
                    rotated_vel_x = Point(x = -left_y, y = 0).rotate_by(math.radians(self.robot.pose.head))
                    rotated_vel_y = Point(x = 0, y = -left_x).rotate_by(-math.radians(self.robot.pose.head))

                    linear_x_multiplier, linear_y_multiplier = (rotated_vel_x + rotated_vel_y).tuple()

                angular_multiplier = right_x

                linear_x_multiplier = 0 if abs(linear_x_multiplier) < self.controls.keybinds.threshold else linear_x_multiplier
                linear_y_multiplier = 0 if abs(linear_y_multiplier) < self.controls.keybinds.threshold else linear_y_multiplier
                angular_multiplier = 0 if abs(angular_multiplier) < self.controls.keybinds.threshold else angular_multiplier


        joy_vel_x = linear_x_multiplier * self.robot.constraints.linear.MAX_VEL
        joy_vel_y = linear_y_multiplier * self.robot.constraints.linear.MAX_VEL
        joy_ang_vel = angular_multiplier * self.robot.constraints.angular.MAX_VEL


        self.robot.set_velocities(ChassisState(
            velocity = Point(x = joy_vel_x, y = joy_vel_y),
            angular_velocity = joy_ang_vel
        ))

    def __update_controller_field_centric(self, values):    
        left_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        if self.constants.MENU_ENTERED.compare():
            return (0,0)

        if (abs(left_x) > joystick_threshold or abs(left_y) > joystick_threshold):
            a_tan = math.atan2(left_y, left_x)

            self.robot.target_head = normalize_degres(math.degrees(a_tan + math.pi / 2))
            joy_y = min(1, math.hypot(left_x, left_y))


            if self.constants.FORWARDS.compare(False):
                joy_y = -joy_y
                self.robot.target_head = normalize_degres(self.robot.target_head + 180)

        else: 
            joy_y = 0

        error = find_shortest_path(self.robot.target_head, self.robot.pose.head) / 180
        joy_x = self.robot.head_controller.calculate(error)

        if abs(joy_x) < joystick_threshold:
            joy_x = 0

        return (joy_x, joy_y)

    def __update_controller_robot_centric(self, values):
        right_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        if self.constants.MENU_ENTERED.compare():
            return (0,0)

        if abs(right_x) > joystick_threshold:
            joy_x = right_x
        else: joy_x = 0

        if abs(left_y) > joystick_threshold:
            joy_y = -left_y
        else: joy_y = 0

        return (joy_x, joy_y)

    def __update_controller_buttons(self):
        if self.controls.joystick_detector[self.controls.keybinds.disable_button].rising:                       # enter with keyboard
            self.__update_buttons_menu()

        if self.constants.MENU_ENTERED.compare():
            return 0
        
        if self.controls.joystick_detector[self.controls.keybinds.erase_trail_button].rising:
            self.robot.trail.hide_trail.set(True)

        if self.constants.FIELD_CENTRIC.compare():
            if self.controls.joystick_detector[self.controls.keybinds.direction_button].rising:
                self.constants.FORWARDS.negate()

                if self.constants.FORWARDS.compare():  
                    self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_forwards, self.constants.screen_size.width))
                else: self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_backwards, self.constants.screen_size.width))


        if self.controls.joystick_detector[self.controls.keybinds.zero_button].rising:
            self.robot.set_pose_estimate(Pose(0,0,0))
        


        if self.controls.joystick_detector[self.controls.keybinds.head_selection_button].high:
            self.constants.HEAD_SELECTION.set(True)
        else: self.constants.HEAD_SELECTION.set(False)

        if self.controls.joystick_detector[self.controls.keybinds.head_selection_button].rising:
                self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_selecting_on, self.constants.screen_size.width))
        elif self.controls.joystick_detector[self.controls.keybinds.head_selection_button].falling:
                self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_selecting_off, self.constants.screen_size.width))

        
        if self.controls.joystick_detector[self.controls.keybinds.trail_button].rising:
            self.robot.trail.draw_trail.negate()

            if self.robot.trail.draw_trail.compare():
                self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_show_trail, self.constants.screen_size.width))
            else: self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_hide_trail, self.constants.screen_size.width))



        if self.constants.HEAD_SELECTION.compare():
            target = self.robot.pose.head

            if self.controls.keybinds.state is JoyType.PS4:
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


    def __update_keyboard_buttons(self):
        if self.controls.keyboard_detector[pygame.K_ESCAPE].rising:
            self.__update_buttons_menu()
        
        if self.constants.MENU_ENTERED.compare():
            return 0
        
        if self.controls.keyboard_detector[pygame.K_DELETE].rising:
            self.robot.trail.hide_trail.set(True)

        if self.constants.FIELD_CENTRIC.compare():
            if self.controls.keyboard_detector[pygame.K_SPACE].rising:
                self.constants.FORWARDS.negate()

                if self.constants.FORWARDS.compare():  
                    self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_forwards, self.constants.screen_size.width))
                else: self.fade.reset(self.constants.resize_image_to_fit_screen_width(img_backwards, self.constants.screen_size.width))


        if self.controls.keyboard_detector[pygame.K_TAB].rising:
            self.robot.set_pose_estimate(Pose(0,0,0))

    def __update_buttons_menu(self):
        self.constants.MENU_ENTERED.negate()

        if self.constants.MENU_ENTERED.compare():
            if self.robot.mouse_locked.get():
                self.robot.mouse_locked.set(False)
                self.constants.cursor.apply_system(pygame.SYSTEM_CURSOR_ARROW, remember = False)
            else: self.constants.cursor.apply_system(pygame.SYSTEM_CURSOR_ARROW)

            if self.manual_control.compare():
                self.robot.target_head = self.robot.pose.head
            self.constants.FREEZE_TRAIL.set(True)
            self.menu.reset()
        else:
            self.constants.cursor.throwback()
            self.constants.FREEZE_TRAIL.set(False)




    def __update_screenshoots(self):
        if self.controls.joystick is not None:
            if self.manual_control.compare(False):
                self.controls.update()
            
            if self.controls.joystick_detector[self.controls.keybinds.screenshot_button].rising:
                #take a screenshot

                screenshot = pygame.Surface(self.constants.screen_size.get())
                screenshot.blit(self.screen, (0, 0))

                date_and_time_info = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                image_name_with_time_format = "{0}.png".format(date_and_time_info)
                individual_data = date_and_time_info.split("-")

                device_screenshot_path = os.path.join(os.path.join(os.path.dirname(__file__), "Screenshots"), image_name_with_time_format)
                pygame.image.save(screenshot, device_screenshot_path)

                print("\n\nyou took a screenshot :o -- check it out:")

                for each in individual_data: # easter egg? :0
                    if each == '42' or each == '69':
                        print("\n\nnice 😎")
                        break

                print(device_screenshot_path)




    def __add_default_presets(self):
        for preset in default_presets:
            self.add_preset(*preset)     
            



    