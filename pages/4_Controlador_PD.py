import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

from src.utils import array_to_sym, parse_to_coeffs, get_multiplicity_info
from src.control_math import (
    calculate_desired_poles, 
    calculate_angle_condition, 
    calculate_pd_zero, 
    calculate_pd_gain, 
    calculate_steady_state_error,
    compute_numerical_root_locus
)

st.set_page_config(
    page_title="Controlador Proporcional-Derivativo (PD)",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Projeto de Controlador PD")
st.markdown("""
Nesta página, projetaremos um **Controlador PD ($K_p + K_d s$)** em 6 passos estruturados.
O controlador PD melhora o regime transitório (tempo de acomodação e sobressinal) adicionando um zero à malha via **Critério de Ângulo**, seguido pelo cálculo de ganho via **Critério de Módulo**.
""")

st.sidebar.header("⚙️ Entrada da Planta G(s)")
use_expr = st.sidebar.toggle("📝 Entrada por Expressões (ex: s+1)", value=False)

if use_expr:
    st.sidebar.markdown("*Aceita notação matemática como `(s+1)(s+2)`*")
    st.sidebar.subheader("G(s) - Numerador")
    g_num_str = st.sidebar.text_input("Expressão de G(s) do numerador:", "4*(s+4)")
    st.sidebar.subheader("G(s) - Denominador")
    g_den_str = st.sidebar.text_input("Expressão de G(s) do denominador:", "s^3+4s^2+4s")
else:
    st.sidebar.markdown("*Listas de coeficientes do maior para o menor grau.*")
    st.sidebar.subheader("G(s) - Numerador")
    g_num_str = st.sidebar.text_input("Coeficientes de G(s) numerador:", "4, 16")
    st.sidebar.subheader("G(s) - Denominador")
    g_den_str = st.sidebar.text_input("Coeficientes de G(s) denominador:", "1, 4, 4, 0")

st.sidebar.markdown("---")
st.sidebar.subheader("Requisitos de Projeto")
overshoot = st.sidebar.number_input("Sobressinal Máximo (%)", value=10.0)
ts = st.sidebar.number_input("Tempo de Acomodação (s)", value=2.0)
ts_criterion_str = st.sidebar.selectbox("Critério do Tempo de Acomodação", ["2%", "5%"])

st.sidebar.markdown("---")
calcular = st.sidebar.button("🚀 Calcular Projeto PD", use_container_width=True)

if calcular:
    st.session_state['pd_params'] = {
        'use_expr': use_expr,
        'g_num_str': g_num_str, 'g_den_str': g_den_str,
        'overshoot': overshoot, 'ts': ts,
        'ts_criterion': ts_criterion_str
    }

if 'pd_params' not in st.session_state:
    st.info("👈 Configure a planta e os requisitos na barra lateral e clique em **🚀 Calcular**.")
    st.stop()

# ==========================================
# EXTRAÇÃO E CÁLCULO INICIAL
# ==========================================
p = st.session_state['pd_params']
s = sp.symbols('s')

if p['use_expr']:
    try:
        g_num = parse_to_coeffs(p['g_num_str'], s)
        g_den = parse_to_coeffs(p['g_den_str'], s)
    except Exception as e:
        st.error(f"❌ Erro ao interpretar as expressões algébricas: {e}")
        st.stop()
else:
    try:
        g_num = np.array([float(x.strip()) for x in p['g_num_str'].split(",")])
        g_den = np.array([float(x.strip()) for x in p['g_den_str'].split(",")])
    except ValueError:
        st.error("❌ Erro ao interpretar os coeficientes.")
        st.stop()

G_num_sym = array_to_sym(g_num, s)
G_den_sym = array_to_sym(g_den, s)

# Achar polos e zeros da planta
all_zeros = [complex(z) for z in sp.nroots(G_num_sym)] if not G_num_sym.is_number else []
all_poles = [complex(p) for p in sp.nroots(G_den_sym)] if not G_den_sym.is_number else []

# ==========================================
# CÁLCULOS INICIAIS
# ==========================================
ts_criterion_val = 0.02 if p.get('ts_criterion', '2%') == '2%' else 0.05
zeta, wn, sd = calculate_desired_poles(p['overshoot'], p['ts'], criterion=ts_criterion_val)

# Exibir Planta Inicial
st.header("📊 Planta Original $G(s)$")
G_display = sp.Rational(1) * G_num_sym / G_den_sym
st.latex(rf"G(s) = {sp.latex(G_display)}")

st.markdown("---")
st.header("📍 Ponto de Operação Desejado vs LGR Original")
st.markdown(rf"**Polos Desejados:** $s_d = {sd.real:.4f} \pm {abs(sd.imag):.4f}j$")

# Plotar o LGR Original e mostrar o ponto sd
num_combined = g_num
den_combined = g_den
K_vals, all_roots = compute_numerical_root_locus(num_combined, den_combined, 10000.0, 5000)

fig_num, ax_num = plt.subplots(figsize=(10, 6))
for i in range(all_roots.shape[1]):
    ax_num.plot(np.real(all_roots[:, i]), np.imag(all_roots[:, i]), linewidth=2)

polos_ma = np.roots(den_combined)
ax_num.plot(np.real(polos_ma), np.imag(polos_ma), 'x', markersize=10, color='red',
            markeredgewidth=2, label='Polos da Planta')
zeros_ma = np.roots(num_combined)
if len(zeros_ma) > 0:
    ax_num.plot(np.real(zeros_ma), np.imag(zeros_ma), 'o', markersize=8, color='green',
                fillstyle='none', markeredgewidth=2, label='Zeros da Planta')

# Overlay sd
ax_num.plot(sd.real, sd.imag, '*', markersize=15, color='magenta', markeredgewidth=1.5, label='Polo Desejado ($s_d$)')
ax_num.plot(sd.real, -sd.imag, '*', markersize=15, color='magenta', markeredgewidth=1.5)

ax_num.axhline(0, color='black', linewidth=1)
ax_num.axvline(0, color='black', linewidth=1)
ax_num.set_title('Lugar das Raízes da Planta Original e Ponto $s_d$')
ax_num.set_xlabel('Parte Real')
ax_num.set_ylabel('Parte Imaginária')

all_pz_real = list(np.real(polos_ma)) + list(np.real(zeros_ma)) + [sd.real]
if all_pz_real:
    x_min_num, x_max_num = min(all_pz_real), max(all_pz_real)
    x_pad = max((x_max_num - x_min_num) * 0.4, 2.0)
    ax_num.set_xlim(x_min_num - x_pad, x_max_num + x_pad)

y_pad = max(abs(sd.imag) * 1.5, 5.0)
ax_num.set_ylim(-y_pad, y_pad)

ax_num.grid(True, linestyle='--', alpha=0.7)
ax_num.legend()
st.pyplot(fig_num)

st.markdown("---")

# ==========================================
# ALGORITMO DE 6 PASSOS
# ==========================================
st.header("📝 Algoritmo de Projeto (6 Passos)")

# 1. Polos Dominantes
with st.expander("**Passo 1:** Traduzir especificações para Polos Dominantes ($s_d$)", expanded=True):
    st.markdown(f"Usando as fórmulas clássicas para sistemas de 2ª ordem subamortecidos (critério de acomodação de {p.get('ts_criterion', '2%')}):")
    st.latex(r"\zeta = \frac{-\ln(\%OS / 100)}{\sqrt{\pi^2 + \ln^2(\%OS / 100)}} \quad \text{e} \quad \omega_n = \frac{" + ("4" if ts_criterion_val == 0.02 else "3") + r"}{\zeta T_s}")
    
    st.markdown(f"Para um Sobressinal de **{p['overshoot']}%** e Tempo de Acomodação de **{p['ts']} s**:")
    st.latex(rf"\zeta = {zeta:.4f}")
    st.latex(rf"\omega_n = {wn:.4f} \text{{ rad/s}}")
    
    st.markdown("A localização desejada para os polos dominantes em malha fechada é:")
    st.latex(rf"s_d = -\zeta\omega_n \pm j\omega_n\sqrt{{1-\zeta^2}}")
    st.success(rf"**$s_d = {sd.real:.4f} \pm {abs(sd.imag):.4f}j$**")

# 2. Verificar Proporcional
with st.expander("**Passo 2:** Verificar suficiência de um Controlador Proporcional"):
    st.markdown("Para sabermos se apenas um ganho ($K$) é suficiente, verificamos se o ponto $s_d$ já pertence ao Lugar das Raízes do sistema não compensado $G(s)$, aplicando o **Critério de Ângulo**:")
    st.latex(r"\angle G(s_d) = \sum \angle(s_d - p_j) - \sum \angle(s_d - z_i)")
    
    angles_poles, angles_zeros, sum_theta, sum_phi, angle_G, phi_zc = calculate_angle_condition(all_poles, all_zeros, sd)
    
    st.markdown(rf"- **Soma dos ângulos dos Polos ($\sum \theta_j$):** {sum_theta:.2f}°")
    st.markdown(rf"- **Soma dos ângulos dos Zeros ($\sum \phi_i$):** {sum_phi:.2f}°")
    
    st.latex(rf"\angle G(s_d) = {sum_theta:.2f}^\circ - {sum_phi:.2f}^\circ = {angle_G:.2f}^\circ")
    
    # Check if multiple of 180 (odd)
    is_odd_multiple = np.isclose(abs((angle_G - 180) % 360), 0, atol=2.0)
    
    if is_odd_multiple:
        st.success(rf"A fase $\angle G(s_d)$ é aproximadamente um múltiplo ímpar de $180^\circ$. **Um controlador Proporcional é suficiente!**")
        needs_pd = False
    else:
        st.warning(rf"A fase $\angle G(s_d)$ **NÃO** é um múltiplo ímpar de $180^\circ$. A deficiência de ângulo é de $\phi_{{zc}} = {phi_zc:.2f}^\circ$. **Precisaremos do Controlador PD** para suprir esse ângulo.")
        needs_pd = True

# 3. Localizar Zero do PD
with st.expander("**Passo 3:** Localizar o zero compensador ($z_c$)"):
    if not needs_pd:
        st.info("Passo ignorado, pois o PD não é estritamente necessário.")
        zc = float('inf')
    else:
        st.markdown(rf"O controlador PD tem a forma $G_c(s) = K_d(s + z_c)$. O zero em $-z_c$ deve contribuir exatamente com o ângulo faltante de $\phi_{{zc}} = {phi_zc:.2f}^\circ$.")
        st.latex(r"\tan(\phi_{zc}) = \frac{\omega_d}{z_c - \sigma_d} \implies z_c = \sigma_d + \frac{\omega_d}{\tan(\phi_{zc})}")
        
        zc = calculate_pd_zero(sd, phi_zc)
        
        if zc == float('inf'):
            st.error("Erro matemático: O ângulo é 0 ou 180, inviabilizando o cálculo trigonométrico simples do zero.")
        else:
            st.latex(rf"z_c = {-sd.real:.4f} + \frac{{{sd.imag:.4f}}}{{\tan({phi_zc:.2f}^\circ)}}")
            st.success(rf"**$z_c = {zc:.4f}$**")
            st.markdown(f"**Controlador não-sintonizado:** $G_c(s) = K_d(s + {zc:.4f})$")

# 4. Calcular Ganhos
with st.expander("**Passo 4:** Calcular o ganho total requerido ($K_d$) e proporcional ($K_p$)"):
    st.markdown("Aplicamos o **Critério de Módulo** no ponto $s_d$ para garantir que o ganho de malha aberta seja igual a 1:")
    st.latex(r"|G_c(s_d) G(s_d)| = 1 \implies K_d = \frac{1}{|(s_d + z_c) G(s_d)|}")
    
    if not needs_pd:
        # Just P controller
        G_val = complex((G_num_sym / G_den_sym).subs(s, sd).evalf())
        Kp = 1.0 / abs(G_val)
        Kd = 0.0
        st.latex(r"|K_p G(s_d)| = 1")
        st.success(rf"**$K_p = {Kp:.4f}$**, e **$K_d = 0$** (Apenas Controlador P)")
    else:
        if zc != float('inf'):
            Kd, Kp = calculate_pd_gain(G_num_sym, G_den_sym, s, zc, sd)
            st.latex(rf"K_d = \frac{{1}}{{|({sd.real:.4f} + {sd.imag:.4f}j + {zc:.4f}) G(s_d)|}}")
            st.success(rf"**$K_d = {Kd:.4f}$**")
            
            st.markdown(r"Sabendo que $K_p = K_d \cdot z_c$:")
            st.success(rf"**$K_p = {Kp:.4f}$**")
            
            st.markdown(f"**Equação final do Controlador PD:**")
            st.latex(rf"G_c(s) = {Kp:.4f} + {Kd:.4f}s")
        else:
            Kp, Kd = 0, 0
            st.error("Falha ao calcular ganho.")

# 5. Erro Estacionário
with st.expander("**Passo 5:** Calcular a constante de erro estacionário"):
    st.markdown("Avaliamos a capacidade do sistema final em rastrear entradas do tipo degrau calculando a constante de posição ($K_p^{sys}$) e o erro em regime permanente ($e_{ss}$):")
    st.latex(r"K_p^{sys} = \lim_{s \to 0} G_c(s)G(s)")
    st.latex(r"e_{ss} = \frac{1}{1 + K_p^{sys}}")
    
    Kp_sys, ess = calculate_steady_state_error(G_num_sym, G_den_sym, s, Kp, Kd)
    
    if Kp_sys == float('inf'):
        st.latex(rf"K_p^{{sys}} \to \infty")
        st.success(rf"**$e_{{ss}} = 0$** (O sistema é do Tipo 1 ou superior)")
    else:
        st.latex(rf"K_p^{{sys}} = {Kp_sys:.4f}")
        st.success(rf"**$e_{{ss}} = {ess:.4f}$** ({ess*100:.2f}%)")

# 6. Avaliação Final
with st.expander("**Passo 6:** Avaliação Final e Recomendações"):
    if ess == 0:
        st.success("O erro estacionário para entrada ao degrau é nulo. O projeto PD atendeu todas as especificações e o regime permanente já é perfeito!")
    elif ess > 0.1: # 10% tolerance is somewhat arbitrary, adjust as needed
        st.warning(f"O erro de regime para entrada em degrau é considerável ({ess*100:.1f}%). Se a especificação exigir erro zero ou muito menor, **considere utilizar um controlador PID**, pois apenas o PD melhorou o transitório, mas sacrificou (ou não melhorou o suficiente) o erro estacionário.")
    else:
        st.info(f"O erro estacionário é de {ess*100:.1f}%. A depender dos requisitos do seu projeto mecânico ou elétrico, isso pode ser perfeitamente aceitável. Se erro zero for imperativo, projete um PID.")
        
    st.markdown("### Planta em Malha Aberta Compensada: $G_c(s)G(s)$")
    Gc_sym = Kp + Kd * s
    OL_final = sp.simplify(Gc_sym * (G_num_sym / G_den_sym))
    st.latex(sp.latex(OL_final))
