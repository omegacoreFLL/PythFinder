from pythfinder.Components.BetterClasses.edgeDetectorEx import *
from pythfinder.Components.BetterClasses.booleanEx import *
from pythfinder.Components.Constants.constants import *
from pythfinder.Trajectory.constraints import *
from pythfinder.Components.trail import *

from pythfinder.Trajectory.Control.Controllers.PIDController import *
from pythfinder.Trajectory.Kinematics.MecanumKinematics import *
from pythfinder.Trajectory.Kinematics.SwerveKinematics import *
from pythfinder.Trajectory.Kinematics.xDriveKinematics import *
from pythfinder.Trajectory.Kinematics.KiwiKinematics import *
from pythfinder.Trajectory.Kinematics.TankKinematics import *
from pythfinder.Trajectory.Kinematics.generic import *

import pygame
import math


# file containing robot information, such as:
#   position, velocity, dimension, image
#
# it's used for a differential two wheel drive, but can be
# extended to any type of wheeled robot with some modifications
#
# it incorporates arc based odometry, calculating it's position 
# on the field. For a more in-depth explanation, check out this paper:
#       (https://medium.com/@nahmed3536/wheel-odometry-model-for-differential-drive-robotics-91b85a012299)
#
# all the calculations are made with the wheel linear and angular velocity,
# but indivitual wheel speeds can be computed if needed



class Robot():
    def __init__(self, constants: Constants):

        self.rotating_instance = None
        self.rectangle = None
        self.pose_font = None
        self.image = None
        self.mask = None

        self.width_in_pixels = 0
        self.height_in_pixels = 0

        self.pose = Pose(0, 0, 90)
        self.past_pose = Pose(0, 0, 90)
        self.target_head = 90

        self.chassis_state = ChassisState()
        self.past_chassis_state = ChassisState()

        self.distance = 0
        self.start_time = 0
        self.last_rotation = Point()

        self.is_stopped = BooleanEx(True)
        self.mouse_locked = EdgeDetectorEx()
        self.head_controller = PIDController(constants.COEFF_JOY_HEAD)

        self.constants = constants

        self.window_pose = self.to_window_coords(self.pose)
        
        self.trail = Trail(self.constants)
        self.constraints = self.constants.constraints.copy()
        self.kinematics = self.constants.kinematics

        self.recalculate()


    def recalculate(self):
        self.head_controller.set(self.constants.COEFF_JOY_HEAD)
        self.pose_font = pygame.font.SysFont(self.constants.TEXT_FONT, 300) # this big because it will resize
        self.image = pygame.image.load(self.constants.ROBOT_IMG_SOURCE)     #   with the screen

        self.get_robot_size_in_pixels()

        #resize to match unit measure
        self.image = pygame.transform.scale(self.image, 
                (self.height_in_pixels, self.width_in_pixels))

        self.rotating_instance = self.image

        self.rectangle = self.rotating_instance.get_rect()
        self.mask = pygame.mask.from_surface(self.rotating_instance)

        self.constraints = self.constants.constraints

        self.__coords_width_offset_ratio = 3.9 / 4
        self.__coords_height_offset_ratio = 3.95 / 4

        self.trail.recalculate()


    def get_robot_size_in_pixels(self):
        self.width_in_pixels = self.constants.ROBOT_SCALE * self.constants.cm_to_pixels(self.constants.ROBOT_WIDTH)
        self.height_in_pixels =  self.constants.ROBOT_SCALE * self.constants.cm_to_pixels(self.constants.ROBOT_HEIGHT)

    def get_wheel_speeds(self):
        return self.kinematics.inverse(self.chassis_state)

    def to_motor_power(self, value):
        return round(value * self.constants.MAX_POWER / self.constants.REAL_MAX_VEL, 2)

    def to_field_coords(self, pose: Pose):
        return Pose((self.constants.screen_size.half_h - pose.y) * 10 / self.constants.PIXELS_2_DEC, 
                    (pose.x - self.constants.screen_size.half_w) * 10 / self.constants.PIXELS_2_DEC, 
                    normalize_degres(pose.head - 90))
    
    def to_window_coords(self, pose: Pose):
        return Pose(self.constants.screen_size.half_w + pose.y * self.constants.PIXELS_2_DEC / 10, 
                    self.constants.screen_size.half_h - pose.x * self.constants.PIXELS_2_DEC / 10, 
                    normalize_degres(pose.head + 90))
    
    def to_field_point(self, point: Point):
        return Point((self.constants.screen_size.half_h - point.y) * 10 / self.constants.PIXELS_2_DEC, 
                (point.x - self.constants.screen_size.half_w) * 10 / self.constants.PIXELS_2_DEC)

    def to_window_point(self, point: Point):
        return Point(self.constants.screen_size.half_w + point.y * self.constants.PIXELS_2_DEC / 10, 
                self.constants.screen_size.half_h - point.x * self.constants.PIXELS_2_DEC / 10)

 
    # FALSE (field centric velocities) / TRUE (robot centric velocities)
    def set_velocities(self, chassis_state: ChassisState, robot_centric: bool = False):
        
        if abs(chassis_state.get_velocity_magnitude()) < 0.01 and abs(chassis_state.ANG_VEL) < 0.01:
            self.is_stopped.set(True)
        else: self.is_stopped.set(False)

        self.past_chassis_state = chassis_state
        self.chassis_state = chassis_state

        if robot_centric:
            self.chassis_state.robot_to_field(self.pose)

    def set_pose_estimate(self, pose: Pose):
        self.pose = self.past_pose = Pose(pose.x, pose.y, normalize_degres(pose.head))
        
        self.window_pose = self.to_window_coords(self.pose)
        self.target_head = self.pose.head



    def zero(self):
        self.distance = 0



    def update(self, time: int):
        self.kinematics = self.constants.kinematics

        x, y, head = self.pose.x, self.pose.y, self.pose.head

        delta_x = self.chassis_state.VEL.x * time
        delta_y = self.chassis_state.VEL.y * time

        delta_head = math.degrees(self.chassis_state.ANG_VEL) * time
        delta_distance = self.pose.distance_to(self.past_pose) / 10 #dec

        if self.constants.SCREEN_BORDER.compare():
            next_pose = self.to_window_coords(Pose(x + delta_x, y + delta_y, head + delta_head))
            border_points = self.__find_border(next_pose)
            
            out_of_screen = True

            for point in border_points:
                out = False
                if point[0] > self.constants.screen_size.width:
                    delta_y = -self.constants.BACKING_DISTANCE
                    out = True
                if point[0] < 0:
                    delta_y = self.constants.BACKING_DISTANCE  
                    out = True
                if point[1] > self.constants.screen_size.height:
                    delta_x = self.constants.BACKING_DISTANCE
                    out = True
                if point[1] < 0:
                    delta_x = -self.constants.BACKING_DISTANCE
                    out = True
                
                out_of_screen = out and out_of_screen

            if out_of_screen:
                print("\n\n✨ achievement unlocked: where am I? ✨")
                x, y, head, delta_x, delta_y, delta_head = 0, 0, 0, 0, 0, 0
                
        x += delta_x
        y += delta_y
        head += delta_head
        self.distance += delta_distance

        self.past_pose = self.pose
        self.pose = Pose(x, y, normalize_degres(head))

        center_of_rotation = self.kinematics.center_offset.copy().negate().rotate_by(self.pose.rad())
        self.window_pose = self.to_window_coords(self.pose + center_of_rotation)



    def on_screen(self, screen: pygame.Surface):
        self.__draw_pose(screen)
        self.__draw_cursor(screen)
        self.trail.draw_trail(screen, self.pose)
        self.__draw_robot(screen)
        if self.constants.ROBOT_BORDER.compare():
            self.__draw_border(screen)
        if self.constants.VELOCITY_VECTOR.compare():
            self.__draw_velocity_vector(screen)
        



    def elapsed_time(self) -> int:
        return pygame.time.get_ticks() - self.start_time

    def is_cursor_over(self, cursor_point: Point) -> bool:
        rectangle_corners = pygame_vector_to_point(self.__find_border(self.window_pose))

        return point_in_rectangle(cursor_point, rectangle_corners)

    def update_cursor_move(self, clicked: bool, released: bool, cursor_point: Point) -> None:
        
        
        if clicked and self.is_cursor_over(cursor_point):
            self.mouse_locked.set(True)
        elif released:
            self.mouse_locked.set(False)
        else: 
            self.mouse_locked.set(self.mouse_locked.get())


        self.mouse_locked.update()
            
        
        if self.mouse_locked.high:
            new_pose = self.to_field_coords(Pose(cursor_point.x, cursor_point.y, 0))
            new_pose.head = self.pose.head
            self.target_head = self.pose.head

            self.set_pose_estimate(new_pose)
        
        elif self.mouse_locked.rising:
            self.constants.cursor.apply_system(pygame.SYSTEM_CURSOR_HAND)  
        elif self.mouse_locked.falling:
            self.constants.cursor.throwback()
            



    def __draw_robot(self, screen: pygame.Surface) -> None:
        self.rotating_instance = pygame.transform.rotate(self.rotating_instance, 
                        normalize_degres(360 - self.window_pose.head))

        self.rectangle = self.rotating_instance.get_rect()
        self.rectangle.center = (self.window_pose.x, self.window_pose.y)

        self.mask = pygame.mask.from_surface(self.rotating_instance)
        screen.blit(self.rotating_instance, self.rectangle)

        self.rotating_instance = self.image

    def __draw_pose(self, screen: pygame.Surface) -> None:
        coords = self.pose_font.render("x: {:.2f}  y: {:.2f} h: {:.2f}".format(self.pose.x, self.pose.y, self.pose.head), 
                                True, self.constants.TEXT_COLOR)
        coords = self.constants.resize_image_to_fit_screen_width(coords, self.constants.screen_size.width)

        coords_rectangle = coords.get_rect()
        coords_rectangle.center = (self.__coords_width_offset_ratio * self.constants.screen_size.width - coords.get_width() / 2,
                                   self.__coords_height_offset_ratio * self.constants.screen_size.height - coords.get_height() / 2)

        screen.blit(coords, coords_rectangle)
    
    def __draw_border(self, screen: pygame.Surface) -> None:
        pygame.draw.lines(screen, self.constants.ROBOT_BORDER_COLOR, True, self.__find_border(self.window_pose), 3)
    
    def __draw_cursor(self, screen: pygame.Surface) -> None:
        x, y = pygame.mouse.get_pos()
        to_field = self.to_field_point(Point(x, y)).tuple()

        coords = self.pose_font.render("x: {:.2f}  y: {:.2f}".format(to_field[0], to_field[1]), 
                                True, self.constants.TEXT_COLOR)
        coords = self.constants.resize_image_to_fit_screen_width(coords, self.constants.screen_size.width)
        
        coords_rectangle = coords.get_rect()
        coords_rectangle.center = ((1 - self.__coords_width_offset_ratio) * self.constants.screen_size.width + coords.get_width() / 2, 
                                   self.__coords_height_offset_ratio * self.constants.screen_size.height - coords.get_height() / 2)

        screen.blit(coords, coords_rectangle)

    def __draw_velocity_vector(self, screen: pygame.Surface) -> None:
        x_vel, y_vel = self.chassis_state.VEL.tuple()
        
        x_point = self.pose.point() + Point(x = x_vel, y = 0)
        y_point = self.pose.point() + Point(x = 0, y = y_vel)
        vel = self.pose.point() + Point(x_vel, y_vel)
        
        x_window = self.to_window_point(x_point)
        y_window = self.to_window_point(y_point)
        vel_window = self.to_window_point(vel)

        pygame.draw.line(screen, "green", 
                        self.window_pose.point().tuple(), x_window.tuple(), width = 8)
        pygame.draw.line(screen, "purple",
                       self.window_pose.point().tuple(), y_window.tuple(), width = 8)
        pygame.draw.line(screen, "orange",
                         self.window_pose.point().tuple(), vel_window.tuple(), width = 8)


    def __find_border(self, pose: Pose) -> List[Point]:
        border = self.image.get_rect(center = (pose.x, pose.y))

        pivot = pygame.math.Vector2(pose.x, pose.y)

        topLeft = (pygame.math.Vector2(border.topleft) - pivot).rotate(pose.head) + pivot 
        topRight = (pygame.math.Vector2(border.topright) - pivot).rotate(pose.head) + pivot 
        bottomRight = (pygame.math.Vector2(border.bottomright) - pivot).rotate(pose.head) + pivot 
        bottonLeft = (pygame.math.Vector2(border.bottomleft) - pivot).rotate(pose.head) + pivot 

        return [topLeft, topRight, bottomRight, bottonLeft]


    # debugging
    def print_pose(self) -> None:
        print("\nx:{0} y:{1} head:{2}".format(round(self.pose.x, 2), 
                                            round(self.pose.y, 2), 
                                            round(self.pose.head, 2)))
