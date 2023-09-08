import sqlite3

api_meta_table = "api_metadata"
def create_table(connection, table_name, columns):
    """Create a table in SQLite in Python.

    Args:
        connection (sqlite3.Connection): The SQLite connection.
        table_name (str): The name of the table.
        columns (list): A list of the columns in the table.

    Returns:
        None.
    """

    query = "CREATE TABLE IF NOT EXISTS {} ({})".format(
        table_name, ", ".join(columns)
    )
    connection.execute(query)

def insert_table(connection, query):
    """Query a table in SQLite in Python.

    Args:
        connection (sqlite3.Connection): The SQLite connection.
        query (str): The SQL query to be executed.

    Returns:
        list: A list of rows from the table.
    """

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

def query_table(connection, query):
    """Query a table in SQLite in Python.

    Args:
        connection (sqlite3.Connection): The SQLite connection.
        query (str): The SQL query to be executed.

    Returns:
        list: A list of rows from the table.
    """

    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows

if __name__ == "__main__":

    connection = sqlite3.connect(".api_db.db")
    create_table(connection, api_meta_table, ["owner_id", "customer_name", "service", "status", "lob"])
    
    query = "INSERT INTO {}  VALUES ({}, '{}', '{}', '{}', '{}')".format(api_meta_table, "18", "rsum", "DB", "INITIALIZED", "GL" )
    rows = insert_table(connection, query)
    query = "SELECT * FROM {}".format(api_meta_table)
    rows = query_table(connection, query)
    for row in rows:
        print(row)