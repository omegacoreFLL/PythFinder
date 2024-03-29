from ev3sim.core import *

sim = Simulator()

while sim.running:
    sim.update()