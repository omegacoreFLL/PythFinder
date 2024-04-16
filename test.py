from ev3sim.Pathing.MotionProfile import *
from ev3sim.Components.Constants.constants import *
from ev3sim.Pathing.OnBot.inLineCM import *
from ev3sim.Pathing.OnBot.turnDeg import *
from ev3sim.core import *

sim = Simulator()

while sim.RUNNING():
    sim.update()