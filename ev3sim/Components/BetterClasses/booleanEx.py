from enum import Enum, auto

class Fun(Enum):
    SET = auto()
    GET = auto()
    NEGATE = auto()
    COMPARE = auto()


# extended class for booleans

class BooleanEx():

    def __init__(self, 
                 value: bool):
        self.__value = value
    
    def get(self):
        return self.__value
    
    def set(self, 
            new: bool):
        self.__value = new
    
    def negate(self):
        self.__value = not self.__value
    
    def compare(self, 
                other: bool = True):
        return self.__value == other
    
    # method including every functionalitiy
    def choose(self, fun: Fun, 
               value: bool | None = None):

        if fun == Fun.SET:
            if value is None:
                raise Exception("choose a boolean to be SET")
            self.set(value)
        elif fun == Fun.GET:
            self.get()
        elif fun == Fun.NEGATE:
            self.negate()
        elif fun == Fun.COMPARE:
            if value is None:
                self.compare()
            else: self.compare(value)
        else: raise Exception("not a valid function")