from pythfinder.Components.Controllers.PIDCoefficients import *
from pythfinder.Components.Controllers.PIDController import *
from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Components.Constants.constraints import *
from pythfinder.Trajectory.feedforward import *
from pythfinder.Trajectory.kinematics import *
from pythfinder.Trajectory.feedback import *
from pythfinder.Trajectory.splines import *

import matplotlib.pyplot as mplt
from enum import Enum, auto
import threading

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

    class Interrupter():
        def __init__(self, val: float, type: MarkerType):
            self.value = val
            self.type = type



class MotionState():
    def __init__(self, time: int, 
                 velocities: ChassisState, 
                 displacement: float,
                 pose: Pose, 
                 turn: bool = False):

        self.velocities = velocities # cm / s

        self.time = time # ms
        self.displacement = displacement
        self.pose = pose

        self.turn = turn
    
    def isLike(self, other): 
        return (self.turn == other.turn
                        and
                self.velocities.isLike(other.velocities)
                        and 
                self.pose.head == other.pose.head)

class MotionSegment():
    def __init__(self, action: MotionAction, value: float, 
                 constraints: Constraints = None):
        self.action = action 
        self.constraints = constraints
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
        self.perfect_increment = 40



    def follow(self, sim: Simulator, perfect: bool = False, 
               wait: bool = True, steps: int = None) -> None:
        if self.trajectoryTime == 0: 
            print("\n\ncan't follow an empty trajectory")
            return 0
        
        if steps is not None:
            self.perfect_increment = steps
        
        print('\n\nFOLLOWING TRAJECTORY...')
        
        sim.autonomus(Auto.ENTER)
        sim.robot.setPoseEstimate(self.start_pose)

        self.marker_iterator = 0
        self.iterator = 0

        if wait:
            for _ in range(201):
                sim.update()

        if perfect:
            sim.robot.target_head = self.__perfectFollow(sim)
            sim.robot.setPoseEstimate(self.end_pose)
        else: 
            sim.robot.target_head = self.__realFollow(sim)
            sim.robot.setVelocities(ChassisState(), True)
        
        #markers from last miliseconds or beyond the time limit
        while self.marker_iterator < len(self.markers):
            sim.update()
            marker = self.markers[self.marker_iterator]

            if marker.value > self.trajectoryTime:
                print('\nThe marker number {0} exceded the time limit of {1}ms with {2}ms'
                      .format(self.marker_iterator + 1, self.trajectoryTime, marker.value - self.trajectoryTime))

            threading.Thread(target = marker.do).start()
            self.marker_iterator += 1

        sim.autonomus(Auto.EXIT)
        print('\n\nTRAJECTORY COMPLETED! ;)')

    def generate(self, sim: Simulator, file_name: str, steps: int = 1):
        if self.trajectoryTime == 0:
            print("\n\ncan't generate data from an empty trajectory")
            return 0
        
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
            
            last_state: MotionState = self.segments[0].states[0]
            appearance = 0

            while self.iterator < self.segment_number:

                while time >= segment_time:
                    self.iterator += 1
                    if self.iterator == self.segment_number:
                        speeds = sim.robot.kinematics.inverse(last_state.velocities)
                    
                        # write velocities for each wheel, acording to the kinematics
                        line = ''.join(str(sim.robot.toMotorPower(value.VELOCITY)) + ' ' for value in speeds)
                        line = line + '{0} {1}'.format(
                            round(last_state.pose.head, 2),
                            appearance * 10 + int(last_state.turn))
                        
                        f.write(line)

                        print('\n\ndone writing in * {0}.txt * file :o'.format(file_name))
                        return 0
                
                    segment = self.segments[self.iterator]
                    segment_time += segment.total_time
                
                state: MotionState = segment.get(time)

                if last_state.isLike(state):
                    appearance += 1
                else:
                    speeds = sim.robot.kinematics.inverse(last_state.velocities)
                    
                    line = ''.join(str(sim.robot.toMotorPower(value.VELOCITY)) + ' ' for value in speeds)

                    # for swerve modules, get the angles
                    if isinstance(sim.robot.kinematics, SwerveKinematics):
                        for value in speeds:
                            line = line + str(sim.robot.toMotorPower(value.ANGLE))

                    line = line + '{0} {1}'.format(
                        round(last_state.pose.head, 2),
                        appearance * 10 + int(last_state.turn))
                    
                    f.write(line)

                    last_state = state
                    appearance = 1

                time += steps

    def graph(self, 
              sim: Simulator,
              connect: bool = True,
              velocity: bool = True,
              acceleration: bool = True,
              each_wheel: bool = True):
        
        if self.trajectoryTime == 0: 
            print("\n\ncan't graph an empty trajectory")
            return 0

        if not velocity and not acceleration:
            print("\n\nno velocity: checked")
            print("no acceleration: checked")
            print("wait... what am I supposed to graph then???")
            print("\nyour greatest dreams and some pizza, right?")
            return 0
        
        print(' ')
        print('computing graph...')

        time: int = 0
        
        self.TIME: list = []
        self.VELOCITY: list = []
        self.ANGULAR_VELOCITY: list = []

        self.VEL: List[list] = []
        self.ACC: List[list] = []

        iterator = 0
        segment: MotionSegment = self.segments[0]
        segment_time = segment.end_time

        while iterator < self.segment_number:    
            if time > segment_time:
                iterator += 1
                
                if not iterator == self.segment_number:
                    segment: MotionSegment = self.segments[iterator]
                    segment_time = segment.end_time
                else:
                    break

            state: MotionState = segment.get(time)

            speeds = sim.robot.kinematics.inverse(state.velocities)
            
            self.TIME.append(time)
            self.VELOCITY.append(state.velocities.getVelocityMagnitude())
            self.ANGULAR_VELOCITY.append(state.velocities.ANG_VEL)

            for i in range(len(speeds)):
                try: self.VEL[i]
                except: self.VEL.append([])
                try: self.ACC[i]
                except: self.ACC.append([])

                self.VEL[i].append(speeds[i].VELOCITY)

                if segment.action is not MotionAction.LINE:
                    self.ACC[i].append(0)
                else: self.ACC[i].append(self.__getDerivative(self.TIME, self.VEL[i]))

            time += 1

        #be sure that accel line ends on the x axis
        for i in range(len(self.VEL)):
                self.VEL[i].append(0)
                self.ACC[i].append(0)

        self.TIME.append(self.TIME[-1] + 1)
        self.ANGULAR_VELOCITY.append(0)
        self.VELOCITY.append(0)

        print('done!')

        print(' ')
        print('plotting...')

        quadrants = 0
        q_index = 1

        if velocity:
            quadrants += 1
        if acceleration:
            quadrants += 1
        
        if not each_wheel:
            # plot robot velocity

            mplt.figure(figsize=(7, 7), facecolor = 'black')
            mplt.style.use('dark_background')

            mplt.gcf().canvas.manager.set_window_title("Linear / Angular velocities")

            mplt.subplot(quadrants, 1, 1)
            mplt.title('robot VELOCITY', fontsize = 22)
            mplt.xlabel('time (ms)', fontsize = 14)
            mplt.ylabel('velocity (cm / s)', fontsize = 14)

            if connect:
                mplt.plot(self.TIME, self.VELOCITY, color = 'green', linewidth = 3)
            else: mplt.scatter(self.TIME, self.VELOCITY, color = 'green', s = 1)

            mplt.axhline(0, color = 'white', linewidth = 0.5)

            # plot robot acceleration
            mplt.subplot(quadrants, 1, 2)
            mplt.title('robot VELOCITY', fontsize = 22)
            mplt.xlabel('time (ms)', fontsize = 14)
            mplt.ylabel('velocity (cm / s)', fontsize = 14)

            if connect:
                mplt.plot(self.TIME, self.ANGULAR_VELOCITY, color = 'red', linewidth = 3)
            else: mplt.scatter(self.TIME, self.ANGULAR_VELOCITY, color = 'red', s = 1)

            mplt.axhline(0, color = 'white', linewidth = 0.5)

        else:
            # plot velocities / accelerations for each wheel
            
            mplt.figure(figsize=(13, 7), facecolor = 'black')
            mplt.style.use('dark_background')

            mplt.gcf().canvas.manager.set_window_title("Wheel Speeds")

            if velocity:
    
                for i in range(len(self.VEL)):
                    mplt.subplot(quadrants, len(self.VEL), q_index)
                    mplt.title('nr. {0} wheel VELOCITY'.format(i + 1), fontsize = 22)
                    mplt.xlabel('time (ms)', fontsize = 14)
                    mplt.ylabel('velocity (cm / s)', fontsize = 14)

                    if connect:
                        mplt.plot(self.TIME, self.VEL[i], color = 'green', linewidth = 3)
                    else: mplt.scatter(self.TIME, self.VEL[i], color = 'green', s = 1)

                    mplt.axhline(0, color = 'white', linewidth = 0.5)
                    q_index += 1

            if acceleration:
                
                for i in range(len(self.VEL)):
                    mplt.subplot(quadrants, len(self.ACC), q_index)
                    mplt.title('nr. {0} wheel ACCELERATION'.format(i + 1), fontsize = 22)
                    mplt.xlabel('time (ms)', fontsize = 14)
                    mplt.ylabel('acceleration (cm / s^2)', fontsize = 14)

                    if connect:
                        mplt.plot(self.TIME, self.ACC[i], color = 'red', linewidth = 3)
                    else: mplt.scatter(self.TIME, self.ACC[i], color = 'red', s = 1)

                    mplt.axhline(0, color = 'white', linewidth = 0.5)
                    q_index += 1

        mplt.subplots_adjust(wspace = 0.15, hspace = 0.4) 
        mplt.tight_layout()

        mplt.show()



    def __getDerivative(self, t: List[int], vel: List[float]):
        if len(vel) > 1:
            dt = (t[-1] - t[-2]) / 1000 #ms to s
            dv = vel[-1] - vel[-2]
                
            if dt != 0:
                accel = dv / dt
                return accel
        return 0

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

            if not past_angle is None:
                if abs(state.pose.head - sim.robot.pose.head) > 1 and state.turn:
                    beforeTurn = getTimeMs()

                    turnDeg(state.pose.head, sim)

                    past_angle = state.pose.head
                    start_time += getTimeMs() - beforeTurn + 1
            else: past_angle = state.pose.head

            sim.robot.setVelocities(state.velocities, True)




class TrajectoryBuilder():
    def __init__(self, sim: Simulator, start_pose: Pose = None, constraints: Constraints = None):
        self.splines = []
        self.segments = []

        self.linear_profiles = []
        self.angular_profiles = []

        self.disp_volatile_constraints = []
        self.temp_volatile_constraints = []

        self.distance = 0
        self.constraints = Constraints() if constraints is None else constraints

        self.start_pose = Pose() if start_pose is None else start_pose
        self.current_pose = start_pose.copy()

        self.temp_markers: List[Marker] = []
        self.disp_markers: List[Marker] = []

        self.TRAJ_DISTANCE = [0]
        self.TRAJ_TIME = [-1]
        self.iterator = 0

        self.hasPrintThis = False
        self.simulator = sim

    def __createProfile(self, boolean: bool):
        if not boolean:
            return 0

        self.linear_profiles.append(MotionProfile(self.distance, self.constraints))

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

    def toPointConstantHeading(self, point: Point):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POINT_CONSTANT_HEAD, point))
        
        return self

    def toPose(self, pose: Pose, forwards: bool = True):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POSE, (pose, forwards)))

        return self
    
    def toPoseConstantsHeading(self, pose: Pose):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POSE_CONSTANT_HEAD, pose))
        
        return self

    def toPoseLinearHeading(self, pose: Pose):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TO_POSE_LINEAR_HEAD, pose))
        
        return self

    def turnDeg(self, deg: float):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.TURN, deg))

        return self

    def inSpline(self, spline: Spline):
        self.splines.append(spline)

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
                                           value = Marker.Interrupter(int(ms), MarkerType.TEMPORAL)))

        return self

    def interruptDisplacement(self, dis: float):
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.segments.append(MotionSegment(MotionAction.INT_MARKER, 
                                           value = Marker.Interrupter(dis, MarkerType.DISPLACEMENT)))

        return self



    def addTemporalMarker(self, ms: int, fun):
        ms = 0 if ms < 0 else ms
        self.temp_markers.append(Marker(val = ms, fun = fun, rel = False,
                                       type = MarkerType.TEMPORAL))
        return self
    
    def addDisplacementMarker(self, dis: float, fun):
        dis = 0 if dis < 0 else dis
        self.disp_markers.append(Marker(val = dis, fun = fun, rel = False,
                                        type = MarkerType.DISPLACEMENT))
        return self
    
    def addRelativeTemporalMarker(self, ms: int, fun):
        self.segments.append(MotionSegment(MotionAction.REL_MARKER, 
                                           value = Marker(val = ms, fun = fun, rel = True,
                                                          type = MarkerType.TEMPORAL)))
        return self

    def addRelativeDisplacementMarker(self, dis: float, fun):
        self.segments.append(MotionSegment(MotionAction.REL_MARKER,
                                           value = Marker(val = dis, fun = fun, rel = True,
                                                          type = MarkerType.DISPLACEMENT)))
        return self



    def addConstraintsTemporal(self, start: float, constraints: Constraints, end: float | None = None):
        self.temp_volatile_constraints.append(VolatileConstraints(abs(start), constraints,
                                                                ConstraintsType.TEMPORAL))
        if end is not None:
            self.temp_volatile_constraints.append(VolatileConstraints(abs(end), self.constraints.copy(),
                                                                    ConstraintsType.TEMPORAL))

        return self

    def addConstraintsDisplacement(self, start: float, constraints: Constraints, end: float | None = None):
        self.disp_volatile_constraints.append(VolatileConstraints(abs(start), constraints,
                                                                ConstraintsType.DISPLACEMENT))
        if end is not None:
            self.disp_volatile_constraints.append(VolatileConstraints(abs(end), self.constraints.copy(),
                                                                    ConstraintsType.DISPLACEMENT))
        
        return self

    def addConstraintsRelativeTemporal(self, start: float, constraints: Constraints, end: float | None = None):
        self.segments.append(MotionSegment(MotionAction.REL_CONSTRAINTS, 
                                           value = VolatileConstraints(start, constraints, 
                                                                      ConstraintsType.TEMPORAL)))
        if end is not None:
            self.segments.append(MotionSegment(MotionAction.REL_CONSTRAINTS, 
                                           value = VolatileConstraints(end, self.constraints.copy(), 
                                                                      ConstraintsType.TEMPORAL)))
            
        return self

    def addConstraintsRelativeDisplacement(self, start: float, constraints: Constraints, end: float | None = None):
        self.segments.append(MotionSegment(MotionAction.REL_CONSTRAINTS, 
                                           value = VolatileConstraints(start, constraints, 
                                                                      ConstraintsType.DISPLACEMENT)))
        if end is not None:
            self.segments.append(MotionSegment(MotionAction.REL_CONSTRAINTS, 
                                           value = VolatileConstraints(end, self.constraints.copy(), 
                                                                      ConstraintsType.DISPLACEMENT)))
        
        return self
    


    def build(self) -> Trajectory: 
        self.__createProfile(boolean = (abs(self.distance) > 0))
        self.__sortConstraints()

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

        self.last_constraints_start = 0
        self.last_stop_distance = 0
        self.last_stop_time = 0

        try: self.disp_next_constraints: VolatileConstraints = self.disp_volatile_constraints.pop(0)
        except: self.disp_next_constraints = None

        try: self.temp_next_constraints: VolatileConstraints = self.temp_volatile_constraints.pop(0)
        except: self.temp_next_constraints = None

        while self.iterator < self.segment_number:
            segment: MotionSegment = self.segments[self.iterator]
            
            if segment.action is MotionAction.LINE:
                self.__buildLine(segment)

            elif segment.action is MotionAction.TURN: 
                self.__buildTurn(segment)
            
            elif segment.action is MotionAction.WAIT:
                self.__buildWait(segment)
            
            elif segment.action is MotionAction.TO_POINT:
                self.__buildToPoint(segment, constant = False)
            
            elif segment.action is MotionAction.TO_POINT_CONSTANT_HEAD:
                self.__buildToPoint(segment, constant = True)
            
            elif segment.action is MotionAction.TO_POSE:
                self.__buildToPose(segment)
            
            elif segment.action is MotionAction.TO_POSE_CONSTANT_HEAD:
                self.__buildToPose(segment, constant = True)
            
            elif segment.action is MotionAction.TO_POSE_LINEAR_HEAD:
                self.__buildToPose(segment, linear = True)
            
            elif segment.action is MotionAction.SPLINE:
                self.__buildSpline(segment)
            
            elif segment.action is MotionAction.REL_MARKER:
                self.__buildMarker(segment)
            
            elif segment.action is MotionAction.INT_MARKER:
                self.__buildInterrupter(segment)
            
            elif segment.action is MotionAction.REL_CONSTRAINTS:
                self.__buildConstraints(segment)

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
                                    velocities = ChassisState(),
                                    displacement = self.TRAJ_DISTANCE[-1],
                                    pose = self.current_pose.copy(),
                                    turn = self.TURN)
            )

            self.TRAJ_DISTANCE.append(self.TRAJ_DISTANCE[-1])
            self.TRAJ_TIME.append(self.TRAJ_TIME[-1] + 1)

        self.TRAJ_TIME.pop()
        self.TRAJ_DISTANCE.pop()



    def __buildLine(self, segment: MotionSegment):
        self.__erase_all_linear_segments_after()

        #recalculate (could have new constraints)
        profile: MotionProfile = self.linear_profiles.pop(0)
        profile = MotionProfile(profile.distance * profile.sign, self.constraints, profile.start_vel)

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
                
                while self.iterator < self.segment_number:
                    if self.segments[self.iterator].action is MotionAction.SET_POSE:
                        self.__buildSetPose(self.segments[self.iterator])
                        self.iterator += 1
                    else: break

                if self.iterator < self.segment_number:
                    segment = self.segments[self.iterator]
                    segment_distance += segment.value
                else: break
            

            VELOCITY, ANGULAR_VELOCITY = velocity, 0

            delta_distance = distance - past_distance
            self.current_pose = self.current_pose + Pose(x = math.cos(self.current_pose.rad()) * delta_distance,
                                       y = math.sin(self.current_pose.rad()) * delta_distance)


            segment.add(MotionState(time = self.TRAJ_TIME[-1],
                                    velocities = ChassisState(Point(VELOCITY, 0), ANGULAR_VELOCITY),
                                    displacement = self.TRAJ_DISTANCE[-1],
                                    pose = self.current_pose.copy(),
                                    turn = self.TURN)
            )

            self.TRAJ_DISTANCE.append(self.START_DIST + abs(distance))
            self.TRAJ_TIME.append(self.START_TIME + t + 1)
            self.EVALUATE = False


            if self.temp_next_constraints is not None:
                
                #treat temporal constraints as displacement ones
                #too lazy to overthink conversions, just convert on the go

                if self.TRAJ_TIME[-1] == self.temp_next_constraints.start:
                    print("\n\nafferent displacement for the constraints set at {0}ms: {1}cm"
                          .format(self.temp_next_constraints.start,
                                round(self.TRAJ_DISTANCE[-1], 2)))
                    self.evaluating_displacement = self.TRAJ_DISTANCE[-1]
                    self.evaluating_constraints = self.temp_next_constraints.constraints
                    self.EVALUATE = True

                    try: self.temp_next_constraints = self.temp_volatile_constraints.pop(0)
                    except: self.temp_next_constraints = None



            if self.disp_next_constraints is not None:

                if self.TRAJ_DISTANCE[-1] >= self.disp_next_constraints.start:
                    print("\n\nafferent time for the constraints set at {0}cm: {1}ms"
                          .format(self.disp_next_constraints.start,
                                self.TRAJ_TIME[-2]))
                    self.evaluating_displacement = self.disp_next_constraints.start
                    self.evaluating_constraints = self.disp_next_constraints.constraints
                    self.EVALUATE = True

                    try: self.disp_next_constraints = self.disp_volatile_constraints.pop(0)
                    except: self.disp_next_constraints = None



            if self.EVALUATE:
                new_profile = MotionProfile(distance = profile.sign * profile.distance - self.evaluating_displacement
                                                                        + self.last_constraints_start,
                                        constraints = self.evaluating_constraints,
                                        start_velocity = abs(velocity))

                if new_profile.recommended_distance is None:
                    self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE,
                                        value = profile.sign * profile.distance - self.evaluating_displacement +
                                                                    self.last_constraints_start))
                    self.segment_number += 1
                        
                    self.linear_profiles.insert(0, new_profile)
                    self.last_constraints_start = self.evaluating_displacement
                    self.constraints = self.evaluating_constraints

                    break
                else:
                    print("\n\nthe constraints set at {0}cm displacement can't compute a continuous trajectory"
                            .format(self.evaluating_displacement))
                    if self.START_DIST > profile.sign * profile.distance + new_profile.recommended_distance:
                        print("you're out of luck, there's no way your constraints fit in this trajectory configuration")
                    else: print("supported interval: [{0}, {1}] cm"
                                .format(round(self.START_DIST, 2),
                                        round(profile.sign * profile.distance + new_profile.recommended_distance, 2)))
                    



            past_distance = distance

        segment.build()
    
    def __buildTurn(self, segment: MotionSegment):
        if not self.__should_build():
            return None
        
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
                                    velocities = ChassisState(),
                                    displacement = self.TRAJ_DISTANCE[-1],
                                    pose = self.current_pose.copy(),
                                    turn = self.TURN)
            )

            self.TRAJ_DISTANCE.append(self.TRAJ_DISTANCE[-1])
            self.TRAJ_TIME.append(self.TRAJ_TIME[-1] + 1)
        

        segment.build()
    
    def __buildToPoint(self, segment: MotionSegment, constant = False):
        current = self.current_pose.point()
        target: Point = segment.value[0]
        forwards: bool = segment.value[1]

        head = normalizeDegrees(toDegrees((target - current).atan2()))
        displacement = (target - current).hypot()

        if not forwards:
            head = normalizeDegrees(180 + head)
            displacement = -displacement

        if self.simulator.robot.kinematics.getType() is ChassisType.NON_HOLONOMIC:
            self.segments[self.iterator] = MotionSegment(MotionAction.TURN, head)
            self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE, displacement))
            self.segment_number += 1
        else:
            self.segments[self.iterator] = MotionSegment(MotionAction.LINE, displacement)

        self.linear_profiles.insert(0, MotionProfile(displacement, self.constraints))

        self.iterator -= 1
    
    def __buildToPose(self, segment: MotionSegment):
        current = self.current_pose.point()
        target: Point = segment.value[0].point()
        forwards: bool = segment.value[1]

        head = normalizeDegrees(toDegrees((target - current).atan2()))
        displacement = (target - current).hypot()

        if not forwards:
            head = normalizeDegrees(180 + head)
            displacement = -displacement

        self.segments[self.iterator] = MotionSegment(MotionAction.TURN, head)
        self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE, displacement))
        self.segments.insert(self.iterator + 2, MotionSegment(MotionAction.TURN, segment.value[0].head))
        self.linear_profiles.insert(0, MotionProfile(displacement, self.constraints))

        self.segment_number += 2
        self.iterator -= 1

    def __buildSpline(self, segment: MotionSegment):
        return 0
    
    def __buildMarker(self, segment: MotionSegment):
        marker: Marker = segment.value

        index = self.__organize()

        if index == -1: 
            if not self.hasPrintThis:
                print("\n\nwhat are you doin' mate? use a marker on what??")
                print("there's nothing before this marker... this, or I need to go to sleep.. 💤")

            self.hasPrintThis = True
            early_leave = True
        else:
            self.__orderConsecutiveMarkers(index)

            if self.segments[self.iterator].action is not MotionAction.REL_MARKER:
                self.iterator -= 1
                
                return None

        self.segments.pop(self.iterator)
        self.segment_number -= 1
        
        self.iterator -= 1
        early_leave = False

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

    def __buildInterrupter(self, segment: MotionSegment, telemetry = True, sort = True):
        inter : Marker.Interrupter = segment.value

        index = self.__organize()

        if index == -1: 
            if telemetry:
                print('\n\nFound no segment to interrupt')
            return None, None, None, None
        
        if sort:
            self.__orderConsecutiveMarkers(index)

            if self.segments[self.iterator].action is not MotionAction.INT_MARKER:
                self.iterator -= 1
                return None, None, None, None
        
        self.segments.pop(self.iterator)
        self.segment_number -= 1

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

            if telemetry:
                print('\n\nreally? interrupt at 0ms? just erase your last linear segment pff..')
                print("don't stress out, I've already done it for you")
                print("but please, for the love of god, get rid of this 😭")
            return None, None, None, None

        start_distance = self.segments[index].get(keys[0]).displacement
        end_distance = self.segments[index].get(keys[-1]).displacement
        total_distance = end_distance - start_distance

        match inter.type:
            case MarkerType.TEMPORAL: 

                if abs(inter.value) >= self.segments[index].total_time:
                    if telemetry:
                        print('\n\nyour temporal interrupter with value {0} is out of bounds: {1}ms - {2}ms'
                            .format(inter.value, keys[0], keys[-1]))
                    self.iterator -= 1
                    return None, None, None, None


                erase_time = (keys[0] + inter.value
                                    if inter.value >= 0 else 
                              keys[-1] + inter.value)
                
                if telemetry:
                    print('\n\nafferent interrupter distance (if you care):')
                    print(round(self.segments[index].get(erase_time).displacement - start_distance, 2),'cm')
                    
                
            case MarkerType.DISPLACEMENT:

                if abs(inter.value) > total_distance:
                    if telemetry:
                        print('\n\nyour displacement interrupter with value {0} is out of bounds: {1}cm - {2}cm'
                            .format(inter.value, start_distance, end_distance))   
                            
                    self.iterator -= 1
                    return None, None, None, None

                search_distance = (self.segments[index].get(keys[0]).displacement + inter.value
                                            if inter.value >= 0 else 
                                   self.segments[index].get(keys[-1]).displacement + inter.value)

                erase_time, _ = binary_search(search_distance, self.segments[index].states, 'displacement',
                                             left = keys[0], right = keys[-1])
                
                if telemetry:
                    print('\n\nafferent interrupter time (if you care):')
                    print(erase_time - keys[0],'ms')
                    
            case _:
                pass
        
        
        self.current_pose = self.segments[index].eraseAllAfter(erase_time)
    
        while self.TRAJ_TIME[-1] > erase_time + 1:
            self.TRAJ_TIME.pop()
            self.TRAJ_DISTANCE.pop()

        #recalculate all values after the truncation (makes less bugs + more straight forward)
        for i in range(index + 1, self.iterator):
            self.segments[i].reset()

        self.iterator = index

        return  (self.segments[index].get(keys[-1]).displacement,
                self.segments[index].get(erase_time).displacement, 
                erase_time,
                self.segments[index].get(erase_time).velocities)

    def __buildConstraints(self, segment: MotionSegment):
        constr: VolatileConstraints = self.segments[self.iterator].value

        index = self.__organize()

        if index == -1: 
            print('\n\nFound no segment to set constraints')
            return None

        self.__orderConsecutiveMarkers(index)


        #if you had inserted markers, they went on the top, so no more constraints setting rn
        #   if this happens, abort the building and return to building the marker

        if self.segments[self.iterator].action is not MotionAction.REL_CONSTRAINTS:
            self.iterator -= 1
            return None


        #strategy: let the interrupter do the heavy lifting for you
        #   NASA approved 👍

        type = None
        match constr.type:
            case ConstraintsType.TEMPORAL:
                type = MarkerType.TEMPORAL
            case ConstraintsType.DISPLACEMENT:
                type = MarkerType.DISPLACEMENT

        afferent_interrupter = Marker.Interrupter(constr.start, type)
        self.segments[self.iterator] = MotionSegment(action = MotionAction.INT_MARKER,
                                                     value = afferent_interrupter)
        
        #don't show the telemetry, because you didn't call an interrupter lol
        total_distance, stop_distance, stop_time, start_vel = self.__buildInterrupter(self.segments[self.iterator], 
                                                                                      telemetry = False,
                                                                                      sort = False)
        if total_distance is not None:
            distance = total_distance - stop_distance
            new_profile = MotionProfile(distance, constr.constraints, abs(start_vel.VEL.x))
    
            if new_profile.recommended_distance is None:
                self.segments.insert(self.iterator + 1, MotionSegment(MotionAction.LINE, value = distance))
                self.linear_profiles.insert(0, new_profile)
                self.constraints = constr.constraints

                self.segment_number += 1


                # renormalize values for the next relative segments, until find another linear segment
                # doing this for better intuition, not that it doesn't work without
                i = self.iterator + 2
                while i < self.segment_number:
                    segment: MotionSegment = self.segments[i]

                    if segment.action is MotionAction.REL_CONSTRAINTS:
                        match segment.value.type:
                            case ConstraintsType.TEMPORAL:
                                self.segments[i].value.start -= (stop_time - self.last_stop_time)
                            case ConstraintsType.DISPLACEMENT:
                                self.segments[i].value.start -= (stop_distance - self.last_stop_distance)
                    
                    elif segment.action is MotionAction.INT_MARKER:
                        last = self.segments[i].value.value

                        match segment.value.type:
                            case MarkerType.TEMPORAL:
                                self.segments[i].value.value -= (stop_time - self.last_stop_time)
                            case MarkerType.DISPLACEMENT:
                                self.segments[i].value.value -= (stop_distance - self.last_stop_distance)
                        
                        if self.segments[i].value.value < 0:
                            self.segments[i].value.value = last

                            #find the second previous linear segment, get rid of everything else
                            #no concern in accidentaly exiting the list
                            found = 0
                            current = i - 1
                            while found < 2:
                                if self.segments[current].action is MotionAction.LINE:
                                    found += 1
                                if found < 2:
                                    self.segments.pop(current)
                                    self.segment_number -= 1
                                
                                current -=1

                    else: break
                    i +=1


                
                self.last_stop_distance = stop_distance
                self.last_stop_time = stop_time

                return None
            

        print('\n\nnooooooooooooooooooooooo')
        print("well, your {0} relative constrain at {1}{2} can't exist ):"
                .format(constr.type.name.lower(), constr.start,
                        'ms' if constr.type is ConstraintsType.TEMPORAL else 'cm'))
        print('next one!')



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
        self.temp_markers = selection_sort(self.temp_markers, 'value')

    def __sortConstraints(self):
        self.constraints_number = len(self.disp_volatile_constraints)

        self.disp_volatile_constraints = selection_sort(self.disp_volatile_constraints, 'start')
        self.temp_volatile_constraints = selection_sort(self.temp_volatile_constraints, 'start')

    def __orderConsecutiveMarkers(self, start_index):
        # markers should be above constrain settings
        # constraints values should be monotonically increasing

        #takes care of the relative hierarchy (order of compiling):
        #       1) RELATIVE MARKERS
        #       2) RELATIVE CONSTRAINTS
        #       3) INTERRUPTERS
        #
        # absolute ones don't really matter

        line_segment: MotionSegment = self.segments[start_index]

        sort: bool = False

        while not sort:
            j = start_index + 1
            sort: bool = True

            while j < self.segment_number:
                current_marker: MotionSegment = self.segments[j]

                if (current_marker.action is MotionAction.REL_CONSTRAINTS or
                    current_marker.action is MotionAction.INT_MARKER or
                    current_marker.action is MotionAction.REL_MARKER):
                    
                    try: #when it's a REL_CONSTRAINTS object
                        if current_marker.value.start < 0:
                            current_marker.value.start = line_segment.value + current_marker.value.start
                    except: pass
                    
                    k = j + 1
                    while k < self.segment_number:
                        current_marker: MotionSegment = self.segments[j]
                        comparing_marker : MotionSegment = self.segments[k]


                        if (comparing_marker.action is MotionAction.REL_MARKER and
                             current_marker.action is not MotionAction.REL_MARKER):
                                sort = False

                                aux = self.segments[j]
                                self.segments[j] = self.segments[k]
                                self.segments[k] = aux


                        elif (comparing_marker.action is MotionAction.REL_CONSTRAINTS
                              and current_marker.action is not MotionAction.REL_MARKER):

                            try:
                                if current_marker.value.start > comparing_marker.value.start:
                                    sort = False

                                    aux = self.segments[j]
                                    self.segments[j] = self.segments[k]
                                    self.segments[k] = aux
                            except:
                                if current_marker.action is MotionAction.INT_MARKER:
                                    sort = False

                                    aux = self.segments[j]
                                    self.segments[j] = self.segments[k]
                                    self.segments[k] = aux

                        else: break
                        k += 1
                        
                else: break
                j += 1
            

        #debugging
        '''print('\n\n')
        for i in range(0, self.segment_number):
            segment: MotionSegment = self.segments[i]

            match segment.action:
                case MotionAction.REL_MARKER:
                    print('REL_MARKER: {0}'.format(segment.value.value))
                case MotionAction.REL_CONSTRAINTS:
                    print('REL_CONSTRAINTS: {0}'.format(segment.value.start))
                case MotionAction.INT_MARKER:
                    print('INT_MARKER: {0}'.format(segment.value.value))
                case MotionAction.LINE:
                    print('LINE: {0}'.format(segment.value))
                case MotionAction.WAIT:
                    print('WAIT: {0}'.format(segment.value))
                case MotionAction.TURN:
                    print('TURN: {0}'.format(segment.value))

        print('\n\n')'''

    def __find_last_marker(self, start_index):
        for i in range(start_index, self.segment_number):
            action = self.segments[i].action

            if (action is MotionAction.LINE or
                action is MotionAction.TO_POINT or
                action is MotionAction.TO_POSE or
                action is MotionAction.TO_POINT_CONSTANT_HEAD or
                action is MotionAction.TO_POSE_CONSTANT_HEAD or
                action is MotionAction.TO_POSE_LINEAR_HEAD):

                return i - 1
        
        return self.segment_number - 1

    def __organize(self):
        #basically making sure that every linear segment is followed by markers, no space between
        #   if a markers exist
        last_marker_index = self.__find_last_marker(self.iterator)



        index = self.iterator - 1

        while index > -1:
            if (self.segments[index].action is MotionAction.LINE or
                self.segments[index].action is MotionAction.WAIT):
                break

            elif (self.segments[index].action is not MotionAction.REL_CONSTRAINTS and
                  self.segments[index].action is not MotionAction.REL_MARKER and
                  self.segments[index].action is not MotionAction.INT_MARKER):
                #switch

                aux = self.segments[index]
                self.segments[index] = self.segments[last_marker_index]
                self.segments[last_marker_index] = aux

                self.iterator -= 1
                last_marker_index -= 1

            index -= 1
        
        return index

    def __should_build(self):
        # between some markers and a line segments --> nuh uh
        #   should've searched upwards for a line and down for markers
        #   but I'm going to search just for markers
        #   deal with it.

        for i in range(self.iterator + 1, self.segment_number):
            if (self.segments[i].action is MotionAction.LINE or
                self.segments[i].action is MotionAction.TO_POINT or
                self.segments[i].action is MotionAction.TO_POSE or
                self.segments[i].action is MotionAction.TO_POINT_CONSTANT_HEAD or
                self.segments[i].action is MotionAction.TO_POSE_CONSTANT_HEAD or
                self.segments[i].action is MotionAction.TO_POSE_LINEAR_HEAD or
                self.segments[i].action is MotionAction.WAIT):

                return True
            
            elif (self.segments[i].action is MotionAction.REL_CONSTRAINTS or
                  self.segments[i].action is MotionAction.REL_MARKER or
                  self.segments[i].action is MotionAction.INT_MARKER):
                
                return False
            
        return True

    def __erase_all_linear_segments_after(self):
        index = self.iterator + 1

        while index < self.segment_number:
            if self.segments[index].action is MotionAction.LINE:
                self.segments.pop(index)
                self.segment_number -= 1

                index += 1
            else: break




    def __isBugged(self):
        last = None
        for each in self.segments:
            if last is not None:
                if last + 1 == each.start_time:
                    last = each.end_time
                else: return True
            else: last = each.end_time
        
        return False
    