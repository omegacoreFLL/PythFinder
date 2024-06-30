from pythfinder.Trajectory.Control.feedforward import *
from pythfinder.Trajectory.Segments.Primitives import *

class PoseSegment(MotionSegment):
    def __init__(self, 
                 last_state: MotionState,
                 kinematics: Kinematics,
                 constraints2d: Constraints2D,
                 pose: Pose,                   # target point
                 tangent: bool = False,         # sets the heading tangent to the line
                 linear_head: bool = False,     # linear + angular velocities at the same time
                 reversed: bool = False         # reverses the heading by 180°
    ):
        self.last_state = last_state
        self.kinematics = kinematics
        self.constraints2d = constraints2d
        self.pose = pose

        self.tangent = tangent
        self.linear_head = linear_head
        self.reversed = reversed


        if last_state is None:
            return None
                
        super().__init__(last_state)

        self.last_generated_state = 0
        
        # store the primitive segments making up a pose segment
        self.primitives: List[MotionSegment] = []

        # non-holonomic chassis require a heading tangent to the path
        if self.kinematics.getType() is ChassisType.NON_HOLONOMIC:
            self.tangent = True
            self.linear_head = False
        
        head = self.last_state.pose.head

        if self.tangent and not self.linear_head:
            # get the angle of the line
            head = normalizeDegrees(toDegrees((self.pose.point() - self.last_state.pose.point()).atan2()))

        # reverse the heading, holonomic or non-holonomic
        if reversed:
            head = normalizeDegrees(180 + head)

        # first primitive in this case would be going reverse / tangent (or no turn at all)
        self.primitives.append(AngularSegment(None, None, kinematics, head))
        self.primitives.append(LinearSegment(None, None, self.pose.point()))
        self.primitives.append(AngularSegment(None, None, kinematics, self.pose.head))

        self.first_angular_states: List[MotionState] = []
        self.linear_states: List[MotionState] = []
        self.last_angular_states: List[MotionState] = []


    
    def addConstraintsTrajTime(self, time: int, constraints2D: Constraints2D, auto_build: bool = True):
        self.addConstraintsSegmTime(self.trajTime_2_segmTime(time), constraints2D, auto_build)

    def addConstraintsSegmTime(self, time: int, constraints2D: Constraints2D, auto_build: bool = True):
        if not self.built:
            print("\n\ncan't add constraints without calling the 'generate' method")
            return None
        
        time = self.normalizeSegmTime(time)

        linear_nr = len(self.linear_states)
        first_angular_nr = len(self.first_angular_states)
        last_angular_nr = len(self.last_angular_states)

        if time < first_angular_nr:       # all 3
                self.primitives[0].addConstraintsSegmTime(time, constraints2D)
                self.primitives[1].addConstraintsSegmTime(0, constraints2D)
                self.primitives[2].addConstraintsSegmTime(0, constraints2D)

        elif not self.linear_head:                      # segments are separated
            if time < linear_nr:          # last 2
                self.primitives[1].addConstraintsSegmTime(time - first_angular_nr, constraints2D)
                self.primitives[2].addConstraintsSegmTime(0, constraints2D)

            if time < last_angular_nr:    # last 1
                self.primitives[2].addConstraintsSegmTime((time - first_angular_nr - linear_nr), constraints2D)
        
        else:                                           # segments are combined
                relative_time = time - first_angular_nr

                if relative_time < linear_nr:
                    self.primitives[1].addConstraintsSegmTime(relative_time, constraints2D)
                if relative_time < last_angular_nr:
                    self.primitives[2].addConstraintsSegmTime(relative_time, constraints2D)


        self.constraints2d = constraints2D

        if auto_build:
            self.generate()

    



    def generate(self):
        self.current_pose = self.last_state.pose.copy()
        self.last_generated_state = self.last_state.copy()

        self.states: List[MotionState] = []

        self.first_angular_states: List[MotionState] = []
        self.linear_states: List[MotionState] = []
        self.last_angular_states: List[MotionState] = []


        for i, primitive in enumerate(self.primitives):
            
            if primitive.last_state is None:
                self.primitives[i] = self.primitives[i].copy(self.last_generated_state.copy(), self.constraints2d)
            else: self.primitives[i] = self.primitives[i].copy(self.last_generated_state.copy())

            # generate the values for each
            self.primitives[i].generate()

            match i:
                case 0: self.first_angular_states = self.primitives[i].get_all()
                case 1: self.linear_states = self.primitives[i].get_all()
                case 2: self.last_angular_states = self.primitives[i].get_all()

            self.total_time += self.primitives[i].total_time
            self.last_generated_state = self.primitives[i].states[-1]
        

        if self.linear_head:
            combined = self.__combineLinearAndAngular()
            self.states = self.first_angular_states + combined
        else: 
            self.states = self.first_angular_states + self.linear_states + self.last_angular_states

        # get the end time
        self.total_time = len(self.states)
        self.end_time = self.states[-1].time
        self.built = True
    
    

    def __combineLinearAndAngular(self):
        combined: List[MotionState] = [] 

        ang_nr = len(self.last_angular_states)
        ang_start_pose = self.last_angular_states[0].pose

        for i, linear_state in enumerate(self.linear_states):
            if i < ang_nr:
                combined.append(MotionState(time = linear_state.time,
                                            field_vel = ChassisState(linear_state.velocities.VEL,
                                                                     self.last_angular_states[i].velocities.ANG_VEL),
                                            displacement = linear_state.displacement,
                                            pose = (linear_state.pose +
                                                    self.last_angular_states[i].pose -
                                                    ang_start_pose)))
            else: 
                combined.append(MotionState(time = linear_state.time,
                                            field_vel = linear_state.velocities,
                                            displacement = linear_state.displacement,
                                            pose = (linear_state.pose +
                                                    self.last_angular_states[-1].pose -
                                                    ang_start_pose)))
                
        for i in range(len(combined), ang_nr):
            combined.append(MotionState(time = combined[-1].time + 1,
                                        field_vel = self.last_angular_states[i].velocities,
                                        displacement = self.last_angular_states[i].displacement,
                                        pose = self.last_angular_states[i].pose))

        
        return combined
        
    def motionFromProfileState(self, t: int, profile_state: ProfileState) -> MotionState:
        pass # the primitives do this for you



    def getAction(self) -> MotionAction:
        return MotionAction.TO_POSE
    
    def copy(self, last_state: MotionState, constraints2d: Constraints2D):
        return PoseSegment(last_state,
                           self.kinematics,
                           constraints2d,
                           self.pose,
                           self.tangent,
                           self.linear_head,
                           self.reversed)
    