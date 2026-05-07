import streamlit as st

st.set_page_config(
    page_title="Controlador PID",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Projeto de Controlador PID")
st.markdown("""
Nesta página, projetaremos o **Controlador PID Completo**.
A ideia é juntar os benefícios do PD (melhoria do regime transitório) com o PI (eliminação do erro em regime estacionário). A estrutura em passos guiará a determinação de $K_p$, $K_i$ e $K_d$.
""")

st.sidebar.header("⚙️ Entrada da Planta G(s)")
use_expr = st.sidebar.toggle("📝 Entrada por Expressões (ex: s+1)", value=False)

if use_expr:
    st.sidebar.markdown("*Aceita notação matemática como `(s+1)(s+2)` ou `s^2 + 2*s`*")
    st.sidebar.subheader("G(s) - Numerador")
    g_num_str = st.sidebar.text_input("Expressão de G(s) do numerador:", "1")
    st.sidebar.subheader("G(s) - Denominador")
    g_den_str = st.sidebar.text_input("Expressão de G(s) do denominador:", "s*(s+2)")
else:
    st.sidebar.markdown("*Listas de coeficientes do maior para o menor grau.*")
    st.sidebar.subheader("G(s) - Numerador")
    g_num_str = st.sidebar.text_input("Coeficientes de G(s) numerador:", "1")
    st.sidebar.subheader("G(s) - Denominador")
    g_den_str = st.sidebar.text_input("Coeficientes de G(s) denominador:", "1, 2, 0")

st.sidebar.markdown("---")
st.sidebar.subheader("Requisitos de Projeto")
overshoot = st.sidebar.number_input("Sobressinal Máximo (%)", value=10.0)
ts = st.sidebar.number_input("Tempo de Acomodação (s)", value=2.0)

st.info("⚠️ Funcionalidade em construção: O passo-a-passo do projeto do Controlador PID será exibido aqui.")
