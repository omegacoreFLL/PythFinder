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
                 pose: Pose = None):

        self.velocities = ChassisState() if field_vel is None else field_vel # cm / s

        self.time = 0 if time is None else time # ms
        self.displacement = 0 if displacement is None else displacement
        self.pose = Pose() if pose is None else pose
    
    def isLike(self, other): 
        return (self.velocities.isLike(other.velocities)
                        and 
                self.pose.head == other.pose.head)

    def print(self):
        print("\n\ntime: {0}\ndisplacement: {1}".format(self.time, self.displacement))
        self.pose.print()
    
    def copy(self):
        return MotionState(self.time,
                           self.velocities,
                           self.displacement,
                           self.pose)

class MotionSegment(ABC):
    def __init__(self,last_state: MotionState):
        self.last_state = last_state

        self.start_time = self.last_state.time + 1
        self.end_time = 0
        self.total_time = 0

        self.current_pose = self.last_state.pose.copy()

        self.profiles: List[MotionProfile] = []
        self.states: List[MotionState] = []
        self.built = False

    # makes the time positive
    def normalizeSegmTime(self, time: int):
        if time < 0: time = self.total_time + time - 1

        return time

    def trajTime_2_segmTime(self, time: int):
        return time - self.start_time



    def generate(self):
        self.current_pose = self.last_state.pose.copy()
        self.states: List[MotionState] = []

        nr_of_profiles = len(self.profiles)
        t = self.start_time
        profile_index = 0

        while profile_index < nr_of_profiles:
            
            if self.profiles[profile_index].FINISHED_ms(t):
                profile_index += 1
                continue
            
            profile_state = self.profiles[profile_index].getStateMs(t)
            self.states.append(self.motionFromProfileState(t, profile_state))

            t += 1

        # check for an empty segment        
        if len(self.states) == 1:
            self.states[-1] = self.last_state
        
        self.total_time = len(self.states)
        self.end_time = self.states[-1].time
        self.built = True



    @abstractmethod
    def getAction(self) -> MotionAction:
        pass

    @abstractmethod
    def copy(self, last_state: MotionState, constraints2d: Constraints2D):
        pass
    
    @abstractmethod
    def motionFromProfileState(self, profile_state: ProfileState) -> MotionState:
        pass
    
    @abstractmethod
    def motionFromProfileState(self, t: int, profile_state: ProfileState) -> MotionState:
        pass

    @abstractmethod
    def addConstraintsSegmTime(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        pass

    def addConstraintsTrajTime(self, time: int, constraints2d: Constraints2D, auto_build: bool = True):
        self.addConstraintsSegmTime(self.trajTime_2_segmTime(time), constraints2d, auto_build)



    def interruptTrajTime(self, time: int):
        self.interruptSegmTime(self.trajTime_2_segmTime(time))

    def interruptSegmTime(self, time: int):
        self.states = self.states[:time]



    def getTrajTime(self, time: int) -> MotionState:
        return self.getSegmTime(self.trajTime_2_segmTime(time))
    
    def getSegmTime(self, time: int) -> MotionState:
        if not self.built:
            print("\n\nplease generate the states of this segment first")
            return MotionState()
        
        try: return self.states[self.normalizeSegmTime(time)]
        except: return None
    


    def timeInSegmentSegmTime(self, time: int) -> bool:
        if time is None: return False

        return inOpenInterval(self.normalizeSegmTime(time), 0, len(self.states) - 1)
    
    def timeInSegmentTrajTime(self, time: int) -> bool:
        return self.timeInSegmentSegmTime(self.trajTime_2_segmTime(time))



    def get_all(self) -> List[MotionState]:
        if not self.built:
            print("\n\nplease generate the states of this segment first")
            return []
    
        return self.states
    
    def graphMotionStates(self, atr: str, second_atr: str = None):
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

    def stateFromPureLinearSegment(self, state: MotionState):
        return state.velocities.ANG_VEL == 0
    
    def stateFromPureAngularSegment(self, state: MotionState):
        return state.velocities.VEL.isEmpty()
    
    def stateFromLinearAndAngularSegment(self, state: MotionState):
        return not (state.velocities.ANG_VEL == 0 or state.velocities.VEL.isEmpty())
    
