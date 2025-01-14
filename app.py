import os
import streamlit as st
import PyPDF2
import docx
import pandas as pd
import xml.etree.ElementTree as ET
import json
import google.generativeai as genai
import asyncio
import logging
import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from datetime import datetime
import hashlib

# Configurar a API do Gemini
GEMINI_API_KEY = "" #INSERIR CHAVE KEY 
genai.configure(api_key=GEMINI_API_KEY)

# Configurar o logger
logging.basicConfig(level=logging.DEBUG)

# Caminho para a pasta com documentos
folder_path = r"" #INSIRA O CAMINHO 

# Funções para extrair texto de diferentes tipos de arquivos
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return " ".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        logging.error(f"Erro ao extrair texto do PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def extract_text_from_excel(file_path):
    return pd.read_excel(file_path).to_string()

def extract_text_from_csv(file_path):
    return pd.read_csv(file_path).to_string()

def extract_text_from_xml(file_path):
    tree = ET.parse(file_path)
    return ET.tostring(tree.getroot(), encoding='unicode', method='text')

def extract_text_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return json.dumps(data, indent=4)
    except Exception as e:
        logging.error(f"Erro ao extrair texto do JSON {file_path}: {e}")
        return ""

# Função assíncrona para extrair texto de um arquivo
async def extract_text_from_file(file_path, ext):
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.xlsx':
        return extract_text_from_excel(file_path)
    elif ext == '.csv':
        return extract_text_from_csv(file_path)
    elif ext == '.xml':
        return extract_text_from_xml(file_path)
    elif ext == '.json':
        return extract_text_from_json(file_path)
    else:
        logging.warning(f"Extensão de arquivo não suportada: {ext}")
        return None

# Função assíncrona para carregar todos os arquivos de uma pasta
async def load_all_files_async(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]
    tasks = [extract_text_from_file(file_path, os.path.splitext(file_path)[1].lower()) for file_path in files]
    results = await asyncio.gather(*tasks)
    return "\n\n".join(filter(None, results))

# Função síncrona para carregar todos os arquivos
def load_all_files(folder_path):
    return asyncio.run(load_all_files_async(folder_path))

# Função para gerar hash da senha (usando MD5)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Função para conectar ao banco de dados
@st.cache_resource
def connect_to_db():
    try:
        connection_pool = MySQLConnectionPool(
            host='',
            port= '',
            database='',
            user='',
            password='',
            connection_timeout=,
            pool_name="mypool",
            pool_size=5
        )
        logging.debug("Conexão com o banco de dados estabelecida com sucesso.")
        return connection_pool
    except Error as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
    return None

# Função para validar usuário
def validate_user(username, password):
    logging.debug("Tentando validar usuário...")
    connection_pool = connect_to_db()
    if connection_pool:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT a.login, a.senha
                FROM usuarios AS a
                JOIN usuarios_groups AS b ON b.login = a.login
                WHERE b.group_id = 10 AND a.login = %s AND a.senha = %s
                """
                hashed_password = hash_password(password)  # Gerar hash da senha
                cursor.execute(query, (username, hashed_password))
                user = cursor.fetchone()
                logging.debug(f"Usuário encontrado: {user}")
                return user
            except Error as e:
                logging.error(f"Erro ao validar usuário: {e}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
        else:
            logging.error("Conexão ao banco de dados falhou ou está inativa.")
    else:
        logging.error("Conexão ao banco de dados falhou ou está inativa.")
    return None

# Função para salvar conversa no banco de dados
def save_conversation_to_db(username, conversation_id, conversation_data):
    connection_pool = connect_to_db()
    if connection_pool:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            try:
                cursor = connection.cursor()
                # Check if conversation_id exists
                query_check = """
                SELECT COUNT(*) AS count FROM tb_messages_bot
                WHERE usuario = %s AND conversation_id = %s
                """
                cursor.execute(query_check, (username, conversation_id))
                count = cursor.fetchone()[0]
                if count > 0:
                    # Update existing conversation
                    query = """
                    UPDATE tb_messages_bot
                    SET data = %s, mensagem = %s
                    WHERE usuario = %s AND conversation_id = %s
                    """
                else:
                    # Insert new conversation
                    query = """
                    INSERT INTO tb_messages_bot (usuario, conversation_id, data, mensagem)
                    VALUES (%s, %s, %s, %s)
                    """
                # Prepare data
                data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                json_data = json.dumps(conversation_data)
                cursor.execute(query, (username, conversation_id, data, json_data))
                connection.commit()
                logging.debug("Conversa salva com sucesso no banco de dados.")
            except Error as e:
                logging.error(f"Erro ao salvar conversa no banco de dados: {e}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
        else:
            logging.error("Conexão ao banco de dados falhou ou está inativa em save_conversation_to_db.")
    else:
        logging.error("Conexão ao banco de dados falhou ou está inativa em save_conversation_to_db.")

# Função para recuperar conversas do usuário do banco de dados
def get_conversations(username):
    connection_pool = connect_to_db()
    if connection_pool:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT conversation_id, mensagem
                FROM tb_messages_bot
                WHERE usuario = %s
                ORDER BY data ASC
                """
                cursor.execute(query, (username,))
                conversations = cursor.fetchall()
                # Create a dictionary with conversation_id as key and conversation_data as value
                conv_dict = {}
                for conv in conversations:
                    conv_id = conv['conversation_id']
                    try:
                        conv_data = json.loads(conv['mensagem'])
                    except json.JSONDecodeError:
                        conv_data = []
                    conv_dict[conv_id] = conv_data
                return conv_dict
            except Error as e:
                logging.error(f"Erro ao recuperar conversas do banco de dados: {e}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
        else:
            logging.error("Conexão ao banco de dados falhou ou está inativa em get_conversations.")
    else:
        logging.error("Conexão ao banco de dados falhou ou está inativa em get_conversations.")
    return {}

# Função para perguntar ao Gemini
def ask_gemini(question, context=None, image=None):
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    prompt = f"Contexto: {context}\nPergunta: {question}" if context else question
    response = model.generate_content([prompt, image] if image else prompt)
    return response.text

# Interface de login
st.sidebar.title("🔑 Login")
if "user" not in st.session_state:
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        user = validate_user(username, password)
        if user:
            st.session_state.user = user['login']
            st.sidebar.success(f"Bem-vindo, {user['login']}!")
            
            # Recuperar conversas do banco de dados
            user_conversations = get_conversations(st.session_state.user)
            if user_conversations:
                st.session_state.chat_history = user_conversations
                st.session_state.chat_id = max(user_conversations.keys(), default=1)
                st.session_state.messages = st.session_state.chat_history.get(st.session_state.chat_id, [{"role": "assistant", "content": "Ce tá bão só, no que posso te ajudar?"}])
            else:
                st.session_state.chat_history = {}
                st.session_state.chat_id = 1
                st.session_state.messages = [{"role": "assistant", "content": "Ce tá bão só, no que posso te ajudar?"}]
        else:
            st.sidebar.error("Usuário ou senha inválidos. Tente novamente.")
else:
    # Inicializar chaves no session_state se não existirem
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = 1
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ce tá bão só, no que posso te ajudar?"}]
    
    # Mostrar interface principal do chatbot
    st.title("𓂀 💻 ScriptCase AI ")
    st.write("Converse com a IA sobre ScriptCase, PHP, ou bancos de dados.")
    
    # Barra lateral para histórico de conversas
    st.sidebar.title("⏳ Histórico de Conversas")
    
    # Botão para iniciar novo chat
    if st.sidebar.button("▶️ Nova Conversa"):
        new_chat_id = max(st.session_state.chat_history.keys(), default=0) + 1
        st.session_state.chat_id = new_chat_id
        st.session_state.chat_history[new_chat_id] = [{"role": "assistant", "content": "Ce tá bão só, no que posso te ajudar?"}]
        st.session_state.messages = st.session_state.chat_history[st.session_state.chat_id]
    
    # Exibir histórico de conversas
    for chat_id in st.session_state.chat_history:
        if st.sidebar.button(f"Conversa {chat_id}"):
            st.session_state.chat_id = chat_id
            st.session_state.messages = st.session_state.chat_history[st.session_state.chat_id]
    
    # Exibir mensagens do chat
    if "messages" in st.session_state and isinstance(st.session_state.messages, list):
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
    else:
        st.error("Formato de mensagens inválido ou variável não inicializada.")
    
    # Interação com o usuário
    if prompt := st.chat_input("Faça sua pergunta sobre ScriptCase, PHP ou bancos de dados:"):
        if "context" not in st.session_state:
            st.session_state.context = load_all_files(folder_path)
        
        # Adicionar pergunta do usuário ao chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Gerar resposta
        response = ask_gemini(prompt, st.session_state.context)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
        
        # Salvar conversa no banco de dados
        save_conversation_to_db(st.session_state.user, st.session_state.chat_id, st.session_state.messages)

# Se o usuário não estiver logado, exibir mensagem de login obrigatório
if "user" not in st.session_state:
    st.write("Por favor, faça login para acessar o chatbot.")
