
from ev3sim.Components.BetterClasses.mathEx import *

from ev3sim.Trajectory.feedforward import *
from ev3sim.Trajectory.feedback import *
from ev3sim.Trajectory.builder import *
from ev3sim.core import *

import matplotlib.pyplot as plt


def get_derivative(t: List[int], vel: List[float]):
    if len(vel) > 1:
        dt = (t[-1] - t[-2]) / 1000 #ms to s
        dv = vel[-1] - vel[-2]
            
        if dt != 0:
            accel = dv / dt
            if abs(accel) > max(constrains.ACC, abs(constrains.DEC)):
                if accel < 0:
                    accel = constrains.DEC
                else: accel = constrains.ACC
            return accel
    return 0


constrains = Constrains(dec = -5)
traj1 = (TrajectoryBuilder(start_pose = Pose(-50, -100, 0), constrains = constrains)
              .inLineCM(50)
              .inLineCM(50)
              .build())



traj = traj1

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
segment = traj.segments[0]
segment_time = segment.end_time
segments_length = len(traj.segments)



print(' ')
print('computing graph...')

while iterator < segments_length:    
    if trajectory_time > segment_time:
        iterator += 1
        
        if not iterator == segments_length:
            segment = traj.segments[iterator]
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

plt.plot(time_points, left_vel_points, color = 'green', linewidth = 3)
plt.axhline(0, color = 'white', linewidth = 0.5)



plt.subplot(2, 2, 2)
plt.title('{0} wheel VELOCITY'.format('right'), fontsize = 22)
plt.xlabel('time (ms)', fontsize = 14)
plt.ylabel('velocity (cm / s)', fontsize = 14)

plt.plot(time_points, right_vel_points, color = 'green', linewidth = 3)
plt.axhline(0, color = 'white', linewidth = 0.5)



#plot derivative

plt.subplot(2, 2, 3)
plt.title('{0} wheel ACCELERATION'.format('left'), fontsize = 22)
plt.xlabel('time (ms)', fontsize = 14)
plt.ylabel('acceleration (cm / s^2)', fontsize = 14)

plt.plot(time_points, left_accel_points, color = 'red', linewidth = 3)
plt.axhline(0, color = 'white', linewidth = 0.5)



plt.subplot(2, 2, 4)
plt.title('{0} wheel ACCELERATION'.format('right'), fontsize = 22)
plt.xlabel('time (ms)', fontsize = 14)
plt.ylabel('acceleration (cm / s^2)', fontsize = 14)

plt.plot(time_points, right_accel_points, color = 'red', linewidth = 3)
plt.axhline(0, color = 'white', linewidth = 0.5)



plt.tight_layout()
plt.subplots_adjust(wspace = 0.15, hspace = 0.4)


#plot velocity profile

plt.figure(figsize=(10, 5), facecolor = 'black')
plt.style.use('dark_background')

plt.plot(time_points, velocity, color = 'purple', linewidth = 7)
plt.axhline(0, color = 'white', linewidth = 0.5)

plt.tight_layout()
plt.show()