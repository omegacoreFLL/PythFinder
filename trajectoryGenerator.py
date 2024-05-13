from ev3sim.Trajectory.builder import *

# Demo python code for generating trajectory values into a '.txt' file.
# HOW IT WORKS:
#
#           The 'TrajectoryBuilder' object is a helper class for building values for a trajectory.
#     A TRAJECTORY is constructed from multiple MOTION SEGMENTS, describing a single intuitively
#     bounded part of the trajetory. Each of these segments are made of MOTION STATES, which 
#     represent the robot's state in a particular moment of the trajectory. These contains the
#     following information: 
#        - the TIME of the trajectory it's associated with
#        - the DISPLACEMENT (distance) of the trajectory
#        - the POSE of the robot
#        - VELOCITY and ANGULAR_VELOCITY, in a tuple
#        - a boolean needed for turning (as turning is different then the other segments)
#    
#           You can input two main types of data into the trajectory builder: MOVES and MARKERS. Moves are 
#     all literal motion functions, like '.inLineCM()', '.toPose()', '.wait()' etc. Markers are other. 
#     non-movement related functions, ranging from '.addRelativeTemporalMarker()' to '.interruptDisplacement()'
#           There are other type of methods (eg: '.turnDeg()', '.addConstrainsDisplacement()') which don't fit 
#     in any of these categories, but are treated as one of those, just in a more special way.
#
#           The idea is that, after all the input data is computed (see documentation for further explanations:
#     -- TODO -- ), we are left with a list of Motion Segments, with data needed to run the simulator. 
#     Transfering this data to the actual robot involves converting the necessary data into a '.txt' file. Because
#     the processor on the brick is old and struggles to read the values in a reasonable time interval, we did
#     the following optimizations:
#        - on the first line are the marker timestamps, sorted
#        - on the second line are the start and end poses (x, y, head)
#        - convert VELOCITY and ANGULAR_VELOCITY locally into powers for left and right wheels -> [-100, 100],
#          based on the REAL max velocity specified (in cm/s)
#        - don't encript DISPLACEMENT, POSE and TIME data (just the heading), you don't need it
#        - transform the boolean into integers
#        - specifying the number of consecutive appearances, to not write values more than once
#        - concatenate the boolean information after the appearance number
#        - writing the data on one single line
#        - introducing steps: instead of writing values for every ms, you can choose the spacing between
#          consecutive writing. It doesn't have a visible impact onto the robot's motion, because the
#          frequency is ~9ms between loops, so the robot couldn't use the values anyways. We insert this
#          value into the generated file too, to know how to cover the empty time spaces with copies of
#          the read values. It's the last value on the second line
#
#           After the generation is compleated, the values are pasted into the robot code, from where it
#     takes some reverse processing to get all these values into simplified versions of Motion States and
#     Trajectories. If the trajectory contains markers, you also need to specify functions to be executed 
#     for each one of them when reading.
#
#           Now that you have an intuition on how the generator works, give it a try! Here is provided a 
#     very simple example, you can modify it as you wish  


STEPS = 6
FILE_NAME = 'test'
START_POSE = Pose(0, -100, 0)
START_CONSTRAINS = Constrains(dec = -30)


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


trajectory.generate(FILE_NAME, STEPS)