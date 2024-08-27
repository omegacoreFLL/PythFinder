from pythfinder.Trajectory.Control.feedforward import ProfileState
from pythfinder.Trajectory.Segments.Primitives.generic import *
from pythfinder.Trajectory.Segments.Primitives.generic import MotionState

class WaitSegment(MotionSegment):
    def __init__(self, 
                 last_state: MotionState,
                 ms: int):
        
        self.last_state = last_state
        self.ms = ms
        self.built = False

        # early exit when empty segment
        if last_state is None:
            return None
        
        super().__init__(last_state)
        
        self.total_time = ms
        self.end_time = self.start_time + self.total_time - 1
    

    def add_constraints_segm_time(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        # what did you expect? Sure, speed constraints when staying in one place, sure
        # go to sleep man
        pass

    def motion_from_profile_state(self, t: int, profile_state: ProfileState) -> MotionState:
        pass # no profile heh



    def generate(self):
        for i in range(self.ms):
            self.states.append(
                MotionState(time = self.start_time + i, 
                            field_vel = ChassisState(),                  # no velocities when stationary
                            displacement = self.last_state.displacement, # same displacement
                            pose = self.last_state.pose,                 # same pose
                            profile_state = ProfileState()))             # empty profile state
        
        # empty segment
        if len(self.states) == 0:
            self.states.append(self.last_state)

        self.built = True
    


    def get_action(self) -> MotionAction:
        return MotionAction.WAIT

    def copy(self, last_state: MotionState, constraints2d: Constraints2D):
        return WaitSegment(last_state,
                           self.ms)
    
    def add_ms(self, ms: int):
        return WaitSegment(self.last_state,
                           self.ms + ms)