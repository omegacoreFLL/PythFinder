from pythfinder import *

sim = Simulator(kinematics = MecanumKinematics(default_track_width, Point(0, 0)))
    



trajectory = (TrajectoryBuilder(sim)
              .toPoint(Point(30, 10))
              .build())

#trajectory.generate(sim, "ceva", steps = 6)
trajectory.follow(sim)



while sim.RUNNING():
    sim.update()
