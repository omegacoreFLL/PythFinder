from ev3sim.Components.BetterClasses.mathEx import *
import matplotlib.pyplot as mat
import math
import time

class HermitePose():
    def __init__(self, point: Point, deriv1 = Pose(), deriv2 = Pose()):
        self.p = point
        self.v = deriv1
        self.a = deriv2
    
    def heading(self, head):
        self.v = Point(math.cos(head), math.sin(head))


class QuinticHermiteSpline():
    def __init__(self, h0: HermitePose, h1: HermitePose):
        self.h0 = h0
        self.h1 = h1
        self.coeff = []

        self.getCoeff()

    def getCoeff(self):
        self.__getCoeffX()
        self.__getCoeffY()
    
    def __getCoeffX(self):
        f = self.h0.p.x
        e = self.h0.v.x
        d = (self.h0.a.x) / 2

        i0 = self.h1.p.x - (d + e + f)
        i1 = self.h1.v.x - (e + 2 * d)
        i2 = self.h1.a.x - 2 * d

        c = 4 * i0 - 4 * i1 + i2 / 2
        b = 7 * i1 - 15 * i0 - i2
        a = i2 / 2 - 3 * i1 + 12 * i0

        self.coeff.append((a, b, c, d, e, f))
    
    def __getCoeffY(self):
        f = self.h0.p.y
        e = self.h0.v.y
        d = (self.h0.a.y) / 2

        i0 = self.h1.p.y - (d + e + f)
        i1 = self.h1.v.y - (e + 2 * d)
        i2 = self.h1.a.y - 2 * d

        c = 4 * i0 - 4 * i1 + i2 / 2
        b = 7 * i1 - 15 * i0 - i2
        a = i2 / 2 - 3 * i1 + 12 * i0

        self.coeff.append((a, b, c, d, e, f))
    
    def calculate(self, t: float):
        if t < 0 or t > 1:
            raise Exception("can't do that here, little guy")
        
        return Point(self.x(t), self.y(t))
    
    def x(self, t):
        return (self.coeff[0][0] * t ** 5 +
                self.coeff[0][1] * t ** 4 +
                self.coeff[0][2] * t ** 3 +
                self.coeff[0][3] * t ** 2 +
                self.coeff[0][4] * t +
                self.coeff[0][5])

    def dx(self, t):
        return (self.coeff[0][0] * 5 * t ** 4 +
                self.coeff[0][1] * 4 * t ** 3 +
                self.coeff[0][2] * 3 * t ** 2 +
                self.coeff[0][3] * 2 * t +
                self.coeff[0][4])

    def ddx(self, t):
        return (self.coeff[0][0] * 20 * t ** 3 +
                self.coeff[0][1] * 12 * t ** 2 +
                self.coeff[0][2] * 6 * t +
                self.coeff[0][3] * 2)


    def y(self, t):
        return (self.coeff[1][0] * t ** 5 +
                self.coeff[1][1] * t ** 4 +
                self.coeff[1][2] * t ** 3 +
                self.coeff[1][3] * t ** 2 +
                self.coeff[1][4] * t +
                self.coeff[1][5])

    def dy(self, t):
        return (self.coeff[1][0] * 5 * t ** 4 +
                self.coeff[0][1] * 4 * t ** 3 +
                self.coeff[1][2] * 3 * t ** 2 +
                self.coeff[1][3] * 2 * t +
                self.coeff[1][4])

    def ddy(self, t):
        return (self.coeff[1][0] * 20 * t ** 3 +
                self.coeff[1][1] * 12 * t ** 2 +
                self.coeff[1][2] * 6 * t +
                self.coeff[1][3] * 2)


    def getCurvatureX(self, t): 
        return abs(self.ddx(t)) / math.sqrt((1 + self.dx(t)) ** 3)
    
    def getCurvatureY(self, t):
        return abs(self.ddy(t)) / math.sqrt((1 + self.dy(t)) ** 3)




start = HermitePose(Pose(0, 3), deriv2 = Pose(0, 80))
start.heading(0)

end = HermitePose(Pose(40, 20))
end.heading(190)

spline = QuinticHermiteSpline(start, end)

first = True

length = 0
i = 0
x, ux, uy = [], [], []
while i <= 1:
    current = spline.calculate(i)
    ux.append(current.x)
    uy.append(current.y)

    i += 0.00001

mat.xlabel('x - axis')
mat.ylabel('y - axis')
mat.title('Quintic Polynomial test')

#figure, graphics = mat.subplots(1, 2)
mat.plot(ux, uy)
#graphics[1].plot(x, uy)

mat.show()