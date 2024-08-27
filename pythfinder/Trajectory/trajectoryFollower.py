from pythfinder.Trajectory.Segments.Primitives.generic import *
from pythfinder.Trajectory.Markers import *
from pythfinder.core import *

import threading


class Auto(Enum):
    ENTER = auto()
    EXIT = auto()

class TrajectoryFollower():
    def __init__(self, 
                 sim: Simulator,
                 motion_states: List[MotionState],
                 markers: List[FunctionMarker]):
        
        self.states = motion_states
        self.markers = markers

        self.start_pose = motion_states[0].pose
        self.end_pose = motion_states[-1].pose
        self.time = motion_states[-1].time + 1

        self.perfect_increment = 10
        self.marker_iterator = 0

        self.sim = sim

    def __wait(self, loops: int):
        for _ in range(loops):
            self.sim.update()
    
    def __check_for_remaining_markers(self):
        while self.marker_iterator < len(self.markers):
            self.sim.update()
            marker = self.markers[self.marker_iterator]

            if marker.time > self.time:
                print('\n\nThe marker number {0} exceded the time limit of {1}ms with {2}ms'
                      .format(self.marker_iterator + 1, self.time, marker.time - self.time))

            threading.Thread(target = marker.do).start()
            self.marker_iterator += 1

    def __check_marker(self, time: int):
        if not self.marker_iterator < len(self.markers):
            return None
        
        marker = self.markers[self.marker_iterator]

        if time >= marker.time:
                threading.Thread(target = marker.do).start()
                self.marker_iterator += 1



    def autonomus(self, do: Auto):
        match do:
            case Auto.ENTER:
                print("\n\nentering autonomus... ready?")

                self.sim.manual_control.set(False)
                self.sim.presets.WRITING.set(False)
                self.sim.robot.trail.draw_trail.set(True)

                self.sim.constants.ERASE_TRAIL.set(False)
                self.sim.constants.SCREEN_BORDER.set(False)

                self.sim.robot.zero()

            case Auto.EXIT:
                self.sim.manual_control.set(True)
                self.sim.presets.WRITING.set(True)
                self.sim.robot.trail.draw_trail.set(False)

                self.sim.constants.ERASE_TRAIL.set(True)
                self.sim.constants.SCREEN_BORDER.set(True)

                print("\n\ntele-op just started! ---- ding ding 🔔")            
            case _:
                pass

        self.sim.menu.check()



    def follow(self, 
               perfect: bool = True, 
               wait: bool = True, 
               steps: int = None) -> None:

        if steps is not None:
            self.perfect_increment = steps
        self.marker_iterator = 0

        self.sim.update()
        self.autonomus(Auto.ENTER)
        self.sim.robot.set_pose_estimate(self.start_pose)
        

        if wait: self.__wait(40)

        if perfect:
            self.__perfect_follow()
        else: self.__real_follow()

        self.__check_for_remaining_markers()
        self.autonomus(Auto.EXIT)

    def __perfect_follow(self) -> None:
        rg = int(len(self.states) / self.perfect_increment)

        for t in range(rg):
            state = self.states[t * self.perfect_increment]

            self.__check_marker(state.time)
            self.sim.robot.set_pose_estimate(state.pose)
            self.sim.update()

    def __real_follow(self) -> None:
        start_time = pygame.time.get_ticks()
        time = 0

        while time < self.time:
            time = pygame.time.get_ticks() - start_time

            try: state = self.states[time]
            except: continue

            self.__check_marker(state.time)
            self.sim.robot.set_velocities(state.velocities)
            self.sim.update()
        
        if self.sim.RUNNING():
            self.sim.robot.set_velocities(ChassisState())
