import math


default_max_robot_vel = 30 # cm/sec
default_max_robot_angular_vel = math.radians(90) #rad/sec

default_max_robot_acc = 10
default_max_robot_dec = -10
default_max_robot_ang_acc = math.radians(90)
default_max_robot_ang_dec = math.radians(-30)

default_track_width = 9.97



class Constrains():
    def __init__(self, vel = default_max_robot_vel, ang_vel = default_max_robot_angular_vel,
                 acc = default_max_robot_acc, dec = default_max_robot_dec,
                 ang_acc = default_max_robot_ang_acc, ang_dec = default_max_robot_dec,
                 track_width = default_track_width):
        
        self.MAX_VEL = abs(vel)
        self.MAX_ANG_VEL = abs(ang_vel)

        self.ACC = abs(acc)
        self.DEC = -abs(dec)
        self.ANG_ACC = abs(ang_acc)
        self.ANG_DEC = -abs(ang_dec)

        self.TRACK_WIDTH = track_width
    
    def set(self, vel = None, ang_vel = None, 
            acc = None, dec = None, 
            ang_acc = None, ang_dec = None,
            track_width = None):
        
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

    def copy(self):
        return Constrains(self.MAX_VEL, self.MAX_ANG_VEL, 
                          self.ACC, self.DEC, self.ANG_ACC, self.ANG_DEC,
                          self.TRACK_WIDTH)

class VolatileConstrains():
    def __init__(self, start: float, constrains: Constrains):
        self.start = start
        self.constrains = constrains