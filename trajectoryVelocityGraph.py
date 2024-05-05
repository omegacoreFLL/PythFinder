from ev3sim.Trajectory.builder import *

import matplotlib.pyplot as plt


# Demo python code for plotting wheel velocities / accelerations usint matplot.
# HOW IT WORKS:
#       After computing a trajectory (explained in 'trajectoryGenerator.py'), it uses the collected data in
#   the motion segments available, looping through it all to create separate lists for velocities and accelerations,
#   as well as for the time. The derivatives are calculated algebraically with the definition: dx/dy
#       The boolean CONNECT specifies if you want to draw lines between the plotted dots or not. Setting it to 
#   False will enable you to spot discontinuities is graphs. If you have discontinuities on the velocity graph and
#   you didn't interrupt intentionally any segment, then there's an issue with the code, please report it!
#       Then we simply set the theme, colors, units, layout and names for the graphs!
#
# It's used to check velocity discontinuity (with a trapezoidal profile, the acceleration is always discontinuous),
#   or just to better understand how motion profiles work


CONNECT = False
START_POSE = Pose(0, -100, 0)
START_CONSTRAINS = constrains = Constrains(dec = -30)

trajectory = (TrajectoryBuilder(START_POSE, START_CONSTRAINS)
              .inLineCM(130)
              .wait(3000)
                    .addRelativeTemporalMarker(-1, lambda: idle)
                    .addConstrainsDisplacement(start = 40, end = 60, constrains = Constrains(vel = 15))
              .build())

 


def get_derivative(t: List[int], vel: List[float]):
    if len(vel) > 1:
        dt = (t[-1] - t[-2]) / 1000 #ms to s
        dv = vel[-1] - vel[-2]
            
        if dt != 0:
            accel = dv / dt
            return accel
    return 0

iterator = 0
increment = 1
trajectory_time = 0

time_points = []
left_vel_points = []
right_vel_points = []

left_accel_points = []
right_accel_points = []
velocity = []

k = TankKinematics(Constrains().TRACK_WIDTH)
segment = trajectory.segments[0]
segment_time = segment.end_time
segments_length = len(trajectory.segments)



print(' ')
print('computing graph...')

while iterator < segments_length:    
    if trajectory_time > segment_time:
        iterator += 1
        
        if not iterator == segments_length:
            segment = trajectory.segments[iterator]
            segment_time = segment.end_time
        else:
            break

    state = segment.get(trajectory_time)

    VEL, ANG_VEL = state.velocities
    left, right = k.inverseKinematics(VEL, ANG_VEL)
        
    velocity.append(VEL)
    left_vel_points.append(left)
    right_vel_points.append(right)
    time_points.append(trajectory_time)

    if segment.action is not MotionAction.LINE:
        left_accel_points.append(0)
        right_accel_points.append(0)
    else:
        left_accel_points.append(get_derivative(time_points, left_vel_points))
        right_accel_points.append(get_derivative(time_points, right_vel_points))

    trajectory_time += increment


#be sure that accel line ends on the x axis
for _ in range(1):
    velocity.append(0)
    left_vel_points.append(0)
    right_vel_points.append(0)
    left_accel_points.append(0)
    right_accel_points.append(0)

    time_points.append(time_points[-1] + 1)


print('done!')

print(' ')
print('plotting...')



#plot velocities

plt.figure(figsize=(13, 7), facecolor = 'black')
plt.style.use('dark_background')

plt.subplot(2, 2, 1)
plt.title('{0} wheel VELOCITY'.format('left'), fontsize = 22)
plt.xlabel('time (ms)', fontsize = 14)
plt.ylabel('velocity (cm / s)', fontsize = 14)

if CONNECT:
    plt.plot(time_points, left_vel_points, color = 'green', linewidth = 3)
else: plt.scatter(time_points, left_vel_points, color = 'green', s = 1)

plt.axhline(0, color = 'white', linewidth = 0.5)



plt.subplot(2, 2, 2)
plt.title('{0} wheel VELOCITY'.format('right'), fontsize = 22)
plt.xlabel('time (ms)', fontsize = 14)
plt.ylabel('velocity (cm / s)', fontsize = 14)

if CONNECT:
    plt.plot(time_points, right_vel_points, color = 'green', linewidth = 3)
else: plt.scatter(time_points, right_vel_points, color = 'green', s = 1)

plt.axhline(0, color = 'white', linewidth = 0.5)



#plot derivative

plt.subplot(2, 2, 3)
plt.title('{0} wheel ACCELERATION'.format('left'), fontsize = 22)
plt.xlabel('time (ms)', fontsize = 14)
plt.ylabel('acceleration (cm / s^2)', fontsize = 14)

if CONNECT:
    plt.plot(time_points, left_accel_points, color = 'red', linewidth = 3)
else: plt.scatter(time_points, left_accel_points, color = 'red', s = 1)

plt.axhline(0, color = 'white', linewidth = 0.5)



plt.subplot(2, 2, 4)
plt.title('{0} wheel ACCELERATION'.format('right'), fontsize = 22)
plt.xlabel('time (ms)', fontsize = 14)
plt.ylabel('acceleration (cm / s^2)', fontsize = 14)

if CONNECT:
    plt.plot(time_points, right_accel_points, color = 'red', linewidth = 3)
else: plt.scatter(time_points, right_accel_points, color = 'red', s = 1)

plt.axhline(0, color = 'white', linewidth = 0.5)

plt.subplots_adjust(wspace = 0.15, hspace = 0.4)




plt.tight_layout()
plt.show()