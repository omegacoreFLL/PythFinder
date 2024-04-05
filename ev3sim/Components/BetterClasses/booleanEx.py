from enum import Enum, auto

class Fun(Enum):
    SET = auto()
    GET = auto()
    NEGATE = auto()
    COMPARE = auto()


class BooleanEx():
    def __init__(self, value: bool):
        self.value = value
    
    def get(self):
        return self.value
    
    def set(self, new: bool):
        self.value = new
    
    def negate(self):
        self.value = not self.value
    
    def compare(self, other = True):
        return self.value == other
    
    def choose(self, fun: Fun, value = None):
        if fun == Fun.SET:
            if value == None:
                raise Exception("choose a boolean to be 'set'")
            self.set(value)
        elif fun == Fun.GET:
            self.get()
        elif fun == Fun.NEGATE:
            self.negate()
        elif fun == Fun.COMPARE:
            if value == None:
                self.compare()
            else: self.compare(value)
        else: raise Exception("not a valid function")