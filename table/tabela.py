import streamlit as st
from data.firebase import buscar_dados_firestore  # Importe a função

# ... (Restante do seu código)

def visualizar_dados():
    """
    Página do Streamlit para visualizar os dados do Firestore.
    """

    st.title("Dados do Firebase")

    # Buscar dados do Firestore
    df = buscar_dados_firestore("deems")  # 'deems' é o nome da sua coleção

    if df is not None:
        st.table(df)  
    else:
        st.error("Erro ao carregar dados do Firebase.")
