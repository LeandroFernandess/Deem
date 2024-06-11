import streamlit as st
import pandas as pd


# Função para carregar os dados do cache
def carregar_dados():
    if "dados_formulario" in st.session_state:
        return pd.DataFrame(st.session_state["dados_formulario"])
    else:
        return pd.DataFrame()


# Função principal para exibir a tabela
def tabela():
    st.markdown(
        "<h2 style='text-align: center;'>Visão Geral 📊</h2>", unsafe_allow_html=True
    )

    dados = carregar_dados()

    if not dados.empty:
        st.dataframe(dados)
    else:
        st.info("Nenhum dado foi inserido até agora.")
