from ev3sim.Components.Controllers.PIDCoefficients import *
from ev3sim.Components.Controllers.PIDController import *
from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constrains import *
from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.kinematics import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.splines import *

from enum import Enum, auto
import threading

class MotionAction(Enum):
    LINE = auto()
    TO_POINT = auto()
    TO_POSE = auto()
    TURN = auto()

    WAIT = auto()
    REL_MARKER = auto()

    SPLINE = auto()

class MarkerType(Enum):
    TEMPORAL = auto()
    DISPLACEMENT = auto()



class Marker():
    def __init__(self, val: float, fun, type: MarkerType, rel):
        self.value = val
        self.type = type
        self.fun = fun
        self.rel = rel
    
    def do(self):
        try: self.fun()
        except: print("\n\nexcuse me, what? \nprovide a method in the 'Marker' object with the value '{0}' and type '{1}'"
                      .format(self.value, self.type.name))



class MotionState():
    def __init__(self, time: int, velocities: tuple, 
                 displacement: float,
                 pose: Pose):

        self.velocities = velocities # [-100, 100] ; tuple -> (left, right)

        self.time = time # ms (int)
        self.displacement = displacement
        self.pose = pose

class MotionSegment():
    def __init__(self, action: MotionAction, value: float, 
                 constrains: Constrains = None):
        self.action = action 
        self.constrains = constrains
        self.value = value
        self.states = {}

        self.start_time = None
        self.end_time = None
        self.total_time = 0

        self.runnable = True
        self.running = False
    
    def add(self, state: MotionState):
        if self.start_time is None:
            self.start_time = state.time
        self.end_time = state.time

        self.states[state.time] = state
    
    def get(self, time: int):
        return self.states[time]
    
    def build(self):
        try: self.total_time = self.end_time - self.start_time
        except: self.total_time = 0
    
    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    def kill(self):
        self.runnable = False

class Trajectory():

    def __init__(self, start_pose: Pose, end_pose: Pose, 
                 segments: List[MotionSegment], time: float,
                 markers: List[Marker]):
        
        self.head_controller = PIDController(PIDCoefficients(kP = kP_head, kD = kD_head, kI = 0))
        self.markers = markers

        self.start_pose = start_pose
        self.end_pose = end_pose

        self.trajectoryTime = time
        self.segments = segments

        self.segment_number = len(self.segments)
        self.perfect_increment = 60



    def follow(self, sim: Simulator, perfect: bool = False, wait = True) -> None:
        if self.trajectoryTime == 0: #empty trajectory
            return 0
        
        sim.robot.trail.draw_trail.set(True)
        sim.constants.ERASE_TRAIL.set(False)
        sim.manual_control.set(False)

        sim.robot.setPoseEstimate(self.start_pose)
        sim.robot.zeroDistance()

        self.marker_iterator = 0
        self.iterator = 0

        if wait:
            for _ in range(101):
                sim.update()

        if perfect:
            sim.robot.target_head = self.__perfectFollow(sim)
            sim.robot.setPoseEstimate(self.end_pose)
        else: 
            sim.robot.target_head = self.__realFollow(sim)
            sim.robot.setVelocities(0, 0)
        
        #markers from last miliseconds or beyond the time limit
        while self.marker_iterator < len(self.markers):
            sim.update()
            marker = self.markers[self.marker_iterator]

            if marker.value > self.trajectoryTime:
                print('The marker number {0} exceded the time limit {1}ms with {2}ms'
                      .format(self.marker_iterator + 1, self.trajectoryTime, marker.value - self.trajectoryTime))

            threading.Thread(target = marker.do).start()
            self.marker_iterator += 1

        sim.manual_control.set(True)
        sim.robot.trail.draw_trail.set(False)
        sim.constants.ERASE_TRAIL.set(True)

                            

    def __perfectFollow(self, sim: Simulator) -> None:
        past_angle = None
        time = 0

        segment: MotionSegment = self.segments[self.iterator]
        marker: Marker = (Marker(0, 0, MarkerType.TEMPORAL, False) 
                            if len(self.markers) == 0 else
                          self.markers[self.marker_iterator])
        segment_time = segment.total_time


        while self.iterator < self.segment_number:
            sim.update()

            if time >= marker.value and self.marker_iterator < len(self.markers):
                threading.Thread(target = marker.do).start()
                self.marker_iterator += 1

                try: marker = self.markers[self.marker_iterator]
                except: pass
            
            while time > segment_time:
                self.iterator += 1
                
                if self.iterator == self.segment_number:
                    return state.pose.head
                
                segment = self.segments[self.iterator]
                segment_time += segment.total_time
                
            try:
                state: MotionState = segment.get(time)
            except: continue

            if not past_angle is None:
                if abs(state.pose.head - sim.robot.pose.head) > 1:
                    turnDeg(state.pose.head, sim)
            else: past_angle = state.pose.head

            time += self.perfect_increment
            sim.robot.setPoseEstimate(state.pose)



    def __realFollow(self, sim: Simulator) -> None:
        past_angle = None
        start_time = getTimeMs()

        segment: MotionSegment = self.segments[self.iterator]
        marker: Marker = (Marker(0, 0, MarkerType.TEMPORAL, False) 
                            if len(self.markers) == 0 else
                          self.markers[self.marker_iterator])
        segment_time = segment.total_time


        while self.iterator < self.segment_number:
            sim.update()
            time = getTimeMs() - start_time

            if time >= marker.value and self.marker_iterator < len(self.markers):
                threading.Thread(target = marker.do).start()
                self.marker_iterator += 1
                
                try: marker = self.markers[self.marker_iterator]
                except: pass
                           
            while time > segment_time:
                self.iterator += 1
                
                if self.iterator == self.segment_number:
                    return state.pose.head
                
                segment = self.segments[self.iterator]
                segment_time += segment.total_time
                
            try:
                state: MotionState = segment.get(time)
            except: continue

            VEL, ANG_VEL = state.velocities

            if not past_angle is None:
                if abs(state.pose.head - sim.robot.pose.head) > 1:
                    beforeTurn = getTimeMs()

                    turnDeg(state.pose.head, sim)

                    past_angle = state.pose.head
                    start_time += getTimeMs() - beforeTurn + 1
            else: past_angle = state.pose.head

            sim.robot.setVelocities(VEL, ANG_VEL)




class TrajectoryBuilder():
    def __init__(self, start_pose: Pose = Pose(), constrains: Constrains = None):
        self.splines = []
        self.markers = []
        self.segments = []
        self.linear_profiles = []
        self.angular_profiles = []

        self.distance = 0
        self.constrains = Constrains() if constrains is None else constrains

        self.start_pose = start_pose
        self.current_pose = start_pose.copy()

        self.k = TankKinematics()

        self.TRAJ_DISTANCE = 0
        self.TRAJ_TIME = 0
        self.iterator = 0

    def createProfile(self, boolean: bool):
        if not boolean:
            return 0

        self.linear_profiles.append(MotionProfile(0, self.distance, self.constrains))

        self.distance = 0





    def inLineCM(self, cm: float):
        self.createProfile(boolean = (not signum(cm) == signum(self.distance) 
                                        and not self.distance == 0))
        
        self.segments.append(MotionSegment(MotionAction.LINE, cm))
        self.distance += cm

        return self
    
    def toPoint(self, point: Point):
        self.createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POINT, point))

        return self

    def toPose(self, pose: Pose):
        self.createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POSE, pose))

        return self
 
    def turnDeg(self, deg: float):
        self.createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TURN, deg))

        return self



    def wait(self, ms: int):
        self.createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.WAIT, ms))

        return self

    def addTemporalMarker(self, ms: int, fun):
        ms = 0 if ms < 0 else ms
        self.markers.append(Marker(val = ms, fun = fun, rel = False,
                                       type = MarkerType.TEMPORAL))
        return self
    
    def addRelativeTemporalMarker(self, ms: int, fun):
        self.segments.append(MotionSegment(MotionAction.REL_MARKER, 
                                           value = Marker(val = ms, fun = fun, rel = True,
                                                          type = MarkerType.TEMPORAL)))
        
        return self



    # TODO: figure out how to get ang vel from spline
    def inSpline(self, start: Point, end: Point,
                    start_tangent: Point, end_tangent: Point):
        return self



    # TODO: add volatile constrains
    def addConstrainsDisplacement(self, constrains: Constrains, displacement: float):
        return self

    def addConstrainsTemporal(self, constrains: Constrains, time: float):
        return self





    def build(self) -> Trajectory: 
        self.createProfile(boolean = (abs(self.distance) > 0))
        self.segment_number = len(self.segments)

        if self.segment_number == 0 or self.nextSegmentsJustMarkers(start = self.iterator):
            print("\n\ncan't compute an empty trajectory..")
            return Trajectory(self.start_pose, self.start_pose, [], 0, [])

        print("\n\ncalculating trajectory...")
 
        self.TRAJ_DISTANCE = 0
        self.TRAJ_TIME = 0
        self.iterator = 0

        while self.iterator < self.segment_number:
            segment: MotionSegment = self.segments[self.iterator]
            
            if segment.action is MotionAction.LINE:
                self.buildLine(segment)

            elif segment.action is MotionAction.TURN: 
                self.buildTurn(segment)
            
            elif segment.action is MotionAction.WAIT:
                self.buildWait(segment)
            
            elif segment.action is MotionAction.TO_POINT:
                self.buildToPoint(segment)
            
            elif segment.action is MotionAction.TO_POSE:
                self.buildToPose(segment)
            
            elif segment.action is MotionAction.SPLINE:
                self.buildSpline(segment)
            
            elif segment.action is MotionAction.REL_MARKER:
                self.buildMarker(segment)
            
            
            self.iterator += 1
        

        self.TRAJ_TIME -= 1

        print("\n\ndone!")
        print("(FINAL POSE) x:{0} ; y:{1} ; head:{2}".format(round(self.current_pose.x, 2),
                                                             round(self.current_pose.y, 2),
                                                             round(self.current_pose.head, 2)))

        return Trajectory(self.start_pose.copy(), self.current_pose.copy(), 
                          self.segments, self.TRAJ_TIME, self.markers)
    


    def specialCase(self, segment: MotionSegment):
        #account for turning at the end of the trajectory

        for t in range(41):
            segment.add(MotionState(time = self.TRAJ_TIME + t,
                                         displacement = self.TRAJ_DISTANCE,
                                         pose = self.current_pose.copy(),
                                         velocities = (0, 0))
            )
            
        self.TRAJ_TIME += 41
        segment.build()



    def buildLine(self, segment: MotionSegment):
        profile: MotionProfile = self.linear_profiles.pop(0)
        segment_distance = segment.value

        VELOCITY = ANGULAR_VELOCITY = t = 0
        profile_time = int(sToMs(profile.t_total)) + 1 # +1 -> [0, t_total]
        past_distance = 0

        for t in range(profile_time):

            sec = msToS(t)
            distance, velocity = profile.get_dis(sec), profile.get_vel(sec)

            if abs(distance) > abs(segment_distance):
                self.iterator += 1

                segment.build()
                segment = self.segments[self.iterator]

                segment_distance += segment.value
            
            VELOCITY, ANGULAR_VELOCITY = velocity, 0

            delta_distance = distance - past_distance
            self.current_pose.sum(Pose(x = math.cos(self.current_pose.rad()) * delta_distance,
                                       y = math.sin(self.current_pose.rad()) * delta_distance))

            segment.add(MotionState(time = self.TRAJ_TIME + t,
                                    displacement = self.TRAJ_DISTANCE + distance,
                                    pose = self.current_pose.copy(),
                                    velocities = (VELOCITY, ANGULAR_VELOCITY))
            )

            past_distance = distance

        self.TRAJ_TIME += profile_time
        segment.build()
    
    def buildTurn(self, segment: MotionSegment):
        self.current_pose.head = segment.value
        segment.add(MotionState(time = self.TRAJ_TIME,
                                displacement = self.TRAJ_DISTANCE,
                                pose = self.current_pose.copy(),
                                velocities = (0, 0))
        )

        self.TRAJ_TIME += 1

        if self.iterator + 1 == self.segment_number or self.nextSegmentsJustMarkers(start = self.iterator + 1):
            self.specialCase(segment)
        segment.build()
    
    def buildWait(self, segment: MotionSegment):
        waiting_time = segment.value + 1

        for t in range(waiting_time):
            segment.add(MotionState(time = self.TRAJ_TIME + t,
                                    displacement = self.TRAJ_DISTANCE,
                                    pose = self.current_pose.copy(),
                                    velocities = (0, 0))
            )

        self.TRAJ_TIME += waiting_time
        segment.build()
    
    def buildToPoint(self, segment: MotionSegment):
        current = self.current_pose.point()
        target: Point = segment.value

        head = normalizeDegrees(toDegrees(target.subtract(current).atan2()))
        displacement = target.subtract(current).hypot()

        self.segments[self.iterator] = MotionSegment(MotionAction.TURN, head)
        self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE, displacement))
        self.linear_profiles.insert(0, MotionProfile(0, displacement, self.constrains))

        self.segment_number += 1
        self.iterator -= 1
    
    def buildToPose(self, segment: MotionSegment):
        current = self.current_pose.point()
        target: Point = segment.value.point()

        head = normalizeDegrees(toDegrees(target.subtract(current).atan2()))
        displacement = target.subtract(current).hypot()

        self.segments[self.iterator] = MotionSegment(MotionAction.TURN, head)
        self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE, displacement))
        self.segments.insert(self.iterator + 2, MotionSegment(MotionAction.TURN, segment.value.head))
        self.linear_profiles.insert(0, MotionProfile(0, displacement, self.constrains))

        self.segment_number += 2
        self.iterator -= 1

    def buildSpline(self, segment: MotionSegment):
        return 0
    
    def buildMarker(self, segment: MotionSegment):
        marker: Marker = segment.value

        match marker.type:
            case MarkerType.TEMPORAL:
                time = 0 if self.TRAJ_TIME + marker.value - 1 < 0 else self.TRAJ_TIME + marker.value - 1
                time = time + 1 if self.TRAJ_TIME == 0 else time

                if len(self.markers) == 0 or time >= self.markers[-1].value:
                    self.markers.append(Marker(val = time, fun = marker.fun, rel = False,
                                                type = MarkerType.TEMPORAL))
                else:
                    for i in range(len(self.markers)):
                        if time <= self.markers[i].value:
                            self.markers.insert(i + 1, Marker(val = time, fun = marker.fun, rel = False,
                                                            type = MarkerType.TEMPORAL))
                

                self.segments.pop(self.iterator)
                self.segment_number -= 1
                self.iterator -= 1

            case MarkerType.DISPLACEMENT:
                pass
            case _:
                pass



    def nextSegmentsJustMarkers(self, start):
        for index in range(start, self.segment_number):
            if self.segments[index].action is not MotionAction.REL_MARKER:
                return False
        
        return True