from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Database connection parameters
config = {
    'user': '',
    'password': '',
    'host': '',
    'port': ,
    'database': ''
}

# Establish a connection to the database
def get_db_connection():
    return mysql.connector.connect(**config)

@app.route('/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM your_table_name")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route('/data', methods=['POST'])
def add_data():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO your_table_name (column1, column2) VALUES (%s, %s)"
    values = (data['column1'], data['column2'])
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Data added successfully'}), 201

# Add PUT and DELETE methods similarly

if __name__ == '__main__':
    app.run(debug=True)
