import requests
import json
import mysql.connector

#api authentication
#The code first defines two variables: API_KEY and API_ENDPOINT. 
#These variables store the API key and the endpoint URL for the API you want to access.
API_KEY = 'your_api_key_here'
API_ENDPOINT = 'https://api.example.com/data'

# The next line creates a dictionary called headers. 
# This dictionary contains a single key-value pair: Authorization and Bearer {API_KEY}. 
# This header tells the API that you are authorized to access it.
headers = {
    'Authorization': f'Bearer {API_KEY}'
}

#The next line uses the requests library to make a GET request to the API endpoint. 
#The headers dictionary is passed as an argument to the requests.get() function.
#The requests.get() function returns a response object. 
#This object contains information about the response, such as the status code and the response body.
try:
    response = requests.get(API_ENDPOINT, headers=headers)
#The next line checks the response.status_code. If the status code is 200, then the request was successful. 
# In this case, the response.json() method is used to decode the response body as JSON. 
# The decoded JSON data is then printed to the console.
    if response.status_code == 200:
        data = response.json()
        print("API response:", data)
#If the status code is not 200, then the request failed. 
#In this case, the print() function is used to print the status code to the console.        
    else:
        print("API request failed. Status code:", response.status_code)
# The final two lines of code handle errors that might occur when making the API request. 
# The except clause catches any requests.exceptions.RequestException errors. 
# These errors are raised when there is a problem making the request, such as a network error or a malformed request. 
# If an error occurs, the print() function is used to print the error message to the console.
except requests.exceptions.RequestException as e:
    print("Error making API request:", e)

# Replace these values with your MySQL database credentials
db_config = {
    'host': 'your_host',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database_name'
}


def create_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


def read_json_data_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as err:
        print(f"Error decoding JSON in file '{file_path}': {err}")
        return None


def check_and_insert_data(data):
    try:
        connection = create_connection()
        if not connection:
            return

        cursor = connection.cursor()

        name = data['name']
        id = data['id']
        lob = data['lob']
        service = data['service']
        # Check if any of the 4 values exist in the database
        cursor.execute("SELECT id FROM employees WHERE name = %s AND id = %s AND lob = %s AND service = AND",
                       (name, employee_id, lob, service))
        print("CUSTOMER ALREADY EXIST")

        # Check if any of the 4 values exist in the database
        cursor.execute("SELECT id FROM employees WHERE name = %s OR id = %s OR lob = %s OR service = %s",
                       (name, employee_id, lob, service))
        print(f"Inserted data for {name}")


        if not result:
            # If none of the values are present, insert the record into the database
            cursor.execute("INSERT INTO employees (name, id, lob, service) VALUES (%s, %s, %s, %s)",
                           (name, employee_id, lob, service))
            print(f"Inserted data for {name}")

        # Commit changes to the database
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error accessing MySQL: {err}")
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    json_file_path = "data.json"  # Replace this with the path to your JSON file
    json_data = read_json_data_from_file(json_file_path)
    if json_data:
        # Now you can use the 'json_data' variable containing the JSON data read from the file
        check_and_insert_data(json_data)