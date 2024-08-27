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

    def get_coefficients(self):
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
        
    def get_coefficients(self):
        return self.a, self.b, self.c, self.d, self.e, self.f
