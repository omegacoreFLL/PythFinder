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


class ChassisType(Enum):
    HOLONOMIC = auto()
    NON_HOLONOMIC = auto()

class KinematicsType(Enum):
    # non-holonomic configurations
    TANK = auto()

    # holonomic configurations
    MECANUM = auto()
    SWERVE = auto()
    X_DRIVE = auto()
    H_DRIVE = auto()
    KIWI = auto()

class SwerveLockStates(Enum):
    X = auto()
    DIAMOND = auto()
    DEFAULT = auto()
    ZERO = auto()

class SwerveModules(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4



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


# center_offset = the vector from the center of the robot (0,0) to the turning center
# assumes a standard n-wheel tank chassis
class TankKinematics(Kinematics):
    def __init__(self, 
                 track_width: float = default_track_width,
                 center_offset: None | Point = None,
                 parallel_wheels: int = 2,
                 perpendicular_wheels: int = 0):
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.track_width = abs(track_width)

        self.parallel_wheels = abs(parallel_wheels)
        self.perpendicular_wheels = abs(perpendicular_wheels)

        if self.parallel_wheels % 2 == 1:
            raise Exception('\n\nyou kinda forgot one wheel somewhere')

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        velocity = chassis_state.VEL
        angular_velocity = chassis_state.ANG_VEL

        left_speed = velocity.x + self.track_width * 0.5 * angular_velocity
        right_speed = velocity.x - self.track_width * 0.5 * angular_velocity
        perpendicular_speed = velocity.y

        return (
            tuple(WheelState(left_speed, 0).copies(self.parallel_wheels // 2)) +
            tuple(WheelState(right_speed, 0).copies(self.parallel_wheels // 2)) +
            tuple(WheelState(perpendicular_speed, 0).copies(self.perpendicular_wheels))
        )
    
    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        midpoint = self.parallel_wheels // 2

        first_half = speeds[:midpoint]
        second_half = speeds[midpoint:self.parallel_wheels]
        perpendicular = speeds[self.parallel_wheels:]

        left_average = sum(state.VELOCITY for state in first_half) / midpoint
        right_average = sum(state.VELOCITY for state in second_half) / midpoint

        velocity_y = sum(state.VELOCITY for state in perpendicular) / self.perpendicular_wheels
        velocity_x = (left_average + right_average) / 2.0
        angular_velocity = (left_average - right_average) / self.track_width # rad / sec

        return ChassisState(
            velocity = Point(velocity_x, velocity_y),
            angular_velocity = angular_velocity
        )
    
    def getType(self) -> ChassisType:
        if self.perpendicular_wheels == 0:
            return ChassisType.NON_HOLONOMIC
        return ChassisType.HOLONOMIC

    def angular2LinearVel(self, angular_velocity):
        return self.track_width * 0.5 * angular_velocity


# assumes a standard 4 wheel mecanum chassis
class MecanumKinematics(Kinematics):
    def __init__(self,
                 track_width: float,
                 center_offset: None | Point = None):
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.track_width = abs(track_width)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        angular_to_linear = chassis_state.ANG_VEL * self.track_width
        velocity = chassis_state.VEL

        return (
            WheelState(velocity.x + velocity.y + angular_to_linear, 0), # FR
            WheelState(velocity.x - velocity.y - angular_to_linear, 0), # FL
            WheelState(velocity.x + velocity.y - angular_to_linear, 0), # BL
            WheelState(velocity.x - velocity.y + angular_to_linear, 0), # BR
        )

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        FR, FL, BL, BR = speeds
        
        velocity_x = (FR.VELOCITY + FL.VELOCITY + BL.VELOCITY + BR.VELOCITY) * 0.25
        velocity_y = (FR.VELOCITY - FL.VELOCITY + BL.VELOCITY - BR.VELOCITY) * 0.25
        angular_velocity = (FR.VELOCITY - FL.VELOCITY - BL.VELOCITY + BR.VELOCITY) * 0.25 / self.track_width

        return ChassisState(
                velocity = Point(velocity_x, velocity_y), 
                angular_velocity = angular_velocity
        )

    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC


# assumes a standard 4 module chassis (for now)
class SwerveKinematics(Kinematics):
    def __init__(self,
                 track_width: float,
                 track_length: float,
                 center_to_module: None | float = None,
                 center_offset: None | Point = None,
                 module_number: SwerveModules = SwerveModules.FOUR):
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.modules = module_number

        if self.modules is not SwerveModules.THREE:
            self.track_width = abs(track_width)
        else: self.track_width = 0 # you can't define the width of a triangle lol

        if self.modules is not SwerveModules.FOUR:
            self.track_length = abs(track_length)
        else: self.track_length = 0 # with 2 modules you don't need this value. Neither with 3

        if center_to_module is None:
            if self.modules is SwerveModules.THREE:
                raise Exception("\n\nprovide the center to module distance\n\n")
            self.R = math.hypot(self.track_width, self.track_length) * 0.5
        else: self.R = abs(center_to_module)

        self.ANGULAR_VELOCITY_X = self.track_length / self.R
        self.ANGULAR_VELOCITY_Y = self.track_width / self.R

        self.LOCKED: bool = False
        self.lock_state = SwerveLockStates.DIAMOND
        self.last_state = []

        for _ in range(self.modules.value):
            self.last_state.append(WheelState())
        self.last_state = tuple(self.last_state)
    
    def lock(self):
        self.LOCKED = True

    def unlock(self):
        self.LOCKED = False
    
    def setLockState(self, lock: SwerveLockStates):
        self.lock_state = lock

    def getLockState(self) -> Tuple[WheelState]:
        module_states: list = []

        match self.lock_state:
            case SwerveLockStates.DEFAULT:
                for i in range(self.modules.value):
                    module_states.append(
                        WheelState(0, self.last_state[i].ANGLE)
                    )
            
            case SwerveLockStates.DIAMOND:
                for i in range(self.modules.value):
                    module_states.append(
                        WheelState(0, (1 if i % 2 == 0 else -1) * math.pi / self.modules.value) 
                    )

            case SwerveLockStates.X:
                for i in range(self.modules.value):
                    module_states.append(
                        SwerveLockStates(0, (-1 if i % 2 == 0 else 1) * math.pi / self.modules.value)
                    )
            
            case SwerveLockStates.ZERO:
                for i in range(self.modules.value):
                    module_states.append(
                        WheelState(0, 0)
                    )
        
        return tuple(module_states)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        if self.LOCKED:
            return self.getLockState()

        velocity = chassis_state.VEL
        angular_velocity = chassis_state.ANG_VEL

        right: float = velocity.x - angular_velocity * self.ANGULAR_VELOCITY_X
        left: float = velocity.x + angular_velocity * self.ANGULAR_VELOCITY_X
        front: float = velocity.y + angular_velocity * self.ANGULAR_VELOCITY_Y
        back: float = velocity.y - angular_velocity * self.ANGULAR_VELOCITY_Y

        match self.modules:
            case SwerveModules.FOUR:
                self.last_state = (
                    WheelState(math.hypot(front, right), math.atan2(front, right)), # FR
                    WheelState(math.hypot(front, left), math.atan2(front, left)),   # FL
                    WheelState(math.hypot(back, left), math.atan2(back, left)),     # BL
                    WheelState(math.hypot(back, right), math.atan2(back, right))    # BR
                ) 
            
            case SwerveModules.THREE:
                pass

            case SwerveModules.TWO:
                self.last_state = (
                    WheelState(math.hypot(front, right), math.atan2(front, right)), # R
                    WheelState(math.hypot(back, left), math.atan2(back, left)),     # L
                )

        return self.last_state

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        velocity = Point()

        for each in speeds:
            velocity = velocity + Point(
                               x = each.VELOCITY * math.cos(each.ANGLE),
                               y = each.VELOCITY * math.sin(each.ANGLE))
            
        angular_velocity = velocity.x / self.R
        velocity = (velocity / len(speeds)).round(5)

        return ChassisState(
            velocity,
            round(angular_velocity, 5)
        )

    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC


# assumes a square-like chassis structure with 4 omni wheels
class X_DriveKinematics(Kinematics):
    def __init__(self, 
                 center_to_wheel: float,
                 center_offset: None | Point = None):

        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.R = abs(center_to_wheel)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        vx, vy, w = chassis_state.VEL.x, chassis_state.VEL.y, chassis_state.ANG_VEL

        FL = WheelState(vx - vy - w * self.R, 0)
        FR = WheelState(vx + vy + w * self.R, 0)
        BL = WheelState(vx - vy + w * self.R, 0)
        BR = WheelState(vx + vy - w * self.R, 0)
        
        return (FR, FL, BL, BR)

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        FR, FL, BL, BR = speeds

        velocity_x = (FR.VELOCITY + FL.VELOCITY + BL.VELOCITY + BR.VELOCITY) * 0.25
        velocity_y = (FR.VELOCITY - FL.VELOCITY - BL.VELOCITY + BR.VELOCITY) * 0.25
        angular_velocity = (+ FR.VELOCITY - FL.VELOCITY + BL.VELOCITY - BR.VELOCITY) * 0.25 / self.R

        return ChassisState(
            velocity = Point(velocity_x, velocity_y),
            angular_velocity = angular_velocity
        )

    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC


# assumes a standard 3 omni wheels kiwi chassis
#    front wheel of coords (R, 0)
#    left wheel of coords  (-R/2, -√3*R/2)
#    right wheel of coords (-R/2, √3*R/2)
class KiwiKinematics(Kinematics):
    def __init__(self, 
                 center_to_wheel: float,
                 center_offset: None | Point = None):
        
        self.center_offset = Pose(0,0) if center_offset is None else center_offset
        self.R = abs(center_to_wheel)

    def inverse(self, chassis_state: ChassisState) -> Tuple[WheelState]:
        # FW, LW, RW
        vx, vy, w = chassis_state.VEL.x, chassis_state.VEL.y, chassis_state.ANG_VEL

        forward_wheel = WheelState(velocity = vx - w * self.R,
                                   angle = 0)
        left_wheel = WheelState(velocity = - vx * 0.5 - vy * 0.5 * math.sqrt(3) - w * self.R,
                                angle = 0)
        right_wheel = WheelState(velocity = - vx * 0.5 + vy * 0.5 * math.sqrt(3) - w * self.R,
                                 angle = 0)
        
        return (forward_wheel, left_wheel, right_wheel)

    def forward(self, speeds: Tuple[WheelState]) -> ChassisState:
        FW, LW, RW = speeds

        return ChassisState(velocity = Point(x = 2 / 3 * (FW.VELOCITY - 0.5 * (LW.VELOCITY + RW.VELOCITY)),
                                             y = (RW.VELOCITY - LW.VELOCITY) / math.sqrt(3)).round(5),
                            angular_velocity = round(-(FW.VELOCITY + LW.VELOCITY + RW.VELOCITY) / (3 * self.R), 5))
    
    def getType(self) -> ChassisType:
        return ChassisType.HOLONOMIC