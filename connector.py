import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool

# Load environment variables
load_dotenv()

# Database credentials
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port

# Initialize connection pool
db_pool = None

def initialize_pool():
    """Initializes the PostgreSQL connection pool."""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,  # Minimum and maximum connections in the pool
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        if db_pool:
            print("Database connection pool created successfully.")
    except Exception as e:
        print(f"Error initializing database connection pool: {e}")

def get_connection():
    """Gets a connection from the pool."""
    try:
        if db_pool:
            return db_pool.getconn()
        else:
            raise Exception("Database connection pool is not initialized.")
    except Exception as e:
        print(f"Error getting a connection: {e}")
        return None

def release_connection(conn):
    """Releases a connection back to the pool."""
    try:
        if db_pool and conn:
            db_pool.putconn(conn)
    except Exception as e:
        print(f"Error releasing the connection: {e}")

def close_pool():
    """Closes all connections in the pool."""
    try:
        if db_pool:
            db_pool.closeall()
            print("Database connection pool closed.")
    except Exception as e:
        print(f"Error closing the connection pool: {e}")
