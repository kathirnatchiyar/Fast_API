import uvicorn
import mysql.connector
import logging
import threading
import subprocess
from fastapi import FastAPI, HTTPException, Header

app = FastAPI()

logging.basicConfig(
    filename=r"api.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# API Key
VALID_API_KEY = '4Ie9HGmIQvsgrMyaUdW16lbOI5w09I2tR0ehrSIcHHFvCgJypLsxLJrRO70KO8xg'
SCRIPT_PATH = r"script.bat"

# MySQL Configuration
mysql_host = '10.100.16.51'
mysql_user = 'runtime_api'
mysql_password = 'Runt!me_api*1'
mysql_database = 'provisioningdb'
mysql_port = '3400'
ss_disable = True

# Database Connection
db_connection = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database,
    port=mysql_port,
    ssl_disabled=ss_disable  # Explicitly disable SSL/TLS
)


# API Key Authentication
def authenticate_api_key(api_key):
    return api_key == VALID_API_KEY


script_statuses = {}


def process_data(data, cursor):
    owner_id = data["ownerid"]
    cursor.execute("SELECT * FROM runtimeapi WHERE ownerid = %s", (owner_id,))
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
                UPDATE runtimeapi
                SET customername = %s,customertype = %s, requestedby = %s, lineofbuisness = %s,
                    transactiondbrequired = %s, uiuxrequired = %s, workflowrequired = %s, ratingrequired = %s, reportingdbrequired = %s,
                    docgenrequired = %s, batchprocessrequired =  %s 
                WHERE ownerid = %s
            """

            cursor.execute(update_query, (
                data["customername"], data["customertype"], data["requestedby"],
                data["lineofbuisness"], data["transactiondbrequired"], data["uiuxrequired"], data["workflowrequired"],
                data["ratingrequired"], data["reportingdbrequired"], data["docgenrequired"], data["batchprocessrequired"], owner_id
            ))

            print("Updated row with changes.")

    else:
        insert_query = """
               INSERT INTO runtimeapi
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s ,%s)
           """
        cursor.execute(insert_query, (
            owner_id, data["customername"], data["customertype"], data["requestedby"],
            data["lineofbuisness"], data["transactiondbrequired"], data["uiuxrequired"],
            data["workflowrequired"], data["ratingrequired"], data["reportingdbrequired"],
            data["docgenrequired"], data["batchprocessrequired"],
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


@app.post('/createruntime')
async def insert_data_route(
    api_key: str = Header(None),
    data: dict = None
):
    if not authenticate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid authentication")

    ownerid = data.get('ownerid')
    if not ownerid:
        raise HTTPException(status_code=400, detail="ownerid field is required")

    # Check if all the values for specified columns are set to "No"
    no_columns = [
        "transactiondbrequired", "uiuxrequired", "workflowrequired",
        "ratingrequired", "reportingdbrequired", "docgenrequired", "batchprocessrequired"
    ]

    all_no = all(data.get(column) == "No" for column in no_columns)

    if all_no:
        response_data = {
            "request_data": data,
            "status": "Error",
            "message": "All service values are 'No'. Data insertion and script execution not allowed."
        }
        return response_data

    cursor = db_connection.cursor()
    try:
        cursor.execute("SELECT * FROM runtimeapi WHERE ownerid = %s", (ownerid,))
        existing_row = cursor.fetchone()

        if existing_row:
            column_names = cursor.column_names
            existing_data = dict(zip(column_names, existing_row))

            all_same = True
            differing_columns = []
            for key in data:
                if key != "ownerid" and existing_data[key] != data[key]:
                    all_same = False
                    differing_columns.append(key)

            if all_same:
                response_data = {
                    "request_data": data,
                    "status": "Error",
                    "message": f"Customer with owner ID {ownerid} already exists with all requested services."
                }
                return response_data
            else:
                response_data = {
                    "request_data": data,
                    "status": "Error",
                    "message": f"Service update for owner ID {ownerid} should be given in update route.",
                    "differing_columns": differing_columns

                }
                return response_data

        insert_query = """
           INSERT INTO runtimeapi
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s)
           """
        cursor.execute(insert_query, (
            ownerid, data["customername"], data["customertype"], data["requestedby"],
            data["lineofbuisness"], data["transactiondbrequired"], data["uiuxrequired"],
            data["workflowrequired"], data["ratingrequired"], data["reportingdbrequired"],
            data["docgenrequired"], data["batchprocessrequired"],
        ))
        db_connection.commit()
        logger.info(f"Data inserted into database for ownerid: {ownerid}")

        thread = threading.Thread(target=execute_script_async, args=(ownerid, data.get('customername')))
        thread.start()

        script_statuses[ownerid] = "InProgress"
        logger.info(f"Data insertion and script execution initiated for ownerid: {ownerid}")

        response_data = {
            "request_data": data,
            "status": "In progress",
            "message": "Data inserted and script execution initiated."

        }

        return response_data

    finally:
        cursor.close()


@app.post('/updateruntime')
async def update_data_route(
    api_key: str = Header(None),
    data: dict = None
):
    if not authenticate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid authentication")

    ownerid = data.get('ownerid')
    if not ownerid:
        raise HTTPException(status_code=400, detail="ownerid field is required")

    # Check if all the values for specified columns are set to "No"
    no_columns = [
        "transactiondbrequired", "uiuxrequired", "workflowrequired",
        "ratingrequired", "reportingdbrequired", "docgenrequired", "batchprocessrequired"
    ]

    all_no = all(data.get(column) == "No" for column in no_columns)

    if all_no:
        response_data = {
            "request_data": data,
            "status": "Error",
            "message": "All service values are 'No'. Data update and script execution not allowed."
        }
        return response_data

    cursor = db_connection.cursor()
    try:
        cursor.execute("SELECT * FROM runtimeapi WHERE ownerid = %s", (ownerid,))
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
                    "request_data": data,
                    "status": "Error",
                    "message": f"Services requested for customer with owner ID {ownerid} already exist."
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
                "request_data": data,
                "status": "In progress",
                "message": "Data updated and script execution initiated."
            }

            return response_data

    finally:
        cursor.close()


if __name__ == "__main__":
    uvicorn.run(app, host="10.100.16.53", port=5000)

