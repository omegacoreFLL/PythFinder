from ev3sim.Trajectory.builder import *
from ev3sim.core import *

# Demo python code for visualising a trajectory.
#
# CAUTION: the actual mat size could be slightly off unit, please be sure you set the right size in the
#     'table.py' file.
#
# HOW IT WORKS:
#           For the logic behind the trajectory construction, read the 'trajectoryGenerator.py' file. 
#     This code works the same until the generating step, this file would NOT generate usable values 
#     for the actual robot.
#
#           For the following, you have two options: PERFECT and REAL following. The perfect following
#     loops through each timestamp (with a specified step between them, default is 40) and displays the
#     robot on the screen at the exact position associated with the afferent Motion State. The real 
#     following gives the velocity and angular velocity data to the robot, it's a perfect replica
#     of how the actual following on the bot occurs. The real following appears smoother, but it's 
#     allways off with ~0.3 cm and 0.1°. The turning is also done with a pid controller, so it's not
#     instant like in the perfect mode.
#           Another useful parameter in the '.follow()' function is the 'wait' parameter, a boolean
#     for waiting to load the simulator window before starting the trajectory. It makes a big difference
#     when you set the perfect follow with a large number of steps.
#
# As a personal recommendation, it's best to use the real mode, just for better visualisation.


PERFECT_STEPS = 40
PERFECT_FOLLOWING = False
START_POSE = Pose(-47, 97, -45)
START_CONSTRAINS = Constrains(vel = 27.7, acc = 27.7, dec = -27.7)

trajectory = (TrajectoryBuilder(START_POSE, START_CONSTRAINS)
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
trajectory.follow(sim, PERFECT_FOLLOWING, PERFECT_STEPS)


while sim.RUNNING():
    sim.update()

