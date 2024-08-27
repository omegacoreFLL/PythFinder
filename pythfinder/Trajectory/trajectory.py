from pythfinder.Trajectory.Segments.Primitives.generic import *
from pythfinder.Trajectory.Markers import *

from pythfinder.Trajectory.trajectoryGenerator import *
from pythfinder.Trajectory.trajectoryFollower import *
from pythfinder.Trajectory.trajectoryGrapher import *

class Trajectory():
    def __init__(self,
                 sim: Simulator,
                 motion_states: List[MotionState],
                 markers: List[FunctionMarker]) -> None:
        
        self.sim = sim
        self.STATES = motion_states
        self.MARKERS = markers

        self.TIME = self.STATES[-1].time

        self.trajGenerator = TrajectoryGenerator(sim, motion_states, markers)
        self.trajFollower = TrajectoryFollower(sim, motion_states, markers)
        self.trajGrapher = TrajectoryGrapher(sim, motion_states)

    # generates a .txt file with wheel velocities
    def generate(self, 
                 file_name: str,
                 steps: int = 1,
                 wheel_speeds: bool = True,
                 separate_lines: bool = False):
        
        if self.TIME <= 0:
            print("\n\ncan't generate data from an empty trajectory")
            return None
        
        print('\n\nwriting precious values into * {0}.txt * ...'.format(file_name))

        if wheel_speeds:
            self.trajGenerator.generate_wheel_speeds(file_name, steps, separate_lines)
        else: self.trajGenerator.generate_chassis_speeds(file_name, steps, separate_lines)

        print('\n\ndone writing in * {0}.txt * file :o'.format(file_name))

    def graph(self,
              connect: bool = False,
              velocity: bool = True,
              acceleration: bool = True,
              wheel_speeds: bool = True):
        
        if self.TIME <= 0: 
            print("\n\ncan't graph an empty trajectory")
            return None

        if not (velocity or acceleration):
            print("\n\nno velocity: checked")
            print("no acceleration: checked")
            print("wait... what am I supposed to graph then???")
            print("\nyour greatest dreams and some pizza, right?")
            return None
        
        print('\n\ncomputing graph...')

        if wheel_speeds:
            self.trajGrapher.graph_wheel_speeds(connect, velocity, acceleration)
        else: self.trajGrapher.graph_chassis_speeds(connect, velocity, acceleration)
    
    def follow(self,
               perfect: bool = True, 
               wait: bool = True, 
               steps: int = None):
        
        if self.TIME == 0: 
            print("\n\ncan't follow an empty trajectory")
            return None
        
        print('\n\nFOLLOWING TRAJECTORY...')

        self.trajFollower.follow(perfect, wait, steps)

        print('\n\nTRAJECTORY COMPLETED! ;)')