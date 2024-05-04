from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.builder import *
from ev3sim.core import *

trajectory = (TrajectoryBuilder(start_pose = Pose(-47, 97, -45), constrains = Constrains(vel = 27.7, acc = 27.7, dec = -27.7))
              .inLineCM(75)
                    .addRelativeDisplacementMarker(35, lambda: print('womp womp'))
                    .addRelativeDisplacementMarker(-12, lambda: print('motor goes brr'))
                    .addConstrainsRelativeDisplacement(start = 30, constrains = Constrains(vel = 10, dec = -50))
                    .addConstrainsRelativeDisplacement(start = 36, constrains = Constrains(vel = 27.7, acc = 35, dec = -30))
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
                    .addRelativeTemporalMarker(-1, lambda: print("the party's over :<"))
              .turnDeg(80)
              .inLineCM(-120)
              .build())

sim = Simulator()

'''constrains = Constrains(dec = -30)
traj1 = (TrajectoryBuilder(start_pose = Pose(0, -100, 90), constrains = constrains)
              .inLineCM(200)
                    .addRelativeDisplacementMarker(50, lambda: print(':('))
                    .interruptDisplacement(50)
              .wait(2000)
              .turnDeg(20)
                    .addConstrainsRelativeDisplacement(start = 85, constrains = Constrains(vel = 15, acc= 31, dec = -30))
              .build())'''


#for each in trajectory.segments:
#    print(each.start_time, each.end_time)


trajectory.follow(sim, perfect = False)

while sim.RUNNING():
    sim.update()

