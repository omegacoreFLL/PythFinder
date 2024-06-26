from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Trajectory.constraints import *


class Marker:
    def __init__(self, time: int = None, displacement: float = None, relative: bool = False):
        self.time = time
        self.displacement = displacement
        self.relative = relative

class FunctionMarker(Marker):
    def __init__(self, time: int = None, displacement: float = None, relative: bool = False, 
                 function = None):
        super().__init__(time, displacement, relative)
        self.function = function
    
    def do(self):
        try: self.function()
        except: print("\n\nno function is to be called ??")

class ConstraintsMarker(Marker):
    def __init__(self, time: int = None, displacement: float = None, relative: bool = False, 
                 constraints: Constraints2D = None):
        super().__init__(time, displacement, relative)
        self.constraints = constraints

class InterruptMarker(Marker):
    pass






