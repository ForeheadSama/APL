import pyodbc

def get_db_connection():
    """
    Establish a connection to the Azure SQL Database and return a connection object.
    """
    # Connection string
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=apblbookingserver.database.windows.net;"
        "DATABASE=APBLBookingDB;"
        "UID=adminlogin;"
        "PWD=adm!n123;"
    )

    # Connect to the database
    conn = pyodbc.connect(conn_str)
    return conn