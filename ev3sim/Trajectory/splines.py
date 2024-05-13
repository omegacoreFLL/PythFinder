
from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Trajectory.feedforward import *

from typing import List


# file containing mathematical interpretation of polynomial splines
#
# not used at the moment 
#   TODO: get splines working


class QubicPolynomial():
    def __init__(self, n0: float, n1: float, 
                       dn0: float, dn1: float):
        
        self.a =2 * n0 + dn0 - 2 * n1 + dn1
        self.b = -3 * n0 - 2 * dn0 + 3 * n1 - dn1
        self.c = dn0
        self.d = n0

        self.control_cords = [n0, n1, dn0, dn1]
    
    def get(self, u: float, n: int) -> float:
        match n:
            case 0:
                return (self.a * u ** 3 +
                        self.b * u ** 2 +
                        self.c * u +
                        self.d)
            case 1:
                return (self.a * 3 * u ** 2 +
                        self.b * 2 * u +
                        self.c)
            case 2:
                return (self.a * 6 * u +
                        self.b * 2)
            case _:
                raise Exception("can't do that here")

class QubicSpline():
    def __init__(self, start: Point, end: Point, startVel: Point, endVel: Point ):

        self.x = QubicPolynomial(start.x, end.x, startVel.x, endVel.x)
        self.y = QubicPolynomial(start.y, end.y, startVel.y, endVel.y)

        self.start = start
        self.end = end
        self.start_deriv = startVel
        self.end_deriv = endVel

        self.t = []
        self.u = []
        self.integral = []
        self.integrand = []

        self.delta_u = 0
        self.steps = 0
        self.last_x = self.last_y = 0
        self.calculate_integral(steps = 1000)

        self.profile = MotionProfile(start = 0, 
                                    end = self.integral[len(self.integral) - 1],
                                    constrains = Constrains())
        self.spline_time = int(sToMs(self.profile.t_total)) + 1
    


    def get(self, u: float, n: int) -> Point: # Point( x(u), y(u) )
        return Point(self.x.get(u, n),
                     self.y.get(u, n))

    def get_ang(self, t: float, n: int) -> float:
        match n:
            case 0:
                return normalizeRadians(self.get_from_profile(t, 1).atan2())
            case 1:
                return normalizeRadians(self.get_from_profile(t, 2).atan2())

    
    def get_curv(self, t: float):
        dx, dy = self.get_from_profile(t, 1).tuple()
        ddx, ddy = self.get_from_profile(t, 2).tuple()

        return (ddy * dx - ddx * dy) / (((dx ** 2 + dy ** 2)**(3 / 2)))
            
    
    def addProfile(self, profile: MotionProfile):
        self.profile = profile

    def calculate_integral(self, steps: int): #WORKS
        self.steps = steps
        self.u = linspace(0, 1, steps)
        self.delta_u = self.u[1] - self.u[0]

        last_sum = 0
        self.integrand = zeros_like(self.u)

        for i in range(len(self.u)):
            self.integrand[i] = self.get(self.u[i], 1).hypot()
            self.integral.append(last_sum + self.delta_u * self.integrand[i])

            last_sum = self.integral[i]

    

    def reparameterize(self, s: float, n: int): # u(s)
        index, _ = binary_search(s, self.integral)

        match n:
            case 0:
                return self.u[index]
            case 1:
                return 1.0 / self.integrand[int(self.u[index] / self.delta_u)]
            case 2:
                    dxdu, dydu = self.get(self.u[index], 1).tuple()
                    dxdudu, dydudu = self.get(self.u[index], 2).tuple()

                    return -0.5 * (dxdudu * dxdu + dydudu * dydu) / (hypot(dxdu, dydu)**3)
            case _:
                raise Exception('take a break my guy')
    
    #Point( x(u(s)), y(u(s)) )
    def get_from_profile(self, t: float, n: int) -> Point:
        t = msToS(t)
        s = self.profile.get(t, 0)
        u = self.reparameterize(s, 0)

        match n:
            case 0:
                return self.get(u, 0)
            case 1:
                dsdt = self.profile.get(t, 1)
                duds = self.reparameterize(s, 1)
                dxdu, dydu = self.get(u, 1).tuple()
                
                return Point(dxdu * duds * dsdt,
                             dydu * duds * dsdt)
            case 2:
                ds = self.profile.get(t, 1)
                dds = self.profile.get(t, 2)

                du = self.reparameterize(s, 1)
                ddu = self.reparameterize(s, 2)

                dx, dy = self.get(u, 1).tuple()
                ddx, ddy = self.get(u, 2).tuple()


                return Point(ddx * (du ** 2) * (ds ** 2) +
                                    dx * ddu * (ds ** 2) +
                                    dx * du * dds,
                            ddy * (du ** 2) * (ds ** 2) +
                                    dy * ddu * (ds ** 2) +
                                    dy * du * dds)
            case _:
                raise Exception('not a valid differentiation grade')
    
    def generate(self, n: float) -> List[Point]:
        self.spline_time = int(sToMs(self.profile.t_total)) + 1
        self.t = linspace(0, self.spline_time, self.spline_time)

        points = []

        for t in range(self.spline_time):
            points.append(self.get_from_profile(t, n))
    
        return points
    
    def generate_ang(self, n: float) -> List[float]:
        self.spline_time = int(sToMs(self.profile.t_total)) + 1
        self.t = linspace(0, self.spline_time, self.spline_time)

        theta = []
        last = None

        for t in range(self.spline_time):
            theta.append(self.get_ang(t, n))
    
        return theta

    