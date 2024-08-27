from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Trajectory.Control.feedforward import *
from pythfinder.Trajectory.Kinematics.generic import *
import matplotlib.pyplot as mplt


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
    def __init__(self, time: int = None, 
                 field_vel: ChassisState = None, 
                 displacement: float = None,
                 pose: Pose = None,
                 profile_state: ProfileState = None):

        self.velocities = ChassisState() if field_vel is None else field_vel # cm / s

        self.time = 0 if time is None else time # ms
        self.displacement = 0 if displacement is None else displacement
        self.pose = Pose() if pose is None else pose
        self.profile_state = ProfileState() if profile_state is None else profile_state
    
    def is_like(self, other): 
        return (self.velocities.is_like(other.velocities)
                        and 
                self.pose.head == other.pose.head)
    
    def decompose(self, n: int) -> Point: 
        match n:
            case 0: # pose
                return self.pose.point()
            case 1: # velocity
                if not self.velocities.VEL.is_zero():
                    return self.velocities.VEL 

                magnitude = 20
                angle = self.pose.rad() - math.pi / 2

                return Point(magnitude * math.cos(angle),
                             magnitude * math.sin(angle))

            case 2: # acceleration
                magnitude = self.profile_state.acc
                angle = self.pose.rad()

                return Point(magnitude * math.cos(angle),
                             magnitude * math.sin(angle))

    def print(self):
        print("\n\ntime: {0}\ndisplacement: {1}".format(self.time, self.displacement))
        self.pose.print()
    
    def copy(self):
        return MotionState(self.time,
                           self.velocities,
                           self.displacement,
                           self.pose)

class MotionSegment(ABC):
    def __init__(self, last_state: MotionState):
        self.last_state = last_state

        self.start_time = self.last_state.time + 1
        self.end_time = 0
        self.total_time = 0

        self.current_pose = self.last_state.pose.copy()

        self.profiles: List[MotionProfile] = []
        self.states: List[MotionState] = []
        self.built = False

    # makes the time positive
    def normalize_segm_time(self, time: int):
        if time < 0: time = self.total_time + time - 1

        return time

    def traj_time_to_segm_time(self, time: int):
        return time - self.start_time



    def generate(self):
        self.current_pose = self.last_state.pose.copy()
        self.states: List[MotionState] = []

        t = self.start_time

        for profile in self.profiles:
            while not profile.FINISHED_ms(t):
                profile_state = profile.get_state_ms(t)
                self.states.append(self.motion_from_profile_state(t, profile_state))
                t += 1

        # check for an empty segment        
        if len(self.states) == 1:
            self.states[-1] = self.last_state
        
        self.total_time = len(self.states)
        self.end_time = self.states[-1].time
        self.built = True



    @abstractmethod
    def get_action(self) -> MotionAction:
        pass

    @abstractmethod
    def copy(self, last_state: MotionState, constraints2d: Constraints2D):
        pass
    
    @abstractmethod
    def motion_from_profile_state(self, t: int, profile_state: ProfileState) -> MotionState:
        pass

    @abstractmethod
    def add_constraints_segm_time(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        pass

    def add_constraints_traj_time(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        self.add_constraints_segm_time(self.traj_time_to_segm_time(time), constraints2d, auto_build)



    def interrupt_traj_time(self, time: int):
        self.interrupt_segm_time(self.traj_time_to_segm_time(time))

    def interrupt_segm_time(self, time: int):
        self.states = self.states[:time]
        
        # to ensure continuity, add an additional 0 speed state
        self.states.append(MotionState(time = self.states[-1].time + 1,
                                       field_vel = ChassisState(),
                                       displacement = self.states[-1].displacement,
                                       pose = self.states[-1].pose))



    def get_traj_time(self, time: int) -> MotionState:
        return self.get_segm_time(self.traj_time_to_segm_time(time))
    
    def get_segm_time(self, time: int) -> MotionState:
        if not self.built:
            print("\n\nplease generate the states of this segment first")
            return MotionState()
        
        try: return self.states[self.normalize_segm_time(time)]
        except: return None
    


    def time_in_segment_segm_time(self, time: int) -> bool:
        if time is None: return False

        return in_open_interval(self.normalize_segm_time(time), 0, len(self.states) - 1)
    
    def time_in_segment_traj_time(self, time: int) -> bool:
        return self.time_in_segment_segm_time(self.traj_time_to_segm_time(time))



    def get_all(self) -> List[MotionState]:
        if not self.built:
            print("\n\nplease generate the states of this segment first")
            return []
    
        return self.states
    
    def graph_motion_states(self, atr: str, second_atr: str = None):
        if not self.built:
            print("\n\ncan't graph the states without generating them")
            return None
        
        value = []
        time = []

        for state in self.states:
            val = getattr(state, atr)
            if second_atr is not None:
                val = getattr(val, second_atr)

            value.append(val)

        time = linspace(0, len(value), len(value))


        mplt.figure(figsize=(7, 7), facecolor = 'black')
        mplt.style.use('dark_background')

        mplt.title('Motion State graph', fontsize = 22)
        mplt.xlabel('time (ms)', fontsize = 14)
        mplt.ylabel('{0} + {1}'.format(atr, second_atr if second_atr is not None else "."), fontsize = 14)

        mplt.scatter(time, value, color = 'red', s = 1)
        mplt.show()

    def state_from_pure_linear_segment(self, state: MotionState):
        return state.velocities.ANG_VEL == 0
    
    def state_from_pure_angular_segment(self, state: MotionState):
        return state.velocities.VEL.is_zero()
    
    def state_from_linear_and_angular_segment(self, state: MotionState):
        return not (state.velocities.ANG_VEL == 0 or state.velocities.VEL.is_zero())
    
