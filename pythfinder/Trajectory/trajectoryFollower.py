from pythfinder.Trajectory.Kinematics.SwerveKinematics import *
from pythfinder.Trajectory.trajectoryFragments import *
from pythfinder.Trajectory.Control.feedforward import *
from pythfinder.Trajectory.Control.feedback import *
from pythfinder.Trajectory.splines import *
from pythfinder.Trajectory.marker import *

import matplotlib.pyplot as mplt
import threading


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
