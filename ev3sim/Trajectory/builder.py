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
    SET_POSE = auto()

    REL_MARKER = auto()
    INT_MARKER = auto()

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

    class Interruptor():
        def __init__(self, val: float, type: MarkerType):
            self.value = val
            self.type = type



class MotionState():
    def __init__(self, time: int, velocities: tuple, 
                 displacement: float,
                 pose: Pose, turn: bool = False):

        self.velocities = velocities # [-100, 100] ; tuple -> (left, right)

        self.time = time # ms (int)
        self.displacement = displacement
        self.pose = pose

        self.turn = turn
    
    def isLike(self, other): 
        return (self.turn == other.turn
                        and
                self.velocities[0] == other.velocities[0]
                        and
                self.velocities[1] == other.velocities[1]
                        and 
                self.pose.head == other.pose.head)

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
    
    def add(self, state: MotionState):
        if self.start_time is None:
            self.start_time = state.time
        self.end_time = state.time

        self.states[state.time] = state
    
    def get(self, time: int):
        return self.states[time]
    
    def build(self):
        try: self.total_time = self.end_time - self.start_time + 1
        except: self.total_time = 1
    
    def reset(self):
        self.start_time = self.end_time = None
        self.total_time = 0
        self.states = {}
    
    def eraseAllAfter(self, index: int):
        #doesn't really erase the values, just sets the bounds such that
        #   it's not accessible anymore. Deal with it.

        self.end_time = index
        self.build()

        return self.states[index].pose.copy()

    def subtract(self, val: int):

        keys = list(self.states.keys())
        new_states = {}

        for key in keys:
            state: MotionState = self.states[key]
            state.time -= val
            new_states[key - val] = state
        
        self.states = new_states
        self.start_time -= val
    



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
        
        print('\n\nFOLLOWING TRAJECTORY...')
        
        sim.autonomus(Auto.ENTER)
        sim.robot.setPoseEstimate(self.start_pose)

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
                print('\nThe marker number {0} exceded the time limit of {1}ms with {2}ms'
                      .format(self.marker_iterator + 1, self.trajectoryTime, marker.value - self.trajectoryTime))

            threading.Thread(target = marker.do).start()
            self.marker_iterator += 1

        
        print('\n\nTRAJECTORY COMPLETED! ;)')

    def generate(self, file_name: str, steps: int = 1):
        print('\n\nwriting precious values into * {0}.txt * ...'.format(file_name))

        with open('{0}.txt'.format(file_name), "w") as f:
            #first layer --> marker times
            first_string = ''
            for marker in self.markers:
                first_string += '{0} '.format(marker.value)
            
            f.write(first_string + '\n')

            #second layer --> start_pose -- end_pose -- steps

            second_string = '{0} {1} {2} {3} {4} {5} {6}'.format(
                round(self.start_pose.x, 2),
                round(self.start_pose.y, 2),
                round(self.start_pose.head, 2),
                round(self.end_pose.x, 2),
                round(self.end_pose.y, 2),
                round(self.end_pose.head, 2),
                steps
            )

            f.write(second_string + '\n')


            #third layer --> LEFT -- RIGHT -- head -- TURN + nr of consecutive copies

            time = 0
            self.iterator = 0
            self.segment_number = len(self.segments)
            segment: MotionSegment = self.segments[self.iterator]
            segment_time = segment.total_time
            k = TankKinematics()
            
            last_state: MotionState = self.segments[0].states[0]
            appearance = 0

            while self.iterator < self.segment_number:

                while time >= segment_time:
                    self.iterator += 1
                    if self.iterator == self.segment_number:
                        left, right = k.inverseKinematics(last_state.velocities[0], last_state.velocities[1])

                        f.write('{0} {1} {2} {3} '.format(
                                    round(left * 100 / REAL_MAX_VEL, 2),
                                    round(right * 100 / REAL_MAX_VEL, 2),
                                    round(last_state.pose.head, 2),
                                    appearance * 10 + int(last_state.turn)
                                ))
                        print('\n\ndone writing in * {0}.txt * file :o'.format(file_name))
                        return 0
                
                    segment = self.segments[self.iterator]
                    segment_time += segment.total_time
                
                state: MotionState = segment.get(time)

                if last_state.isLike(state):
                    appearance += 1
                else:
                    left, right = k.inverseKinematics(last_state.velocities[0], last_state.velocities[1])

                    f.write('{0} {1} {2} {3} '.format(
                        round(left * 100 / REAL_MAX_VEL, 2),
                        round(right * 100 / REAL_MAX_VEL, 2),
                        round(last_state.pose.head, 2),
                        appearance * 10 + int(last_state.turn)
                    ))

                    last_state = state
                    appearance = 1

                time += steps
            


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
            
            while time >= segment_time:
                self.iterator += 1
                
                if self.iterator == self.segment_number:
                    return state.pose.head
                
                segment = self.segments[self.iterator]
                segment_time += segment.total_time

            state: MotionState = segment.get(time)

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
                           
            while time >= segment_time:
                self.iterator += 1
                
                if self.iterator == self.segment_number:
                    return state.pose.head
                
                
                segment = self.segments[self.iterator]
                segment_time += segment.total_time
                
            state: MotionState = segment.get(time)

            VEL, ANG_VEL = state.velocities

            if not past_angle is None:
                if abs(state.pose.head - sim.robot.pose.head) > 1 and state.turn:
                    beforeTurn = getTimeMs()

                    turnDeg(state.pose.head, sim)

                    past_angle = state.pose.head
                    start_time += getTimeMs() - beforeTurn + 1
            else: past_angle = state.pose.head

            sim.robot.setVelocities(VEL, ANG_VEL)




class TrajectoryBuilder():
    def __init__(self, start_pose: Pose = Pose(), constrains: Constrains = None):
        self.splines = []
        self.segments = []
        self.linear_profiles = []
        self.angular_profiles = []

        self.distance = 0
        self.constrains = Constrains() if constrains is None else constrains

        self.start_pose = start_pose
        self.current_pose = start_pose.copy()

        self.temp_markers: List[Marker] = []
        self.disp_markers: List[Marker] = []

        self.TRAJ_DISTANCE = [0]
        self.TRAJ_TIME = [-1]
        self.iterator = 0

        self.hasPrintThis = False

    def __createProfile(self, boolean: bool):
        if not boolean:
            return 0

        self.linear_profiles.append(MotionProfile(0, self.distance, self.constrains))

        self.distance = 0





    def inLineCM(self, cm: float):
        self.__createProfile(boolean = (not signum(cm) == signum(self.distance) 
                                        and not self.distance == 0))
        
        self.segments.append(MotionSegment(MotionAction.LINE, cm))
        self.distance += cm

        return self
    
    def toPoint(self, point: Point, forwards: bool = True):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POINT, (point, forwards)))

        return self

    def toPose(self, pose: Pose, forwards: bool = True):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POSE, (pose, forwards)))

        return self
 
    def turnDeg(self, deg: float):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TURN, deg))

        return self



    def wait(self, ms: int):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.WAIT, ms))

        return self

    def setPoseEstimate(self, pose: Pose):
        self.segments.append(MotionSegment(MotionAction.SET_POSE, pose))
        return self



    def interruptTemporal(self, ms: int): #interrupts last linear move
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.INT_MARKER, 
                                           value = Marker.Interruptor(int(ms), MarkerType.TEMPORAL)))

        return self

    def interruptDisplacement(self, dis: float):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.INT_MARKER, 
                                           value = Marker.Interruptor(dis, MarkerType.DISPLACEMENT)))

        return self



    def addTemporalMarker(self, ms: int, fun):
        ms = 0 if ms < 0 else ms
        self.temp_markers.append(Marker(val = ms, fun = fun, rel = False,
                                       type = MarkerType.TEMPORAL))
        return self
    
    def addRelativeTemporalMarker(self, ms: int, fun):
        self.segments.append(MotionSegment(MotionAction.REL_MARKER, 
                                           value = Marker(val = ms, fun = fun, rel = True,
                                                          type = MarkerType.TEMPORAL)))
        return self

    def addDisplacementMarker(self, dis: float, fun):
        dis = 0 if dis < 0 else dis
        self.disp_markers.append(Marker(val = dis, fun = fun, rel = False,
                                        type = MarkerType.DISPLACEMENT))
        return self

    def addRelativeDisplacementMarker(self, dis: float, fun):
        self.segments.append(MotionSegment(MotionAction.REL_MARKER,
                                           value = Marker(val = dis, fun = fun, rel = True,
                                                          type = MarkerType.DISPLACEMENT)))
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
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segment_number = len(self.segments)

        if self.segment_number == 0 or self.__nextSegmentsJustMarkers(start = self.iterator):
            print("\n\ncan't compute an empty trajectory..")
            return Trajectory(self.start_pose, self.start_pose, [], 0, [])

        print("\n\ncalculating trajectory...")
 
        self.TRAJ_DISTANCE = [0]
        self.TRAJ_TIME = [0]
        self.TURN = False
        self.iterator = 0

        self.START_TIME = 0
        self.START_DIST = 0

        while self.iterator < self.segment_number:
            segment: MotionSegment = self.segments[self.iterator]
            
            if segment.action is MotionAction.LINE:
                self.__buildLine(segment)

            elif segment.action is MotionAction.TURN: 
                self.__buildTurn(segment)
            
            elif segment.action is MotionAction.WAIT:
                self.__buildWait(segment)
            
            elif segment.action is MotionAction.TO_POINT:
                self.__buildToPoint(segment)
            
            elif segment.action is MotionAction.TO_POSE:
                self.__buildToPose(segment)
            
            elif segment.action is MotionAction.SPLINE:
                self.__buildSpline(segment)
            
            elif segment.action is MotionAction.REL_MARKER:
                self.__buildMarker(segment)
            
            elif segment.action is MotionAction.INT_MARKER:
                self.__buildInterruptor(segment)

            elif segment.action is MotionAction.SET_POSE:
                self.__buildSetPose(segment)
            
            
            self.iterator += 1
        
        self.__sortMarkers()

        self.TRAJ_DISTANCE.pop()
        self.TRAJ_TIME.pop()

        print("\n\ndone!")
        print("(FINAL POSE) x:{0} ; y:{1} ; head:{2}".format(round(self.current_pose.x, 2),
                                                             round(self.current_pose.y, 2),
                                                             round(self.current_pose.head, 2)))
        
        if self.__isBugged():
            print('\n\noh no! a wild bug has appeared!')
            print("('in the basement', yoo, chill google 😭😭)")
            print('\nPLEASE REPORT THE BUG APPEARANCE BACK TO US!')
            print("you'll get free candy :D")
            print('actually no, I lied :<')
            print('please still do it 🥺')

        return Trajectory(self.start_pose.copy(), self.current_pose.copy(), 
                          self.segments, self.TRAJ_TIME[-1], self.temp_markers)
    


    def __specialCase(self, segment: MotionSegment):
        #account for turning at the end of the trajectory

        for _ in range(60):
            segment.add(MotionState(time = self.TRAJ_TIME[-1],
                                         displacement = self.TRAJ_DISTANCE[-1],
                                         pose = self.current_pose.copy(),
                                         velocities = (0, 0),
                                         turn = self.TURN)
            )

            self.TRAJ_DISTANCE.append(self.TRAJ_DISTANCE[-1])
            self.TRAJ_TIME.append(self.TRAJ_TIME[-1] + 1)

        self.TRAJ_TIME.pop()
        self.TRAJ_DISTANCE.pop()



    def __buildLine(self, segment: MotionSegment):
        profile: MotionProfile = self.linear_profiles.pop(0)
        segment_distance = segment.value

        VELOCITY = ANGULAR_VELOCITY = t = 0
        self.START_TIME, self.START_DIST = self.TRAJ_TIME[-1], self.TRAJ_DISTANCE[-1]

        profile_time = int(sToMs(profile.t_total)) + 1 # +1 -> [0, t_total]
        past_distance = 0

        for t in range(profile_time):

            sec = msToS(t)
            distance, velocity = profile.get_dis(sec), profile.get_vel(sec)

            if abs(distance) > abs(segment_distance):
                self.iterator += 1
                segment.build()
                
                while self.segments[self.iterator].action is MotionAction.SET_POSE and self.iterator < self.segment_number:
                    self.__buildSetPose(self.segments[self.iterator])
                    self.iterator += 1

                segment = self.segments[self.iterator]
                segment_distance += segment.value
            
            VELOCITY, ANGULAR_VELOCITY = velocity, 0

            delta_distance = distance - past_distance
            self.current_pose.sum(Pose(x = math.cos(self.current_pose.rad()) * delta_distance,
                                       y = math.sin(self.current_pose.rad()) * delta_distance))


            segment.add(MotionState(time = self.TRAJ_TIME[-1],
                                    displacement = self.TRAJ_DISTANCE[-1],
                                    pose = self.current_pose.copy(),
                                    velocities = (VELOCITY, ANGULAR_VELOCITY),
                                    turn = self.TURN)
            )

            self.TRAJ_DISTANCE.append(self.START_DIST + abs(distance))
            self.TRAJ_TIME.append(self.START_TIME + t + 1)

            past_distance = distance

        segment.build()
    
    def __buildTurn(self, segment: MotionSegment):
        self.TURN = True
    
        self.current_pose.head = segment.value
        self.segments.pop(self.iterator)
        self.segment_number -= 1
        self.iterator -= 1

        

        if self.iterator + 1 == self.segment_number or self.__nextSegmentsJustMarkers(start = self.iterator + 1):
            self.__specialCase(self.segments[self.iterator])
            self.segments[self.iterator].build()    
    
    def __buildWait(self, segment: MotionSegment):
        waiting_time = segment.value

        self.START_TIME, self.START_DIST = self.TRAJ_TIME[-1], self.TRAJ_DISTANCE[-1]

        for _ in range(waiting_time):
            segment.add(MotionState(time = self.TRAJ_TIME[-1],
                                    displacement = self.TRAJ_DISTANCE[-1],
                                    pose = self.current_pose.copy(),
                                    velocities = (0, 0),
                                    turn = self.TURN)
            )

            self.TRAJ_DISTANCE.append(self.TRAJ_DISTANCE[-1])
            self.TRAJ_TIME.append(self.TRAJ_TIME[-1] + 1)
        

        segment.build()
    
    def __buildToPoint(self, segment: MotionSegment):
        current = self.current_pose.point()
        target: Point = segment.value[0]
        forwards: bool = segment.value[1]

        head = normalizeDegrees(toDegrees(target.subtract(current).atan2()))
        displacement = target.subtract(current).hypot()

        if not forwards:
            head = normalizeDegrees(180 + head)
            displacement = -displacement

        self.segments[self.iterator] = MotionSegment(MotionAction.TURN, head)
        self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE, displacement))
        self.linear_profiles.insert(0, MotionProfile(0, displacement, self.constrains))

        self.segment_number += 1
        self.iterator -= 1
    
    def __buildToPose(self, segment: MotionSegment):
        current = self.current_pose.point()
        target: Point = segment.value[0].point()
        forwards: bool = segment.value[1]

        head = normalizeDegrees(toDegrees(target.subtract(current).atan2()))
        displacement = target.subtract(current).hypot()

        if not forwards:
            head = normalizeDegrees(180 + head)
            displacement = -displacement

        self.segments[self.iterator] = MotionSegment(MotionAction.TURN, head)
        self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE, displacement))
        self.segments.insert(self.iterator + 2, MotionSegment(MotionAction.TURN, segment.value[0].head))
        self.linear_profiles.insert(0, MotionProfile(0, displacement, self.constrains))

        self.segment_number += 2
        self.iterator -= 1

    def __buildSpline(self, segment: MotionSegment):
        return 0
    
    def __buildMarker(self, segment: MotionSegment):
        marker: Marker = segment.value

        if self.__nextNonMarkerSegmentIsInterruptor(self.iterator + 1): 
            #build the marker after the interruptor
            return 0

        self.segments.pop(self.iterator)
        self.segment_number -= 1
        self.iterator -= 1
        early_leave = False

        if self.iterator == -1:

            if not self.hasPrintThis:
                print("\n\nwhat are you doin' mate? use a marker on what??")
                print("there's nothing before this marker... this, or I need to go to sleep.. 💤")

            self.hasPrintThis = True
            early_leave = True

        self.hasPrintThis = False

        if len(self.TRAJ_TIME) < 3 and marker.type is MarkerType.TEMPORAL:
            print("\n\nquick, we don't have time! 😵")
            print("(not enough time available for the relative temporal marker with the value {}ms)"
                  .format(marker.value))
            early_leave = True
        
        if len(self.TRAJ_DISTANCE) < 3 and marker.type is MarkerType.DISPLACEMENT:
            print("\n\nhow short...")
            print("(not enough distance available for the relative displacement marker with the value {}ms)"
                  .format(marker.value))
            early_leave = True

        if early_leave:
            self.temp_markers.append(Marker(val = 0, fun = marker.fun, rel = False,
                                            type = MarkerType.TEMPORAL))
            return 0
            

        match marker.type:
            case MarkerType.TEMPORAL:
                
                if marker.value >= 0:
                    time = self.START_TIME + marker.value - 1 if self.START_TIME + marker.value - 1 < self.TRAJ_TIME[-2] else self.TRAJ_TIME[-2]
                else: time = 0 if self.TRAJ_TIME[-2] + marker.value < 0 else self.TRAJ_TIME[-2] + marker.value

                self.temp_markers.append(Marker(val = time, fun = marker.fun, rel = False,
                                        type = MarkerType.TEMPORAL))
                

            case MarkerType.DISPLACEMENT:
                if marker.value >= 0:
                    dist = self.TRAJ_DISTANCE[-2] if self.TRAJ_DISTANCE[-2] - self.START_DIST < marker.value else marker.value
                else: dist = 0 if self.TRAJ_DISTANCE[-2] + marker.value < 0 else self.TRAJ_DISTANCE[-2] + marker.value


                self.disp_markers.append(Marker(val = dist, fun = marker.fun, rel = False,
                                                type = MarkerType.DISPLACEMENT))
                
            case _:
                pass


    def __buildInterruptor(self, segment: MotionSegment):
        inter : Marker.Interruptor = segment.value

        self.segments.pop(self.iterator)
        self.segment_number -= 1


        index = self.iterator - 1

        while index > -1:
            if self.segments[index].action is MotionAction.LINE:
                break
            index -= 1
        
        if index == -1: 
            print('\n\nFound no segment to interrupt')
            return 0
    
        
        keys = list(self.segments[index].states.keys())
        erase_time = 0
        
        #at this point, just remove the part of the trajectory
        if inter.value == 0:
            self.segments.pop(index)
            self.segment_number -= 1
            self.iterator -= 2

            for i in range(index, self.iterator + 1):
                self.segments[i].reset()
            
            while self.TRAJ_TIME[-1] > keys[0]:
                self.TRAJ_TIME.pop()
                self.TRAJ_DISTANCE.pop()
            
            self.iterator = index - 1

            print('\n\nreally? interrupt at 0ms? just erase your last linear segment pff..')
            print("don't stress out, I've already done it for you")
            print("but please, for the love of god, get rid of this 😭")
            return 0

        start_distance = self.segments[index].get(keys[0]).displacement
        end_distance = self.segments[index].get(keys[-1]).displacement

        match inter.type:
            case MarkerType.TEMPORAL: 

                if abs(inter.value) >= self.segments[index].total_time:
                    print('\n\nYour TEMPORAL marker with value {0} is out of bounds: {1}ms - {2}ms'
                          .format(inter.value, keys[0], keys[-1]))
                    self.iterator -= 1
                    return 0


                erase_time = (keys[0] + inter.value
                                    if inter.value >= 0 else 
                              keys[-1] + inter.value)
                
                print('\n\nafferent distance (if you care):')
                print(round(self.segments[index].get(erase_time).displacement - start_distance, 2),'cm')
                
                
            case MarkerType.DISPLACEMENT:
                total_distance = end_distance - start_distance

                if abs(inter.value) > total_distance:
                    print('\n\nYour DISPLACEMENT marker with value {0} is out of bounds: {1}cm - {2}cm'
                          .format(inter.value, start_distance, end_distance))   
                         
                    self.iterator -= 1
                    return 0

                search_distance = (self.segments[index].get(keys[0]).displacement + inter.value
                                            if inter.value >= 0 else 
                                   self.segments[index].get(keys[-1]).displacement + inter.value)

                erase_time, _ = binary_search(search_distance, self.segments[index].states, 'displacement',
                                             left = keys[0], right = keys[-1])
                
                print('\n\nafferent time (if you care):')
                print(erase_time - keys[0],'ms')
                
            case _:
                pass
        
        
        print(erase_time)
        self.current_pose = self.segments[index].eraseAllAfter(erase_time)

        while self.TRAJ_TIME[-1] > erase_time + 1:
            self.TRAJ_TIME.pop()
            self.TRAJ_DISTANCE.pop()

        #recalculate all values after the truncation (makes less bugs + more straight forward)
        for i in range(index + 1, self.iterator):
            self.segments[i].reset()

        self.iterator = index

    def __buildSetPose(self, segment: MotionSegment):
        self.current_pose = segment.value.copy()
        self.TURN = False

        self.segments.pop(self.iterator)
        self.segment_number -= 1
        self.iterator -= 1



    def __nextSegmentsJustMarkers(self, start):
        for index in range(start, self.segment_number):
            if (self.segments[index].action is not MotionAction.REL_MARKER 
                                            and 
                self.segments[index].action is not MotionAction.INT_MARKER):
                return False
        
        return True
    
    def __nextNonMarkerSegmentIsInterruptor(self, start):
        for index in range(start, self.segment_number):
            if self.segments[index].action is not MotionAction.REL_MARKER:
                if self.segments[index].action is MotionAction.INT_MARKER:
                    return True
                return False
        
        return False

    def __disp_2_temp_marker(self):
        marker_iterator = 1

        for marker in self.disp_markers:
            index, value = binary_search(marker.value, self.TRAJ_DISTANCE)

            if value > self.TRAJ_DISTANCE[-2]:
                print('\nThe displacement marker number {0} exceded the displacement limit of {1}cm with {2}cm'
                      .format(marker_iterator, round(self.TRAJ_DISTANCE[-2], 2), 
                              round(marker.value - self.TRAJ_DISTANCE[-2], 2)))

            self.temp_markers.append(Marker(val = self.TRAJ_TIME[index], fun = marker.fun, rel = False,
                                            type = MarkerType.TEMPORAL))
            
            marker_iterator += 1
    
    def __sortMarkers(self):
        self.__disp_2_temp_marker()

        #selection sort
        sorted: bool = False
        marker_number = len(self.temp_markers) - 1

        while not sorted:
            sorted = True
            for i in range(marker_number):
                if self.temp_markers[i].value > self.temp_markers[i+1].value:
                    sorted = False

                    aux = self.temp_markers[i]
                    self.temp_markers[i] = self.temp_markers[i+1]
                    self.temp_markers[i+1] = aux



    def __isBugged(self):
        last = None
        for each in self.segments:
            if last is not None:
                if last + 1 == each.start_time:
                    last = each.end_time
                else: return True
            else: last = each.end_time
        
        return False