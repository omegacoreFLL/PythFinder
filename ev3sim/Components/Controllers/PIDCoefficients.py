class PIDCoefficients():
    def __init__(self, kP = 0, kI = 0, kD = 0):
        self.kP = kP
        self.kI = kI
        self.kD = kD
    
    def set(self, kP = None, kI = None, kD = None):
        if kP is not None:
            self.kP = kP
        if kI is not None:
            self.kI = kI
        if kD is not None:
            self.kD = kD
        