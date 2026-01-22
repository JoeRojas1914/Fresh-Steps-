import os
import mysql.connector
from dotenv import load_dotenv

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )
