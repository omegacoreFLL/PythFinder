from pythfinder.Trajectory.Segments.Splines.polynomialSplines import *
from pythfinder.Trajectory.Segments.Primitives.generic import *
from pythfinder.Trajectory.Segments.Splines.generic import *
from pythfinder.Trajectory.Control.feedforward import *

class SplineSegment(MotionSegment):
    def __init__(self, 
                 last_state: MotionState,
                 kinematics: Kinematics,
                 constraints2d: Constraints2D,
                 end: SplineTarget,
                 tangent: bool = True,
                 reversed: bool = False
    ):
        self.last_state = last_state
        self.kinematics = kinematics
        self.constraints2d = constraints2d
        self.end = end
        self.tangent = tangent
        self.reversed = reversed
        
        
        if last_state is None:
            return None
        
        super().__init__(last_state)
        
        self.last_generated_state = last_state.copy()

        self.start_derivatives = [self.last_state.decompose(n) for n in range(2)]  # now we match derivatives
        self.start = SplineTarget(self.start_derivatives)

        self.spline = QubicSpline(self.start, self.end, self.constraints2d.linear)

    def generate(self):
        self.current_pose = self.last_state.pose.copy()
        self.states: List[MotionState] = []

        self.last_generated_state = self.last_generated_state.copy()

        self.pose_linear = self.spline.generate(0)
        self.vel_linear = self.spline.generate(1)

        self.pose_angular = self.spline.generate_ang(0)
        self.vel_angular = self.spline.generate_ang(1)

        for i in range(len(self.pose_linear)):
            self.states.append(MotionState(time = i + 1 + self.last_state.time,
                                           field_vel = ChassisState(self.vel_linear[i], self.vel_angular[i]),
                                           displacement = self.last_state.displacement + self.spline.integral[i],
                                           pose = Pose(self.pose_linear[i].x, self.pose_linear[i].y, math.degrees(self.pose_angular[i])),
                                           profile_state = ProfileState()))

        # get the end time
        self.total_time = len(self.states)
        self.end_time = self.states[-1].time
        self.built = True


    
    def motion_from_profile_state(self, t: int, profile_state: ProfileState) -> MotionState:
        pass

    def add_constraints_segm_time(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        pass



    def get_action(self) -> MotionAction:
        return MotionAction.SPLINE
    
    def copy(self, last_state: MotionState, constraints2d: Constraints2D):
        return SplineSegment(last_state,
                             self.kinematics,
                             constraints2d,
                             self.end,
                             self.tangent,
                             self.reversed)