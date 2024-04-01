from ev3sim.Components.constants import *

import pygame 
import time 


class Robot():
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
        self.past_pose = Pose(0, 0, 0)
        self.window_pose = toWindowCoords(self.pose)
        self.target_head = 0

        self.velocity = 0
        self.left_speed = 0
        self.right_speed = 0
        self.past_left_speed = 0
        self.past_right_speed = 0

        self.distance = 0

        self.is_stopped = True
        self.start_time = 0

        self.trail_point_list = []
        self.draw_trail = False
        self.hide_trail = False

        self.pop_trail_loop = 0
        self.past_trail_length = 0
 
    def elapsed_time(self):
        return pygame.time.get_ticks() - self.start_time

    def slewRateLimiter(self, targetSpeed):
        if self.is_stopped:
            self.start_time = pygame.time.get_ticks()
            self.is_stopped = False
        
        acceleration = (msToS(self.elapsed_time()) / acceleration_interval) * acceleration_dc
        if abs(acceleration) < abs(targetSpeed):
            return acceleration * signum(targetSpeed)
        return targetSpeed
    
    def setWheelPowers(self, left, right, sensitivity = 1, accelerating = True):
        if abs(left) < 10 and abs(right) < 10:
            self.is_stopped = True
        else: self.is_stopped = False
    
        if accelerating:
            left = self.slewRateLimiter(left)
            right = self.slewRateLimiter(right)

        self.past_left_speed = self.left_speed
        self.past_right_speed = self.right_speed

        self.left_speed = left * sensitivity
        self.right_speed = right * sensitivity


    def setPoseEstimate(self, pose):
        self.target_head = pose.head
        self.trail_point_list = []
        self.pose = pose
       
    def zeroDistance(self):
        self.distance = 0

    def mirrorPoints(self, axis):
        length = len(self.trail_point_list)

        if length * 2 <= trail_len:
            for point in range(length):
                mirroring_point = tuple2Point(self.trail_point_list[length - 1 - point])
                self.trail_point_list.append(point2Tuple(symmetrical(mirroring_point, axis)))

    
    def update(self, time):
        self.velocity = (self.right_speed + self.left_speed) / 2

        x, y, head = self.pose.x, self.pose.y, self.pose.head

        delta_x = self.velocity * math.cos(math.radians(head)) * time
        delta_y = self.velocity * math.sin(math.radians(head)) * time
        delta_head = math.degrees((self.right_speed - self.left_speed) / (robot_wheel_distance) * time)
        delta_distance = hypot(self.pose.x - self.past_pose.x, self.pose.y - self.past_pose.y) / 10


        if using_border:
            next_pose = toWindowCoords(Pose(x + delta_x, y + delta_y, head + delta_head))
            border_points = self.__findBorder(next_pose)
            
            for point in border_points:
                if point[0] > default_width:
                    delta_y = -backing_distance
                if point[0] < 0:
                    delta_y = backing_distance  
                if point[1] > default_length:
                    delta_x = backing_distance
                if point[1] < 0:
                    delta_x = -backing_distance
                

        x += delta_x
        y += delta_y
        head += delta_head
        self.distance += delta_distance

        self.past_pose = self.pose
        self.pose = Pose(x, y, normalizeDegrees(head))
        self.window_pose = toWindowCoords(self.pose)

    def onScreen(self, screen):
        self.__drawPose(screen)
        self.__drawTrail(screen)
        self.__drawRobot(screen)
        if draw_border:
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
    
    def __erasePoint(self, length):
        if not erase_trail:
            return False
        
        if length == self.past_trail_length:
            self.pop_trail_loop += 1
        else: self.pop_trail_loop = 0

        if length == trail_len:
            return True
        if self.pop_trail_loop >= trail_loops:
            return True
    
        return False



    def __drawTrail(self, screen):
        if self.draw_trail:
            self.__build_Trail()

        if self.hide_trail:
            self.trail_point_list = []
            self.hide_trail = False
        else:
            isFirst = True
            for point in range(len(self.trail_point_list)):
                if not isFirst:
                    if distance(self.trail_point_list[point - 1], self.trail_point_list[point]) < drawing_trail_threshold:
                        pygame.draw.line(screen, trail_color, 
                                self.trail_point_list[point - 1], self.trail_point_list[point], width = trail_width)
                isFirst = False
            
            

    def __build_Trail(self):
        length = len(self.trail_point_list)

        if self.__erasePoint(length):
            self.trail_point_list.pop(0)
            length -= 1

        if length == 0:
            self.trail_point_list.append((int(self.window_pose.x), int(self.window_pose.y)))
        elif self.trail_point_list[length - 1] != (int(self.window_pose.x), int(self.window_pose.y)):
            self.trail_point_list.append((int(self.window_pose.x), int(self.window_pose.y)))
        
        self.past_trail_length = length


    def __findBorder(self, pose):
        border = self.image.get_rect(center = (pose.x, pose.y))

        pivot = pygame.math.Vector2(pose.x, pose.y)

        topLeft = (pygame.math.Vector2(border.topleft) - pivot).rotate(pose.head) + pivot 
        topRight = (pygame.math.Vector2(border.topright) - pivot).rotate(pose.head) + pivot 
        bottomRight = (pygame.math.Vector2(border.bottomright) - pivot).rotate(pose.head) + pivot 
        bottonLeft = (pygame.math.Vector2(border.bottomleft) - pivot).rotate(pose.head) + pivot 

        return [topLeft, topRight, bottomRight, bottonLeft]
    
    def __drawBorder(self, screen):
        pygame.draw.lines(screen, "yellow", True, self.__findBorder(self.window_pose), 3)
 