from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.builder import *



trajectory = (TrajectoryBuilder(start_pose = Pose(-47, 97, -45), constrains = Constrains(vel = 27.7, acc = 27.7, dec = -27.7))
              .inLineCM(75)
                    .addRelativeDisplacementMarker(-2, idle)
                    .addRelativeDisplacementMarker(-1, lambda: print('motor goes brr'))
                    .interruptDisplacement(-25)
              .wait(2700)
                    .addRelativeTemporalMarker(-1, lambda: print('motor goes :('))
              .inLineCM(-30)
              .turnDeg(90)
              .inLineCM(-20)
              .turnDeg(105)
              .inLineCM(-47)
              .turnDeg(20)
              .wait(1200)
                    .addRelativeTemporalMarker(0, idle)
                    .addRelativeTemporalMarker(1199, idle)
              .turnDeg(80)
              .inLineCM(-120)
              .build())

print(trajectory.trajectoryTime)

trajectory.generate(file_name = 'test', steps = 6)
#_, _, _, states = trajectory.recieve(file_name = 'test')