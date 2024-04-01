from ev3sim.Pathing.motionProfile import *
from ev3sim.Pathing.turnDeg import *
from ev3sim.Pathing.inLineCM import *
from ev3sim.core import *
import pygame

def startMultiplierTuner(simulator: Simulator, distance, multiplier = robot_multiplier):
    pygame.init()
    
    simulator.manual_control = False
    profile = TrapezoidalProfile(distance = distance, max_vel = robot_velocity, 
                                 acc = robot_acceleration, dec = robot_deceleration)

    values = None
    actual_distance = 0
    
    while profile.isBusy:
        simulator.update()
        values = profile.calculate(pygame.time.get_ticks())

        wheel_speeds = cmToPixels(values[1]) * multiplier
        simulator.robot.setWheelPowers(wheel_speeds, wheel_speeds)
    
    actual_distance = simulator.robot.pose.x / 10
    print("recommended multiplier: {:.4f}".format(multiplier * abs(distance / actual_distance)))
        