from enum import Enum, auto
import math

# file containting constraints data
#
# constraints are motion limitations at a given state of time
#
# constraints may change along a trajectory, so this data should not be
#   used to as the robot's REAL max velocity, which is determined
#   by it's mechanical systems' limitations 

default_max_robot_vel = 30 # cm/sec
default_max_robot_angular_vel = math.radians(90) #rad/sec

default_max_robot_acc = 10
default_max_robot_dec = -10
default_max_robot_ang_acc = math.radians(90)
default_max_robot_ang_dec = math.radians(-30)

default_track_width = 9.97


class ConstraintsType(Enum):
    TEMPORAL = auto()
    DISPLACEMENT = auto()


class Constraints():
    def __init__(self, 
                 vel: float | int = default_max_robot_vel, 
                 acc: float | int = default_max_robot_acc, 
                 dec: float | int = default_max_robot_dec,

                 ang_vel: float | int = default_max_robot_angular_vel,
                 ang_acc: float | int = default_max_robot_ang_acc, 
                 ang_dec: float | int = default_max_robot_dec,

                 track_width: float | int = default_track_width):
        
        self.MAX_VEL = abs(vel)
        self.MAX_ANG_VEL = abs(ang_vel)

        self.ACC = abs(acc)
        self.DEC = -abs(dec)
        self.ANG_ACC = abs(ang_acc)
        self.ANG_DEC = -abs(ang_dec)

        self.TRACK_WIDTH = abs(track_width)
    
    def set(self, 
            vel: float | int | None = None, 
            acc: float | int | None = None, 
            dec: float | int | None = None, 

            ang_vel: float | int | None = None, 
            ang_acc: float | int | None = None, 
            ang_dec: float | int | None = None,

            track_width: float | int | None = None):
        
        if vel is not None:
            self.MAX_VEL = abs(vel)
        if ang_vel is not None:
            self.MAX_ANG_VEL = abs(ang_vel)
        if acc is not None:
            self.ACC = abs(acc)
        if dec is not None:
            self.DEC = -abs(dec)
        if ang_acc is not None:
            self.ANG_ACC = abs(ang_acc)
        if ang_dec is not None:
            self.ANG_DEC = -abs(ang_dec)
        if track_width is not None:
            self.TRACK_WIDTH = abs(track_width)

    # creates a different instance to avoid unwanted modifications
    def copy(self):
        return Constraints(self.MAX_VEL, self.ACC, self.DEC,  
                          self.MAX_ANG_VEL, self.ANG_ACC, self.ANG_DEC,
                          self.TRACK_WIDTH)


# used in constrain markers.
# A cleaner way to store the data

class VolatileConstraints():
    def __init__(self, start: float, constraints: Constraints, type: ConstraintsType):
        self.start = start
        self.constraints = constraints

        self.type = type