from pythfinder.Components.BetterClasses.mathEx import *
from abc import ABC, abstractmethod

from enum import Enum, auto
from typing import Tuple

# file containing robot drive kinematics
#
# an abstract kinematics class is used for ease of using
#
# for FLL purpose, the only kinematic model addressed in this file is
#   for the two wheel differential drive (also known as 'Tank Drive').
#   For a brief overview of the math, check out the wiki page:
#     (https://en.wikipedia.org/wiki/Differential_wheeled_robot)


def kinematicOptions():
    print("\n\nchoose from the following kinematic models: ")
    print(list(KinematicsType.__members__.keys()))



class WheelState():
    def __init__(self, velocity: float = 0, angle: float = 0):
        self.VELOCITY = velocity
        self.ANGLE = angle
    
    def copies(self, number: int):
        if number < 1:
            return None

        for _ in range(number):
            yield WheelState(self.VELOCITY, self.ANGLE)

class ChassisState():
    def __init__(self, 
                 velocity: Point = Point(), 
                 angular_velocity: float = 0) -> None:
        
        self.VEL = velocity
        self.ANG_VEL = angular_velocity
    
    def getVelocityMagnitude(self):
        return self.VEL.hypot()

    def isLike(self, other):
        return (
            self.VEL.x == other.VEL.x
                        and
            self.VEL.y == other.VEL.y
                        and
            self.ANG_VEL == other.ANG_VEL
        )

    def __add__(self, other):
        return ChassisState(
            velocity = self.VEL + other.VEL,
            angular_velocity = self.ANG_VEL + other.ANG_VEL
        )

    def fieldToRobot(self, robot_pose: Pose):
        alpha = normalizeRadians(self.VEL.atan2())
        beta = normalizeRadians(alpha + robot_pose.rad())

        magnitude = self.getVelocityMagnitude()
        
        x = math.sin(beta) * magnitude
        y = math.cos(beta) * magnitude

        if x < 10e-5: x = 0
        if y < 10e-5: y = 0

        return ChassisState(Point(x, y), self.ANG_VEL)

    def robotToField(self, robot_pose: Pose):
        beta = normalizeRadians(self.VEL.atan2())
        alpha = normalizeRadians(beta - robot_pose.rad())
        magnitude = self.getVelocityMagnitude()

        x = math.sin(alpha) * magnitude
        y = math.cos(alpha) * magnitude

        if x < 10e-5: x = 0
        if y < 10e-5: y = 0

        return ChassisState(Point(x, y), self.ANG_VEL)

class KinematicsType(Enum):
    # non-holonomic configurations
    TANK = auto()

    # holonomic configurations
    MECANUM = auto()
    SWERVE = auto()
    X_DRIVE = auto()
    H_DRIVE = auto()
    KIWI = auto()

class ChassisType(Enum):
    HOLONOMIC = auto()
    NON_HOLONOMIC = auto()



class Kinematics(ABC):
    def __init__(self) -> None:
        self.center_offset: Point = Point()

    @abstractmethod
    def inverse(self, chassis_state: ChassisState) -> tuple[WheelState]:
        pass

    @abstractmethod
    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        pass

    @abstractmethod
    def getType(self) -> ChassisType:
        pass

    @abstractmethod
    def copy(self):
        pass
