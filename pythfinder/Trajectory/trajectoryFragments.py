from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Trajectory.Kinematics.generic import *


class MotionAction(Enum):
    LINE = auto()

    TO_POINT = auto()
    TO_POSE = auto()
    TO_POINT_CONSTANT_HEAD = auto()
    TO_POSE_CONSTANT_HEAD = auto()
    TO_POSE_LINEAR_HEAD = auto()

    SPLINE = auto()

    TURN = auto()
    WAIT = auto()
    SET_POSE = auto()

    REL_MARKER = auto()
    INT_MARKER = auto()
    REL_CONSTRAINTS = auto()

class MotionState():
    def __init__(self, time: int, 
                 velocities: ChassisState, 
                 displacement: float,
                 pose: Pose, 
                 turn: bool = False):

        self.velocities = velocities # cm / s

        self.time = time # ms
        self.displacement = displacement
        self.pose = pose

        self.turn = turn
    
    def isLike(self, other): 
        return (self.turn == other.turn
                        and
                self.velocities.isLike(other.velocities)
                        and 
                self.pose.head == other.pose.head)

class MotionSegment():
    def __init__(self, action: MotionAction, value: float, 
                 constraints: Constraints = None):
        self.action = action 
        self.constraints = constraints
        self.value = value
        self.states = {}

        self.start_time = None
        self.end_time = None
        self.total_time = 0
    
    def add(self, state: MotionState):
        if self.start_time is None:
            self.start_time = state.time
        self.end_time = state.time

        self.states[state.time] = state
    
    def get(self, time: int):
        return self.states[time]
    
    def build(self):
        try: self.total_time = self.end_time - self.start_time + 1
        except: self.total_time = 1
    
    def reset(self):
        self.start_time = self.end_time = None
        self.total_time = 0
        self.states = {}
    
    def eraseAllAfter(self, index: int):
        #doesn't really erase the values, just sets the bounds such that
        #   it's not accessible anymore. Deal with it.

        self.end_time = index
        self.build()

        return self.states[index].pose.copy()
