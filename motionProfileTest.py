from ev3sim.Pathing.motionProfile import *
import pygame

pygame.init()

dist = 50
vel = 20
accel = 5
deccel = -5

profile = TrapezoidalProfile(distance = dist, max_vel = vel, accel = accel, deccel = deccel)

while profile.isBusy:
    print(profile.calculate(pygame.time.get_ticks()))
