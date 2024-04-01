import math

#---Point--- and ---Pose--- classes, used for localisation
class Point:
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
        return hypot(other.x - self.x, other.y, - self.y)

class Pose(Point):
    def __init__(self, x = 0, y = 0, head = 0):
        super().__init__(x, y)
        self.head = head 

    def set(self, x, y, head):
        super().set(x, y)
        self.head = head 


#enhanced math functions
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
