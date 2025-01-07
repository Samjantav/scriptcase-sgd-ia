import streamlit as st
import PyPDF2
import docx
import pandas as pd
import xml.etree.ElementTree as ET
import mysql.connector
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Configuração da API do Gemini
GEMINI_API_KEY = "AIzaSyCaqOCdgJ8F0Y-LTMiFS8mAzQUHpSeeQkY" 
genai.configure(api_key=GEMINI_API_KEY)

# Configuração do Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'caminho/para/seu/arquivo_de_credenciais.json'  # Substitua pelo caminho do seu arquivo JSON

# Função para autenticar no Google Drive
def authenticate_google_drive():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

# Função para listar arquivos no Google Drive
def list_files(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        pageSize=10, fields="files(id, name)").execute()
    return results.get('files', [])

# Função para baixar um arquivo do Google Drive
def download_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file.seek(0)
    return file

# Função para extrair texto de PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Função para extrair texto de Word (docx)
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Função para extrair texto de Excel (xlsx)
def extract_text_from_excel(file):
    df = pd.read_excel(file)
    return df.to_string()

# Função para extrair texto de CSV
def extract_text_from_csv(file):
    df = pd.read_csv(file)
    return df.to_string()

# Função para extrair texto de XML
def extract_text_from_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    text = ET.tostring(root, encoding='unicode', method='text')
    return text

# Função para conectar ao MariaDB
def connect_to_mariadb(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para obter o esquema do banco de dados
def get_database_schema(connection):
    schema = {}
    cursor = connection.cursor()

    # Obter tabelas
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        schema[table_name] = [col[0] for col in columns]  # Nomes das colunas

    cursor.close()
    return schema

# Função para enviar uma solicitação à API do Gemini
def ask_gemini(question, context=None, image=None):
    model = genai.GenerativeModel('gemini-1.5-pro')  # Use o modelo desejado
    if context:
        if image:
            # Enviar texto e imagem
            response = model.generate_content([f"Contexto: {context}\nPergunta: {question}", image])
        else:
            # Enviar apenas texto
            response = model.generate_content(f"Contexto: {context}\nPergunta: {question}")
    else:
        if image:
            # Enviar apenas imagem
            response = model.generate_content([question, image])
        else:
            # Enviar apenas a pergunta
            response = model.generate_content(question)
    return response.text

# Interface do Streamlit
st.title("💬 Chatbot de Ajuda com ScriptCase")
st.write("Este chatbot ajuda você a desenvolver aplicações web usando o ScriptCase, integrando documentação, banco de dados e análise de imagens.")

# Autenticação no Google Drive
drive_service = authenticate_google_drive()

# Listar arquivos no Google Drive
folder_id = "ID_DA_PASTA_NO_GOOGLE_DRIVE"  # Substitua pelo ID da pasta no Google Drive
files = list_files(drive_service, folder_id)

if files:
    st.write("Documentos disponíveis no Google Drive:")
    for file in files:
        st.write(f"- {file['name']}")

    # Selecionar um arquivo para carregar
    selected_file_name = st.selectbox("Selecione um arquivo para carregar:", [file['name'] for file in files])
    selected_file_id = next(file['id'] for file in files if file['name'] == selected_file_name)

    if st.button("Carregar Documentação"):
        file = download_file(drive_service, selected_file_id)
        file_extension = selected_file_name.split(".")[-1].lower()

        if file_extension == "pdf":
            context = extract_text_from_pdf(file)
        elif file_extension == "docx":
            context = extract_text_from_docx(file)
        elif file_extension == "xlsx":
            context = extract_text_from_excel(file)
        elif file_extension == "csv":
            context = extract_text_from_csv(file)
        elif file_extension == "xml":
            context = extract_text_from_xml(file)
        else:
            st.error("Formato de arquivo não suportado.")
            st.stop()

        st.session_state.context = context
        st.success("Documentação carregada com sucesso!")
else:
    st.warning("Nenhum arquivo encontrado no Google Drive.")

# Conexão com o MariaDB
st.sidebar.header("Conexão com o Banco de Dados")
host = st.sidebar.text_input("Host", value="localhost")
user = st.sidebar.text_input("Usuário", value="root")
password = st.sidebar.text_input("Senha", type="password")
database = st.sidebar.text_input("Banco de Dados", value="testdb")

if st.sidebar.button("Conectar ao Banco de Dados"):
    connection = connect_to_mariadb(host, user, password, database)
    if connection:
        st.session_state.connection = connection
        st.session_state.schema = get_database_schema(connection)
        st.sidebar.success("Conectado ao banco de dados com sucesso!")
    else:
        st.sidebar.error("Falha ao conectar ao banco de dados.")

# Exibir esquema do banco de dados
if "schema" in st.session_state:
    st.write("### Esquema do Banco de Dados")
    for table, columns in st.session_state.schema.items():
        st.write(f"**Tabela: {table}**")
        st.write(f"Colunas: {', '.join(columns)}")

# Upload de imagem (opcional)
uploaded_image = st.file_uploader("Carregue uma imagem (opcional)", type=["png", "jpg", "jpeg"])

# Inicializar o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar você com o ScriptCase hoje?"}]

# Exibir mensagens anteriores
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Digite sua pergunta sobre o ScriptCase, PHP ou banco de dados:"):
    if "context" not in st.session_state:
        st.warning("Por favor, carregue a documentação antes de fazer perguntas.")
        st.stop()
    if "connection" not in st.session_state:
        st.warning("Por favor, conecte-se ao banco de dados antes de fazer perguntas.")
        st.stop()

    # Gerar contexto com base no esquema do banco de dados
    schema_context = "Esquema do banco de dados:\n"
    for table, columns in st.session_state.schema.items():
        schema_context += f"Tabela: {table}, Colunas: {', '.join(columns)}\n"

    # Combinar o contexto da documentação e do banco de dados
    combined_context = f"{st.session_state.context}\n\n{schema_context}"

    # Adicionar a pergunta do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Preparar a imagem, se houver
    image = None
    if uploaded_image:
        image = uploaded_image.read()

    # Enviar a pergunta, o contexto e a imagem (se houver) para a API do Gemini
    response = ask_gemini(prompt, combined_context, image)

    # Adicionar a resposta ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)