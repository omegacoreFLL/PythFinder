from typing import List

import pygame
import math

EPSILON = 1e-5


class Point():
    """
    A class representing a point in a 2D coordinate system.
    Attributes:
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
    Methods:
        from_tuple(tuple): Creates a Point object from a tuple of coordinates.

        rotate_by(rad): Rotates the point by a given angle in radians.
        distance_to(other): Calculates the distance between this point and another point.
        inverse_atan2(): Calculates the inverse tangent of the point's coordinates.
        is_zero(): Checks if the point is at the origin (0, 0).
        flip_coordinates(): Flips the x and y coordinates of the point.

        __sub__(other): Subtracts another point or a scalar from this point.
        __add__(other): Adds another point or a scalar to this point.
        __mul__(other): Multiplies this point by another point or a scalar.
        __truediv__(other): Divides this point by another point or a scalar.
        __eq__(other): Checks if this point is equal to another point.

        set(x, y): Sets the coordinates of the point.
        hypot(): Calculates the hypotenuse of the point's coordinates.
        round(n): Rounds the coordinates of the point to a given number of decimal places.
        tuple(): Returns the coordinates of the point as a tuple.
        atan2(): Calculates the arctangent of the point's coordinates.
        copy(): Creates a copy of the point.
        negate(): Negates the coordinates of the point.

        print(): Prints the coordinates of the point.
        str(): Returns a string representation of the point.
    """

    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y  

    @staticmethod
    def from_tuple(tuple: tuple):
        return Point(tuple[0], tuple[1])



    def rotate_by(self, rad):
        copy = self.x

        self.x = self.x * math.cos(rad) - self.y * math.sin(rad)
        self.y = copy * math.sin(rad) - self.y * math.cos(rad)

        return self
    
    def distance_to(self, other):
        return math.hypot(other.x - self.x, other.y - self.y)
    
    def inverse_atan2(self):
        return math.atan2(self.x, self.y)
    
    def is_zero(self):
        return self.x == 0 and self.y == 0

    def flip_coordinates(self):
        copy = self.x
        self.x = self.y
        self.y = copy

        return self
    


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
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    

        
    def set(self, x, y):
        self.x = x 
        self.y = y 

    def hypot(self):
        return math.hypot(self.x, self.y)
  
    def round(self, n):
        self.x = round(self.x, n)
        self.y = round(self.y, n)

        return self

    def tuple(self):
        return (self.x, self.y)
    
    def atan2(self):
        return math.atan2(self.y, self.x)
    
    def copy(self):
        return Point(self.x, self.y)
    
    def negate(self):
        self.x = -self.x
        self.y = -self.y

        return self
    


    def print(self):
        print("x: {0} y: {1}".format(self.x, self.y))
    
    def str(self):
        return "x: {0} y: {1}".format(*self.round(4).tuple())

class Pose(Point):
    """
    Represents a pose in a 2D space with x and y coordinates and a heading angle.
    Args:
        x (float): The x-coordinate of the pose. Default is 0.
        y (float): The y-coordinate of the pose. Default is 0.
        head (float): The heading angle of the pose in degrees. Default is 0.
    Attributes:
        x (float): The x-coordinate of the pose.
        y (float): The y-coordinate of the pose.
        head (float): The heading angle of the pose in degrees.
    Methods:
        from_point(point: Point) -> Pose:
            Creates a new Pose object from a Point object.
        
        set(x, y, head):
            Sets the x, y, and head attributes of the pose.
        rad() -> float:
            Converts the heading angle from degrees to radians.
        point() -> Point:
            Returns a Point object with the same x and y coordinates as the pose.
        copy() -> Pose:
            Creates a copy of the pose.

        __sub__(other) -> Pose:
            Subtracts another pose or a point from the current pose.
        __add__(other) -> Pose:
            Adds another pose or a point to the current pose.
        __mul__(other) -> Pose:
            Multiplies the current pose by another pose or a point.
        __truediv__(other) -> Pose:
            Divides the current pose by another pose or a point.
        __eq__(other) -> bool:
            Checks if the current pose is equal to another pose or a point.

        rotate_by(rad) -> Pose:
            Rotates the pose by a given angle in radians.
        normalize_degreez() -> Pose:
            Normalizes the heading angle of the pose to the range [0, 360).
            
        str() -> str:
            Returns a string representation of the pose.
        write() -> str:
            Returns a formatted string representation of the pose with rounded values.
        print():
            Prints the pose in the format "x: {x} y: {y} head: {head}".
    """
    def __init__(self, x = 0, y = 0, head = 0):
        super().__init__(x, y)
        self.head = head 
    
    def from_point(self, point: Point):
        self.x = point.x
        self.y = point.y

        return self



    def set(self, x, y, head):
        super().set(x, y)
        self.head = head 
    
    def rad(self):
        return math.radians(self.head)

    def point(self):
        return Point(self.x, self.y)
        
    def copy(self):
        return Pose(self.x, self.y, self.head)
    


    def __sub__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x - other.x, self.y - other.y, normalize_degres(self.head - other.head))
        if isinstance(other, Point):
            return Pose(self.x - other.x, self.y - other.y, self.head)
        return Pose(self.x - other, self.y - other, normalize_degres(self.head - other))
    
    def __add__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x + other.x, self.y + other.y, normalize_degres(self.head + other.head))
        if isinstance(other, Point):
            return Pose(self.x + other.x, self.y + other.y, self.head)
        return Pose(self.x + other, self.y + other, normalize_degres(self.head + other))
   
    def __mul__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x * other.x, self.y * other.y, normalize_degres(self.head * other.head))
        if isinstance(other, Point):
            return Pose(self.x * other.x, self.y * other.y, self.head)
        return Pose(self.x * other, self.y * other, normalize_degres(self.head * other))
    
    def __truediv__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x / other.x, self.y / other.y, normalize_degres(self.head / other.head))
        if isinstance(other, Point):
            return Pose(self.x / other.x, self.y / other.y, self.head)
        return Pose(self.x / other, self.y / other, normalize_degres(self.head / other))
    
    def __eq__(self, other):
        if isinstance(other, Pose):
            return self.x == other.x and self.y == other.y and self.head == other.head
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
    


    def rotate_by(self, rad):
        point = super().rotate_by(rad)
        return Pose(point.x, point.y, self.head)
    
    def normalize_degreez(self):
        return Pose(self.x, self.y, normalize_degres(self.head))



    def str(self):
        return ("x: {0} y: {1} head: {2}"
                   .format(self.x, self.y, self.head))
    
    def write(self):
        return self.round(2).str()
    
    def print(self):
        print("x:{0} y:{1} head:{2}".format(self.x, self.y, self.head))



def rotate_by(rad, point: Point, origin: Point = Point(0, 0)):
    x = point.x - origin.x
    y = point.y - origin.y

    rotated_x = x * math.cos(rad) - y * math.sin(rad)
    rotated_y = x * math.sin(rad) - y * math.cos(rad)

    return Point(rotated_x, rotated_y)



def normalize_degres(deg):
    while deg >= 360:
        deg -= 360
    while deg < 0:
        deg +=360

    return deg  

def normalize_radians(rad):
    while rad >= 2 * math.pi:
        rad -= 2 * math.pi
    while rad < 0:
        rad += 2 * math.pi

    return rad   



def signum(x):
    if x < 0:
        return -1
    return 1



def ms_to_sec(ms):
    return ms / 1000

def sec_to_ms(sec):
    return sec * 1000



def find_shortest_path(current_angle, target_angle):
    error = target_angle - current_angle
    error_abs = abs(error)

    if (error_abs <= 360 - error_abs):
        return -error
    return signum(error) * 360 - error

def find_longest_path(current_angle, target_angle):
    shortest = find_shortest_path(current_angle, target_angle)
    return (360 - abs(shortest)) * -signum(shortest)



# numpy custom implementations

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



# algorithms

def binary_search(val, list, atr: str | None = None, left = None, right = None):
    """
    Perform binary search on a sorted list to find the index and value of a given element.
    Args:
        val: The value to search for.
        list: The sorted list to search in.
        atr (str | None, optional): The attribute name to compare if the list contains objects. Defaults to None.
        left (int, optional): The left index of the sublist to search in. Defaults to None.
        right (int, optional): The right index of the sublist to search in. Defaults to None.
    Returns:
        Tuple[int, Any]: A tuple containing the index and value of the found element, or the index and value of the closest element if the element is not found.
    """

    if left is None:
        left = 0
    if right is None:
        right = len(list) - 1

    while left + 1 < right:
        m = (left + right) // 2
        if atr is None:
            compare = list[m]
        else: compare = getattr(list[m], atr)

        if val == compare:
            return m, list[m]
        if val < compare:
            right = m
        else: left = m
    
    return left, list[left]

def linear_interpolation(x, x0, x1, y0, y1):
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    
def quick_sort(list, atr: str | None = None):
    if len(list) <= 1:
        return list
    
    if atr is not None:
        pivot = list[len(list) // 2]
        left = [x for x in list if getattr(x, atr) < getattr(pivot, atr)]
        middle = [x for x in list if getattr(x, atr) == getattr(pivot, atr)]
        right = [x for x in list if getattr(x, atr) > getattr(pivot, atr)]
    else:
        pivot = list[len(list) // 2]
        left = [x for x in list if x < pivot]
        middle = [x for x in list if x == pivot]
        right = [x for x in list if x > pivot]

    return quick_sort(left, atr) + middle + quick_sort(right, atr)

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



# conversion functions

def convert_points_to_lists(points: List[Point]):
    x = []
    y = []

    for point in points:
        x.append(point.x)
        y.append(point.y)
    
    return x, y

def pygame_vector_to_point(vector: pygame.math.Vector2 | List[pygame.math.Vector2]):
    if not isinstance(vector, list):
        return Point(vector.x, vector.y)
    
    new = []
    for each in vector:
        new.append(Point(each.x, each.y))

    return new





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



def in_closed_interval(val: float, left: float, right: float) -> bool:
    return val >= left and val <= right

def in_open_interval(val: float, left: float, right: float) -> bool:
    return val > left and val < right



def distance(p1: tuple | Point, p2: tuple | Point):
    if isinstance(p1, Point):
        p1 = p1.tuple()
    if isinstance(p2, Point):
        p2 = p2.tuple()

    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])



def percentage_to_alpha(value: int):
    return value * 2.25



def idle():
    pass