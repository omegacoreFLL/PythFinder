from abc import ABC, abstractmethod
from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Components.Constants.constants import *

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

    @abstractmethod
    def inverse(self, chassis_state: ChassisState) -> tuple[WheelState]:
        pass

    @abstractmethod
    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        pass

    @abstractmethod
    def getType(self) -> ChassisType:
        pass
