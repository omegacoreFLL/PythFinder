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
default_max_robot_ang_vel = math.radians(90) #rad/sec

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
                 vel: float = default_max_robot_vel, 
                 acc: float = default_max_robot_acc, 
                 dec: float = default_max_robot_dec):
        
        self.MAX_VEL = abs(vel)

        self.ACC = abs(acc)
        self.DEC = -abs(dec)
    
    def set(self, 
            vel: float | None = None, 
            acc: float | None = None, 
            dec: float | None = None):
        
        if vel is not None:
            self.MAX_VEL = abs(vel)
        if acc is not None:
            self.ACC = abs(acc)
        if dec is not None:
            self.DEC = -abs(dec)


    # creates a different instance to avoid unwanted modifications
    def copy(self):
        return Constraints(self.MAX_VEL, self.ACC, self.DEC,  
                          self.MAX_ANG_VEL, self.ANG_ACC, self.ANG_DEC,
                          self.TRACK_WIDTH)

class Constraints3D():
    def __init__(self, 
                 x: Constraints = None, 
                 y: Constraints = None,
                 head: Constraints = None,
                 track_width: float = default_track_width) -> None:
        
        self.x = Constraints() if x is None else x
        self.y = Constraints(0, 0, 0) if y is None else y
        self.head = (Constraints(default_max_robot_ang_vel, 
                                default_max_robot_ang_acc,
                                default_max_robot_ang_dec)
                                
                        if head is None else head
        )

        self.TRACK_WIDTH = track_width


# used in constrain markers.
# A cleaner way to store the data
class VolatileConstraints():
    def __init__(self, start: float, constraints: Constraints, type: ConstraintsType):
        self.start = start
        self.constraints = constraints

        self.type = type