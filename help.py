from scipy.optimize import minimize
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from ev3sim.core import *
from ev3sim.Pathing.MotionProfile import *
import numpy as np

# Define the quintic polynomial function
def quintic_polynomial(x, coeffs):
    a, b, c, d, e, f = coeffs
    return a * x ** 5 + b * x ** 4 + c * x ** 3 + d * x ** 2 + e * x + f

def quintic_derivative(x, coeffs):
    a, b, c, d, e, _ = coeffs
    return 5 * a * x ** 4 + 4 * b * x ** 3 + 3 * c * x ** 2 + 2 * d * x + e

# Define the objective function to minimize (squared error)
def objective(coeffs):
    y_start_pred = quintic_polynomial(x_start, coeffs)
    v_start_pred = 5 * coeffs[0] * x_start ** 4 + 4 * coeffs[1] * x_start ** 3 + 3 * coeffs[2] * x_start ** 2 + 2 * coeffs[3] * x_start + coeffs[4]
    a_start_pred = 20 * coeffs[0] * x_start ** 3 + 12 * coeffs[1] * x_start ** 2 + 6 * coeffs[2] * x_start + 2 * coeffs[3]
    y_end_pred = quintic_polynomial(x_end, coeffs)
    v_end_pred = 5 * coeffs[0] * x_end ** 4 + 4 * coeffs[1] * x_end ** 3 + 3 * coeffs[2] * x_end ** 2 + 2 * coeffs[3] * x_end + coeffs[4]
    a_end_pred = 20 * coeffs[0] * x_end ** 3 + 12 * coeffs[1] * x_end ** 2 + 6 * coeffs[2] * x_end + 2 * coeffs[3]

    return (y_start_pred - y_start) ** 2 + (v_start_pred - v_start) ** 2 + (a_start_pred - a_start) ** 2 + \
           (y_end_pred - y_end) ** 2 + (v_end_pred - v_end) ** 2 + (a_end_pred - a_end) ** 2


# Define a function to calculate the length of the curve using the trapezoidal rule
def curve_length(coeffs, x_start, x_end, num_points=1000):
    x_values = np.linspace(x_start, x_end, num_points)
    y_values = quintic_polynomial(x_values, coeffs)
    dx = (x_end - x_start) / num_points
    dy = np.diff(y_values)
    length = np.sum(np.sqrt(dx ** 2 + dy ** 2))
    return length


# Define initial and final conditions
x_start, y_start = 0, 0 # Initial point
x_end, y_end = 2, 3  # Final point
v_start, v_end = 0, 0  # Initial and final velocities
a_start, a_end = 0, 0  # Initial and final accelerations

# Initial guess for coefficients
coeffs_init = [0, 0, 0, 0, 0, 0]

# Minimize the objective function to find coefficients
result = minimize(objective, coeffs_init, method='SLSQP', tol=1e-6)

# Extract the coefficients
coeffs = result.x

# Generate some sample data points for x
x_data = np.linspace(0, 5, 100)

# Calculate the corresponding y values using the quintic polynomial function
y_data = quintic_polynomial(x_data, coeffs)

# Initialize the plot
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', label='Quintic Polynomial Curve')
tangent_line, = ax.plot([], [], 'r--', alpha=0.5, label='Tangent Line')
point_annot = ax.text(0.1, 0.9, '', transform=ax.transAxes, fontsize=10)

# Function to update the animation frame
def update(frame):
    ax.clear()
    ax.plot(x_data, y_data, 'b-', label='Quintic Polynomial Curve')
    x_point = x_data[frame]
    y_point = quintic_polynomial(x_point, coeffs)
    tangent_slope = quintic_derivative(x_point, coeffs)
    tangent_line_x = [x_point - 0.5, x_point + 0.5]
    tangent_line_y = [y_point - 0.5 * tangent_slope, y_point + 0.5 * tangent_slope]
    ax.plot(tangent_line_x, tangent_line_y, 'r--', alpha=0.5)
    ax.scatter(x_point, y_point, color='red')
    point_annot.set_text(f'Point: ({x_point:.2f}, {y_point:.2f}), Slope: {tangent_slope:.2f}')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Quintic Polynomial Curve and Tangent Line')
    ax.legend()
    ax.grid(True)

    print("angle: ", np.degrees(np.arctan(tangent_slope)))

# Create the animation
ani = FuncAnimation(fig, update, frames=len(x_data), interval=100)

'''length = curve_length(coeffs, x_start, x_end)
print("Length of the curve:", length)

linear_profile = TrapezoidalProfile(distance = length, max_vel = 100, acc = 50)

sim = Simulator()
sim.manual_control.set(False)
sim.robot.trail.draw_trail.set(True)

#pygame.time.wait(4000)
index = 0
while linear_profile.isBusy:
    time = pygame.time.get_ticks()

    linear_value = linear_profile.calculate(time)[1]
    tangent_slope = quintic_derivative(index * 0.01, coeffs)
    sim.robot.target_head = np.degrees(np.arctan(tangent_slope))

    angular_velocity = findShortestPath(sim.robot.target_head, sim.robot.pose.head) / 180
    index += 1


    sim.robot.setVelocities(linear_value, angular_velocity)
    sim.update()
'''
plt.show()