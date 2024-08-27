
from pythfinder.Trajectory.Segments.Splines.polynomials import *
from pythfinder.Trajectory.Segments.Splines.generic import *

class QubicSpline(Spline):
    def __init__(self, 
                 start: SplineTarget, end: SplineTarget, 
                 constraints: Constraints = Constraints()):

        self.x = QubicPolynomial(start.get(0).x, end.get(0).x, start.get(1).x, end.get(1).x)
        self.y = QubicPolynomial(start.get(0).y, end.get(0).y, start.get(1).y, end.get(1).y)

        self.dsdt = []

        self.start = start
        self.end = end

        self.u = []
        self.integral = []
        self.integrand = []

        self.delta_u = 0
        self.steps = 0
        self.last_x = self.last_y = 0
        self.calculate_integral(steps = 10000)

        self.profile = MotionProfile(distance = self.integral[-1],
                                     constraints = constraints)
        self.spline_time = int(sec_to_ms(self.profile.t_total)) + 1
    


    def get(self, u: float, n: int) -> Point: # Point( x(u), y(u) )
        return Point(self.x.get(u, n),
                     self.y.get(u, n))

    def get_ang(self, t: float, n: int) -> float:
        match n:
            case 0:
                return normalize_radians(self.get_from_profile(t, 1).atan2())
            case 1:
                curvature = self.get_curv(t)
                velocity = self.get_from_profile(t, 1).hypot()

                return curvature * velocity
            
            case _:
                return 0
    
    def get_curv(self, t: float):
        dx, dy = self.get_from_profile(t, 1).tuple()
        ddx, ddy = self.get_from_profile(t, 2).tuple()

        return ((ddy * dx - ddx * dy) / (((dx ** 2 + dy ** 2)**(3 / 2))) 
                    if not (((dx ** 2 + dy ** 2)**(3 / 2))) == 0 else
                0)

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
                return 1.0 / self.get(self.u[index], 1).hypot() if not self.get(self.u[index], 1).hypot() == 0 else 0
            case 2:
                    dxdu, dydu = self.get(self.u[index], 1).tuple()
                    dxdudu, dydudu = self.get(self.u[index], 2).tuple()

                    return -0.5 * (dxdudu * dxdu + dydudu * dydu) / (math.hypot(dxdu, dydu)**3)
            case _:
                raise Exception('take a break my guy')
    


    #Point( x(u(s(t))), y(u(s(t))) )
    def get_from_profile(self, t: float, n: int) -> Point:
        t = ms_to_sec(t)
        s = self.profile.get(t, 0)
        u = self.reparameterize(s, 0)

        match n:
            case 0:
                return self.get(u, 0)
            case 1:
                dsdt = self.profile.get(t, 1)
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
        self.spline_time = int(sec_to_ms(self.profile.t_total)) + 1
        points = []

        for t in range(self.spline_time):
            points.append(self.get_from_profile(t, n))

        return points
    
    def generate_ang(self, n: float) -> List[float]:
        self.spline_time = int(sec_to_ms(self.profile.t_total)) + 1
        theta = []

        for t in range(self.spline_time):
            theta.append(self.get_ang(t, n))
    
        return theta
