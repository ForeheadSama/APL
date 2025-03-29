# backend/database/connect_alt.py
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """
     Connection function, no Azure SDK
    """
    # Build connection string
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    
    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        print(f"Database connection error: {str(e)}")
        raise