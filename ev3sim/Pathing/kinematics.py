from abc import ABC, abstractmethod
from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *

class Kinematics(ABC):

    @abstractmethod
    def inverseKinematics(self, velocity, angular_velocity):
        pass

    @abstractmethod
    def forwardKinematics(self, speeds: tuple):
        pass

class TankKinematics(Kinematics):
    def __init__(self, track_width):
        self.track_width = track_width

    def forwardKinematics(self, speeds: tuple):
        left_speed = speeds[0]
        right_speed = speeds[1]

        velocity = (right_speed + left_speed) / 2.0
        angular_velocity = (left_speed - right_speed) / self.track_width # rad / sec

        return (velocity, angular_velocity)

    def inverseKinematics(self, velocity, angular_velocity):
        left_speed = velocity + self.track_width / 2.0 * angular_velocity
        right_speed = velocity - self.track_width / 2.0 * angular_velocity

        return (left_speed, right_speed)
    
    def angular2LinearVel(self, angular_velocity):
        return self.track_width / 2.0 * angular_velocity

