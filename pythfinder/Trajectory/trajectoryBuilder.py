from pythfinder.Trajectory.Control.feedforward import *
from pythfinder.Trajectory.Control.feedback import *
from pythfinder.Trajectory.Markers.generic import *
from pythfinder.Trajectory.trajectory import *
from pythfinder.Trajectory.Segments import *

# for marker sorting
type_priority = {
    'constraints': 0,
    'interrupt': 1,
    'function': 2
}


class TrajectoryBuilder():
    def __init__(self,
                 sim: Simulator,
                 start_pose: Pose | None = None,
                 preset: int = 1):
        
        self.sim = sim
        self.robot = sim.robot

        self.preset_nr = preset

        self.sim.presets.on(self.preset_nr)
        self.preset = self.sim.presets.get(self.preset_nr)
        

        
        if preset is None:
            self.kinematics = self.sim.constants.kinematics
            self.CONSTRAINTS = self.sim.constants.constraints
        
        else:
            self.kinematics = self.preset.preset_constants.kinematics
            self.CONSTRAINTS = self.preset.preset_constants.constraints

            self.sim.constants.REAL_MAX_VEL = self.preset.preset_constants.REAL_MAX_VEL
            self.sim.constants.MAX_POWER = self.preset.preset_constants.MAX_POWER

        self.sim.constants.kinematics = self.kinematics.copy()
        self.sim.constants.constraints = self.CONSTRAINTS.copy()



        self.START_POSE = Pose() if start_pose is None else start_pose

        self.segments: List[MotionSegment] = []
        self.relative_markers: List[Marker] = []
        self.final_markers: List[FunctionMarker] = []
        self.absolute_markers: List[ConstraintsMarker] = []

        self.last_state = MotionState()

        self.pose = self.START_POSE

        self.states: List[MotionState] = []
        self.TRAJ_TIME = 0

    

    def inLineCM(self, cm: float):
        if self.__isEligibleToCombineLinear(cm): # combine consecutive line segments
            last_linear_sgm: LinearSegment = self.segments[-1]
            self.segments[-1] = last_linear_sgm.addCM(cm)

            return self

        self.segments.append(LinearSegment(last_state = None,
                                           constraints = self.CONSTRAINTS.linear,
                                           point_cm = cm)) # calculate the point when building the trajectory
        self.relative_markers.append(None)

        return self
    
    def wait(self, ms: int):
        ms = abs(ms)
        if self.__isEligibleToCombineWait(ms):
            last_wait_sgm: WaitSegment = self.segments[-1]
            self.segments[-1] = last_wait_sgm.addMS(ms)
            
            return self
        
        self.segments.append(WaitSegment(last_state = None,
                                         ms = ms))
        self.relative_markers.append(None)

        return self

    def turnToDeg(self, deg: float, reversed: bool = False):
        self.segments.append(AngularSegment(last_state = None,
                                            constraints = self.CONSTRAINTS.angular,
                                            kinematics = self.kinematics,
                                            angle_deg = deg,
                                            reversed = reversed))
        self.relative_markers.append(None)

        return self



    def toPoint(self, point: Point, reversed: bool = False):
        self.segments.append(PointSegment(last_state = None,
                                          kinematics = self.kinematics,
                                          constraints2d = self.CONSTRAINTS,
                                          point = point,
                                          tangent = False,
                                          reversed = reversed))
        self.relative_markers.append(None)

        return self

    def toPointTangentHead(self, point: Point, reversed: bool = False):
        self.segments.append(PointSegment(last_state = None,
                                          kinematics = self.kinematics,
                                          constraints2d = self.CONSTRAINTS,
                                          point = point,
                                          tangent = True,
                                          reversed = reversed))
        self.relative_markers.append(None)

        return self
    


    def toPose(self, pose: Pose, reversed: bool = False):
        self.segments.append(PoseSegment(last_state = None,
                                         kinematics = self.kinematics,
                                         constraints2d = self.CONSTRAINTS,
                                         pose = pose.norm(),
                                         tangent = False,
                                         linear_head = False,
                                         reversed = reversed))
        self.relative_markers.append(None)

        return self

    def toPoseTangentHead(self, pose: Pose, reversed: bool = False):
        self.segments.append(PoseSegment(last_state = None,
                                         kinematics = self.kinematics,
                                         constraints2d = self.CONSTRAINTS,
                                         pose = pose.norm(),
                                         tangent = True,
                                         linear_head = False,
                                         reversed = reversed))
        self.relative_markers.append(None)

        return self

    def toPoseLinearHead(self, pose: Pose, reversed: bool = False):
        self.segments.append(PoseSegment(last_state = None,
                                         kinematics = self.kinematics,
                                         constraints2d = self.CONSTRAINTS,
                                         pose = pose.norm(),
                                         tangent = False,
                                         linear_head = True,
                                         reversed = reversed))
        self.relative_markers.append(None)

        return self



    def addRelativeDisplacementConstraints(self, cm: float, constraints2d: Constraints2D):
        marker = (ConstraintsMarker(time = None,
                                    displacement = cm,
                                    constraints = constraints2d,
                                    relative = True))
    
        self.__addRelativeMarker(marker)
        return self

    def addRelativeTemporalConstraints(self, ms: int, constraints2d: Constraints2D):
        marker = (ConstraintsMarker(time = ms,
                                    displacement = None,
                                    constraints = constraints2d,
                                    relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def addRelativeDisplacementMarker(self, cm: float, fun = idle):
        marker = (FunctionMarker(time = None,
                                displacement = cm,
                                function = fun,
                                relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def addRelativeTemporalMarker(self, ms: int, fun = idle):
        marker = (FunctionMarker(time = ms,
                                displacement = None,
                                function = fun,
                                relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def interruptDisplacement(self, cm: float):
        marker = (InterruptMarker(time = None,
                                  displacement = cm,
                                  relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def interruptTemporal(self, ms: float):
        marker = (InterruptMarker(time = ms,
                                  displacement = None,
                                  relative = True))
        
        self.__addRelativeMarker(marker)
        return self



    def addDisplacementMarker(self, cm: float, fun = idle):
        self.final_markers.append(FunctionMarker(time = None,
                                                 displacement = cm,
                                                 function = fun,
                                                 relative = False))
        return self
    
    def addTemporalMarker(self, ms: int, fun = idle):
        self.final_markers.append(FunctionMarker(time = ms,
                                                 displacement = None,
                                                 function = fun,
                                                 relative = False))
        return self



    def build(self) -> Trajectory:

        self.last_state = MotionState(pose = self.START_POSE)
        self.pose = self.START_POSE.copy()

        self.states = []
        self.segment_number = len(self.segments)
        self.TRAJ_TIME = 0


        for i in range(self.segment_number):
            sgm: MotionSegment = self.segments[i]
            markers: List[Marker] | None = self.relative_markers[i]

            # recursively compleate each 
            if sgm.last_state is None:
                sgm: MotionSegment = sgm.copy(self.last_state.copy(), self.CONSTRAINTS)

            # generate the values for each
            sgm.generate()

            if markers is not None:
                _, sgm = self.__processRelativeMarkers(markers, sgm)

            # combine states from the primitive into one state
            self.states += sgm.get_all()
            self.TRAJ_TIME += sgm.total_time

            self.last_state = sgm.states[-1]
        

        self.__processFinalFunctionMarkers()
        return Trajectory(self.sim, self.states, self.final_markers)


        
    def __addRelativeMarker(self, marker: Marker):
        if self.relative_markers[-1] is None:
            self.relative_markers[-1] = [marker]
        else: self.relative_markers[-1].append(marker)



    def __markerPriority(self, marker: Marker):
        class_name = marker.__class__.__name__.lower()

        for key in type_priority.keys():    # loop through the priority dictionary
            if key in class_name:           # check if the string is in the class name
                return type_priority[key]   # get the aferent value
            
        return float('inf')                 # Fallback if no type found
    
    def __markerSortKey(self, marker: Marker):
        priority = self.__markerPriority(marker)
        is_displacement = 0 if marker.displacement is not None else 1
        value = marker.time if marker.time is not None else marker.displacement

        return (priority,                               # sort by priority
                is_displacement,                        # displacement in front of time
                value if value >= 0 else float('inf'),  # put negatives in the back 
                value)                                  # normal sort, by value
    
    def __sortMarkers(self, markers: List[Marker]) -> List[Marker]:
        return sorted(markers, 
                      key = self.__markerSortKey) 



    def __processNegativeIntoPositiveDisplacement(self, markers: List[Marker], segment: MotionSegment) -> List[Marker]:
        remove = []
        removed = 0

        for i in range(len(markers)):
            marker = markers[i]

            if marker.displacement is None: continue
            if marker.displacement < 0:
                positive = round(segment.states[-1].displacement + marker.displacement, 3)

                if positive >= segment.states[0].displacement:    # check if it's still in the segment
                    marker.displacement = positive   # if so, update marker
                else: 
                    remove.append(i)                 # else remove marker, because it's impossible
                    
                    print("\n\nyour displacement marker with value {0} is outside".format(marker.displacement))
                    print("of the segment by {0}cm. It will be discarded".format(segment.states[0].displacement - positive))
            
        for index in remove:
            markers.pop(index - removed)
            removed += 1
            
        return markers

    def __processRelativesIntoAbsolutesDisplacement(self, markers: List[Marker], segment: MotionSegment) -> List[Marker]:
        for i in range(len(markers)):

            if markers[i].displacement is not None:
                    if markers[i].displacement >= 0:
                        markers[i].displacement = round(markers[i].displacement + segment.states[0].displacement, 3)
        
        return markers



    def __findDisplacementFromSegmTime(self, time: int, segment: MotionSegment) -> float:
        state = segment.getSegmTime(time)

        if state is None: return None
        return state.displacement

    def __findSegmTimeFromDisplacement(self, displacement: float, segment: MotionSegment) -> int:
        if not inOpenInterval(displacement, 
                              left = segment.states[0].displacement, 
                              right = segment.states[-1].displacement):
            return None
        
        return binary_search(displacement, segment.states, "displacement")[0]
    


    def __separateMarkersByType(self, markers: List[Marker]) -> Tuple[list]:
        constraints_markers = [m for m in markers if isinstance(m, ConstraintsMarker)]
        interrupt_markers = [m for m in markers if isinstance(m, InterruptMarker)]
        function_markers = [m for m in markers if isinstance(m, FunctionMarker)]

        return (markers, constraints_markers, interrupt_markers, function_markers)

    def __separateMarkersByValue(self, markers: List[Marker]) -> Tuple[list]:
        displacement = [m for m in markers if m.displacement is not None]
        temporal = [m for m in markers if m.time is not None]

        return (markers, temporal, displacement)



    def __findTheFirstInDisplacementOrder(self, markers: List[Marker], segment: MotionSegment) -> int:
        min_disp = math.inf
        min_index = -1

        for i in range(len(markers)):
            marker = markers[i]

            if marker.displacement is None:
                current_disp = self.__findDisplacementFromSegmTime(marker.time, segment)
            else: current_disp = marker.displacement

            if current_disp is None: # marker is not in the segment
                continue

            if current_disp < min_disp:
                min_disp = current_disp
                min_index = i
        
        return min_index



    def __processRelativeConstraints(self, markers: List[ConstraintsMarker], segment: MotionSegment) -> MotionSegment:
        while markers:
            index = self.__findTheFirstInDisplacementOrder(markers, segment)

            the_chosen_one = markers.pop(index)
            time = (the_chosen_one.time if the_chosen_one.time is not None else
                    self.__findSegmTimeFromDisplacement(the_chosen_one.displacement, segment))
            
            if not segment.timeInSegmentSegmTime(time): # marker is not in the segment
                self.__printMarkerNotInSegmentError(the_chosen_one, segment)
                continue

            self.CONSTRAINTS = the_chosen_one.constraints
            segment.addConstraintsSegmTime(time, the_chosen_one.constraints)
            
        
        return segment
    
    def __processRelativeInterrupt(self, markers: List[InterruptMarker], segment: MotionSegment) -> MotionSegment:
        # use just the earliest interrupter, obviously
        # earliest in the segment, obviously
        marker_found = False

        while not marker_found and markers:
            effective = self.__findTheFirstInDisplacementOrder(markers, segment)

            the_chosen_one = markers.pop(effective)
            time = (the_chosen_one.time if the_chosen_one.time is not None else
                    self.__findSegmTimeFromDisplacement(the_chosen_one.displacement, segment))
            
            if not segment.timeInSegmentSegmTime(time): # marker is not in the segment
                self.__printMarkerNotInSegmentError(the_chosen_one, segment)
                continue

            segment.interruptSegmTime(time)
            marker_found = True
        

        markers = []
        return segment

    def __processRelativeFunction(self, markers: List[FunctionMarker], segment: MotionSegment):
        while markers:
            current = markers.pop()
            time = (current.time if current.time is not None else
                    self.__findSegmTimeFromDisplacement(current.displacement, segment))
            
            if not segment.timeInSegmentSegmTime(time): # marker is not in the segment
                self.__printMarkerNotInSegmentError(current, segment)
                continue

            self.final_markers.append(FunctionMarker(time = segment.states[time].time,
                                                        function = current.function))
        
        return segment


    # big boss function
    def __processRelativeMarkers(self, markers: List[Marker], segment: MotionSegment):
        markers = self.__processRelativesIntoAbsolutesDisplacement(markers, segment)
        markers = self.__processNegativeIntoPositiveDisplacement(markers, segment)
        markers = self.__sortMarkers(markers)

        # now we are working with relative time and absolute displacement

        markers, constraints, interrupt, function = self.__separateMarkersByType(markers)
        segment = self.__processRelativeConstraints(constraints, segment)
        segment = self.__processRelativeInterrupt(interrupt, segment)
        self.__processRelativeFunction(function, segment)

        return markers, segment

    def __processFinalFunctionMarkers(self):
        self.__processNegativeIntoPositiveAll()
        self.__transformDisplacementIntoTemporal()
        self.__sortFinalFunctionMarkers()

    

    def __processNegativeIntoPositiveAll(self):
        remove = []
        removed = 0

        for i in range(len(self.final_markers)):
            marker = self.final_markers[i]

            if marker.time is None: 
                if marker.displacement < 0:
                    positive = round(self.states[-1].displacement + marker.displacement, 3)

                    if positive >= 0:                    # check if it's still in the segment
                        marker.displacement = positive   # if so, update marker
                    else: 
                        remove.append(i)                 # else remove marker, because it's impossible
                        self.__printMarkerNotInTrajectoryError(marker)
            
            else:
                if marker.time < 0:
                    positive = self.states[-1].time + marker.time

                    if positive >= 0:
                        marker.time = positive
                    else:
                        remove.append(i)
                        self.__printMarkerNotInTrajectoryError(marker)
                        
        for index in remove:
            self.final_markers.pop(index - removed)
            removed += 1

    def __transformDisplacementIntoTemporal(self):
        for marker in self.final_markers:
            if marker.displacement is None: 
                continue

            index, _ = binary_search(marker.displacement, self.states, "displacement")

            marker.displacement = None
            marker.time = self.states[index].time

    def __sortFinalFunctionMarkers(self):
        self.final_markers = self.__sortMarkers(self.final_markers)



    def __isEligibleToCombineLinear(self, cm: float) -> bool:
        if len(self.segments) == 0:
            return False
        
        if not isinstance(self.segments[-1], LinearSegment):
            return False
        
        if isinstance(self.segments[-1].target, Point):
            return False
        
        if not signum(cm) == signum(self.segments[-1].target):
            return False
        
        return True

    def __isEligibleToCombineWait(self, ms: float) -> bool:
        if len(self.segments) == 0:
            return False
        
        if not isinstance(self.segments[-1], WaitSegment):
            return False
        
        return True



    def __printMarkersDebugging(self, markers: List[Marker]):
        print("\n\n")

        for marker in markers:
            class_type = marker.__class__.__name__

            print("{0}: time ({1})   displacement ({2})"
                  .format(class_type,
                          marker.time,
                          marker.displacement))
    
    def __printMarkerNotInSegmentError(self, marker: Marker, segment: MotionSegment):
        print("\n\nthere is no motion state at {0}{1} in this segment"
                  .format(marker.time if marker.time is not None else round(marker.displacement - segment.states[0].displacement, 2),
                          "ms" if marker.time is not None else "cm"))
        print("the supported range is: ({0}, {1}) {2}"
                  .format(0, 
                          
                                len(segment.states) - 1 
                          if marker.time is not None else 
                                round(segment.states[-1].displacement - segment.states[0].displacement, 2),

                          "ms" if marker.time is not None else "cm"))

    def __printMarkerNotInTrajectoryError(self, marker: Marker):
        print("\n\nthere is no motion state at {0}{1} in this trajectory"
                  .format(marker.time if marker.time is not None else round(marker.displacement, 2),
                          "ms" if marker.time is not None else "cm"))
        print("the supported range is: ({0}, {1}) {2}"
                  .format(0, 
                                len(self.states) - 1 
                          if marker.time is not None else 
                                round(self.states[-1].displacement, 2),

                          "ms" if marker.time is not None else "cm"))

    def __writeSegmentInFileDebugging(self, segment: MotionSegment, file_name: str = "test"):
        with open("{0}.txt".format(file_name), "w") as f:
            for state in segment.states:
                f.write("{0} {1} {2} {3}\n".format(round(state.velocities.getVelocityMagnitude(), 1),
                                             state.velocities.ANG_VEL,
                                             state.time,
                                             round(state.displacement, 3)))
    
