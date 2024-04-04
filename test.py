from ev3sim.Pathing.MotionProfile import *
from ev3sim.Components.Constants.constants import *
#from ev3sim.Pathing.inLineCM import *
#from ev3sim.Pathing.turnDeg import *
from ev3sim.core import *

    
sim = Simulator()
ang_vel = sim.robot.constrains.TRACK_WIDTH / 2 * sim.robot.constrains.ang_vel
vel = sim.robot.constrains.vel
sim.manual_control.set(False)
start_head = 360

start_time = pygame.time.get_ticks()

while pygame.time.get_ticks() - start_time <= 1000:
    sim.robot.setWheelPowers(ang_vel, -ang_vel)
    sim.update()
sim.robot.setWheelPowers(0, 0)

print("delta: ", abs(sim.robot.pose.head - start_head))
#sim.manual_control.set(True)

while sim.RUNNING():
    sim.update()



