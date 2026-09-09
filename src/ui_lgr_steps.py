import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from src.utils import get_multiplicity_info, sym_to_latex
from src.plotting import plot_poles_zeros_with_multiplicity, draw_real_axis_segments, plot_base_lgr, setup_lgr_axes
from src.control_math import calculate_break_points, calculate_departure_arrival_angles

def render_12_steps(s, GH_expr_expanded_den, GH_final_display, all_poles, all_zeros, rl_segments, Np, Nz, Ls, Na, P_num_sym, P_den_sym, all_roots, s_test_real, s_test_imag, threshold):
    # ============================================================
    st.header("Algoritmo dos 12 Passos")

    # --- Passo 1 ---
    with st.expander("**Passo 1:** Escrever Polinômio Característico $P(s)$", expanded=True):
        st.markdown("Escrever o polinômio característico de modo que $K$ apareça claramente:")
        st.latex(rf"1 + G(s)H(s) = 1 + k{sym_to_latex(GH_expr_expanded_den)} = 1 + kP(s)")
    
    # --- Passo 2 ---
    with st.expander("**Passo 2:** Fatorar $P(s)$ em polos e zeros"):
        st.latex(rf"P(s) = {sym_to_latex(GH_final_display)}")

    # --- Passo 3 ---
    with st.expander("**Passo 3:** Marcar polos e zeros no plano complexo"):
        col1, col2 = st.columns(2)
        pole_mult = get_multiplicity_info(all_poles)
        zero_mult = get_multiplicity_info(all_zeros)
        with col1:
            st.markdown("**Polos:**")
            for i, (p, mult) in enumerate(pole_mult.items()):
                mult_str = f" *(multiplicidade {mult})*" if mult > 1 else ""
                st.markdown(f"- $p_{{{i+1}}} = {p.real:.4f} {p.imag:+.4f}j${mult_str}")
        with col2:
            st.markdown("**Zeros:**")
            if all_zeros:
                for i, (z, mult) in enumerate(zero_mult.items()):
                    mult_str = f" *(multiplicidade {mult})*" if mult > 1 else ""
                    st.markdown(f"- $z_{{{i+1}}} = {z.real:.4f} {z.imag:+.4f}j${mult_str}")
            else:
                st.markdown("*Não há zeros finitos.*")
    
    # --- Passo 4 ---
    with st.expander("**Passo 4:** Marcar segmentos do eixo real que pertencem ao LGR"):
        fig4, ax4 = plt.subplots(figsize=(15, 6))
        plot_poles_zeros_with_multiplicity(ax4, all_poles, all_zeros)
    
        draw_real_axis_segments(ax4, rl_segments, alpha=1.0)
    
        ax4.axhline(0, color='black', linewidth=1.2)
        ax4.axvline(0, color='black', linewidth=1.2)
    
        all_x = [p.real for p in all_poles] + [z.real for z in all_zeros]
        for seg in rl_segments:
            all_x.extend([seg[0], seg[1]])
        if all_x:
            x_min, x_max = min(all_x), max(all_x)
            x_span = x_max - x_min
            pad = x_span * 0.1 if x_span > 0 else 1.0
            ax4.set_xlim(x_min - pad, x_max + pad)
            y_coords = [abs(p.imag) for p in all_poles] + [abs(z.imag) for z in all_zeros]
            y_limit = max(y_coords) + 1 if y_coords else 2
            ax4.set_ylim(-y_limit, y_limit)
    
        ax4.set_aspect('auto')
        ax4.set_title('LGR - Segmentos do Eixo Real', fontsize=14)
        ax4.set_xlabel(r'Eixo Real ($\sigma$)', fontsize=12)
        ax4.set_ylabel(r'Eixo Imaginário ($j\omega$)', fontsize=12)
        ax4.grid(True, linestyle=':', alpha=0.6)
        ax4.legend(loc='upper right')
        plt.tight_layout()
        st.pyplot(fig4)
    
        st.markdown("**Regra:** A esquerda de números ímpares de polos ou zeros reais.")
        if rl_segments:
            for seg in rl_segments:
                kind = seg[2] if len(seg) > 2 else 'finite'
                if kind == 'inf_left':
                    st.markdown(rf"- Segmento: $[-\infty, {seg[1]:.4f}]$")
                elif kind == 'inf_right':
                    st.markdown(rf"- Segmento: $[{seg[0]:.4f}, +\infty]$")
                else:
                    st.markdown(f"- Segmento: $[{seg[0]:.4f}, {seg[1]:.4f}]$")
        else:
            st.markdown("*Nenhum segmento do eixo real pertence ao LGR.*")
    
    # --- Passo 5 ---
    with st.expander("**Passo 5:** Determinar o número de lugares separados"):
        st.markdown(rf"O número de polos $N_p$ é: **{Np}**")
        st.markdown(rf"O número de zeros $N_z$ é: **{Nz}**")
        st.markdown(rf"O número de lugares separados $L_s = \max\{{N_p, N_z\}}$ é: **{Ls}**")
    
    # --- Passo 6 ---
    with st.expander("**Passo 6:** Simetria"):
        st.markdown("O LGR é **simétrico em relação ao eixo real**.")
        st.markdown("Isso se deve ao fato de que raízes complexas sempre ocorrem em pares conjugados.")
    
    # --- Passo 7 ---
    with st.expander(r"**Passo 7:** Determinar centro $\sigma_A$ e ângulos $\phi_A$ das assíntotas"):
        if Na > 0:
            sum_poles = sum(np.real(all_poles))
            sum_zeros = sum(np.real(all_zeros)) if Nz > 0 else 0
            sigma_A = (sum_poles - sum_zeros) / Na
    
            angles_deg = [((2 * q + 1) * 180) / Na for q in range(Na)]
            angles_rad = np.deg2rad(angles_deg)
    
            st.markdown(r"### Centro das assíntotas, $\sigma_A$:")
            st.latex(r"\sigma_A = \frac{\sum (-p_j) - \sum (-z_i)}{n_p - n_z}")
            st.latex(rf"\sigma_A = \frac{{({sum_poles:.2f}) - ({sum_zeros:.2f})}}{{{Na}}} = {sigma_A:.2f}")

            st.markdown(r"### Ângulos das assíntotas, $\phi_A$:")
            st.latex(r"\phi_A = \frac{(2q + 1)}{n_p - n_z} \cdot 180^\circ; \forall q\in\{0,...,n_p-n_z-1\}")
            for q, ang in enumerate(angles_deg):
                st.markdown(rf"Para $q = {q}$: $\phi_A = {ang:.1f}°$")
    
            # Plot com assintotas
            fig7, ax7 = plt.subplots(figsize=(15, 6))
            plot_poles_zeros_with_multiplicity(ax7, all_poles, all_zeros)
    
            draw_real_axis_segments(ax7, rl_segments, alpha=1.0)
    
            line_length = 30
            for i, angle in enumerate(angles_rad):
                dx = line_length * np.cos(angle)
                dy = line_length * np.sin(angle)
                ax7.plot([sigma_A, sigma_A + dx], [0, dy], '--', color='darkorange',
                         alpha=0.8, linewidth=2, label='Assíntotas' if i == 0 else "")
    
            ax7.plot(sigma_A, 0, '*', markersize=12, color='darkviolet',
                     label=r'Centroide ($\sigma_A$)')
    
            ax7.axhline(0, color='black', linewidth=1.2)
            ax7.axvline(0, color='black', linewidth=1.2)
    
            all_x = [p.real for p in all_poles] + [z.real for z in all_zeros] + [sigma_A]
            for seg in rl_segments:
                all_x.extend([seg[0], seg[1]])
            if all_x:
                x_min, x_max = min(all_x), max(all_x)
                x_span = x_max - x_min
                pad = x_span * 0.2 if x_span > 0 else 3.0
                ax7.set_xlim(x_min - pad, max(x_max + pad, 2))
                y_coords = [abs(p.imag) for p in all_poles] + [abs(z.imag) for z in all_zeros]
                y_limit = max(y_coords) + 6 if y_coords else 6
                ax7.set_ylim(-y_limit, y_limit)
    
            ax7.set_aspect('auto')
            ax7.set_title('LGR com Assíntotas', fontsize=14)
            ax7.set_xlabel(r'Eixo Real ($\sigma$)', fontsize=12)
            ax7.set_ylabel(r'Eixo Imaginário ($j\omega$)', fontsize=12)
            ax7.grid(True, linestyle=':', alpha=0.6)
            ax7.legend(loc='upper right')
            plt.tight_layout()
            st.pyplot(fig7)
        else:
            st.markdown("**Não há assíntotas para o infinito.** $n_p \\le n_z$")
    
    # --- Passo 8: Pontos de Saída/Entrada (Descolamento) ---
    with st.expander("**Passo 8:** Pontos de Saída/Entrada no Eixo Real"):
        st.markdown('Este passo parte do princípio de que os os pontos em que o LGR sai do eixo real são pontos em que')
        st.latex(r'1 + KP(S) = 0 \implies K = -\frac{1}{P(s)} \equiv p(s)')

        # Utilize the imported function for math logic
        K_expr_break, break_eq, break_roots_complex, valid_break_points = calculate_break_points(P_num_sym, P_den_sym, s, rl_segments)
    
        st.markdown(r"**1º Encontrar $p(s)$:**")
        st.latex(rf"p(s) = -\frac{{1}}{{P(s)}} = -\frac{{D(s)}}{{N(s)}} = {sym_to_latex(sp.cancel(K_expr_break))}")
    
        st.markdown(r"**2º Determinar as raízes de $\frac{dp(s)}{ds} = 0$:**")
        dK_ds_simplified = sp.cancel(sp.diff(K_expr_break, s))
        st.latex(rf"\frac{{dp(s)}}{{ds}} = {sym_to_latex(dK_ds_simplified)}")
    
        st.markdown(r"Para a derivada ser zero, basta que o polinômio do numerador seja zero:")
        st.latex(rf"{sym_to_latex(sp.expand(break_eq))} = 0")
    
        tol = 1e-5
        all_roots_str = ", ".join([f"{r.real:.4f} + {r.imag:.4f}j" if abs(r.imag) > tol else f"{r.real:.4f}" for r in break_roots_complex])
        st.markdown(rf"**Todas as raízes calculadas:** $s = [{all_roots_str}]$")
    
        if valid_break_points:
            points_str = ", ".join([str(p) for p in valid_break_points])
            st.success(rf"**Raízes válidas (pertencem ao LGR no eixo real):** $s = {points_str}$")
        else:
            st.info("**Não há raízes válidas no eixo real para este sistema.**")
    
        # Plot: breakaway points
        fig8, ax8 = plt.subplots(figsize=(15, 6))
        plot_poles_zeros_with_multiplicity(ax8, all_poles, all_zeros)
        draw_real_axis_segments(ax8, rl_segments, alpha=1.0)
        if Na > 0:
            line_length = 30
            for i, angle in enumerate(angles_rad):
                dx = line_length * np.cos(angle)
                dy = line_length * np.sin(angle)
                ax8.plot([sigma_A, sigma_A + dx], [0, dy], '--', color='darkorange',
                         alpha=0.5, linewidth=2, label='Assíntotas' if i == 0 else "")
        if valid_break_points:
            ax8.plot(valid_break_points, [0]*len(valid_break_points), 'd', markersize=10,
                     color='magenta', markeredgewidth=2, label='Pontos de Saída/Entrada')
            for p in valid_break_points:
                ax8.text(p, 0.5, f'{p:.2f}', color='magenta', fontsize=11, fontweight='bold',
                         ha='center', bbox=dict(facecolor='white', edgecolor='magenta',
                         boxstyle='round,pad=0.2', alpha=0.8))
    
        ax8.axhline(0, color='black', linewidth=1.2)
        ax8.axvline(0, color='black', linewidth=1.2)
        all_x8 = [p.real for p in all_poles] + [z.real for z in all_zeros]
        if Na > 0:
            all_x8.append(sigma_A)
        all_x8.extend(valid_break_points)
        for seg in rl_segments:
            all_x8.extend([seg[0], seg[1]])
        if all_x8:
            x_min8, x_max8 = min(all_x8), max(all_x8)
            x_span8 = x_max8 - x_min8
            pad8 = x_span8 * 0.2 if x_span8 > 0 else 3.0
            ax8.set_xlim(x_min8 - pad8, max(x_max8 + pad8, 2))
            y_coords8 = [abs(p.imag) for p in all_poles] + [abs(z.imag) for z in all_zeros]
            y_limit8 = max(y_coords8) + 6 if y_coords8 else 6
            ax8.set_ylim(-y_limit8, y_limit8)
        ax8.set_aspect('auto')
        ax8.set_title('Lugar das Raízes (com Pontos de Descolamento)', fontsize=14)
        ax8.set_xlabel(r'Eixo Real ($\sigma$)', fontsize=12)
        ax8.set_ylabel(r'Eixo Imaginário ($j\omega$)', fontsize=12)
        ax8.grid(True, linestyle=':', alpha=0.6)
        ax8.legend(loc='upper right')
        plt.tight_layout()
        st.pyplot(fig8)
    
    # --- Passo 9: Cruzamento com o Eixo Imaginário (Routh-Hurwitz) ---
    with st.expander("**Passo 9:** Cruzamento com o Eixo Imaginário (Routh-Hurwitz)"):
        k = sp.symbols('k', real=True)
        CE_expr = sp.expand(P_den_sym + k * P_num_sym)
        CE_poly = sp.Poly(CE_expr, s)
        coeffs_routh = CE_poly.all_coeffs()
        n_routh = CE_poly.degree()
    
        st.markdown("### Cruzamento com o Eixo Imaginário")
        st.markdown(r"Equação Característica $1 + k \frac{N(s)}{D(s)} = 0 \implies D(s) + kN(s) = 0$:")
        st.latex(rf"{sym_to_latex(sp.collect(CE_expr, s))} = 0")

        # Build Routh table
        routh_table = []
        row0 = coeffs_routh[0::2]
        row1 = coeffs_routh[1::2]
        max_len = max(len(row0), len(row1))
        row0.extend([0] * (max_len - len(row0)))
        row1.extend([0] * (max_len - len(row1)))
        routh_table.append(row0)
        routh_table.append(row1)
    
        for i in range(2, n_routh + 1):
            prev_row = routh_table[i-1]
            pprev_row = routh_table[i-2]
            new_row = []
            for j in range(len(prev_row) - 1):
                if prev_row[0] == 0:
                    elem = 0
                else:
                    elem = (prev_row[0] * pprev_row[j+1] - pprev_row[0] * prev_row[j+1]) / prev_row[0]
                new_row.append(sp.cancel(elem))
            new_row.append(0)
            routh_table.append(new_row)
    
        # Display Routh table as markdown
        table_md = "| Colunas | " + " | ".join([f"{i+1}" for i in range(max_len)]) + " |\n"
        table_md += "|" + "---|" * (max_len + 1) + "\n"
        for i, row in enumerate(routh_table):
            power = n_routh - i
            row_str = f"| $s^{power}$ | "
            row_str += " | ".join([f"${sym_to_latex(elem)}$" if str(elem) != "0" else "$0$" for elem in row]) + " |\n"
            table_md += row_str
    
        st.markdown("### Tabela de Routh-Hurwitz:")
        st.markdown(table_md)
    
        # Find stability margin
        s1_elem = routh_table[n_routh-1][0]
        st.markdown(r"Para encontrar a margem de estabilidade, forçamos o primeiro termo da linha $s^1$ a ser zero:")
        st.latex(rf"{sym_to_latex(sp.cancel(s1_elem))} = 0")
    
        k_crits = []
        crossing_points = []
    
        if s1_elem.has(k):
            num_rh, den_rh = sp.fraction(sp.cancel(s1_elem))
            possible_ks = sp.solve(num_rh, k)
            for pk in possible_ks:
                if pk.is_real and pk > 0:
                    k_crits.append(float(pk))
    
        for kc in k_crits:
            aux_row = routh_table[n_routh-2]
            A = aux_row[0].subs(k, kc)
            B = aux_row[1].subs(k, kc)
            aux_eq = sp.simplify(A * s**2 + B)
            st.markdown(rf"Para o ganho crítico $k = {kc:.4f}$, a equação auxiliar (da linha $s^2$) é:")
            st.latex(rf"{sym_to_latex(aux_eq)} = 0")
            roots_aux = sp.solve(aux_eq, s)
            for r in roots_aux:
                crossing_points.append(complex(r))
    
        valid_crossings = sorted(
            list(set([complex(pt) for pt in crossing_points if abs(pt.real) < 1e-5])),
            key=lambda x: x.imag
        )
    
        if valid_crossings:
            cross_str = ", ".join([f"{pt.imag:.4f}j" if pt.imag >= 0 else f"- {abs(pt.imag):.4f}j" for pt in valid_crossings])
            st.success(rf"**Pontos de cruzamento exatos no eixo imaginário:** $s = {cross_str}$")
        else:
            st.info("**O Lugar das Raízes não cruza o eixo imaginário para $k > 0$.**")
    
        # Plot: imaginary axis crossings
        fig9, ax9 = plt.subplots(figsize=(15, 8))
        plot_base_lgr(ax9, all_poles, all_zeros, rl_segments, all_roots)
        if Na > 0:  # todo: add as a function
            line_length = 30
            for i, angle in enumerate(angles_rad):
                dx = line_length * np.cos(angle)
                dy = line_length * np.sin(angle)
                ax9.plot([sigma_A, sigma_A + dx], [0, dy], '--', color='darkorange',
                         alpha=0.5, linewidth=2, label='Assíntotas' if i == 0 else "")
        if valid_break_points:
            ax9.plot(valid_break_points, [0]*len(valid_break_points), 'd', markersize=10,
                     color='magenta', alpha=0.7)
        if valid_crossings:
            for pt in valid_crossings:
                ax9.plot(0, pt.imag, 's', markersize=12, color='cyan', markeredgecolor='navy',
                         markeredgewidth=2, label='Cruzamento Eixo Imag.' if pt == valid_crossings[0] else "")
                ax9.annotate(f'  jω = {pt.imag:.2f}', xy=(0, pt.imag), fontsize=10,
                             fontweight='bold', color='navy')
        setup_lgr_axes(ax9, all_poles, all_zeros, rl_segments, title='LGR com Cruzamentos no Eixo Imaginário')
        plt.tight_layout()
        st.pyplot(fig9)
    
    # --- Passo 10: Ângulos de Partida e Chegada ---
    with st.expander("**Passo 10:** Ângulos de Partida e Chegada"):
        st.markdown("### *Ângulos de Partida* (dos polos complexos) e *Ângulos de Chegada* (nos zeros complexos)")
        st.markdown(r"""
    O *ângulo de partida* indica a **direção** em que o lugar das raízes "sai" de um polo complexo 
    quando $K$ começa a crescer a partir de zero. Analogamente, o *ângulo de chegada* indica a direção 
    em que o LGR "entra" em um zero complexo quando $K \to \infty$.
    """)
    
        tol_10 = 1e-5  # tolerance for im component == 0
        complex_poles_10 = [p for p in all_poles if abs(p.imag) > tol_10]
        complex_zeros_10 = [z for z in all_zeros if abs(z.imag) > tol_10]
    
        departure_angles_full, arrival_angles_full = calculate_departure_arrival_angles(all_poles, all_zeros, tol_10)
    
        if not complex_poles_10 and not complex_zeros_10:
            st.info("**Não há polos ou zeros complexos neste sistema.** O Passo 10 não se aplica.")
        else:
            # We need simpler dicts for plotting
            departure_angles = {k: v[0] for k, v in departure_angles_full.items()}
            arrival_angles = {k: v[0] for k, v in arrival_angles_full.items()}
    
            # ===================== DEPARTURE ANGLES =====================
            if complex_poles_10:
                st.markdown("---")
                st.markdown("#### Ângulos de Partida ($\\theta_d$) — Saída dos polos complexos")
                st.markdown(r"""
    **Condição de ângulo** aplicada a um ponto $s$ infinitesimalmente próximo do polo $p_k$:
    
    $$\sum_{j} \angle(p_k - z_j) - \sum_{\substack{i \\ i \neq k}} \angle(p_k - p_i) - \theta_d = (2q+1) \cdot 180°$$
    
    Isolando $\theta_d$ (para $q = 0$):
    
    $$\boxed{\theta_d = 180° - \sum_{\substack{i \\ i \neq k}} \theta_i + \sum_{j} \phi_j}$$
    
    onde $\theta_i = \angle(p_k - p_i)$ é o ângulo do vetor **do polo $p_i$ até $p_k$**, 
    e $\phi_j = \angle(p_k - z_j)$ é o ângulo do vetor **do zero $z_j$ até $p_k$**.
    """)
    
                for pk in complex_poles_10:  # todo: ignore conjugates
                    angle_dep, angles_from_other_poles, angles_from_zeros = departure_angles_full[pk]
                    other_poles = [p for p in all_poles if not np.isclose(pk, p)]
    
                    st.markdown(f"##### Polo $p_k = {pk.real:.4f}{pk.imag:+.4f}j$")
    
                    # Show each vector and angle from other poles
                    st.markdown("**Ângulos dos vetores dos outros polos até $p_k$:**")
                    for i, (p, ang) in enumerate(zip(other_poles, angles_from_other_poles)):
                        vec = pk - p
                        st.latex(  # todo: change display format (results in new line)
                            rf"\theta_{{{i+1}}} = \angle(p_k - p_{{{i+1}}}) = "
                            rf"\angle\big(({pk.real:.4f}{pk.imag:+.4f}j) - ({p.real:.4f}{p.imag:+.4f}j)\big) = "
                            rf"\angle({vec.real:.4f}{vec.imag:+.4f}j) = {ang:.2f}°"
                        )
    
                    # Show each vector and angle from zeros
                    if all_zeros:
                        st.markdown("**Ângulos dos vetores dos zeros até $p_k$:**")
                        for j, (z, ang) in enumerate(zip(all_zeros, angles_from_zeros)):
                            vec = pk - z
                            st.latex(  # todo: change display format (results in new line)
                                rf"\phi_{{{j+1}}} = \angle(p_k - z_{{{j+1}}}) = "
                                rf"\angle\big(({pk.real:.4f}{pk.imag:+.4f}j) - ({z.real:.4f}{z.imag:+.4f}j)\big) = "
                                rf"\angle({vec.real:.4f}{vec.imag:+.4f}j) = {ang:.2f}°"
                            )
                    else:
                        st.markdown(r"*Não há zeros finitos, logo $\sum \phi_j = 0°$*")
    
                    # Show summations with explicit terms
                    sum_theta = sum(angles_from_other_poles)
                    sum_phi = sum(angles_from_zeros)
    
                    theta_terms = " + ".join([f"({a:.2f}°)" for a in angles_from_other_poles])
                    st.latex(rf"\sum \theta_i = {theta_terms} = {sum_theta:.2f}°")
    
                    if angles_from_zeros:
                        phi_terms = " + ".join([f"({a:.2f}°)" for a in angles_from_zeros])
                        st.latex(rf"\sum \phi_j = {phi_terms} = {sum_phi:.2f}°")
    
                    # Final substitution
                    st.latex(
                        rf"\theta_d = 180° - ({sum_theta:.2f}°) + ({sum_phi:.2f}°) = "
                        rf"180° {-sum_theta:+.2f}° {sum_phi:+.2f}°"
                    )
                    st.success(rf"$\theta_d = {angle_dep:.2f}°$")  # todo: format [0,360]
                    st.markdown("---")
            else:
                st.info("Não há polos complexos — ângulos de partida não são aplicáveis.")
    
            # ===================== ARRIVAL ANGLES =====================
            if complex_zeros_10:
                st.markdown("#### Ângulos de Chegada ($\\theta_a$) — Entrada nos zeros complexos")
                st.markdown(r"""
    **Condição de ângulo** aplicada a um ponto $s$ infinitesimalmente próximo do zero $z_k$:
    
    $$\theta_a + \sum_{\substack{j \\ j \neq k}} \angle(z_k - z_j) - \sum_{i} \angle(z_k - p_i) = (2q+1) \cdot 180°$$
    
    Isolando $\theta_a$ (para $q = 0$):
    
    $$\boxed{\theta_a = 180° - \sum_{\substack{j \\ j \neq k}} \phi_j + \sum_{i} \theta_i}$$
    
    onde $\theta_i = \angle(z_k - p_i)$ é o ângulo do vetor **do polo $p_i$ até $z_k$**, 
    e $\phi_j = \angle(z_k - z_j)$ é o ângulo do vetor **do zero $z_j$ até $z_k$**.
    """)
    
                for zk in complex_zeros_10:
                    angle_arr, angles_from_other_zeros, angles_from_poles = arrival_angles_full[zk]
                    other_zeros = [z for z in all_zeros if not np.isclose(zk, z)]
    
                    st.markdown(f"##### Zero $z_k = {zk.real:.4f}{zk.imag:+.4f}j$")
    
                    # Show each vector and angle from poles
                    st.markdown("**Ângulos dos vetores dos polos até $z_k$:**")
                    for i, (p, ang) in enumerate(zip(all_poles, angles_from_poles)):
                        vec = zk - p
                        st.latex(
                            rf"\theta_{{{i+1}}} = \angle(z_k - p_{{{i+1}}}) = "
                            rf"\angle\big(({zk.real:.4f}{zk.imag:+.4f}j) - ({p.real:.4f}{p.imag:+.4f}j)\big) = "
                            rf"\angle({vec.real:.4f}{vec.imag:+.4f}j) = {ang:.2f}°"
                        )
    
                    # Show each vector and angle from other zeros
                    if other_zeros:
                        st.markdown("**Ângulos dos vetores dos outros zeros até $z_k$:**")
                        for j, (z, ang) in enumerate(zip(other_zeros, angles_from_other_zeros)):
                            vec = zk - z
                            st.latex(
                                rf"\phi_{{{j+1}}} = \angle(z_k - z_{{{j+1}}}) = "
                                rf"\angle\big(({zk.real:.4f}{zk.imag:+.4f}j) - ({z.real:.4f}{z.imag:+.4f}j)\big) = "
                                rf"\angle({vec.real:.4f}{vec.imag:+.4f}j) = {ang:.2f}°"
                            )
                    else:
                        st.markdown(r"*Não há outros zeros, logo $\sum \phi_j = 0°$*")
    
                    # Show summations with explicit terms
                    sum_phi_z = sum(angles_from_other_zeros)
                    sum_theta_z = sum(angles_from_poles)
    
                    theta_z_terms = " + ".join([f"({a:.2f}°)" for a in angles_from_poles])
                    st.latex(rf"\sum \theta_i = {theta_z_terms} = {sum_theta_z:.2f}°")
    
                    if angles_from_other_zeros:
                        phi_z_terms = " + ".join([f"({a:.2f}°)" for a in angles_from_other_zeros])
                        st.latex(rf"\sum \phi_j = {phi_z_terms} = {sum_phi_z:.2f}°")
    
                    # Final substitution
                    st.latex(
                        rf"\theta_a = 180° - ({sum_phi_z:.2f}°) + ({sum_theta_z:.2f}°) = "
                        rf"180° {-sum_phi_z:+.2f}° {sum_theta_z:+.2f}°"
                    )
                    st.success(rf"$\theta_a = {angle_arr:.2f}°$")
                    st.markdown("---")

                    # --- Plot ---  # fixme: needs to plot if there is only complex zeroes or complex poles
                    fig10, ax10 = plt.subplots(figsize=(15, 8))
                    plot_base_lgr(ax10, all_poles, all_zeros, rl_segments, all_roots)
                    if Na > 0:
                        line_length = 40
                        for i, angle in enumerate(angles_rad):
                            dx = line_length * np.cos(angle)
                            dy = line_length * np.sin(angle)
                            ax10.plot([sigma_A, sigma_A + dx], [0, dy], '--', color='darkorange',
                                      alpha=0.4, linewidth=2, label='Assíntotas' if i == 0 else "")
                    if valid_break_points:
                        ax10.plot(valid_break_points, [0] * len(valid_break_points), 'd', markersize=12,
                                  color='magenta', markeredgewidth=2, label='Pontos Saída/Entrada')
                    if valid_crossings:
                        cross_y = [pt.imag for pt in valid_crossings]
                        ax10.plot([0] * len(valid_crossings), cross_y, '*', markersize=18, color='cyan',
                                  markeredgewidth=2, markeredgecolor='black', label='Cruzamento jω')

                    arrow_len = 1.5
                    text_offset = 0.8
                    extra_x = [p.real for p in all_poles] + [z.real for z in all_zeros]
                    extra_y = [p.imag for p in all_poles] + [z.imag for z in all_zeros]
                    for seg in rl_segments:
                        extra_x.extend([seg[0], seg[1]])
                    if Na > 0:
                        extra_x.append(sigma_A)
                    extra_x.extend(valid_break_points)

                    # Draw departure arrows (red, outward from pole)
                    for pk, angle_deg in departure_angles.items():  # fixme: UnboundLocalError
                        angle_rad_d = np.radians(angle_deg)
                        dx = arrow_len * np.cos(angle_rad_d)
                        dy = arrow_len * np.sin(angle_rad_d)
                        ax10.annotate('', xy=(pk.real + dx, pk.imag + dy),
                                      xytext=(pk.real, pk.imag),
                                      arrowprops=dict(arrowstyle='->', color='darkred', lw=2, mutation_scale=15))
                        tx = pk.real + (arrow_len + text_offset) * np.cos(angle_rad_d)
                        ty = pk.imag + (arrow_len + text_offset) * np.sin(angle_rad_d)
                        if abs(np.sin(angle_rad_d)) < 0.3:
                            ty += 0.6 * np.sign(pk.imag)
                        ax10.text(tx, ty, f'{angle_deg:.1f}°', color='darkred', fontsize=10, fontweight='bold',
                                  ha='center', va='center',
                                  bbox=dict(facecolor='white', edgecolor='darkred',
                                            boxstyle='round,pad=0.2', alpha=0.9))
                        extra_x.append(pk.real + (arrow_len + text_offset + 1) * np.cos(angle_rad_d))
                        extra_y.append(pk.imag + (arrow_len + text_offset + 1) * np.sin(angle_rad_d))

                    # Draw arrival arrows (green, outward from zero)
                    for zk, angle_deg in arrival_angles.items():  # fixme: UnboundLocalError
                        angle_rad_a = np.radians(angle_deg)
                        dx = arrow_len * np.cos(angle_rad_a)
                        dy = arrow_len * np.sin(angle_rad_a)
                        ax10.annotate('', xy=(zk.real + dx, zk.imag + dy),
                                      xytext=(zk.real, zk.imag),
                                      arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2, mutation_scale=15))
                        tx = zk.real + (arrow_len + text_offset) * np.cos(angle_rad_a)
                        ty = zk.imag + (arrow_len + text_offset) * np.sin(angle_rad_a)
                        ax10.text(tx, ty, f'{angle_deg:.1f}°', color='darkgreen', fontsize=10, fontweight='bold',
                                  ha='center', va='center',
                                  bbox=dict(facecolor='white', edgecolor='darkgreen',
                                            boxstyle='round,pad=0.2', alpha=0.9))
                        extra_x.append(zk.real + (arrow_len + text_offset + 1) * np.cos(angle_rad_a))
                        extra_y.append(zk.imag + (arrow_len + text_offset + 1) * np.sin(angle_rad_a))

                    # Set limits to include all arrows and text
                    if extra_x:
                        x_min10, x_max10 = min(extra_x), max(extra_x)
                        x_span10 = x_max10 - x_min10
                        pad_x10 = x_span10 * 0.25 if x_span10 > 0 else 5.0
                        ax10.set_xlim(x_min10 - pad_x10, max(x_max10 + pad_x10, 5))
                    if extra_y:
                        y_abs = [abs(y) for y in extra_y]
                        y_limit10 = max(y_abs) + 4 if y_abs else 8
                        ax10.set_ylim(-y_limit10, y_limit10)

                    ax10.set_aspect('auto')
                    ax10.set_title('Lugar das Raízes com Vetores de Partida/Chegada', fontsize=16, pad=20)
                    ax10.set_xlabel(r'Eixo Real ($\sigma$)', fontsize=14)
                    ax10.set_ylabel(r'Eixo Imaginário ($j\omega$)', fontsize=14)
                    ax10.grid(True, linestyle=':', alpha=0.7)
                    handles, labels = ax10.get_legend_handles_labels()
                    by_label = dict(zip(labels, handles))
                    ax10.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=11)
                    plt.tight_layout()
                    st.pyplot(fig10)

            else:
                st.info("Não há zeros complexos — ângulos de chegada não são aplicáveis.")

    # --- Passo 11: Critério de Ângulo ---
    with st.expander("**Passo 11:** Critério de Ângulo"):
        st.markdown('Determinar a localização das raízes que satisfazem o critério do ângulo de fase:')
        st.latex(r'\angle \left. P(s) \right|_{s=s_i} = \left.\left( \sum_{n_p} \theta_j - \sum_{n_p} \phi_j \right) \right|_{s=s_i} = 180^\circ \pm q 360^\circ')
        st.markdown('onde $q \in \{0,...,n_p-n_z-1\}$.')

        s_test = complex(s_test_real, s_test_imag)
    
        st.markdown(f"**Ponto de teste:** $s_i = {s_test.real} {s_test.imag:+}j$")
    
        theta_poles = [np.degrees(np.angle(s_test - p)) for p in all_poles]
        phi_zeros = [np.degrees(np.angle(s_test - z)) for z in all_zeros]
    
        sum_theta = sum(theta_poles)
        sum_phi = sum(phi_zeros)
        total_angle = sum_theta - sum_phi
        total_angle_norm = total_angle % 360.0
        is_on_lgr = (180.0 - threshold) <= total_angle_norm <= (180.0 + threshold)
    
        st.markdown(r"#### Ângulos partindo dos Polos ($\theta_i$):")  # todo: name poles and zeroes, use absolute angles
        for i, p in enumerate(all_poles):
            st.markdown(rf"Polo $p_{{{i+1}}} = {p.real:.2f}{p.imag:+.2f}j$: $\theta_{{{i+1}}} = {theta_poles[i]:.2f}°$")
        st.markdown(rf"**Somatório:** ${sum_theta:.2f}°$")
    
        if all_zeros:
            st.markdown(r"#### Ângulos partindo dos Zeros ($\phi_j$):")
            for j, z in enumerate(all_zeros):
                st.markdown(rf"Zero $z_{{{j+1}}} = {z.real:.2f}{z.imag:+.2f}j$: $\phi_{{{j+1}}} = {phi_zeros[j]:.2f}°$")
            st.markdown(rf"**Somatório:** ${sum_phi:.2f}°$")
        else:
            st.markdown(r"*Não há zeros, logo $\sum \phi_j = 0°$*")
    
        st.markdown("#### Avaliação Final:")
        st.markdown(rf"Ângulo Resultante = ${sum_theta:.2f}° - {sum_phi:.2f}° = {total_angle:.2f}°$")
    
        if total_angle < 0 or total_angle >= 360:
            st.markdown(rf"Normalizado (módulo 360°): ${total_angle_norm:.2f}°$")
    
        if is_on_lgr:
            st.success(rf"O ponto **PERTENCE** ao LGR! ({total_angle_norm:.2f}° está dentro de 180° ± {threshold}°)")
        else:
            st.error(rf"O ponto **NÃO PERTENCE** ao LGR! ({total_angle_norm:.2f}° fora de 180° ± {threshold}°)")
    
        # Plot do critério de ângulo
        fig11, ax11 = plt.subplots(figsize=(12, 6))
        plot_poles_zeros_with_multiplicity(ax11, all_poles, all_zeros)
    
        draw_real_axis_segments(ax11, rl_segments, alpha=0.5)
    
        point_color = 'limegreen' if is_on_lgr else 'red'
        point_marker = '*' if is_on_lgr else 'X'
        point_label = f's_i = {s_test.real}{s_test.imag:+}j ({"Pertence" if is_on_lgr else "Não pertence"})'
        ax11.plot(s_test.real, s_test.imag, point_marker, markersize=18, color=point_color,
                  markeredgecolor='black', label=point_label)
    
        for p in all_poles:
            ax11.plot([p.real, s_test.real], [p.imag, s_test.imag], ':', color='red', alpha=0.3)
        for z in all_zeros:
            ax11.plot([z.real, s_test.real], [z.imag, s_test.imag], ':', color='green', alpha=0.3)
    
        ax11.axhline(0, color='black', linewidth=1.2)
        ax11.axvline(0, color='black', linewidth=1.2)
    
        all_x = [p.real for p in all_poles] + [z.real for z in all_zeros] + [s_test.real]
        if all_x:
            x_min, x_max = min(all_x), max(all_x)
            ax11.set_xlim(x_min - 2, x_max + 2)
            y_coords = [abs(p.imag) for p in all_poles] + [abs(z.imag) for z in all_zeros] + [abs(s_test.imag)]
            y_limit = max(y_coords) + 2 if y_coords else 4
            ax11.set_ylim(-y_limit, y_limit)
    
        ax11.set_aspect('auto')
        ax11.set_title('Critério de Ângulo: Verificação de Ponto', fontsize=14)
        ax11.set_xlabel(r'Eixo Real ($\sigma$)', fontsize=12)
        ax11.set_ylabel(r'Eixo Imaginário ($j\omega$)', fontsize=12)
        ax11.grid(True, linestyle=':', alpha=0.6)
        ax11.legend(loc='upper right')
        plt.tight_layout()
        st.pyplot(fig11)  # todo: add full LGR to plot
    
    # --- Passo 12: Critério de Módulo (Cálculo de K) ---
    with st.expander("**Passo 12:** Critério de Módulo (Cálculo de K)"):
        st.markdown("### Critério de Módulo")
        st.markdown(r"Se um ponto $s_i$ pertence ao LGR, o valor de $K$ correspondente é dado por:")
        st.latex(r"K = \left.\frac{1}{|P(s)|}\right|_{s=s_i} = \frac{\prod |s_0 - p_j|}{\prod |s_0 - z_j|}")
    
        s_test_k = complex(s_test_real, s_test_imag)
    
        # Check if point is approximately on the LGR (reuse criterion from step 11)
        theta_p = [np.degrees(np.angle(s_test_k - p)) for p in all_poles]
        phi_z = [np.degrees(np.angle(s_test_k - z)) for z in all_zeros]
        angle_total = (sum(theta_p) - sum(phi_z)) % 360.0
        on_lgr_k = (180.0 - threshold) <= angle_total <= (180.0 + threshold)
    
        prod_poles = 1.0
        for p in all_poles:
            prod_poles *= abs(s_test_k - p)
    
        prod_zeros = 1.0
        for z in all_zeros:
            prod_zeros *= abs(s_test_k - z)
    
        st.markdown(f"**Ponto de teste:** $s_0 = {s_test_k.real} {s_test_k.imag:+}j$")
    
        st.markdown("#### Distâncias dos polos:")
        for i, p in enumerate(all_poles):
            dist = abs(s_test_k - p)
            st.markdown(rf"$|s_0 - p_{{{i+1}}}| = |{s_test_k.real}{s_test_k.imag:+}j - ({p.real:.2f}{p.imag:+.2f}j)| = {dist:.4f}$")
        st.markdown(rf"$\prod |s_0 - p_i| = {prod_poles:.4f}$")
    
        if all_zeros:
            st.markdown("#### Distâncias dos zeros:")
            for j, z in enumerate(all_zeros):
                dist = abs(s_test_k - z)
                st.markdown(rf"$|s_0 - z_{{{j+1}}}| = |{s_test_k.real}{s_test_k.imag:+}j - ({z.real:.2f}{z.imag:+.2f}j)| = {dist:.4f}$")
            st.markdown(rf"$\prod |s_0 - z_j| = {prod_zeros:.4f}$")
        else:
            st.markdown(r"*Não há zeros finitos, logo $\prod |s_0 - z_j| = 1$*")
    
        if prod_zeros > 1e-10:
            K_value = prod_poles / prod_zeros
            st.markdown("#### Resultado:")
            st.latex(rf"K = \frac{{{prod_poles:.4f}}}{{{prod_zeros:.4f}}} = {K_value:.4f}")
    
            if on_lgr_k:
                st.success(rf"O ponto pertence ao LGR. O valor de $K$ correspondente é: **K = {K_value:.4f}**")
            else:
                st.warning(rf"O ponto **não pertence** ao LGR (falha no critério de ângulo). O valor calculado de K = {K_value:.4f} é apenas uma referência.")
        else:
            st.error("Não é possível calcular K: o ponto coincide com um zero.")
