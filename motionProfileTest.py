from ev3sim.Pathing.MotionProfile import *
from ev3sim.Pathing.turnDeg import *
from ev3sim.core import *
import pygame

pygame.init()

dist = toRadians(320+260)
vel = math.radians(80)
accel = math.radians(20)
decel = math.radians(20)


angular_profile = TrapezoidalProfile(distance = dist, max_vel = vel, acc = accel, dec = decel)
linear_profile = TrapezoidalProfile(distance = -200, max_vel = 50, acc = 5)

sim = Simulator()

sim.robot.target_head = 0
sim.robot.setPoseEstimate(Pose())
sim.manual_control.set(False)
sim.robot.trail.draw_trail.set(True)

#pygame.time.wait(4000)

while angular_profile.isBusy or linear_profile.isBusy:
    time = pygame.time.get_ticks()
    if angular_profile.isBusy:
        ang_value = angular_profile.calculate(time)[1]
    else: ang_value = 0
    
    if linear_profile.isBusy:
        linear_value = linear_profile.calculate(time)[1]
        
    else: linear_value = 0


    sim.robot.setVelocities(linear_value, ang_value)
    sim.update()

print(sim.robot.distance)

sim.robot.setVelocities(0, 0)
sim.robot.trail.draw_trail.set(False)
sim.robot.target_head = sim.robot.pose.head

sim.manual_control.set(True)

while sim.RUNNING():
    sim.update()

