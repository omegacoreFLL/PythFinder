from abc import ABC, abstractmethod
from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *


class MotionProfile(ABC):
    def __init__(self, distance, max_vel, acc, dec = None, telemetry = False):
        self.telemetry = telemetry

        if acc < 0 and telemetry:
            print("acceleration needs to be positive")
        
        if not dec == None:
            if dec > 0 and telemetry:
                print("deceleration need to be negative")
        
        if distance < 0:
            self.reversed = True
        else: self.reversed = False

        self.distance = abs(distance)

        self.max_vel = abs(max_vel)
        self.acc = abs(acc)

        if dec == None:
            self.dec = -acc
        else: self.dec = -abs(dec)

        self.x1 = self.x2 = self.x3 = 0
        self.t1 = self.t2 = self.t3 = 0
        self.x_total = self.t_total = 0

        self.dt = 0
        self.time = 0
        self.last_time = 0

        self.isBusy = True
        self.isFirst = True
        self.first_time = 0

        self.motion_state = None
        self.initial()


    
    @abstractmethod
    def initial(self):
        pass

    def reset(self):
        self.isBusy = True
        self.isFirst = True
        self.first_time = 0

        self.x1 = self.x2 = self.x3 = 0
        self.x_total = 0
    
    @abstractmethod
    def calculate(self, time):
        pass


class TrapezoidalProfile(MotionProfile):

    def initial(self):
        self.t1 = self.max_vel / self.acc
        self.t3 = self.max_vel / -self.dec


        if self.max_vel * (self.t1 + self.t3) <= self.distance * 2:
            if self.telemetry:
                print("trapezoidal")
                
            self.t2 = self.distance / self.max_vel - (self.t1 + self.t3) / 2
        else:
            if self.telemetry:
                print("triangular")
           
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


        self.x_total = self.x1 + self.x2 + self.x3
        self.t_total = self.t1 + self.t2 + self.t3
    

    def calculate(self, time):
        if not self.isBusy:
            return (0, 0, 0, 0, 0)
        
        if self.isFirst:
            self.isFirst = 0
            self.first_time = time
        
        time = time - self.first_time
        
        position = velocity = acceleration = stageTime = 0
        time = msToS(time)
        self.time = time
        stage = None


        if time <= self.t1:
            stageTime = time
            acceleration = self.acc
            velocity = acceleration * time
            position = (velocity * stageTime) / 2

            stage = "T1"
        elif time <= self.t1 + self.t2:
            stageTime = time - self.t1
            acceleration = 0
            velocity = self.max_vel
            position = self.x1 + velocity * stageTime

            stage = "T2"
        elif time <= self.t_total:
            stageTime = time - (self.t1 + self.t2)
            acceleration = self.dec
            velocity = self.max_vel + stageTime * acceleration
            position = self.x1 + self.x2 + (self.max_vel + velocity) / 2 * stageTime

            stage = "T3"
        else: self.isBusy = False


        if self.reversed:
            return (round(-position, 2), round(-velocity, 6), round(-acceleration, 2), stage, round(stageTime, 5))
        return (round(position, 2), round(velocity, 6), round(acceleration, 2), stage, round(stageTime, 5))
        
