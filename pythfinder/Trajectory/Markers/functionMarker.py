from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Trajectory.Markers.generic import *

class FunctionMarker(Marker):
    def __init__(self, time: int = None, displacement: float = None, relative: bool = False, 
                 function = idle):
        super().__init__(time, displacement, relative)
        self.function = function
    
    def do(self):
        try: self.function()
        except: print("\n\nno function is to be called ??")