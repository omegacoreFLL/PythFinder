from pythfinder import *

trajectory = (TrajectoryBuilder()
              .inLineCM(40)
              .turnDeg(90)
              .inLineCM(-70)
              .build())

sim = Simulator()
#trajectory.graph()
trajectory.follow(sim)

while sim.RUNNING():
    sim.update()
