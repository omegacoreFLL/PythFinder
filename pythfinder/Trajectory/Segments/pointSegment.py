from pythfinder.Trajectory.Control.feedforward import ProfileState
from pythfinder.Trajectory.Segments.Primitives import *
from pythfinder.Trajectory.Segments.Primitives.generic import MotionState

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

        self.last_generated_state = last_state

        if last_state is None:
            return None
        
        super().__init__(last_state)

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
        self.primitives.append(AngularSegment(last_state, constraints2d.angular, kinematics, head))
        self.primitives.append(LinearSegment(None, constraints2d.linear, self.point))
        


    def addConstraintsTrajTime(self, time: int, constraints2D: Constraints2D):
        if not self.built:
            print("\n\ncan't add constraints without calling the 'generate' method")
            return None
        
        if not self.stateFromLinearSegment(self.states[time]):
            self.primitives[-2].addConstraintsTrajTime(time, constraints2D.angular)
        self.primitives[-1].addConstraintsTrajTime(time, constraints2D.linear)


        

    def addConstraintsSegmTime(self, time: int, constraints2D: Constraints2D):
        pass # idk man



    def generate(self):
        self.last_generated_state = self.last_state


        for prm in self.primitives:

            # recursively compleate each 
            if prm.last_state is None:
                prm: MotionSegment = prm.copy(self.last_generated_state)

            # generate the values for each
            prm.generate()

            # combine states from the primitive into one state
            self.states += prm.get_all()
            self.total_time += prm.total_time

            self.last_generated_state = prm.states[-1]


        # get the end time
        self.end_time = self.start_time + self.total_time - 1
        self.built = True
    
    

    def motionFromProfileState(self, t: int, profile_state: ProfileState) -> MotionState:
        pass # the primitives do this for you


    def getAction(self) -> MotionAction:
        return MotionAction.TO_POINT
    
    def copy(self, last_state: MotionState):
        return PointSegment(last_state,
                            self.kinematics,
                            self.constraints2d,
                            self.point,
                            self.tangent,
                            self.reversed)
