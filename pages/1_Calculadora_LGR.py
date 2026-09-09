"""
LGR (Lugar das Raízes / Root Locus) Calculator - Streamlit App
A didactic step-by-step Root Locus calculator.
"""

import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from src.utils import poly_to_latex, array_to_sym, fatorar_numerico, get_multiplicity_info, parse_to_coeffs
from src.control_math import compute_real_axis_segments, sort_roots_by_proximity, compute_numerical_root_locus, calculate_break_points, calculate_departure_arrival_angles
from src.plotting import draw_real_axis_segments, plot_poles_zeros_with_multiplicity, plot_base_lgr, setup_lgr_axes

# ============================================================
# Page configuration
# ============================================================
st.set_page_config(
    page_title="Calculadora LGR - Lugar das Raízes",
    page_icon="📈",
    layout="wide",
)

st.title("Calculadora do Lugar das Raízes (Root Locus)")
st.markdown("""
Ferramenta didática para cálculo e visualização do **Lugar Geométrico das Raízes (LGR)**,
mostrando todos os passos do algoritmo dos 12 passos.
""")

use_expr = st.toggle("Entrada de dados por expressões (ex: `s^2+1`)", value=False)
with st.form('Entrada das funções de transferência'):
    if use_expr:
        st.markdown("*Aceita notação matemática como `(s+1)(s+2)` ou `s^2 + 2*s`*")
        col_g, col_h = st.columns(2)
        with col_g:
            st.subheader('$G(s)=$')
            g_num_str = st.text_input("Expressão de $G(s)$ do numerador:", "1")
            g_den_str = st.text_input("Expressão de $G(s)$ do denominador:", "s*(s^2 + 8*s + 32)")
        with col_h:
            st.subheader('$H(s)=$')
            h_num_str = st.text_input("Expressão de $H(s)$ do numerador:", "1")
            h_den_str = st.text_input("Expressão de $H(s)$ do denominador:", "s + 4")
    else:
        st.markdown("*Listas de coeficientes do maior para o menor grau.*")
        col_g, col_h = st.columns(2)
        with col_g:
            st.subheader('$G(s)=$')
            g_num_str = st.text_input("Coeficientes de $G(s)$ numerador:", "1")
            g_den_str = st.text_input("Coeficientes de $G(s)$ denominador:", "1, 8, 32, 0")
        with col_h:
            st.subheader('$H(s)=$')
            h_num_str = st.text_input("Coeficientes de $H(s)$ numerador:", "1")
            h_den_str = st.text_input("Coeficientes de $H(s)$ denominador:", "1, 4")

    st.subheader('Ponto de teste')
    cols = st.columns(6)
    cols[0].latex('s_i=')
    s_test_real = cols[1].number_input('Parte real:', value=-1.0)
    cols[2].latex(r'\pm')
    s_test_imag = cols[3].number_input('Parte imaginária:', value=-1.0)
    cols[4].latex('j')
    cols[5].space()
    threshold = st.number_input("Tolerância [graus]:", min_value=0.1, value=10.0, step=1.0)

    st.text('Configurações adicionais na barra lateral.')

    submit = st.form_submit_button('Calcular')


# ============================================================
# Sidebar - Input
# ============================================================
st.sidebar.subheader("Parâmetros do LGR Numérico")
k_max = st.sidebar.number_input("K máximo:", min_value=1.0, value=10000.0, step=100.0)
k_points = st.sidebar.number_input("Número de pontos:", min_value=100, value=10000, step=100)

st.sidebar.subheader("Limites do Gráfico")
y_min_input = st.sidebar.number_input("y mínimo:", value=-10.0, step=1.0)
y_max_input = st.sidebar.number_input("y máximo:", value=10.0, step=1.0)

update = st.sidebar.button("Atualizar", use_container_width=True)

# On button click, save parameters to session state
if update or submit:
    st.session_state['params'] = {
        'use_expr': use_expr,
        'g_num_str': g_num_str, 'g_den_str': g_den_str,
        'h_num_str': h_num_str, 'h_den_str': h_den_str,
        'k_max': k_max, 'k_points': k_points,
        'y_min': y_min_input, 'y_max': y_max_input,
        's_test_real': s_test_real, 's_test_imag': s_test_imag,
        'threshold': threshold,
    }

# If never calculated, show prompt
if 'params' not in st.session_state:
    st.info('Após definir funções de transferência, clique no botão de "Calcular", acima.')
    st.stop()

# Use saved parameters
p = st.session_state['params']
use_expr_state = p.get('use_expr', False)
g_num_str = p['g_num_str']
g_den_str = p['g_den_str']
h_num_str = p['h_num_str']
h_den_str = p['h_den_str']
k_max = p['k_max']
k_points = p['k_points']
y_min_input = p['y_min']
y_max_input = p['y_max']
s_test_real = p['s_test_real']
s_test_imag = p['s_test_imag']
threshold = p['threshold']

# Parse inputs
# Symbolic variable
s = sp.symbols('s')

if use_expr_state:
    try:
        # returns list of coefficients
        g_num = parse_to_coeffs(g_num_str, s)
        g_den = parse_to_coeffs(g_den_str, s)
        h_num = parse_to_coeffs(h_num_str, s)
        h_den = parse_to_coeffs(h_den_str, s)
    except Exception as e:
        st.error(f"Erro ao interpretar as expressões algébricas: verifique a sintaxe. Detalhe: {e}")
        st.stop()
else:
    try:
        g_num = np.array([float(x.strip()) for x in g_num_str.split(",")])
        g_den = np.array([float(x.strip()) for x in g_den_str.split(",")])
        h_num = np.array([float(x.strip()) for x in h_num_str.split(",")])
        h_den = np.array([float(x.strip()) for x in h_den_str.split(",")])
    except ValueError:
        st.error("Erro ao interpretar os coeficientes. Use números separados por vírgula.")
        st.stop()

# ============================================================
# Computations
# ============================================================

# Convert to symbolic
G_num_s = array_to_sym(g_num, s)
G_den_s = array_to_sym(g_den, s)
H_num_s = array_to_sym(h_num, s)
H_den_s = array_to_sym(h_den, s)

# Compute G(s)H(s) symbolically
GH_expr = (G_num_s * H_num_s) / (G_den_s * H_den_s)
P_num_sym, P_den_sym = GH_expr.as_numer_denom()
P_den_expanded_sym = sp.expand(P_den_sym)
GH_expr_expanded_den = P_num_sym / P_den_expanded_sym

# Compute combined num/den for numerical root locus
num_combined = np.polymul(g_num, h_num)
den_combined = np.polymul(g_den, h_den)

# Factored form
GH_simplified = sp.simplify(GH_expr)
P_num_simp, P_den_simp = GH_simplified.as_numer_denom()

P_num_factored = fatorar_numerico(P_num_simp, s)
P_den_factored = fatorar_numerico(P_den_simp, s)
GH_final_display = P_num_factored / P_den_factored

# Zeros and Poles  # todo: use consistent numbering
if P_num_simp.is_number:
    all_zeros = []
else:
    all_zeros = [complex(z) for z in sp.nroots(P_num_simp)]

if P_den_simp.is_number:
    all_poles = []
else:
    all_poles = [complex(p) for p in sp.nroots(P_den_simp)]

Np = len(all_poles)
Nz = len(all_zeros)
Na = Np - Nz
Ls = max(Np, Nz)

# Real axis segments
rl_segments = compute_real_axis_segments(all_poles, all_zeros)

# ============================================================
# Step Display
# ============================================================

# --- Mostrar G(s) e H(s) ---
st.header("Funções de Transferência:")
col_gs, col_hs, col_test = st.columns(3)
with col_gs:
    G_display = sp.Rational(1) * G_num_s / G_den_s
    st.latex(rf"G(s) = {sp.latex(G_display)}")
with col_hs:
    H_display = sp.Rational(1) * H_num_s / H_den_s
    st.latex(rf"H(s) = {sp.latex(H_display)}")
with col_test:
    st.markdown(f'Ponto de teste: $s_i = {sp.latex(s_test_real + 1j * s_test_imag)}$')

st.markdown("---")

# --- LGR Numérico ---
st.header("LGR Numérico")
st.markdown("Determinação do LGR numericamente para comparação.")

K_vals, all_roots = compute_numerical_root_locus(num_combined, den_combined, k_max, int(k_points))

fig_num, ax_num = plt.subplots(figsize=(10, 7))  # todo: change to plotly
# plota curvas do LGR com x=Re(s) e y=Im(s)
for i in range(all_roots.shape[1]):
    ax_num.plot(np.real(all_roots[:, i]), np.imag(all_roots[:, i]), linewidth=2)

polos_ma = np.roots(den_combined)
ax_num.plot(np.real(polos_ma), np.imag(polos_ma), 'x', markersize=10, color='red',
            markeredgewidth=2, label='Polos (Malha Aberta)')
zeros_ma = np.roots(num_combined)
if len(zeros_ma) > 0:
    ax_num.plot(np.real(zeros_ma), np.imag(zeros_ma), 'o', markersize=8, color='red',
                fillstyle='none', markeredgewidth=2, label='Zeros (Malha Aberta)')

# Annotate multiplicity on numerical plot
pole_mult_num = get_multiplicity_info([complex(p) for p in polos_ma])
for pt, mult in pole_mult_num.items():
    if mult > 1:
        ax_num.annotate(f'  ×{mult}', xy=(pt.real, pt.imag), fontsize=10,
                        fontweight='bold', color='darkred', va='bottom')

zero_mult_num = get_multiplicity_info([complex(z) for z in zeros_ma]) if len(zeros_ma) > 0 else {}
for pt, mult in zero_mult_num.items():
    if mult > 1:
        ax_num.annotate(f'  ×{mult}', xy=(pt.real, pt.imag), fontsize=10,
                        fontweight='bold', color='darkgreen', va='bottom')

ax_num.scatter(s_test_real, s_test_imag, s=100, c='red', marker='*', label='Ponto de teste')

ax_num.axhline(0, color='black', linewidth=1)
ax_num.axvline(0, color='black', linewidth=1)
ax_num.set_title('Lugar das Raízes (Root Locus)', fontsize=14)
ax_num.set_xlabel(r'Eixo Real ($\sigma$)', fontsize=12)
ax_num.set_ylabel(r'Eixo Imaginário ($j\omega$)', fontsize=12)
ax_num.set_ylim(y_min_input, y_max_input)  # todo: auto-limit y-axis...

# Auto-limit x-axis based on poles/zeros to prevent infinite stretching
all_pz_real = list(np.real(polos_ma))
if len(zeros_ma) > 0:
    all_pz_real.extend(list(np.real(zeros_ma)))
if all_pz_real:
    x_min_num = min(all_pz_real)
    x_max_num = max(all_pz_real)
    x_span_num = x_max_num - x_min_num
    x_pad = max(x_span_num * 0.4, 2.0)
    ax_num.set_xlim(x_min_num - x_pad, x_max_num + x_pad)

ax_num.grid(True, linestyle='--', alpha=0.7)
ax_num.legend()
st.pyplot(fig_num)

# ============================================================
# Algoritmo dos 12 Passos
from src.ui_lgr_steps import render_12_steps

render_12_steps(s, GH_expr_expanded_den, GH_final_display, all_poles, all_zeros, rl_segments, Np, Nz, Ls, Na, P_num_sym, P_den_sym, all_roots, s_test_real, s_test_imag, threshold)
# Footer
# ============================================================
st.markdown("---")
st.markdown("**Calculadora LGR** - Ferramenta didática para análise de sistemas de controle.")
