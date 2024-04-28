from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.builder import *
from ev3sim.core import *

start, end = Point(0, 0), Point(15, 20)
start_tan, end_tan = Point(0, 5), Point(10, 0)

sim = Simulator()

def testFun():
    sim.robot.trail.draw_trail.set(False)
    print('\nstop drawing')

def testFun2():
    print('\nwe back')
    sim.robot.trail.draw_trail.set(True)


trajectory = (TrajectoryBuilder(start_pose = Pose(0, 30, 0))
              .toPose(Pose(20, -40, 180))
              .addRelativeTemporalMarker(ms = -2000, fun = testFun)
              .wait(3000)
              .build())

trajectory.follow(sim, perfect = False)

while sim.RUNNING():
    sim.update()

