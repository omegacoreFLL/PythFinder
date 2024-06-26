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
                 start_constraints: Constraints2D | None = None):
        
        self.sim = sim
        self.robot = sim.robot

        self.START_POSE = Pose() if start_pose is None else start_pose
        self.CONSTRAINTS = self.robot.constraints if start_constraints is None else start_constraints

        self.segments: List[MotionSegment] = []
        self.absolute_markers: List[Marker] = []
        self.relative_markers: List[Marker] = []

        self.last_state = MotionState()

        self.pose = self.START_POSE

        self.states: List[MotionState] = []
        self.TRAJ_TIME = 0

    

    def inLineCM(self, cm: float):
        self.segments.append(LinearSegment(last_state = None,
                                           constraints = self.CONSTRAINTS.linear,
                                           point_cm = cm)) # calculate the point when building the trajectory
        self.relative_markers.append(None)

        return self
    


    def addRelativeDisplacementConstraints(self, disp: float, constraints2d: Constraints2D):
        marker = (ConstraintsMarker(time = None,
                                    displacement = disp,
                                    constraints = constraints2d,
                                    relative = True))
    
        self.__addRelativeMarker(marker)
        return self

    def addRelativeTemporalConstraints(self, time: int, constraints2d: Constraints2D):
        marker = (ConstraintsMarker(time = time,
                                    displacement = None,
                                    constraints = constraints2d,
                                    relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def addRelativeDisplacementMarker(self, disp: float, fun):
        marker = (FunctionMarker(time = None,
                                displacement = disp,
                                function = fun,
                                relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def addRelativeTemporalMarker(self, time: int, fun):
        marker = (FunctionMarker(time = time,
                                displacement = None,
                                function = fun,
                                relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def interruptDisplacement(self, disp: float):
        marker = (InterruptMarker(time = None,
                                  displacement = disp,
                                  relative = True))
        
        self.__addRelativeMarker(marker)
        return self

    def interruptTemporal(self, time: float):
        marker = (InterruptMarker(time = time,
                                  displacement = None,
                                  relative = True))
        
        self.__addRelativeMarker(marker)
        return self



    def build(self) -> Trajectory:

        self.last_state = MotionState(0, ChassisState(), 0, self.START_POSE)
        self.pose = self.START_POSE

        self.states = []
        self.segment_number = len(self.segments)
        self.TRAJ_TIME = 0


        for i in range(self.segment_number):
            sgm: MotionSegment = self.segments[i]
            markers: List[Marker] | None = self.relative_markers[i]

            # recursively compleate each 
            if sgm.last_state is None:
                sgm: MotionSegment = sgm.copy(self.last_state)

            # generate the values for each
            sgm.generate()

            if markers is not None:
                _, sgm = self.__processRelativeMarkers(markers, sgm)

            # combine states from the primitive into one state
            self.states += sgm.get_all()
            self.TRAJ_TIME += sgm.total_time

            self.last_state = sgm.states[-1]
        
        return Trajectory(self.sim, self.states, self.absolute_markers)


        
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
 
    def __processNegativeDisplacement(self, markers: List[Marker], segment: MotionSegment) -> List[Marker]:
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


    
    def __processRelativeMarkers(self, markers: List[Marker], segment: MotionSegment):
        markers = self.__processNegativeDisplacement(markers, segment)
        markers = self.__sortMarkers(markers)

        self.__printMarkersDebugging(markers)
        return markers, segment

    def __printMarkersDebugging(self, markers: List[Marker]):
        print("\n\n")

        for marker in markers:
            class_type = marker.__class__.__name__

            print("{0}: time ({1})   displacement ({2})"
                  .format(class_type,
                          marker.time,
                          marker.displacement))