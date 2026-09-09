import sympy as sp
import numpy as np

def compute_real_axis_segments(all_poles, all_zeros):
    """Compute which segments of the real axis belong to the root locus."""
    poles_real = [p.real for p in all_poles if abs(p.imag) < 1e-7]
    zeros_real = [z.real for z in all_zeros if abs(z.imag) < 1e-7]
    all_real_points = sorted(list(set([round(x, 8) for x in poles_real + zeros_real])))

    if not all_real_points:
        return []

    segments = []
    span = all_real_points[-1] - all_real_points[0] if len(all_real_points) > 1 else 2
    INF_LEN = max(span * 0.15, 1.5)

    def count_to_right(test_pt):
        return (sum(1 for p in poles_real if p > test_pt) +
                sum(1 for z in zeros_real if z > test_pt))

    test_left = all_real_points[0] - 1
    if count_to_right(test_left) % 2 != 0:
        segments.append((all_real_points[0] - INF_LEN, all_real_points[0], 'inf_left'))

    for i in range(len(all_real_points) - 1):
        test_mid = (all_real_points[i] + all_real_points[i + 1]) / 2
        if count_to_right(test_mid) % 2 != 0:
            segments.append((all_real_points[i], all_real_points[i + 1], 'finite'))

    test_right = all_real_points[-1] + 1
    if count_to_right(test_right) % 2 != 0:
        segments.append((all_real_points[-1], all_real_points[-1] + INF_LEN, 'inf_right'))

    return segments

def sort_roots_by_proximity(prev_roots, curr_roots):
    """Sort curr_roots to best match prev_roots order (nearest-neighbor)."""
    n = len(curr_roots)
    sorted_roots = np.empty_like(curr_roots)
    used = np.zeros(n, dtype=bool)
    for i in range(n):
        dists = np.abs(curr_roots - prev_roots[i])
        dists[used] = np.inf
        j = np.argmin(dists)
        sorted_roots[i] = curr_roots[j]
        used[j] = True
    return sorted_roots

def compute_numerical_root_locus(num, den, k_max=10000, k_points=10000):
    """Compute numerical root locus with logarithmic K spacing and root tracking."""
    K_vals = np.concatenate([
        [0],
        np.logspace(-3, np.log10(k_max), k_points - 1)  # fixme
    ])

    eq0 = np.polyadd(den, K_vals[0] * num)
    prev = np.roots(eq0)
    all_roots = [prev]

    for K in K_vals[1:]:
        eq = np.polyadd(den, K * num)
        curr = np.roots(eq)
        curr_sorted = sort_roots_by_proximity(prev, curr)
        all_roots.append(curr_sorted)
        prev = curr_sorted

    return K_vals, np.array(all_roots)

def calculate_break_points(P_num_sym, P_den_sym, s_sym, rl_segments):
    """Calculate valid break-away and break-in points on the real axis."""
    K_expr_break = -P_den_sym / P_num_sym
    dN_ds = sp.diff(P_num_sym, s_sym)
    dD_ds = sp.diff(P_den_sym, s_sym)
    break_eq = dD_ds * P_num_sym - P_den_sym * dN_ds

    try:
        break_roots_sympy = sp.nroots(break_eq)
        break_roots_complex = [complex(r) for r in break_roots_sympy]
    except Exception:
        break_roots_complex = []

    tol = 1e-5
    valid_break_points = []
    for r in break_roots_complex:
        if abs(r.imag) < tol:
            real_val = r.real
            is_on_lgr_bp = False
            for seg in rl_segments:
                start, end = seg[0], seg[1]
                seg_min, seg_max = min(start, end), max(start, end)
                if seg_min - tol <= real_val <= seg_max + tol:
                    is_on_lgr_bp = True
                    break
            if is_on_lgr_bp:
                valid_break_points.append(real_val)

    valid_break_points = sorted(list(set([round(p, 4) for p in valid_break_points])))
    return K_expr_break, break_eq, break_roots_complex, valid_break_points

def calculate_departure_arrival_angles(all_poles, all_zeros, tol=1e-5):
    """Calculate departure angles from complex poles and arrival angles to complex zeros."""
    complex_poles = [p for p in all_poles if abs(p.imag) > tol]
    complex_zeros = [z for z in all_zeros if abs(z.imag) > tol]

    departure_angles = {}
    arrival_angles = {}

    for pk in complex_poles:
        other_poles = [p for p in all_poles if not np.isclose(pk, p)]
        angles_from_other_poles = [np.degrees(np.angle(pk - p)) for p in other_poles]
        angles_from_zeros = [np.degrees(np.angle(pk - z)) for z in all_zeros]
        sum_theta = sum(angles_from_other_poles)
        sum_phi = sum(angles_from_zeros)
        angle_dep = (180.0 - sum_theta + sum_phi) % 360.0
        if angle_dep > 180:
            angle_dep -= 360
        departure_angles[pk] = (angle_dep, angles_from_other_poles, angles_from_zeros)

    for zk in complex_zeros:
        other_zeros = [z for z in all_zeros if not np.isclose(zk, z)]
        angles_from_other_zeros = [np.degrees(np.angle(zk - z)) for z in other_zeros]
        angles_from_poles = [np.degrees(np.angle(zk - p)) for p in all_poles]
        sum_phi_z = sum(angles_from_other_zeros)
        sum_theta_z = sum(angles_from_poles)
        angle_arr = (180.0 - sum_phi_z + sum_theta_z) % 360.0
        if angle_arr > 180:
            angle_arr -= 360
        arrival_angles[zk] = (angle_arr, angles_from_other_zeros, angles_from_poles)

    return departure_angles, arrival_angles

def calculate_desired_poles(os_percent, ts, criterion=0.02):
    """Calculate dominant poles based on overshoot and settling time criterion (0.02 or 0.05)."""
    if os_percent <= 0 or ts <= 0:
        return 0, 0, complex(0,0)
    os_ratio = os_percent / 100.0
    zeta = -np.log(os_ratio) / np.sqrt(np.pi**2 + np.log(os_ratio)**2)
    
    if criterion == 0.02:
        wn = 4.0 / (zeta * ts)
    else:
        wn = 3.0 / (zeta * ts)
        
    sigma = zeta * wn
    wd = wn * np.sqrt(1 - zeta**2)
    sd = complex(-sigma, wd)
    return zeta, wn, sd

def calculate_angle_condition(all_poles, all_zeros, sd):
    """Calculate the sum of angles from plant poles and zeros to sd, and the deficiency."""
    angles_from_poles = [np.degrees(np.angle(sd - p)) for p in all_poles]
    angles_from_zeros = [np.degrees(np.angle(sd - z)) for z in all_zeros]
    sum_theta = sum(angles_from_poles)
    sum_phi = sum(angles_from_zeros)
    # User requested: angulos dos polos - angulos dos zeros
    angle_G = sum_theta - sum_phi
    
    # Condição de ângulo: \sum \theta_p - (\sum \phi_z + \phi_{zc}) = 180 (ímpar)
    # \phi_{zc} = \sum \theta_p - \sum \phi_z - 180 = angle_G - 180
    phi_zc = (angle_G - 180.0) % 360.0
    if phi_zc > 180:
        phi_zc -= 360
        
    return angles_from_poles, angles_from_zeros, sum_theta, sum_phi, angle_G, phi_zc

def calculate_pd_zero(sd, phi_zc_deg):
    """Calculate the zero of the PD controller."""
    phi_zc_rad = np.radians(phi_zc_deg)
    sigma_d = -sd.real
    omega_d = sd.imag
    
    if np.isclose(np.sin(phi_zc_rad), 0):
        return float('inf')
        
    zc = sigma_d + omega_d / np.tan(phi_zc_rad)
    return zc

def calculate_pd_gain(G_num_sym, G_den_sym, s_sym, zc, sd):
    """Calculate Kd and Kp based on the magnitude criterion."""
    if zc == float('inf'):
        return 0, 0
    G_val = complex((G_num_sym / G_den_sym).subs(s_sym, sd).evalf())
    G_mag = abs(G_val)
    Gc_part_mag = abs(sd + zc)
    Kd = 1.0 / (Gc_part_mag * G_mag)
    Kp = Kd * zc
    return Kd, Kp

def calculate_steady_state_error(G_num_sym, G_den_sym, s_sym, Kp, Kd):
    """Calculate position error constant (Kp_sys) and steady state error to a step."""
    Gc_sym = Kp + Kd * s_sym
    OL_sym = Gc_sym * (G_num_sym / G_den_sym)
    Kp_sys = sp.limit(OL_sym, s_sym, 0)
    try:
        Kp_sys_val = float(Kp_sys)
        ess = 1.0 / (1.0 + Kp_sys_val)
    except Exception:
        Kp_sys_val = float('inf')
        ess = 0.0
    return Kp_sys_val, ess
