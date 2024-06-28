from pythfinder.Components.BetterClasses.booleanEx import *
from pythfinder.Components.Constants.constants import *
from pythfinder.Components.background import *
from pythfinder.Components.Menu.mainMenu import *
from pythfinder.Components.controls import *
from pythfinder.Components.robot import *
from pythfinder.Components.presets import *
from pythfinder.Components.fade import *

from datetime import datetime
import pygame


# file connecting all features into one big ecosystem of classes
#
# from the Simulator object, all different aspects of the simulator can be accessed and be modified
#
# one big feature is the implementation of dynamic constants. Any of the lower-hierarchized objects,
#   or the user, can modify the simulator constants, and the simulator makes sure that all the objects
#   run the latest constants available with an update system based on change detection
#
# the joystick logic is also run in this class, as well as all the updates, screen drawings and simulator
#   quiting events


class Auto(Enum):
    ENTER = auto()
    EXIT = auto()


class Simulator():
    def __init__(self, constants: Constants = Constants()):
        
        pygame.init()
        pygame.display.set_caption("PythFinder")
        self.running = BooleanEx(True)
        self.manual_control = BooleanEx(True)

        self.constants = constants
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.constants.screen_size.get())

        self.dt = 0

        self.background = Background(self.constants)
        self.presets = PresetManager()
        self.fade = Fade(self.constants)
        self.menu = Menu(MenuType.UNDEFINED, self.constants, None)
        self.robot = Robot(constants = self.constants)
        self.controls = Controls()

        self.__addDefaultPresets()
        


    def chooseFieldCentric(self, fun: Fun, bool = None):
        self.constants.FIELD_CENTRIC.choose(fun, bool)
        self.constants.FORWARDS.set(True)
    
    def chooseDrawRobotBorder(self, fun: Fun, bool = None):
        self.constants.ROBOT_BORDER.choose(fun, bool)
    
    def chooseUsingScreenBorder(self, fun: Fun, bool = None):
        self.constants.USE_SCREEN_BORDER.choose(fun, bool)
    
    def chooseMenuEntered(self, fun: Fun, bool = None):
        self.constants.MENU_ENTERED.choose(fun, bool)
    
    def chooseHeadSelection(self, fun: Fun, bool = None):
        self.constants.HEAD_SELECTION.choose(fun, bool)
    
    def chooseForward(self, fun: Fun, bool = None):
        self.constants.FORWARDS.choose(fun, bool)

    def chooseJoystickEnabled(self, fun: Fun, bool = None):
        self.constants.JOYSTICK_ENABLED.choose(fun, bool)


    def addPreset(self, 
                  name: str, 
                  constants: Constants, 
                  image: pygame.Surface | None = None,
                  size: Size | None = None,
                  key: None | int = None):
        
        constants.reset_buttons_default = True
        self.presets.add(Preset(name, self.constants, constants, image, size), key)

    def autonomus(self, do: Auto):
        match do:
            case Auto.ENTER:
                print("\n\nentering autonomus... ready?")

                self.robot.trail.draw_trail.set(True)
                self.constants.ERASE_TRAIL.set(False)
                self.manual_control.set(False)
                self.constants.USE_SCREEN_BORDER.set(False)
                self.presets.WRITING.set(False)
                #self.presets.on(1)

                self.robot.zeroDistance()
            case Auto.EXIT:
                self.manual_control.set(True)
                self.robot.trail.draw_trail.set(False)
                self.constants.ERASE_TRAIL.set(True)
                self.constants.USE_SCREEN_BORDER.set(True)

                print("\n\ntele-op just started! ---- ding ding 🔔")            
            case _:
                pass
        
        self.menu.check()


    def recalculate(self):
        if self.constants.recalculate.compare(False):
            return 0
        
        self.screen = pygame.display.set_mode(self.constants.screen_size.get())
        self.menu.recalculate()
        self.fade.recalculate()
        self.robot.recalculate()
        self.presets.recalculate()
        self.background.recalculate()

        self.menu.check()
        self.constants.recalculate.set(False)


    def matchScreenSize(self, image: pygame.Surface, width):
        size_multiplier = self.constants.WIDTH_PERCENT / 100 * width / self.constants.screen_size.MAX_WIDTH

        return pygame.transform.scale(image, 
            (size_multiplier * image.get_width(),
            size_multiplier * image.get_height()))

    def RUNNING(self):
        return self.running.compare()



    def update(self):
        self.recalculate()
        self.__updateEventManager()

        #reset frame
        self.screen.fill(default_background_color)

        if self.manual_control.compare():
            self.__updateControls()
        self.robot.update(self.dt)

        self.presets.onScreen(self.screen)
        self.background.onScreen(self.screen)
        self.robot.onScreen(self.screen)
        self.fade.onScreen(self.screen)
        if self.constants.MENU_ENTERED.compare():
            self.menu.addControls(self.controls)
            self.menu.onScreen(self.screen)

        self.__updateScreenshoot()
        pygame.display.update()
        self.dt = self.clock.tick(self.constants.FPS) / 1000
    


    def __updateEventManager(self):
        self.presets.WRITING.set(not self.constants.MENU_ENTERED.get())
        self.presets.addKey(None)
        self.menu.addKey(None)

        try:
            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    self.controls.addJoystick(pygame.joystick.Joystick(event.device_index))
                
                elif event.type == pygame.JOYDEVICEREMOVED:
                    self.controls.addJoystick(None)
                
                if event.type == pygame.KEYDOWN:
                    self.presets.addKey(event)
                    self.menu.addKey(event)

                if event.type == pygame.QUIT:
                    self.running.set(False)
                    print('\n\n')
                    pygame.quit()


        except: pass

    def __updateControls(self):
        self.controls.update()

        if self.controls.using_joystick.compare() and self.constants.JOYSTICK_ENABLED.compare():
            self.__updateJoystick()
        self.__updateCursorRobotMove()

    def __updateCursorRobotMove(self):
        if not (self.robot.cursorOver() and pygame.mouse.get_pressed()[0]):
            return None 
        
        cursor_pose = self.robot.toFieldCoords(Pose(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 0))
        cursor_pose.head = self.robot.pose.head
        self.robot.setPoseEstimate(cursor_pose)




    def __updateJoystick(self):
        left_x = round(self.controls.joystick.get_axis(self.controls.keybinds.left_x), 4)
        left_y = round(self.controls.joystick.get_axis(self.controls.keybinds.left_y), 4)
        right_x = round(self.controls.joystick.get_axis(self.controls.keybinds.right_x), 4)

        self.__updateJoystickButtons()

        match self.robot.kinematics.getType():
            case ChassisType.NON_HOLONOMIC:
                if self.constants.FIELD_CENTRIC.compare():
                    angular_multiplier, linear_x_multiplier = self.__updateJoystickFieldCentric((left_x, left_y))
                else: angular_multiplier, linear_x_multiplier = self.__updateJoystickRobotCentric((right_x, left_y))

                linear_y_multiplier = linear_x_multiplier * math.sin(math.radians(self.robot.pose.head))
                linear_x_multiplier = linear_x_multiplier * math.cos(math.radians(self.robot.pose.head))

            case ChassisType.HOLONOMIC:
                if self.constants.FIELD_CENTRIC.compare():
                    linear_x_multiplier, linear_y_multiplier = -left_y, left_x
                else:
                    rotated_vel_x = Point(x = -left_y, y = 0).rotateMatrix(math.radians(self.robot.pose.head))
                    rotated_vel_y = Point(x = 0, y = -left_x).rotateMatrix(-math.radians(self.robot.pose.head))

                    linear_x_multiplier, linear_y_multiplier = (rotated_vel_x + rotated_vel_y).tuple()

                angular_multiplier = right_x


        joy_vel_x = linear_x_multiplier * self.robot.constraints.linear.MAX_VEL
        joy_vel_y = linear_y_multiplier * self.robot.constraints.linear.MAX_VEL
        joy_ang_vel = angular_multiplier * self.robot.constraints.angular.MAX_VEL

        self.robot.setVelocities(ChassisState(
            velocity = Point(x = joy_vel_x, y = joy_vel_y),
            angular_velocity = joy_ang_vel
        ))

    def __updateJoystickFieldCentric(self, values):    
        left_x, left_y = values
        joystick_threshold = self.controls.keybinds.threshold

        if self.constants.MENU_ENTERED.compare():
            return (0,0)

        if (abs(left_x) > joystick_threshold or abs(left_y) > joystick_threshold):
            a_tan = math.atan2(left_y, left_x)

            self.robot.target_head = normalizeDegrees(math.degrees(a_tan + math.pi / 2))
            joy_y = min(1, math.hypot(left_x, left_y))


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

        if self.constants.MENU_ENTERED.compare():
            return (0,0)

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

            if self.constants.MENU_ENTERED.compare():
                if self.manual_control.compare():
                    self.robot.target_head = self.robot.pose.head
                self.constants.FREEZE_TRAIL.set(True)
                self.menu.reset()
            else: 
                self.constants.FREEZE_TRAIL.set(False)
        
        if self.constants.MENU_ENTERED.compare():
            return 0
        
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

    def __updateScreenshoot(self):
        if exists(self.controls.joystick):
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




    def __addDefaultPresets(self):
        for preset in default_presets:
            self.addPreset(*preset)     
            



    