import numpy as np
from src.control_math import calculate_desired_poles, calculate_angle_condition

os_percent = 10.0
ts = 2.0
zeta, wn, sd = calculate_desired_poles(os_percent, ts, criterion=0.02)
print(f"sd = {sd}")

all_poles = [0j, -2+0j, -2+0j]
all_zeros = [-4+0j]

angles_poles, angles_zeros, sum_theta, sum_phi, angle_G, phi_zc = calculate_angle_condition(all_poles, all_zeros, sd)
print(f"angles_poles: {angles_poles}")
print(f"angles_zeros: {angles_zeros}")
print(f"sum_theta (poles): {sum_theta}")
print(f"sum_phi (zeros): {sum_phi}")
print(f"angle_G (poles - zeros): {angle_G}")
print(f"phi_zc: {phi_zc}")
