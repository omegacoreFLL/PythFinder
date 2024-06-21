from pythfinder import *

sim = Simulator()

traj = (TrajectoryBuilder(sim)
        .toPoint(Point(10, 30))
        .build())

traj.follow(sim, perfect = True, steps = 5)

while sim.RUNNING():
    sim.update()
