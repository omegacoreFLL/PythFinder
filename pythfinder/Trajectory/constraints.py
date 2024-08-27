import math

# file containting constraints data
#
# constraints are motion limitations at a given state of time
#
# constraints may change along a trajectory, so this data should not be
#   used to as the robot's REAL max velocity, which is determined
#   by it's mechanical systems' limitations 

default_max_robot_vel_x = 27.7 # cm/sec
default_max_robot_vel_y = 0
default_max_robot_ang_vel = math.radians(150) #rad/sec

default_max_robot_acc = 27.7
default_max_robot_dec = -27.7
default_max_robot_ang_acc = math.radians(150)
default_max_robot_ang_dec = math.radians(-150)

default_track_width = 9.97


class Constraints():
    def __init__(self, 
                 vel: float = math.hypot(default_max_robot_vel_x, default_max_robot_vel_y),
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
    
    def is_like(self, other):
        return (self.MAX_VEL == other.MAX_VEL 
                            and
                self.ACC == other.ACC
                            and
                self.DEC == other.DEC)

    # creates a different instance to avoid unwanted modifications
    def copy(self):
        return Constraints(self.MAX_VEL, self.ACC, self.DEC)

class Constraints2D():
    def __init__(self, 
                 linear: Constraints = None, 
                 angular: Constraints = None,
                 track_width: float = default_track_width) -> None:
        
        self.linear = Constraints() if linear is None else linear
        self.angular = (Constraints(default_max_robot_ang_vel,
                                    default_max_robot_ang_acc,
                                    default_max_robot_ang_dec) if angular is None else angular)

        self.TRACK_WIDTH = track_width
    
    def copy(self):
        return Constraints2D(self.linear.copy(),
                             self.angular.copy(),
                             self.TRACK_WIDTH)
    
    def is_like(self, other):
        return (self.linear.is_like(other.linear)
                            and
                self.angular.is_like(other.angular)
                            and
                self.TRACK_WIDTH == other.TRACK_WIDTH)