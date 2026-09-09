import streamlit as st

st.set_page_config(
    page_title="Página Inicial - Sistemas de Controle",
    page_icon="🏠",
    layout="wide",
)

st.title("Bem-vindo ao Laboratório de Sistemas de Controle")

st.markdown("""
Esta é uma aplicação didática construída em **Streamlit** para o estudo prático de Engenharia de Controle.

Utilize o **menu lateral** para navegar entre as diferentes ferramentas disponíveis:

### 1. Calculadora do Lugar das Raízes (LGR)
A clássica calculadora didática que destrincha o algoritmo de construção do *Root Locus* em 12 passos fundamentais, 
mostrando toda a matemática desde a equação característica até as assíntotas, pontos de descolamento e ângulos de partida.
- **Ferramentas:** SymPy para matemática simbólica e Matplotlib para renderização fiel dos ramos.

### 2. Projeto de Controladores Clássicos [Não revisado]
Agora, o laboratório conta com páginas isoladas e dedicadas para o projeto de cada tipo de controlador. 
Cada página implementa um passo-a-passo único para sintonizar os ganhos com base nos requisitos do usuário (como sobressinal e tempo de acomodação).

- **[Página 2] Controlador Proporcional (P)**
- **[Página 3] Controlador Proporcional-Integral (PI)**
- **[Página 4] Controlador Proporcional-Derivativo (PD)**
- **[Página 5] Controlador PID Completo**

---
*Selecione uma página no menu à esquerda para começar!*
""")
