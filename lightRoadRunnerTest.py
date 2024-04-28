import numpy as np
import matplotlib.pyplot as plt

vectorize_tail = lambda f: np.vectorize(f, excluded={0})


#CONSTANT VELOCITY PROFILE
def vel_traj_gen(x0, x1, vmax):
    dt = (x1 - x0) / vmax
    return x0, vmax, dt




#CONSTANT ACCELERATION PROFILE
def accel_traj_gen(x0, x1, vmax, amax):
    dx = x1 - x0
    if vmax / amax < dx / vmax:
        # normal trajectory
        dt1 = vmax / amax
        dt2 = dx / vmax - vmax / amax
        dt3 = dt1
        return x0, (
            (amax, dt1),
            (0, dt2),
            (-amax, dt3)
        )
    else:
        # degenerate trajectory
        dt1 = np.sqrt(dx / amax)
        dt2 = dt1
        return x0, (
            (amax, dt1), 
            (-amax, dt2)
        )


@vectorize_tail
def accel_traj_get_accel(traj, t):
    _, phases = traj
    for a, dt in phases:
        if t < dt:
            return a
        
        t -= dt
    return a

        
@vectorize_tail
def accel_traj_get_vel(traj, t):
    _, phases = traj
    v0 = 0
    for a, dt in phases:
        if t < dt:
            return v0 + a * t
        
        v0 += a * dt
        
        t -= dt
    return v0
    
    
@vectorize_tail
def accel_traj_get_pos(traj, t):
    x0, phases = traj
    v0 = 0
    for a, dt in phases:
        if t < dt:
            return x0 + v0 * t + a * t**2 / 2
        
        x0 += v0 * dt + a * dt**2 / 2
        v0 += a * dt
        
        t -= dt 
    return x0


def accel_traj_duration(traj):
    _, phases = traj
    duration = 0
    for _, dt in phases:
        duration += dt
    return duration




def spline_fit(x0, dx0, x1, dx1):
    a = 2 * x0 + dx0 - 2 * x1 + dx1
    b = -3 * x0 - 2 * dx0 + 3 * x1 - dx1
    c = dx0
    d = x0
    return a, b, c, d

def spline_get(spline, u):
    a, b, c, d = spline
    return a * u**3 + b * u**2 + c * u + d

def spline_deriv(spline, u):
    a, b, c, d = spline
    return 3 * a * u**2 + 2 * b * u + c

def spline_deriv_second(spline, u):
    a, b, c, d = spline
    return 6 * a * u + 2 * b











x_spline = spline_fit(0, 10, 40, 20)
y_spline = spline_fit(0, 5, 10, -15)






upsilon = np.linspace(0, 1, 1000)

dupsilon = upsilon[1] - upsilon[0]
integrand = np.sqrt(
    spline_deriv(x_spline, upsilon)**2 + 
    spline_deriv(y_spline, upsilon)**2
)


sums = np.zeros_like(upsilon)
last_sum = 0
for i in range(len(upsilon)):
    sums[i] = last_sum + integrand[i] * dupsilon
    last_sum = sums[i]


    
@np.vectorize
def spline_param_of_disp(s):
    for i in range(len(sums)):
        if s < sums[i]:
            return upsilon[i]

def spline_param_of_disp_deriv(x_spline, y_spline, u):
    return 1.0 / np.sqrt(spline_deriv(x_spline, u)**2 + spline_deriv(y_spline, u)**2)

def spline_param_of_disp_deriv_second(x_spline, y_spline, u):
    dxdu = spline_deriv(x_spline, u)
    dydu = spline_deriv(y_spline, u)
    
    dxdudu = spline_deriv_second(x_spline, u)
    dydudu = spline_deriv_second(y_spline, u)
    
    denominator = np.sqrt(dxdu**2 + dydu**2)
    
    numerator = dxdudu * dxdu + dydudu * dydu
    
    return -0.5 * numerator / (denominator**3)






length = sums[-1]
traj = accel_traj_gen(0, length, 30, 10)
t = np.linspace(0, accel_traj_duration(traj), 1000)

s = accel_traj_get_pos(traj, t)

u = spline_param_of_disp(s)

x = spline_get(x_spline, u)
y = spline_get(y_spline, u)

dsdt = accel_traj_get_vel(traj, t)
dsdtdt = accel_traj_get_accel(traj, t)

duds = spline_param_of_disp_deriv(x_spline, y_spline, u)
dudsds = spline_param_of_disp_deriv_second(x_spline, y_spline, u)

dxdu = spline_deriv(x_spline, u)
dydu = spline_deriv(y_spline, u)

dxdudu = spline_deriv_second(x_spline, u)
dydudu = spline_deriv_second(y_spline, u)

dxdt = dxdu * duds * dsdt
dydt = dydu * duds * dsdt

dxdtdt = (dxdudu * (duds ** 2) * dsdt +
          dxdu * dudsds * dsdt +
          dxdu * duds * dsdtdt)
dydtdt = (dydudu * (duds ** 2) * dsdt +
          dydu * dudsds * dsdt +
          dydu * duds * dsdtdt)




plt.figure(figsize=(15, 9), facecolor = 'black')
plt.style.use('dark_background')

plt.title('Qubic Spline', fontsize=22)
plt.xlabel('x', fontsize=14)
plt.ylabel('y', fontsize=14)
plt.grid(True)

# Plot the curve
plt.axhline(0, color = 'white', linewidth = 1)
plt.axvline(0, color = 'white', linewidth = 1)

plt.plot(t, dydt, color='red', zorder=1, linewidth = 2)

plt.show()