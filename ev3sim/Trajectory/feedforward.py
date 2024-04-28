from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constrains import *

class MotionProfile():
    def __init__(self, start: float, end: float, constrains: Constrains):
        self.constrains = constrains
        self.start_time = 0

        if end - start < 0:
            self.reversed = True
            self.sign = -1
        else: 
            self.reversed = False
            self.sign = 1

        self.distance = abs(end - start)

        self.max_vel = constrains.MAX_VEL
        self.acc = constrains.ACC
        self.dec = constrains.DEC

        self.x1 = self.x2 = self.x3 = 0
        self.t1 = self.t2 = self.t3 = 0
        self.x_total = self.t_total = 0

        self.dt = 0
        self.time = 0
        self.last_time = 0

        self.isFirst = True
        self.first_time = 0

        self.motion_state = None
        
        self.t1 = self.max_vel / self.acc
        self.t3 = self.max_vel / -self.dec


        if self.max_vel * (self.t1 + self.t3) <= self.distance * 2:
            # trapezoidal  
            self.t2 = self.distance / self.max_vel - (self.t1 + self.t3) / 2
        else:
            # triangular
           
            self.t2 = 0

            a = (self.acc / 2) * (1 + self.acc / -self.dec)
            b = 0
            c = -self.distance

            delta = math.sqrt(- 4 * a * c)

            self.t1 = delta / (2 * a)
            self.max_vel = self.acc * self.t1 
            self.t3 = self.max_vel / -self.dec



        self.x1 = (self.max_vel * self.t1) / 2
        self.x2 = self.max_vel * self.t2
        self.x3 = (self.max_vel * self.t3) / 2

        self.x_total = self.x1 + self.x2 + self.x3 #cm
        self.t_total = self.t1 + self.t2 + self.t3 #s

    
    def get_dis(self, t: float):
        if t <= self.t1:
            return self.sign * (self.acc * (t ** 2) / 2)
        if t <= self.t1 + self.t2:
            return self.sign * (self.x1 + self.max_vel * (t - self.t1))
        
        return self.sign * (self.x1 + self.x2 + (self.max_vel + self.dec * (t - (self.t1 + self.t2)) / 2) * (t - (self.t1 + self.t2)))

    def get_vel(self, t: float):

        if t <= self.t1:
            return self.sign * (self.acc * t)
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