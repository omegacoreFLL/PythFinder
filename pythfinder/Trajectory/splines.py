
from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Trajectory.Control.feedforward import *

from typing import List
from abc import ABC

# file containing mathematical interpretation of polynomial splines
#
# not used at the moment 
#   TODO: get splines working

class Spline(ABC):
    def get(self, u: float, n: int) -> Point:
        pass

    def get_ang(self, t: float, n: int) -> float:
        pass

    def get_curv(self, t: float, n: int) -> float:
        pass

    def generate(self, n: float) -> List[Point]:
        pass

    def generate_ang(self, n: float) -> List[float]:
        pass

    def calculate_integral(self, steps: int): #WORKS
        self.steps = steps
        self.u = linspace(0, 1, steps)
        self.delta_u = self.u[1] - self.u[0]

        last_sum = 0
        self.integral = []
        self.integrand = zeros_like(self.u)

        for i in range(len(self.u)):
            self.integrand[i] = self.get(self.u[i], 1).hypot()
            self.integral.append(last_sum + self.delta_u * self.integrand[i])

            last_sum = self.integral[i]
    
    def addProfile(self, profile: MotionProfile):
        self.profile = profile



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

    def getCoeff(self):
        return self.a, self.b, self.c, self.d

class QuinticPolynomial():
    def __init__(self, n0: float, n1: float, n2: float,
                       dn0: float, dn1: float, dn2: float) -> None:
        self.a = (-6.0 * n0 - 3.0 * n1 - 0.5 * n2 +
                   6.0 * dn0 - 3.0 * dn1 + 0.5 * dn2)
        self.b = (15.0 * n0 + 8.0 * n1 + 1.5 * n2 -
                  15.0 * dn0 + 7.0 * dn1 - dn2)
        self.c = (-10.0 * n0 - 6.0 * n1 - 1.5 * n2 +
                   10.0 * dn0 - 4.0 * dn1 + 0.5 * dn2)
        self.d = 0.5 * n2
        self.e = n1
        self.f = n0

    def get(self, t: float, n: int):
        match n:
            case 0:
                return ((((self.a * t + self.b) * t + self.c) * t + self.d) * t + self.e) * t + self.f
            case 1:
                return (((5.0 * self.a * t + 4.0 * self.b) * t + 3.0 * self.c) * t + 2.0 * self.d) * t + self.e
            case 2:
                return ((20.0 * self.a * t + 12.0 * self.b) * t + 6.0 * self.c) * t + 2.0 * self.d
            case 3:
                return (60.0 * self.a * t + 24.0 * self.b) * t + 6.0 * self.c
            case 4:
                return 120.0 * self.a * t + 24.0 * self.b
            case 5:
                return 120.0 * self.a
            case _:
                return 0.0


    

class QubicSpline(Spline):
    def __init__(self, start: Point, end: Point, startVel: Point, endVel: Point, 
                 constraints: Constraints = Constraints()):

        self.x = QubicPolynomial(start.x, end.x, startVel.x, endVel.x)
        self.y = QubicPolynomial(start.y, end.y, startVel.y, endVel.y)

        self.dsdt = []

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

        self.profile = MotionProfile(distance = self.integral[-1],
                                     constraints = constraints)
        self.spline_time = int(sToMs(self.profile.t_total)) + 1
    


    def get(self, u: float, n: int) -> Point: # Point( x(u), y(u) )
        return Point(self.x.get(u, n),
                     self.y.get(u, n))

    def get_ang(self, t: float, n: int) -> float:
        match n:
            case 0:
                return normalizeRadians(self.get_from_profile(t, 1).atan2())
            case 1:
                radius = self.get_radius(t)
                velocity = self.get_from_profile(t, 1).hypot()

                return radius * velocity
    
    def get_curv(self, t: float):
        dx, dy = self.get_from_profile(t, 1).tuple()
        ddx, ddy = self.get_from_profile(t, 2).tuple()

        return (ddy * dx - ddx * dy) / (((dx ** 2 + dy ** 2)**(3 / 2)))
    
    def get_radius(self, t: float):
        dx, dy = self.get_from_profile(t, 1).tuple()
        ddx, ddy = self.get_from_profile(t, 2).tuple()

        try: return (((dx ** 2 + dy ** 2)**(3 / 2))) / (ddy * dx - ddx * dy)
        except: return 0
            
    
    def reparameterize(self, s: float, n: int): # u(s)
        index, _ = binary_search(s, self.integral)

        match n:
            case 0:
                return self.u[index]
            case 1:
                return 1.0 / self.get(self.u[index], 1).hypot()
            case 2:
                    dxdu, dydu = self.get(self.u[index], 1).tuple()
                    dxdudu, dydudu = self.get(self.u[index], 2).tuple()

                    return -0.5 * (dxdudu * dxdu + dydudu * dydu) / (hypot(dxdu, dydu)**3)
            case _:
                raise Exception('take a break my guy')
    
    #Point( x(u(s(t))), y(u(s(t))) )
    def get_from_profile(self, t: float, n: int) -> Point:
        t = msToS(t)
        s = self.profile.get(t, 0)
        u = self.reparameterize(s, 0)

        match n:
            case 0:
                return self.get(u, 0)
            case 1:
                with open("spline_custom.txt", "a") as f:
                    dsdt = self.profile.get(t, 1)
                    f.write(str(dsdt) + "\n")
                duds = self.reparameterize(s, 1)
                dxdu, dydu = self.get(u, 1).tuple()


                self.dsdt.append(dsdt)
                
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
        self.t = linspace(0, self.spline_time, self.steps)

        points = []
        #print(len(self.t))

        for t in self.t:
            points.append(self.get_from_profile(t, n))

        return points
    
    def generate_ang(self, n: float) -> List[float]:
        self.spline_time = int(sToMs(self.profile.t_total)) + 1
        self.t = linspace(0, self.spline_time, self.steps)

        theta = []

        for t in self.t:
            theta.append(self.get_ang(t, n))
    
        return theta



class QuinticSpline():
    def __init__(self, start: Point, end: Point, 
                       startVel: Point, endVel: Point, 
                       startAcc: Point, endAcc: Point) -> None:
        
        self.x = QuinticPolynomial(start.x, startVel.x, startAcc.x,
                                   end.x, endVel.x, endAcc.x)
        self.y = QuinticPolynomial(start.y, startVel.y, startAcc.y,
                                   end.y, endVel.y, endAcc.y)
        
    def get(self, t: float, n: int):
        pass