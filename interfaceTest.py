from ev3sim.core import *

sim = Simulator()

while sim.RUNNING():
    sim.update()