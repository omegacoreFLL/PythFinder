from pythfinder.Trajectory.Control.feedforward import *
from pythfinder.Trajectory.Segments.Primitives import *

class PointSegment(MotionSegment):
    def __init__(self, 
                 last_state: MotionState,
                 kinematics: Kinematics,
                 constraints2d: Constraints2D,
                 point: Point,                  # target point
                 tangent: bool = False,         # sets the heading tangent to the line
                 reversed: bool = False         # reverses the heading by 180°
    ):
        self.last_state = last_state
        self.kinematics = kinematics
        self.constraints2d = constraints2d
        self.point = point
        self.tangent = tangent
        self.reversed = reversed


        if last_state is None:
            return None
        
        super().__init__(last_state)

        self.last_generated_state = last_state.copy()
        target = self.point
        current = self.last_state.pose.point()
        
        # store the primitive segments making up a point segment
        self.primitives: List[MotionSegment] = []

        # non-holonomic chassis require a heading tangent to the path
        if self.kinematics.getType() is ChassisType.NON_HOLONOMIC:
            self.tangent = True
        
        head = self.last_state.pose.head

        if self.tangent:
            # get the angle of the line
            head = normalizeDegrees(toDegrees((target - current).atan2()))

        # reverse the heading, holonomic or non-holonomic
        if reversed:
            head = normalizeDegrees(180 + head)

        # first primitive in this case would be going reverse / tangent (or no turn at all)
        self.primitives.append(AngularSegment(None, None, kinematics, head))
        self.primitives.append(LinearSegment(None, None, self.point))
        


    def addConstraintsTrajTime(self, time: int, constraints2D: Constraints2D, auto_build: bool = True):
        self.addConstraintsSegmTime(self.trajTime_2_segmTime(time), constraints2D, auto_build)

    def addConstraintsSegmTime(self, time: int, constraints2D: Constraints2D, auto_build: bool = True):
        if not self.built:
            print("\n\ncan't add constraints without calling the 'generate' method")
            return None
        
        time = self.normalizeSegmTime(time)

        if not self.stateFromPureLinearSegment(self.states[time]):
            self.primitives[-2].addConstraintsSegmTime(self.pointSegmTime_2_angularSegmTime(time), constraints2D, auto_build = False)       # angular
            self.primitives[-1].addConstraintsSegmTime(0, constraints2D, auto_build = False)                                                # linear

        else: self.primitives[-1].addConstraintsSegmTime(self.pointSegmTime_2_linearSegmTime(time), constraints2D, auto_build = False)

        self.constraints2d = constraints2D

        if auto_build:
            self.generate()



    def pointSegmTime_2_linearSegmTime(self, time: int):
        return time - len(self.primitives[-2].states) + 1

    def pointSegmTime_2_angularSegmTime(self, time: int):
        return time # i mean



    def generate(self):
        self.current_pose = self.last_state.pose.copy()
        self.states: List[MotionState] = []

        self.last_generated_state = self.last_state.copy()


        for i, primitive in enumerate(self.primitives):
    
            # recursively compleate each 
            if primitive.last_state is None:
                self.primitives[i] = self.primitives[i].copy(self.last_generated_state.copy(), self.constraints2d)
            else: self.primitives[i] = self.primitives[i].copy(self.last_generated_state.copy())

            # generate the values for each
            self.primitives[i].generate()

            # combine states from the primitive into one state
            self.states += self.primitives[i].get_all()
            self.total_time += self.primitives[i].total_time

            self.last_generated_state = self.primitives[i].states[-1]
        


        # get the end time
        self.total_time = len(self.states)
        self.end_time = self.states[-1].time
        self.built = True
    
    

    def motionFromProfileState(self, t: int, profile_state: ProfileState) -> MotionState:
        pass # the primitives do this for you



    def getAction(self) -> MotionAction:
        return MotionAction.TO_POINT
    
    def copy(self, last_state: MotionState, constraints2d: Constraints2D):
        return PointSegment(last_state,
                            self.kinematics,
                            constraints2d,
                            self.point,
                            self.tangent,
                            self.reversed)
    