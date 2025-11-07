import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'shipping_ml'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'raise_on_warnings': True
}

def get_db_connection():
    """
    Create and return a new database connection.
    Returns None if connection fails.
    """
    try:
        # Create connection with extended timeout and better error handling
        connection = mysql.connector.connect(
            **DB_CONFIG,
            connection_timeout=10,
            buffered=True,
            autocommit=True
        )
        
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
            
    except Error as e:
        print(f"Error connecting to MySQL database: {str(e)}")
        if "Access denied" in str(e):
            print("Check your MySQL username and password in .env file")
        elif "Can't connect" in str(e):
            print("Make sure MySQL server is running")
        elif "Unknown database" in str(e):
            print(f"Database '{DB_CONFIG['database']}' does not exist")
        return None
        
    except Exception as e:
        print(f"Unexpected error while connecting to database: {str(e)}")
        return None

def test_connection():
    """
    Test database connection and print status.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Test querying the database
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            print("Database connection test successful!")
            print(f"Connected to: {DB_CONFIG['database']}")
            
            # Get and print table information
            cursor.execute("""
                SELECT table_name, table_rows 
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (DB_CONFIG['database'],))
            
            print("\nAvailable tables:")
            for table in cursor.fetchall():
                print(f"- {table[0]}: ~{table[1]} rows")
                
        except Error as e:
            print(f"Error testing database: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Could not establish database connection")