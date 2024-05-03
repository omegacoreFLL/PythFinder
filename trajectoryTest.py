from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.builder import *
from ev3sim.core import *

'''trajectory = (TrajectoryBuilder(start_pose = Pose(-47, 97, -45), constrains = Constrains(vel = 27.7, acc = 27.7, dec = -27.7))
              .inLineCM(75)
                    .addRelativeDisplacementMarker(-15, lambda: print('womp womp'))
                    .addRelativeDisplacementMarker(-1, lambda: print('motor goes brr'))
                    .interruptDisplacement(55)
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
              .build())'''

constrains = Constrains(dec = -20)
traj1 = (TrajectoryBuilder(start_pose = Pose(0, -100, 90), constrains = constrains)
              .inLineCM(90)
              .turnDeg(0)
              .inLineCM(60)
                    .interruptDisplacement(40)
                    .addConstrainsDisplacement(start = 40, end = 90, constrains = Constrains(vel = 10, acc = 10, dec = -15))
                    .addConstrainsDisplacement(start = 54, constrains = Constrains(vel = 20, acc= 31, dec = -17))
                    .addRelativeTemporalMarker(2000, lambda: print('helooo'))
              .build())


#for each in trajectory.segments:
#    print(each.start_time, each.end_time)

sim = Simulator()
traj1.follow(sim, perfect = False)

while sim.RUNNING():
    sim.update()

