# helper class to store and manage PID coefficients

class PIDCoefficients():
    def __init__(self, 
                 kP: int | float = 0, 
                 kI: int | float = 0, 
                 kD: int | float = 0):
        
        self.kP = kP
        self.kI = kI
        self.kD = kD
    
    def set(self,
            kP: int | float | None = None, 
            kI: int | float | None = None, 
            kD: int | float | None = None):
        
        if kP is not None:
            self.kP = kP
        if kI is not None:
            self.kI = kI
        if kD is not None:
            self.kD = kD
        