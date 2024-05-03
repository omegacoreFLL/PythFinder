from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.builder import *



trajectory = (TrajectoryBuilder(start_pose = Pose(-47, 97, -45), constrains = Constrains(vel = 27.7, acc = 27.7, dec = -27.7))
              .inLineCM(150)
                    .addConstrainsDisplacement(start = 50, end = 90, constrains = Constrains(vel = 10, acc = 10, dec = -15))
              .build())

print(trajectory.trajectoryTime)

trajectory.generate(file_name = 'test', steps = 6)
#_, _, _, states = trajectory.recieve(file_name = 'test')