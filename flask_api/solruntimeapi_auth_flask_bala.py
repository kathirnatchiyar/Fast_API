from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL Configuration
mysql_host = '127.0.0.1'
mysql_user = 'root'
mysql_password = 'redhat'
mysql_database = 'runtimedb'

# API Key
valid_api_key = '4Ie9HGmIQvsgrMyaUdW16lbOI5w09I2tR0ehrSIcHHFvCgJypLsxLJrRO70KO8xg'

# Database Connection
db_connection = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)


# API Key Authentication Middleware
def authenticate_api_key(api_key):
    return api_key == valid_api_key


# Validate if name exists in the database
def check_name_exists(name):
    cursor = db_connection.cursor()
    query = "SELECT id FROM customer WHERE name = %s"
    cursor.execute(query, (name))
    result = cursor.fetchone()
    cursor.close()
    return result is not None


# REST API Route
@app.route('/insert_data', methods=['POST'])
def insert_data():
    # Authentication
    api_key = request.headers.get('API-Key')
    if not authenticate_api_key(api_key):
        return jsonify({"message": "Invalid authentication"}), 401

    # JSON Data from Request
    data = request.json
    name = data.get('name')
    age = data.get('age')

    if not name:
        return jsonify({"message": "Name field is required"}), 400

    if check_name_exists(name):
        return jsonify({"message": "Name already exists"}), 400

    # Insert data into MySQL
    cursor = db_connection.cursor()
    query = "INSERT INTO customer (name, age) VALUES (%s, %s)"
    cursor.execute(query, (name, age))
    db_connection.commit()
    cursor.close()

    return jsonify({"message": "Data inserted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
