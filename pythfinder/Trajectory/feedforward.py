from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Components.Constants.constraints import *

# file containing all the feedforward control calculation.
#
# we use a trapezoidal motion profile (meaning velocity and acceleration constrained). It supports
#   advanced manipulation. Specifying the start velocity enables to connect multiple motion
#   profiles into one smooth profile, thus implementing dynamic constraints. 
#
# in some cases, this much freedom doesn't give the profile acc / dec to complete the distance,
#   so it estimates the distance it can reach with the given constraines, alerting the user of
#   the impossible case.

class MotionProfile():
    def __init__(self, distance: float, constraints: Constraints, start_velocity: float = 0):
        self.constraints = constraints

        if distance < 0:
            self.reversed = True
            self.sign = -1
        else: 
            self.reversed = False
            self.sign = 1

        self.distance = abs(distance)

        self.start_vel = start_velocity
        self.max_vel = constraints.MAX_VEL
        self.acc = constraints.ACC
        self.dec = constraints.DEC

        self.x1 = self.x2 = self.x3 = 0
        self.t1 = self.t2 = self.t3 = 0
        self.x_total = self.t_total = 0

        self.time = 0
        self.recommended_distance = None


        #decelerating from start_vel to 0
        t_dec_to_0 = self.start_vel / -self.dec
        d_dec_to_0 = t_dec_to_0 * self.start_vel / 2.0

        if self.distance - d_dec_to_0 < 0:
            #impossible case
            self.t1 = self.t2 = self.t3 = -1
            self.x1 = self.x2 = self.x3 = 0
            self.t_total = self.x_total = 0

            self.recommended_distance = -d_dec_to_0
            return None
    

        if self.start_vel > self.max_vel:
            self.UP = False
            self.acc = self.dec
        else: self.UP = True


        self.t1 = (self.max_vel - self.start_vel) / self.acc
        self.t3 = self.max_vel / -self.dec

        self.x1 = self.t1 * (self.max_vel + self.start_vel) / 2
        self.x3 = self.t3 * (self.max_vel) / 2

        if self.distance - (self.x1 + self.x3) >= 0:
            # trapezoidal 

            self.x2 = self.distance - (self.x1 + self.x3)
            self.t2 = (self.x2) / self.max_vel

        else:
            #triangular (only on a rising profile, aka start_vel < max_vel)

            self.t2 = self.x2 = 0

            # math 🗿
            self.max_vel = math.sqrt(self.dec * (2 * self.distance * self.acc + (self.start_vel ** 2)) 
                                                        /
                                                (self.dec - self.acc))

            #recalculate t1 and t3
            self.t1 = (self.max_vel - self.start_vel) / self.acc
            self.t3 = self.max_vel / -self.dec

            self.x1 = (self.max_vel * self.t1) / 2
            self.x3 = (self.max_vel * self.t3) / 2


        self.x_total = self.x1 + self.x2 + self.x3 #cm
        self.t_total = self.t1 + self.t2 + self.t3 #s


    
    def get_dis(self, t: float):

        if t <= self.t1:
            return self.sign * (self.acc * (t ** 2) / 2 + t * self.start_vel)
        if t <= self.t1 + self.t2:
            return self.sign * (self.x1 + self.max_vel * (t - self.t1))
            
        return self.sign * (self.x1 + self.x2 + (self.max_vel + self.dec * (t - (self.t1 + self.t2)) / 2) * (t - (self.t1 + self.t2)))

    def get_vel(self, t: float):
        
        if t <= self.t1:
            return self.sign * (self.start_vel + self.acc * t)
        if t <= self.t1 + self.t2:
            return self.sign * (self.max_vel)
            
        return self.sign * (self.max_vel + self.dec * (t - (self.t1 + self.t2)))     
    
    def get_acc(self, t: float):

        if t <= self.t1:
            return self.sign * (self.acc)
        if t <= self.t1 + self.t2:
            return 0

        return self.sign * (self.dec)
    
    def get(self, t: float, n: int):
        match n:
            case 0: return self.get_dis(t)
            case 1: return self.get_vel(t)
            case 2: return self.get_vel(t)
            case _: raise Exception('not a valid differentiation grade')