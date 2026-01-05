import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="*Teddygringo1",
        database="FreshSteps"
    )