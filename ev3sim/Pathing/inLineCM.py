from ev3sim.Components.Controllers.PIDController import *
from ev3sim.Components.BetterClasses.mathEx import *
from Constants.constants import *
from ev3sim.Pathing.turnDeg import *
from ev3sim.core import *


def inLineCM(cm, simulator: Simulator, chained = False,
            threshold = 0.1, 
            sensitivity = 1, 
            correctHeading = True, tangential_angle = None,
            interpolating = False, accelerating = False,
            draw_trail = True, hide_trail = False):
    
    simulator.robot.draw_trail = draw_trail
    simulator.robot.hide_trail = hide_trail
    simulator.manual_control = False

    threshold = abs(threshold)
    sensitivity = abs(sensitivity)

    if cm < 0:
        direction_sign = -1
    else: direction_sign = 1
    cm = abs(cm)

    pose = simulator.robot.pose

    if not tangential_angle == None:
        facing_angle = normalizeDegrees(tangential_angle)
    else: facing_angle = pose.head
    

    if not interpolating and abs(facing_angle - pose.head) > 0.4:
        turnDeg(facing_angle, simulator)

    
    head_controller = PIDController(kP = kP_correction_agresive, kD = kD_correction, kI = 0)
    fwd_controller = PIDController(kP = kP_fwd, kD = 0, kI = 0)
    max_forward = fwd_controller.calculate(cm) + signum(cm) * kS_fwd
    simulator.robot.zeroDistance()
    isBusy = True


    while isBusy: 
        simulator.update()
        pose = simulator.robot.pose


        fwd_error = cm - simulator.robot.distance
        fwd_error_abs = abs(fwd_error)
        forward = (fwd_controller.calculate(fwd_error) + signum(cm) * kS_fwd)
        forward = direction_sign * forward / max_forward * cmToPixels(simulator.robot.max_vel)


        if correctHeading:

            if interpolating:
                kP = kP_interpolating
            elif fwd_error_abs < forward_threshold:
                kP = kP_correction_mild
            else: kP = kP_correction_agresive

            head_controller.setCoefficients(kP = kP)
            head_error = findShortestPath(facing_angle, pose.head)
            correction = head_controller.calculate(head_error)
        
        else: correction = 0


        if fwd_error_abs <= threshold:
            isBusy = False
        else: simulator.robot.setWheelPowers(left = forward - correction, right = forward + correction, 
                            sensitivity = sensitivity, accelerating = accelerating)
        

    if not chained:
        if abs(head_error) > 0.4:
            turnDeg(facing_angle, simulator, chained = chained)

        simulator.manual_control = True
        simulator.robot.setWheelPowers(0, 0)
    
    