import mysql.connector

def connect(username, password):
    sydtp_db = mysql.connector.connect(
        host="localhost",
        user=username,
        password=password,
        database="SydneyTransport"
    )

    return sydtp_db