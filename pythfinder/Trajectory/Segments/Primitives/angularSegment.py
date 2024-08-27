from pythfinder.Components.BetterClasses.mathEx import Pose
from pythfinder.Trajectory.Control.feedforward import Pose, ProfileState
from pythfinder.Trajectory.Kinematics.generic import Pose
from pythfinder.Trajectory.Segments.Primitives.generic import *
from pythfinder.Trajectory.Control.feedforward import *
from pythfinder.Trajectory.Segments.Primitives.generic import MotionState

class AngularSegment(MotionSegment):
    def __init__(self,
                 last_state: MotionState,
                 constraints: Constraints,
                 kinematics: Kinematics,
                 angle_deg: float,
                 reversed: bool = False):
    
        self.last_state = last_state
        self.constraints = constraints
        self.kinematics = kinematics
        self.target = angle_deg
        self.reversed = reversed
        self.built = False

        # early exit when empty segment
        if last_state is None:
            return None
        
        super().__init__(last_state)
        
        self.diff = (math.radians(find_shortest_path(angle_deg, last_state.pose.head))
                                    if not reversed else
                     math.radians(find_longest_path(angle_deg, last_state.pose.head))
        )
        
        self.sign = signum(self.diff)
        self.diff = abs(self.diff)

        self.profile_states: List[ProfileState] = []
        self.profiles: List[MotionProfile] = []
        
        
        self.profiles.append(MotionProfile(self.diff, constraints, 
                                    start_velocity = self.last_state.velocities.ANG_VEL,
                                    end_velocity = 0,
                                    start_time_ms = self.start_time,
                                    start_distance = 0)
        )
    


    def add_constraints_segm_time(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        if not self.built:
            print("\n\ncan't add profile without generating")
            return None

        new_start_time = self.states[time].time
        new_start_distance = self.profile_states[time].dis
        new_start_velocity = self.profile_states[time].vel

        previous = 0
        for i in range(len(self.profiles) - 1):
            previous += self.profiles[i].distance
        distance = self.profile_states[-1].dis - new_start_distance + previous


        self.profiles.append(MotionProfile(distance, constraints2d.angular,
                                           new_start_velocity,
                                           0,
                                           new_start_time,
                                           new_start_distance)
        )

        if self.profiles[-1].NOT_DEFINED:
            print("\n\nconstraints impossible to satisfy without compromising continuity")
            print("'PROFILE NOT DEFINED' error")
            self.profiles.pop()

        else:
            # update the previous profile to end when the new one starts
            self.profiles[-2] = self.profiles[-2].copy(
                distance = new_start_distance - previous,
                end_velocity = new_start_velocity
            )

            if time == 0:
                self.profiles.pop(-2)

            self.built = False
            if auto_build: self.generate()

    def motion_from_profile_state(self, t: int, profile_state: ProfileState) -> MotionState:
        ang, ang_vel, ang_acc = profile_state.tuple()
        ang, ang_vel = ang * self.sign, ang_vel * self.sign

        self.profile_states.append(profile_state)
        self.current_pose = self.last_state.pose + Pose(0, 0, math.degrees(ang))
                
        # no linear velocity on pure angular motion
        VEL = Point()
        ANG_VEL = ang_vel
                
        return MotionState(time = t,
                           field_vel = ChassisState(VEL, ANG_VEL),
                           displacement = self.last_state.displacement,
                           pose = self.current_pose.copy(),
                           profile_state = profile_state
        )
    
        
                



    def get_action(self) -> MotionAction:
        return MotionAction.TURN
    
    def copy(self, last_state: MotionState, constraints2d: Constraints2D = None):
        return AngularSegment(last_state,
                              constraints2d.angular if constraints2d is not None else self.constraints,
                              self.kinematics,
                              self.target,
                              self.reversed)
        