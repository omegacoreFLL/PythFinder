import math


default_max_robot_vel = 30 # cm/sec
default_max_robot_angular_vel = math.radians(90) #rad/sec

default_max_robot_acc = 10
default_max_robot_dec = -10

default_track_width = 9.97



class Constrains():
    def __init__(self, vel = default_max_robot_vel, ang_vel = default_max_robot_angular_vel,
                 acc = default_max_robot_acc, dec = default_max_robot_dec,
                 track_width = default_track_width):
        self.vel = vel
        self.ang_vel = ang_vel

        self.acc = acc
        self.dec = dec

        self.TRACK_WIDTH = track_width
    
    def set(self, vel = None, ang_vel = None, acc = None, dec = None, track_width = None):
        if not vel == None:
            self.vel = vel
        if not ang_vel == None:
            self.ang_vel = ang_vel
        if not acc == None:
            self.acc = acc
        if not dec == None:
            self.dec = dec
        if not track_width == None:
            self.TRACK_WIDTH = track_width
