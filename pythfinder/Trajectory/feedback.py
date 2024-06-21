from pythfinder.Components.Controllers.PIDController import *
from pythfinder.Components.BetterClasses.mathEx import *
from pythfinder.Components.Constants.constants import *
from pythfinder.core import *

# file simulating feedback movements.
#
# because it's a simulator, we could've used feedforward for turning also,
#   but the scope of this implementation was to mimic as best as we could
#   the real behaviour of the robot. It's the reason why the robot does allways
#   turn ~0.1° off.
#
# this uses a PID controller to turn the robot separately from the trajectory
#   generated with feedback calculations.

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
        turn = turn / (max_turn + EPSILON) * simulator.constants.cmToPixels(0.3 * simulator.robot.constraints.head.MAX_VEL / 2 
                                                                * simulator.robot.constraints.TRACK_WIDTH) * 1.4

        if abs(head_error) <= threshold:
            isBusy = False
        else: simulator.robot.setVelocities(ChassisState(Point(), turn))
    
    simulator.robot.setVelocities(ChassisState())