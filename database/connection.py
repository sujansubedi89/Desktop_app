# database/connection.py
#
# One job: connect to MySQL.
# Every other file calls get_connection() from here.
# Change DB settings here only — nowhere else.

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()  # reads your .env file


def get_connection():
    """
    Opens and returns a MySQL connection.

    Usage in every other file:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        # ... do your SQL ...
        cursor.close()
        conn.close()   ← always close when done!
    """
    try:
        conn = mysql.connector.connect(
            host     = os.getenv("DB_HOST",     "localhost"),
            port     = int(os.getenv("DB_PORT", 3306)),
            user     = os.getenv("DB_USER",     "root"),
            password = os.getenv("DB_PASSWORD", ""),
            database = os.getenv("DB_NAME",     "nepal_tickets")
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Database connection failed: {e}")
        raise


def get_connection_no_db():
    """
    Connects WITHOUT selecting a database.
    Only used by schema.py to CREATE the database the first time.
    """
    load_dotenv()
    return mysql.connector.connect(
        host     = os.getenv("DB_HOST",     "localhost"),
        port     = int(os.getenv("DB_PORT", 3306)),
        user     = os.getenv("DB_USER",     "root"),
        password = os.getenv("DB_PASSWORD", "")
    )