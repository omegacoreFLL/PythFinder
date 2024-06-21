from typing import List

import pygame
import math
import time

EPSILON = 1e-5

# enhanced math methods
# Point and Pose classes, used for localisation

class DualNumber():
    def __init__(self, values: List[float]) -> None:
        self.values = values
    
    @staticmethod
    def constant(c: float = 0, n: int = 1):
        values = [c]
        for i in range(n):
            values.append(0)
        
        return DualNumber(values)
    
    @staticmethod
    def variable(c: float = 0, n: int = 1):
        values = [c, 1]
        for i in range(n-1):
            values.append(0)
        
        return DualNumber(values)
    
    def size(self) -> int:
        return len(self.values)
    
    def get(self, i: int):
        return self.values[i]
    
    def value(self):
        return self.values[0]
    
    def reciprocal(self):
        size = self.size()
        out = DualNumber([0] * size)

        recip = 1.0 / self.values[0]
        out.values[0] = recip
        if out.size() == 1: return out

        negRecip = -recip
        negRecip2 = recip * negRecip
        deriv = negRecip2 * self.values[1]
        out.values[1] = deriv
        if out.size() == 2: return out

        int1 = 2 * negRecip * deriv
        deriv2 = int1 * self.values[1] + negRecip2 * self.values[2]
        out.values[2] = deriv2
        if out.size() == 3: return out

        int2 = int1 * self.values[2]
        out.values[3] = (int2 + negRecip2 * self.values[3] +
                         int2 - 2 * (deriv * deriv + recip * deriv2) * self.values[1])
        
        if out.size() > 4: print("\n\ncut the check at the 3rd derivative")

        return out

    def sqrt(self):
        size = self.size()
        out = DualNumber([0] * size)

        sqrt = math.sqrt(self.values[0])
        out.values[0] = sqrt

        if out.size() == 1: return out

        recip = 1 / (2 * sqrt)
        deriv = recip * self.values[1]
        out.values[1] = deriv

        if out.size() == 2: return out

        negRecip = -2 * recip
        negRecip2 = recip * negRecip
        int1 = negRecip2 * deriv
        secondDeriv = int1 * self.values[1] + recip * self.values[2]
        out.values[2] = secondDeriv

        if out.size() == 3: return out

        int2 = 2 * int1
        out.values[3] = (recip * self.values[3] + int2 * self.values[2] +
                        (deriv * negRecip * int2 + negRecip2 * secondDeriv) * self.values[1])

        if out.size() > 4: print("\n\ncut the check at the 3rd derivative")

        return out

    def sin(self):
        size = self.size()
        out = DualNumber([0] * size)

        sin = math.sin(self.values[0])
        out.values[0] = sin
        if out.size() == 1: return out

        cos = math.cos(self.values[0])
        deriv = cos * self.values[1]
        out.values[1] = deriv
        if out.size() == 2: return out

        inDeriv2 = self.values[1] * self.values[1]
        out.values[2] = cos * self.values[2] - sin * inDeriv2
        if out.size() == 3: return out

        out.values[3] = (cos * self.values[3] -
                         3 * sin * self.values[1] * self.values[2] -
                         deriv * inDeriv2)

        return out

    def cos(self):
        size = self.size()
        out = DualNumber(size)

        cos = math.cos(self.values[0])
        out.values[0] = cos
        if out.size() == 1: return out

        sin = math.sin(self.values[0])
        negInDeriv = - self.values[1]
        deriv = sin * negInDeriv
        out.values[1] = deriv
        if out.size() == 2: return out

        int = cos * negInDeriv
        out.values[2] = int * self.values[1] - sin * self.values[2]
        if out.size() == 3: return out

        out.values[3] = (deriv * negInDeriv * self.values[1] +
                        3 * int * self.values[2] -
                        sin * self.values[3])

        return out


    
    def __add__(self, other):
        size = min(self.size(), other.size())
        out = DualNumber([0] * size)

        if isinstance(other, DualNumber):
            for i in range(size):
                out.values[i] = self.values[i] + other.values[i]
        
        else:
            for i in range(size):
                out.values[i] = self.values[i] + other
        
        return out
    
    def __sub__(self, other):
        size = min(self.size(), other.size())
        out = DualNumber([0] * size)

        if isinstance(other, DualNumber):
            for i in range(size):
                out.values[i] = self.values[i] - other.values[i]
        
        else:
            for i in range(size):
                out.values[i] = self.values[i] - other

        return out
    
    def __mul__(self, other):
        size = min(self.size(), other.size())
        out = DualNumber([0] * size)

        if isinstance(other, DualNumber):
            out.values[0] = self.values[0] * other.values[0]
            if out.size() == 1: return out

            out.values[1] = (self.values[0] * other.values[1] + 
                            self.values[1] * other.values[0])
            if out.size() == 2: return out

            out.values[2] = (self.values[0] * other.values[2] + 
                            self.values[2] * other.values[0] + 2 * 
                            self.values[1] * other.values[1])
            if out.size() == 3: return out

            out.values[3] = (self.values[0] * other.values[3] + 
                            self.values[3] * other.values[0] +
                            3 * (self.values[2] * other.values[1] + 
                                self.values[1] * other.values[2]))
            
            if out.size() > 4: print("\n\ncut the check at the 3rd derivative")
        
        else: 
            for i in range(size):
                out.values[i] = self.values[i] * other

        return out

    def __div__(self, other):
        if isinstance(other, DualNumber):
            return self * other.reciprocal()
        else: return self * (1 / other)

    def __neg__(self):
        size = self.size()
        out = DualNumber([0] * size)

        for i in range(size):
            out.values[i] = - self.values[i]
        
        return out



class Point():
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y  
    
    def set(self, x, y):
        self.x = x 
        self.y = y 
    
    def rotateMatrix(self, angle):
        copy = self.x
        self.x = self.x * math.cos(angle) - self.y * math.sin(angle)
        self.y = copy * math.sin(angle) - self.y * math.cos(angle)

        return self
    
    def distanceTo(self, other):
        return hypot(other.x - self.x, other.y - self.y)
    
    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        return Point(self.x - other, self.y - other)
    
    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return Point(self.x + other, self.y + other)
    
    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        return Point(self.x * other, self.y * other)
    
    def __truediv__(self, other):
        if isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)
        return Point(self.x / other, self.y / other)
    
    def hypot(self):
        return hypot(self.x, self.y)

    def tuple(self):
        return (self.x, self.y)
    
    def atan2(self):
        return math.atan2(self.y, self.x)
    
    def reverse_atan2(self):
        return math.atan2(self.x, self.y)
    
    def round(self, n):
        self.x = round(self.x, n)
        self.y = round(self.y, n)

        return self

    def reverse(self):
        copy = self.x
        self.x = self.y
        self.y = copy

        return self
    
    def copy(self):
        return Point(self.x, self.y)
    
    def negate(self):
        self.x = -self.x
        self.y = -self.y

        return self

class PointDual():
    def __init__(self, x: DualNumber = DualNumber.constant(), 
                       y: DualNumber = DualNumber.constant()) -> None:
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return PointDual(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return PointDual(self.x - other.x, self.y - other.y)
    
    def __neg__(self):
        return PointDual(-self.x, -self.y)
    
    def __mul__(self, other):
        return PointDual(self.x * other.x, self.y * other.y)
    
    def __div__(self, other):
        return PointDual(self.x / other.x, self.y / other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def sqrNorm(self):
        return self.dot(self)
    
    def normalize(self):
        return self.sqrNorm().sqrt()


class Pose(Point):
    def __init__(self, x = 0, y = 0, head = 0):
        super().__init__(x, y)
        self.head = head 

    def set(self, x, y, head):
        super().set(x, y)
        self.head = head 
    
    def rad(self):
        return toRadians(self.head)

    def __sub__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x - other.x, self.y - other.y, normalizeDegrees(self.head - other.head))
        return Pose(self.x - other, self.y - other, normalizeDegrees(self.head - other))
    
    def __add__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x + other.x, self.y + other.y, normalizeDegrees(self.head + other.head))
        return Pose(self.x + other, self.y + other, normalizeDegrees(self.head + other))
    
    def __mul__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x * other.x, self.y * other.y, normalizeDegrees(self.head * other.head))
        return Pose(self.x * other, self.y * other, normalizeDegrees(self.head * other))
    
    def __truediv__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x / other.x, self.y / other.y, normalizeDegrees(self.head / other.head))
        return Pose(self.x / other, self.y / other, normalizeDegrees(self.head / other))
    
    
    def copy(self):
        return Pose(self.x, self.y, self.head)
    
    def print(self):
        print("x:{0} y:{1} head:{2}".format(self.x, self.y, self.head))

    def point(self):
        return Point(self.x, self.y)
    
    def rotateMatrix(self, angle):
        point = super().rotateMatrix(angle)
        return Pose(point.x, point.y, self.head)



    
        





def rotateMatrix(x, y, angle):
    rotated_x = x * math.cos(angle) - y * math.sin(angle)
    rotated_y = x * math.sin(angle) - y * math.cos(angle)

    return Point(rotated_x, rotated_y)

def normalizeDegrees(deg):
    while deg >= 360:
        deg -= 360
    while deg < 0:
        deg +=360

    return deg  

def normalizeRadians(rad):
    while rad >= 2 * math.pi:
        rad -= 2 * math.pi
    while rad < 0:
        rad += 2 * math.pi

    return rad   

def toRadians(deg):
   return deg * math.pi / 180

def toDegrees(rad):
    return rad * 180 / math.pi

def hypot(x, y):
    return math.sqrt(x * x + y * y)

def signum(x):
    if x < 0:
        return -1
    return 1

def msToS(ms):
    return ms / 1000

def sToMs(sec):
    return sec * 1000

def clipMotor(value):
    if value < -100:
        value = -100
    elif value > 100:
        value = 100
    return value

def findShortestPath(current_angle, target_angle):
    error = target_angle - current_angle
    error_abs = abs(error)

    if (error_abs <= 360 - error_abs):
        return -error
    return signum(error) * 360 - error

def getTimeMs():
    return int(time.time() * 1000)

def zeros_like(list):
    return [0] * len(list)

def linspace(start: int, stop: int, num: int = 50, endpoint: bool = True):
    if num <= 0:
        raise ValueError("Number of samples must be positive")
    
    if endpoint:
        step = (stop - start) / max(1, num - 1)
    else: step = (stop - start) / max(1, num)

    result = [start + i * step for i in range(num)]

    if not endpoint and num > 1:
        result[-1] = stop

    return result

def binary_search(val, list, atr: str | None = None, left = None, right = None):
    if left == None:
        left = 0
    if right == None:
        right = len(list) - 1
    

    while left + 1 < right:
        m = int((left + right) / 2)
        if atr is None:
            compare = list[m]
        else: compare = getattr(list[m], atr)


        if val == compare:
            return m, list[m]
        if val < compare:
            right = m
        else: left = m
    
    return left, list[left]

def selection_sort(list, atr: str):
    sorted: bool = False
    length = len(list)

    while not sorted:
        sorted = True
        for i in range(length - 1):
            if getattr(list[i], atr) > getattr(list[i+1], atr):
                sorted = False

                aux = list[i]
                list[i] = list[i+1]
                list[i+1] = aux
    
    return list

def pointsToGraph(points: List[Point]):
    x = []
    y = []

    for point in points:
        x.append(point.x)
        y.append(point.y)
    
    return x, y

def idle():
    pass

def joy_clip(value: float):
    if value < -1:
        return -1
    if value > 1:
        return 1
    return value

def point_on_right_of_line(point: Point, line1: Point, line2: Point):
    x1, y1 = line1.tuple()
    x2, y2 = line2.tuple()

    a = float(y2 - y1)
    b = float(x1 - x2)
    c = - (a * x1 + b * y1) 

    return a * point.x + b * point.y + c >= 0

def point_in_rectangle(point: Point, corners: List[Point]):
    size = len(corners)

    for i in range(size):
        first: Point = corners[i]
        try: second: Point = corners[i + 1]
        except: second: Point = corners[0]

        if point_on_right_of_line(point, first, second):
            return False
    
    return True

def pygame_vector_to_point(vector: pygame.math.Vector2 | List[pygame.math.Vector2]):
    if not isinstance(vector, list):
        return Point(vector.x, vector.y)
    
    new = []
    for each in vector:
        new.append(Point(each.x, each.y))

    return new

def rotateByPoint(origin: Point, point: Point, angle: int) -> Point:
    ox, oy = origin.tuple()
    px, py = point.tuple()

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    
    return Point(qx, qy)

