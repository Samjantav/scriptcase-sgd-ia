import os
import streamlit as st
import PyPDF2
import docx
import pandas as pd
import xml.etree.ElementTree as ET
import google.generativeai as genai
import io
import asyncio
import logging

# Configure the Gemini API
GEMINI_API_KEY = "AIzaSyCaqOCdgJ8F0Y-LTMiFS8mAzQUHpSeeQkY"
genai.configure(api_key=GEMINI_API_KEY)

# Configure the logger
logging.basicConfig(level=logging.DEBUG)

# Path to the folder with documents
folder_path = r"C:\Users\samuel.januario\Desktop\Documentação"

# Functions to extract text from different file types
def extract_text_from_pdf(file_path):
    logging.debug(f"Extracting text from PDF: {file_path}")
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = " ".join(page.extract_text() for page in pdf_reader.pages)
            logging.debug(f"Text extracted from PDF: {file_path}")
            return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF {file_path}: {e}")
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

# Async function to extract text from a file
async def extract_text_from_file(file_path, ext):
    logging.debug(f"Extracting text from file: {file_path} with extension: {ext}")
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
    else:
        logging.warning(f"Unsupported file extension: {ext}")
        return None

# Async function to load all files from a folder
async def load_all_files_async(folder_path):
    context = []
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
             if os.path.isfile(os.path.join(folder_path, f))]
    
    tasks = []
    for file_path in files:
        ext = os.path.splitext(file_path)[1].lower()
        tasks.append(extract_text_from_file(file_path, ext))
    
    results = await asyncio.gather(*tasks)
    for result in results:
        if result:
            context.append(result)
    
    logging.debug(f"Loaded context: {context}")
    return "\n\n".join(context)

# Synchronous function to load all files
def load_all_files(folder_path):
    logging.debug(f"Loading all files from folder: {folder_path}")
    return asyncio.run(load_all_files_async(folder_path))

# Function to ask Gemini
def ask_gemini(question, context=None, image=None):
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    prompt = question
    if context:
        prompt = f"Context: {context}\nQuestion: {question}"
    
    response = model.generate_content([prompt, image] if image else prompt)
    return response.text

# Streamlit interface
st.title("💬 ScriptCase AI")
st.write("Vamos Hackear a Nasa.")

# Load documentation on the first run
if "context" not in st.session_state:
    logging.debug("Loading documentation on first run.")
    st.session_state.context = load_all_files(folder_path)
    st.success("Documentation loaded!")

# Upload image (optional)
uploaded_image = st.file_uploader("Insira uma imagem (optional)", type=["png", "jpg", "jpeg"])

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ce ta bão só, no que posso te ajudar?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User interaction
if prompt := st.chat_input("Ask a question about ScriptCase, PHP, or databases:"):
    if "context" not in st.session_state:
        st.warning("Please wait for the documentation to load.")
        st.stop()
    
    # Process image (if provided)
    image = uploaded_image.read() if uploaded_image else None
    response = ask_gemini(prompt, st.session_state.context, image)
    
    # Add response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)