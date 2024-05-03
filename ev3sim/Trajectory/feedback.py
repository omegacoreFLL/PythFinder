from ev3sim.Components.Controllers.PIDController import *
from ev3sim.Components.BetterClasses.mathEx import *
from ev3sim.Components.Constants.constants import *
from ev3sim.core import *


def turnDeg(deg, simulator: Simulator, 
            threshold = 0.1, 
            sensitivity = 1):
    
    threshold = abs(threshold)
    sensitivity = abs(sensitivity)
    pose = simulator.robot.pose

    deg = normalizeDegrees(deg)
    head_error = findShortestPath(deg, pose.head)

    head_controller = PIDController(PIDCoefficients(kP = kP_head, kD = kD_head, kI = 0))
    max_turn = abs(head_controller.calculate(head_error))
    isBusy = True

    while isBusy:
        simulator.update()
        pose = simulator.robot.pose

        head_error = findShortestPath(deg, pose.head)

        turn = head_controller.calculate(head_error)
        turn = turn / (max_turn + EPSILON) * simulator.constants.cmToPixels(0.3 * simulator.robot.constrains.MAX_ANG_VEL / 2 
                                                                * simulator.robot.constants.TRAIL_WIDTH) * 1.4

        if abs(head_error) <= threshold:
            isBusy = False
        else: simulator.robot.setVelocities(0, turn)
    
    simulator.robot.setVelocities(0, 0)