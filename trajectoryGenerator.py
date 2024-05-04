from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.builder import *


trajectory = (TrajectoryBuilder(start_pose = Pose(-47, 97, -45), constrains = Constrains(vel = 27.7, acc = 27.7, dec = -27.7))
              .inLineCM(75)
                    .addConstrainsRelativeDisplacement(start = 30, constrains = Constrains(vel = 10, dec = -50))
                    .addConstrainsRelativeDisplacement(start = 36, constrains = Constrains(vel = 27.7, acc = 35, dec = -30))
                    .addRelativeDisplacementMarker(35, lambda: print('womp womp'))
                    .addRelativeDisplacementMarker(63, lambda: print('motor goes brr'))
                    .interruptDisplacement(66)
              .wait(2600)
                    .addRelativeTemporalMarker(-1, lambda: print('motor goes :('))
              .inLineCM(-30)
              .turnDeg(90)
              .inLineCM(-20)
              .turnDeg(105)
              .inLineCM(-47)
              .turnDeg(20)
              .wait(1200)
                    .addRelativeTemporalMarker(0, lambda: print("spin'n'spin'n'spin.."))
                    .addRelativeTemporalMarker(1199, lambda: print("the party's over :<"))
              .turnDeg(80)
              .inLineCM(-120)
              .build())

print(trajectory.trajectoryTime)

trajectory.generate(file_name = 'test', steps = 6)
#_, _, _, states = trajectory.recieve(file_name = 'test')