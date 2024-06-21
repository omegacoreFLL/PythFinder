from enum import Enum, auto

class MarkerType(Enum):
    TEMPORAL = auto()
    DISPLACEMENT = auto()



class Marker():
    def __init__(self, val: float, fun, type: MarkerType, rel):
        self.value = val
        self.type = type
        self.fun = fun
        self.rel = rel
    
    def do(self):
        try: self.fun()
        except: print("\n\nexcuse me, what? \nprovide a method in the 'Marker' object with the value '{0}' and type '{1}'"
                      .format(self.value, self.type.name))

    class Interrupter():
        def __init__(self, val: float, type: MarkerType):
            self.value = val
            self.type = type
