from pythfinder.Trajectory.Markers.generic import *
from pythfinder.Trajectory.constraints import *

class ConstraintsMarker(Marker):
    def __init__(self, time: int = None, displacement: float = None, relative: bool = False, 
                 constraints: Constraints2D = None):
        super().__init__(time, displacement, relative)
        self.constraints = constraints



