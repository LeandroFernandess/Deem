# Importando as bibliotecas necessárias:

import streamlit as st
from forms.formulario import form
from table.tabela import tabela
from streamlit_navigation_bar import st_navbar

#                                                                       ------------------------------------------------------------------------------
#                                                                       |                           Criando a barra lateral:                         |
#                                                                       ------------------------------------------------------------------------------


opção_selecionada = st_navbar(["Formulário de Deem 📝", "Visão Geral 📊"])

# Exibindo o conteúdo dependendo da opção selecionada:

if opção_selecionada == "Formulário de Deem 📝":
    form()
if opção_selecionada == "Visão Geral 📊":
    tabela()
