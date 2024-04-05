class PIDCoefficients():
    def __init__(self, kP = 0, kI = 0, kD = 0):
        self.kP = kP
        self.kI = kI
        self.kD = kD
    
    def set(self, kP = None, kI = None, kD = None):
        if not kP == None:
            self.kP = kP
        if not kI == None:
            self.kI = kI
        if not kD == None:
            self.kD = kD
        