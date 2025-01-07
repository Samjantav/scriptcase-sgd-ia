import os
import streamlit as st
import PyPDF2
import docx
import pandas as pd
import xml.etree.ElementTree as ET
import mysql.connector
import google.generativeai as genai
import io
import asyncio
from functools import lru_cache

# Configuração da API do Gemini
GEMINI_API_KEY = "AIzaSyCaqOCdgJ8F0Y-LTMiFS8mAzQUHpSeeQkY"
genai.configure(api_key=GEMINI_API_KEY)

# Caminho da pasta com os documentos
folder_path = r"C:\Users\samuel.januario\Desktop\Documentação"

# Funções para extrair texto de diferentes tipos de arquivo
@lru_cache(maxsize=128)
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        return " ".join(page.extract_text() for page in pdf_reader.pages)

@lru_cache(maxsize=128)
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

@lru_cache(maxsize=128)
def extract_text_from_excel(file_path):
    return pd.read_excel(file_path).to_string()

@lru_cache(maxsize=128)
def extract_text_from_csv(file_path):
    return pd.read_csv(file_path).to_string()

@lru_cache(maxsize=128)
def extract_text_from_xml(file_path):
    tree = ET.parse(file_path)
    return ET.tostring(tree.getroot(), encoding='unicode', method='text')

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

# Função assíncrona para carregar todos os arquivos de uma pasta
async def load_all_files_async(folder_path):
    context = []
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
             if os.path.isfile(os.path.join(folder_path, f))]
    
    for file_path in files:
        ext = os.path.splitext(file_path)[1].lower()
        result = await extract_text_from_file(file_path, ext)  # Aguarda o resultado
        if result:
            context.append(result)
    
    return "\n\n".join(context)

# Função síncrona para carregar todos os arquivos
def load_all_files(folder_path):
    return asyncio.run(load_all_files_async(folder_path))

# Função para conectar ao banco de dados MySQL
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="172.16.9.17",
            port=3306,
            user="dolpenge",
            password="Dolp2024",
            database="DEV",
            connect_timeout=10,
            allow_local_infile=True
        )
        return connection
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            st.error("Access denied: Check username and password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            st.error("Database 'DEV' does not exist")
        elif err.errno == 2003:
            st.error("Can't connect to database server. Check if server is running and host/port are correct")
        else:
            st.error(f"Database connection error: {err}")
        return None

# Função para obter o esquema do banco de dados
def get_database_schema(connection):
    schema = {}
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")
        schema[table_name] = [col[0] for col in cursor.fetchall()]

    cursor.close()
    return schema

# Função para perguntar ao Gemini
def ask_gemini(question, context=None, image=None):
    model = genai.GenerativeModel('gemini-2.0')
    prompt = question
    if context:
        prompt = f"Context: {context}\nQuestion: {question}"
    
    response = model.generate_content([prompt, image] if image else prompt)
    return response.text

# Interface do Streamlit
st.title("💬 Chatbot de Ajuda com ScriptCase")
st.write("Este chatbot ajuda você a desenvolver aplicações web usando o ScriptCase.")

# Carregar a documentação na primeira execução
if "context" not in st.session_state:
    st.session_state.context = load_all_files(folder_path)
    st.success("Documentação carregada!")

# Conectar ao banco de dados
if st.sidebar.button("Conectar ao Banco de Dados"):
    connection = connect_to_mysql()
    if connection:
        st.session_state.connection = connection
        st.session_state.schema = get_database_schema(connection)
        st.sidebar.success("Conectado ao banco de dados!")
    else:
        st.sidebar.error("Falha na conexão.")

# Exibir o esquema do banco de dados
if "schema" in st.session_state:
    st.write("### Esquema do Banco de Dados")
    for table, columns in st.session_state.schema.items():
        st.write(f"**{table}**")
        st.write(f"Colunas: {', '.join(columns)}")

# Upload de imagem (opcional)
uploaded_image = st.file_uploader("Carregue uma imagem (opcional)", type=["png", "jpg", "jpeg"])

# Inicializar mensagens do chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar você com o ScriptCase hoje?"}]

# Exibir mensagens do chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Interação com o usuário
if prompt := st.chat_input("Digite sua pergunta sobre o ScriptCase, PHP ou banco de dados:"):
    if "context" not in st.session_state:
        st.warning("Aguarde o carregamento da documentação.")
        st.stop()
    if "connection" not in st.session_state:
        st.warning("Conecte-se ao banco de dados primeiro.")
        st.stop()

    # Adicionar contexto do esquema do banco de dados
    schema_context = "Database Schema:\n" + "\n".join(
        f"Table: {table}, Columns: {', '.join(columns)}" 
        for table, columns in st.session_state.schema.items()
    )
    
    # Combinar contexto da documentação e do banco de dados
    combined_context = f"{st.session_state.context}\n\n{schema_context}"
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Processar imagem (se fornecida)
    image = uploaded_image.read() if uploaded_image else None
    response = ask_gemini(prompt, combined_context, image)
    
    # Adicionar resposta ao chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)