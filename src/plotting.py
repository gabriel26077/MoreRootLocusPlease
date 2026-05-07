import numpy as np
import matplotlib.pyplot as plt
from .utils import get_multiplicity_info

def draw_real_axis_segments(ax, rl_segments, alpha=1.0):
    """Refactored drawing logic for real axis LGR segments to reuse code."""
    for i, seg in enumerate(rl_segments):
        start, end = seg[0], seg[1]
        kind = seg[2] if len(seg) > 2 else 'finite'
        
        ax.plot([start, end], [0, 0], color='blue', linewidth=4,
                solid_capstyle='round', alpha=alpha, label='LGR Eixo Real' if i == 0 else "")
                
        if kind == 'inf_left':
            ax.annotate('', xy=(start, 0), xytext=(start + (end-start)*0.2, 0),
                        arrowprops=dict(arrowstyle="->", color="blue", lw=2.5, alpha=alpha))
            ax.text(start - 0.2, 0.4, r'$-\infty$', color="blue", fontsize=12, fontweight='bold', ha='right', va='bottom', alpha=alpha)
        elif kind == 'inf_right':
            ax.annotate('', xy=(end, 0), xytext=(end - (end-start)*0.2, 0),
                        arrowprops=dict(arrowstyle="->", color="blue", lw=2.5, alpha=alpha))
            ax.text(end + 0.2, 0.4, r'$+\infty$', color="blue", fontsize=12, fontweight='bold', ha='left', va='bottom', alpha=alpha)


def plot_poles_zeros_with_multiplicity(ax, all_poles, all_zeros):
    """Plot poles (x) and zeros (o) with multiplicity annotations."""
    pole_mult = get_multiplicity_info(all_poles)
    zero_mult = get_multiplicity_info(all_zeros)

    if all_poles:
        ax.plot(np.real(all_poles), np.imag(all_poles), 'x', markersize=12, color='red',
                markeredgewidth=3, label='Polos')
    for pt, mult in pole_mult.items():
        if mult > 1:
            ax.annotate(f'  ×{mult}', xy=(pt.real, pt.imag), fontsize=10,
                        fontweight='bold', color='darkred', va='bottom')

    if all_zeros:
        ax.plot(np.real(all_zeros), np.imag(all_zeros), 'o', markersize=10, color='green',
                fillstyle='none', markeredgewidth=2, label='Zeros')
    for pt, mult in zero_mult.items():
        if mult > 1:
            ax.annotate(f'  ×{mult}', xy=(pt.real, pt.imag), fontsize=10,
                        fontweight='bold', color='darkgreen', va='bottom')


def plot_base_lgr(ax, all_poles, all_zeros, rl_segments, all_roots_data=None):
    """Draw the base LGR plot elements reused in multiple steps."""
    if all_roots_data is not None:
        for i in range(all_roots_data.shape[1]):
            ax.plot(np.real(all_roots_data[:, i]), np.imag(all_roots_data[:, i]),
                    linewidth=1.5, alpha=0.3, color='gray')

    plot_poles_zeros_with_multiplicity(ax, all_poles, all_zeros)
    draw_real_axis_segments(ax, rl_segments, alpha=0.6)

    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)


def setup_lgr_axes(ax, all_poles, all_zeros, rl_segments, extra_points=None, title=''):
    """Set up axes limits and style for an LGR plot."""
    all_x = [p.real for p in all_poles] + [z.real for z in all_zeros]
    for seg in rl_segments:
        all_x.extend([seg[0], seg[1]])
    if extra_points:
        all_x.extend(extra_points)
    if all_x:
        x_min, x_max = min(all_x), max(all_x)
        x_span = x_max - x_min
        pad = x_span * 0.2 if x_span > 0 else 3.0
        ax.set_xlim(x_min - pad, max(x_max + pad, 2))
        y_coords = [abs(p.imag) for p in all_poles] + [abs(z.imag) for z in all_zeros]
        y_limit = max(y_coords) + 6 if y_coords else 6
        ax.set_ylim(-y_limit, y_limit)
    ax.set_aspect('auto')
    ax.set_title(title, fontsize=14)
    ax.set_xlabel(r'Eixo Real ($\sigma$)', fontsize=12)
    ax.set_ylabel(r'Eixo Imaginário ($j\omega$)', fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right')
