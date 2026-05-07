import streamlit as st

st.set_page_config(
    page_title="Controlador Proporcional-Integral (PI)",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Projeto de Controlador PI")
st.markdown("""
Nesta página, projetaremos um **Controlador PI ($K_p + K_i/s$)**.
O foco principal do PI é eliminar o erro de regime estacionário através da adição de um polo na origem ($s=0$) e alocar um zero próximo para não desestabilizar muito o regime transitório.
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

st.info("⚠️ Funcionalidade em construção: O passo-a-passo do projeto do Controlador PI será exibido aqui.")
