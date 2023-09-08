import mysql.connector
import logging
import threading
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(
    filename=r"C:\Users\balakumaran_m\Downloads\Angular_python\api.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Instead of directly using the logger from the logging module,
# use the fully qualified class name when defining the logger
logger = logging.getLogger("logging.Logger")
# API Key
VALID_API_KEY = 'abcdefghijkl250899'
SCRIPT_PATH = r"C:\Users\balakumaran_m\Downloads\Angular_python\script.bat"

# MySQL Configuration
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'redhat'
mysql_database = 'test'
ss_disable = True

# Database Connection
db_connection = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database,
    ssl_disabled=ss_disable  # Explicitly disable SSL/TLS
)

# API Key Authentication
def authenticate_api_key(api_key):
    return api_key == VALID_API_KEY

script_statuses = {}


def process_data(data, cursor):
    owner_id = data["ownerid"]
    cursor.execute("SELECT * FROM dbautobala WHERE ownerid = %s", (owner_id,))
    existing_row = cursor.fetchone()

    if existing_row:
        all_same = True
        print("the customer already exist")

        for i, key in enumerate(data):
            if key != "ownerid" and existing_row[i] != data[key]:
                all_same = False
                break

        if all_same:
            print(f"Customer with owner ID {owner_id} already exists with all requested services.")
        else:
            update_query = """
                UPDATE dbautobala
                SET customername = %s, sessionUser = %s, lob = %s,
                    transdb = %s, uiux = %s, wf = %s, rating = %s, reportingdb = %s
                WHERE ownerid = %s
            """

            cursor.execute(update_query, (
                data["customername"], data["sessionUser"],
                data["lob"], data["transdb"], data["uiux"], data["wf"],
                data["rating"], data["reportingdb"], owner_id
            ))

            print("Updated row with changes.")

    else:
        insert_query = """
               INSERT INTO dbautobala
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
           """
        cursor.execute(insert_query, (
            owner_id, data["customername"], data["sessionUser"],
            data["lob"], data["transdb"], data["uiux"],
            data["wf"], data["rating"], data["reportingdb"],
        ))
        print("Inserted new row.")


def execute_script_async(ownerid, customername):
    script_args = [SCRIPT_PATH, ownerid, customername]
    try:
        subprocess.run(script_args, check=True)
        script_statuses[ownerid] = "Completed"
        logger.info(f"Script execution completed for ownerid: {ownerid}")
    except subprocess.CalledProcessError as e:
        script_statuses[ownerid] = f"Error: {e}"
        logger.error(f"Script execution failed for ownerid: {ownerid} - Error: {e}")
    except Exception as e:
        script_statuses[ownerid] = f"Error: {e}"
        logger.error(f"An error occurred during script execution for ownerid: {ownerid} - Error: {e}")
# API Route for Inserting Data
@app.route('/insert_data', methods=['POST'])
def insert_data_route():
    api_key = request.headers.get('api_key')
    data = request.json

    if not authenticate_api_key(api_key):
        return jsonify({"status": "error", "message": "Invalid authentication"}), 401

    ownerid = data.get('ownerid')
    if not ownerid:
        return jsonify({"status": "error", "message": "ownerid field is required"}), 400

    cursor = db_connection.cursor()
    try:
        cursor.execute("SELECT * FROM dbautobala WHERE ownerid = %s", (ownerid,))
        existing_row = cursor.fetchone()

        if existing_row:
            column_names = cursor.column_names  # Get the column names from the cursor
            existing_data = dict(zip(column_names, existing_row))

            all_same = True
            for key in data:
                if key != "ownerid" and existing_data[key] != data[key]:
                    all_same = False
                    break

            if all_same:
                response_data = {
                    "status": "Error",
                    "message": f"Customer with owner ID {ownerid} already exists with all requested services."
                }
                return response_data

        insert_query = """
           INSERT INTO dbautobala
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
           """
        cursor.execute(insert_query, (
            ownerid, data["customername"], data["sessionUser"],
            data["lob"], data["transdb"], data["uiux"],
            data["wf"], data["rating"], data["reportingdb"],
        ))
        db_connection.commit()
        logger.info(f"Data inserted into database for ownerid: {ownerid}")

        thread = threading.Thread(target=execute_script_async, args=(ownerid, data.get('customername')))
        thread.start()

        script_statuses[ownerid] = "InProgress"
        logger.info(f"Data insertion and script execution initiated for ownerid: {ownerid}")

        response_data = {
            "status": "success",
            "message": "Data inserted and script execution initiated."
        }

        return jsonify(response_data)

    finally:
        cursor.close()
# API Route for Updating Data
@app.route('/update_data', methods=['POST'])
def update_data_route():
    api_key = request.headers.get('api_key')
    data = request.json

    if not authenticate_api_key(api_key):
        return jsonify({"status": "error", "message": "Invalid authentication"}), 401

    ownerid = data.get('ownerid')
    if not ownerid:
        return jsonify({"status": "error", "message": "ownerid field is required"}), 400

    cursor = db_connection.cursor()
    try:
        cursor.execute("SELECT * FROM dbautobala WHERE ownerid = %s", (ownerid,))
        existing_row = cursor.fetchone()

        if existing_row:
            column_names = cursor.column_names
            all_same = True

            for key in data:
                if key != "ownerid":
                    column_index = column_names.index(key)
                    if existing_row[column_index] != data[key]:
                        all_same = False
                        break

            if all_same:
                response_data = {
                    "status": "error",
                    "message": f"All values for customer with owner ID {ownerid} are already the same."
                }
                return response_data

            process_data(data, cursor)
            db_connection.commit()
            logger.info(f"Data updated in database for ownerid: {ownerid}")

            thread = threading.Thread(target=execute_script_async, args=(ownerid, data.get('customername')))
            thread.start()

            script_statuses[ownerid] = "InProgress"
            logger.info(f"Data update and script execution initiated for ownerid: {ownerid}")

            response_data = {
                "status": "success",
                "message": "Data updated and script execution initiated."
            }

            return jsonify(response_data)

    finally:
        cursor.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)