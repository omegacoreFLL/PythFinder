from ev3sim.Pathing.MotionProfile import *
from ev3sim.Pathing.inLineCM import *
from ev3sim.Pathing.turnDeg import *
from ev3sim.profile import *
from ev3sim.core import *


sim = Simulator()
sim.manual_control = False
startProfile(sim, -40)

pygame.time.wait(200)

startProfile(sim, 70)

sim.manual_control = True
while sim.running:
    sim.update()

