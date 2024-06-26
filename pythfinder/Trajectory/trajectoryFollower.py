from pythfinder.Trajectory.Segments.Primitives.generic import *
from pythfinder.Trajectory.Control.feedback import *
from pythfinder.Trajectory.Markers import *

import threading


class TrajectoryFollower():
    def __init__(self, 
                 sim: Simulator,
                 motion_states: List[MotionState],
                 markers: List[FunctionMarker]):
        
        self.head_controller = PIDController(PIDCoefficients(kP = kP_head, kD = kD_head, kI = 0))
        self.states = motion_states
        self.markers = markers

        self.start_pose = motion_states[0].pose
        self.end_pose = motion_states[-1].pose
        self.time = motion_states[-1].time + 1

        self.perfect_increment = 20
        self.marker_iterator = 0

        self.sim = sim

    def __wait(self, ms: int):
        for _ in range(ms):
            self.sim.update()
    
    def __checkForRemainingMarkers(self):
        while self.marker_iterator < len(self.markers):
            self.sim.update()
            marker = self.markers[self.marker_iterator]

            if marker.time > self.time:
                print('\nThe marker number {0} exceded the time limit of {1}ms with {2}ms'
                      .format(self.marker_iterator + 1, self.time, marker.time - self.time))

            threading.Thread(target = marker.do).start()
            self.marker_iterator += 1

    def __checkMarker(self, time: int):
        if not self.marker_iterator < len(self.markers):
            return None
        
        marker = self.markers[self.marker_iterator]

        if time >= marker.time:
                threading.Thread(target = marker.do).start()
                self.marker_iterator += 1



    def follow(self, perfect: bool = True, 
               wait: bool = True, steps: int = None) -> None:

        if steps is not None:
            self.perfect_increment = steps
        self.marker_iterator = 0

        self.sim.autonomus(Auto.ENTER)
        self.sim.robot.setPoseEstimate(self.start_pose)

        if wait: self.__wait(200)

        if perfect:
            self.__perfectFollow()
        else: self.__realFollow()

        self.__checkForRemainingMarkers()
        self.sim.autonomus(Auto.EXIT)

    def __perfectFollow(self) -> None:
        rg = int(len(self.states) / self.perfect_increment)

        for t in range(rg):
            state = self.states[t * self.perfect_increment]

            self.__checkMarker(state.time)
            self.sim.robot.setPoseEstimate(state.pose)
            self.sim.update()

    def __realFollow(self) -> None:
        start_time = getTimeMs()
        time = 0

        while time < self.time:
            time = getTimeMs() - start_time

            try: state = self.states[time]
            except: continue

            self.__checkMarker(state.time)
            self.sim.robot.setVelocities(state.velocities)
            self.sim.update()
        
        self.sim.robot.setVelocities(ChassisState())
