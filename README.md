# scriptcase-sgd-ia
IA para auxiliar criação de aplicação na feramenta do scriptcase
Passo 1: Instalar o Python
Se você ainda não tem o Python instalado, siga estas etapas:

Baixe o Python:

Acesse o site oficial: python.org.

Baixe a versão mais recente do Python (3.8 ou superior).

Instale o Python:

Execute o instalador.

Marque a opção "Add Python to PATH" durante a instalação.

Conclua a instalação.

Verifique a instalação:

Abra o terminal (ou Prompt de Comando no Windows).

Execute o comando:

bash
Copy
python --version
Isso deve retornar a versão do Python instalada (por exemplo, Python 3.11.5).

Passo 2: Criar um Ambiente Virtual (Opcional, mas Recomendado)
Um ambiente virtual isola as dependências do projeto. Para criar um:

Instale o virtualenv:

No terminal, execute:

bash
Copy
pip install virtualenv
Crie o ambiente virtual:

Navegue até a pasta do seu projeto.

Execute:

bash
Copy
virtualenv venv
Ative o ambiente virtual:

No Windows:

bash
Copy
venv\Scripts\activate
No macOS/Linux:

bash
Copy
source venv/bin/activate
Após ativar, o nome do ambiente virtual (venv) aparecerá no início do prompt do terminal.

Passo 3: Instalar as Bibliotecas Necessárias
Agora, instale as bibliotecas usadas no projeto. Execute os comandos abaixo no terminal (com o ambiente virtual ativado, se aplicável):

Bibliotecas principais:

bash
Copy
pip install streamlit google-generativeai mysql-connector-python python-docx pandas openpyxl PyPDF2
Essas bibliotecas incluem:

streamlit: Para a interface do usuário.

google-generativeai: Para interagir com a API do Gemini.

mysql-connector-python: Para conectar ao MariaDB.

python-docx: Para ler arquivos Word.

pandas e openpyxl: Para ler arquivos Excel e CSV.

PyPDF2: Para ler arquivos PDF.

Bibliotecas para integração com o Google Drive:

bash
Copy
pip install google-auth google-auth-httplib2 google-auth-oauthlib google-api-python-client
Essas bibliotecas permitem acessar arquivos no Google Drive usando a API do Google.

Verifique as instalações:

Para confirmar que tudo foi instalado corretamente, execute:

bash
Copy
pip list
Verifique se todas as bibliotecas listadas acima estão presentes.

Passo 4: Configurar o Google Drive API
Para acessar arquivos no Google Drive, você precisa configurar a API:

Crie um projeto no Google Cloud Console:

Acesse o Google Cloud Console.

Crie um novo projeto ou selecione um existente.

Habilite a API do Google Drive:

No menu lateral, vá para APIs e Serviços > Biblioteca.

Pesquise por "Google Drive API" e habilite-a.

Crie credenciais:

Vá para APIs e Serviços > Credenciais.

Clique em Criar Credenciais e selecione Conta de Serviço.

Siga as etapas para criar a conta de serviço.

Após criar, baixe o arquivo JSON de credenciais.

Compartilhe a pasta do Google Drive:

No Google Drive, compartilhe a pasta que contém os arquivos de documentação com o e-mail da conta de serviço (encontrado no arquivo JSON).

Coloque o arquivo JSON no projeto:

Coloque o arquivo JSON baixado na pasta do seu projeto.

Atualize o caminho no script (SERVICE_ACCOUNT_FILE).

Passo 5: Configurar o MariaDB
Se você ainda não tem um banco de dados MariaDB configurado:

Instale o MariaDB:

Baixe e instale o MariaDB a partir do site oficial: mariadb.org.

Siga as instruções de instalação para o seu sistema operacional.

Crie um banco de dados e tabelas:

Use uma ferramenta como phpMyAdmin, HeidiSQL ou o terminal para criar um banco de dados e tabelas.

Exemplo de comando SQL:

sql
Copy
CREATE DATABASE testdb;
USE testdb;
CREATE TABLE usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(100), email VARCHAR(100));
Anote as credenciais:

Você precisará do host, usuário, senha e nome do banco de dados para configurar no script.

Passo 6: Configurar a API do Gemini
Obtenha uma chave de API do Gemini:

Acesse o site do Google AI: Google AI Studio.

Crie uma conta e gere uma chave de API.

Atualize o script:

Substitua SUA_CHAVE_DA_API_AQUI no script pela sua chave de API.

Passo 7: Executar o Script
 chatbot_scriptcase.py.

Execute o script:

No terminal, navegue até a pasta do projeto e execute:

bash
Copy
streamlit run chatbot_scriptcase.py
Acesse a interface:

O Streamlit abrirá automaticamente uma aba no navegador com a interface do chatbot.

Resumo das Bibliotecas Instaladas
Biblioteca	Descrição
streamlit	Interface do usuário para o chatbot.
google-generativeai	Integração com a API do Gemini.
mysql-connector-python	Conexão com o banco de dados MariaDB.
python-docx	Leitura de arquivos Word (.docx).
pandas e openpyxl	Leitura de arquivos Excel (.xlsx) e CSV.
PyPDF2	Leitura de arquivos PDF.
google-auth	Autenticação com a API do Google Drive.
google-api-python-client	Interação com a API do Google Drive.
Próximos Passos
Teste o chatbot:

Carregue documentos, conecte-se ao banco de dados e faça perguntas.

Personalize o script:

Adicione mais funcionalidades ou integre outras ferramentas.

Implante o chatbot:

Use serviços como Streamlit Sharing, Heroku ou AWS para disponibilizar o chatbot online.

Com esses passos, você terá um ambiente totalmente configurado para rodar o chatbot integrado com ScriptCase, Google Drive, MariaDB e Gemini API! 🚀

![image](https://github.com/user-attachments/assets/a3303f24-fbba-4db5-a39a-0b6da9f1c25e)

![image](https://github.com/user-attachments/assets/a0fca711-7078-470f-b5cb-f448c815f617)


