from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Trajectory.constraints import *

# file containing all the feedforward control calculation.
#
# we use a trapezoidal motion profile (meaning velocity and acceleration constrained). It supports
#   advanced manipulation. Specifying the start velocity enables to connect multiple motion
#   profiles into one smooth profile, thus implementing dynamic constraints. 
#
# in some cases, this much freedom doesn't give the profile acc / dec to complete the distance,
#   so it estimates the distance it can reach with the given constraines, alerting the user of
#   the impossible case.

class ProfileState():
    def __init__(self, dis: float, vel: float, acc: float) -> None:
        self.dis = dis
        self.vel = vel
        self.acc = acc
    
    def tuple(self):
        return (self.dis, self.vel, self.acc)

class MotionProfile():
    def __init__(self, distance: float, constraints: Constraints, 
                 start_velocity: float = 0, end_velocity: float = 0,
                 start_time_ms: int = 0, start_distance: float = 0):
        self.constraints = constraints

        if distance < 0:
            self.reversed = True
            self.sign = -1
        else: 
            self.reversed = False
            self.sign = 1

        self.distance = abs(distance)

        self.start_vel = start_velocity
        self.end_vel = end_velocity
        
        self.start_x = start_distance
        self.start_t_ms = abs(start_time_ms)

        self.max_vel = constraints.MAX_VEL

        self.acc = constraints.ACC if self.start_vel < self.max_vel else -constraints.DEC
        self.dec = constraints.DEC if self.end_vel < self.max_vel else -constraints.ACC

        self.x1 = self.x2 = self.x3 = 0
        self.t1 = self.t2 = self.t3 = 0
        self.x_total = self.t_total = 0

        self.time = 0
        self.recommended_distance = None

        self.NOT_DEFINED = False

        if self.max_vel == 0 or self.acc == 0 or self.dec == 0:
            #no profile exists
            self.NOT_DEFINED = True
            return None



        self.t1 = abs(self.max_vel - self.start_vel) / self.acc
        self.t3 = abs(self.max_vel - self.end_vel) / (-self.dec)

        self.x1 = (abs(self.max_vel - self.start_vel) * self.t1 * 0.5 + # the triangle part
                   min(self.max_vel, self.start_vel) * self.t1          # the rectangle part
        )
        self.x3 = (abs(self.max_vel - self.end_vel) * self.t3 * 0.5 + # same stuff here
                   min(self.max_vel, self.end_vel) * self.t3
        )


        if self.x1 + self.x3 <= self.distance:
            # trapezoidal

            self.x2 = self.distance - (self.x1 + self.x3)
            self.t2 = self.x2 / self.max_vel

        else:
            # triangular

            self.x2 = 0
            self.t2 = 0

            # math 🗿
            self.max_vel = math.sqrt((2 * self.distance * self.acc * self.dec +
                                      self.dec * math.pow(self.start_vel, 2)  -
                                      self.acc * math.pow(self.end_vel, 2))
                                                    /
                                            (self.dec - self.acc))
                     
            # recalculate stuff
            self.t1 = abs(self.max_vel - self.start_vel) / self.acc
            self.t3 = abs(self.max_vel - self.end_vel) / (-self.dec)

            self.x1 = (abs(self.max_vel - self.start_vel) * self.t1 * 0.5 + 
                       min(self.max_vel, self.start_vel) * self.t1          
            )
            self.x3 = (abs(self.max_vel - self.end_vel) * self.t3 * 0.5 +
                       min(self.max_vel, self.end_vel) * self.t3
            )

        self.x_total = self.x1 + self.x2 + self.x3 # cm
        self.t_total = self.t1 + self.t2 + self.t3 # s

        if not round(self.x_total, 2) == round(self.distance, 2):
            print("\n\nwith these constraints, you get a distance with {0} cm off than you wanted"
                  .format(self.distance - self.x_total))
            print("'PROFILE NOT DEFINED' error")
            self.NOT_DEFINED = True

        # this time account for the sign
        self.acc = constraints.ACC if self.start_vel < self.max_vel else constraints.DEC
        self.dec = constraints.DEC if self.end_vel < self.max_vel else constraints.ACC


    
    def get_dis(self, t: float):

        if t <= self.t1:
            return self.start_x + self.sign * (self.acc * (t ** 2) / 2 + t * self.start_vel)
        if t <= self.t1 + self.t2:
            return self.start_x + self.sign * (self.x1 + self.max_vel * (t - self.t1))
        if t <= self.t_total:
            return self.start_x + self.sign * (self.x1 + self.x2 + (self.max_vel + self.dec * (t - (self.t1 + self.t2)) / 2) * (t - (self.t1 + self.t2)))
        
        return self.start_x + self.distance

    def get_vel(self, t: float):
        
        if t <= self.t1:
            return self.sign * (self.start_vel + self.acc * t)
        if t <= self.t1 + self.t2:
            return self.sign * (self.max_vel)
        if t <= self.t_total:
            return self.sign * (self.max_vel + self.dec * (t - (self.t1 + self.t2)))  
        
        return 0   
    
    def get_acc(self, t: float):
        
        if t <= self.t1:
            return self.sign * (self.acc)
        if t <= self.t1 + self.t2:
            return 0
        if t <= self.t_total:
            return self.sign * (self.dec)
        
        return 0



    def get(self, t: float, n: int):
        match n:
            case 0: return round(self.get_dis(t), 15)
            case 1: return round(self.get_vel(t), 15)
            case 2: return round(self.get_vel(t), 15)
            case _: raise Exception('not a valid differentiation grade')

    def getStateS(self, t: float) -> ProfileState:
        '''with open ("muie.txt", "a") as f:
            f.write(str(t) + " " + str(self.start_t_ms) + " " 
                    + str(round(self.get_dis(t), 2)) + 
                    " " + str(self.start_x) + "\n")'''
    
        return ProfileState(self.get_dis(t),
                            self.get_vel(t),
                            self.get_acc(t))

    def getStateMs(self, t: float) -> ProfileState:
        return self.getStateS(msToS(t - self.start_t_ms))



    def FINISHED(self, t: float) -> bool:
        return t > self.t_total or self.NOT_DEFINED

    def FINISHED_ms(self, t: float) -> bool:
        return self.FINISHED(msToS(t - self.start_t_ms))
    


    def copy(self, 
             distance: float = None, constraints: Constraints = None,
             start_velocity: float = None, end_velocity: float = None,
             start_time_ms: int = None, start_distance: float = None):
        
        return MotionProfile(
            distance = self.distance if distance is None else distance,
            constraints = self.constraints if constraints is None else constraints,
            start_velocity = self.start_vel if start_velocity is None else start_velocity,
            end_velocity = self.end_vel if end_velocity is None else end_velocity,
            start_time_ms = self.start_t_ms if start_time_ms is None else start_time_ms,
            start_distance = self.start_x if start_distance is None else start_distance
        )