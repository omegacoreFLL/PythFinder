from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Trajectory.Control.feedforward import *

from typing import List
from abc import ABC

# file containing mathematical interpretation of polynomial splines

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
        self.integral = [0]  # Start with 0 for the first step
        self.integrand = zeros_like(self.u)

        for i in range(1, len(self.u)):
            self.integrand[i] = self.get(self.u[i], 1).hypot()

            # Simpson's rule requires at least two points for a segment
            if i % 2 == 0 and i >= 2:
                simpson_integral = (self.integrand[i-2] + 4 * self.integrand[i-1] + self.integrand[i]) * (self.delta_u / 3)
                last_sum += simpson_integral

            self.integral.append(last_sum)

        # Adjust final integration sum if the number of steps is odd
        if steps % 2 == 0:
            self.integral[-1] = last_sum + 0.5 * self.delta_u * (self.integrand[-2] + self.integrand[-1])
  
    @staticmethod
    def simpsons_rule(y_values: List[float], h: float) -> float:
        n = len(y_values) - 1
        if n % 2 == 1:
            n -= 1  # make n even
        
        result = y_values[0] + y_values[n]
        for i in range(1, n, 2):
            result += 4 * y_values[i]
        for i in range(2, n-1, 2):
            result += 2 * y_values[i]
        
        return (h / 3) * result
    
    def addProfile(self, profile: MotionProfile):
        self.profile = profile

class SplineTarget():
    def __init__(self, derivatives: List[Point]) -> None:
        self.deriv = derivatives
    
    def get(self, n: int) -> Point:
        try: return self.deriv[n]
        except: raise Exception("You don't have an {0} order derivative".format(n))