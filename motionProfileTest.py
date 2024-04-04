from ev3sim.Pathing.MotionProfile import *
from ev3sim.Pathing.turnDeg import *
from ev3sim.core import *
import pygame

pygame.init()

dist = toRadians(180)
vel = math.radians(90)
accel = math.radians(50)
decel = math.radians(50)

profile = TrapezoidalProfile(distance = dist, max_vel = vel, acc = accel, dec = decel)

sim = Simulator()
sim.manual_control.set(False)


while profile.isBusy:
    values = profile.calculate(pygame.time.get_ticks())

    speeds = sim.robot.kinematics.inverseKinematics(0, values[1])

    sim.robot.setWheelPowers(speeds[0], speeds[1])
    sim.update()
    print("profile:", profile.dt)
    print("    ")
    print("    ")


while sim.RUNNING():
    sim.update()

#turnDeg(300, sim)
