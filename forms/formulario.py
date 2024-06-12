import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import datetime 
from data.codigos import dicionario_dados as dados_base
from data.funcionarios import dicionario_funcionarios as funcionarios_base

# Credenciais do seu projeto Firebase
cred = credentials.Certificate('Streamlit\data\credentials.json') 

# Objeto do Firestore
db = firestore.client()
# Objeto do Storage
bucket = storage.bucket()

# Inicializar o Firebase (se ainda não estiver)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'projeto-deem.appspot.com' # Substitua pelo nome do seu bucket
    })


# Função para obter os dados dos códigos com cache
@st.cache_data
def carregar_dados():
    return dados_base()


# Função para obter os dados dos funcionários com cache
@st.cache_data
def carregar_funcionarios():
    return funcionarios_base()


# Função para obter o nome do funcionário
def pegar_nome_funcionario(matricula, dados):
    return dados.get(matricula, {}).get("Nome")


# Inicializando o estado da aplicação
def init_session_state():
    if "nome" not in st.session_state:
        st.session_state["nome"] = ""
    if "matricula_valida" not in st.session_state:
        st.session_state["matricula_valida"] = True
    if "codigo_erro" not in st.session_state:
        st.session_state["codigo_erro"] = ""
    if "dados_formulario" not in st.session_state:
        st.session_state["dados_formulario"] = []


# Função para verificar a matrícula
def verificar_matricula():
    funcionario = carregar_funcionarios()
    input_matricula = st.session_state["input_matricula"]
    if input_matricula and not input_matricula.isdigit():
        st.session_state["matricula_valida"] = False
        st.session_state["nome"] = ""
        st.session_state["input_matricula"] = ""
    else:
        nome = pegar_nome_funcionario(input_matricula, funcionario)
        if nome:
            st.session_state["nome"] = nome
            st.session_state["matricula_valida"] = True
        else:
            st.session_state["nome"] = ""
            st.session_state["matricula_valida"] = False
            st.session_state["input_matricula"] = ""


# Função para calcular o valor total
def calcular_valor_total():
    quantidade = st.session_state["input_quantidade"]
    valor_unitario = st.session_state["input_valor_unitário"]
    if quantidade.isdigit() and valor_unitario.replace(".", "", 1).isdigit():
        valor_total = int(quantidade) * float(valor_unitario)
        st.session_state["input_valor_total"] = f"{valor_total:.2f}"


# Função para atualizar os dados com base no código inserido
def atualizar_dados():
    dados = carregar_dados()
    código = st.session_state["input_codigo"]
    if código in dados:
        linha = dados[código]
        st.session_state["input_descrição"] = linha["Texto breve material"]
        st.session_state["input_valor_unitário"] = str(linha["Preço"])
        st.session_state["input_depósito"] = linha["TpM"]
        calcular_valor_total()
        st.session_state["codigo_erro"] = ""
    else:
        st.session_state["codigo_erro"] = (
            "Código não encontrado na base de dados, verifique o código inserido e se o erro persistir procure seu gestor."
        )
        st.session_state["input_codigo"] = ""


# Função para salvar os dados no cache
def salvar_dados():
    try:
        # Upload da imagem para o Storage
        foto = st.session_state["input_foto"] 
        if foto:
            nome_foto = f"fotos/{foto.name}"
            blob = bucket.blob(nome_foto)
            blob.upload_from_string(foto.read(), content_type=foto.type)
            foto_url = blob.public_url
        else:
            foto_url = None

        # Converter a data para timestamp
        data_timestamp = datetime.datetime.combine(
            st.session_state["input_data"], datetime.datetime.min.time()
        )

        # Dados para o Firestore
        dados = {
            "Matrícula": st.session_state["input_matricula"],
            "Código": st.session_state["input_codigo"],
            "Quantidade": st.session_state["input_quantidade"],
            "Relação de Carga": st.session_state["input_rc"],
            "Tipo da DEEM": st.session_state["input_tipo"],
            "Área": st.session_state["input_área"],
            "Comentário": st.session_state["input_comentário"],
            "Data": data_timestamp,
            "Descrição": st.session_state["input_descrição"],
            "Valor Unitário": st.session_state["input_valor_unitário"],
            "Valor Total": st.session_state["input_valor_total"],
            "Depósito": st.session_state["input_depósito"],
            "Foto_URL": foto_url,  
        }

        # Salvar no Firestore
        db.collection('deems').document().set(dados)
        st.success("Dados inseridos com sucesso no Firebase!")

    except Exception as e:
        st.error(f"Erro ao salvar dados no Firebase: {e}")


# Função principal do formulário
def form():
    init_session_state()

    # Título do formulário
    st.markdown(
        "<h2 style='text-align: center;'>Formulário de Deem</h2>",
        unsafe_allow_html=True,
    )

    # Entrada de matrícula fora do formulário para permitir verificação dinâmica
    st.text_input(
        label="Matrícula",
        key="input_matricula",
        on_change=verificar_matricula,
        max_chars=7,
    )

    # Exibindo o campo de nome com base na verificação
    if not st.session_state["matricula_valida"]:
        st.error(
            "A matrícula deve conter apenas números ou não está cadastrada na base de dados, verifique a informação ou procure o seu gestor."
        )

    # Container para o campo de entrada de código e a mensagem de erro
    codigo_container = st.container()
    with codigo_container:
        st.text_input(
            label="Código", key="input_codigo", on_change=atualizar_dados, max_chars=10
        )
        if st.session_state["codigo_erro"]:
            st.error(st.session_state["codigo_erro"])

    # Campos do formulário
    st.text_input(
        label="Quantidade",
        key="input_quantidade",
        on_change=calcular_valor_total,
        max_chars=4,
    )
    st.text_input(
        label="Relação de Carga",
        key="input_rc",
        max_chars=6,
        placeholder="Exemplo: 123456",
    )
    st.selectbox(label="Tipo da DEEM", options=["Maior", "Menor"], key="input_tipo")
    st.selectbox(label="Área", options=["CLP 1", "CLP 2"], key="input_área")
    st.file_uploader(label="Imagem", key="input_foto")
    st.text_area(
        label="Comentário",
        key="input_comentário",
        placeholder="Este campo não é obrigatório, preencha-o caso haja informações adicionais.",
        max_chars=9999,
    )
    st.date_input(label="Data", format="DD/MM/YYYY", key="input_data")
    st.text_input(label="Descrição", key="input_descrição", disabled=True)
    st.text_input(label="Valor Unitário", key="input_valor_unitário", disabled=True)
    st.text_input(label="Valor Total", key="input_valor_total", disabled=True)
    st.text_input(label="Depósito", key="input_depósito", disabled=True)
    input_botão = st.button("Confirmar Deem")

    # Evento para quando o usuário confirmar a inserção dos dados
    if input_botão:
        if (
            not st.session_state["input_codigo"]
            or not st.session_state["input_quantidade"]
            or not st.session_state["input_rc"]
            or not st.session_state["input_matricula"]
        ):
            st.error(
                "Preencha todos os campos obrigatórios: Matrícula, Código, Quantidade e Relação de Carga"
            )
        else:
            salvar_dados()
            st.success(
                "Divergência inserida com sucesso! Você pode verificar a informação pelo menu de navegação na guia 'Visão Geral 📊'"
            )
            st.session_state["codigo_erro"] = ""
