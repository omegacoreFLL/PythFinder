from ev3sim.Trajectory.splines import *

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

start, end = Point(0, 0), Point(-5, 20)
start_tan, end_tan = Point(0, 5), Point(10, 0)

spline = QubicSpline(start, end,
                    start_tan, end_tan)

x, y = pointsToGraph(spline.generate(n = 0))
yaw = spline.generate_ang(n = 0)


plt.figure(figsize=(15, 9), facecolor = 'black')
plt.style.use('dark_background')

plt.title('Qubic Spline Curvature', fontsize=22)
plt.xlabel('time', fontsize=14)
plt.ylabel('curvature', fontsize=14)
plt.grid(False)

# Plot the curve
plt.axhline(0, color = 'white', linewidth = 1)
plt.axvline(0, color = 'white', linewidth = 1)

plt.plot(spline.t, yaw, color='red', zorder=1, linewidth = 4)

flg, ax = plt.subplots(1)
plt.plot(x, y, color='magenta', zorder=1, linewidth = 2)

plt.show()


