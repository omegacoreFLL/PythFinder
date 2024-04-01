from ev3sim.Pathing.motionProfile import *
from ev3sim.Pathing.inLineCM import *
from ev3sim.Pathing.turnDeg import *
from ev3sim.multiplierTuner import *
from ev3sim.core import *

sim = Simulator()
sim.manual_control = False
startMultiplierTuner(sim, -40)
startMultiplierTuner(sim, 70)

while sim.running:
    sim.update()

