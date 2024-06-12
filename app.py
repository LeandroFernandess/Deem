# Importando as bibliotecas necessárias:

import streamlit as st
from forms.formulario import form
from table.tabela import visualizar_dados


opção_selecionada = st.sidebar.radio(label='Opções', options=["Formulário de Deem 📝", "Visão Geral 📊"])

# Exibindo o conteúdo dependendo da opção selecionada:

if opção_selecionada == "Formulário de Deem 📝":
    form()
if opção_selecionada == "Visão Geral 📊":
    visualizar_dados()
