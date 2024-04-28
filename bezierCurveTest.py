from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from typing import List
from enum import Enum
import numpy as np
import math
import time

class CurveType(Enum):
    QUADRATIC_BEZIER = auto()
    QUBIC_BEZIER = auto()





def normalizeRGB(rgb):
    r, g, b = rgb
    return (r / 255, g / 255, b / 255)

class BezierCurve():
    def __init__(self, points: List[Point] = [], goThrough: bool = False):
        match len(points):
            case 0, 1, 2:
                raise Exception('what?')
            case 3:
                self.curve = self.QuadraticBezier(points, goThrough)
                self.type = CurveType.QUADRATIC_BEZIER
            case 4:
                self.curve = self.QubicBezier(points, goThrough)
                self.type = CurveType.QUBIC_BEZIER
            case _:
                raise Exception("you've entered the dark side...")
        
        self.displayPointList = self.curve.displayPointList
        self.goThroughPoints = self.curve.goThroughPoints
        self.integral = 0
        self.angles = []
    
    def calculate(self, t: float) -> Point:
        return self.curve.calculate(t)

    def derivative(self, t: float) -> Point:
        return self.curve.derivative(t)
    
    def generate(self, samples: int) -> List[Point]:
        step = 1 / samples
        points = []
        derivative = []
        t = 0

        while t <= 1:
            points.append(self.calculate(t))
            derivative.append(self.derivative(t))

            if len(points) > 1:
                self.integral += points[len(points) - 1].subtract(points[len(points) - 2]).div(step).hypot()
                self.angles.append(Point(t, toDegrees(points[len(points) - 1].subtract(points[len(points) - 2]).atan2())))

            t += step
        
        return points, derivative
    
    
    class QuadraticBezier():
        def __init__(self, points: List[Point], goThrough: bool):
            self.goThrough = goThrough

            self.goThroughPoints = []
            self.displayPointList = points

            if goThrough:
                self.goThroughPoints.append(self.displayPointList[1])
                self.displayPointList[1] = points[1].product(2).subtract(points[0].sum(points[2]).div(2))

            self.a, self.b, self.c = (
                points[0].product(1).sum(points[1].product(-2))
                                     .sum(points[2]),
                
                points[0].product(-2).sum(points[1].product(2)),

                points[0]
            )

        

        def calculate(self, t: float) -> Point:
            return (self.c.sum(self.b.product(t))
                          .sum(self.a.product(t*t))
            )

        def derivative(self, t: float) -> Point:
            return (self.b.sum(self.a.product(2*t)))

    class QubicBezier():
        def __init__(self, points: List[Point], goThrough: bool):
            self.goThrough = goThrough

            self.goThroughPoints = []
            self.displayPointList = points

            if goThrough:
                pass
                '''self.goThroughPoints.append(self.displayPointList[1])
                self.goThroughPoints.append(self.displayPointList[2])

                q1 = self.displayPointList[0].sum(self.displayPointList[0].subtract(self.displayPointList[1]).div(3))
                q2 = self.displayPointList[3].subtract(self.displayPointList[3].subtract(self.displayPointList[2]).div(3))


                self.displayPointList[1] = points[1] = q1
                self.displayPointList[2] = points[2] = q2'''

            
            self.a, self.b, self.c, self.d = (
                points[0].product(-1).sum(points[1].product(3))
                                     .sum(points[2].product(-3))
                                     .sum(points[3]),
                
                points[0].product(3).sum(points[1].product(-6))
                                    .sum(points[2].product(3)),
                
                points[0].product(-3).sum(points[1].product(3)),

                points[0]
            )
            
        
        def calculate(self, t: float) -> Point:
            return (self.d.sum(self.c.product(t))
                          .sum(self.b.product(t*t))
                          .sum(self.a.product(t*t*t))
            )

        def derivative(self, t: float) -> Point:
            return (self.c.sum(self.b.product(2*t))
                          .sum(self.a.product(3*t*t))
            )

class BezierSpline():
    def __init__(self, type: CurveType, points: List[Point] = [],  goThrough: bool = False):
        self.integral = 0
        self.angles = []

        match type:
            case CurveType.QUADRATIC_BEZIER:
                if not len(points) % 5 == 0 and len(points) == 0 and not len(points) == 3:
                    raise Exception("what?")
            
                point_number = len(points)
                self.curves = []
                self.goThroughPoints = []
                self.displayPointList = []
                index = 0

                while index + 2 < point_number:
                    current_curve_points = [points[index], points[index+1], points[index+2]]
                    self.curves.append(BezierCurve(current_curve_points, goThrough))

                    self.goThroughPoints += self.curves[len(self.curves) - 1].curve.goThroughPoints
                    self.displayPointList += self.curves[len(self.curves) - 1].curve.displayPointList

                    index += 2


            case CurveType.QUBIC_BEZIER:
                if len(points) % 4 == 0 or len(points) == 0:
                    raise Exception("what?")
                
                point_number = len(points)
                self.curves = []
                self.goThroughPoints = []
                self.displayPointList = []
                index = 0

                while index + 3 < point_number:
                    current_curve_points = [points[index], points[index+1], points[index+2], points[index+3]]

                    self.goThroughPoints += self.curves[len(self.curves) - 1].curve.goThroughPoints
                    self.displayPointList += self.curves[len(self.curves) - 1].curve.displayPointList

                    index += 3
    
    def generate(self, samples: int) -> List[Point]:
        point_list = []
        derivative_list = []

        for each in self.curves:
            points, derivative = each.generate(samples)

            point_list += points
            derivative_list += derivative
        
        return point_list, derivative_list
            

        

            

through = True
p0, p1, p2 = Point(0,0), Point(10, 5), Point(5, 20)

p3 = p2.product(2).subtract(p1)
p4 = Point(15, 30)

og_p1 = Point()
og_p3 = Point()

if through:
    og_p1 = p1
    og_p3 = p3
    new_p1 = p1.product(2).subtract(p0.sum(p2).div(2))
    new_p3 = p3.product(2).subtract(p2.sum(p4).div(2))
    p1 = new_p1
    p3 = p2.product(2).subtract(p1)


pointList = ([
    p0, p1, p2, p3, p4
])

#curve = BezierCurve(pointList, goThrough = False)
curve = BezierSpline(CurveType.QUADRATIC_BEZIER, goThrough = False, points = pointList)

points, derivative = curve.generate(1000)
x_points, y_points = pointsToGraph(points)
x_deriv, y_deriv = pointsToGraph(derivative)
x_control, y_control = pointsToGraph(curve.displayPointList + [og_p1, og_p3])



darkerblue = (9, 102, 102)


plt.figure(figsize=(15, 9), facecolor = 'black')
plt.style.use('dark_background')

plt.title('{0}-point Bezier'.format(len(pointList)), fontsize = 22)
plt.xlabel('x(u)', fontsize = 14)
plt.ylabel('y(u)', fontsize = 14)

plt.plot(x_points, y_points, color = 'lightblue', zorder = 1)
plt.plot(x_control, y_control, color = normalizeRGB(darkerblue), dashes = (10, 10))

plt.axhline(0, color = 'white', linewidth = 3)
plt.axvline(0, color = 'white', linewidth = 3)

for point in curve.displayPointList:
    plt.scatter(point.x, point.y, s = 300, c = 'blue', zorder = 2)

for point in curve.goThroughPoints:
    plt.scatter(point.x, point.y, s = 300, c = 'red', zorder = 2)









# Create a figure and axis
'''fig, ax = plt.subplots(figsize=(15, 9), facecolor='black')
ax.set_facecolor('black')
ax.set_title('Object Moving on Quadratic Bezier Curve', fontsize=22)
ax.set_xlabel('x', fontsize=14)
ax.set_ylabel('y', fontsize=14)

# Plot the curve
ax.plot(x_points, y_points, color='lightblue', zorder=1)
ax.plot(x_control, y_control, color=normalizeRGB(darkerblue), dashes=(10, 10))

# Initialize the object
object_marker, = ax.plot([], [], 'ro', markersize=10)  # red circle for the object

# Function to update the object position
def update(frame):
    object_marker.set_data([x_points[frame]], [y_points[frame]])
    return object_marker,

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=len(x_points), blit=True, interval=0.00001)
plt.subplot(1, 2, 2)






fig, ax = plt.subplots(figsize=(15, 9), facecolor='black')
t_values, angles = pointToGraph(curve.angles)

ax.plot(t_values, angles, label='Tangent Angle (degrees)')
ax.set_title('Tangent Angles')
ax.set_xlabel('t')
ax.set_ylabel('Angle (degrees)')
ax.grid(True)
ax.set_ylim(-180, 180)  # Set y-axis limits to -180 to 180 degrees
ax.legend()'''




















'''plt.figure(figsize=(15, 9), facecolor = 'black')
plt.style.use('dark_background')

plt.title('derivative', fontsize = 22)
plt.xlabel('x(u)', fontsize = 14)
plt.ylabel('y(u)', fontsize = 14)

plt.scatter(x_deriv, y_deriv, color = 'lightblue', zorder = 1, s = 10)

plt.axhline(0, color = 'white', linewidth = 3)
plt.axvline(0, color = 'white', linewidth = 3)




x_min = min(min(x_points), min(x_control)) - 10
x_max = max(max(x_points), max(x_control)) + 10
y_min = min(min(y_points), min(y_control)) - 10
y_max = max(max(y_points), max(y_control)) + 10

plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)

x_ticks = np.arange(x_min, x_max + 1, 5)
y_ticks = np.arange(y_min, y_max + 1, 5)

print(curve.integral)






plt.xticks(x_ticks)
plt.yticks(y_ticks)'''

plt.axis('equal')
plt.grid(True, color = normalizeRGB(default_grid_color))
plt.tight_layout()
plt.show()


