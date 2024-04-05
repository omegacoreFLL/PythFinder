from ev3sim.Components.Controllers.PIDController import *
from ev3sim.Components.BetterClasses.booleanEx import *
from ev3sim.Components.Constants.constrains import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Pathing.kinematics import *
from ev3sim.Components.trail import *

import pygame







class Robot():
    def __init__(self, constants: Constants):

        self.rotating_instance = None
        self.rectangle = None
        self.pose_font = None
        self.image = None
        self.mask = None

        self.width_in_pixels = 0
        self.height_in_pixels = 0

        self.pose = Pose(0, 0, 0)
        self.past_pose = Pose(0, 0, 0)
        self.target_head = 0

        self.left_speed = 0
        self.right_speed = 0

        self.velocity = 0
        self.angular_velocity = 0
        self.past_velocity = 0
        self.past_angular_velocity = 0

        self.distance = 0
        self.start_time = 0

        self.is_stopped = BooleanEx(True)
        self.head_controller = PIDController(constants.COEFF_JOY_HEAD)

        self.constants = 0
        self.constrains = 0

        self.setConstants(constants)
        self.setConstrains(Constrains())

        self.window_pose = self.toWindowCoords(self.pose)
        
        self.trail = Trail(self.constants)
        self.kinematics = TankKinematics(self.constrains.TRACK_WIDTH)



    def setConstrains(self, constrains: Constrains):
        self.constrains = constrains

        self.kinematics = TankKinematics(self.constrains.TRACK_WIDTH)

    def setConstants(self, constants: Constants):
        self.constants = constants

        self.head_controller.set(constants.COEFF_JOY_HEAD)
        self.pose_font = pygame.font.SysFont(self.constants.TEXT_FONT, 50)
        self.image = pygame.image.load("{0}{1}.{2}".format(self.constants.ROBOT_IMG_PATH, 
                                                           self.constants.ROBOT_IMG_NAME, 
                                                           self.constants.ROBOT_IMG_EX))

        self.getRobotSizeInPixels()

        #resize to match unit measure
        self.image = pygame.transform.scale(self.image, 
                (self.height_in_pixels, self.width_in_pixels))

        self.rotating_instance = self.image
        self.rotating_instance = pygame.transform.rotate(self.rotating_instance, -90)

        self.rectangle = self.rotating_instance.get_rect()
        self.mask = pygame.mask.from_surface(self.rotating_instance)


    def getRobotSizeInPixels(self):
        self.width_in_pixels = self.constants.ROBOT_SCALE * self.constants.cmToPixels(self.constants.ROBOT_WIDTH)
        self.height_in_pixels =  self.constants.ROBOT_SCALE * self.constants.cmToPixels(self.constants.ROBOT_HEIGHT)

    def getWheelSpeeds(self):
        forward = self.kinematics.inverseKinematics(self.velocity, self.angular_velocity)

        self.left_speed = forward[0]
        self.right_speed = forward[1]



    def toFieldCoords(self, pose):
        return Pose(self.constants.screen_size.half_h - pose.y, 
                    pose.x - self.constants.screen_size.half_w, 
                    normalizeDegrees(pose.head - 90))
    
    def toWindowCoords(self, pose):
        return Pose(self.constants.screen_size.half_w + pose.y, 
                    self.constants.screen_size.half_h - pose.x, 
                    normalizeDegrees(pose.head + 90))
    
    def toFieldPoint(self, point):
        return (self.constants.screen_size.half_h - point.y, 
                point.x - self.constants.screen_size.half_w)

    def toWindowPoint(self, point):
        return (self.constants.screen_size.half_w + point.y, 
                self.constants.screen_size.half_h - point.x)

 
 
    def setVelocities(self, vel, ang_vel):
        if abs(vel) < 0.01 and abs(ang_vel) < 0.01:
            self.is_stopped.set(True)
        else: self.is_stopped.set(False)

        self.past_velocity = self.velocity
        self.past_angular_velocity = self.angular_velocity

        self.velocity = self.constants.cmToPixels(vel)
        self.angular_velocity = ang_vel

    def setPoseEstimate(self, pose):
        self.target_head = pose.head
        self.pose = pose




    def zeroDistance(self):
        self.distance = 0

    def update(self, time):
        self.getWheelSpeeds()

        x, y, head = self.pose.x, self.pose.y, self.pose.head

        delta_x = self.velocity * math.cos(math.radians(head)) * time
        delta_y = self.velocity * math.sin(math.radians(head)) * time
        delta_head = math.degrees(self.angular_velocity) * time
        delta_distance = self.pose.distanceTo(self.past_pose) / 10 #dec


        if self.constants.USE_SCREEN_BORDER.compare():
            next_pose = self.toWindowCoords(Pose(x + delta_x, y + delta_y, head + delta_head))
            border_points = self.__findBorder(next_pose)
            
            for point in border_points:
                if point[0] > self.constants.screen_size.width:
                    delta_y = -self.constants.BACKING_DISTANCE
                if point[0] < 0:
                    delta_y = self.constants.BACKING_DISTANCE  
                if point[1] > self.constants.screen_size.height:
                    delta_x = self.constants.BACKING_DISTANCE
                if point[1] < 0:
                    delta_x = -self.constants.BACKING_DISTANCE
                

        x += delta_x
        y += delta_y
        head += delta_head
        self.distance += delta_distance


        self.past_pose = self.pose
        self.pose = Pose(x, y, normalizeDegrees(head))
        self.window_pose = self.toWindowCoords(self.pose)

    def onScreen(self, screen):
        self.__drawPose(screen)
        self.trail.drawTrail(screen, self.window_pose)
        self.__drawRobot(screen)
        if self.constants.DRAW_ROBOT_BORDER.compare():
            self.__drawBorder(screen)

    def elapsed_time(self):
        return pygame.time.get_ticks() - self.start_time
   



    def __drawRobot(self, screen):
        self.rotating_instance = pygame.transform.rotate(self.rotating_instance, 
                        normalizeDegrees(360 - self.window_pose.head))

        self.rectangle = self.rotating_instance.get_rect()
        self.rectangle.center = (self.window_pose.x, self.window_pose.y)

        self.mask = pygame.mask.from_surface(self.rotating_instance)
        screen.blit(self.rotating_instance, self.rectangle)

        self.rotating_instance = self.image

    def __drawPose(self, screen):
        centimeters = self.constants.pixelsToCmPoint(self.pose)

        coords = self.pose_font.render("x: {:.2f}  y: {:.2f} h: {:.2f}".format(centimeters.x, centimeters.y, self.pose.head), 
                                True, self.constants.TEXT_COLOR, self.constants.BACKGROUND_COLOR)

        coords_rectangle = coords.get_rect()
        coords_rectangle.center = (3 / 4 * self.constants.screen_size.width, self.constants.screen_size.height - 60)

        screen.blit(coords, coords_rectangle)
    
    def __drawBorder(self, screen):
        pygame.draw.lines(screen, "yellow", True, self.__findBorder(self.window_pose), 3)
 
    def __findBorder(self, pose):
        border = self.image.get_rect(center = (pose.x, pose.y))

        pivot = pygame.math.Vector2(pose.x, pose.y)

        topLeft = (pygame.math.Vector2(border.topleft) - pivot).rotate(pose.head) + pivot 
        topRight = (pygame.math.Vector2(border.topright) - pivot).rotate(pose.head) + pivot 
        bottomRight = (pygame.math.Vector2(border.bottomright) - pivot).rotate(pose.head) + pivot 
        bottonLeft = (pygame.math.Vector2(border.bottomleft) - pivot).rotate(pose.head) + pivot 

        return [topLeft, topRight, bottomRight, bottonLeft]
