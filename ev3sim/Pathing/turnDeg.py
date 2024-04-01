from ev3sim.Components.Controllers.PIDController import *
from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.constants import *
from ev3sim.core import *


def turnDeg(deg, simulator, 
            threshold = 0.1, 
            sensitivity = 1,
            chained = False):
    
    simulator.manual_control = False
    threshold = abs(threshold)
    sensitivity = abs(sensitivity)
    pose = simulator.robot.pose


    deg = normalizeDegrees(deg)
    head_error = findShortestPath(deg, pose.head)

    head_controller = PIDController(kP = kP_head, kD = kD_head, kI = 0)
    max_turn = abs(head_controller.calculate(head_error) + signum(head_error) * kS_head)
    isBusy = True


    while isBusy:
        simulator.update()
        pose = simulator.robot.pose

        head_error = findShortestPath(deg, pose.head)

        turn = head_controller.calculate(head_error) + signum(head_error) * kS_head
        turn = turn / max_turn * velocity_multiplier

        print(turn)

        if abs(head_error) <= threshold:
            isBusy = False
        else: simulator.robot.setWheelPowers(left = -turn, right = turn, sensitivity = sensitivity)
    

    if not chained:
        simulator.robot.setWheelPowers(0, 0)
        simulator.manual_control = True