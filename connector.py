import psycopg2
from psycopg2 import pool
import os

# Environment Variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Initialize the connection pool
connection_pool = None

def initialize_pool():
    global connection_pool
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1, 
        maxconn=10,  # Adjust max connections based on your needs
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    if connection_pool:
        print("Database connection pool initialized.")

def get_connection():
    if connection_pool:
        return connection_pool.getconn()
    raise Exception("Connection pool is not initialized.")

def release_connection(conn):
    if connection_pool and conn:
        connection_pool.putconn(conn)

def close_pool():
    if connection_pool:
        connection_pool.closeall()
        print("Database connection pool closed.")
