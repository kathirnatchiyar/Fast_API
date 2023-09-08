import uvicorn
import mysql.connector
import logging
import threading
import subprocess
from fastapi import FastAPI, HTTPException, Header
from cryptography.fernet import Fernet
from datetime import datetime
import time
from base64 import b64decode, b64encode
import base64
import pytz
import json
from mysql.connector import pooling
import traceback
from fastapi import Request


app = FastAPI()

# Logging configuration
logging.basicConfig(
    filename=r"C:\Users\balakumaran_m\Downloads\Angular_python\api.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("This is an info message")
logger.error("This is an error message")


SCRIPT_PATH = r"C:\Users\balakumaran_m\Downloads\Angular_python\script.bat"

# MySQL Configuration
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'redhat'
mysql_database = 'runtimedb'
ss_disable = True

# Database Connection
db_connection = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database,
    ssl_disabled=ss_disable
)


# Database Connection Pooling
def createsysdbConnectionPooling():
    try:
        configs = {
            "pool_size": 2,
            "db_host": "10.101.4.13",
            "db_port": "3401",
            "db_user": "usquoperationuser",
            "db_cred": "USQUat*23jKla!kLq65",
            "dbname": "solartissysconfigdbV3"
        }
        sysdb_pooling_object = pooling.MySQLConnectionPool(
            pool_name="sysconfigdbV3",
            pool_size=int(configs["pool_size"]),
            pool_reset_session=True,
            host=configs["db_host"],
            port=int(configs["db_port"]),
            user=configs["db_user"],
            password=configs["db_cred"],
            database=configs["dbname"],
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            buffered=True
        )
        return sysdb_pooling_object
    except Exception as exception:
        raise exception("Error while getting createsysdbConnectionPooling")


def tokenValidation(privilegeName, requestJson, rheaders):
    try:
        sysdbPoolingObject = createsysdbConnectionPooling()
        sysdbConnection = sysdbPoolingObject.get_connection()
        ruleInformationList = []
        validateHeaders(rheaders, requestJson, ruleInformationList)
        if (len(ruleInformationList) != 0):
            return ruleInformationList
        transDict = requestJson.copy()
        transDict['headers'] = rheaders
        decryptedToken = decryptToken(transDict, sysdbConnection, ruleInformationList)
        if (len(ruleInformationList) == 0):
            validateToken(transDict, decryptedToken, privilegeName, ruleInformationList)
        return ruleInformationList
    except Exception as exception:
        print(traceback.format_exc())
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)
        return ruleInformationList


def decryptToken(transDict, sysdbConnection, ruleInformationList):
    try:
        syscursor = sysdbConnection.cursor(dictionary=True)
        encryptedToken = transDict['headers']['Token']
        # print(transDict)
        keyfetchingsql = "SELECT PARAMETER_VALUE FROM OWNER_CONFIG WHERE OWNER_ID=" + transDict[
            'ownerid'] + " AND PARAMETER_NAME = 'TOKEN::AES::ENCRYPTION/DECRYPTION' AND ACTIVE = 'Y' LIMIT 1"
        syscursor.execute(keyfetchingsql)
        resultData = syscursor.fetchone()
        if (resultData != None):
            decryptionKey = resultData['PARAMETER_VALUE']
            tokenbytes = bytes(encryptedToken, 'utf-8')
            enctoken = b64decode(tokenbytes)
            # Convert the pre shared key from string to bytes.
            key = bytes(decryptionKey, 'utf-8')
            cipher_obj = AES.new(key, AES.MODE_ECB)
            decoded_token = cipher_obj.decrypt(enctoken).decode('utf8')
            return decoded_token
        else:
            errorDict = {}
            errorDict['Error'] = "Token Preshared Key Not Found"
            ruleInformationList.append(errorDict)
            # If the Number of characters in token is less than the actual character length of token
    except UnicodeDecodeError:
        errorDict = {}
        errorDict['Error'] = "Invalid Token, UnicodeDecodeError"
        ruleInformationList.append(errorDict)
    # If the Token is Invalid
    except base64.binascii.Error:
        errorDict = {}
        errorDict['Error'] = "Invalid Token. base64.binascii.Error"
        ruleInformationList.append(errorDict)
    except Exception as exception:
        print(traceback.format_exc(), flush=True)
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)


def getUTCTimeFromInputDate(dateString):
    try:
        dateGetTimeZoneNonExtracted = dateString.split(":")[-1]
        DateexactTimeZone = dateGetTimeZoneNonExtracted[3:-4]
        startdatewithouttimezone = dateString.replace(DateexactTimeZone, "")
        datetime_obj = datetime.strptime(startdatewithouttimezone, "%a %b %d %H:%M:%S %Y")
        timezoneValues = {
            "IST": "Asia/Kolkata",
            "EDT": "America/New_York"
        }
        if (DateexactTimeZone[:-1] in timezoneValues):
            dynamicTZ = pytz.timezone(timezoneValues[DateexactTimeZone[:-1]])
            dynamicTime = dynamicTZ.localize(datetime_obj)
            utc_time = dynamicTime.astimezone(pytz.utc)
            return utc_time
        else:
            raise Exception("TimeZone not configured")
    except Exception as e:
        print(traceback.format_exc())
        raise Exception


def validateToken(transDict, token, privilegeName, ruleInformationList):
    try:
        if (token != None and token != ""):
            tokenSplitted = token.split("[")
            extractedData = []
            extractedDataPrivileges = []
            for split in tokenSplitted:
                if ("]" in split):
                    extractedData.append(split.split("]")[0])
            privilegeTokenSplitted = token.split("{")
            for splitPrivileges in privilegeTokenSplitted:
                if ("}" in splitPrivileges):
                    extractedDataPrivileges.append(splitPrivileges.split("}")[0])
            if (privilegeName not in extractedDataPrivileges):
                errorDict = {}
                errorDict['Error'] = "Privilege not found in the token"
                ruleInformationList.append(errorDict)
            else:
                if (transDict['ownerid'] != extractedData[0]):
                    errorDict = {}
                    errorDict['Error'] = "ownerId Does Not Match in the token"
                    ruleInformationList.append(errorDict)
                else:
                    if (transDict['requestedby'] != extractedData[2]):
                        errorDict = {}
                        errorDict['Error'] = "requestedby does not match in the token"
                        ruleInformationList.append(errorDict)
                    else:
                        startTime = extractedData[4]
                        startTimeOBJ = getUTCTimeFromInputDate(startTime)
                        endTime = extractedData[5]
                        endTimeOBJ = getUTCTimeFromInputDate(endTime)
                        currentTime_utc = datetime.now().astimezone(pytz.utc)
                        if (currentTime_utc < startTimeOBJ or currentTime_utc > endTimeOBJ):
                            errorDict = {}
                            errorDict['Error'] = "Token Expired"
                            ruleInformationList.append(errorDict)
        return ruleInformationList
    except Exception as exception:
        print(traceback.format_exc(), flush=True)
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)
        return ruleInformationList


def validateHeaders(rheaders, requestJson, ruleInformationList):
    try:
        # header validation
        headerData = rheaders
        if (headerData.get("Token", "") == ""):
            errorDict = {}
            errorDict['Error'] = "Token is not found or Empty in Header Data"
            ruleInformationList.append(errorDict)
            return ruleInformationList

        # input data validation
        # required_inputs = ["ownerId",  "customerName", "customerType",  "sessionUser", "datetime",  "lob", "transdb",  "uiux",  "wf",  "rating",  "reportingdb"]
        required_inputs = ["ownerid", "customername", "customertype", "requestedby", "lineofbuisness",
                           "transactiondbrequired", "uiuxrequired", "workflowrequired", "ratingrequired",
                           "reportingdbrequired", "docgenrequired", "batchprocessrequired"]
        for rinput in required_inputs:
            # print(rinput)
            if (requestJson.get(rinput, "") == ""):
                print("{} is not found in input".format(rinput))
                errorDict = {}
                errorDict['Error'] = "{} is not found in input".format(rinput)
                ruleInformationList.append(errorDict)
                return ruleInformationList

    except Exception as exception:
        print(traceback.format_exc(), flush=True)
        errorDict = {}
        errorDict['Error'] = traceback.format_exc()
        ruleInformationList.append(errorDict)
        return ruleInformationList

script_statuses = {}
# Process Data Function (unchanged from previous code)
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


# Execute Script Async Function (unchanged from previous code)
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

async def insert_data_route( request : Request, data: dict = None ):
    rheaders = request.headers
    auth_stat = tokenValidation("Python_Microservice", data, rheaders )
    if(len(auth_stat) > 0):
        resp =  {
                        "status": "Failed",
                        "message": auth_stat
                    }
        raise HTTPException(status_code=401, detail=resp)

# async def insert_data_route(
#     api_key: str = Header(None),
#     data: dict = None
# ):
#     if not authenticate_api_key(api_key):
#         raise HTTPException(status_code=401, detail="Invalid authentication")
#
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

# FastAPI route for updating runtime data
@app.post('/updateruntime')
async def insert_data_route( request : Request, data: dict = None ):
    rheaders = request.headers
    auth_stat = tokenValidation("Python_Microservice", data, rheaders )
    if(len(auth_stat) > 0):
        resp =  {
                        "status": "Failed",
                        "message": auth_stat
                    }
        raise HTTPException(status_code=401, detail=resp)

# async def update_data_route(
#     api_key: str = Header(None),
#     data: dict = None
# ):
#     if not authenticate_api_key(api_key):
#         raise HTTPException(status_code=401, detail="Invalid authentication")

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
    uvicorn.run(app, host="0.0.0.0", port=80)
