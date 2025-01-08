import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    connection = mysql.connector.connect(
        host="172.16.9.17",
        port=3307,
        user="dolpenge",
        password="Dolp2024",
        database="DEV",
        connect_timeout=30,
        allow_local_infile=True
    )
    logging.debug("Conexão com o banco de dados estabelecida com sucesso.")

    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")
        columns = [col[0] for col in cursor.fetchall()]
        schema[table_name] = columns
    print(schema)
    cursor.close()
except mysql.connector.Error as err:
    logging.error(f"Erro: {err}")
finally:
    if connection.is_connected():
        connection.close()
        logging.debug("Conexão encerrada.")
        logging.debug(f"Tables fetched: {tables}")
        logging.debug(f"Columns for {table_name}: {columns}")