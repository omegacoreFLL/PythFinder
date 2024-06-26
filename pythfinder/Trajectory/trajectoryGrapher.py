from pythfinder.Trajectory.Segments import *
from pythfinder.core import *

import matplotlib.pyplot as mplt

class TrajectoryGrapher():
    def __init__(self,
                 sim: Simulator,
                 motion_states: List[MotionState]
                 ):
        
        self.sim = sim
        self.STATES = motion_states

   
    
    def graphWheelSpeeds(self, connect: bool = False, velocity: bool = True, acceleration: bool = True):
        VEL = []
        ACC = []

        # get wheel speeds
        for state in self.STATES:
            robot_centric_vel = state.velocities.fieldToRobot(state.pose)
            wheel_speeds = self.sim.robot.kinematics.inverse(robot_centric_vel)

            for i in range(len(wheel_speeds)):
                try: VEL[i].append(wheel_speeds[i].VELOCITY)
                except: 
                    VEL.append([])
                    VEL[-1].append(wheel_speeds[i].VELOCITY)
        
        # make sure acc ends on the X axis
        for each in VEL: 
            each.append(0) 
            each.append(0)
        
        # get the time
        time = linspace(0, len(VEL[-1]), len(VEL[-1]))

        # get wheel accelerations
        for vel in VEL:
            ACC.append(self.__getDerivative(time, vel))
        


        mplt.style.use('dark_background')

        if acceleration:
            self.__plotWheelAccelerationWindow(time, ACC, connect, "red")
            mplt.tight_layout()

        if velocity:
            self.__plotWheelVelocityWindow(time, VEL, connect, "green")
            mplt.tight_layout()

        mplt.show()

    def __plotWheelVelocityWindow(self, t: List[int], vel: List[list],
                                  connect: bool, color: str):
        
        figure = mplt.figure(figsize = (7, 7), facecolor = 'black')
        figure.canvas.manager.set_window_title("Wheel velocities")

        columns = len(vel) / 2 if len(vel) % 2 == 0 else int(len(vel) / 2) + 1

        for i in range(len(vel)):
            nr = int(200 + 10 * columns + i + 1)

            ax = figure.add_subplot(nr)
            ax.set_xlabel('time (ms)', fontsize = 14)
            ax.set_ylabel('velocity (cm / s)', fontsize = 14)
            ax.set_title('wheel {0}'.format(i + 1))

            if connect:
                    ax.plot(t, vel[i], color = color, linewidth = 3)
            else: ax.scatter(t, vel[i], color = color, s = 1)

            ax.axhline(0, color = 'white', linewidth = 0.5)

    def __plotWheelAccelerationWindow(self, t: List[int], acc: List[list],
                                      connect: bool, color: str):
        
        figure = mplt.figure(figsize = (7, 7), facecolor = 'black')
        figure.canvas.manager.set_window_title("Wheel accelerations")

        columns = len(acc) / 2 if len(acc) % 2 == 0 else int(len(acc) / 2) + 1

        for i in range(len(acc)):
            nr = int(200 + 10 * columns + i + 1)

            ax = figure.add_subplot(nr)
            ax.set_xlabel('time (ms)', fontsize = 14)
            ax.set_ylabel('acceleration (cm / s^2)', fontsize = 14)
            ax.set_title('wheel {0}'.format(i + 1))

            if connect:
                    ax.plot(t, acc[i], color = color, linewidth = 3)
            else: ax.scatter(t, acc[i], color = color, s = 1)

            ax.axhline(0, color = 'white', linewidth = 0.5)



    def graphChassisSpeeds(self, connect: bool = False, velocity: bool = True, acceleration: bool = True):
        VEL_X = []
        VEL_Y = []
        ANG_VEL = []

        # get all velocities into separate lists
        for state in self.STATES:
            robot_centric_vel = state.velocities.fieldToRobot(state.pose)

            VEL_X.append(robot_centric_vel.VEL.x)
            VEL_Y.append(robot_centric_vel.VEL.y)
            ANG_VEL.append(robot_centric_vel.ANG_VEL)
        
        plots = [VEL_X, VEL_Y, ANG_VEL]

        # make sure acc ends on the X axis
        for each in plots:
            each.append(0)
            each.append(0)

        time = linspace(0, len(VEL_X), len(VEL_X))
        plots_deriv = [self.__getDerivative(time, vel) for vel in plots]
        


        mplt.style.use('dark_background')

        if acceleration:
            self.__plotChassisAccelerationWindow(time, plots_deriv, connect, color = 'red')
            mplt.tight_layout()
        if velocity:
            self.__plotChassisVelocityWindow(time, plots, connect, color = 'green')
            mplt.tight_layout()

        mplt.show()
            
    def __plotChassisVelocityWindow(self, t: List[int], vel: List[list], 
                                    connect: bool, color: str):

        figure = mplt.figure(figsize = (10, 4), facecolor = 'black')
        figure.canvas.manager.set_window_title("Velocities")

        titles = ["x velocity", "y velocity", "angular velocity"]

        for i in range(3):
            nr = 130 + i + 1

            ax = figure.add_subplot(nr)
            ax.set_xlabel('time (ms)', fontsize = 14)
            ax.set_ylabel('velocity (cm / s)' if not i == 2 else "velocity (rad / s)", fontsize = 14)
            ax.set_title(titles[i])

            if connect:
                    ax.plot(t, vel[i], color = color, linewidth = 3)
            else: ax.scatter(t, vel[i], color = color, s = 1)

            ax.axhline(0, color = 'white', linewidth = 0.5)

    def __plotChassisAccelerationWindow(self, t: List[int], acc: List[list], 
                                        connect: bool, color: str):
        
        figure = mplt.figure(figsize = (10, 4), facecolor = 'black')
        figure.canvas.manager.set_window_title("Accelerations")

        titles = ["x acceleration", "y acceleration", "angular acceleration"]

        for i in range(3):
            nr = 130 + i + 1

            ax = figure.add_subplot(nr)
            ax.set_xlabel('time (ms)', fontsize = 14)
            ax.set_ylabel('acceleration (cm / s^2)' if not i == 2 else "acceleration (rad / s^2)", fontsize = 14)
            ax.set_title(titles[i])

            if connect:
                    ax.plot(t, acc[i], color = color, linewidth = 3)
            else: ax.scatter(t, acc[i], color = color, s = 1)

            ax.axhline(0, color = 'white', linewidth = 0.5)



    def __getDerivative(self, t: List[int], vel: List[float]):
        ACC = []

        for i in range(len(t)):
            if i > 1:
                dt = (t[i] - t[i-1]) / 1000 #ms to s
                dv = vel[i] - vel[i-1]
                    
                ACC.append(dv / dt)
            else: ACC.append(0)
        
        return ACC

            
