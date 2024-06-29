from pythfinder.Trajectory.Segments import *
from pythfinder.Trajectory.Markers import *
from pythfinder.core import *

class TrajectoryGenerator():
    def __init__(self,
                 sim: Simulator,
                 motion_states: List[MotionState],
                 markers: List[FunctionMarker]
                 ):
        
        self.sim = sim
        self.STATES = motion_states
        self.MARKERS = markers
    
    def generateWheelSpeeds(self, file_name: str, steps: int = 1, separate_lines: bool = False):
        with open('{0}.txt'.format(file_name), "w") as f:

            # first layer --> marker times
            first_string = ''
            for marker in self.MARKERS:
                first_string += '{0} '.format(marker.time)
            
            f.write(first_string + '\n')
            
            # second layer --> steps
            f.write("{0}\n".format(steps))

            # third layer --> wheel velocities -- head -- nr of consecutive copies
            rg = int(len(self.STATES) / steps)
            t = 0

            while t <= rg:
                try: # basically you're out of the list
                    current_state = self.STATES[t * steps]
                except: break

                consecutive = 0
                try: # same stuff here
                    while current_state.isLike(self.STATES[t * steps]):
                        consecutive += 1
                        t += 1
                except: pass
                
                # write velocities for each wheel, acording to the kinematics
                robot_centric_vel = current_state.velocities.fieldToRobot(current_state.pose)
                wheel_states = self.sim.constants.kinematics.inverse(robot_centric_vel)

                if isinstance(self.sim.constants.kinematics, SwerveKinematics):
                    # add module angles too
                    line = ''.join("{0} {1} ".format((self.sim.robot.toMotorPower(state.VELOCITY), 2), round(state.ANGLE, 2)) for state in wheel_states)
                else:
                    line = ''.join(str(round(self.sim.robot.toMotorPower(state.VELOCITY), 2)) + " " for state in wheel_states)
                
                line = line + "{0} {1} ".format(
                    round(current_state.pose.head, 2), 
                    consecutive)
                
                if separate_lines:
                    line += "\n"
                        
                f.write(line)

    def generateChassisSpeeds(self, file_name: str, steps: int = 1, separate_lines: bool = False):

        with open('{0}.txt'.format(file_name), "w") as f:

            # first layer --> marker times
            first_string = ''
            for marker in self.MARKERS:
                first_string += '{0} '.format(marker.time)
            
            f.write(first_string + '\n')
            
            # second layer --> steps
            f.write("{0}\n".format(steps))

            # third layer --> VEL_X -- VEL_Y -- ANG_VEL -- head -- nr of consecutive copies
            rg = int(len(self.STATES) / steps)
            t = 0

            while t <= rg:
                try: # basically you're out of the list
                    current_state = self.STATES[t * steps]
                except: break

                consecutive = 0
                try: # same stuff here
                    while current_state.isLike(self.STATES[t * steps]):
                        consecutive += 1
                        t += 1
                except: break
                
                robot_centric_vel = current_state.velocities.fieldToRobot(current_state.pose)

                # write velocities for each wheel, acording to the kinematics
                line = '{0} {1} {2} {3} {4}'.format(
                    round(robot_centric_vel.VEL.x, 2),
                    round(robot_centric_vel.VEL.y, 2),
                    round(robot_centric_vel.ANG_VEL,2),
                    round(current_state.pose.head, 2),
                    consecutive)
                
                if separate_lines:
                    line += "\n"
                        
                f.write(line)
