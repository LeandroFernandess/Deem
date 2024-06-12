import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd

# Credenciais do Firebase
cred = credentials.Certificate('Streamlit\data\credentials.json') 

# Inicializar o Firebase (verificar se já não foi inicializado)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Objeto do Firestore
db = firestore.client()

def buscar_dados_firestore(nome_colecao):
    """
    Busca dados de uma coleção no Firestore e retorna um DataFrame.

    Args:
        nome_colecao: O nome da coleção no Firestore.

    Returns:
        Um DataFrame com os dados da coleção, ou None em caso de erro.
    """

    try:
        docs = db.collection(nome_colecao).stream()
        data = [doc.to_dict() for doc in docs]
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Erro ao buscar dados do Firestore: {e}")
        return None